"""Unified Command-line interface (CLI) for ClaudeMark."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

# Ensure stdout and stderr handle Unicode gracefully on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from . import __author__, __version__, analyze_text, compute_forensic_diff, normalize_text
from .core.constants import MAX_INPUT_BYTES, MAX_TEXT_LENGTH
from .core.normalizer import NormalizationOptions
from .core.unicode_forensics import analyze_unicode_forensics, visualize_unicode_markers
from .detectors.registry import detector_registry
from .provenance.batch import (
    batch_clean,
    batch_inspect,
    clean_single_file,
    inspect_single_file,
)
from .reports.json_report import format_json_report
from .reports.markdown_report import format_markdown_report
from .reports.terminal import format_terminal_diff, format_terminal_report
from .watermark.experimental import run_parameter_sweep

MAX_FILE_SIZE_BYTES = MAX_INPUT_BYTES


def _workspace_path(raw_path: str) -> Path:
    """Resolve a CLI path inside the configured workspace boundary.

    CLI paths can name nested files, but may never escape the current working
    directory (or ``CLAUDEMARK_WORKSPACE_ROOT`` when configured).
    """
    root = os.path.realpath(os.environ.get("CLAUDEMARK_WORKSPACE_ROOT", os.getcwd()))
    # Treat both slash styles as separators on every OS. This prevents a path
    # accepted on Linux from becoming traversal when later consumed on Windows.
    normalized_input = str(raw_path).replace("\\", os.sep).replace("/", os.sep)
    candidate = os.path.realpath(os.path.normpath(os.path.join(root, normalized_input)))
    if candidate != root and not candidate.startswith(root + os.sep):
        raise ValueError("Path traversal detected: target is outside the workspace root")
    return Path(candidate)


def _read_input(
    file_path: str | None,
    raw_text: str | None,
    raw_escaped_text: str | None = None,
) -> tuple[str, str]:
    """Read text from file, string argument, explicit escaped string, or stdin securely."""
    if raw_escaped_text is not None:
        try:
            # Decode literal \u200b or \x escape sequences cleanly
            decoded = raw_escaped_text.encode("utf-8").decode("unicode_escape")
            return decoded, "<escaped_text>"
        except Exception:
            return raw_escaped_text, "<raw_text>"

    if raw_text is not None:
        return raw_text, "<raw_text>"

    if file_path and file_path != "-":
        p = Path(file_path).resolve()
        if not p.is_file():
            sys.stderr.write(f"Error: File not found: {file_path}\n")
            sys.exit(1)
        if p.stat().st_size > MAX_FILE_SIZE_BYTES:
            sys.stderr.write(f"Error: File size exceeds safety limit ({MAX_FILE_SIZE_BYTES} bytes): {file_path}\n")
            sys.exit(1)
        try:
            return p.read_text(encoding="utf-8", errors="replace"), p.name
        except Exception as ex:
            sys.stderr.write(f"Error reading {file_path}: {ex}\n")
            sys.exit(1)

    if not sys.stdin.isatty():
        return sys.stdin.read(MAX_FILE_SIZE_BYTES), "<stdin>"

    sys.stderr.write("Error: No input provided. Specify a file or pass --text / --text-escaped.\n")
    sys.exit(1)


def _write_output(content: str, out_path: str | None) -> None:
    if out_path:
        p = Path(out_path).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        print(f"Report written to: {p}")
    else:
        sys.stdout.write(content)


def cmd_analyze(args: argparse.Namespace) -> int:
    text, source_name = _read_input(args.file, args.text, getattr(args, "text_escaped", None))
    res = analyze_text(text, detector_name=args.algorithm, threshold=args.threshold)
    
    stats = res["text_statistics"]
    unicode_rep = res["unicode_forensics"]
    wm_res = res["watermark_result"]

    if args.json:
        out = format_json_report(stats, unicode_rep, wm_res, source_name=source_name)
    elif args.markdown:
        out = format_markdown_report(source_name, stats, unicode_rep, wm_res, verbose=args.verbose)
    else:
        out = format_terminal_report(source_name, stats, unicode_rep, wm_res, verbose=args.verbose)

    _write_output(out, args.output)
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    target = _workspace_path(args.target)
    if not target.exists():
        sys.stderr.write(f"Error: Path does not exist: {target}\n")
        return 1

    if target.is_dir():
        # Batch directory inspection
        res = batch_inspect(target, recursive=not args.no_recursive)
        if args.json:
            _write_output(json.dumps(res.to_dict(), indent=2), args.output)
        else:
            print("ClaudeMark Batch Provenance Inspection")
            print("═" * 60)
            print(f"Directory:           {res.directory}")
            print(f"Total Scanned:       {res.total_files_scanned} files")
            print(f"Supported Formats:   {res.supported_files_count} files")
            print(f"Suspicious Files:    {res.suspicious_count} files")
            print("─" * 60)
            for r in res.file_reports[:20]:
                susp = "⚠️ SUSPICIOUS" if r.get("suspicious") else "✅ CLEAN"
                print(f"[{susp}] {Path(r.get('file_path', '')).name:<30} ({r.get('file_format', '').upper()})")
            if len(res.file_reports) > 20:
                print(f"... and {len(res.file_reports) - 20} more files (use --json for complete list).")
        return 0
    else:
        # Single file inspection
        rep = inspect_single_file(target)
        if args.certificate:
            from .provenance.certificate import save_audit_certificate
            cert_p = Path(args.certificate).resolve()
            save_audit_certificate(target, rep.to_dict(), cert_p)
            print(f"Generated Forensic Audit Certificate: {cert_p}")

        if args.json:
            _write_output(json.dumps(rep.to_dict(), indent=2), args.output)
        else:
            print(f"ClaudeMark File Provenance Report: {rep.file_name}")
            print("═" * 60)
            print(f"Format:            {rep.file_format.upper()}")
            print(f"File Size:         {rep.file_size_bytes:,} bytes")
            print(f"C2PA Manifest:     {'YES' if rep.has_c2pa else 'NO'}")
            print(f"EXIF Metadata:     {'YES' if rep.has_exif else 'NO'}")
            print(f"XMP Metadata:      {'YES' if rep.has_xmp else 'NO'}")
            print(f"AI Metadata Tags:  {'YES' if rep.has_ai_metadata else 'NO'}")
            print(f"Unicode Anomalies: {rep.unicode_anomalies}")
            print("─" * 60)
            print(f"Summary:           {rep.summary}")
        return 0


def cmd_clean(args: argparse.Namespace) -> int:
    target = _workspace_path(args.target)
    if not target.exists():
        sys.stderr.write(f"Error: Path does not exist: {target}\n")
        return 1

    if target.is_dir():
        # Batch directory cleaning
        if not args.output and not args.in_place:
            sys.stderr.write("Error: For batch directory cleaning, specify -o <output_dir> or --in-place.\n")
            return 1
        res = batch_clean(target, output_dir=Path(args.output) if args.output else None, in_place=args.in_place)
        if args.json:
            _write_output(json.dumps(res.to_dict(), indent=2), None)
        else:
            print("ClaudeMark Batch Cleaning Summary")
            print("═" * 60)
            print(f"Directory:           {res.directory}")
            print(f"Cleaned Successfully:{res.cleaned_count} files")
            print(f"Failed:              {res.failed_count} files")
        return 0
    else:
        out_p = Path(args.output).resolve() if args.output else None
        res = clean_single_file(target, out_p, strip_all_metadata=not args.keep_non_ai, remove_pixel=args.remove_pixel)
        if args.json:
            _write_output(json.dumps(res.to_dict(), indent=2), None)
        else:
            print(f"Cleaned: {target.name} -> {res.output_path}")
            print(f"Size: {res.original_size_bytes:,} -> {res.cleaned_size_bytes:,} bytes (delta: {res.size_delta_bytes:+d})")
            print("Actions performed:")
            for a in res.actions_performed:
                print(f"  • {a}")
        return 0


def cmd_normalize(args: argparse.Namespace) -> int:
    text, source_name = _read_input(args.file, args.text)
    opts = NormalizationOptions(
        strip_zero_width=not args.keep_zero_width,
        normalize_spaces=not args.keep_spaces,
        strip_bidi_controls=not args.keep_bidi,
        strip_unprintable_controls=True,
        normalize_unicode_form="NFKC" if args.nfkc else "NFC",
        replace_homoglyphs=args.replace_homoglyphs,
        strip_bom=True,
    )
    res = normalize_text(text, options=opts)
    
    if args.output:
        out_p = Path(args.output).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(res.normalized_text, encoding="utf-8")
        print(f"Cleaned text written to: {out_p}")
    else:
        if args.verbose:
            print(f"# Normalization Summary for {source_name}:")
            print(f"# Zero-width removed: {res.zero_width_removed}, Spaces normalized: {res.spaces_normalized}")
            print("---")
        sys.stdout.write(res.normalized_text)
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    if not args.json:
        args.markdown = True
    return cmd_analyze(args)


def cmd_diff(args: argparse.Namespace) -> int:
    orig_text, orig_name = _read_input(args.file1, None)
    proc_text, proc_name = _read_input(args.file2, None)

    detector = detector_registry.get(args.algorithm)
    orig_score = detector.score(orig_text)
    proc_score = detector.score(proc_text)

    diff = compute_forensic_diff(
        orig_text,
        proc_text,
        original_score=orig_score,
        new_score=proc_score,
    )

    if getattr(args, "html", False):
        from .core.diff import render_html_diff
        html_rep = render_html_diff(orig_text, proc_text, orig_name, proc_name, diff)
        _write_output(html_rep, args.output)
    elif args.json:
        payload = {
            "tool": "ClaudeMark",
            "command": "diff",
            "file1": orig_name,
            "file2": proc_name,
            "diff": diff.to_dict(),
        }
        _write_output(json.dumps(payload, indent=2), args.output)
    else:
        rep = format_terminal_diff(diff, orig_name, proc_name)
        _write_output(rep, args.output)
    return 0


def cmd_unicode(args: argparse.Namespace) -> int:
    text, source_name = _read_input(args.file, args.text, getattr(args, "text_escaped", None))
    op = args.operation

    if op == "inspect":
        rep = analyze_unicode_forensics(text)
        if args.json:
            print(json.dumps(rep.to_dict(), indent=2))
        else:
            print(f"Unicode Forensics Report: {source_name}")
            print("═" * 50)
            print(f"Total Anomalies:       {rep.total_anomalies}")
            print(f"Zero-Width Characters: {rep.zero_width_count}")
            print(f"Non-Breaking Spaces:   {rep.nbsp_count}")
            print(f"BiDi Controls:         {rep.bidi_control_count}")
            print(f"Homoglyphs:            {rep.homoglyph_count}")
            print(f"NFC Normalized:        {rep.is_nfc}")
            print(f"Summary:               {rep.summary_text}")

    elif op == "visualize":
        vis = visualize_unicode_markers(text)
        _write_output(vis, args.output)

    elif op in ("normalize", "clean"):
        res = normalize_text(text)
        if args.json:
            print(json.dumps(res.to_dict(), indent=2))
        else:
            _write_output(res.normalized_text, args.output)
            print(f"Cleaned {res.zero_width_removed} zero-width character(s).", file=sys.stderr)

    return 0


def cmd_rewrite(args: argparse.Namespace) -> int:
    text, source_name = _read_input(args.file, args.text, getattr(args, "text_escaped", None))
    from .rewrite.paraphrase import disrupt_watermark

    res = disrupt_watermark(text, strategy=args.strategy, detector_name=args.algorithm)
    if args.json:
        print(json.dumps(res.to_dict(), indent=2))
    else:
        _write_output(res.rewritten_text, args.output)
        if res.evaluation:
            ev = res.evaluation
            print(f"\nDisruption Evaluation ({source_name}):", file=sys.stderr)
            print(f"  • Original Watermark Score:  {ev.original_watermark_score:.2f}", file=sys.stderr)
            print(f"  • Rewritten Watermark Score: {ev.rewritten_watermark_score:.2f} (delta: {ev.watermark_score_delta:+.2f})", file=sys.stderr)
            print(f"  • Semantic Similarity:       {ev.semantic_similarity * 100:.1f}%", file=sys.stderr)
            print(f"  • Character Change:          {ev.character_change_ratio:.1f}%", file=sys.stderr)

    return 0


def cmd_evaluate(args: argparse.Namespace) -> int:
    orig_text, orig_name = _read_input(args.file1, None)
    proc_text, proc_name = _read_input(args.file2, None)
    from .rewrite.evaluation import evaluate_rewrite

    ev = evaluate_rewrite(orig_text, proc_text, detector_name=args.algorithm)
    if args.json:
        print(json.dumps(ev.to_dict(), indent=2))
    else:
        print(f"ClaudeMark Before/After Forensic Evaluation")
        print("═" * 50)
        print(f"Original File:         {orig_name}")
        print(f"Processed File:        {proc_name}")
        print(f"Watermark Score:       {ev.original_watermark_score:.2f} -> {ev.rewritten_watermark_score:.2f} (delta: {ev.watermark_score_delta:+.2f})")
        print(f"Semantic Similarity:   {ev.semantic_similarity * 100:.1f}%")
        print(f"Character Change:      {ev.character_change_ratio:.1f}%")
        print(f"Word Change:           {ev.word_change_ratio:.1f}%")
        print(f"Shannon Entropy:       {ev.original_entropy:.2f} -> {ev.rewritten_entropy:.2f}")

    return 0


def cmd_security(args: argparse.Namespace) -> int:
    from .security.scanner import scan_file_security
    target = _workspace_path(args.target)
    rep = scan_file_security(target)
    if args.json:
        print(json.dumps(rep.to_dict(), indent=2))
    else:
        print(f"ClaudeMark Security Scan: {rep.file_name}")
        print("═" * 50)
        print(f"Threat Level: {rep.threat_level}")
        print(f"Is Safe:      {'YES' if rep.is_safe else 'NO'}")
        if rep.warnings:
            print("\nWarnings:")
            for w in rep.warnings:
                print(f"  ⚠️  {w}")
        else:
            print("\nNo security vulnerabilities or malicious payloads detected.")

    return 0 if rep.is_safe else 1


def cmd_agent(args: argparse.Namespace) -> int:
    from .agent.tools import AGENT_TOOLS_MANIFEST, execute_agent_tool

    # 'tools' is an alias for 'list'
    if args.subcommand in ("list", "tools") or args.subcommand is None:
        print(json.dumps(AGENT_TOOLS_MANIFEST, indent=2))
    elif args.subcommand == "exec":
        # Accept tool name from --tool flag OR positional argument
        tool_name = getattr(args, "tool_name", None) or getattr(args, "tool_name_pos", None)
        if not tool_name:
            sys.stderr.write("Error: Specify tool via --tool <name> or as a positional argument.\n")
            sys.stderr.write("Example: claudemark agent exec --tool analyze_watermark --args '{\"text\":\"sample\"}'\n")
            return 1

        raw_args = args.args or "{}"
        try:
            arguments = json.loads(raw_args)
        except Exception:
            try:
                import ast
                arguments = ast.literal_eval(raw_args)
                if not isinstance(arguments, dict):
                    arguments = {}
            except Exception as e:
                sys.stderr.write(f"Error: Invalid JSON in --args: {e}\n")
                return 1

        res = execute_agent_tool(tool_name, arguments)
        print(json.dumps(res, indent=2))

    return 0



def cmd_c2pa(args: argparse.Namespace) -> int:
    target = _workspace_path(args.target)
    from .provenance.c2pa import inspect_c2pa_bytes, inspect_c2pa_tool

    if not target.is_file():
        sys.stderr.write(f"Error: Target file not found: {target}\n")
        return 1

    data = target.read_bytes()
    tool_res = inspect_c2pa_tool(target)
    byte_res = inspect_c2pa_bytes(data, asset_name=target.name)

    res = tool_res if tool_res else byte_res
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"C2PA Provenance Inspection: {target.name}")
        print("═" * 50)
        print(f"Status: {res.get('status', 'UNVERIFIED')}")
        tree = byte_res.get("provenance_tree", {})
        print("\nProvenance Hierarchy:")
        print(tree.get("tree_text", "No provenance tree generated"))

    return 0


def cmd_normalize(args: argparse.Namespace) -> int:
    text, source_name = _read_input(args.file, args.text)
    opts = NormalizationOptions(
        strip_zero_width=not args.keep_zero_width,
        normalize_spaces=not args.keep_special_spaces,
        normalize_unicode_form=args.unicode_form,
        replace_homoglyphs=args.replace_homoglyphs,
    )
    res = normalize_text(text, opts)
    if args.json:
        print(json.dumps(res.to_dict(), indent=2))
    else:
        _write_output(res.normalized_text, args.output)
    return 0


def cmd_capabilities(args: argparse.Namespace) -> int:
    from .agent.tools import AGENT_TOOLS_MANIFEST
    from .pixel.registry import pixel_registry

    caps = {
        "version": __version__,
        "detectors": detector_registry.list_detectors(),
        "pixel_backends": pixel_registry.list_details(),
        "supported_document_formats": ["pdf", "docx", "odt", "html", "md", "txt"],
        "supported_image_formats": ["png", "jpeg", "jpg", "webp", "svg", "avif", "heic"],
        "agent_tools": [t["name"] for t in AGENT_TOOLS_MANIFEST],
        "system_tools": {
            "c2patool": shutil.which("c2patool") is not None,
            "exiftool": shutil.which("exiftool") is not None,
            "qpdf": shutil.which("qpdf") is not None,
        },
    }
    if args.json:
        print(json.dumps(caps, indent=2))
    else:
        print(f"ClaudeMark Capabilities (v{__version__})")
        print("═" * 50)
        print(f"Active Detectors:     {', '.join(caps['detectors'])}")
        print(f"Pixel Backends:       {', '.join(b['name'] for b in caps['pixel_backends'])}")
        print(f"Document Formats:     {', '.join(caps['supported_document_formats'])}")
        print(f"Image Formats:        {', '.join(caps['supported_image_formats'])}")
        print(f"Agent Tools:          {', '.join(caps['agent_tools'])}")
        print("System Tools:")
        for tool, present in caps["system_tools"].items():
            print(f"  • {tool:<12} {'[Available]' if present else '[Not Installed]'}")
    return 0


def cmd_experimental(args: argparse.Namespace) -> int:
    print("ClaudeMark Experimental Research Engine")
    print("═" * 50)
    detector = detector_registry.get(args.algorithm)
    print(f"Active Detector: {detector.name} (v{detector.version})")
    
    sweep = run_parameter_sweep()
    print("\nEmpirical Threshold Sweep Table:")
    print("─" * 50)
    print(f"{'Threshold':<12} | {'F1-Score':<10} | {'FPR':<10} | {'TPR':<10}")
    print("─" * 50)
    for ev in sweep.evaluations:
        print(f"{ev.threshold:<12.2f} | {ev.f1_score:<10.2f} | {ev.false_positive_rate:<10.2f} | {ev.true_positive_rate:<10.2f}")
    print("─" * 50)
    print(f"Calibrated default threshold: {sweep.recommended_threshold:.2f}")
    return 0


def cmd_version(args: argparse.Namespace) -> int:
    print(f"ClaudeMark v{__version__} — Multi-AI Watermark & Provenance Forensics Toolkit")
    print(f"Registered Detectors: {', '.join(detector_registry.list_detectors())}")
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    from .server import run_server
    run_server(host=args.host, port=args.port)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="claudemark",
        description="ClaudeMark: Multi-AI Watermark & Provenance Forensics Toolkit",
    )
    # Standard --version flag (unix convention)
    parser.add_argument(
        "--version", "-V",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show version string and exit",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # serve
    p_srv = subparsers.add_parser("serve", help="Start ClaudeMark Web UI and REST API server")
    p_srv.add_argument("--host", default="127.0.0.1", help="Host interface to bind")
    p_srv.add_argument("--port", type=int, default=8950, help="Port to listen on")
    p_srv.set_defaults(func=cmd_serve)

    # inspect
    p_insp = subparsers.add_parser("inspect", help="Inspect file or directory for C2PA, EXIF, XMP, and AI marks")
    p_insp.add_argument("target", help="File or directory path to inspect")
    p_insp.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_insp.add_argument("--certificate", "-c", default=None, help="Generate standalone HTML audit certificate")
    p_insp.add_argument("--no-recursive", action="store_true", help="Do not recursively scan subdirectories")
    p_insp.add_argument("--output", "-o", default=None, help="Save report to file")
    p_insp.set_defaults(func=cmd_inspect)

    # clean
    p_cln = subparsers.add_parser("clean", help="Clean metadata and provenance marks from file or directory")
    p_cln.add_argument("target", help="File or directory path to clean")
    p_cln.add_argument("--output", "-o", default=None, help="Output destination file or directory")
    p_cln.add_argument("--in-place", action="store_true", help="Overwrite files in-place during batch cleaning")
    p_cln.add_argument("--keep-non-ai", action="store_true", help="Preserve standard non-AI metadata")
    p_cln.add_argument("--remove-pixel", choices=["ctrlregen", "diffusion"], default=None, help="Optional pixel removal backend")
    p_cln.add_argument("--json", action="store_true", help="Output JSON cleaning report")
    p_cln.set_defaults(func=cmd_clean)

    # analyze
    p_analyze = subparsers.add_parser("analyze", help="Analyze text for watermark signals & Unicode forensics")
    p_analyze.add_argument("file", nargs="?", default=None, help="Input text file path (or - for stdin)")
    p_analyze.add_argument("--text", "-t", default=None, help="Direct text string to analyze")
    p_analyze.add_argument("--text-escaped", default=None, help="Explicit Unicode-escaped text string (e.g. 'Hello\\u200bWorld')")
    p_analyze.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_analyze.add_argument("--markdown", action="store_true", help="Output GitHub-flavored Markdown")
    p_analyze.add_argument("--verbose", "-v", action="store_true", help="Include full hypothesis testing")
    p_analyze.add_argument("--threshold", type=float, default=None, help="Custom detection threshold (0.0 to 1.0)")
    p_analyze.add_argument("--algorithm", "-a", default="claude", help="Detector algorithm (claude, kirchenbauer, synthid, generic)")
    p_analyze.add_argument("--output", "-o", default=None, help="Save report to specified output path")
    p_analyze.set_defaults(func=cmd_analyze)

    # diff
    p_diff = subparsers.add_parser("diff", help="Forensic comparison between original and processed texts")
    p_diff.add_argument("file1", help="Original text file path")
    p_diff.add_argument("file2", help="Processed text file path")
    p_diff.add_argument("--json", action="store_true", help="Output JSON diff")
    p_diff.add_argument("--html", action="store_true", help="Generate side-by-side interactive HTML comparison")
    p_diff.add_argument("--algorithm", "-a", default="claude", help="Algorithm for score delta")
    p_diff.add_argument("--output", "-o", default=None, help="Save diff output to file")
    p_diff.set_defaults(func=cmd_diff)

    # unicode
    p_uni = subparsers.add_parser("unicode", help="Unicode and invisible character forensics")
    p_uni.add_argument("operation", choices=["inspect", "visualize", "normalize", "clean"], help="Operation to run")
    p_uni.add_argument("file", nargs="?", default=None, help="Target text file")
    p_uni.add_argument("--text", "-t", default=None, help="Direct text string")
    p_uni.add_argument("--text-escaped", default=None, help="Explicit Unicode-escaped text string (e.g. 'Hello\\u200bWorld')")
    p_uni.add_argument("--json", action="store_true", help="Output JSON report")
    p_uni.add_argument("--output", "-o", default=None, help="Destination output file")
    p_uni.set_defaults(func=cmd_unicode)

    # rewrite
    p_rw = subparsers.add_parser("rewrite", help="Best-effort statistical watermark disruption through text restructuring")
    p_rw.add_argument("file", nargs="?", default=None, help="Target text file")
    p_rw.add_argument("--text", "-t", default=None, help="Direct text string")
    p_rw.add_argument("--text-escaped", default=None, help="Explicit Unicode-escaped text string (e.g. 'Hello\\u200bWorld')")
    p_rw.add_argument("--strategy", choices=["synonym_cadence", "cadence_only"], default="synonym_cadence", help="Disruption strategy")
    p_rw.add_argument("--algorithm", "-a", default="claude", help="Detector to evaluate disruption against")
    p_rw.add_argument("--json", action="store_true", help="Output JSON evaluation")
    p_rw.add_argument("--output", "-o", default=None, help="Destination output file")
    p_rw.set_defaults(func=cmd_rewrite)

    # evaluate
    p_eval = subparsers.add_parser("evaluate", help="Evaluate before/after watermark score shifts and semantic similarity")
    p_eval.add_argument("file1", help="Original text file")
    p_eval.add_argument("file2", help="Rewritten / cleaned text file")
    p_eval.add_argument("--algorithm", "-a", default="claude", help="Detector to evaluate score shifts")
    p_eval.add_argument("--json", action="store_true", help="Output JSON evaluation report")
    p_eval.set_defaults(func=cmd_evaluate)

    # security
    p_sec = subparsers.add_parser("security", help="Defensive security inspection for zip bombs, malicious PDFs, and macros")
    p_sec.add_argument("target", help="Target file path to scan")
    p_sec.add_argument("--json", action="store_true", help="Output JSON security report")
    p_sec.set_defaults(func=cmd_security)

    # c2pa
    p_c2pa = subparsers.add_parser("c2pa", help="C2PA manifest inspection and provenance hierarchy extraction")
    p_c2pa.add_argument("target", help="Target file path to inspect")
    p_c2pa.add_argument("--json", action="store_true", help="Output JSON C2PA manifest")
    p_c2pa.set_defaults(func=cmd_c2pa)

    # agent
    p_agt = subparsers.add_parser("agent", help="AI Agent tool interface and dispatcher")
    p_agt_sub = p_agt.add_subparsers(dest="subcommand", help="Agent action")
    p_agt_list = p_agt_sub.add_parser("list", help="List all agent tools in JSON schema format")
    p_agt_tools = p_agt_sub.add_parser("tools", help="Alias for 'list': list all agent tools in JSON schema format")
    p_agt_exec = p_agt_sub.add_parser("exec", help="Execute an agent tool locally")
    p_agt_exec.add_argument("--tool", dest="tool_name", default=None, help="Name of tool to execute")
    p_agt_exec.add_argument("tool_name_pos", nargs="?", default=None, help="Tool name (positional, alternative to --tool)")
    p_agt_exec.add_argument("--args", default="{}", help="JSON string of arguments (e.g. '{\"file_path\":\"input.txt\"}')")
    p_agt.set_defaults(func=cmd_agent)

    # normalize
    p_norm = subparsers.add_parser("normalize", help="Safely strip invisible characters & normalize text")
    p_norm.add_argument("file", nargs="?", default=None, help="Input text file path (or - for stdin)")
    p_norm.add_argument("--text", "-t", default=None, help="Direct text string to normalize")
    p_norm.add_argument("--text-escaped", default=None, help="Explicit Unicode-escaped text string (e.g. 'Hello\\u200bWorld')")
    p_norm.add_argument("--json", action="store_true", help="Output JSON normalization details")
    p_norm.add_argument("--keep-zero-width", action="store_true", help="Do not remove zero-width characters")
    p_norm.add_argument("--keep-special-spaces", action="store_true", help="Do not replace non-breaking spaces")
    p_norm.add_argument("--replace-homoglyphs", action="store_true", help="Replace Latin-confusable homoglyphs")
    p_norm.add_argument("--unicode-form", choices=["NFC", "NFKC", "NFD", "NFKD", "none"], default="NFC", help="Unicode form")
    p_norm.add_argument("--output", "-o", default=None, help="Save normalized text to output file")
    p_norm.set_defaults(func=cmd_normalize)

    # capabilities
    p_caps = subparsers.add_parser("capabilities", help="Inspect available tools, detectors, and formats")
    p_caps.add_argument("--json", action="store_true", help="Output JSON capabilities")
    p_caps.set_defaults(func=cmd_capabilities)

    # experimental
    p_exp = subparsers.add_parser("experimental", help="Run empirical research and calibration benchmarks")
    p_exp.add_argument("--algorithm", "-a", default="claude", help="Detector to benchmark")
    p_exp.set_defaults(func=cmd_experimental)

    # audit
    p_audit = subparsers.add_parser("audit", help="Recursively audit directory tree for watermarks & provenance")
    p_audit.add_argument("subcommand_or_target", nargs="?", default=".", help="Directory to audit, or 'dir'/'site'")
    p_audit.add_argument("target_path", nargs="?", default=None, help="Target path when subcommand is specified")
    p_audit.add_argument("--max-files", type=int, default=1000, help="Maximum files to scan")
    p_audit.add_argument("--json", action="store_true", help="Output JSON audit report")
    p_audit.add_argument("--format", choices=["text", "json", "sarif"], default="text", help="Output format")
    p_audit.add_argument("--sarif", "-s", default=None, help="Save OASIS SARIF v2.1.0 report for GitHub Security")
    p_audit.add_argument("--fail-on", choices=["never", "any", "confirmed", "security"], default="never", help="CI exit failure threshold")
    p_audit.add_argument("--output", "-o", default=None, help="Save report to file")
    p_audit.set_defaults(func=cmd_audit)

    # doctor
    p_doc = subparsers.add_parser("doctor", help="Inspect local environment, binaries, format decoders, and security status")
    p_doc.add_argument("--json", action="store_true", help="Output JSON diagnostic report")
    p_doc.set_defaults(func=cmd_doctor)

    # selftest
    p_st = subparsers.add_parser("selftest", help="Run 9-point self-test diagnostic release gate")
    p_st.add_argument("--json", action="store_true", help="Output JSON diagnostic report")
    p_st.set_defaults(func=cmd_selftest)

    # benchmark
    p_bm = subparsers.add_parser("benchmark", help="Run reproducible scientific benchmark evaluation matrix")
    p_bm.add_argument("--reproduce", action="store_true", default=True, help="Run standard deterministic benchmark suite")
    p_bm.add_argument("--json", action="store_true", help="Output JSON benchmark metrics")
    p_bm.set_defaults(func=cmd_benchmark)

    # schema
    p_sch = subparsers.add_parser("schema", help="Export JSON Schemas for tool dispatch and API contracts")
    p_sch.add_argument("--json", action="store_true", default=True, help="Output formatted JSON")
    p_sch.set_defaults(func=cmd_schema)

    # version
    p_ver = subparsers.add_parser("version", help="Show ClaudeMark version and build info")
    p_ver.add_argument("--json", action="store_true", help="Output JSON version info")
    p_ver.set_defaults(func=cmd_version)

    return parser

def cmd_selftest(args: argparse.Namespace) -> int:
    from .core.selftest import print_selftest_report, run_selftest
    report = run_selftest()
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print_selftest_report(report)
    return 0 if report.overall_status == "PASS" else 1


def cmd_doctor(args: argparse.Namespace) -> int:
    from .core.doctor import print_doctor_report, run_doctor_diagnostics
    report = run_doctor_diagnostics()
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print_doctor_report(report)
    return 0 if report.overall_health == "HEALTHY" else 1

def cmd_benchmark(args: argparse.Namespace) -> int:
    from .core.benchmarks import print_benchmark_table, run_benchmark_suite
    result = run_benchmark_suite(reproduce=args.reproduce)
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print_benchmark_table(result)
    return 0

def cmd_schema(args: argparse.Namespace) -> int:
    from .agent.tools import AGENT_TOOLS_MANIFEST
    schema_manifest = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "ClaudeMarkForensicsSchema",
        "version": __version__,
        "tools": AGENT_TOOLS_MANIFEST,
    }
    print(json.dumps(schema_manifest, indent=2))
    return 0

def cmd_audit(args: argparse.Namespace) -> int:
    from .provenance.audit import audit_directory
    from .provenance.sarif import convert_audit_report_to_sarif, export_sarif

    raw_target = args.target_path if args.subcommand_or_target in ("dir", "directory") and args.target_path else args.subcommand_or_target
    target = _workspace_path(raw_target or ".")
    rep = audit_directory(target, max_files=args.max_files)

    if args.sarif:
        export_sarif(rep, Path(args.sarif))
        print(f"Generated OASIS SARIF v2.1.0 Report: {Path(args.sarif).resolve()}")

    if args.format == "sarif":
        sarif_json = json.dumps(convert_audit_report_to_sarif(rep), indent=2)
        _write_output(sarif_json, args.output)
    elif args.json or args.format == "json":
        _write_output(json.dumps(rep.to_dict(), indent=2), args.output)
    else:
        print(f"ClaudeMark Recursive Forensic Audit: {target}")
        print("═" * 60)
        print(f"Total Files Scanned:      {rep.total_files_scanned}")
        print(f"Suspicious Files:         {rep.total_suspicious_files}")
        print(f"Unicode Anomalies Found:  {rep.total_unicode_anomalies}")
        print(f"C2PA Manifests Detected:  {rep.total_c2pa_manifests}")
        print(f"Security Threats Flagged: {rep.total_security_threats}")
        if rep.findings:
            print("\nFindings Detail:")
            print("─" * 60)
            for f in rep.findings:
                print(f"[{f.confidence.upper()}] {f.finding_type} -> {Path(f.file_path).name}")
                print(f"    Details: {f.details}")

    # CI Policy Exit Code Evaluation
    if args.fail_on == "any" and (rep.total_suspicious_files > 0 or rep.total_unicode_anomalies > 0):
        return 1
    if args.fail_on == "security" and rep.total_security_threats > 0:
        return 1
    if args.fail_on == "confirmed" and (rep.total_c2pa_manifests > 0 or rep.total_security_threats > 0):
        return 1

    return 0


def cmd_version(args: argparse.Namespace) -> int:
    if getattr(args, "json", False):
        v_info = {
            "version": __version__,
            "author": __author__,
            "detectors": detector_registry.list_detectors(),
            "zero_egress": True,
        }
        print(json.dumps(v_info, indent=2))
    else:
        print(f"ClaudeMark v{__version__} (Core Engine & Forensic Suite)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    try:
        return args.func(args)
    except KeyboardInterrupt:
        sys.stderr.write("\nInterrupted by user.\n")
        return 130
    except Exception as ex:
        sys.stderr.write(f"Error: {ex}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

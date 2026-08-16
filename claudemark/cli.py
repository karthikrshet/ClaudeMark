"""Unified Command-line interface (CLI) for ClaudeMark."""

from __future__ import annotations

import argparse
import json
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

from . import __version__, analyze_text, compute_forensic_diff, normalize_text
from .core.normalizer import NormalizationOptions
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

MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB


def _read_input(file_path: str | None, raw_text: str | None) -> tuple[str, str]:
    """Read text from file, string argument, or stdin securely."""
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

    sys.stderr.write("Error: No input provided. Specify a file or pass --text.\n")
    sys.exit(1)


def _write_output(content: str, out_path: str | None) -> None:
    if out_path:
        p = Path(out_path).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        print(f"Report written to: {p}")
    else:
        print(content)


def cmd_analyze(args: argparse.Namespace) -> int:
    text, source_name = _read_input(args.file, args.text)
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
    target = Path(args.target).resolve()
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
    target = Path(args.target).resolve()
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

    if args.json:
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


def cmd_capabilities(args: argparse.Namespace) -> int:
    caps = {
        "version": __version__,
        "detectors": detector_registry.list_detectors(),
        "supported_document_formats": ["pdf", "docx", "odt", "html", "md", "txt"],
        "supported_image_formats": ["png", "jpeg", "jpg", "webp", "svg"],
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
        print(f"Document Formats:     {', '.join(caps['supported_document_formats'])}")
        print(f"Image Formats:        {', '.join(caps['supported_image_formats'])}")
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
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # serve
    p_srv = subparsers.add_parser("serve", help="Start ClaudeMark Web UI and REST API server")
    p_srv.add_argument("--host", default="127.0.0.1", help="Host interface to bind")
    p_srv.add_argument("--port", type=int, default=8765, help="Port to listen on")
    p_srv.set_defaults(func=cmd_serve)

    # inspect
    p_insp = subparsers.add_parser("inspect", help="Inspect file or directory for C2PA, EXIF, XMP, and AI marks")
    p_insp.add_argument("target", help="File or directory path to inspect")
    p_insp.add_argument("--json", action="store_true", help="Output machine-readable JSON")
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
    p_diff.add_argument("--algorithm", "-a", default="claude", help="Algorithm for score delta")
    p_diff.add_argument("--output", "-o", default=None, help="Save diff output to file")
    p_diff.set_defaults(func=cmd_diff)

    # capabilities
    p_caps = subparsers.add_parser("capabilities", help="Inspect available tools, detectors, and formats")
    p_caps.add_argument("--json", action="store_true", help="Output JSON capabilities")
    p_caps.set_defaults(func=cmd_capabilities)

    # normalize
    p_norm = subparsers.add_parser("normalize", help="Safely normalize text removing invisible watermark markers")
    p_norm.add_argument("file", nargs="?", default=None, help="Input text file path")
    p_norm.add_argument("--text", "-t", default=None, help="Direct text string to normalize")
    p_norm.add_argument("--output", "-o", default=None, help="Output cleaned file path")
    p_norm.add_argument("--nfkc", action="store_true", help="Use NFKC compatibility normalization instead of NFC")
    p_norm.add_argument("--replace-homoglyphs", action="store_true", help="Replace Latin-confusable homoglyphs")
    p_norm.add_argument("--keep-zero-width", action="store_true", help="Do not strip zero-width characters")
    p_norm.add_argument("--keep-spaces", action="store_true", help="Do not normalize special spaces to ASCII")
    p_norm.add_argument("--keep-bidi", action="store_true", help="Do not strip BiDi controls")
    p_norm.add_argument("--verbose", "-v", action="store_true", help="Print summary banner")
    p_norm.set_defaults(func=cmd_normalize)

    # report
    p_rep = subparsers.add_parser("report", help="Generate detailed Markdown or JSON forensic report")
    p_rep.add_argument("file", nargs="?", default=None, help="Input text file path")
    p_rep.add_argument("--text", "-t", default=None, help="Direct text string")
    p_rep.add_argument("--json", action="store_true", help="Output JSON format")
    p_rep.add_argument("--markdown", action="store_true", default=True, help="Output Markdown format")
    p_rep.add_argument("--verbose", "-v", action="store_true", help="Include full hypothesis")
    p_rep.add_argument("--threshold", type=float, default=None, help="Custom threshold")
    p_rep.add_argument("--algorithm", "-a", default="claude", help="Watermark algorithm")
    p_rep.add_argument("--output", "-o", default=None, help="Output file path")
    p_rep.set_defaults(func=cmd_report)

    # experimental
    p_exp = subparsers.add_parser("experimental", help="Run experimental calibration & threshold sweep")
    p_exp.add_argument("--algorithm", "-a", default="claude", help="Algorithm to sweep")
    p_exp.set_defaults(func=cmd_experimental)

    # version
    p_ver = subparsers.add_parser("version", help="Print version & active detectors")
    p_ver.set_defaults(func=cmd_version)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

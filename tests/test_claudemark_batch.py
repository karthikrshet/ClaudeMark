"""Unit tests for ClaudeMark batch directory inspection and cleaning."""

from pathlib import Path
import pytest
from claudemark.provenance.batch import batch_clean, batch_inspect


def test_batch_inspect_and_clean_directory(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    f1 = docs_dir / "doc1.txt"
    f2 = docs_dir / "doc2.md"
    f3 = docs_dir / "ignored.bin"

    f1.write_text("Hello\u200b test 1", encoding="utf-8")
    f2.write_text("# Doc 2\n\nSample\u200c content", encoding="utf-8")
    f3.write_bytes(b"\x00\x01\x02\x03")

    # Batch inspect
    insp_res = batch_inspect(docs_dir)
    assert insp_res.total_files_scanned == 3
    assert insp_res.supported_files_count == 2
    assert insp_res.suspicious_count == 2

    # Batch clean
    out_dir = tmp_path / "cleaned_docs"
    clean_res = batch_clean(docs_dir, output_dir=out_dir)
    assert clean_res.cleaned_count == 2

    cleaned_f1 = out_dir / "doc1.txt"
    cleaned_f2 = out_dir / "doc2.md"
    assert cleaned_f1.is_file()
    assert cleaned_f2.is_file()
    assert "\u200b" not in cleaned_f1.read_text(encoding="utf-8")
    assert "\u200c" not in cleaned_f2.read_text(encoding="utf-8")

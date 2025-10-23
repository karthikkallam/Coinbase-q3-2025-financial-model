import sys
from pathlib import Path

from pdfminer.high_level import extract_text


def extract_pdf_to_txt(pdf_path: Path, dest: Path) -> None:
    text = extract_text(str(pdf_path))
    dest.write_text(text, encoding="utf-8")


def main(root: str) -> None:
    root_path = Path(root)
    out_dir = root_path / "output" / "text_cache"
    out_dir.mkdir(parents=True, exist_ok=True)
    for pdf_path in root_path.rglob("*.pdf"):
        rel = pdf_path.relative_to(root_path)
        dest = out_dir / rel.with_suffix(".txt")
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            extract_pdf_to_txt(pdf_path, dest)
        except Exception as exc:
            dest.write_text(f"ERROR extracting {pdf_path}: {exc}\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pdf_to_text.py <root>")
        sys.exit(1)
    main(sys.argv[1])

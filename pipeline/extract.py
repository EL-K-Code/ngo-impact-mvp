from pathlib import Path
import fitz


def extract_document(pdf_path: str) -> dict:
    doc = fitz.open(pdf_path)
    pages = []

    for i, page in enumerate(doc):
        text = page.get_text("text") or ""
        pages.append(
            {
                "page_number": i + 1,
                "text": text,
            }
        )

    doc.close()

    return {
        "file_name": Path(pdf_path).name,
        "file_path": str(Path(pdf_path).resolve()),
        "page_count": len(pages),
        "pages": pages,
        "full_text": "\n\n".join(page["text"] for page in pages),
    }

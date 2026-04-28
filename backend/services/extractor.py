import pdfplumber
from docx import Document


class TextExtractor:
    def extract(self, file_path: str, filetype: str) -> str:
        if filetype == "pdf":
            return self._extract_pdf(file_path)
        elif filetype == "docx":
            return self._extract_docx(file_path)
        elif filetype in ("md", "txt"):
            return self._extract_text(file_path)
        else:
            raise ValueError(f"Unsupported filetype: {filetype}")

    def _extract_pdf(self, file_path: str) -> str:
        with pdfplumber.open(file_path) as pdf:
            pages = [page.extract_text() for page in pdf.pages]
        return "\n\n".join(page for page in pages if page)

    def _extract_docx(self, file_path: str) -> str:
        doc = Document(file_path)
        return "\n\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text)

    def _extract_text(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

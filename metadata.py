import sys
import os
from docx2pdf import convert
from pathlib import Path
from PyPDF2 import PdfReader


class PageCounter:
    """Считает количество страниц в PDF или DOCX файле."""

    def count_pages(self, file_path: str | Path) -> int | None:
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            return self._get_pdf_pages(path)
        elif suffix == ".docx":
            return self._get_docx_pages(path)
        else:
            raise ValueError(f"Неподдерживаемый формат: '{suffix}'. Ожидается .pdf или .docx")

    def _get_pdf_pages(self, path: Path) -> int:
        reader = PdfReader(path)
        return len(reader.pages)

    def _get_docx_pages(self, path: Path) -> int | None:
        try:
            convert(path, "temp.pdf")

            with open("temp.pdf", "rb") as f:
                pdf = PdfReader(f)
                pages = len(pdf.pages)

            # Опционально: удаляем временный PDF
            os.unlink("temp.pdf")

            return pages

        except Exception as e:
            print(f"  [!] Ошибка конвертации OnlyOffice: {e}", file=sys.stderr)
            return None


if __name__ == "__main__":
    counter = PageCounter()

    for filename in ["docs/БУКВЫ.docx", "docs/Уведомление(RU).pdf"]:
        try:
            pages = counter.count_pages(filename)
            print(f"{filename}: {pages} стр.")
        except ValueError as e:
            print(f"Ошибка: {e}")
from PyPDF2 import PdfReader

def get_pdf_pages(file_path):
    reader = PdfReader(file_path)
    return len(reader.pages)

if __name__ == "__main__":
    file_path = r"C:\Users\Astana\Desktop\Client\Болат\сен 2023 - янв 2024.pdf"
    num_pages = get_pdf_pages(file_path)
    print(f"Количество страниц в файле: {num_pages}")
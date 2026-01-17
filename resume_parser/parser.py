import os
import PyPDF2
import docx


# ---------------- PDF TEXT EXTRACTION ----------------
def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + " "
    except Exception as e:
        print("PDF parsing error:", e)
    return text.strip()


# ---------------- DOCX TEXT EXTRACTION ----------------
def extract_text_from_docx(file_path: str) -> str:
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print("DOCX parsing error:", e)
    return text.strip()


# ---------------- MAIN PARSER ----------------
def parse_resume(file_path: str) -> str:
    if not os.path.exists(file_path):
        return ""

    if file_path.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_path)

    if file_path.lower().endswith(".docx"):
        return extract_text_from_docx(file_path)

    return ""

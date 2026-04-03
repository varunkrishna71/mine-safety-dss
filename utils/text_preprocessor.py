import PyPDF2
import docx
import re

def extract_text_from_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception:
        return ""

def extract_text_from_docx(file):
    try:
        doc = docx.Document(file)
        return " ".join([para.text for para in doc.paragraphs])
    except Exception:
        return ""

def clean_text(text):
    # Remove special characters but keep percentages and decimals
    text = text.lower()
    text = re.sub(r'[^a-z0-9.% ]', ' ', text)
    return " ".join(text.split())

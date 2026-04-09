import os
import pdfplumber

DATA_PATH = "data"

def save_pdf(uploaded_file):
    os.makedirs(DATA_PATH, exist_ok=True)
    file_path = os.path.join(DATA_PATH, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def list_pdfs():
    if not os.path.exists(DATA_PATH):
        return []
    return [f for f in os.listdir(DATA_PATH) if f.endswith('.pdf')]

def delete_pdf(filename):
    file_path = os.path.join(DATA_PATH, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

def load_all_pdfs():
    text = ""
    if not os.path.exists(DATA_PATH):
        return text

    for file in os.listdir(DATA_PATH):
        if not file.endswith('.pdf'):
            continue
        file_path = os.path.join(DATA_PATH, file)
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error reading {file}: {e}")

    return text
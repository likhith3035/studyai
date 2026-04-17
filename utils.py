import os
import pdfplumber
import json

DATA_PATH = "data"
SUPPORTED_EXTENSIONS = ('.pdf', '.json', '.txt', '.md')

def save_document(uploaded_file):
    os.makedirs(DATA_PATH, exist_ok=True)
    file_path = os.path.join(DATA_PATH, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def list_documents():
    if not os.path.exists(DATA_PATH):
        return []
    return [f for f in os.listdir(DATA_PATH) if f.lower().endswith(SUPPORTED_EXTENSIONS)]

def delete_document(filename):
    file_path = os.path.join(DATA_PATH, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

def load_all_documents():
    text = ""
    if not os.path.exists(DATA_PATH):
        return text

    for file in os.listdir(DATA_PATH):
        if not file.lower().endswith(SUPPORTED_EXTENSIONS):
            continue
        
        file_path = os.path.join(DATA_PATH, file)
        try:
            if file.lower().endswith('.pdf'):
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            
            elif file.lower().endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    text += json.dumps(data, indent=2) + "\n"
                    
            elif file.lower().endswith(('.txt', '.md')):
                with open(file_path, 'r', encoding='utf-8') as f:
                    text += f.read() + "\n"
                    
        except Exception as e:
            print(f"Error reading {file}: {e}")

    return text
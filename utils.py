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
    docs = []
    if not os.path.exists(DATA_PATH):
        return docs

    for file in os.listdir(DATA_PATH):
        if not file.lower().endswith(SUPPORTED_EXTENSIONS):
            continue
        
        file_path = os.path.join(DATA_PATH, file)
        try:
            if file.lower().endswith('.pdf'):
                with pdfplumber.open(file_path) as pdf:
                    pdf_text = []
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            pdf_text.append(page_text)
                    if pdf_text:
                        docs.append({"text": "\n".join(pdf_text), "metadata": {"source": file}})
            
            elif file.lower().endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and "text" in item:
                                docs.append({
                                    "text": item["text"],
                                    "metadata": item.get("metadata", {"source": file})
                                })
                    
            elif file.lower().endswith(('.txt', '.md')):
                with open(file_path, 'r', encoding='utf-8') as f:
                    docs.append({"text": f.read(), "metadata": {"source": file}})
                    
        except Exception as e:
            print(f"Error reading {file}: {e}")

    return docs
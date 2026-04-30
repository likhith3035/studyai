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
                    for i, page in enumerate(pdf.pages):
                        page_text = page.extract_text()
                        if page_text:
                            docs.append({"text": page_text, "metadata": {"source": file, "page": i + 1}})
            
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

def get_document_metadata(filename):
    file_path = os.path.join(DATA_PATH, filename)
    if not os.path.exists(file_path):
        return None
        
    stat = os.stat(file_path)
    # Get modified time (behaves identically to upload time here)
    upload_time = stat.st_mtime
    
    file_type = "pdf"
    if filename.lower().endswith(".json"): file_type = "json"
    elif filename.lower().endswith((".txt", ".md")): file_type = "txt"
    
    return {
        "file_name": filename,
        "upload_time": upload_time,
        "file_type": file_type,
        "file_path": file_path
    }

def get_document_preview(filename):
    file_path = os.path.join(DATA_PATH, filename)
    if not os.path.exists(file_path):
        return None
        
    try:
        if filename.lower().endswith('.pdf'):
            with pdfplumber.open(file_path) as pdf:
                preview = []
                for i, page in enumerate(pdf.pages[:2]): # Preview first 2 pages
                    text = page.extract_text()
                    if text: preview.append(f"--- PAGE {i+1} ---\n{text}")
                return "\n\n".join(preview) if preview else "No readable text found."
                
        elif filename.lower().endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f) # Return dict for st.json()
                
        elif filename.lower().endswith(('.txt', '.md')):
            with open(file_path, 'r', encoding='utf-8') as f:
                # Preview up to 2000 chars to avoid memory bloat
                content = f.read(2000)
                if len(content) == 2000:
                    content += "\n...[Content Truncated]..."
                return content
    except Exception as e:
        return f"Error loading preview: {str(e)}"
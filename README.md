# 🤖 Study AI: Premium RAG Chatbot with Auto-Diagrams

Welcome to **Study AI**, a high-performance, local-first RAG (Retrieval-Augmented Generation) application designed to transform your study materials into interactive learning experiences. 

Study AI allows you to upload PDFs, chat with them using local LLMs, generate quizzes, and visualize complex processes automatically through Mermaid.js diagrams.

---

## ✨ Key Features

- **💬 Intelligent RAG Chat**: Ask questions about your documents. The AI searches your PDFs and provides answers grounded in your specific context.
- **📊 Auto-Mermaid Diagrams**: When the AI explains processes, workflows, or architectures, it automatically generates a visual **Mermaid diagram** alongside the text.
- **📝 MCQ Quiz Generator**: Instantly generate challenging 5-question multiple-choice quizzes from your study notes to test your knowledge.
- **🛠️ Admin Control Center**: Easily upload, manage, and delete PDF documents. The knowledge base re-indexes automatically on every change.
- **📤 Export & Share**: Download your entire chat history as a JSON file or copy it as formatted text to share with study groups.
- **🏗️ Multi-Model Support**: Switch between different local LLMs like `llama3`, `mistral`, `gemma`, and `phi3` on the fly.
- **💎 Premium UI**: A sleek, modern interface built with Streamlit, featuring custom CSS, glassmorphism-inspired elements, and smooth interactions.

---

## 🛠️ Tech Stack

- **Frontend/API**: [Streamlit](https://streamlit.io/)
- **LLM Engine**: [Ollama](https://ollama.com/) (Local generation)
- **Vector Database**: [FAISS](https://github.com/facebookresearch/faiss) (Fast indexing and similarity search)
- **Embeddings**: `sentence-transformers` (`all-MiniLM-L6-v2`)
- **PDF Parsing**: `pdfplumber`
- **Visuals**: `Mermaid.js` (Rendered via custom HTML components)

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have **Python 3.10+** and **Ollama** installed on your system.

### 2. Install Ollama & Models
Download Ollama from [ollama.com](https://ollama.com). Once installed, pull the models you wish to use:
```bash
ollama pull llama3
ollama pull mistral
```

### 3. Clone & Install Dependencies
```bash
# Clone the repository
git clone <your-repo-url>
cd studyAibylikik

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install streamlit requests sentence-transformers faiss-cpu pdfplumber numpy
```

### 4. Run the Application
```bash
streamlit run app.py
```

---

## 📖 How to Use

1. **Upload Documents**: Go to the **🛠️ Admin Space** in the sidebar. Upload one or more PDFs (e.g., lecture notes, research papers).
2. **Chat**: Switch to **💬 User Chat**. Ask anything like *"Explain the main concept in the document"* or *"Create a flowchart of the process described."*
3. **Take a Quiz**: Switch to **📝 Quiz Generator** and click **🚀 Generate New Quiz**.
4. **Export**: Use the sidebar buttons to download your session for later review.

---

## 📂 Project Structure

- `app.py`: The main Streamlit entry point, UI logic, and state management.
- `llm.py`: Interface for Ollama API, prompt engineering, and streaming logic.
- `rag_faiss.py`: Vector database logic (creating the index and performing similarity searches).
- `text_processor.py`: Smart text chunking to ensure context is preserved.
- `utils.py`: PDF file management and parsing logic.
- `data/`: (Auto-created) Directory where your uploaded PDFs are stored.

---

## ⚠️ Important Notes
- **Ollama must be running**: The app communicates with Ollama's local API (`http://localhost:11434`).
- **Resource Usage**: Embedding generation happens on the first load or when "Reload Data Index" is clicked. Large PDFs may take a few seconds to index initially.
- **Safety**: This app is designed for local use. Your data stays on your machine and never leaves your local network.

---

*Built with ❤️ for students and researchers.*
developer :- Likhiith

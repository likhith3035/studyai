import streamlit as st
import time
import re
import streamlit.components.v1 as components
from text_processor import chunk_text
from rag_faiss import create_index, search, search_legacy
from llm import generate_answer_stream, generate_hybrid_answer_stream, classify_relevance, basic_chat, generate_quiz_stream, generate_summary_stream, generate_flashcards_stream, generate_mindmap_stream, generate_cheatsheet_stream, generate_study_plan_stream, generate_quiz_evaluate_stream, generate_diagram_for_text_stream
from utils import save_document, load_all_documents, list_documents, delete_document, get_document_metadata, get_document_preview
import socket
import urllib.parse

def get_network_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


# ---------------- CONFIG ---------------- #
st.set_page_config(page_title="Study AI: Premium RAG", page_icon="🤖", layout="wide")

# ---------------- CSS (🔥 STITCH AI: LUMINA ACADEMIC) ---------------- #
st.markdown("""
<style>
/* === STITCH AI: "LUMINA ACADEMIC" DESIGN SYSTEM === */
/* Creative North Star: The Ethereal Library */
/* Fonts: Space Grotesk (headlines) + Manrope (body) */

@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Manrope:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400&display=swap');

/* --- ROOT VARIABLES --- */
:root {
    --bg: #0b1326;
    --surface: #0b1326;
    --surface-container-low: #131b2e;
    --surface-container: #171f33;
    --surface-container-high: #222a3d;
    --surface-container-highest: #2d3449;
    --surface-variant: #2d3449;
    --primary: #bdc2ff;
    --primary-container: #7c87f3;
    --secondary: #ddb8ff;
    --secondary-container: #62259b;
    --tertiary: #3cddc7;
    --tertiary-container: #008678;
    --on-surface: #dae2fd;
    --on-surface-variant: #c7c4d7;
    --outline: #908fa0;
    --outline-variant: #464554;
    --error: #ffb4ab;
}

/* --- GLOBAL RESET --- */
html, body, [class*="css"] {
    font-family: 'Manrope', sans-serif !important;
    color: var(--on-surface);
}

.main .block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

/* --- STREAMLIT OVERRIDES --- */
[data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
}

[data-testid="stSidebar"] {
    background: rgba(19, 27, 46, 0.65) !important;
    backdrop-filter: blur(32px) !important;
    -webkit-backdrop-filter: blur(32px) !important;
    border-right: 1px solid rgba(70, 69, 84, 0.15);
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
[data-testid="stSidebar"] label {
    color: var(--on-surface-variant) !important;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

/* --- ANIMATED GRADIENT TITLE --- */
@keyframes gradient-x {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 15px rgba(124, 135, 243, 0.15); }
    50% { box-shadow: 0 0 25px rgba(124, 135, 243, 0.35); }
}

.premium-title {
    font-family: 'Space Grotesk', sans-serif !important;
    background: linear-gradient(270deg, var(--primary), var(--secondary), var(--tertiary), var(--primary));
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3.2rem;
    font-weight: 700;
    margin-bottom: 4px;
    animation: gradient-x 10s ease infinite;
    letter-spacing: -1.5px;
}

/* --- SUBTITLE --- */
.subtitle-text {
    color: var(--on-surface-variant);
    font-size: 0.95rem;
    font-weight: 400;
    margin-bottom: 1.5rem;
    opacity: 0.7;
}

/* --- CHAT BUBBLES WITH FADE-IN --- */
.stChatMessage {
    background: transparent !important;
    padding: 4px 0 !important;
    animation: fadeSlideUp 0.4s ease-out;
}

div[data-testid="chatAvatarIcon-user"] {
    background: linear-gradient(135deg, var(--primary-container), var(--primary)) !important;
}

div[data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, var(--secondary-container), var(--secondary)) !important;
}

div[data-testid="stChatMessageContent"] {
    padding: 1.1rem 1.3rem;
    border-radius: 16px;
    font-size: 0.95rem;
    line-height: 1.7;
    animation: fadeSlideUp 0.3s ease-out;
}

/* User Message Block */
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) div[data-testid="stChatMessageContent"] {
    background: var(--surface-container-highest);
    border-bottom-right-radius: 4px;
}

/* Assistant Message Block — Glass with AI Glow */
.stChatMessage:has([data-testid="chatAvatarIcon-assistant"]) div[data-testid="stChatMessageContent"] {
    background: rgba(124, 135, 243, 0.08);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(70, 69, 84, 0.15);
    border-bottom-left-radius: 4px;
    box-shadow: 0 20px 40px rgba(0, 7, 103, 0.12), inset 0 -2px 12px rgba(60, 221, 199, 0.06);
}

/* --- BUTTONS: Ghost Glass --- */
.stButton > button {
    font-family: 'Manrope', sans-serif !important;
    font-weight: 600;
    background: linear-gradient(135deg, rgba(189, 194, 255, 0.06), rgba(189, 194, 255, 0.02)) !important;
    border: 1px solid rgba(70, 69, 84, 0.2) !important;
    border-radius: 12px;
    padding: 0.6rem 1.2rem;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    color: var(--on-surface) !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 24px rgba(0, 7, 103, 0.2);
    border-color: rgba(124, 135, 243, 0.4) !important;
    background: linear-gradient(135deg, rgba(189, 194, 255, 0.12), rgba(189, 194, 255, 0.04)) !important;
}
.stButton > button:active {
    transform: translateY(0);
}

/* --- INPUT FIELDS: Pill-shaped Glow --- */
[data-testid="stChatInput"] {
    border-radius: 9999px !important;
}
[data-testid="stChatInput"] textarea {
    background: var(--surface-container-lowest, #060e20) !important;
    border: 1px solid rgba(70, 69, 84, 0.2) !important;
    border-radius: 9999px !important;
    color: var(--on-surface) !important;
    font-family: 'Manrope', sans-serif !important;
    transition: all 0.3s ease;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 15px rgba(189, 194, 255, 0.25) !important;
}

/* --- SELECT BOXES --- */
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: var(--surface-container) !important;
    border: 1px solid rgba(70, 69, 84, 0.2) !important;
    border-radius: 10px;
    color: var(--on-surface) !important;
}

/* --- EXPANDERS --- */
[data-testid="stExpander"] {
    background: var(--surface-container-low) !important;
    border: 1px solid rgba(70, 69, 84, 0.1) !important;
    border-radius: 12px !important;
}

/* --- FLASHCARDS: Tonal Layering --- */
.flashcard-container {
    perspective: 1200px;
}
.flashcard {
    background: rgba(34, 42, 61, 0.7);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(70, 69, 84, 0.15);
    border-radius: 24px;
    padding: 48px 36px;
    min-height: 280px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--on-surface);
    cursor: pointer;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    box-shadow: 0 20px 40px rgba(0, 7, 103, 0.12);
    animation: pulse-glow 4s ease-in-out infinite;
}
.flashcard:hover {
    border-color: var(--primary-container);
    transform: translateY(-6px) scale(1.01);
    box-shadow: 0 30px 50px rgba(124, 135, 243, 0.2);
}
.flashcard-answer {
    color: var(--tertiary);
}

/* --- CODE BLOCKS --- */
code {
    font-family: 'JetBrains Mono', monospace !important;
    color: var(--tertiary) !important;
    background: rgba(6, 14, 32, 0.6) !important;
    border-radius: 6px;
    padding: 2px 6px;
}
pre {
    border-radius: 14px !important;
    border: 1px solid rgba(70, 69, 84, 0.15) !important;
    background: var(--surface-container-lowest, #060e20) !important;
}

/* --- WARNINGS & INFO --- */
[data-testid="stAlert"] {
    background: var(--surface-container) !important;
    border: 1px solid rgba(70, 69, 84, 0.15) !important;
    border-radius: 12px;
}

/* --- DIVIDERS --- */
hr {
    border-color: rgba(70, 69, 84, 0.15) !important;
}

/* --- SCROLLBAR STYLING --- */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-track {
    background: var(--surface-container-low);
}
::-webkit-scrollbar-thumb {
    background: var(--outline-variant);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: var(--outline);
}

/* --- RADIO BUTTONS: Nav-style --- */
[data-testid="stRadio"] label {
    font-family: 'Manrope', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.2s ease;
}
[data-testid="stRadio"] label:hover {
    color: var(--primary) !important;
}

/* --- SPINNER --- */
[data-testid="stSpinner"] {
    color: var(--tertiary) !important;
}

/* --- METRIC / CAPTION TEXT --- */
.stCaption, [data-testid="stCaptionContainer"] {
    color: var(--on-surface-variant) !important;
    opacity: 0.6;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HELPERS ---------------- #
def normalize_query(query):
    q_lower = query.lower()
    show_image = any(w in q_lower for w in ["pic", "pic ", "image", "photo", "show "])
    
    expansions = {
        r"\bhod\b": "head of department"
        # Removing drastic acronym expansions to prevent semantic drift
    }
    
    expanded = q_lower
    for k, v in expansions.items():
        expanded = re.sub(k, v, expanded)
        
    return expanded, show_image

def render_profile_card(meta, show_image=False):
    if not isinstance(meta, dict):
        return
    if not any(k in meta for k in ["name", "image_url", "profile_url"]):
        return
        
    st.markdown('''
<div style="padding: 16px; border-radius: 12px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255,255,255,0.1); margin-bottom: 16px;">
''', unsafe_allow_html=True)
    
    cols = st.columns([1, 4])
    with cols[0]:
        if "image_url" in meta and show_image:
            st.image(meta["image_url"], width=120)
        else:
            st.markdown("<h3>👤</h3>", unsafe_allow_html=True)
            
    with cols[1]:
        if "name" in meta:
            st.subheader(meta["name"])
        if "role" in meta:
            st.markdown(f"**{meta['role']}**")
        if "department" in meta:
            st.caption(meta["department"])
            
        b_cols = st.columns([1, 1, 2])
        if "profile_url" in meta:
            b_cols[0].link_button("🔗 View Profile", meta["profile_url"], use_container_width=True)
        if "image_url" in meta:
            b_cols[1].link_button("🖼️ View Image", meta["image_url"], use_container_width=True)
            
    st.markdown("</div>", unsafe_allow_html=True)

@st.cache_resource
def load_rag():
    docs = load_all_documents()
    chunks = chunk_text(docs)
    index = create_index(chunks)
    return chunks, index

def sanitize_mermaid(code: str) -> str:
    """Aggressively cleans up common LLM mistakes in Mermaid syntax."""
    code = re.sub(r'-->\|[^|]*\|>\s*', '--> ', code)
    code = re.sub(r'-->\|[^|]*\|\s*', '--> ', code)
    code = re.sub(r';\s*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'\(([^)]*)\)', r'- \1', code)
    return code

def render_mermaid(code: str):
    """Renders Mermaid code with high-res PNG download functionality."""
    clean_code = sanitize_mermaid(code)
    escaped_code = clean_code.replace('`', '\\`')
    components.html(
        f"""
        <div id="mermaid-outer" style="display:flex; flex-direction:column; align-items:center; gap:12px;">
            <div id="mermaid-container"></div>
            <button id="dl-btn" onclick="downloadPNG()" style="
                display:none; 
                background: rgba(59, 130, 246, 0.1);
                border: 1px solid rgba(59, 130, 246, 0.3);
                color: #60a5fa;
                padding: 6px 14px;
                border-radius: 20px;
                cursor: pointer;
                font-family: sans-serif;
                font-size: 12px;
                transition: all 0.3s;
                backdrop-filter: blur(5px);
            ">📥 Download PNG</button>
        </div>
        
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: false, theme: 'dark' }});
            
            const container = document.getElementById('mermaid-container');
            const btn = document.getElementById('dl-btn');
            const code = `{escaped_code}`;
            
            window.downloadPNG = async () => {{
                const svgElement = container.querySelector('svg');
                if (!svgElement) return;
                
                const svgData = new XMLSerializer().serializeToString(svgElement);
                const canvas = document.createElement("canvas");
                const ctx = canvas.getContext("2d");
                const img = new Image();
                
                img.onload = () => {{
                    const scale = 2; 
                    canvas.width = img.width * scale;
                    canvas.height = img.height * scale;
                    ctx.fillStyle = "#0b1326";
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                    
                    const link = document.createElement("a");
                    link.download = "study_ai_diagram.png";
                    link.href = canvas.toDataURL("image/png");
                    link.click();
                }};
                img.src = "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(svgData)));
            }};

            try {{
                const {{ svg }} = await mermaid.render('mermaid-diagram', code);
                container.innerHTML = svg;
                btn.style.display = 'block';
            }} catch (e) {{
                container.innerHTML = `
                    <div style="background:#1e293b; border:1px solid #334155; border-radius:8px; padding:16px; font-family:monospace; color:#94a3b8; font-size:13px; white-space:pre-wrap;">
                        <div style="color:#60a5fa; margin-bottom:8px; font-family:sans-serif;">📊 Diagram (raw code):</div>
                        ${{code}}
                    </div>`;
            }}
        </script>
        <style>
            #dl-btn:hover {{
                background: rgba(59, 130, 246, 0.2);
                border-color: rgba(59, 130, 246, 0.6);
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
            }}
        </script>
        """,
        height=450,
        scrolling=True
    )

def speak_text(text: str):
    """Injects a small JS snippet to speak text using the browser Web Speech API."""
    cleaned_text = text.replace("'", "\\'").replace("\n", " ").replace("`", "").replace('"', '')
    components.html(
        f"""
        <script>
            window.speechSynthesis.cancel();
            const msg = new SpeechSynthesisUtterance('{cleaned_text}');
            msg.rate = 0.95;
            msg.pitch = 1.0;
            window.speechSynthesis.speak(msg);
        </script>
        """,
        height=0,
        width=0
    )

def stop_speech():
    """Injects JS to stop any currently playing speech."""
    components.html(
        """
        <script>
            window.speechSynthesis.cancel();
        </script>
        """,
        height=0,
        width=0
    )

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.title("⚙️ Control Panel")
    
    st.subheader("🌐 Network Access")
    network_url = f"http://{get_network_ip()}:8501"
    st.caption("Access on mobile (same Wi-Fi):")
    st.code(network_url)
    
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={urllib.parse.quote(network_url)}&color=bdc2ff&bgcolor=0b1326"
    st.image(qr_url, width=150)
    st.divider()
    
    st.subheader("🤖 LLM Configuration")
    model_url = st.text_input("LLM Server URL", value="http://127.0.0.1:1234", help="Ollama: http://localhost:11434 | LM Studio: http://127.0.0.1:1234")
    model_choice = st.text_input("LLM Model Identifier", value="google/gemma-4-e4b", help="Example: llama3, gemma, or the full path from LM Studio")

    st.divider()
    mode = st.radio("App Mode", ["💬 User Chat", "📝 Quiz Generator", "📚 Master Summary", "🗂️ Flashcard Center", "🧠 Mind Map Explorer", "📊 Cheat Sheet", "📅 Study Planner", "🛠️ Admin Space"])

    if st.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.button("🔄 Reload Data Index", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()

    st.divider()
    
    st.subheader("⏱️ Pomodoro Timer")
    # A simple UI for Pomodoro; logic is tricky in Streamlit statelessness, so we provide an interactive HTML widget.
    components.html(
        """
        <div style="font-family: sans-serif; text-align: center; color: white;">
            <h1 id="time" style="font-size: 3rem; margin: 0;">25:00</h1>
            <button onclick="startTimer()" style="padding: 10px 20px; margin-top: 10px; background: #3b82f6; border: none; color: white; border-radius: 5px; cursor: pointer;">Start Focus</button>
            <button onclick="resetTimer()" style="padding: 10px 20px; margin-top: 10px; background: #ef4444; border: none; color: white; border-radius: 5px; cursor: pointer;">Break</button>
        </div>
        <script>
            let time = 1500;
            let timer = null;
            function updateDisplay() {
                let m = Math.floor(time/60).toString().padStart(2, '0');
                let s = (time%60).toString().padStart(2, '0');
                document.getElementById('time').innerText = m + ":" + s;
            }
            function startTimer() {
                if(timer) clearInterval(timer);
                time = 1500; updateDisplay();
                timer = setInterval(() => { if(time>0) {time--; updateDisplay();} }, 1000);
            }
            function resetTimer() {
                if(timer) clearInterval(timer);
                time = 300; updateDisplay();
                timer = setInterval(() => { if(time>0) {time--; updateDisplay();} }, 1000);
            }
        </script>
        """,
        height=180
    )

    st.divider()
    
    st.subheader("📤 Export & Share")
    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        import json
        chat_data = json.dumps(st.session_state.messages, indent=2)
        st.download_button(
            label="Download Chat History (JSON)",
            data=chat_data,
            file_name=f"chat_export_{int(time.time())}.json",
            mime="application/json",
            use_container_width=True
        )
    else:
        st.info("No chat history to export yet.")

    st.divider()

    with st.expander("📖 How to Use", expanded=False):
        st.markdown("""
**1. Upload Documents (Admin)**
- Switch to **🛠️ Admin Space** mode.
- Upload your study PDFs. They will be indexed automatically.

**2. Chat with AI (User)**
- Switch to **💬 User Chat** mode.
- Ask questions. AI will reference your docs and add diagrams.
- Click **🔊 Read Aloud** to hear the answer.

**3. Master Summary 📚**
- Get a complete "CliffNotes" study guide for all your documents at once.

**4. Flashcard Center 🗂️**
- Test your memory with AI-generated cards. Flip them to see answers!

**5. Quiz Generator 📝**
- Get a 5-question MCQ quiz to prep for exams.
        """)

# ---------------- ADMIN ---------------- #
if mode == "🛠️ Admin Space":
    st.markdown("<h1 class='premium-title'>🛠️ Admin Space</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle-text'>Manage your documents and knowledge base</p>", unsafe_allow_html=True)

    st.divider()
    
    st.subheader("📝 Raw JSON Ingestion")
    st.caption("Paste structured JSON arrays to manually inject specific college knowledge (e.g., faculty names, lab hours, rules).")
    
    json_example = '''[
  {
    "text": "Dr Rajasekhar Reddy A is the Head of the CSE department.",
    "metadata": { "type": "faculty", "name": "Rajasekhar Reddy A", "role": "HOD" }
  }
]'''
    
    raw_json_input = st.text_area("JSON Input", value="", placeholder=json_example, height=200)
    
    if st.button("🚀 Ingest JSON Data", use_container_width=True):
        if not raw_json_input.strip():
            st.error("❌ Input cannot be empty.")
        else:
            try:
                import json
                import datetime
                parsed_data = json.loads(raw_json_input)
                
                if not isinstance(parsed_data, list):
                    st.error("❌ Invalid format: JSON must be a list containing objects.")
                else:
                    valid = True
                    for i, item in enumerate(parsed_data):
                        if not isinstance(item, dict) or "text" not in item:
                            st.error(f"❌ Item at index {i} is missing the required 'text' key.")
                            valid = False
                            break
                    
                    if valid:
                        import os
                        os.makedirs("data", exist_ok=True)
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"knowledge_drop_{timestamp}.json"
                        filepath = os.path.join("data", filename)
                        
                        with open(filepath, "w", encoding="utf-8") as f:
                            json.dump(parsed_data, f, indent=2)
                        
                        st.success(f"✅ Successfully ingested {len(parsed_data)} knowledge items! Saved as {filename}.")
                        st.cache_resource.clear()
                        st.rerun()
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON format: {str(e)}")

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Upload Data")
        st.caption("Supported formats: **PDF, JSON, TXT, MD**")
        files = st.file_uploader("Upload Files", type=["pdf", "json", "txt", "md"], accept_multiple_files=True)
        if files:
            for f in files:
                save_document(f)
            st.success(f"✅ Saved {len(files)} files successfully.")
            st.cache_resource.clear()
        
        # Document stats
        st.divider()
        st.subheader("📊 Knowledge Base Stats")
        docs = list_documents()
        chunks_loaded, _ = load_rag()
        st.metric("Total Documents", len(docs))
        st.metric("Total Chunks Indexed", len(chunks_loaded) if chunks_loaded else 0)

    with col2:
        st.subheader("📁 Current Documents")
        docs = list_documents()
        
        # Aggregate chunks per file to show stats cleanly
        chunk_counts = {}
        if chunks_loaded:
            for c in chunks_loaded:
                src = c.get("metadata", {}).get("source") if isinstance(c, dict) else None
                if src:
                    chunk_counts[src] = chunk_counts.get(src, 0) + 1
                    
        if not docs:
            st.info("No documents uploaded yet. Upload some files to get started!")
        else:
            import datetime
            for doc in docs:
                meta = get_document_metadata(doc)
                if not meta: continue
                
                dt = datetime.datetime.fromtimestamp(meta["upload_time"])
                time_str = dt.strftime("%d %b %Y, %I:%M %p")
                
                icon = "📄" if meta["file_type"] == "pdf" else "🧩" if meta["file_type"] == "json" else "📝"
                chunks_in_file = chunk_counts.get(doc, 0)
                
                with st.expander(f"{icon} {doc}"):
                    st.caption(f"**Uploaded:** {time_str}  •  **Chunks Index:** {chunks_in_file}")
                    
                    preview = get_document_preview(doc)
                    if meta["file_type"] == "json" and isinstance(preview, (dict, list)):
                        st.json(preview)
                    else:
                        st.text_area("Preview (First 2000 chars)", value=str(preview), height=200, disabled=True)
                        
                    if st.button("🗑️ Delete", key=f"del_{doc}"):
                        if delete_document(doc):
                            st.success(f"Deleted {doc}")
                            st.cache_resource.clear()
                            st.rerun()
            st.divider()
            if st.button("🗑️ Delete All Documents", use_container_width=True):
                for doc in docs:
                    delete_document(doc)
                st.cache_resource.clear()
                st.rerun()

# ---------------- SUMMARY ---------------- #
elif mode == "📚 Master Summary":
    st.markdown("<h1 class='premium-title'>📚 Master Summary</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle-text'>AI-generated CliffNotes study guide from all your documents</p>", unsafe_allow_html=True)
    
    chunks, index = load_rag()
    
    if not chunks:
        st.warning("⚠️ No documents mapped. Please upload PDFs in Admin Space first.")
    else:
        if st.button("✨ Generate Study Guide", use_container_width=True):
            with st.spinner("Analyzing all documents for key insights..."):
                full_context = "\n".join([c["text"] if isinstance(c, dict) else c for c in chunks[:min(len(chunks), 40)]])
                with st.chat_message("assistant", avatar="📖"):
                    summary_gen = generate_summary_stream(full_context, model_name=model_choice, base_url=model_url)
                    final_summary = st.write_stream(summary_gen)
                    st.session_state.last_summary = final_summary
        
        # Copy/Download buttons for summary
        if "last_summary" in st.session_state and st.session_state.last_summary:
            s1, s2 = st.columns(2)
            with s1:
                st.download_button("📥 Download Summary (.txt)", data=st.session_state.last_summary, file_name="study_summary.txt", mime="text/plain", use_container_width=True)
            with s2:
                st.download_button("📥 Download as Markdown", data=st.session_state.last_summary, file_name="study_summary.md", mime="text/markdown", use_container_width=True)

# ---------------- FLASHCARDS ---------------- #
elif mode == "🗂️ Flashcard Center":
    st.markdown("<h1 class='premium-title'>🗂️ Flashcard Center</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle-text'>Active recall training — flip, score, and master your material</p>", unsafe_allow_html=True)
    
    chunks, index = load_rag()
    
    if not chunks:
        st.warning("⚠️ No documents mapped. Please upload PDFs in Admin Space first.")
    else:
        if "flashcards" not in st.session_state:
            st.session_state.flashcards = []
            st.session_state.card_index = 0
            st.session_state.show_answer = False
            st.session_state.fc_score = {"correct": 0, "incorrect": 0}

        fc1, fc2 = st.columns([2, 1])
        with fc1:
            if st.button("🚀 Generate New Flashcards", use_container_width=True):
                with st.spinner("Crafting flashcards..."):
                    import random
                    sample_context = "\n".join([c["text"] if isinstance(c, dict) else c for c in random.sample(chunks, min(len(chunks), 15))])
                    raw_cards = "".join(list(generate_flashcards_stream(sample_context, model_name=model_choice, base_url=model_url)))
                    
                    parsed = []
                    cards = raw_cards.split("---")
                    for c in cards:
                        if "Q:" in c and "A:" in c:
                            q = c.split("Q:")[1].split("A:")[0].strip()
                            a = c.split("A:")[1].strip()
                            parsed.append({"q": q, "a": a})
                    
                    st.session_state.flashcards = parsed
                    st.session_state.card_index = 0
                    st.session_state.show_answer = False
                    st.session_state.fc_score = {"correct": 0, "incorrect": 0}
                    st.rerun()
        with fc2:
            if st.session_state.flashcards:
                import random as rnd
                if st.button("🔀 Shuffle Cards", use_container_width=True):
                    rnd.shuffle(st.session_state.flashcards)
                    st.session_state.card_index = 0
                    st.session_state.show_answer = False
                    st.rerun()

        if st.session_state.flashcards:
            st.divider()
            
            # Progress bar
            total = len(st.session_state.flashcards)
            progress = (st.session_state.card_index + 1) / total
            st.progress(progress, text=f"Card {st.session_state.card_index + 1} of {total}")
            
            # Safety guard
            if st.session_state.card_index >= total:
                st.session_state.card_index = 0
                
            card = st.session_state.flashcards[st.session_state.card_index]
            
            content = card['a'] if st.session_state.show_answer else card['q']
            label = "✅ ANSWER" if st.session_state.show_answer else "❓ QUESTION"
            color = "var(--tertiary)" if st.session_state.show_answer else "var(--primary)"
            
            st.markdown(f"""
                <div class="flashcard">
                    <div>
                        <div style="color:{color}; font-size:0.75rem; font-weight:bold; margin-bottom:12px; letter-spacing:2px;">{label}</div>
                        <div style="line-height:1.6;">{content}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            if col1.button("⬅️ Previous", disabled=st.session_state.card_index == 0, use_container_width=True):
                st.session_state.card_index -= 1
                st.session_state.show_answer = False
                st.rerun()
            if col2.button("🔄 Flip Card", use_container_width=True):
                st.session_state.show_answer = not st.session_state.show_answer
                st.rerun()
            if col3.button("Next ➡️", disabled=st.session_state.card_index == total-1, use_container_width=True):
                st.session_state.card_index += 1
                st.session_state.show_answer = False
                st.rerun()
            
            # Self-scoring
            if st.session_state.show_answer:
                st.divider()
                st.caption("How did you do? Rate yourself:")
                sc1, sc2, _ = st.columns([1, 1, 3])
                with sc1:
                    if st.button("✅ I Knew It", use_container_width=True, key="fc_correct"):
                        st.session_state.fc_score["correct"] += 1
                        if st.session_state.card_index < total - 1:
                            st.session_state.card_index += 1
                            st.session_state.show_answer = False
                        st.rerun()
                with sc2:
                    if st.button("❌ Got It Wrong", use_container_width=True, key="fc_incorrect"):
                        st.session_state.fc_score["incorrect"] += 1
                        if st.session_state.card_index < total - 1:
                            st.session_state.card_index += 1
                            st.session_state.show_answer = False
                        st.rerun()
            
            # Score Display
            answered = st.session_state.fc_score["correct"] + st.session_state.fc_score["incorrect"]
            if answered > 0:
                st.divider()
                m1, m2, m3 = st.columns(3)
                m1.metric("✅ Correct", st.session_state.fc_score["correct"])
                m2.metric("❌ Incorrect", st.session_state.fc_score["incorrect"])
                pct = round(st.session_state.fc_score['correct'] / answered * 100)
                m3.metric("📈 Accuracy", f"{pct}%")

# ---------------- QUIZ ---------------- #
elif mode == "📝 Quiz Generator":
    st.markdown("<h1 class='premium-title'>📝 Quiz Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle-text'>Take a quiz, submit answers, and get AI-powered evaluation & suggestions</p>", unsafe_allow_html=True)
    
    chunks, index = load_rag()
    
    if not chunks:
        st.warning("⚠️ No documents mapped. Please upload PDFs in Admin Space first.")
    else:
        if "quiz_text" not in st.session_state:
            st.session_state.quiz_text = ""
        
        if st.button("🚀 Generate New Quiz", use_container_width=True):
            with st.spinner("Analyzing notes and crafting questions..."):
                import random
                sample_context = "\n".join([c["text"] if isinstance(c, dict) else c for c in random.sample(chunks, min(len(chunks), 10))])
                raw_quiz = "".join(list(generate_quiz_stream(sample_context, model_name=model_choice, base_url=model_url)))
                st.session_state.quiz_text = raw_quiz
                st.rerun()
        
        if st.session_state.quiz_text:
            st.divider()
            st.subheader("📋 Your Quiz")
            st.markdown(st.session_state.quiz_text)
            
            # Download/Share quiz
            q1, q2 = st.columns(2)
            with q1:
                st.download_button("📥 Download Quiz (.txt)", data=st.session_state.quiz_text, file_name="quiz.txt", mime="text/plain", use_container_width=True)
            with q2:
                st.download_button("📤 Share Quiz (.md)", data=f"# Study AI Quiz\n\n{st.session_state.quiz_text}\n\n---\n*Generated by Study AI — The Cognitive Sanctuary*", file_name="quiz_share.md", mime="text/markdown", use_container_width=True)
            
            # Answer submission
            st.divider()
            st.subheader("✍️ Submit Your Answers")
            st.caption("Type your answers below (e.g., '1. B, 2. A, 3. C, 4. D, 5. A') and get instant AI evaluation.")
            user_answers = st.text_area("Your Answers:", placeholder="1. B\n2. A\n3. C\n4. D\n5. A", height=120)
            
            if st.button("🧠 Evaluate My Answers", use_container_width=True, disabled=not user_answers):
                with st.spinner("Grading your quiz..."):
                    with st.chat_message("assistant", avatar="🎓"):
                        eval_gen = generate_quiz_evaluate_stream(st.session_state.quiz_text, user_answers, model_name=model_choice, base_url=model_url)
                        st.write_stream(eval_gen)

# ---------------- MIND MAP EXPLORER ---------------- #
elif mode == "🧠 Mind Map Explorer":
    st.markdown("<h1 class='premium-title'>🧠 Mind Map Explorer</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle-text'>Visualize the conceptual structure of your documents as a hierarchical graph</p>", unsafe_allow_html=True)
    chunks, index = load_rag()
    
    if not chunks:
        st.warning("⚠️ No documents mapped. Please upload PDFs in Admin Space first.")
    else:
        depth = st.slider("🔍 Depth (how many chunks to analyze)", 5, 30, 15)
        if st.button("🕸️ Generate Mind Map", use_container_width=True):
            with st.spinner("Extracting conceptual web..."):
                full_context = "\n".join([c["text"] if isinstance(c, dict) else c for c in chunks[:min(len(chunks), depth)]])
                with st.chat_message("assistant", avatar="🧠"):
                    map_gen = generate_mindmap_stream(full_context, model_name=model_choice, base_url=model_url)
                    final_answer = st.write_stream(map_gen)
                    st.session_state.last_mindmap = final_answer
                    
                    mermaid_matches = re.findall(r'```mermaid\n(.*?)\n```', final_answer, re.DOTALL)
                    for m_code in mermaid_matches:
                        render_mermaid(m_code)
        
        if "last_mindmap" in st.session_state and st.session_state.last_mindmap:
            st.download_button("📥 Download Mind Map (.md)", data=st.session_state.last_mindmap, file_name="mindmap.md", mime="text/markdown", use_container_width=True)

# ---------------- CHEAT SHEET ---------------- #
elif mode == "📊 Cheat Sheet":
    st.markdown("<h1 class='premium-title'>📊 Cheat Sheet Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle-text'>Extract the most critical terms, dates, and formulas into a quick-reference table</p>", unsafe_allow_html=True)
    chunks, index = load_rag()
    
    if not chunks:
        st.warning("⚠️ No documents mapped.")
    else:
        if st.button("✨ Generate Cheat Sheet", use_container_width=True):
            with st.spinner("Compiling cheat sheet..."):
                full_context = "\n".join([c["text"] if isinstance(c, dict) else c for c in chunks[:min(len(chunks), 25)]])
                with st.chat_message("assistant", avatar="📊"):
                    sheet_gen = generate_cheatsheet_stream(full_context, model_name=model_choice, base_url=model_url)
                    final_sheet = st.write_stream(sheet_gen)
                    st.session_state.last_cheatsheet = final_sheet
        
        if "last_cheatsheet" in st.session_state and st.session_state.last_cheatsheet:
            cs1, cs2 = st.columns(2)
            with cs1:
                st.download_button("📥 Download Cheat Sheet (.txt)", data=st.session_state.last_cheatsheet, file_name="cheat_sheet.txt", mime="text/plain", use_container_width=True)
            with cs2:
                st.download_button("📤 Share Cheat Sheet (.md)", data=f"# Cheat Sheet\n\n{st.session_state.last_cheatsheet}\n\n---\n*Generated by Study AI*", file_name="cheat_sheet_share.md", mime="text/markdown", use_container_width=True)

# ---------------- STUDY PLANNER ---------------- #
elif mode == "📅 Study Planner":
    st.markdown("<h1 class='premium-title'>📅 AI Study Planner</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle-text'>Get a structured 5-day study schedule tailored to your material</p>", unsafe_allow_html=True)
    chunks, index = load_rag()
    
    if not chunks:
        st.warning("⚠️ No documents mapped.")
    else:
        if st.button("📅 Plan My Study Week", use_container_width=True):
            with st.spinner("Structuring curriculum..."):
                full_context = "\n".join([c["text"] if isinstance(c, dict) else c for c in chunks[:min(len(chunks), 30)]])
                with st.chat_message("assistant", avatar="📅"):
                    plan_gen = generate_study_plan_stream(full_context, model_name=model_choice, base_url=model_url)
                    final_plan = st.write_stream(plan_gen)
                    st.session_state.last_plan = final_plan
        
        if "last_plan" in st.session_state and st.session_state.last_plan:
            sp1, sp2 = st.columns(2)
            with sp1:
                st.download_button("📥 Download Study Plan", data=st.session_state.last_plan, file_name="study_plan.txt", mime="text/plain", use_container_width=True)
            with sp2:
                st.download_button("📤 Share Study Plan (.md)", data=f"# My Study Plan\n\n{st.session_state.last_plan}\n\n---\n*Generated by Study AI*", file_name="study_plan_share.md", mime="text/markdown", use_container_width=True)


# ---------------- USER CHAT ---------------- #
else:
    st.markdown("<h1 class='premium-title'>🤖 Study AI Chat</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle-text'>The Cognitive Sanctuary — Powered by Local LLMs & RAG</p>", unsafe_allow_html=True)
    
    colA, colB = st.columns([3, 1])
    with colB:
        persona_choice = st.selectbox("🎭 Tutor Persona", ["Standard Tutor", "Explain Like I'm 5 (ELI5)", "PhD Level", "Analogy Mode"], index=0)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    chunks, index = load_rag()
    has_docs = bool(chunks)
    if not has_docs:
        st.info("💡 No college documents uploaded yet. I'll answer using AI knowledge. Upload PDFs in Admin Space for college-specific answers.")

    # Display Chat History
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            if "profile_cards" in msg and msg["profile_cards"]:
                for p in msg["profile_cards"]:
                    render_profile_card(p, msg.get("show_image", False))
            elif "profile_card" in msg and msg["profile_card"]: # backwards compat
                render_profile_card(msg["profile_card"], msg.get("show_image", False))
            st.markdown(msg["content"])
            
            # Mermaid diagrams
            mermaid_matches = list(re.finditer(r'```mermaid\n(.*?)\n```', msg.get("content", ""), re.DOTALL))
            has_embedded_mermaid = len(mermaid_matches) > 0
            
            for m_match in mermaid_matches:
                render_mermaid(m_match.group(1))

            if "diagram_code" in msg:
                render_mermaid(msg["diagram_code"])
            
            # Source badge for history messages
            if msg["role"] == "assistant" and "source" in msg:
                src = msg["source"]
                if src == "college_data":
                    st.markdown(
                        '<div style="display:inline-block; background:rgba(59,130,246,0.15); border:1px solid rgba(59,130,246,0.3); '
                        'color:#60a5fa; padding:4px 14px; border-radius:20px; font-size:12px; margin-top:4px;">'
                        '\U0001f3eb Based on College Data</div>',
                        unsafe_allow_html=True
                    )
                elif src == "ai_generated":
                    st.markdown(
                        '<div style="display:inline-block; background:rgba(168,85,247,0.15); border:1px solid rgba(168,85,247,0.3); '
                        'color:#c084fc; padding:4px 14px; border-radius:20px; font-size:12px; margin-top:4px;">'
                        '\U0001f916 Generated by our AI for better understanding</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        '<div style="display:inline-block; background:rgba(45,212,191,0.15); border:1px solid rgba(45,212,191,0.3); '
                        'color:#2dd4bf; padding:4px 14px; border-radius:20px; font-size:12px; margin-top:4px;">'
                        '\U0001f500 College Data + AI Enhanced</div>',
                        unsafe_allow_html=True
                    )

            # Action buttons for assistant messages
            if msg["role"] == "assistant":
                clean_text = re.sub(r'```mermaid.*?```', '', msg["content"], flags=re.DOTALL).strip()
                vcol1, vcol2, ccol, dlcol, dcol, _ = st.columns([1, 1, 1, 1, 1.5, 1])
                with vcol1:
                    if st.button("\U0001f50a Read", key=f"voice_{i}"):
                        clean_voice = re.sub(r'```mermaid.*?```', '', msg["content"], flags=re.DOTALL)
                        speak_text(clean_voice)
                with vcol2:
                    if st.button("\U0001f507 Stop", key=f"stop_{i}"):
                        stop_speech()
                with ccol:
                    if st.button("\U0001f4cb Copy", key=f"copy_{i}"):
                        escaped = clean_text.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
                        components.html(
                            f"""<script>
                            navigator.clipboard.writeText(`{escaped}`).then(() => {{}});
                            </script>""",
                            height=0, width=0
                        )
                        st.toast("\u2705 Copied to clipboard!", icon="\U0001f4cb")
                with dlcol:
                    st.download_button("\U0001f4e5 Save", data=clean_text, file_name=f"answer_{i}.txt", mime="text/plain", key=f"dl_{i}")
                with dcol:
                    if not has_embedded_mermaid and "diagram_code" not in msg:
                        if st.button("\U0001f4ca Diagram", key=f"diag_{i}", use_container_width=True):
                            with st.spinner("\U0001f916 Drawing diagram..."):
                                diag_stream = list(generate_diagram_for_text_stream(msg["content"], model_name=model_choice, base_url=model_url))
                                diag_text = "".join(diag_stream).strip()
                                mermaid_match = re.search(r'```mermaid\s*\n(.*?)(?:```|$)', diag_text, re.DOTALL)
                                if mermaid_match:
                                    msg["diagram_code"] = mermaid_match.group(1).strip()
                                elif diag_text.startswith("graph TD") or diag_text.startswith("flowchart") or diag_text.startswith("mindmap"):
                                    msg["diagram_code"] = diag_text.replace("```", "").strip()
                                else:
                                    msg["diagram_code"] = "graph TD\nA[Error] --> B[Could not generate valid diagram]"
                                st.rerun()

    query = st.chat_input("Ask anything — college topics or general questions...")
    
    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            with st.spinner("🤖 Studying and thinking..."):
                expanded_query, show_image = normalize_query(query)
                
                # Get scored results from FAISS
                if has_docs:
                    scored_results = search(expanded_query, index, chunks)
                else:
                    scored_results = []
                
                # Classify relevance
                source_type, high_chunks, all_chunks = classify_relevance(scored_results)
                
                # Check for metadata across top hits
                active_profiles = []
                if scored_results:
                    for chunk, score in scored_results[:4]:
                        if score >= 0.45 and isinstance(chunk, dict):
                            meta = chunk.get("metadata", {})
                            if any(k in meta for k in ["name", "image_url", "profile_url"]):
                                dedup_key = meta.get("name") or meta.get("profile_url")
                                if not any((p.get("name") or p.get("profile_url")) == dedup_key for p in active_profiles):
                                    active_profiles.append(meta)
                
                for prof in active_profiles:
                    render_profile_card(prof, show_image)
                
                # Generate hybrid answer using original original query (but context is drawn from expanded search)
                stream_generator = generate_hybrid_answer_stream(
                    query, scored_results,
                    model_name=model_choice, base_url=model_url, persona=persona_choice
                )
                final_answer = st.write_stream(stream_generator)
            
            # Source Badge
            if source_type == "college_data":
                st.markdown(
                    '<div style="display:inline-block; background:rgba(59,130,246,0.15); border:1px solid rgba(59,130,246,0.3); '
                    'color:#60a5fa; padding:4px 14px; border-radius:20px; font-size:12px; margin-top:8px;">'
                    '🏫 Based on College Data</div>',
                    unsafe_allow_html=True
                )
            elif source_type == "ai_generated":
                st.markdown(
                    '<div style="display:inline-block; background:rgba(168,85,247,0.15); border:1px solid rgba(168,85,247,0.3); '
                    'color:#c084fc; padding:4px 14px; border-radius:20px; font-size:12px; margin-top:8px;">'
                    '🤖 Generated by our AI for better understanding</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<div style="display:inline-block; background:rgba(45,212,191,0.15); border:1px solid rgba(45,212,191,0.3); '
                    'color:#2dd4bf; padding:4px 14px; border-radius:20px; font-size:12px; margin-top:8px;">'
                    '🔀 College Data + AI Enhanced</div>',
                    unsafe_allow_html=True
                )
            
            # Source Context with Relevance Scores
            if scored_results:
                with st.expander("📎 Source Context (" + str(len(scored_results[:5])) + " segments found)"):
                    for idx, (chunk, score) in enumerate(scored_results[:5]):
                        score_pct = round(score * 100)
                        score_color = "#22c55e" if score >= 0.7 else "#f59e0b" if score >= 0.4 else "#ef4444"
                        st.markdown(
                            f'**Segment {idx+1}** — <span style="color:{score_color}; font-weight:600;">{score_pct}% match</span>',
                            unsafe_allow_html=True
                        )
                        st.markdown(chunk.get("text", "") if isinstance(chunk, dict) else chunk)
                        if idx < len(scored_results[:5]) - 1:
                            st.divider()

            msg_meta = {"role": "assistant", "content": final_answer, "source": source_type, "show_image": show_image}
            if active_profiles:
                msg_meta["profile_cards"] = active_profiles
            st.session_state.messages.append(msg_meta)
            st.rerun()
import streamlit as st
import time
import re
import streamlit.components.v1 as components
from text_processor import chunk_text
from rag_faiss import create_index, search
from llm import generate_answer_stream, basic_chat, generate_quiz_stream, generate_summary_stream, generate_flashcards_stream, generate_mindmap_stream, generate_cheatsheet_stream, generate_study_plan_stream, generate_quiz_evaluate_stream
from utils import save_pdf, load_all_pdfs, list_pdfs, delete_pdf

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
@st.cache_resource
def load_rag():
    text = load_all_pdfs()
    chunks = chunk_text(text)
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
    """Renders Mermaid code with graceful fallback if syntax is invalid."""
    clean_code = sanitize_mermaid(code)
    escaped_code = clean_code.replace('`', '\\`')
    components.html(
        f"""
        <div id="mermaid-container"></div>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: false, theme: 'dark' }});
            const container = document.getElementById('mermaid-container');
            const code = `{escaped_code}`;
            try {{
                const {{ svg }} = await mermaid.render('mermaid-diagram', code);
                container.innerHTML = '<div style="display:flex;justify-content:center;">' + svg + '</div>';
            }} catch (e) {{
                container.innerHTML = `
                    <div style="background:#1e293b; border:1px solid #334155; border-radius:8px; padding:16px; font-family:monospace; color:#94a3b8; font-size:13px; white-space:pre-wrap;">
                        <div style="color:#60a5fa; margin-bottom:8px; font-family:sans-serif;">📊 Diagram (raw code):</div>
                        ${{code}}
                    </div>`;
            }}
        </script>
        """,
        height=400,
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
    
    st.subheader("Model Selection")
    model_choice = st.selectbox("LLM Model", ["llama3", "mistral", "gemma", "phi3"], index=0)

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

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Upload Documents")
        files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
        if files:
            for f in files:
                save_pdf(f)
            st.success(f"✅ Saved {len(files)} files successfully.")
            st.cache_resource.clear()
        
        # Document stats
        st.divider()
        st.subheader("📊 Knowledge Base Stats")
        pdfs = list_pdfs()
        chunks_loaded, _ = load_rag()
        st.metric("Total Documents", len(pdfs))
        st.metric("Total Chunks Indexed", len(chunks_loaded) if chunks_loaded else 0)

    with col2:
        st.subheader("📁 Current Documents")
        pdfs = list_pdfs()
        if not pdfs:
            st.info("No documents uploaded yet. Upload PDFs to get started!")
        else:
            for pdf in pdfs:
                cols = st.columns([4, 1])
                cols[0].write(f"📄 {pdf}")
                if cols[1].button("🗑️", key=f"del_{pdf}"):
                    if delete_pdf(pdf):
                        st.success(f"Deleted {pdf}")
                        st.cache_resource.clear()
                        st.rerun()
            st.divider()
            if st.button("🗑️ Delete All Documents", use_container_width=True):
                for pdf in pdfs:
                    delete_pdf(pdf)
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
                full_context = "\n".join(chunks[:min(len(chunks), 40)])
                with st.chat_message("assistant", avatar="📖"):
                    summary_gen = generate_summary_stream(full_context, model_name=model_choice)
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
                    sample_context = "\n".join(random.sample(chunks, min(len(chunks), 15)))
                    raw_cards = "".join(list(generate_flashcards_stream(sample_context, model_name=model_choice)))
                    
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
                sample_context = "\n".join(random.sample(chunks, min(len(chunks), 10)))
                raw_quiz = "".join(list(generate_quiz_stream(sample_context, model_name=model_choice)))
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
                        eval_gen = generate_quiz_evaluate_stream(st.session_state.quiz_text, user_answers, model_name=model_choice)
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
                full_context = "\n".join(chunks[:min(len(chunks), depth)])
                with st.chat_message("assistant", avatar="🧠"):
                    map_gen = generate_mindmap_stream(full_context, model_name=model_choice)
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
                full_context = "\n".join(chunks[:min(len(chunks), 25)])
                with st.chat_message("assistant", avatar="📊"):
                    sheet_gen = generate_cheatsheet_stream(full_context, model_name=model_choice)
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
                full_context = "\n".join(chunks[:min(len(chunks), 30)])
                with st.chat_message("assistant", avatar="📅"):
                    plan_gen = generate_study_plan_stream(full_context, model_name=model_choice)
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
    if not chunks:
        st.warning("⚠️ No documents mapped. Please ask the Admin to upload PDFs.")
        st.stop()

    # Display Chat History
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
            # Action buttons for assistant messages
            if msg["role"] == "assistant":
                vcol1, vcol2, vcol3, _ = st.columns([1, 1, 1, 3])
                with vcol1:
                    if st.button("🔊 Read Aloud", key=f"voice_{i}"):
                        clean_voice = re.sub(r'```mermaid.*?```', '', msg["content"], flags=re.DOTALL)
                        speak_text(clean_voice)
                with vcol2:
                    if st.button("🔇 Stop", key=f"stop_{i}"):
                        stop_speech()
                with vcol3:
                    clean_text = re.sub(r'```mermaid.*?```', '', msg["content"], flags=re.DOTALL).strip()
                    st.download_button("📋 Copy", data=clean_text, file_name=f"answer_{i}.txt", mime="text/plain", key=f"copy_{i}")

            # Mermaid diagrams
            mermaid_matches = re.findall(r'```mermaid\n(.*?)\n```', msg["content"], re.DOTALL)
            for m_code in mermaid_matches:
                render_mermaid(m_code)

    query = st.chat_input("Ask about your documents...")
    
    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            with st.spinner("Searching document context..."):
                results = search(query, index, chunks)
                context_str = "\n\n".join(results[:3])
            
            stream_generator = generate_answer_stream(query, context_str, model_name=model_choice, persona=persona_choice)
            final_answer = st.write_stream(stream_generator)
            
            # Source Clip
            with st.expander("📎 Source Context (" + str(len(results[:3])) + " segments found)"):
                for idx, r in enumerate(results[:3]):
                    st.markdown(f"**Segment {idx+1}:**")
                    st.markdown(r)
                    if idx < 2:
                        st.divider()

            # Render diagrams
            mermaid_matches = re.findall(r'```mermaid\n(.*?)\n```', final_answer, re.DOTALL)
            for m_code in mermaid_matches:
                render_mermaid(m_code)
            
            st.session_state.messages.append({"role": "assistant", "content": final_answer})
            st.rerun()
import streamlit as st
import time
import re
import streamlit.components.v1 as components
from text_processor import chunk_text
from rag_faiss import create_index, search
from llm import generate_answer_stream, basic_chat, generate_quiz_stream, generate_summary_stream, generate_flashcards_stream, generate_mindmap_stream, generate_cheatsheet_stream, generate_study_plan_stream
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
    st.markdown("Manage your documents and embedding knowledge base.")

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Documents")
        files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
        if files:
            for f in files:
                save_pdf(f)
            st.success(f"Saved {len(files)} files successfully.")
            st.cache_resource.clear()

    with col2:
        st.subheader("Current Documents")
        pdfs = list_pdfs()
        if not pdfs:
            st.info("No documents uploaded yet.")
        else:
            for pdf in pdfs:
                cols = st.columns([4, 1])
                cols[0].write(f"📄 {pdf}")
                if cols[1].button("Delete", key=f"del_{pdf}"):
                    if delete_pdf(pdf):
                        st.success(f"Deleted {pdf}")
                        st.cache_resource.clear()
                        st.rerun()

# ---------------- SUMMARY ---------------- #
elif mode == "📚 Master Summary":
    st.markdown("<h1 class='premium-title'>📚 Master Summary</h1>", unsafe_allow_html=True)
    st.markdown("Generates a comprehensive study guide from all your uploaded documents.")
    
    chunks, index = load_rag()
    
    if not chunks:
        st.warning("⚠️ No documents mapped. Please upload PDFs in Admin Space first.")
    else:
        if st.button("✨ Generate Study Guide", use_container_width=True):
            with st.spinner("Analyzing all documents for key insights..."):
                full_context = "\n".join(chunks[:min(len(chunks), 40)])
                with st.chat_message("assistant", avatar="📖"):
                    summary_gen = generate_summary_stream(full_context, model_name=model_choice)
                    st.write_stream(summary_gen)

# ---------------- FLASHCARDS ---------------- #
elif mode == "🗂️ Flashcard Center":
    st.markdown("<h1 class='premium-title'>🗂️ Flashcard Center</h1>", unsafe_allow_html=True)
    st.markdown("Test your active recall with AI-generated flashcards.")
    
    chunks, index = load_rag()
    
    if not chunks:
        st.warning("⚠️ No documents mapped. Please upload PDFs in Admin Space first.")
    else:
        if "flashcards" not in st.session_state:
            st.session_state.flashcards = []
            st.session_state.card_index = 0
            st.session_state.show_answer = False

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
                st.rerun()

        if st.session_state.flashcards:
            st.divider()
            
            # Safety guard: Ensure index is within bounds (prevents IndexError)
            if st.session_state.card_index >= len(st.session_state.flashcards):
                st.session_state.card_index = 0
                
            card = st.session_state.flashcards[st.session_state.card_index]
            
            content = card['a'] if st.session_state.show_answer else card['q']
            label = "ANSWER" if st.session_state.show_answer else "QUESTION"
            color = "#10b981" if st.session_state.show_answer else "#3b82f6"
            
            st.markdown(f"""
                <div class="flashcard">
                    <div>
                        <div style="color:{color}; font-size:0.8rem; font-weight:bold; margin-bottom:10px;">{label}</div>
                        {content}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            if col1.button("⬅️ Previous", disabled=st.session_state.card_index == 0):
                st.session_state.card_index -= 1
                st.session_state.show_answer = False
                st.rerun()
            if col2.button("🔄 Flip Card", use_container_width=True):
                st.session_state.show_answer = not st.session_state.show_answer
                st.rerun()
            if col3.button("Next ➡️", disabled=st.session_state.card_index == len(st.session_state.flashcards)-1):
                st.session_state.card_index += 1
                st.session_state.show_answer = False
                st.rerun()
            
            st.caption(f"Card {st.session_state.card_index + 1} of {len(st.session_state.flashcards)}")

# ---------------- QUIZ ---------------- #
elif mode == "📝 Quiz Generator":
    st.markdown("<h1 class='premium-title'>📝 Quiz Generator</h1>", unsafe_allow_html=True)
    chunks, index = load_rag()
    
    if not chunks:
        st.warning("⚠️ No documents mapped. Please upload PDFs in Admin Space first.")
    else:
        if st.button("🚀 Generate New Quiz", use_container_width=True):
            with st.spinner("Analyzing notes and crafting questions..."):
                import random
                sample_context = "\n".join(random.sample(chunks, min(len(chunks), 10)))
                with st.chat_message("assistant", avatar="🎓"):
                    quiz_gen = generate_quiz_stream(sample_context, model_name=model_choice)
                    st.write_stream(quiz_gen)

# ---------------- MIND MAP EXPLORER ---------------- #
elif mode == "🧠 Mind Map Explorer":
    st.markdown("<h1 class='premium-title'>🧠 Mind Map Explorer</h1>", unsafe_allow_html=True)
    st.markdown("Visualize the core concepts of your documents as a connected graph.")
    chunks, index = load_rag()
    
    if not chunks:
        st.warning("⚠️ No documents mapped. Please upload PDFs in Admin Space first.")
    else:
        if st.button("🕸️ Generate Mind Map", use_container_width=True):
            with st.spinner("Extracting conceptual web..."):
                full_context = "\n".join(chunks[:min(len(chunks), 15)])
                with st.chat_message("assistant", avatar="🧠"):
                    map_gen = generate_mindmap_stream(full_context, model_name=model_choice)
                    final_answer = st.write_stream(map_gen)
                    
                    # Render the mind map if valid markdown was generated
                    mermaid_matches = re.findall(r'```mermaid\n(.*?)\n```', final_answer, re.DOTALL)
                    for m_code in mermaid_matches:
                        render_mermaid(m_code)

# ---------------- CHEAT SHEET ---------------- #
elif mode == "📊 Cheat Sheet":
    st.markdown("<h1 class='premium-title'>📊 Cheat Sheet Generator</h1>", unsafe_allow_html=True)
    st.markdown("Instantly extract the 10 most critical terms/formulas into a quick-reference table.")
    chunks, index = load_rag()
    
    if not chunks:
        st.warning("⚠️ No documents mapped.")
    else:
        if st.button("✨ Generate Cheat Sheet", use_container_width=True):
            with st.spinner("Compiling cheat sheet..."):
                full_context = "\n".join(chunks[:min(len(chunks), 25)])
                with st.chat_message("assistant", avatar="📊"):
                    sheet_gen = generate_cheatsheet_stream(full_context, model_name=model_choice)
                    st.write_stream(sheet_gen)

# ---------------- STUDY PLANNER ---------------- #
elif mode == "📅 Study Planner":
    st.markdown("<h1 class='premium-title'>📅 AI Study Planner</h1>", unsafe_allow_html=True)
    st.markdown("Get a structured 5-day schedule to conquer your study material.")
    chunks, index = load_rag()
    
    if not chunks:
        st.warning("⚠️ No documents mapped.")
    else:
        if st.button("📅 Plan My Study Week", use_container_width=True):
            with st.spinner("Structuring curriculum..."):
                full_context = "\n".join(chunks[:min(len(chunks), 30)])
                with st.chat_message("assistant", avatar="📅"):
                    plan_gen = generate_study_plan_stream(full_context, model_name=model_choice)
                    st.write_stream(plan_gen)


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
            
            # Voice buttons for assistant messages
            if msg["role"] == "assistant":
                vcol1, vcol2, _ = st.columns([1, 1, 4])
                with vcol1:
                    if st.button("🔊 Read Aloud", key=f"voice_{i}"):
                        clean_voice = re.sub(r'```mermaid.*?```', '', msg["content"], flags=re.DOTALL)
                        speak_text(clean_voice)
                with vcol2:
                    if st.button("🔇 Stop", key=f"stop_{i}"):
                        stop_speech()

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
            with st.expander("📎 Source Context"):
                st.markdown(context_str)

            # Render diagrams
            mermaid_matches = re.findall(r'```mermaid\n(.*?)\n```', final_answer, re.DOTALL)
            for m_code in mermaid_matches:
                render_mermaid(m_code)
            
            st.session_state.messages.append({"role": "assistant", "content": final_answer})
            st.rerun()
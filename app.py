import streamlit as st
import time
import re
import streamlit.components.v1 as components
from text_processor import chunk_text
from rag_faiss import create_index, search
from llm import generate_answer_stream, basic_chat, generate_quiz_stream
from utils import save_pdf, load_all_pdfs, list_pdfs, delete_pdf

# ---------------- CONFIG ---------------- #
st.set_page_config(page_title="AI Chatbot Ultra + Visuals", page_icon="🤖", layout="wide")

# ---------------- CSS (🔥 PREMIUM UI) ---------------- #
st.markdown("""
<style>
/* Streamlit Chat UI Tweaks */
.stChatMessage {
    border-radius: 10px;
}
.main {
    font-family: 'Inter', sans-serif;
}
.premium-title {
    background: -webkit-linear-gradient(45deg, #3b82f6, #8b5cf6, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 0px;
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
    # Fix: -->|Label|> B  =>  --> B   (remove broken edge labels entirely)
    code = re.sub(r'-->\|[^|]*\|>\s*', '--> ', code)
    # Fix: -->|Label| B   =>  --> B   (remove valid-looking edge labels that still break)
    code = re.sub(r'-->\|[^|]*\|\s*', '--> ', code)
    # Remove semicolons at end of lines
    code = re.sub(r';\s*$', '', code, flags=re.MULTILINE)
    # Replace parentheses inside labels: A[Foo (Bar)] -> A[Foo - Bar]
    code = re.sub(r'\(([^)]*)\)', r'- \1', code)
    return code

def render_mermaid(code: str):
    """Renders Mermaid code with graceful fallback if syntax is invalid."""
    clean_code = sanitize_mermaid(code)
    # Escape backticks for JS template literal safety
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

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.title("⚙️ Control Panel")
    
    st.subheader("Model Configuration")
    model_choice = st.selectbox("LLM Model", ["llama3", "mistral", "gemma", "phi3"], index=0)

    st.divider()
    mode = st.radio("App Mode", ["💬 User Chat", "📝 Quiz Generator", "🛠️ Admin Space"])

    if st.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.button("🔄 Reload Data Index", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()

    st.divider()
    
    # Export Chat Feature
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
        if st.button("📋 Copy Shareable text", use_container_width=True):
            share_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
            st.code(share_text)
            st.success("Copied to clipboard area!")
    else:
        st.info("No chat history to export yet.")

    st.divider()

    with st.expander("📖 How to Use", expanded=False):
        st.markdown("""
**1. Upload Documents (Admin)**
- Switch to **🛠️ Admin Space** mode.
- Click **Upload PDFs** and select your study material / notes.
- Your documents will be indexed automatically.

**2. Chat with AI (User)**
- Switch to **💬 User Chat** mode.
- Type any question about your uploaded documents.
- The AI will search your PDFs and answer with context.

**3. Quiz Generator 📝**
- Switch to **📝 Quiz Generator** mode.
- Click **Generate Quiz** to get 5 challenging MCQ questions from your notes.

**4. Auto Diagrams 📊**
- Ask questions involving processes, architectures, or steps.
- The AI will automatically generate **Mermaid diagrams** alongside text answers.

**5. Export & Share 📤**
- Use the **Download Chat History** button in the sidebar to save your session.
- Perfect for sharing with study groups or saving for revision.

**6. Model Selection**
- Use the **LLM Model** dropdown above to switch between models.

**7. Controls**
- 🧹 **Clear Chat** — Wipes all messages from the current session.
- 🔄 **Reload Data** — Re-indexes all PDFs (use after uploading/deleting files).
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

# ---------------- QUIZ ---------------- #
elif mode == "📝 Quiz Generator":
    st.markdown("<h1 class='premium-title'>📝 Study Quiz Generator</h1>", unsafe_allow_html=True)
    st.markdown("Test your knowledge! I'll generate a custom MCQ quiz from your notes.")
    
    chunks, index = load_rag()
    
    if not chunks:
        st.warning("⚠️ No documents mapped. Please upload PDFs in Admin Space first.")
    else:
        if st.button("🚀 Generate New Quiz", use_container_width=True):
            with st.spinner("Analyzing notes and crafting questions..."):
                import random
                # Combine a few random chunks for variety
                sample_context = "\n".join(random.sample(chunks, min(len(chunks), 10)))
                
                with st.chat_message("assistant", avatar="🎓"):
                    quiz_gen = generate_quiz_stream(sample_context, model_name=model_choice)
                    full_quiz = st.write_stream(quiz_gen)
                    
                    st.info("💡 Tip: You can copy these questions into your study group chat!")

# ---------------- USER ---------------- #
else:
    st.markdown("<h1 class='premium-title'>🤖 AI Chatbot Ultra</h1>", unsafe_allow_html=True)
    st.markdown("Powered by Local LLMs & RAG")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    chunks, index = load_rag()

    if not chunks:
        st.warning("⚠️ No documents mapped. Please ask the Admin to upload PDFs.")
        st.stop()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
            # Persist Mermaid diagrams in chat history correctly!
            mermaid_matches = re.findall(r'```mermaid\n(.*?)\n```', msg["content"], re.DOTALL)
            for m_code in mermaid_matches:
                render_mermaid(m_code)

    with st.expander("💡 Suggested Questions"):
        st.markdown("- Can you map out the system architecture from the document?\n- Give me a flowchart of the steps.\n- Please explain the key findings.")

    query = st.chat_input("Ask about your documents...")
    st.markdown("<p style='text-align:center; color:#6b7280; font-size:12px; margin-top:-10px;'>AI can make mistakes. Always verify important information.</p>", unsafe_allow_html=True)

    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            basic_resp = basic_chat(query)
            
            if basic_resp:
                st.markdown(basic_resp)
                st.session_state.messages.append({"role": "assistant", "content": basic_resp})
            else:
                with st.spinner("Searching document context..."):
                    results = search(query, index, chunks)
                    context_str = "\n\n".join(results[:3])
                
                stream_generator = generate_answer_stream(query, context_str, model_name=model_choice)
                final_answer = st.write_stream(stream_generator)
                
                # Render any diagram generated live directly beneath the printed text!
                mermaid_matches = re.findall(r'```mermaid\n(.*?)\n```', final_answer, re.DOTALL)
                for m_code in mermaid_matches:
                    render_mermaid(m_code)
                
                st.session_state.messages.append({"role": "assistant", "content": final_answer})
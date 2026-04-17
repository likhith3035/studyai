import requests
import json

def call_llm_stream(prompt, model_name, base_url):
    """
    Centralized helper to call different local LLM APIs (Ollama vs OpenAI/LM Studio).
    """
    # Auto-detect format based on port
    is_openai_format = ":1234" in base_url or "/v1" in base_url
    
    try:
        if is_openai_format:
            # OpenAI / LM Studio Chat Completions format
            url = f"{base_url.rstrip('/')}/v1/chat/completions"
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True,
                "temperature": 0.7
            }
            response = requests.post(url, json=payload, stream=True, timeout=10)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith("data: "):
                        data_content = line_str[6:]
                        if data_content == "[DONE]":
                            break
                        data = json.loads(data_content)
                        if "choices" in data and len(data["choices"]) > 0:
                            content = data["choices"][0].get("delta", {}).get("content", "")
                            if content:
                                yield content
        else:
            # Ollama Generate format
            url = f"{base_url.rstrip('/')}/api/generate"
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": True
            }
            response = requests.post(url, json=payload, stream=True, timeout=10)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
                    if data.get("done"):
                        break
    except Exception as e:
        yield f"⚠️ LLM Connection Error ({base_url}): {str(e)}"

def generate_answer_stream(query, context, model_name="llama3", base_url="http://localhost:11434", persona="Standard Tutor"):
    """Legacy function — kept for backward compatibility with quiz/summary modules."""
    persona_prompts = {
        "Standard Tutor": "You are a helpful AI assistant.",
        "Explain Like I'm 5 (ELI5)": "You are a highly enthusiastic teacher. Explain the following concepts so simply that a 5-year-old child could understand them.",
        "PhD Level": "You are a post-doctoral researcher. Explain the concepts using advanced terminology, deep insights, and academic rigor.",
        "Analogy Mode": "You are an expert at analogies. Explain the concepts entirely by comparing them to everyday objects, events, or pop culture."
    }
    
    selected_persona = persona_prompts.get(persona, persona_prompts["Standard Tutor"])

    prompt = f"""
{selected_persona}

Answer ONLY from the context.
If not found, say: Not found in document.

Context:
{context}

Question:
{query}

Answer:
"""
    yield from call_llm_stream(prompt, model_name, base_url)


# ============================================================
# HYBRID RAG SYSTEM: College Expert + AI Knowledge Combined
# ============================================================

RELEVANCE_THRESHOLD = 0.7

def classify_relevance(scored_results):
    """
    Classify query relevance based on similarity scores.
    
    Returns:
        source_type: "college_data" | "ai_generated" | "mixed"
        high_relevance_chunks: list of chunks with score >= threshold
        all_chunks: list of all chunk texts
    """
    if not scored_results:
        return "ai_generated", [], []
    
    high_relevance = [(chunk, score) for chunk, score in scored_results if score >= RELEVANCE_THRESHOLD]
    all_chunks = [chunk["text"] if isinstance(chunk, dict) else chunk for chunk, score in scored_results]
    high_chunks = [chunk["text"] if isinstance(chunk, dict) else chunk for chunk, score in high_relevance]
    
    if len(high_relevance) == 0:
        return "ai_generated", [], all_chunks
    elif len(high_relevance) == len(scored_results):
        return "college_data", high_chunks, all_chunks
    else:
        return "mixed", high_chunks, all_chunks


def generate_hybrid_answer_stream(query, scored_results, model_name="llama3", base_url="http://localhost:11434", persona="Standard Tutor"):
    """
    Hybrid answering system that intelligently routes between:
    - Case 1: College data (high relevance)
    - Case 2: AI-generated knowledge (low/no relevance)
    - Case 3: Mixed (some college data + AI enhancement)
    """
    persona_prompts = {
        "Standard Tutor": "You are a helpful, friendly AI study assistant.",
        "Explain Like I'm 5 (ELI5)": "You are a highly enthusiastic teacher. Explain concepts so simply that a 5-year-old child could understand them.",
        "PhD Level": "You are a post-doctoral researcher. Explain concepts using advanced terminology, deep insights, and academic rigor.",
        "Analogy Mode": "You are an expert at analogies. Explain concepts entirely by comparing them to everyday objects, events, or pop culture."
    }
    
    selected_persona = persona_prompts.get(persona, persona_prompts["Standard Tutor"])
    source_type, high_chunks, all_chunks = classify_relevance(scored_results)
    
    if source_type == "college_data":
        context = "\n\n".join(high_chunks)
        prompt = f"""
{selected_persona}

You are answering a student's question using VERIFIED college/institutional data.
Answer the question based ONLY on the following retrieved college documents.
Be clear, structured, and helpful. Do NOT add information that is not in the context.

College Data Context:
{context}

Student's Question:
{query}

Provide a clear, well-structured answer based on the college data above:
"""
    
    elif source_type == "ai_generated":
        # Hard stop if they are explicitly asking for college directory data that we don't have
        college_keywords = ["hod", "faculty", "professor", "department", "staff", "pic", "image"]
        if any(k in query.lower() for k in college_keywords) and not high_chunks:
            yield "No relevant college data found."
            return
            
        # Use any low-relevance context as optional hints, but primarily use general knowledge
        hint_context = "\n".join(all_chunks[:2]) if all_chunks else ""
        hint_section = f"\n(Note: Some loosely related content was found but may not directly answer the question: {hint_context[:300]}...)\n" if hint_context else ""
        
        prompt = f"""
{selected_persona}

A student asked a question that is NOT directly covered in the college database.
Use your own knowledge to provide a helpful, accurate, and educational answer.
Be conversational and supportive. Never say "not found" or "I don't have information".
{hint_section}

Student's Question:
{query}

Provide a thorough, educational answer using your knowledge:
"""
    
    else:  # mixed
        college_context = "\n\n".join(high_chunks)
        prompt = f"""
{selected_persona}

A student asked a question that is PARTIALLY covered by college data.
For parts that match the college data, answer strictly from that context.
For parts not covered, use your general knowledge to provide a complete answer.
Seamlessly combine both into a single, coherent, helpful response.

College Data (use for specific institutional facts):
{college_context}

Student's Question:
{query}

Provide a complete, unified answer combining college-specific data and your own knowledge where needed:
"""
    
    yield from call_llm_stream(prompt, model_name, base_url)


def generate_diagram_for_text_stream(text_context, model_name="llama3", base_url="http://localhost:11434"):
    prompt = f"""
Read the following text block and generate ONLY a valid Mermaid.js diagram representing the relationships, steps, or structure described.

CRITICAL MERMAID RULES:
1. Wrap code in triple backtick blocks with mermaid language tag.
2. Start with graph TD
3. Use only alphanumeric characters for node IDs (e.g., A, B, Node1).
4. For all nodes, use the format: NodeID[Label text here]
5. Keep labels short and simple. DO NOT use special characters like ==, !=, (), or pipes | in IDs or labels. Replace them with words like "Equals" or "NotEquals".
6. Use simple arrows: A --> B
7. DO NOT use semicolons at end of lines.
8. DO NOT use parentheses () or quotes in any labels.

Example:
```mermaid
graph TD
  A[Start] --> B[Process]
  B --> C[Decision]
  C --> D[Result Alpha]
  C --> E[Result Beta]
```

Text to visualize:
{text_context}

Output ONLY the markdown block with the diagram code. No explanation.
"""
    yield from call_llm_stream(prompt, model_name, base_url)

def basic_chat(query):
    q = query.lower()
    if "hi" in q or "hello" in q:
        return "👋 Hello! How can I help you today?"
    elif "how are you" in q:
        return "😊 I'm doing great! Ready to help you with your PDF."
    elif "thank" in q:
        return "🙏 You're welcome! Happy to help."
    elif "bye" in q:
        return "👋 Goodbye! Have a great day."
    return None

def generate_quiz_stream(context, model_name="llama3", base_url="http://localhost:11434"):
    prompt = f"""
You are an expert tutor. Based on the following document context, create a challenging 5-question Multiple Choice Quiz.
For each question:
1. Provide the Question.
2. Provide 4 options (A, B, C, D).
3. Clearly state the correct answer with a brief explanation.

Context:
{context}

Quiz:
"""
    yield from call_llm_stream(prompt, model_name, base_url)

def generate_summary_stream(context, model_name="llama3", base_url="http://localhost:11434"):
    prompt = f"""
You are a master summarizer. Read the following document context and provide a highly structured "Master Study Guide".
Structure the guide with:
1. 📌 TL;DR (3-4 bullet points)
2. 📖 Detailed Summary (Split by key topics)
3. 🔑 Key Terminology (Definitions)
4. 🚀 Actionable Takeaways

Context:
{context}

Summary:
"""
    yield from call_llm_stream(prompt, model_name, base_url)

def generate_flashcards_stream(context, model_name="llama3", base_url="http://localhost:11434"):
    prompt = f"""
Based on the following document context, create 5 high-quality flashcards for active recall.

Format each card EXACTLY like this:
Q: [Question]
A: [Answer]
---
(Repeat 5 times)

Rules:
1. Keep questions challenging.
2. Keep answers concise.

Context:
{context}

Flashcards:
"""
    yield from call_llm_stream(prompt, model_name, base_url)

def generate_mindmap_stream(context, model_name="llama3", base_url="http://localhost:11434"):
    prompt = f"""
Create a comprehensive visual Mind Map of the following document context.
You MUST output valid Mermaid mindmap syntax.

CRITICAL RULES:
1. Start with the keyword 'mindmap' on its own line.
2. You MUST have EXACTLY ONE root node at the first indentation level.
3. Use only spaces for indentation (2-4 spaces per level).
4. For EVERY node, use quotes to wrap the text: `  "Node Text"`
5. Keep node text very short (1-3 words).
6. STRICTLY FORBIDDEN: Do not use symbols like ':', '!', '=', '-', '•', '(', ')', '[', ']', ',', or hyphens inside the node quotes. Replace them with plain words.
7. Wrap the code in triple backtick blocks with 'mermaid' tag.
8. Provide a brief textual summary before the diagram.

Example:
```mermaid
mindmap
  "Study Material"
    "Data Types"
      "Numeric"
      "Text"
    "Logic"
      "Conditionals"
      "Loops"
```

Context:
{context}

Response:
"""
    yield from call_llm_stream(prompt, model_name, base_url)

def generate_cheatsheet_stream(context, model_name="llama3", base_url="http://localhost:11434"):
    prompt = f"""
Create a highly structured Markdown Table acting as a "Cheat Sheet" for the following document context.
Extract exactly 10 of the most important terms, dates, or formulas.

Table Format:
| Key Concept / Term | Definition / Significance | Importance (High/Med/Low) |
|---|---|---|

Context:
{context}

Cheat Sheet:
"""
    yield from call_llm_stream(prompt, model_name, base_url)

def generate_study_plan_stream(context, model_name="llama3", base_url="http://localhost:11434"):
    prompt = f"""
You are an expert academic planner. Based on the following document context, generate a logical 5-Day Study Schedule.
Break down the material so it is easy to consume.

Format:
### Day 1: [Topic Name]
- **Focus**: [What to learn]
- **Goal**: [What you should know by the end]

(Repeat for 5 Days)
Finally, add a short "Tips for Success" section.

Context:
{context}

Study Plan:
"""
    yield from call_llm_stream(prompt, model_name, base_url)

def generate_quiz_evaluate_stream(quiz_text, user_answers, model_name="llama3", base_url="http://localhost:11434"):
    prompt = f"""
You are an expert exam evaluator. A student took a quiz and provided their answers.

Here is the quiz:
{quiz_text}

Here are the student's answers:
{user_answers}

Please:
1. Grade each answer as ✅ Correct or ❌ Incorrect.
2. For each incorrect answer, explain the correct answer briefly.
3. At the end, give an overall score (e.g., "3/5") and provide 2-3 personalized study suggestions based on what the student got wrong.

Evaluation:
"""
    yield from call_llm_stream(prompt, model_name, base_url)
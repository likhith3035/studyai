import requests
import json

def generate_answer_stream(query, context, model_name="llama3", persona="Standard Tutor"):
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
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model_name, "prompt": prompt, "stream": True},
            stream=True
        )
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "response" in data:
                    yield data["response"]
    except Exception as e:
        yield f"⚠️ Error: {str(e)}"

def generate_diagram_for_text_stream(text_context, model_name="llama3"):
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
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model_name, "prompt": prompt, "stream": True},
            stream=True
        )
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "response" in data:
                    yield data["response"]
    except Exception as e:
        yield f"```mermaid\ngraph TD\nA[Error] --> B[{str(e)}]\n```"

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

def generate_quiz_stream(context, model_name="llama3"):
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
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": True
            },
            stream=True
        )

        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "response" in data:
                    yield data["response"]

    except Exception as e:
        yield f"⚠️ Error generating quiz: {str(e)}"

def generate_summary_stream(context, model_name="llama3"):
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
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model_name, "prompt": prompt, "stream": True},
            stream=True
        )
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "response" in data:
                    yield data["response"]
    except Exception as e:
        yield f"⚠️ Error generating summary: {str(e)}"

def generate_flashcards_stream(context, model_name="llama3"):
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
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model_name, "prompt": prompt, "stream": True},
            stream=True
        )
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "response" in data:
                    yield data["response"]
    except Exception as e:
        yield f"⚠️ Error generating flashcards: {str(e)}"

def generate_mindmap_stream(context, model_name="llama3"):
    prompt = f"""
Create a comprehensive visual Mind Map of the following document context.
You MUST output valid Mermaid mindmap syntax.

CRITICAL RULES:
1. Start with 'mindmap'
2. You MUST have EXACTLY ONE root node at the first indentation level. Do NOT create multiple top-level concepts under 'mindmap'. Syntax will crash if there is more than 1 root.
3. Use strict indentation (spaces) to show hierarchy under the single root node.
4. Keep node text very short (1-3 words).
5. Do NOT use any parentheses, quotes, or special characters in the nodes.
6. Wrap the code in triple backticks with 'mermaid' tag.
7. Provide a brief textual summary before the diagram.

Example:
```mermaid
mindmap
  StudyMaterial
    Topic 1
      Subtopic A
    Topic 2
```

Context:
{context}

Response:
"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model_name, "prompt": prompt, "stream": True},
            stream=True
        )
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "response" in data:
                    yield data["response"]
    except Exception as e:
        yield f"⚠️ Error generating mind map: {str(e)}"

def generate_cheatsheet_stream(context, model_name="llama3"):
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
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model_name, "prompt": prompt, "stream": True},
            stream=True
        )
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "response" in data:
                    yield data["response"]
    except Exception as e:
        yield f"⚠️ Error generating cheat sheet: {str(e)}"

def generate_study_plan_stream(context, model_name="llama3"):
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
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model_name, "prompt": prompt, "stream": True},
            stream=True
        )
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "response" in data:
                    yield data["response"]
    except Exception as e:
        yield f"⚠️ Error generating study plan: {str(e)}"

def generate_quiz_evaluate_stream(quiz_text, user_answers, model_name="llama3"):
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
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model_name, "prompt": prompt, "stream": True},
            stream=True
        )
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "response" in data:
                    yield data["response"]
    except Exception as e:
        yield f"⚠️ Error evaluating quiz: {str(e)}"
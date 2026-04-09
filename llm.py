import requests
import json

def generate_answer_stream(query, context, model_name="llama3"):
    prompt = f"""
You are a helpful AI assistant with diagramming capabilities.

Answer ONLY from the context.
If not found, say: Not found in document.

If the answer involves processes, steps, or relationships, also provide a Mermaid.js diagram.

CRITICAL MERMAID RULES:
1. Wrap code in triple backtick blocks with mermaid language tag.
2. Start with graph TD
3. Use simple arrows: A --> B
4. DO NOT use edge labels with pipes like -->|label|
5. DO NOT use semicolons at end of lines
6. DO NOT use parentheses () in any labels
7. Keep all node labels inside square brackets []
8. Keep labels short and simple, no special characters

CORRECT example:
```mermaid
graph TD
    A[Data Collection] --> B[Data Processing]
    B --> C[Analysis]
    C --> D[Results]
```

WRONG - never do this:
- A -->|label|> B
- A[Something (x)]
- Lines ending with ;

Provide the textual answer first, then the diagram.

Context:
{context}

Question:
{query}

Answer:
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
        yield f"⚠️ Make sure Ollama is running (`ollama run {model_name}`). Error: {str(e)}"


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
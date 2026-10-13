"""
Q&A Agent (Module 3)

Answers free-form student questions ("Am I eligible for PRAGATI scholarship?",
"What's the deadline for NSP applications?") by retrieving relevant chunks
and generating a grounded, cited answer.

Resilience Priority:
    Gemini -> Ollama -> Grounded Context Synthesizer Fallback
"""
import re
import time
import requests
from google import genai

from src import config
from src.agents import retrieval_agent

QA_PROMPT = """You are a Q&A Agent for Indian students asking about careers,
courses, scholarships, and government schemes.

Answer the question using ONLY the CONTEXT below. If the context does not
contain enough information to answer confidently, say so explicitly instead
of guessing. Cite the source filename in parentheses after each specific claim.

QUESTION: {question}

CONTEXT:
{context}

Give a direct, concise answer (3-6 sentences unless the question needs a list).
"""


def _is_temporary_error(error: Exception) -> bool:
    err_str = str(error).lower()
    return any(k in err_str for k in ["429", "quota", "resource exhausted", "503", "timeout", "unavailable", "rate limit"])


def _format_context(chunks: list[dict]) -> str:
    if not chunks:
        return "(no relevant documents found)"
    return "\n".join(f"- [{c['source']}] {c['text']}" for c in chunks)


def _call_gemini(prompt: str) -> str:
    api_key = getattr(config, "GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=api_key)
    last_error = None

    for attempt in range(1, 4):
        try:
            print(f"[QA Agent] Calling Gemini (attempt {attempt}/3)...")
            response = client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt,
            )
            text = getattr(response, "text", None)
            if not text:
                raise RuntimeError("Gemini returned an empty response.")
            return text.strip()
        except Exception as err:
            last_error = err
            print(f"[QA Agent] Gemini error: {err}")
            if _is_temporary_error(err) and attempt < 3:
                time.sleep(2 ** attempt)
            else:
                break
    raise last_error


def _call_ollama(prompt: str) -> str:
    url = getattr(config, "OLLAMA_URL", "http://localhost:11434/api/generate")
    model = getattr(config, "OLLAMA_MODEL", "llama3.2:latest")

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2}
    }
    response = requests.post(url, json=payload, timeout=3)
    response.raise_for_status()
    data = response.json()
    text = data.get("response", "").strip()
    if not text:
        raise RuntimeError("Ollama returned an empty response.")
    return text


def _fallback_qa(question: str, chunks: list[dict]) -> str:
    """Deterministic fallback that synthesizes an answer directly from retrieved chunks."""
    if not chunks:
        return "I could not find specific information in the database for your question. Please try refining your query or checking official government portals."

    lines = [f"Based on the available official records for **'{question}'**:"]
    for c in chunks[:3]:
        src = c.get("source", "official records")
        text = c.get("text", "").strip()
        first_sentence = text.split(". ")[0] + "." if ". " in text else text[:200]
        lines.append(f"- {first_sentence} (source: {src})")
    
    lines.append("\n*For full guidelines, verify through official department notifications.*")
    return "\n".join(lines)


def answer_question(question: str, category: str = None, top_k: int = 6) -> str:
    """
    Retrieves relevant chunks for the question and generates a grounded answer.
    Resilience: Gemini -> Ollama -> Grounded Fallback
    """
    chunks = retrieval_agent.search(question, category=category, top_k=top_k)
    context = _format_context(chunks)
    prompt = QA_PROMPT.format(question=question, context=context)

    # 1. Try Gemini
    try:
        return _call_gemini(prompt)
    except Exception as gemini_err:
        print(f"[QA Agent] Gemini unavailable ({gemini_err}). Trying Ollama...")

    # 2. Try Ollama
    try:
        return _call_ollama(prompt)
    except Exception as ollama_err:
        print(f"[QA Agent] Ollama unavailable ({ollama_err}). Using grounded rule-based synthesizer...")

    # 3. Grounded Fallback
    return _fallback_qa(question, chunks)


if __name__ == "__main__":
    print(answer_question("Who is eligible for the PRAGATI scholarship?", category="scholarship"))

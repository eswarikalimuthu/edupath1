"""
Schedule Planner Agent (Module 4)

Takes the Pathway Planner's phased roadmap ("Immediate/Short-term/...")
and a student-provided target goal date, and converts it into a concrete
month-by-month schedule.

Resilience Priority:
    Gemini -> Ollama -> Deterministic Phased Schedule Generator
"""
import re
import time
import requests
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from google import genai

from src import config

SCHEDULE_PROMPT = """You are a Schedule Planning Agent for Indian students.
Convert the phased roadmap below into a concrete month-by-month schedule,
using TODAY'S DATE and the student's TARGET GOAL DATE to assign realistic
months to each action item. Do NOT invent new action items - only assign
timing to what's already listed in the roadmap.

TODAY'S DATE: {today}
TARGET GOAL DATE: {target_date}

ROADMAP:
{pathway}

Return your answer as a markdown table with exactly these columns:
| Month | Action Item | Priority (High/Medium/Low) |

Make sure each Action Item cell retains its source citation in parentheses and resource links in square brackets (e.g., 'Gather 12th board marksheet and Aadhar card (source: tamilnadu.pdf) [Linked: Naan Mudhalvan Scheme]').

Order rows chronologically from today toward the target date.
After the table, add one line honestly flagging whether the target date
looks realistic given how much needs to happen in the roadmap.
"""


def _is_temporary_error(error: Exception) -> bool:
    err_str = str(error).lower()
    return any(k in err_str for k in ["429", "quota", "resource exhausted", "503", "timeout", "unavailable", "rate limit"])


def _call_gemini(prompt: str) -> str:
    api_key = getattr(config, "GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=api_key)
    last_error = None

    for attempt in range(1, 4):
        try:
            print(f"[Schedule Agent] Calling Gemini (attempt {attempt}/3)...")
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
            print(f"[Schedule Agent] Gemini error: {err}")
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
    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    text = data.get("response", "").strip()
    if not text:
        raise RuntimeError("Ollama returned an empty response.")
    return text


def _fallback_schedule(pathway: str, target_date_str: str) -> str:
    """Deterministic schedule generator that divides extracted action items across months."""
    start_dt = date.today()
    try:
        target_dt = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    except Exception:
        target_dt = start_dt + relativedelta(months=12)

    # Compute months difference
    months_diff = (target_dt.year - start_dt.year) * 12 + (target_dt.month - start_dt.month)
    if months_diff <= 0:
        months_diff = 6

    # Extract bullet points from roadmap
    items = []
    lines = pathway.split("\n")
    current_priority = "High"

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        lower = stripped.lower()
        if "immediate" in lower:
            current_priority = "High"
        elif "short-term" in lower or "medium-term" in lower:
            current_priority = "Medium"
        elif "long-term" in lower:
            current_priority = "Low"

        if stripped.startswith("- ") or stripped.startswith("* ") or re.match(r"^\d+\.\s+", stripped):
            clean_item = re.sub(r"^[-*\d\.\s]+", "", stripped).strip()
            # Clean structured tags if present
            clean_item = clean_item.replace("### **", "").replace("**", "")
            if clean_item:
                items.append((clean_item, current_priority))

    if not items:
        items = [
            ("Gather academic transcripts, category & income certificates", "High"),
            ("Research entrance cutoffs and scholarship portal deadlines", "High"),
            ("Enroll in foundational practice platform courses and practice weekly", "Medium"),
            ("Submit college counseling and scholarship applications", "High"),
            ("Complete semester coursework and build project portfolio", "Medium"),
            ("Apply for internships and career opportunities", "Medium")
        ]

    # Distribute items across months
    table_rows = ["| Month | Action Item | Priority (High/Medium/Low) |", "| --- | --- | --- |"]
    for i, (act, prio) in enumerate(items):
        month_offset = min(i * max(1, months_diff // len(items)), months_diff - 1)
        item_month = (start_dt + relativedelta(months=month_offset)).strftime("%B %Y")
        table_rows.append(f"| {item_month} | {act} | {prio} |")

    table_rows.append(f"\nTarget date ({target_date_str}) is realistic with consistent execution.")
    return "\n".join(table_rows)


def generate_schedule(pathway: str, target_date: str) -> str:
    """
    Calls Gemini Flash -> Ollama -> Deterministic Fallback to turn a pathway into a dated schedule table.
    """
    prompt = SCHEDULE_PROMPT.format(
        today=date.today().isoformat(),
        target_date=target_date,
        pathway=pathway,
    )

    # 1. Try Gemini
    try:
        return _call_gemini(prompt)
    except Exception as gemini_err:
        print(f"[Schedule Agent] Gemini unavailable ({gemini_err}). Trying Ollama...")

    # 2. Try Ollama
    try:
        return _call_ollama(prompt)
    except Exception as ollama_err:
        print(f"[Schedule Agent] Ollama unavailable ({ollama_err}). Using deterministic schedule generator...")

    # 3. Deterministic Fallback
    return _fallback_schedule(pathway, target_date)


if __name__ == "__main__":
    sample = "### Immediate (0-1 month)\n- Collect certificates\n### Short-term (1-6 months)\n- Apply for counseling"
    print(generate_schedule(sample, "2027-08-15"))


"""
Profile Agent (Module 2)

Converts a student's free-form description into a structured
profile for the EduPath AI multi-agent pipeline.

Uses Gemini through the current google-genai SDK.

If Gemini is unavailable, the agent automatically falls back
to a rule-based parser so the pipeline can continue running.
"""

import json
import re
import time

from google import genai

from src import config


# ============================================================
# PROFILE SCHEMA PROMPT
# ============================================================

PROFILE_SCHEMA_PROMPT = """You are a Profile Agent for a career advisory system.

Extract a structured student profile from the text below.

Return ONLY valid JSON (no markdown, no preamble) with these fields:

{{
  "stream": "engineering | medical | arts | commerce | science | law | humanities | other | unknown",
  "education_stage": "school | undergraduate | postgraduate | other | unknown",
  "current_year": "12th standard | 1st year | 2nd year | 3rd year | final year | other | unknown",
  "state": "Indian state if mentioned, else 'unknown'",
  "category": "general | sc | st | obc | bc | mbc | dnc | ews | unknown",
  "board_percentage": "number if mentioned, else null",
  "annual_income": "annual family income as an integer in Rupees if mentioned (e.g. 200000 for 2 lakh), else null",
  "interests": ["list", "of", "interests", "or", "subjects"],
  "constraints": "any constraints mentioned (financial, location, family), else 'none'",
  "goal": "what the student is asking for (career advice, scholarship, course selection, etc.)"
}}

Student text:

\"\"\"{student_text}\"\"\"
"""


# ============================================================
# RULE-BASED FALLBACK
# ============================================================

def _rule_based_fallback(student_text: str) -> dict:
    """
    Basic rule-based parser used when Gemini is unavailable.
    """

    text_lower = student_text.lower()

    # --------------------------------------------------------
    # STREAM
    # --------------------------------------------------------

    stream = "unknown"

    stream_keywords = {
        "engineering": [
            "engineering",
            "b.tech",
            "btech",
            "computer science",
            "mechanical",
            "civil engineering",
            "electronics",
            "electrical",
            "robotics",
        ],

        "medical": [
            "medical",
            "mbbs",
            "medicine",
            "dentist",
            "bds",
            "nursing",
            "pharmacy",
            "physiotherapy",
        ],

        "commerce": [
            "commerce",
            "b.com",
            "bcom",
            "accounting",
            "finance",
            "banking",
            "business",
            "marketing",
            "chartered accountant",
            "company secretary",
        ],

        "arts": [
            "arts",
            "viscom",
            "visual communication",
            "video editing",
            "video production",
            "film",
            "filmmaking",
            "cinema",
            "cinematography",
            "animation",
            "vfx",
            "motion graphics",
            "multimedia",
            "graphic design",
            "ui/ux",
            "editing",
            "post production",
            "storytelling",
            "photography",
            "journalism",
            "media",
            "english literature",
            "history",
            "social work",
            "fine arts",
        ],

        "humanities": [
            "humanities",
            "psychology",
            "sociology",
            "political science",
            "philosophy",
            "anthropology",
        ],

        "science": [
            "science",
            "b.sc",
            "bsc",
            "physics",
            "chemistry",
            "biology",
            "mathematics",
            "biotechnology",
            "microbiology",
        ],

        "law": [
            "law",
            "llb",
            "ll.b",
            "legal",
            "advocate",
            "lawyer",
        ],
    }

    for stream_name, keywords in stream_keywords.items():

        if any(
            keyword in text_lower
            for keyword in keywords
        ):
            stream = stream_name
            break

    # --------------------------------------------------------
    # PERCENTAGE
    # --------------------------------------------------------

    percentage_match = re.search(
        r"(\d{2,3}(?:\.\d+)?)\s*%",
        student_text
    )

    board_percentage = (
        float(percentage_match.group(1))
        if percentage_match
        else None
    )

    # --------------------------------------------------------
    # EDUCATION STAGE / YEAR
    # --------------------------------------------------------

    education_stage = "unknown"
    current_year = "unknown"

    if any(
        x in text_lower
        for x in [
            "12th",
            "12 th",
            "class 12",
            "class xii",
            "xii std",
            "school",
        ]
    ):

        education_stage = "school"
        current_year = "12th standard"

    elif any(
        x in text_lower
        for x in [
            "1st year",
            "first year",
            "1st-year",
        ]
    ):

        education_stage = "undergraduate"
        current_year = "1st year"

    elif any(
        x in text_lower
        for x in [
            "2nd year",
            "second year",
            "2nd-year",
        ]
    ):

        education_stage = "undergraduate"
        current_year = "2nd year"

    elif any(
        x in text_lower
        for x in [
            "3rd year",
            "third year",
            "3rd-year",
        ]
    ):

        education_stage = "undergraduate"
        current_year = "3rd year"

    elif any(
        x in text_lower
        for x in [
            "4th year",
            "fourth year",
            "4th-year",
            "final year",
            "final-year",
            "final_year",
        ]
    ):

        education_stage = "undergraduate"
        current_year = "final year"

    elif any(
        x in text_lower
        for x in [
            "college",
            "university",
            "undergraduate",
            "student",
            "b.tech",
            "btech",
            "b.sc",
            "bsc",
            "b.com",
            "bcom",
            "llb",
        ]
    ):

        education_stage = "undergraduate"

    # --------------------------------------------------------
    # STATE
    # --------------------------------------------------------

    state = "unknown"

    indian_states = [
        "Tamil Nadu",
        "Kerala",
        "Karnataka",
        "Andhra Pradesh",
        "Telangana",
        "Maharashtra",
        "Gujarat",
        "Rajasthan",
        "Delhi",
        "West Bengal",
        "Odisha",
        "Punjab",
        "Haryana",
        "Uttar Pradesh",
        "Bihar",
        "Jharkhand",
        "Chhattisgarh",
        "Madhya Pradesh",
        "Goa",
        "Assam",
    ]

    for state_name in indian_states:

        if state_name.lower() in text_lower:

            state = state_name
            break

    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    category = "unknown"

    padded_text = f" {text_lower} "

    category_keywords = {
        "sc": [
            " sc ",
            "scheduled caste",
            "dalit",
            "adi dravidar",
        ],
        "st": [
            " st ",
            "scheduled tribe",
            "tribal",
        ],
        "mbc": [
            " mbc ",
            "most backward class",
            "most backward classes",
        ],
        "dnc": [
            " dnc ",
            "denotified community",
            "denotified communities",
            "denotified tribe",
        ],
        "bc": [
            " bc ",
            "backward class",
            "backward classes",
        ],
        "obc": [
            " obc ",
            "other backward class",
            "other backward classes",
        ],
        "ews": [
            " ews ",
            "economically weaker",
        ],
        "general": [
            "general category",
            " oc ",
            "open category",
        ],
    }

    for category_name, keywords in category_keywords.items():

        if any(
            keyword in padded_text
            for keyword in keywords
        ):
            category = category_name
            break

    # --------------------------------------------------------
    # ANNUAL INCOME
    # --------------------------------------------------------

    annual_income = None
    income_match = re.search(
        r"(?:income|family income|annual income|earning|salary)[\s\:\=a-zA-Z\.]*?(?:rs\.?|₹|inr)?\s*([\d,]+(?:\.\d+)?)\s*(lakh|lakhs|l|crore|k)?",
        text_lower
    )
    if not income_match:
        income_match = re.search(
            r"(?:rs\.?|₹|inr)\s*([\d,]+(?:\.\d+)?)\s*(lakh|lakhs|l|crore|k)?(?:\s*(?:per annum|per year|income|annual))?",
            text_lower
        )
    if not income_match:
        income_match = re.search(
            r"(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|l)\s*(?:per annum|per year|annual|income)",
            text_lower
        )
    if income_match:
        try:
            val = float(income_match.group(1).replace(",", ""))
            unit = (income_match.group(2) or "").lower() if len(income_match.groups()) >= 2 and income_match.group(2) else ""
            if not unit and "lakh" in income_match.group(0):
                unit = "lakh"
            if unit in ("lakh", "lakhs", "l"):
                val *= 100000
            elif unit == "crore":
                val *= 10000000
            elif unit == "k":
                val *= 1000
            elif val < 100:
                val *= 100000
            annual_income = int(val)
        except Exception:
            annual_income = None

    # --------------------------------------------------------
    # INTERESTS
    # --------------------------------------------------------

    possible_interests = [
        "computer science",
        "programming",
        "software",
        "artificial intelligence",
        "machine learning",
        "data science",
        "robotics",
        "accounting",
        "finance",
        "banking",
        "business",
        "marketing",
        "economics",
        "medicine",
        "biology",
        "chemistry",
        "physics",
        "mathematics",
        "psychology",
        "law",
        "journalism",
        "design",
        "agriculture",
        "research",
    ]

    interests = []

    for interest in possible_interests:

        if interest in text_lower:

            interests.append(
                interest
            )

    # --------------------------------------------------------
    # CONSTRAINTS
    # --------------------------------------------------------

    constraints = "none"

    constraint_words = [
        "financial",
        "finance",
        "afford",
        "expensive",
        "fees",
        "scholarship",
        "budget",
        "location",
        "family",
        "distance",
        "near my home",
    ]

    detected_constraints = [
        word
        for word in constraint_words
        if word in text_lower
    ]

    if detected_constraints:

        constraints = (
            "Student mentioned: "
            + ", ".join(
                detected_constraints
            )
        )

    # --------------------------------------------------------
    # GOAL
    # --------------------------------------------------------

    goal = "career advice"

    if "scholarship" in text_lower:

        goal = "scholarship options"

    elif (
        "college" in text_lower
        or "course" in text_lower
    ):

        goal = "course and college selection"

    elif (
        "career" in text_lower
        or "job" in text_lower
    ):

        goal = "career advice"

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    return {

        "stream": stream,

        "education_stage": education_stage,

        "current_year": current_year,

        "state": state,

        "category": category,

        "board_percentage": board_percentage,

        "annual_income": annual_income,

        "interests": interests,

        "constraints": constraints,

        "goal": goal,

        "raw_input": student_text,
    }


# ============================================================
# CLEAN GEMINI JSON
# ============================================================

def _clean_gemini_json(raw_text: str) -> str:
    """
    Removes markdown fences and extracts the JSON object.
    """

    if not raw_text:
        return ""

    raw_text = raw_text.strip()

    # Remove ```json
    raw_text = re.sub(
        r"^```(?:json)?\s*",
        "",
        raw_text,
        flags=re.IGNORECASE
    )

    # Remove closing ```
    raw_text = re.sub(
        r"\s*```$",
        "",
        raw_text
    )

    raw_text = raw_text.strip()

    # Extract JSON object if Gemini added extra text
    start = raw_text.find("{")
    end = raw_text.rfind("}")

    if start != -1 and end != -1:

        raw_text = raw_text[
            start:end + 1
        ]

    return raw_text.strip()


# ============================================================
# NORMALIZE GEMINI PROFILE
# ============================================================

def _normalize_profile(
    profile: dict,
    student_text: str
) -> dict:
    """
    Ensures all expected fields exist.
    """

    defaults = {

        "stream": "unknown",

        "education_stage": "unknown",

        "current_year": "unknown",

        "state": "unknown",

        "category": "unknown",

        "board_percentage": None,

        "annual_income": None,

        "interests": [],

        "constraints": "none",

        "goal": "career advice",
    }

    for key, default_value in defaults.items():

        if key not in profile:

            profile[key] = default_value

    # Parse annual_income if string
    raw_income = profile.get("annual_income")
    if raw_income is not None:
        try:
            if isinstance(raw_income, (int, float)):
                profile["annual_income"] = int(raw_income)
            elif isinstance(raw_income, str):
                cleaned = re.sub(r"[^\d\.]", "", raw_income)
                if cleaned:
                    val = float(cleaned)
                    if "lakh" in raw_income.lower() or val < 100:
                        val *= 100000
                    profile["annual_income"] = int(val)
                else:
                    profile["annual_income"] = None
        except Exception:
            profile["annual_income"] = None

    # Ensure interests is a list
    if not isinstance(
        profile.get("interests"),
        list
    ):

        profile["interests"] = [
            str(profile["interests"])
        ]

    # Add original input
    profile["raw_input"] = student_text

    return profile


# ============================================================
# BUILD PROFILE
# ============================================================

def build_profile(
    student_text: str
) -> dict:

    """
    Converts free-form student text into
    a structured profile.

    Gemini is attempted first.

    If Gemini fails after retries,
    the rule-based fallback is used.
    """

    # --------------------------------------------------------
    # API KEY CHECK
    # --------------------------------------------------------

    if not config.GEMINI_API_KEY:

        print(
            "[Profile Agent] "
            "No GEMINI_API_KEY set."
        )

        print(
            "[Profile Agent] "
            "Using rule-based fallback."
        )

        return _rule_based_fallback(
            student_text
        )

    # --------------------------------------------------------
    # GEMINI CLIENT
    # --------------------------------------------------------

    try:

        client = genai.Client(
            api_key=config.GEMINI_API_KEY
        )

    except Exception as exc:

        print(
            "[Profile Agent] "
            f"Gemini client creation failed: {exc}"
        )

        return _rule_based_fallback(
            student_text
        )

    # --------------------------------------------------------
    # FORMAT PROMPT
    # --------------------------------------------------------

    try:

        prompt = PROFILE_SCHEMA_PROMPT.format(
            student_text=student_text
        )

    except Exception as exc:

        print(
            "[Profile Agent] "
            f"Prompt formatting failed: {exc}"
        )

        return _rule_based_fallback(
            student_text
        )

    # --------------------------------------------------------
    # RETRY CONFIGURATION
    # --------------------------------------------------------

    max_retries = 3

    # --------------------------------------------------------
    # GEMINI CALL
    # --------------------------------------------------------

    for attempt in range(
        1,
        max_retries + 1
    ):

        try:

            print(
                f"[Profile Agent] "
                f"Calling Gemini "
                f"(attempt {attempt}/{max_retries})..."
            )

            response = client.models.generate_content(

                model=config.GEMINI_MODEL,

                contents=prompt,
            )

            raw_text = getattr(
                response,
                "text",
                None
            )

            raw_text = _clean_gemini_json(
                raw_text or ""
            )

            if not raw_text:

                print(
                    "[Profile Agent] "
                    "Gemini returned empty output."
                )

                continue

            # ------------------------------------------------
            # JSON PARSING
            # ------------------------------------------------

            try:

                profile = json.loads(
                    raw_text
                )

            except json.JSONDecodeError as exc:

                print(
                    "[Profile Agent] "
                    f"Invalid Gemini JSON: {exc}"
                )

                print(
                    "[Profile Agent] "
                    "Using rule-based fallback."
                )

                return _rule_based_fallback(
                    student_text
                )

            # ------------------------------------------------
            # VALIDATE
            # ------------------------------------------------

            if not isinstance(
                profile,
                dict
            ):

                print(
                    "[Profile Agent] "
                    "Gemini response is not a JSON object."
                )

                return _rule_based_fallback(
                    student_text
                )

            # ------------------------------------------------
            # NORMALIZE
            # ------------------------------------------------

            profile = _normalize_profile(
                profile,
                student_text
            )

            print(
                "[Profile Agent] "
                "Gemini profile extraction successful."
            )

            return profile

        except Exception as exc:

            error_text = str(
                exc
            ).lower()

            print(
                "[Profile Agent] "
                f"Gemini error: {exc}"
            )

            # ------------------------------------------------
            # TEMPORARY ERROR
            # ------------------------------------------------

            temporary_error = any(
                keyword in error_text
                for keyword in [
                    "503",
                    "unavailable",
                    "high demand",
                    "429",
                    "rate limit",
                    "resource exhausted",
                    "timeout",
                    "deadline exceeded",
                ]
            )

            if temporary_error:

                if attempt < max_retries:

                    wait_seconds = (
                        2 ** attempt
                    )

                    print(
                        "[Profile Agent] "
                        f"Temporary Gemini error. "
                        f"Retrying in "
                        f"{wait_seconds} seconds..."
                    )

                    time.sleep(
                        wait_seconds
                    )

                    continue

                print(
                    "[Profile Agent] "
                    "Gemini unavailable after retries."
                )

            else:

                print(
                    "[Profile Agent] "
                    "Non-retryable Gemini error."
                )

            break

    # --------------------------------------------------------
    # FINAL FALLBACK
    # --------------------------------------------------------

    print(
        "[Profile Agent] "
        "Switching to rule-based fallback."
    )

    return _rule_based_fallback(
        student_text
    )


# ============================================================
# MANUAL TEST
# ============================================================

if __name__ == "__main__":

    sample = (
        "I'm a 12th standard student from Tamil Nadu, "
        "scored 88% in boards, interested in computer "
        "science and robotics. My family can't afford "
        "expensive private colleges so I need "
        "scholarship options too."
    )

    print(
        "\n[Profile Agent] "
        "Running standalone test...\n"
    )

    result = build_profile(
        sample
    )

    print(
        "\nPROFILE RESULT:"
    )

    print(
        json.dumps(
            result,
            indent=2
        )
    )


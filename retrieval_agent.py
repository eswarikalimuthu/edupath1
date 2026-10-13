"""
Retrieval Agent (Module 2)

Personalized RAG retrieval for EduPath AI.

Pipeline:

Student Profile
      ↓
Stream + Interest + Domain Detection
      ↓
Personalized Category Queries
      ↓
ChromaDB Semantic Search
      ↓
Stream / Domain / Location Filtering
      ↓
Record Quality Scoring
      ↓
Weighted Re-ranking
      ↓
Career / Institute Deduplication
      ↓
Eligibility / Historical Metadata
      ↓
Grounded Results for Recommendation Agent
"""

import re
import functools

import chromadb
from sentence_transformers import SentenceTransformer

from src import config


# ============================================================
# LAZY LOADING
# ============================================================

_model = None
_client = None
_collection = None


def _get_model():
    global _model

    if _model is None:
        _model = SentenceTransformer(
            config.EMBEDDING_MODEL
        )

    return _model


def _get_collection():
    global _client, _collection

    if _collection is None:
        _client = chromadb.PersistentClient(
            path=config.CHROMA_DB_DIR
        )

        _collection = _client.get_or_create_collection(
            name=config.COLLECTION_NAME
        )

    return _collection


# ============================================================
# BASIC SEMANTIC SEARCH & CACHING
# ============================================================

@functools.lru_cache(maxsize=1024)
def _get_cached_query_embedding(query_text: str) -> tuple:
    """Caches dense vector embeddings for queries to prevent redundant neural model inference."""
    model = _get_model()
    return tuple(model.encode([query_text])[0].tolist())


def search(
    query_text: str,
    category: str = None,
    top_k: int = config.RETRIEVAL_TOP_K
) -> list[dict]:

    collection = _get_collection()

    query_embedding = [list(_get_cached_query_embedding(query_text))]

    where_filter = (
        {"category": category}
        if category
        else None
    )

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        where=where_filter
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    return [
        {
            "text": doc,
            "source": meta.get("source", ""),
            "category": meta.get("category", ""),
            "score": round(
                max(0.0, 1 - dist),
                3
            ),
        }
        for doc, meta, dist in zip(
            documents,
            metadatas,
            distances
        )
    ]


# ============================================================
# TEXT HELPERS
# ============================================================

def _clean_text(value) -> str:

    if value is None:
        return ""

    if isinstance(value, list):
        return " ".join(
            str(item)
            for item in value
        )

    return str(value)


def _normalize(text: str) -> str:

    return re.sub(
        r"\s+",
        " ",
        _clean_text(text).lower()
    ).strip()


def _keyword_match(
    text: str,
    keyword: str
) -> bool:
    """
    Safer keyword matching.

    Prevents short keywords such as:
    AI, ML, IT, BE, BA, CA

    from accidentally matching inside unrelated words.
    """

    text = _normalize(text)
    keyword = _normalize(keyword)

    if not keyword:
        return False

    # Short keywords need word boundaries.
    if len(keyword) <= 3:
        return bool(
            re.search(
                rf"(?<!\w){re.escape(keyword)}(?!\w)",
                text
            )
        )

    return keyword in text


def _contains_any(
    text: str,
    keywords: list[str]
) -> bool:

    return any(
        _keyword_match(text, keyword)
        for keyword in keywords
    )


# ============================================================
# LOCATION DATA
# ============================================================

STATE_ALIASES = {
    "tamil nadu": [
        "tamil nadu",
        "tamilnadu"
    ],
    "karnataka": [
        "karnataka"
    ],
    "kerala": [
        "kerala"
    ],
    "andhra pradesh": [
        "andhra pradesh"
    ],
    "telangana": [
        "telangana"
    ],
    "maharashtra": [
        "maharashtra"
    ],
    "delhi": [
        "delhi",
        "new delhi"
    ],
    "uttar pradesh": [
        "uttar pradesh"
    ],
    "west bengal": [
        "west bengal"
    ],
    "rajasthan": [
        "rajasthan"
    ],
    "gujarat": [
        "gujarat"
    ],
    "odisha": [
        "odisha"
    ],
    "punjab": [
        "punjab"
    ],
    "haryana": [
        "haryana"
    ],
}


TN_DISTRICTS = [
    "chennai",
    "coimbatore",
    "madurai",
    "tiruchirappalli",
    "trichy",
    "kancheepuram",
    "chengalpattu",
    "salem",
    "erode",
    "tiruppur",
    "vellore",
    "thoothukudi",
    "tuticorin",
    "tirunelveli",
    "thanjavur",
    "dindigul",
    "virudhunagar",
    "kanyakumari",
    "namakkal",
    "dharmapuri",
    "krishnagiri",
    "cuddalore",
    "villupuram",
    "kallakurichi",
    "nagapattinam",
    "mayiladuthurai",
    "ramanathapuram",
    "sivaganga",
    "pudukkottai",
    "nilgiris",
    "the nilgiris",
    "perambalur",
    "ariyalur",
    "karur",
    "tenkasi",
    "thiruvarur",
]


OTHER_STATE_LOCATIONS = {
    "karnataka": [
        "bengaluru",
        "bangalore",
        "mysuru",
        "mysore",
        "mangalore",
        "hubli",
    ],
    "kerala": [
        "kochi",
        "cochin",
        "thiruvananthapuram",
        "trivandrum",
        "kozhikode",
    ],
    "telangana": [
        "hyderabad",
        "warangal",
    ],
    "andhra pradesh": [
        "vijayawada",
        "visakhapatnam",
        "vizag",
        "tirupati",
    ],
    "maharashtra": [
        "mumbai",
        "pune",
        "nagpur",
    ],
    "delhi": [
        "new delhi",
        "delhi",
    ],
}


# ============================================================
# DOMAIN KEYWORDS
# ============================================================

DOMAIN_KEYWORDS = {

    "computer_science": [
        "computer science",
        "programming",
        "software",
        "coding",
        "developer",
        "web development",
        "app development",
        "information technology",
        "it",
    ],

    "ai_ml": [
        "artificial intelligence",
        "machine learning",
        "ai",
        "ml",
        "deep learning",
        "data science",
        "data scientist",
        "neural network",
    ],

    "robotics": [
        "robotics",
        "robot",
        "automation",
        "embedded",
        "arduino",
        "raspberry pi",
        "control systems",
        "mechatronics",
    ],

    "electronics": [
        "electronics",
        "ece",
        "electrical",
        "eee",
        "embedded systems",
        "circuits",
        "microcontroller",
        "vlsi",
    ],

    "mechanical": [
        "mechanical",
        "automobile",
        "manufacturing",
        "cad",
        "thermodynamics",
        "mechanics",
    ],

    "civil": [
        "civil engineering",
        "construction",
        "structural",
        "architecture",
        "surveying",
        "urban planning",
    ],

    "commerce_finance": [
        "commerce",
        "accounting",
        "finance",
        "financial",
        "banking",
        "investment",
        "taxation",
        "audit",
        "chartered accountant",
        "company secretary",
        "business",
        "management",
    ],

    "law": [
        "law",
        "legal",
        "llb",
        "llm",
        "advocate",
        "lawyer",
        "corporate law",
        "cyber law",
        "intellectual property",
        "criminal law",
    ],

    "medical": [
        "medicine",
        "medical",
        "mbbs",
        "doctor",
        "healthcare",
        "clinical",
        "nursing",
        "physiotherapy",
        "pharmacy",
        "dentistry",
        "bds",
    ],

    "life_science": [
        "biology",
        "biotechnology",
        "microbiology",
        "biochemistry",
        "zoology",
        "botany",
        "genetics",
        "life science",
    ],

    "physical_science": [
        "physics",
        "chemistry",
        "mathematics",
        "statistics",
        "astronomy",
        "geology",
        "scientific research",
    ],

    "psychology": [
        "psychology",
        "psychologist",
        "counselling",
        "counseling",
        "mental health",
        "behavioral science",
    ],

    "humanities": [
        "history",
        "political science",
        "sociology",
        "philosophy",
        "anthropology",
        "archaeology",
        "geography",
        "humanities",
        "literature",
        "english",
    ],

    "journalism_media": [
        "journalism",
        "journalist",
        "media",
        "mass communication",
        "content writing",
        "content creator",
        "public relations",
        "broadcasting",
    ],

    "design": [
        "design",
        "graphic design",
        "ui ux",
        "ui/ux",
        "fashion",
        "animation",
        "visual design",
        "product design",
        "interior design",
    ],

    "agriculture": [
        "agriculture",
        "agricultural",
        "farming",
        "horticulture",
        "agronomy",
        "fisheries",
        "dairy",
    ],

    "environment": [
        "environment",
        "environmental science",
        "climate",
        "ecology",
        "sustainability",
        "conservation",
        "forestry",
    ],

    "education": [
        "teaching",
        "teacher",
        "education",
        "school",
        "professor",
        "lecturer",
        "training",
    ],

    "government": [
        "civil services",
        "government",
        "public administration",
        "police",
        "defence",
        "defense",
        "ias",
        "ips",
        "government officer",
    ],

    "hospitality_tourism": [
        "hospitality",
        "hotel management",
        "tourism",
        "travel",
        "culinary",
        "hotel",
        "event management",
    ],

    "aviation": [
        "aviation",
        "pilot",
        "airport",
        "aerospace",
        "aircraft",
        "cabin crew",
    ],

    "maritime": [
        "maritime",
        "marine",
        "shipping",
        "merchant navy",
        "nautical",
        "ocean",
    ],

    "food_science": [
        "food technology",
        "food science",
        "food safety",
        "nutrition",
        "dairy technology",
    ],

    "biotechnology": [
        "biotechnology",
        "biotech",
        "genetic engineering",
        "bioinformatics",
        "molecular biology",
    ],

    "cybersecurity": [
        "cybersecurity",
        "cyber security",
        "ethical hacking",
        "penetration testing",
        "information security",
        "digital forensics",
    ],

    "cloud_devops": [
        "cloud",
        "aws",
        "azure",
        "google cloud",
        "devops",
        "docker",
        "kubernetes",
    ],

    "blockchain": [
        "blockchain",
        "web3",
        "cryptocurrency",
        "smart contract",
        "solidity",
    ],

    "gaming": [
        "game development",
        "gaming",
        "unity",
        "unreal",
        "game developer",
    ],
}


# ============================================================
# STREAM KEYWORDS
# ============================================================

STREAM_KEYWORDS = {

    "commerce": [
        "commerce",
        "b.com",
        "bcom",
        "bba",
        "accounting",
        "finance",
        "business",
        "management",
        "banking",
        "marketing",
        "economics",
        "ca",
        "company secretary",
    ],

    "engineering": [
        "engineering",
        "b.e",
        "be",
        "btech",
        "b.tech",
        "computer science",
        "information technology",
        "mechanical",
        "civil engineering",
        "electrical",
        "electronics",
        "robotics",
        "artificial intelligence",
        "data science",
        "aerospace",
    ],

    "medical": [
        "medical",
        "medicine",
        "mbbs",
        "bds",
        "nursing",
        "pharmacy",
        "b.pharm",
        "physiotherapy",
        "dentistry",
        "healthcare",
    ],

    "arts": [
        "arts",
        "b.a",
        "ba",
        "journalism",
        "psychology",
        "history",
        "political science",
        "sociology",
        "english",
        "literature",
        "design",
        "mass communication",
    ],

    "humanities": [
        "humanities",
        "arts",
        "history",
        "sociology",
        "political science",
        "psychology",
        "philosophy",
        "anthropology",
        "geography",
        "journalism",
        "public administration",
        "social work",
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
        "statistics",
        "zoology",
        "botany",
        "geology",
        "astronomy",
        "forensic science",
    ],

    "law": [
        "law",
        "llb",
        "ll.m",
        "llm",
        "ba llb",
        "b.a. ll.b",
        "bba llb",
        "bcom llb",
        "legal",
        "jurisprudence",
        "national law university",
        "nlu",
    ],
}


# ============================================================
# STREAM COURSE TERMS
# ============================================================

STREAM_COURSE_TERMS = {

    "engineering": [
        "b.e",
        "be",
        "b.tech",
        "btech",
        "computer science",
        "information technology",
        "artificial intelligence",
        "machine learning",
        "data science",
        "robotics",
        "mechatronics",
        "electronics",
        "electrical",
        "mechanical",
        "civil engineering",
        "aerospace",
        "automation",
    ],

    "commerce": [
        "b.com",
        "bcom",
        "bba",
        "accounting",
        "finance",
        "banking",
        "economics",
        "business",
        "management",
        "marketing",
        "commerce",
    ],

    "medical": [
        "mbbs",
        "bds",
        "b.pharm",
        "bpharm",
        "nursing",
        "physiotherapy",
        "medicine",
        "dentistry",
        "health sciences",
        "medical",
    ],

    "arts": [
        "b.a",
        "ba",
        "psychology",
        "history",
        "journalism",
        "mass communication",
        "english",
        "literature",
        "political science",
        "sociology",
        "social work",
        "design",
    ],

    "humanities": [
        "b.a",
        "ba",
        "psychology",
        "history",
        "sociology",
        "political science",
        "philosophy",
        "anthropology",
        "geography",
        "public administration",
        "international relations",
        "journalism",
    ],

    "science": [
        "b.sc",
        "bsc",
        "physics",
        "chemistry",
        "biology",
        "mathematics",
        "statistics",
        "biotechnology",
        "microbiology",
        "zoology",
        "botany",
        "geology",
        "astronomy",
        "forensic science",
        "food science",
    ],

    "law": [
        "llb",
        "ll.m",
        "llm",
        "ba llb",
        "b.a. ll.b",
        "bba llb",
        "bcom llb",
        "law",
        "legal studies",
        "national law university",
    ],
}


# ============================================================
# DOMAIN DETECTION
# ============================================================

def _detect_domains(
    profile: dict
) -> list[str]:

    stream = _normalize(
        profile.get("stream", "")
    )

    interests = _normalize(
        " ".join(
            str(x)
            for x in profile.get(
                "interests",
                []
            )
        )
    )

    goal = _normalize(
        profile.get(
            "goal",
            ""
        )
    )

    combined = (
        f"{stream} "
        f"{interests} "
        f"{goal}"
    )

    matches = []

    for domain, keywords in DOMAIN_KEYWORDS.items():

        score = 0

        for keyword in keywords:
            if _keyword_match(
                combined,
                keyword
            ):
                score += 1

        if score > 0:
            matches.append(
                (
                    domain,
                    score
                )
            )

    matches.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return [
        domain
        for domain, _ in matches[:5]
    ]


# ============================================================
# BUILD PROFILE CONTEXT
# ============================================================

def _build_profile_context(
    profile: dict
) -> str:

    stream = profile.get(
        "stream",
        "unknown"
    )

    education_stage = profile.get(
        "education_stage",
        "unknown"
    )

    current_year = profile.get(
        "current_year",
        "unknown"
    )

    state = profile.get(
        "state",
        "unknown"
    )

    category = profile.get(
        "category",
        "unknown"
    )

    interests = profile.get(
        "interests",
        []
    )

    constraints = profile.get(
        "constraints",
        "none"
    )

    goal = profile.get(
        "goal",
        "career advice"
    )

    domains = _detect_domains(
        profile
    )

    interests_text = (
        ", ".join(
            str(i)
            for i in interests
        )
        if interests
        else "not specified"
    )

    domains_text = (
        ", ".join(domains)
        if domains
        else "general"
    )

    return (
        f"Stream: {stream}. "
        f"Education stage: {education_stage}. "
        f"Current year: {current_year}. "
        f"State: {state}. "
        f"Category: {category}. "
        f"Interests: {interests_text}. "
        f"Career domains: {domains_text}. "
        f"Constraints: {constraints}. "
        f"Goal: {goal}."
    )


# ============================================================
# PERSONALIZED QUERY BUILDER
# ============================================================

def _build_queries(
    profile: dict
) -> dict:

    stream = _normalize(
        profile.get(
            "stream",
            "student"
        )
    )

    education_stage = profile.get(
        "education_stage",
        "unknown"
    )

    current_year = profile.get(
        "current_year",
        "unknown"
    )

    state = profile.get(
        "state",
        "India"
    )

    category = profile.get(
        "category",
        "unknown"
    )

    interests = profile.get(
        "interests",
        []
    )

    interests_text = (
        ", ".join(
            str(x)
            for x in interests
        )
        if interests
        else stream
    )

    goal = profile.get(
        "goal",
        "career advice"
    )

    constraints = profile.get(
        "constraints",
        "none"
    )

    domains = _detect_domains(
        profile
    )

    domains_text = (
        ", ".join(domains)
        if domains
        else stream
    )

    course_terms = STREAM_COURSE_TERMS.get(
        stream,
        []
    )

    course_text = ", ".join(
        course_terms[:15]
    )

    career_query = f"""
    career paths, occupations and job roles
    for a {education_stage} {current_year}
    student from the {stream} stream.

    Interests: {interests_text}.
    Career domains: {domains_text}.
    Goal: {goal}.

    Relevant careers, required skills,
    qualifications, specializations,
    education pathways and opportunities.
    """

    course_query = f"""
    colleges, universities, undergraduate
    courses and degree programs for
    {stream} students interested in
    {interests_text}.

    Career domains: {domains_text}.
    Location: {state}, India.

    Relevant programs include:
    {course_text}.

    Find institutions, degree names,
    eligibility, admission pathways,
    government or affordable institutions
    where relevant.
    """

    scholarship_query = f"""
    scholarships and financial aid for
    {stream} students in {state}, India.

    Education stage: {education_stage}.
    Category: {category}.
    Academic performance and merit.

    Financial constraints: {constraints}.

    Relevant government, state, central,
    institutional and merit based scholarships.
    Eligibility requirements and benefits.
    """

    scheme_query = f"""
    government schemes, student welfare schemes,
    education support schemes and skill development
    programs for {stream} students in
    {state}, India.

    Education stage: {education_stage}.
    Interests: {interests_text}.
    Goal: {goal}.

    Include relevant central and state schemes,
    fee concessions, financial assistance,
    education support and skill development.
    """

    return {
        "career": career_query,
        "course": course_query,
        "scholarship": scholarship_query,
        "scheme": scheme_query,
    }


# ============================================================
# CAREER NAME EXTRACTION
# ============================================================

def _extract_career_name(
    text: str
) -> str | None:

    text_clean = _clean_text(text).strip()

    patterns = [
        r"career\s*:\s*([^,\n.]+)",
        r"career\s*name\s*:\s*([^,\n.]+)",
        r"occupation\s*:\s*([^,\n.]+)",
        r"job\s*role\s*:\s*([^,\n.]+)",
        r"title\s*:\s*([^,\n.]+)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text_clean,
            flags=re.IGNORECASE
        )

        if match:

            return (
                match.group(1)
                .strip()
                .lower()
            )

    return None


# ============================================================
# CAREER RECORD QUALITY
# ============================================================

def _career_record_quality(
    text: str,
    source: str
) -> tuple[int, str]:

    text_normalized = _normalize(text)
    source_normalized = _normalize(source)

    quality = 0

    # Canonical career dataset
    if re.search(
        r"\bcareer\s*:",
        text_normalized
    ):
        quality += 6
        record_type = "canonical_career"

    # Occupation / role record
    elif re.search(
        r"\boccupation\s*:|\bjob role\s*:",
        text_normalized
    ):
        quality += 4
        record_type = "career_record"

    # Job dataset / job posting
    elif (
        "jobid:" in text_normalized
        or "experiencelevel:" in text_normalized
        or "yearsofexperience:" in text_normalized
        or "job_dataset" in source_normalized
    ):
        quality -= 4
        record_type = "job_posting"

    else:
        quality += 1
        record_type = "career_record"

    return quality, record_type


# ============================================================
# CAREER DEDUPLICATION
# ============================================================

def _dedupe_by_career(
    chunks: list[dict]
) -> list[dict]:

    seen = {}

    for chunk in chunks:

        text = chunk.get(
            "text",
            ""
        )

        career_name = _extract_career_name(
            text
        )

        if not career_name:
            career_name = (
                _normalize(text)[:120]
            )

        # Select using retrieval score + record quality.
        selection_score = (
            float(
                chunk.get(
                    "retrieval_score",
                    0
                )
            )
            + float(
                chunk.get(
                    "_record_quality",
                    0
                )
            )
        )

        existing = seen.get(
            career_name
        )

        if (
            existing is None
            or selection_score
            > existing.get(
                "_selection_score",
                -999
            )
        ):

            updated = dict(chunk)

            updated["_selection_score"] = (
                selection_score
            )

            seen[career_name] = updated

    results = list(
        seen.values()
    )

    for item in results:
        item.pop(
            "_selection_score",
            None
        )
        item.pop(
            "_record_quality",
            None
        )

    return sorted(
        results,
        key=lambda x: x.get(
            "retrieval_score",
            0
        ),
        reverse=True
    )


# ============================================================
# INSTITUTE NAME EXTRACTION
# ============================================================

def _extract_institute_name(
    text: str
) -> str | None:

    patterns = [
        r"college\s*name\s*:\s*([^,\n.]+)",
        r"institute\s*name\s*:\s*([^,\n.]+)",
        r"institution\s*:\s*([^,\n.]+)",
        r"university\s*:\s*([^,\n.]+)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:

            return (
                match.group(1)
                .strip()
                .lower()
            )

    return None


# ============================================================
# COURSE RECORD QUALITY
# ============================================================

def _course_record_quality(
    text: str,
    source: str
) -> tuple[int, str]:

    text_normalized = _normalize(text)
    source_normalized = _normalize(source)

    quality = 0
    record_type = "course_record"

    # --------------------------------------------------------
    # Actual institution record
    # --------------------------------------------------------

    if re.search(
        r"college\s*name\s*:",
        text_normalized
    ):
        quality += 7
        record_type = "institution_record"

    elif re.search(
        r"institute\s*name\s*:|institution\s*:|university\s*:",
        text_normalized
    ):
        quality += 7
        record_type = "institution_record"

    # --------------------------------------------------------
    # Actual course / branch information
    # --------------------------------------------------------

    if re.search(
        r"branch\s*name\s*:",
        text_normalized
    ):
        quality += 4

    if re.search(
        r"course\s*name\s*:|program\s*:",
        text_normalized
    ):
        quality += 3

    # --------------------------------------------------------
    # Historical cutoff dataset
    # --------------------------------------------------------

    if re.search(
        r"\b20(1[0-9]|2[0-4])\b",
        text_normalized
    ):
        quality -= 2
        record_type = "historical_course_record"

    # --------------------------------------------------------
    # Generic reference PDF
    # --------------------------------------------------------

    reference_pdf = (
        "information_about_colleges"
        in source_normalized
        or "college information"
        in source_normalized
    )

    if reference_pdf:

        has_real_institution = re.search(
            r"college\s*name\s*:|"
            r"institute\s*name\s*:|"
            r"institution\s*:|"
            r"university\s*:",
            text_normalized
        )

        if not has_real_institution:

            quality -= 15
            record_type = "reference_document"

    # --------------------------------------------------------
    # Reference-style branch code tables
    # --------------------------------------------------------

    if (
        "branch code" in text_normalized
        and "branch name" not in text_normalized
        and "college name" not in text_normalized
    ):
        quality -= 8
        record_type = "reference_document"

    return quality, record_type


# ============================================================
# INSTITUTE DEDUPLICATION
# ============================================================

def _dedupe_by_institute(
    chunks: list[dict]
) -> list[dict]:

    seen = {}

    for chunk in chunks:

        text = chunk.get(
            "text",
            ""
        )

        institute_name = _extract_institute_name(
            text
        )

        if not institute_name:

            institute_name = (
                _normalize(text)[:150]
            )

        selection_score = (
            float(
                chunk.get(
                    "retrieval_score",
                    0
                )
            )
            + float(
                chunk.get(
                    "_record_quality",
                    0
                )
            )
        )

        existing = seen.get(
            institute_name
        )

        if (
            existing is None
            or selection_score
            > existing.get(
                "_selection_score",
                -999
            )
        ):

            updated = dict(chunk)

            updated["_selection_score"] = (
                selection_score
            )

            seen[institute_name] = updated

    results = list(
        seen.values()
    )

    for item in results:
        item.pop(
            "_selection_score",
            None
        )
        item.pop(
            "_record_quality",
            None
        )

    return sorted(
        results,
        key=lambda x: x.get(
            "retrieval_score",
            0
        ),
        reverse=True
    )


# ============================================================
# SCHOLARSHIP & SCHEME DEDUPLICATION
# ============================================================

def _extract_scholarship_name(text: str) -> str:
    patterns = [
        r"(?:scholarship name|name of scholarship|scheme name|scholarship)\s*[:\-]\s*([^\n,;\(\)]+)",
        r"(?:post-matric scholarship|pre-matric scholarship|pragati scholarship|saksham scholarship|national fellowship|cm scholarship|pudhumai penn|naan mudhalvan)[^\n,;\(\)]*"
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            val = m.group(0).strip()
            if len(val) > 4:
                return _normalize(val)[:100]
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if lines:
        cleaned = re.sub(r"^[\#\*\-\d\.\s]+", "", lines[0])
        return _normalize(cleaned)[:100]
    return _normalize(text)[:100]


def _dedupe_by_scholarship(chunks: list[dict]) -> list[dict]:
    seen = {}
    for chunk in chunks:
        name = _extract_scholarship_name(chunk.get("text", ""))
        score = float(chunk.get("retrieval_score", 0))
        if name not in seen or score > float(seen[name].get("retrieval_score", -999)):
            seen[name] = chunk
    return sorted(seen.values(), key=lambda x: x.get("retrieval_score", 0), reverse=True)


def _dedupe_by_scheme(chunks: list[dict]) -> list[dict]:
    seen = {}
    for chunk in chunks:
        name = _extract_scholarship_name(chunk.get("text", ""))
        score = float(chunk.get("retrieval_score", 0))
        if name not in seen or score > float(seen[name].get("retrieval_score", -999)):
            seen[name] = chunk
    return sorted(seen.values(), key=lambda x: x.get("retrieval_score", 0), reverse=True)


# ============================================================
# STREAM RELEVANCE
# ============================================================

def _stream_relevance(
    text: str,
    stream: str
) -> int:

    stream = _normalize(stream)

    keywords = STREAM_KEYWORDS.get(
        stream,
        []
    )

    text = _normalize(text)

    score = sum(
        1
        for keyword in keywords
        if _keyword_match(
            text,
            keyword
        )
    )

    # Prevent keyword-heavy documents
    # from dominating the ranking.
    return min(
        score,
        6
    )


# ============================================================
# INTEREST RELEVANCE
# ============================================================

def _interest_relevance(
    text: str,
    interests: list
) -> int:

    text = _normalize(text)

    score = 0

    for interest in interests:

        interest_text = _normalize(
            interest
        )

        if not interest_text:
            continue

        # Exact phrase
        if _keyword_match(
            text,
            interest_text
        ):
            score += 4

        # Individual meaningful words
        words = interest_text.split()

        for word in words:

            if len(word) >= 4:

                if _keyword_match(
                    text,
                    word
                ):
                    score += 1

    return min(
        score,
        8
    )


# ============================================================
# DOMAIN RELEVANCE
# ============================================================

def _domain_relevance(
    text: str,
    domains: list[str]
) -> int:

    text = _normalize(text)

    score = 0

    for domain in domains:

        keywords = DOMAIN_KEYWORDS.get(
            domain,
            []
        )

        domain_score = sum(
            1
            for keyword in keywords
            if _keyword_match(
                text,
                keyword
            )
        )

        score += min(
            domain_score,
            4
        )

    return min(
        score,
        8
    )


# ============================================================
# STATE RELEVANCE
# ============================================================

def _state_relevance(
    text: str,
    state: str
) -> int:

    if not state:
        return 0

    state = _normalize(state)

    if state in (
        "",
        "unknown",
        "india"
    ):
        return 0

    text = _normalize(text)

    aliases = STATE_ALIASES.get(
        state,
        [state]
    )

    # Exact state match
    if any(
        _keyword_match(
            text,
            alias
        )
        for alias in aliases
    ):
        return 6

    # Tamil Nadu district match
    if state == "tamil nadu":

        if any(
            _keyword_match(
                text,
                district
            )
            for district in TN_DISTRICTS
        ):
            return 5

    return 0


# ============================================================
# OUT-OF-STATE LOCATION PENALTY
# ============================================================

def _location_penalty(
    text: str,
    state: str
) -> int:

    state = _normalize(state)
    text = _normalize(text)

    if (
        not state
        or state == "unknown"
        or state == "india"
    ):
        return 0

    penalty = 0

    for other_state, locations in (
        OTHER_STATE_LOCATIONS.items()
    ):

        if other_state == state:
            continue

        if any(
            _keyword_match(
                text,
                location
            )
            for location in locations
        ):
            penalty = -8
            break

    return penalty


# ============================================================
# TEMPORAL INFORMATION
# ============================================================

def _temporal_metadata(
    text: str,
    source: str
) -> tuple[str | None, int]:

    combined = (
        _normalize(text)
        + " "
        + _normalize(source)
    )

    years = re.findall(
        r"\b(20\d{2})\b",
        combined
    )

    if not years:
        return None, 0

    try:
        latest_year = max(
            int(year)
            for year in years
        )
    except ValueError:
        return None, 0

    current_year = 2026

    if latest_year < current_year - 1:

        return (
            f"Historical data ({latest_year})",
            -2
        )

    return None, 0


# ============================================================
# SCHOLARSHIP ELIGIBILITY & INCOME MATCHING ENGINE
# ============================================================

def _parse_scholarship_income_limit(text: str) -> int | None:
    """
    Extracts numerical family income limit from scholarship text in INR.
    Handles '2.5 lakh', '2,50,000', 'Rs 200000', '8 lakhs', etc.
    """
    text_lower = text.lower()
    patterns = [
        r"(?:income|family income|annual income|parental income|annual family income)[^\.\n;]{0,60}?(?:not exceed|below|less than|up to|upto|within|maximum of|ceiling of)?\s*(?:rs\.?|₹|inr)?\s*([\d,]+(?:\.\d+)?)\s*(lakh|lakhs|l|crore|k)?",
        r"(?:rs\.?|₹|inr)?\s*([\d,]+(?:\.\d+)?)\s*(?:lakh|lakhs|l)\s*(?:per annum|p\.a\.|annual income|family income)",
        r"(?:income ceiling|ceiling)[^\.\n;]{0,40}?(?:rs\.?|₹|inr)?\s*([\d,]+(?:\.\d+)?)\s*(lakh|lakhs|l)?"
    ]
    for pattern in patterns:
        m = re.search(pattern, text_lower)
        if m:
            try:
                val = float(m.group(1).replace(",", ""))
                unit = m.group(2).lower() if len(m.groups()) >= 2 and m.group(2) else ""
                if not unit and "lakh" in m.group(0):
                    unit = "lakh"
                if unit in ("lakh", "lakhs", "l"):
                    val *= 100000
                elif unit == "crore":
                    val *= 10000000
                elif unit == "k":
                    val *= 1000
                elif val <= 50:
                    val *= 100000
                if 20000 <= val <= 50000000:
                    return int(val)
            except Exception:
                continue
    return None


def _evaluate_scholarship(text: str, profile: dict) -> dict:
    """
    Performs deterministic, explainable evaluation of scholarship eligibility
    considering social category (SC/ST/BC/MBC/DNC/OBC/EWS), income ceiling,
    state residency, education stage, and gender.
    """
    text_lower = _normalize(text)
    user_category = _normalize(profile.get("category", "unknown"))
    user_income = profile.get("annual_income")
    user_state = _normalize(profile.get("state", "unknown"))
    user_gender = _normalize(profile.get("gender", "unknown"))
    user_stage = _normalize(profile.get("education_stage", "unknown"))
    user_year = _normalize(profile.get("current_year", "unknown"))

    # 1. Target Social Category Detection
    is_sc_targeted = any(t in text_lower for t in [
        "scheduled caste", "sc student", "sc students", "adi dravidar",
        "arunthathiyar", "post matric scholarship for sc", "post-matric scholarship for sc", "sc/st"
    ])
    is_st_targeted = (any(t in text_lower for t in [
        "scheduled tribe", "st student", "st students", "tribal"
    ]) or "st scholarship" in text_lower) and not is_sc_targeted

    is_bc_mbc_targeted = any(t in text_lower for t in [
        "backward class", "backward classes", "most backward class", "most backward classes",
        "mbc", "dnc", "denotified community", "denotified communities", "bc/mbc", "bc, mbc", "bcm"
    ]) and not ("irrespective of caste" in text_lower or "all categories" in text_lower)

    is_minority_targeted = any(t in text_lower for t in [
        "minority", "minorities", "muslim", "christian", "jain", "buddhist", "sikh"
    ]) and not ("irrespective of" in text_lower)

    is_girls_only = any(t in text_lower for t in [
        "for girls only", "girl students only", "female students only", "pragati scholarship", "pudhumai penn"
    ])

    category_status = "eligible"
    category_score = 0.0
    category_match_desc = "Open to all categories"

    if user_category == "sc":
        if is_sc_targeted:
            category_status = "eligible"
            category_score = 12.0
            category_match_desc = "✓ Direct Match: SC-targeted scholarship"
        elif is_bc_mbc_targeted:
            category_status = "not_eligible"
            category_score = -14.0
            category_match_desc = "✕ Ineligible: Restricted to BC / MBC / DNC"
        elif is_minority_targeted:
            category_status = "needs_verification"
            category_score = -4.0
            category_match_desc = "⚠ Restricted to Religious Minorities"
        else:
            category_status = "eligible"
            category_score = 3.0
            category_match_desc = "✓ Eligible: Open / Merit-based category"

    elif user_category in ("bc", "mbc", "dnc", "obc"):
        if is_bc_mbc_targeted:
            category_status = "eligible"
            category_score = 10.0
            category_match_desc = f"✓ Direct Match: {user_category.upper()} targeted scholarship"
        elif is_sc_targeted or is_st_targeted:
            category_status = "not_eligible"
            category_score = -14.0
            category_match_desc = "✕ Ineligible: Restricted to SC / ST"
        elif is_minority_targeted:
            category_status = "needs_verification"
            category_score = -4.0
            category_match_desc = "⚠ Restricted to Minorities"
        else:
            category_status = "eligible"
            category_score = 2.0
            category_match_desc = "✓ Eligible: Open / Merit-based category"

    elif user_category == "st":
        if is_st_targeted or is_sc_targeted:
            category_status = "eligible"
            category_score = 12.0
            category_match_desc = "✓ Direct Match: ST / SC targeted scholarship"
        elif is_bc_mbc_targeted:
            category_status = "not_eligible"
            category_score = -14.0
            category_match_desc = "✕ Ineligible: Restricted to BC / MBC / DNC"
        else:
            category_status = "eligible"
            category_score = 3.0
            category_match_desc = "✓ Eligible: Open / Merit-based category"

    elif user_category in ("general", "unknown", ""):
        if is_sc_targeted or is_st_targeted or is_bc_mbc_targeted or is_minority_targeted:
            category_status = "needs_verification"
            category_score = -3.0
            category_match_desc = "⚠ Specific social category required"
        else:
            category_status = "eligible"
            category_score = 2.0
            category_match_desc = "✓ Open to all categories"

    # 2. Income Analysis
    limit = _parse_scholarship_income_limit(text)
    income_status = "eligible"
    income_score = 0.0
    if limit is not None:
        if user_income is not None:
            if user_income <= limit:
                income_status = "eligible"
                income_score = 6.0
                income_match_desc = f"✓ Income within limit: ₹{user_income:,} <= ₹{limit:,}/yr"
            else:
                income_status = "not_eligible"
                income_score = -15.0
                income_match_desc = f"✕ Income exceeds ceiling: ₹{user_income:,} > ₹{limit:,}/yr"
        else:
            income_status = "needs_verification"
            income_score = 0.0
            income_match_desc = f"⚠ Family income ceiling: ₹{limit:,}/yr (Needs verification)"
    else:
        income_status = "eligible"
        income_score = 1.0
        income_match_desc = "✓ No restrictive income limit found"

    # 3. Gender Analysis
    gender_status = "eligible"
    if is_girls_only:
        if user_gender in ("female", "girl", "woman"):
            gender_status = "eligible"
        elif user_gender in ("male", "boy", "man"):
            gender_status = "not_eligible"
        else:
            gender_status = "needs_verification"

    # 4. State Analysis
    state_score = 0.0
    state_status = "eligible"
    is_tn_scheme = any(k in text_lower for k in [
        "tamil nadu", "tamilnadu", "tnea", "adi dravidar and tribal welfare department",
        "naan mudhalvan", "pudhumai penn"
    ])

    # Check if scholarship requires domicile in another state
    other_state_domicile = None
    if user_state not in ("unknown", ""):
        for other_st, aliases in STATE_ALIASES.items():
            if other_st != user_state:
                if any(f"domiciled in {alias}" in text_lower or f"domicile of {alias}" in text_lower or f"government of {alias}" in text_lower for alias in aliases):
                    if not any(c in text_lower for c in ["ministry of", "central sector", "aicte", "ugc", "government of india"]):
                        other_state_domicile = other_st
                        break

    if other_state_domicile:
        state_status = "not_eligible"
        state_score = -14.0
        state_match_desc = f"✕ Ineligible: Requires {other_state_domicile.capitalize()} domicile"
    elif user_state == "tamil nadu":
        if is_tn_scheme:
            state_score = 5.0
            state_match_desc = "✓ Tamil Nadu State resident scheme"
        else:
            state_score = 2.0
            state_match_desc = "✓ Central / All-India scholarship"
    else:
        state_match_desc = "Central / National scholarship"

    # 5. Education Stage Analysis
    stage_score = 0.0
    stage_match_desc = "Education stage compatible"
    is_pre_matric = "pre-matric" in text_lower or "class 9-10" in text_lower or "class 9 to 10" in text_lower
    is_post_matric_or_ug = any(k in text_lower for k in [
        "post-matric", "post matric", "class 11", "ug", "undergraduate",
        "degree", "higher education", "premier institutes", "top class"
    ])

    if "12th" in user_year or "school" in user_stage:
        if is_pre_matric:
            stage_score = -8.0
            stage_match_desc = "⚠ For Class 9-10 (Pre-matric)"
        elif is_post_matric_or_ug:
            stage_score = 5.0
            stage_match_desc = "✓ College entry / Post-Matric scholarship"
    elif "undergraduate" in user_stage or "college" in user_stage:
        if is_pre_matric:
            stage_score = -15.0
            stage_match_desc = "✕ Ineligible (Pre-matric only)"
        elif is_post_matric_or_ug:
            stage_score = 5.0
            stage_match_desc = "✓ Undergraduate degree scholarship"

    # 6. Combined Overall Eligibility
    if category_status == "not_eligible" or income_status == "not_eligible" or gender_status == "not_eligible" or state_status == "not_eligible" or stage_score <= -12.0:
        overall_status = "not_eligible"
    elif category_status == "eligible" and income_status == "eligible" and gender_status == "eligible" and state_status == "eligible" and stage_score >= 0:
        if is_sc_targeted or (limit and user_income and user_income <= limit):
            overall_status = "eligible"
        else:
            overall_status = "potentially_eligible"
    else:
        overall_status = "needs_verification"

    return {
        "status": overall_status,
        "category_status": category_status,
        "category_score": category_score,
        "category_match": category_match_desc,
        "income_status": income_status,
        "income_score": income_score,
        "income_match": income_match_desc,
        "income_limit": limit,
        "stage_score": stage_score,
        "stage_match": stage_match_desc,
        "state_score": state_score,
        "state_match": state_match_desc,
        "is_sc_targeted": is_sc_targeted,
        "is_bc_mbc_targeted": is_bc_mbc_targeted,
    }


def _eligibility_status(text: str, profile: dict) -> str:
    """Wrapper returning the eligibility status string for backward compatibility."""
    return _evaluate_scholarship(text, profile)["status"]


# ============================================================
# COURSE FILTER
# ============================================================

def _filter_courses_by_stream(
    chunks: list[dict],
    stream: str
) -> list[dict]:

    stream = _normalize(stream)

    positive_keywords = STREAM_COURSE_TERMS.get(
        stream,
        []
    )

    if not positive_keywords:
        return chunks

    filtered = []

    for chunk in chunks:

        text = _normalize(
            f"""
            {chunk.get('text', '')}
            {chunk.get('source', '')}
            """
        )

        positive_score = sum(
            1
            for keyword in positive_keywords
            if _keyword_match(
                text,
                keyword
            )
        )

        # TNEA is engineering-specific.
        if (
            stream != "engineering"
            and "tnea" in text
        ):
            continue

        # Remove obvious reference-only college PDFs.
        source = _normalize(
            chunk.get(
                "source",
                ""
            )
        )

        if (
            "information_about_colleges" in source
            and "college name:" not in text
            and "institute name:" not in text
            and "university:" not in text
        ):
            continue

        if positive_score > 0:

            updated = dict(chunk)

            updated["course_stream_match"] = min(
                positive_score,
                6
            )

            filtered.append(
                updated
            )

    return filtered


# ============================================================
# SCHEME FILTER
# ============================================================

def _filter_schemes(
    chunks: list[dict]
) -> list[dict]:

    filtered = []

    for chunk in chunks:

        text = _normalize(
            chunk.get(
                "text",
                ""
            )
        )

        # Must look like an actual scheme record.
        has_scheme_name = (
            "scheme name:" in text
            or "scheme:" in text
        )

        if not has_scheme_name:
            continue

        # Remove admission/information documents.
        excluded_terms = [
            "tnea admission guidelines",
            "admission guidelines",
            "admission prospectus",
            "college admission information",
        ]

        if any(
            term in text
            for term in excluded_terms
        ):
            continue

        filtered.append(
            chunk
        )

    return filtered


# ============================================================
# REMOVE CLEARLY IRRELEVANT CAREER RESULTS
# ============================================================

def _filter_careers_by_profile(
    chunks: list[dict],
    profile: dict
) -> list[dict]:

    stream = _normalize(
        profile.get(
            "stream",
            ""
        )
    )

    domains = _detect_domains(
        profile
    )

    if not stream:
        return chunks

    stream_keywords = STREAM_KEYWORDS.get(
        stream,
        []
    )

    if (
        not stream_keywords
        and not domains
    ):
        return chunks

    filtered = []

    for chunk in chunks:

        text = _normalize(
            chunk.get(
                "text",
                ""
            )
        )

        stream_match = _contains_any(
            text,
            stream_keywords
        )

        domain_match = False

        for domain in domains:

            if _contains_any(
                text,
                DOMAIN_KEYWORDS.get(
                    domain,
                    []
                )
            ):
                domain_match = True
                break

        if (
            stream_match
            or domain_match
        ):
            filtered.append(
                chunk
            )

    if filtered:
        return filtered

    return chunks


# ============================================================
# WEIGHTED RE-RANKING
# ============================================================

def _rerank(
    chunks: list[dict],
    profile: dict,
    category: str
) -> list[dict]:

    stream = profile.get(
        "stream",
        ""
    )

    interests = profile.get(
        "interests",
        []
    )

    state = profile.get(
        "state",
        ""
    )

    domains = _detect_domains(
        profile
    )

    reranked = []

    for chunk in chunks:

        text = chunk.get(
            "text",
            ""
        )

        source = chunk.get(
            "source",
            ""
        )

        semantic_score = float(
            chunk.get(
                "score",
                0
            )
        )

        stream_score = _stream_relevance(
            text,
            stream
        )

        interest_score = _interest_relevance(
            text,
            interests
        )

        domain_score = _domain_relevance(
            text,
            domains
        )

        state_score = _state_relevance(
            text,
            state
        )

        location_penalty = 0
        record_quality = 0
        record_type = None
        temporal_note = None
        temporal_penalty = 0

        # ----------------------------------------------------
        # RECORD QUALITY
        # ----------------------------------------------------

        if category == "career":

            (
                record_quality,
                record_type
            ) = _career_record_quality(
                text,
                source
            )

        elif category == "course":

            (
                record_quality,
                record_type
            ) = _course_record_quality(
                text,
                source
            )

            location_penalty = _location_penalty(
                text,
                state
            )

            (
                temporal_note,
                temporal_penalty
            ) = _temporal_metadata(
                text,
                source
            )

        # ----------------------------------------------------
        # CATEGORY-SPECIFIC WEIGHTS & EXPLAINABILITY
        # ----------------------------------------------------

        scholarship_eval = None
        explanation = []

        if category == "career":

            final_score = (
                semantic_score * 10.0
                + min(stream_score, 4) * 1.5
                + min(interest_score, 6) * 2.0
                + min(domain_score, 6) * 2.0
                + record_quality
            )

            if stream_score > 0:
                explanation.append(f"✓ Matches {stream.capitalize()} stream")
            if interest_score > 0:
                explanation.append("✓ Matches student career interests")
            if domain_score > 0:
                explanation.append("✓ Relevant technical domain")

        elif category == "course":

            final_score = (
                semantic_score * 12.0
                + min(stream_score, 4) * 1.5
                + min(interest_score, 6) * 1.5
                + min(domain_score, 5) * 1.5
                + state_score * 3.5
                + record_quality
                + location_penalty
                + temporal_penalty
            )

            if state_score > 0:
                explanation.append(f"✓ {state.capitalize()} institution / state quota")
            elif location_penalty < 0:
                explanation.append("⚠ Out-of-state institution")
            if stream_score > 0:
                explanation.append(f"✓ Offers {stream.capitalize()} curriculum")
            if temporal_note:
                explanation.append(f"ℹ {temporal_note}")

        elif category == "scholarship":

            scholarship_eval = _evaluate_scholarship(
                text,
                profile
            )

            eligibility_status = scholarship_eval["status"]
            cat_score = scholarship_eval["category_score"]
            inc_score = scholarship_eval["income_score"]
            st_score = scholarship_eval["state_score"]
            stage_score = scholarship_eval["stage_score"]

            final_score = (
                semantic_score * 8.0
                + min(stream_score, 4) * 1.5
                + min(interest_score, 4) * 0.5
                + st_score
                + cat_score
                + inc_score
                + stage_score
            )

            # Heavy penalty if explicitly ineligible (wrong category or income exceeded)
            if eligibility_status == "not_eligible":
                final_score -= 15.0

            explanation.append(scholarship_eval["category_match"])
            explanation.append(scholarship_eval["income_match"])
            if st_score > 0:
                explanation.append(scholarship_eval["state_match"])

        else:  # scheme

            scheme_eval = _evaluate_scholarship(
                text,
                profile
            )

            final_score = (
                semantic_score * 10.0
                + min(stream_score, 4) * 1.5
                + min(interest_score, 4) * 1.0
                + min(domain_score, 5) * 1.5
                + state_score * 3.0
                + (scheme_eval["category_score"] * 0.5)
            )

            if state_score > 0:
                explanation.append(f"✓ {state.capitalize()} government initiative")
            explanation.append(scheme_eval["category_match"])

        updated = dict(
            chunk
        )

        updated["retrieval_score"] = round(
            final_score,
            3
        )

        match_details = {
            "semantic": round(
                semantic_score,
                3
            ),
            "stream": stream_score,
            "interest": interest_score,
            "domain": domain_score,
            "state": state_score,
            "category": round(scholarship_eval["category_score"], 1) if scholarship_eval else 0,
            "income": round(scholarship_eval["income_score"], 1) if scholarship_eval else 0,
            "education_stage": profile.get("education_stage", "unknown"),
            "eligibility": scholarship_eval["status"] if scholarship_eval else "eligible",
            "quality": record_quality,
            "freshness": temporal_note or "current",
        }

        if category in (
            "career",
            "course"
        ):
            match_details["quality"] = record_quality

        if category == "course":
            match_details["location_penalty"] = location_penalty

        updated["match_details"] = match_details
        updated["explanation"] = explanation

        if category == "career":
            updated["record_type"] = record_type
            updated["_record_quality"] = record_quality

        elif category == "course":
            updated["record_type"] = record_type
            updated["_record_quality"] = record_quality
            if temporal_note:
                updated["temporal_note"] = temporal_note

        elif category == "scholarship":
            updated["eligibility_status"] = scholarship_eval["status"]
            updated["scholarship_evaluation"] = scholarship_eval

        reranked.append(
            updated
        )

    reranked.sort(
        key=lambda x: x.get(
            "retrieval_score",
            0
        ),
        reverse=True
    )

    return reranked


# ============================================================
# PERSONALIZED RETRIEVAL
# ============================================================

def retrieve_for_profile(
    profile: dict
) -> dict:

    queries = _build_queries(
        profile
    )

    retrieved = {}

    # ========================================================
    # RETRIEVE EACH CATEGORY
    # ========================================================

    for category, query_text in queries.items():

        # ----------------------------------------------------
        # RETRIEVAL POOL
        # ----------------------------------------------------

        if category == "course":

            fetch_k = max(
                config.RETRIEVAL_TOP_K * 60,
                150
            )

        elif category == "career":

            fetch_k = max(
                config.RETRIEVAL_TOP_K * 8,
                30
            )

        elif category == "scholarship":

            fetch_k = max(
                config.RETRIEVAL_TOP_K * 8,
                30
            )

        else:

            fetch_k = max(
                config.RETRIEVAL_TOP_K * 8,
                30
            )

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        chunks = search(
            query_text,
            category=category,
            top_k=fetch_k
        )

        # ----------------------------------------------------
        # CATEGORY FILTERING
        # ----------------------------------------------------

        if category == "career":

            chunks = _filter_careers_by_profile(
                chunks,
                profile
            )

        elif category == "course":

            chunks = _filter_courses_by_stream(
                chunks,
                profile.get(
                    "stream",
                    ""
                )
            )

        elif category == "scheme":

            chunks = _filter_schemes(
                chunks
            )

        # ----------------------------------------------------
        # WEIGHTED RE-RANKING
        # ----------------------------------------------------

        chunks = _rerank(
            chunks,
            profile,
            category
        )

        # ----------------------------------------------------
        # DEDUPLICATION
        # ----------------------------------------------------

        if category == "career":

            chunks = _dedupe_by_career(
                chunks
            )

        elif category == "course":

            chunks = _dedupe_by_institute(
                chunks
            )

        elif category == "scholarship":

            chunks = _dedupe_by_scholarship(
                chunks
            )

        elif category == "scheme":

            chunks = _dedupe_by_scheme(
                chunks
            )

        # ----------------------------------------------------
        # FINAL TOP-K
        # ----------------------------------------------------

        chunks = chunks[
            :config.RETRIEVAL_TOP_K
        ]

        retrieved[category] = chunks

    return retrieved


# ============================================================
# DEBUG DISPLAY
# ============================================================

def print_retrieval_results(
    results: dict
):

    print(
        "\n============================================================"
    )

    print(
        "PERSONALIZED RETRIEVAL RESULTS"
    )

    print(
        "============================================================"
    )

    for category, chunks in results.items():

        print(
            f"\n--- {category.upper()} "
            f"({len(chunks)} results) ---"
        )

        for index, chunk in enumerate(
            chunks,
            start=1
        ):

            print(
                f"\n{index}. "
                f"{chunk.get('source', '')}"
            )

            print(
                f"   Semantic Score : "
                f"{chunk.get('score', 0)}"
            )

            print(
                f"   Retrieval Score: "
                f"{chunk.get('retrieval_score', 0)}"
            )

            print(
                f"   Match Details  : "
                f"{chunk.get('match_details', {})}"
            )

            if chunk.get(
                "record_type"
            ):
                print(
                    f"   Record Type    : "
                    f"{chunk.get('record_type')}"
                )

            if chunk.get(
                "eligibility_status"
            ):
                print(
                    f"   Eligibility    : "
                    f"{chunk.get('eligibility_status')}"
                )

            if chunk.get(
                "temporal_note"
            ):
                print(
                    f"   Data Status    : "
                    f"{chunk.get('temporal_note')}"
                )

            print(
                f"   Text           : "
                f"{chunk.get('text', '')[:250]}..."
            )


# ============================================================
# MANUAL TEST
# ============================================================

if __name__ == "__main__":

    sample_profile = {

        "stream": "engineering",

        "education_stage": "school",

        "current_year": "12th standard",

        "state": "Tamil Nadu",

        "category": "unknown",

        "board_percentage": 88,

        "interests": [
            "computer science",
            "robotics"
        ],

        "constraints": (
            "financial constraints "
            "(family cannot afford expensive "
            "private colleges)"
        ),

        "goal": (
            "scholarship options and "
            "career advice"
        ),
    }

    print(
        "\n============================================================"
    )

    print(
        "PROFILE CONTEXT"
    )

    print(
        "============================================================"
    )

    print(
        _build_profile_context(
            sample_profile
        )
    )

    print(
        "\nDetected Domains:"
    )

    print(
        _detect_domains(
            sample_profile
        )
    )

    print(
        "\nGenerating personalized retrieval..."
    )

    results = retrieve_for_profile(
        sample_profile
    )

    print_retrieval_results(
        results
    )
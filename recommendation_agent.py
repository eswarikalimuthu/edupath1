
"""
EduPath AI - Recommendation Agent

Responsibilities:
1. Analyze the student's structured profile.
2. Use retrieved RAG context.
3. Generate personalized career recommendations.
4. Recommend suitable institutions, courses, scholarships and schemes.
5. Generate stream/domain-specific practice platforms.
6. Generate a personalized practice plan.
7. Provide actionable next steps.
8. Fall back to Ollama / rule-based recommendations when Gemini is unavailable.

LLM priority:
    Gemini -> Ollama -> Rule-based fallback
"""

import re
import time
import requests

from google import genai

from src import config


# ============================================================
# STREAM / CAREER DOMAIN -> PRACTICE PLATFORM ENGINE
# ============================================================

PRACTICE_PLATFORM_ENGINE = {

    "engineering": [
        {
            "platform": "HackerRank",
            "focus": "Python, C/C++, DSA, problem solving",
            "practice": "Solve beginner and intermediate programming problems regularly."
        },
        {
            "platform": "LeetCode",
            "focus": "Data Structures & Algorithms",
            "practice": "Start with arrays, strings, hashing, recursion, sorting and searching."
        },
        {
            "platform": "CodeChef",
            "focus": "Competitive programming",
            "practice": "Participate in coding contests and solve implementation problems."
        },
        {
            "platform": "GitHub",
            "focus": "Projects and portfolio",
            "practice": "Upload mini-projects and maintain a technical portfolio."
        }
    ],

    "computer science": [
        {
            "platform": "LeetCode",
            "focus": "DSA and coding interviews",
            "practice": "Solve 2-3 problems daily and gradually increase difficulty."
        },
        {
            "platform": "HackerRank",
            "focus": "Python, SQL and algorithms",
            "practice": "Complete skill certifications and topic-based challenges."
        },
        {
            "platform": "CodeChef",
            "focus": "Competitive programming",
            "practice": "Practice timed coding problems and contests."
        },
        {
            "platform": "GitHub",
            "focus": "Software projects",
            "practice": "Build and publish real-world applications."
        }
    ],

    "ai": [
        {
            "platform": "Kaggle",
            "focus": "Machine Learning and datasets",
            "practice": "Complete notebooks and beginner ML competitions."
        },
        {
            "platform": "Google Colab",
            "focus": "Python and ML experimentation",
            "practice": "Train small ML models without requiring a powerful local computer."
        },
        {
            "platform": "LeetCode",
            "focus": "Python and DSA",
            "practice": "Practice algorithms required for technical interviews."
        },
        {
            "platform": "HackerRank",
            "focus": "Python, SQL and problem solving",
            "practice": "Complete Python and SQL skill tracks."
        },
        {
            "platform": "GitHub",
            "focus": "AI portfolio",
            "practice": "Publish ML projects, notebooks and APIs."
        }
    ],

    "data": [
        {
            "platform": "Kaggle",
            "focus": "Datasets, EDA and Machine Learning",
            "practice": "Work with real datasets and publish notebooks."
        },
        {
            "platform": "HackerRank",
            "focus": "SQL and Python",
            "practice": "Solve SQL queries and Python programming challenges."
        },
        {
            "platform": "LeetCode",
            "focus": "SQL and DSA",
            "practice": "Practice SQL interview questions and algorithmic problems."
        },
        {
            "platform": "Google Colab",
            "focus": "Data analysis",
            "practice": "Practice Pandas, NumPy, Matplotlib and ML experiments."
        }
    ],

    "robotics": [
        {
            "platform": "Tinkercad Circuits",
            "focus": "Arduino and electronics simulation",
            "practice": "Build virtual circuits using sensors, LEDs and Arduino."
        },
        {
            "platform": "Arduino",
            "focus": "Embedded programming",
            "practice": "Practice sensor and actuator programming."
        },
        {
            "platform": "ROS",
            "focus": "Robot Operating System",
            "practice": "Learn robot simulation, nodes, topics and basic robotics programming."
        },
        {
            "platform": "LeetCode",
            "focus": "Programming and algorithms",
            "practice": "Strengthen Python/C++ and algorithmic problem solving."
        },
        {
            "platform": "GitHub",
            "focus": "Robotics portfolio",
            "practice": "Document robotics projects and simulation work."
        }
    ],

    "cybersecurity": [
        {
            "platform": "TryHackMe",
            "focus": "Cybersecurity fundamentals",
            "practice": "Follow beginner security learning paths and labs."
        },
        {
            "platform": "PortSwigger Web Security Academy",
            "focus": "Web security",
            "practice": "Practice web-security concepts through guided labs."
        },
        {
            "platform": "Hack The Box",
            "focus": "Security labs",
            "practice": "Progress through legal penetration-testing challenges."
        },
        {
            "platform": "HackerRank",
            "focus": "Python, SQL and programming",
            "practice": "Strengthen programming foundations required for security."
        },
        {
            "platform": "GitHub",
            "focus": "Security projects",
            "practice": "Build defensive security tools and document them."
        }
    ],

    "commerce": [
        {
            "platform": "HackerRank",
            "focus": "SQL and problem solving",
            "practice": "Practice SQL queries and data-analysis problems."
        },
        {
            "platform": "Kaggle",
            "focus": "Finance and business datasets",
            "practice": "Analyze financial and business datasets."
        },
        {
            "platform": "Microsoft Learn",
            "focus": "Excel and Power BI",
            "practice": "Learn spreadsheets, dashboards and business analytics."
        },
        {
            "platform": "Coursera",
            "focus": "Accounting, finance and business",
            "practice": "Follow beginner-friendly business and finance courses."
        }
    ],

    "finance": [
        {
            "platform": "Kaggle",
            "focus": "Financial data analysis",
            "practice": "Analyze stock, economic and financial datasets."
        },
        {
            "platform": "HackerRank",
            "focus": "SQL",
            "practice": "Solve SQL problems useful for financial analytics."
        },
        {
            "platform": "Microsoft Learn",
            "focus": "Excel and Power BI",
            "practice": "Build financial dashboards and reports."
        },
        {
            "platform": "Investopedia",
            "focus": "Financial concepts",
            "practice": "Learn terminology, markets, accounting and investment concepts."
        }
    ],

    "medical": [
        {
            "platform": "Khan Academy",
            "focus": "Biology, chemistry and medicine",
            "practice": "Strengthen foundational science concepts."
        },
        {
            "platform": "MedlinePlus",
            "focus": "Medical knowledge",
            "practice": "Read reliable health and medical reference material."
        },
        {
            "platform": "Quizlet",
            "focus": "Revision and flashcards",
            "practice": "Create flashcards for anatomy, terminology and science."
        },
        {
            "platform": "Coursera",
            "focus": "Healthcare and biomedical learning",
            "practice": "Explore introductory healthcare courses."
        }
    ],

    "science": [
        {
            "platform": "Khan Academy",
            "focus": "Physics, chemistry, mathematics and biology",
            "practice": "Strengthen fundamental scientific concepts."
        },
        {
            "platform": "PhET Interactive Simulations",
            "focus": "Physics, chemistry and mathematics",
            "practice": "Use interactive simulations to understand scientific concepts."
        },
        {
            "platform": "NPTEL",
            "focus": "University-level science",
            "practice": "Follow structured courses from Indian institutions."
        },
        {
            "platform": "Kaggle",
            "focus": "Statistics and data science",
            "practice": "Analyze scientific datasets and build notebooks."
        }
    ],

    "law": [
        {
            "platform": "Indian Kanoon",
            "focus": "Case law and judgments",
            "practice": "Read judgments and practice identifying legal principles."
        },
        {
            "platform": "SCC Online",
            "focus": "Legal research",
            "practice": "Practice structured case-law and legal research."
        },
        {
            "platform": "Manupatra",
            "focus": "Legal databases",
            "practice": "Explore legal research and case references."
        },
        {
            "platform": "India Code",
            "focus": "Indian legislation",
            "practice": "Read Acts, rules and statutory provisions."
        }
    ],

    "arts": [
        {
            "platform": "Coursera",
            "focus": "Psychology, communication, history and arts",
            "practice": "Take introductory courses related to your chosen discipline."
        },
        {
            "platform": "edX",
            "focus": "Humanities and social sciences",
            "practice": "Explore university-level humanities courses."
        },
        {
            "platform": "Medium",
            "focus": "Writing and communication",
            "practice": "Write articles and publish structured essays."
        },
        {
            "platform": "Google Arts & Culture",
            "focus": "Art and cultural studies",
            "practice": "Explore museums, artworks and cultural resources."
        }
    ],

    "humanities": [
        {
            "platform": "Coursera",
            "focus": "Psychology, sociology, history and political science",
            "practice": "Complete introductory courses in your chosen discipline."
        },
        {
            "platform": "edX",
            "focus": "Humanities and social sciences",
            "practice": "Study university-level courses."
        },
        {
            "platform": "Medium",
            "focus": "Writing and analysis",
            "practice": "Publish essays, opinion pieces and research summaries."
        },
        {
            "platform": "Google Scholar",
            "focus": "Academic research",
            "practice": "Read research papers and practice literature review."
        }
    ],

    "design": [
        {
            "platform": "Figma",
            "focus": "UI/UX design",
            "practice": "Create mobile and web interface prototypes."
        },
        {
            "platform": "Canva",
            "focus": "Graphic design",
            "practice": "Practice posters, presentations and social media designs."
        },
        {
            "platform": "Behance",
            "focus": "Portfolio development",
            "practice": "Study professional portfolios and publish your own work."
        },
        {
            "platform": "Dribbble",
            "focus": "UI/visual design inspiration",
            "practice": "Study design patterns and recreate interfaces for practice."
        }
    ],

    "architecture": [
        {
            "platform": "AutoCAD",
            "focus": "Technical drawing",
            "practice": "Practice 2D architectural drawings."
        },
        {
            "platform": "SketchUp",
            "focus": "3D modelling",
            "practice": "Create basic architectural models."
        },
        {
            "platform": "Revit",
            "focus": "BIM",
            "practice": "Practice building information modelling."
        },
        {
            "platform": "ArchDaily",
            "focus": "Architecture knowledge",
            "practice": "Study architectural projects and design approaches."
        }
    ],

    "agriculture": [
        {
            "platform": "ICAR resources",
            "focus": "Agricultural science",
            "practice": "Study crop science, soil science and agricultural technology."
        },
        {
            "platform": "FAO resources",
            "focus": "Agriculture and food systems",
            "practice": "Explore agriculture, sustainability and food-security topics."
        },
        {
            "platform": "Kaggle",
            "focus": "Agricultural data",
            "practice": "Analyze crop, climate and agricultural datasets."
        },
        {
            "platform": "QGIS",
            "focus": "GIS and spatial analysis",
            "practice": "Learn basic mapping and agricultural spatial analysis."
        }
    ],

    "media": [
        {
            "platform": "Medium",
            "focus": "Writing and publishing",
            "practice": "Publish articles, stories and opinion pieces."
        },
        {
            "platform": "Canva",
            "focus": "Visual content",
            "practice": "Create posters, social-media content and presentations."
        },
        {
            "platform": "Google Trends",
            "focus": "Trend research",
            "practice": "Analyze current search trends and identify story ideas."
        },
        {
            "platform": "Adobe tools",
            "focus": "Video, photo and graphic editing",
            "practice": "Practice basic editing and content production."
        }
    ],

    "education": [
        {
            "platform": "Khan Academy",
            "focus": "Teaching resources",
            "practice": "Study instructional methods and subject content."
        },
        {
            "platform": "NPTEL",
            "focus": "Academic learning",
            "practice": "Follow structured courses and teaching-related subjects."
        },
        {
            "platform": "Google Classroom",
            "focus": "Digital education",
            "practice": "Learn digital classroom and assignment workflows."
        },
        {
            "platform": "Coursera",
            "focus": "Education and pedagogy",
            "practice": "Explore teaching and learning courses."
        }
    ],

    "government": [
        {
            "platform": "PIB",
            "focus": "Government policies and current affairs",
            "practice": "Read government announcements and policy updates."
        },
        {
            "platform": "PRS Legislative Research",
            "focus": "Polity and legislation",
            "practice": "Read summaries of bills, laws and parliamentary developments."
        },
        {
            "platform": "India Code",
            "focus": "Indian laws",
            "practice": "Read important Acts and statutory provisions."
        },
        {
            "platform": "UPSC resources",
            "focus": "Civil service preparation",
            "practice": "Practice previous-year questions and mock tests."
        }
    ],

    "research": [
        {
            "platform": "Google Scholar",
            "focus": "Research papers",
            "practice": "Search, read and summarize research papers."
        },
        {
            "platform": "Kaggle",
            "focus": "Data-driven research",
            "practice": "Work with datasets and publish analytical notebooks."
        },
        {
            "platform": "GitHub",
            "focus": "Research code",
            "practice": "Maintain reproducible research projects."
        },
        {
            "platform": "NPTEL",
            "focus": "Advanced academic learning",
            "practice": "Complete advanced university-level courses."
        }
    ],

    "hospitality": [
        {
            "platform": "Coursera",
            "focus": "Hospitality and tourism",
            "practice": "Study hotel management and customer-service concepts."
        },
        {
            "platform": "edX",
            "focus": "Business and hospitality",
            "practice": "Explore hospitality management courses."
        },
        {
            "platform": "LinkedIn Learning",
            "focus": "Professional skills",
            "practice": "Develop communication and management skills."
        }
    ],

    "tourism": [
        {
            "platform": "Google Travel",
            "focus": "Travel planning",
            "practice": "Study destinations, travel routes and tourism information."
        },
        {
            "platform": "Coursera",
            "focus": "Tourism management",
            "practice": "Learn tourism and hospitality fundamentals."
        },
        {
            "platform": "Canva",
            "focus": "Travel content",
            "practice": "Create travel guides and promotional content."
        }
    ],

    "fashion": [
        {
            "platform": "Canva",
            "focus": "Fashion presentations and branding",
            "practice": "Create mood boards and fashion presentations."
        },
        {
            "platform": "Behance",
            "focus": "Fashion portfolio",
            "practice": "Build and publish a visual portfolio."
        },
        {
            "platform": "Figma",
            "focus": "Digital fashion concepts",
            "practice": "Create digital layouts and product concepts."
        }
    ],

    "psychology": [
        {
            "platform": "Coursera",
            "focus": "Psychology fundamentals",
            "practice": "Study introductory psychology courses."
        },
        {
            "platform": "Google Scholar",
            "focus": "Psychology research",
            "practice": "Read and summarize peer-reviewed research."
        },
        {
            "platform": "Quizlet",
            "focus": "Psychology terminology",
            "practice": "Create flashcards for theories and terminology."
        }
    ],

    "biotechnology": [
        {
            "platform": "Khan Academy",
            "focus": "Biology and chemistry",
            "practice": "Strengthen molecular biology and chemistry fundamentals."
        },
        {
            "platform": "NPTEL",
            "focus": "Biotechnology",
            "practice": "Complete university-level biotechnology courses."
        },
        {
            "platform": "Google Scholar",
            "focus": "Biotechnology research",
            "practice": "Read current research papers."
        },
        {
            "platform": "Kaggle",
            "focus": "Biological datasets",
            "practice": "Explore bioinformatics and biological data."
        }
    ],

    "environment": [
        {
            "platform": "Kaggle",
            "focus": "Environmental datasets",
            "practice": "Analyze climate and environmental datasets."
        },
        {
            "platform": "QGIS",
            "focus": "Geospatial analysis",
            "practice": "Create environmental maps and spatial analyses."
        },
        {
            "platform": "NASA Earthdata",
            "focus": "Earth observation",
            "practice": "Explore environmental and satellite datasets."
        }
    ],

    "food": [
        {
            "platform": "Khan Academy",
            "focus": "Chemistry and biology",
            "practice": "Strengthen science fundamentals relevant to food technology."
        },
        {
            "platform": "NPTEL",
            "focus": "Food technology",
            "practice": "Study food processing and technology courses."
        },
        {
            "platform": "Kaggle",
            "focus": "Food and nutrition data",
            "practice": "Analyze food, nutrition and consumer datasets."
        }
    ],

    "aviation": [
        {
            "platform": "Khan Academy",
            "focus": "Physics and mathematics",
            "practice": "Strengthen mechanics, vectors and mathematics."
        },
        {
            "platform": "FlightGear",
            "focus": "Flight simulation",
            "practice": "Explore basic flight simulation."
        },
        {
            "platform": "Coursera",
            "focus": "Aviation and aerospace",
            "practice": "Explore introductory aviation courses."
        }
    ],

    "maritime": [
        {
            "platform": "Khan Academy",
            "focus": "Physics and mathematics",
            "practice": "Strengthen mechanics and mathematical fundamentals."
        },
        {
            "platform": "NPTEL",
            "focus": "Marine engineering",
            "practice": "Study engineering and maritime-related courses."
        },
        {
            "platform": "Coursera",
            "focus": "Marine and logistics",
            "practice": "Explore maritime and supply-chain fundamentals."
        }
    ],

    "social services": [
        {
            "platform": "Coursera",
            "focus": "Social work and development",
            "practice": "Study social-service and community-development courses."
        },
        {
            "platform": "edX",
            "focus": "Social sciences",
            "practice": "Explore development and social-policy courses."
        },
        {
            "platform": "Google Scholar",
            "focus": "Social research",
            "practice": "Read and summarize social-science research."
        }
    ],

    "fintech": [
        {
            "platform": "HackerRank",
            "focus": "SQL and programming",
            "practice": "Practice SQL, Python and data problems."
        },
        {
            "platform": "LeetCode",
            "focus": "DSA",
            "practice": "Practice technical interview problems."
        },
        {
            "platform": "Kaggle",
            "focus": "Financial data",
            "practice": "Analyze financial datasets."
        },
        {
            "platform": "GitHub",
            "focus": "FinTech projects",
            "practice": "Build payment, banking or financial analytics projects."
        }
    ]
}


# ============================================================
# DEFAULT PRACTICE PLATFORMS
# ============================================================

DEFAULT_PRACTICE_PLATFORMS = [
    {
        "platform": "HackerRank",
        "focus": "Programming and problem solving",
        "practice": "Solve beginner-friendly programming challenges."
    },
    {
        "platform": "Coursera",
        "focus": "Structured learning",
        "practice": "Follow courses related to your chosen career."
    },
    {
        "platform": "GitHub",
        "focus": "Portfolio building",
        "practice": "Create projects and document your learning."
    }
]


# ============================================================
# GEMINI PROMPT
# ============================================================

RECOMMENDATION_PROMPT = """
You are the Recommendation Agent of EduPath AI,
an AI-powered personalized career and education advisor.

Your job is to analyze the student's profile and retrieved
knowledge-base information and produce a personalized,
evidence-grounded recommendation.

IMPORTANT:
- STRICT DOMAIN ALIGNMENT: You MUST recommend careers that strictly match the student's stated stream and interests (e.g. for Commerce/Finance: Chartered Accountant, Financial Analyst, Banker; for Medical/Medicine: Doctor, Medical Specialist, Clinical Pharmacist; for Law: Advocate, Legal Advisor, Corporate Lawyer; for Arts/Humanities: Civil Services, Policy Analyst, Journalist; for Engineering/Tech: specific engineering roles aligned with their focus). NEVER recommend generic software coding or IT jobs to a non-technical student unless explicitly requested.
- Do NOT invent colleges, scholarships, schemes or eligibility.
- Use ONLY information available in the retrieved context.
- Clearly mention when information is historical or needs verification.
- Never present historical cutoff information as current.
- Do not claim a scholarship is guaranteed.
- Do not recommend another undergraduate degree to a student
  who is already an undergraduate.
- Recommendations must match the student's education stage.
- Practice platforms MUST match the student's stream/career/domain as listed in AVAILABLE PRACTICE PLATFORM ENGINE.
- Practice platforms are learning recommendations, not eligibility claims.

STUDENT PROFILE:
{profile}

RETRIEVED KNOWLEDGE:
{context}

AVAILABLE PRACTICE PLATFORM ENGINE:
{practice_platforms}

Return the answer using this structure:

### 1. SUGGESTED CAREER PATHWAYS

For each career:
- Career
- Why it matches
- Education
- Skills
- Source

### 2. RECOMMENDED INSTITUTIONS & COURSES

For each institution:
- Institution
- Course
- Why suitable
- Source

### 3. ELIGIBLE SCHOLARSHIPS

For each scholarship:
- Scholarship
- Eligibility
- Benefit
- Source

Clearly mention if eligibility depends on missing information.

### 4. GOVERNMENT SCHEMES

For each scheme:
- Scheme
- Eligibility
- Benefit
- Source

### 5. PRACTICE & SKILL DEVELOPMENT

Recommend 3-5 relevant platforms from the supplied practice
platform engine.

For every platform provide:
- Platform
- Focus
- How to practice
- Why it is useful for the recommended career

Do NOT randomly add unrelated platforms.

### 6. PERSONALIZED 30-DAY PRACTICE PLAN

Create a realistic 30-day plan.

Week 1:
Foundation

Week 2:
Core skill development

Week 3:
Applied practice

Week 4:
Projects / portfolio / assessment

Include the recommended practice platforms.

### 7. NEXT STEPS

Give 4-6 concrete actions.

### 8. IMPORTANT NOTE

Mention:
- Historical data
- Missing profile information
- Scholarship eligibility verification
- Current admission verification

Use clear, student-friendly language.
"""


# ============================================================
# FORMAT RETRIEVED CONTEXT
# ============================================================

def _format_context(context):
    """Convert retrieval results into readable prompt text."""

    if not context:
        return "No retrieval context available."

    sections = []

    for category in ["career", "course", "scholarship", "scheme"]:

        items = context.get(category, [])

        if not items:
            continue

        lines = [f"--- {category.upper()} ---"]

        for item in items:
            if isinstance(item, dict):
                text = item.get("text", "")
                source = item.get("source", "")

                score = item.get("score")

                if score is not None:
                    lines.append(
                        f"[score={score:.3f}] "
                        f"{text} "
                        f"(source: {source})"
                    )
                else:
                    lines.append(
                        f"{text} "
                        f"(source: {source})"
                    )
            else:
                lines.append(str(item))

        sections.append("\n".join(lines))

    return "\n\n".join(sections)


# ============================================================
# PROFILE HELPERS
# ============================================================

def _normalize(value):
    """Normalize text for matching."""

    if value is None:
        return ""

    return str(value).strip().lower()


def _detect_practice_domains(profile, careers=None):
    """
    Detect all relevant practice domains.

    This allows one student to receive multiple domain-specific
    practice platforms.

    Example:
        Engineering + Robotics + AI
        -> engineering
        -> robotics
        -> ai
    """

    domains = []

    stream = _normalize(profile.get("stream"))
    interests = " ".join(
        _normalize(x)
        for x in profile.get("interests", [])
    )

    goal = _normalize(profile.get("goal"))

    career_text = ""

    if careers:
        career_text = " ".join(
            _normalize(x)
            for x in careers
        )

    combined = " ".join(
        [stream, interests, goal, career_text]
    )

    # Direct stream mapping
    stream_map = {
        "engineering": "engineering",
        "computer science": "computer science",
        "cs": "computer science",
        "cse": "computer science",
        "computer": "computer science",
        "commerce": "commerce",
        "finance": "finance",
        "medical": "medical",
        "medicine": "medical",
        "science": "science",
        "law": "law",
        "arts": "arts",
        "humanities": "humanities",
        "design": "design",
        "architecture": "architecture",
    }

    if stream in stream_map:
        domains.append(stream_map[stream])

    # Keyword-based domain detection
    keyword_map = {
        "ai": [
            "artificial intelligence",
            "ai",
            "machine learning",
            "ml",
            "deep learning",
        ],

        "data": [
            "data science",
            "data scientist",
            "data analyst",
            "analytics",
            "statistics",
        ],

        "robotics": [
            "robotics",
            "robot",
            "automation",
            "embedded",
        ],

        "cybersecurity": [
            "cybersecurity",
            "cyber security",
            "ethical hacking",
            "penetration testing",
            "information security",
        ],

        "finance": [
            "finance",
            "financial analyst",
            "investment",
            "banking",
            "accounting",
            "chartered accountant",
            "ca",
            "fintech",
        ],

        "medical": [
            "doctor",
            "dentist",
            "pharmacist",
            "physiotherapist",
            "medical",
            "healthcare",
            "medicine",
        ],

        "law": [
            "lawyer",
            "advocate",
            "legal",
            "law",
            "judge",
        ],

        "design": [
            "designer",
            "design",
            "ui",
            "ux",
            "graphic design",
        ],

        "architecture": [
            "architect",
            "architecture",
            "urban planner",
            "interior designer",
        ],

        "agriculture": [
            "agriculture",
            "agricultural",
            "agronomy",
            "horticulture",
            "fisheries",
            "dairy",
        ],

        "media": [
            "journalist",
            "journalism",
            "media",
            "content writer",
            "public relations",
            "pr specialist",
        ],

        "education": [
            "teacher",
            "teaching",
            "education",
            "professor",
            "lecturer",
        ],

        "government": [
            "civil services",
            "civil service",
            "ias",
            "ips",
            "government officer",
            "public administration",
            "police",
            "defence",
        ],

        "research": [
            "research scientist",
            "researcher",
            "research",
            "scientist",
        ],

        "psychology": [
            "psychology",
            "psychologist",
        ],

        "biotechnology": [
            "biotechnology",
            "biotech",
            "microbiology",
            "biologist",
        ],

        "environment": [
            "environment",
            "environmental scientist",
            "climate",
            "sustainability",
        ],

        "food": [
            "food technology",
            "food technologist",
            "food safety",
            "food science",
        ],

        "aviation": [
            "aviation",
            "pilot",
            "aerospace",
            "aircraft",
        ],

        "maritime": [
            "maritime",
            "marine engineering",
            "merchant navy",
            "shipping",
        ],

        "tourism": [
            "tourism",
            "travel",
            "tourism management",
        ],

        "hospitality": [
            "hospitality",
            "hotel management",
            "hotel",
        ],

        "fashion": [
            "fashion",
            "fashion designer",
        ],

        "fintech": [
            "fintech",
            "financial technology",
            "payment technology",
        ],

        "social services": [
            "social worker",
            "social services",
            "community development",
        ],
    }

    for domain, keywords in keyword_map.items():

        if any(keyword in combined for keyword in keywords):
            if domain not in domains:
                domains.append(domain)

    return domains


# ============================================================
# PRACTICE PLATFORM BUILDER
# ============================================================

def build_practice_platforms(profile, careers=None):
    """
    Build a personalized list of practice platforms.

    Platforms are selected from the local engine instead of
    being hallucinated by the LLM.
    """

    domains = _detect_practice_domains(
        profile,
        careers
    )

    platforms = []

    for domain in domains:

        for platform in PRACTICE_PLATFORM_ENGINE.get(
            domain,
            []
        ):

            platform_name = platform["platform"].lower()

            already_exists = any(
                x["platform"].lower() == platform_name
                for x in platforms
            )

            if not already_exists:
                enriched = dict(platform)
                enriched["domain"] = domain
                platforms.append(enriched)

    # Fallback
    if not platforms:
        for platform in DEFAULT_PRACTICE_PLATFORMS:
            enriched = dict(platform)
            enriched["domain"] = "general"
            platforms.append(enriched)

    # Maximum 8 platforms to avoid overwhelming the student
    return platforms[:8]


def format_practice_platforms(platforms):
    """Format platform engine data for the LLM."""

    if not platforms:
        return "No platform data available."

    lines = []

    for item in platforms:
        lines.append(
            f"- {item['platform']} | "
            f"Domain: {item['domain']} | "
            f"Focus: {item['focus']} | "
            f"Practice: {item['practice']}"
        )

    return "\n".join(lines)


# ============================================================
# TEMPORARY GEMINI ERROR DETECTION
# ============================================================

def _is_temporary_error(error):
    """Detect errors where retrying makes sense."""

    text = str(error).lower()

    temporary_patterns = [
        "503",
        "unavailable",
        "high demand",
        "429",
        "rate limit",
        "resource exhausted",
        "timeout",
        "deadline exceeded",
        "temporarily",
    ]

    return any(
        pattern in text
        for pattern in temporary_patterns
    )


# ============================================================
# EXTRACT CAREERS
# ============================================================

def _extract_career_options(context):
    """Extract clean career names from retrieved career records."""

    careers = []

    for item in context.get("career", []):

        text = item.get("text", "") if isinstance(item, dict) else str(item)

        # Match career:, Title:, occupation:, job role:, or job title:
        match = re.search(
            r"(?:career|title|occupation|job\s*title|job\s*role)\s*:\s*([^,\.\n]+)",
            text,
            re.IGNORECASE,
        )

        if match:
            career = match.group(1).strip()
            # Strip any residual database prefixes like JobID: 101 or Level:
            career = re.sub(r"^(?:jobid|id|code|level)\s*:\s*\S+\s*", "", career, flags=re.IGNORECASE).strip()
        else:
            clean_first = text.split(".")[0].strip()
            career = re.sub(r"^[A-Za-z0-9_\-]+\s*:\s*", "", clean_first).strip()

        if career and len(career) >= 3 and career.lower() not in {
            c.lower() for c in careers
        }:
            careers.append(career)

    return careers[:6]


# ============================================================
# EXTRACT INSTITUTIONS
# ============================================================

def _extract_institutions(context):
    """Extract institution names."""

    institutions = []

    for item in context.get("course", []):

        text = item.get("text", "") if isinstance(item, dict) else str(item)

        match = re.search(
            r"(?:Institute Name|institute_name|Institute)\s*:\s*([^,\n]+)",
            text,
            re.IGNORECASE,
        )

        if match:
            name = match.group(1).strip()

            if name.lower() not in {
                x.lower() for x in institutions
            }:
                institutions.append(name)

    return institutions[:6]


# ============================================================
# EXTRACT SCHOLARSHIPS
# ============================================================

def _extract_scholarships(context):
    """Extract scholarship snippets."""

    scholarships = []

    for item in context.get("scholarship", []):

        text = item.get("text", "") if isinstance(item, dict) else str(item)

        match = re.search(
            r"(?:Scholarship Name|Scholarship)\s*:\s*([^,\n]+)",
            text,
            re.IGNORECASE,
        )

        if match:
            scholarship = match.group(1).strip()
        else:
            scholarship = text[:220].strip()

        if scholarship:
            scholarships.append(scholarship)

    return scholarships[:6]


# ============================================================
# EXTRACT SCHEMES
# ============================================================

def _extract_schemes(context):
    """Extract government scheme snippets."""

    schemes = []

    for item in context.get("scheme", []):

        text = item.get("text", "") if isinstance(item, dict) else str(item)

        match = re.search(
            r"Scheme Name\s*:\s*([^,\n]+)",
            text,
            re.IGNORECASE,
        )

        if match:
            scheme = match.group(1).strip()
        else:
            scheme = text[:220].strip()

        if scheme:
            schemes.append(scheme)

    return schemes[:6]


# ============================================================
# RULE-BASED FALLBACK
# ============================================================

def _rule_based_recommendation(
    profile,
    context,
    practice_platforms
):
    """
    Safe fallback when both Gemini and Ollama are unavailable.
    """

    careers = _extract_career_options(context)

    institutions = _extract_institutions(context)

    scholarships = _extract_scholarships(context)

    schemes = _extract_schemes(context)

    stage = _normalize(
        profile.get("education_stage")
    )

    if stage in {
        "undergraduate",
        "ug",
        "college",
        "graduate",
    }:

        next_steps = [
            "Continue your current undergraduate program and build skills aligned with your target career.",
            "Practice consistently using the recommended platforms.",
            "Build at least one portfolio project related to your career goal.",
            "Apply for relevant scholarships, internships and skill-development opportunities.",
        ]

    elif stage in {
        "school",
        "12th standard",
        "higher secondary",
    }:

        next_steps = [
            "Complete your current school studies with strong academic performance.",
            "Research suitable entrance examinations and admission pathways.",
            "Check scholarship and government-scheme eligibility.",
            "Start foundational practice using the recommended learning platforms.",
        ]

    else:

        next_steps = [
            "Identify the strongest career pathway from the recommended options.",
            "Build the core skills required for that career.",
            "Practice regularly using the recommended platforms.",
            "Build a small portfolio project.",
        ]

    output = []

    # --------------------------------------------------------
    # CAREERS
    # --------------------------------------------------------

    output.append("### 1. SUGGESTED CAREER PATHWAYS\n")

    if careers:

        for career in careers[:4]:
            output.append(
                f"**Career:** {career}\n"
                f"* **Why it matches:** This career was retrieved "
                f"from the knowledge base and should be evaluated "
                f"against your interests and goals.\n"
                f"* **Source:** Career knowledge base\n"
            )

    else:
        output.append(
            "No sufficiently relevant career records were retrieved."
        )

    # --------------------------------------------------------
    # INSTITUTIONS
    # --------------------------------------------------------

    output.append("\n---\n### 2. RECOMMENDED INSTITUTIONS & COURSES\n")

    if institutions:

        for institution in institutions[:4]:

            output.append(
                f"**Institution:** {institution}\n"
                f"* **Why suitable:** Retrieved as a potentially "
                f"relevant institution/course option. Verify current "
                f"admission rules, fees and availability.\n"
                f"* **Source:** Course knowledge base\n"
            )

    else:
        output.append(
            "No sufficiently relevant institution records were retrieved."
        )

    # --------------------------------------------------------
    # SCHOLARSHIPS
    # --------------------------------------------------------

    output.append("\n---\n### 3. ELIGIBLE SCHOLARSHIPS\n")

    if scholarships:

        for scholarship in scholarships[:4]:

            output.append(
                f"**Scholarship:** {scholarship}\n"
                f"* **Eligibility:** Verify the student's current "
                f"category, income, marks and course requirements.\n"
                f"* **Benefit:** Refer to the retrieved source for "
                f"the exact benefit.\n"
                f"* **Source:** Scholarship knowledge base\n"
            )

    else:
        output.append(
            "No scholarship records were sufficiently matched."
        )

    # --------------------------------------------------------
    # SCHEMES
    # --------------------------------------------------------

    output.append("\n---\n### 4. GOVERNMENT SCHEMES\n")

    if schemes:

        for scheme in schemes[:4]:

            output.append(
                f"**Scheme:** {scheme}\n"
                f"* **Eligibility:** Verify current government "
                f"eligibility requirements.\n"
                f"* **Benefit:** Refer to the retrieved source "
                f"for the exact benefit.\n"
                f"* **Source:** Government-scheme knowledge base\n"
            )

    else:
        output.append(
            "No government scheme records were sufficiently matched."
        )

    # --------------------------------------------------------
    # PRACTICE PLATFORM ENGINE
    # --------------------------------------------------------

    output.append(
        "\n---\n### 5. PRACTICE & SKILL DEVELOPMENT\n"
    )

    if practice_platforms:

        for platform in practice_platforms[:8]:

            output.append(
                f"**Platform:** {platform['platform']}\n"
                f"* **Domain:** {platform['domain']}\n"
                f"* **Focus:** {platform['focus']}\n"
                f"* **How to practice:** {platform['practice']}\n"
            )

    # --------------------------------------------------------
    # 30-DAY PLAN
    # --------------------------------------------------------

    output.append(
        "\n---\n### 6. PERSONALIZED 30-DAY PRACTICE PLAN\n"
    )

    primary_platforms = practice_platforms[:4]

    names = [
        x["platform"]
        for x in primary_platforms
    ]

    platform_text = ", ".join(names)

    output.append(
        f"* **Week 1: Foundation**\n"
        f"  * Learn the fundamental concepts required for your "
        f"target career.\n"
        f"  * Practice using {platform_text}.\n\n"

        f"* **Week 2: Core Skills**\n"
        f"  * Solve progressively harder problems and complete "
        f"topic-based exercises.\n\n"

        f"* **Week 3: Applied Practice**\n"
        f"  * Build a small project related to your career domain.\n"
        f"  * Use GitHub or an appropriate portfolio platform "
        f"to document your work.\n\n"

        f"* **Week 4: Portfolio & Assessment**\n"
        f"  * Complete a mini-project.\n"
        f"  * Review your weak areas.\n"
        f"  * Attempt assessments, challenges or mock tests."
    )

    # --------------------------------------------------------
    # NEXT STEPS
    # --------------------------------------------------------

    output.append(
        "\n---\n### 7. NEXT STEPS\n"
    )

    for index, step in enumerate(next_steps, start=1):
        output.append(
            f"{index}. {step}"
        )

    # --------------------------------------------------------
    # IMPORTANT NOTE
    # --------------------------------------------------------

    output.append(
        "\n---\n### 8. IMPORTANT NOTE\n"
        "\n* Retrieved information should be treated as "
        "decision-support information.\n"
        "* Historical admission/cutoff data must not be treated "
        "as current.\n"
        "* Scholarship and scheme eligibility must be verified "
        "against the current official rules.\n"
        "* Current admission dates, fees and deadlines should be "
        "verified before making decisions."
    )

    return "\n".join(output)


# ============================================================
# OLLAMA CALL
# ============================================================

def _call_ollama(prompt):
    """Call local Ollama model."""

    url = getattr(
        config,
        "OLLAMA_URL",
        "http://localhost:11434/api/generate"
    )

    model = getattr(
        config,
        "OLLAMA_MODEL",
        "llama3.2:latest"
    )

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    response = requests.post(
        url,
        json=payload,
        timeout=3
    )

    response.raise_for_status()

    data = response.json()

    text = data.get("response", "").strip()

    if not text:
        raise RuntimeError(
            "Ollama returned an empty response."
        )

    return text


def _is_temporary_error(error: Exception) -> bool:
    err_str = str(error).lower()
    return any(k in err_str for k in ["429", "quota", "resource exhausted", "503", "timeout", "unavailable", "rate limit"])


# ============================================================
# GEMINI CALL
# ============================================================

def _call_gemini(prompt):
    """Call Gemini with retry logic."""

    api_key = getattr(
        config,
        "GEMINI_API_KEY",
        ""
    )

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    client = genai.Client(
        api_key=api_key
    )

    last_error = None

    for attempt in range(1, 4):

        try:

            print(
                f"[Recommendation Agent] "
                f"Calling Gemini (attempt {attempt}/3)..."
            )

            response = client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt,
            )

            text = getattr(
                response,
                "text",
                None
            )

            if not text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            print(
                "[Recommendation Agent] "
                "Gemini recommendation successful."
            )

            return text.strip()

        except Exception as error:

            last_error = error

            print(
                f"[Recommendation Agent] "
                f"Gemini error: {error}"
            )

            if _is_temporary_error(error) and attempt < 3:

                wait_time = 2 ** attempt

                print(
                    f"[Recommendation Agent] "
                    f"Temporary Gemini error. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:
                break

    raise last_error


# ============================================================
# MAIN RECOMMENDATION FUNCTION
# ============================================================

def generate_recommendation(
    profile,
    context
):
    """
    Generate the complete recommendation.

    Pipeline:
        Profile
            ↓
        RAG Context
            ↓
        Practice Platform Engine
            ↓
        Gemini
            ↓
        Ollama
            ↓
        Rule-based fallback
    """

    careers = _extract_career_options(
        context
    )

    # --------------------------------------------------------
    # BUILD PRACTICE ENGINE
    # --------------------------------------------------------

    practice_platforms = build_practice_platforms(
        profile,
        careers
    )

    formatted_context = _format_context(
        context
    )

    formatted_platforms = format_practice_platforms(
        practice_platforms
    )

    prompt = RECOMMENDATION_PROMPT.format(
        profile=profile,
        context=formatted_context,
        practice_platforms=formatted_platforms,
    )

    # --------------------------------------------------------
    # GEMINI
    # --------------------------------------------------------

    try:

        return _call_gemini(
            prompt
        )

    except Exception as gemini_error:

        print(
            "[Recommendation Agent] "
            f"Gemini unavailable: {gemini_error}"
        )

        print(
            "[Recommendation Agent] "
            "Switching to Ollama..."
        )

    # --------------------------------------------------------
    # OLLAMA
    # --------------------------------------------------------

    try:

        result = _call_ollama(
            prompt
        )

        print(
            "[Recommendation Agent] "
            "Ollama recommendation successful."
        )

        return result

    except Exception as ollama_error:

        print(
            "[Recommendation Agent] "
            f"Ollama unavailable: {ollama_error}"
        )

        print(
            "[Recommendation Agent] "
            "Switching to rule-based fallback."
        )

    # --------------------------------------------------------
    # RULE-BASED FALLBACK
    # --------------------------------------------------------

    return _rule_based_recommendation(
        profile,
        context,
        practice_platforms
    )


# ============================================================
# GRAPH ENTRY POINT
# ============================================================

def run_recommendation(
    state
):
    """
    LangGraph-compatible Recommendation Agent.
    """

    profile = state.get(
        "profile",
        {}
    )

    context = state.get(
        "retrieval",
        {}
    )

    recommendation = generate_recommendation(
        profile,
        context
    )

    return {
        **state,
        "recommendation": recommendation,
        "practice_platforms": build_practice_platforms(
            profile,
            _extract_career_options(context)
        ),
    }


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    test_profile = {
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
            "financial constraints"
        ),
        "goal": (
            "scholarship options and career advice"
        ),
    }

    test_context = {
        "career": [
            {
                "text": (
                    "career: Robotics Engineer, "
                    "education: B.Tech Robotics / Mechanical / ECE"
                ),
                "source": "expanded_careers.csv",
                "score": 0.65,
            },
            {
                "text": (
                    "career: AI ML Engineer, "
                    "education: B.Tech Computer Science / AI ML"
                ),
                "source": "expanded_careers.csv",
                "score": 0.62,
            },
        ],

        "course": [],

        "scholarship": [],

        "scheme": [],
    }

    print(
        "\n"
        + "=" * 60
    )

    print(
        "PRACTICE PLATFORM ENGINE TEST"
    )

    print(
        "=" * 60
    )

    platforms = build_practice_platforms(
        test_profile,
        [
            "Robotics Engineer",
            "AI ML Engineer"
        ]
    )

    for item in platforms:

        print(
            f"\n{item['platform']}"
        )

        print(
            f"Domain : {item['domain']}"
        )

        print(
            f"Focus  : {item['focus']}"
        )

        print(
            f"Practice: {item['practice']}"
        )

    print(
        "\n"
        + "=" * 60
    )

    print(
        "GENERATING RECOMMENDATION"
    )

    print(
        "=" * 60
    )

    result = generate_recommendation(
        test_profile,
        test_context
    )

    print(result)

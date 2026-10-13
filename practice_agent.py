"""
Practice & Skills Agent

Provides domain-to-platform mappings and generates a 30-Day structured practice plan
broken down into 4 progressive weeks for students across technical, medical, commerce,
humanities, law, core engineering, and pure science disciplines.
"""
from typing import Any, Dict, List

# Curated platform registry per domain / stream
PLATFORM_REGISTRY = {
    "computer_science": [
        {
            "platform": "LeetCode",
            "url": "https://leetcode.com",
            "focus": "Data Structures & Algorithms (DSA)",
            "practice": "Solve 1-2 problems daily starting with Arrays, Two Pointers, Strings, and Hashing.",
            "badge": "DSA / Coding Interviews",
        },
        {
            "platform": "HackerRank",
            "url": "https://www.hackerrank.com",
            "focus": "Language Proficiency (Python / C++ / Java / SQL)",
            "practice": "Earn 5-star badges in Python and SQL through targeted problem sets.",
            "badge": "Core Fundamentals",
        },
        {
            "platform": "GitHub",
            "url": "https://github.com",
            "focus": "Version Control & Portfolio",
            "practice": "Commit code daily, maintain structured READMEs, and showcase end-to-end projects.",
            "badge": "Portfolio & Git",
        },
        {
            "platform": "CodeChef",
            "url": "https://www.codechef.com",
            "focus": "Contest & Timed Problem Solving",
            "practice": "Participate in Starters / Wednesday contests to build speed and accuracy.",
            "badge": "Competitive Programming",
        },
    ],
    "ai_ml_data": [
        {
            "platform": "Kaggle",
            "url": "https://www.kaggle.com",
            "focus": "Data Science Competitions & Datasets",
            "practice": "Work through Kaggle Learn micro-courses (Pandas, Intro to ML) and EDA notebooks.",
            "badge": "Machine Learning",
        },
        {
            "platform": "Google Colab",
            "url": "https://colab.research.google.com",
            "focus": "Cloud GPU & Model Training",
            "practice": "Train PyTorch / Scikit-Learn models with free T4 GPU acceleration.",
            "badge": "Deep Learning / GPU",
        },
        {
            "platform": "Hugging Face",
            "url": "https://huggingface.co",
            "focus": "Pre-trained Transformer Models & NLP",
            "practice": "Experiment with open-source LLMs, embeddings, and build Gradio spaces.",
            "badge": "GenAI & NLP",
        },
        {
            "platform": "GitHub",
            "url": "https://github.com",
            "focus": "ML Project Repositories",
            "practice": "Publish reproducible notebook repos with requirements.txt and evaluation metrics.",
            "badge": "MLOps & Portfolio",
        },
    ],
    "robotics_embedded": [
        {
            "platform": "Tinkercad Circuits",
            "url": "https://www.tinkercad.com/circuits",
            "focus": "Arduino & Circuit Simulation",
            "practice": "Simulate sensor interfacing (ultrasonic, IR, servo motors) without hardware cost.",
            "badge": "Circuit Sim",
        },
        {
            "platform": "Wokwi",
            "url": "https://wokwi.com",
            "focus": "ESP32 & IoT Microcontroller Emulation",
            "practice": "Simulate WiFi-connected MQTT IoT sensors and MicroPython code.",
            "badge": "IoT & ESP32",
        },
        {
            "platform": "ROS (Robot Operating System)",
            "url": "https://www.ros.org",
            "focus": "Robotics Middleware & Navigation",
            "practice": "Practice node communication (publishers/subscribers) and Gazebo simulations.",
            "badge": "Robotics Software",
        },
        {
            "platform": "GitHub",
            "url": "https://github.com",
            "focus": "Firmware & Embedded Repos",
            "practice": "Share embedded C/C++ projects, schematics, and sensor drivers.",
            "badge": "Hardware Projects",
        },
    ],
    "electronics_ece": [
        {
            "platform": "Falstad Circuit Simulator",
            "url": "https://www.falstad.com/circuit",
            "focus": "Analog & Digital Circuit Intuition",
            "practice": "Explore interactive AC/DC, op-amps, filters, and digital logic circuits.",
            "badge": "Analog Simulation",
        },
        {
            "platform": "EDA Playground",
            "url": "https://www.edaplayground.com",
            "focus": "Verilog & Digital VLSI Design",
            "practice": "Write and simulate Verilog testbenches for combinational and sequential logic.",
            "badge": "VLSI / Verilog",
        },
        {
            "platform": "KiCad",
            "url": "https://www.kicad.org",
            "focus": "Schematic Capture & PCB Layout",
            "practice": "Design a complete 2-layer PCB (power supply or sensor breakout board).",
            "badge": "PCB Design",
        },
    ],
    "mechanical_civil_core": [
        {
            "platform": "Autodesk Fusion 360",
            "url": "https://www.autodesk.com/products/fusion-360",
            "focus": "3D CAD Modeling & Engineering Design",
            "practice": "Model mechanical components, parametric sketches, and structural assemblies.",
            "badge": "CAD & Drafting",
        },
        {
            "platform": "GrabCAD",
            "url": "https://grabcad.com",
            "focus": "Engineering Community & CAD Library",
            "practice": "Study real-world mechanical models, mechanisms, and manufacturing blueprints.",
            "badge": "Mechanical Design",
        },
        {
            "platform": "SimScale",
            "url": "https://www.simscale.com",
            "focus": "Cloud-Based FEA & CFD Simulation",
            "practice": "Run structural stress analysis and fluid flow simulations on CAD geometry.",
            "badge": "FEA / CFD Simulation",
        },
        {
            "platform": "NPTEL Core Engineering",
            "url": "https://nptel.ac.in",
            "focus": "GATE & Core Engineering Concepts",
            "practice": "Prepare for GATE and technical interviews with IIT faculty video lectures.",
            "badge": "GATE & Core Theory",
        },
    ],
    "medical_healthcare": [
        {
            "platform": "Medscape",
            "url": "https://www.medscape.com",
            "focus": "Clinical Knowledge, Case Studies & Drug Guides",
            "practice": "Review clinical case presentations, diagnostic protocols, and medical updates.",
            "badge": "Clinical Practice",
        },
        {
            "platform": "Osmosis & BioNinja",
            "url": "https://www.osmosis.org",
            "focus": "Medical Physiology & Pathology Visuals",
            "practice": "Master complex physiological pathways and biochemical cycles through visual revision.",
            "badge": "Physiology & Anatomy",
        },
        {
            "platform": "NCBI Bookshelf & PubMed",
            "url": "https://www.ncbi.nlm.nih.gov/books",
            "focus": "Medical Reference & Evidence-Based Research",
            "practice": "Read peer-reviewed clinical articles and authoritative medical textbooks.",
            "badge": "Medical Research",
        },
        {
            "platform": "Khan Academy Medicine",
            "url": "https://www.khanacademy.org/science/health-and-medicine",
            "focus": "Pre-Med & Human Biology Foundations",
            "practice": "Practice organ system quizzes and NEET/medical entrance preparation concepts.",
            "badge": "Pre-Med Foundations",
        },
    ],
    "commerce_finance_ca": [
        {
            "platform": "Zerodha Varsity",
            "url": "https://zerodha.com/varsity",
            "focus": "Financial Markets, Technical & Fundamental Analysis",
            "practice": "Complete comprehensive modules on stock markets, corporate valuation, and taxation.",
            "badge": "Financial Markets",
        },
        {
            "platform": "ICAI BoS Knowledge Portal",
            "url": "https://boslive.icai.org",
            "focus": "CA Foundation, Intermediate & Accounting Standards",
            "practice": "Study official ICAI study materials, practice past exam RTPs and MTPs.",
            "badge": "CA / Accounting Standards",
        },
        {
            "platform": "Corporate Finance Institute (CFI)",
            "url": "https://corporatefinanceinstitute.com",
            "focus": "Financial Modeling, Valuation & Advanced Excel",
            "practice": "Build balance sheet financial models and practice ratio analysis in spreadsheets.",
            "badge": "Financial Modeling",
        },
        {
            "platform": "Moneycontrol & TradingView",
            "url": "https://www.moneycontrol.com",
            "focus": "Live Financial Statements & Market Analysis",
            "practice": "Analyze annual reports, P&L statements, and track economic indicators.",
            "badge": "Corporate Finance",
        },
    ],
    "law_legal": [
        {
            "platform": "LiveLaw & Bar and Bench",
            "url": "https://www.livelaw.in",
            "focus": "Supreme Court & High Court Judgments",
            "practice": "Read daily judgment summaries and extract legal principles and constitutional doctrines.",
            "badge": "Legal Current Affairs",
        },
        {
            "platform": "Indian Kanoon",
            "url": "https://indiankanoon.org",
            "focus": "Indian Case Law & Statute Database",
            "practice": "Practice searching case laws by citations and analyze judicial precedents.",
            "badge": "Case Law Research",
        },
        {
            "platform": "India Code",
            "url": "https://www.indiacode.nic.in",
            "focus": "Central & State Acts, Statutes & Bare Acts",
            "practice": "Study bare acts (IPC/BNS, CrPC/BNSS, Contract Act, Constitution of India).",
            "badge": "Statutory Law",
        },
        {
            "platform": "Legal Bites / CLAT Prep",
            "url": "https://www.legalbites.in",
            "focus": "Legal Aptitude & Constitutional Law Drills",
            "practice": "Solve passage-based legal reasoning questions and mock test series.",
            "badge": "CLAT / Judicial Prep",
        },
    ],
    "arts_humanities_civil_services": [
        {
            "platform": "InsightsIAS / ClearIAS",
            "url": "https://www.insightsonindia.com",
            "focus": "UPSC / TNPSC Current Affairs & Daily Answer Writing",
            "practice": "Practice daily mains answer writing drills and secure editorial analysis.",
            "badge": "Civil Services Prep",
        },
        {
            "platform": "Drishti IAS",
            "url": "https://www.drishtiias.com",
            "focus": "General Studies, Polity, History & Geography",
            "practice": "Review detailed syllabus maps, toppers' answer copies, and static quizzes.",
            "badge": "General Studies",
        },
        {
            "platform": "Press Information Bureau (PIB)",
            "url": "https://pib.gov.in",
            "focus": "Official Government Policies, Data & Scheme Notifications",
            "practice": "Extract authoritative data points and scheme summaries for competitive exams.",
            "badge": "Govt Policy & Data",
        },
        {
            "platform": "Project Gutenberg & Internet Archive",
            "url": "https://www.gutenberg.org",
            "focus": "Classic Literature, Historical Texts & Philosophy",
            "practice": "Study primary source documents and critical essays for academic depth.",
            "badge": "Literature & Research",
        },
    ],
    "pure_sciences": [
        {
            "platform": "PhET Interactive Simulations",
            "url": "https://phet.colorado.edu",
            "focus": "Physics & Chemistry Interactive Concept Experiments",
            "practice": "Explore interactive simulations of atomic models, optics, kinematics, and thermodynamics.",
            "badge": "Interactive Science Sim",
        },
        {
            "platform": "Brilliant.org & Wolfram Alpha",
            "url": "https://www.wolframalpha.com",
            "focus": "Mathematical Logic, Proofs & Scientific Computation",
            "practice": "Solve advanced calculus, linear algebra, and computational science problems.",
            "badge": "Math & Theory",
        },
        {
            "platform": "NPTEL Science Disciplines",
            "url": "https://nptel.ac.in",
            "focus": "Higher University Physics, Chemistry & Biology",
            "practice": "Follow university-level courses designed by IIT & IISc faculty.",
            "badge": "IISc / IIT Science",
        },
        {
            "platform": "PubChem & ChemSpider",
            "url": "https://pubchem.ncbi.nlm.nih.gov",
            "focus": "Molecular Structures & Chemical Informatics",
            "practice": "Analyze chemical formulas, 3D structures, bioassays, and reaction kinetics.",
            "badge": "Chemical Informatics",
        },
    ],
    "design_architecture": [
        {
            "platform": "Figma Community",
            "url": "https://www.figma.com",
            "focus": "UI/UX Wireframing, Prototypes & Design Systems",
            "practice": "Build responsive app and website designs, master auto-layout and interactive components.",
            "badge": "UI/UX Design",
        },
        {
            "platform": "Behance & Dribbble",
            "url": "https://www.behance.net",
            "focus": "Design Portfolio Showcase & Industry Feedback",
            "practice": "Publish comprehensive case studies documenting your design process and problem solving.",
            "badge": "Design Portfolio",
        },
        {
            "platform": "Sketchfab",
            "url": "https://sketchfab.com",
            "focus": "3D Modeling, Visualization & Architecture",
            "practice": "Explore and showcase real-time 3D models, architectural renders, and spatial design.",
            "badge": "3D & Spatial Design",
        },
    ],
    "general_engineering": [
        {
            "platform": "HackerRank",
            "url": "https://www.hackerrank.com",
            "focus": "Problem Solving & Programming",
            "practice": "Learn Python basics and algorithmic thinking for technical screening rounds.",
            "badge": "Foundational Coding",
        },
        {
            "platform": "Coursera / NPTEL",
            "url": "https://nptel.ac.in",
            "focus": "IIT / IISc Certified Academic Courses",
            "practice": "Enroll in core domain subjects taught by premier Indian faculty.",
            "badge": "Govt Recognized Certs",
        },
        {
            "platform": "GitHub",
            "url": "https://github.com",
            "focus": "Engineering Projects",
            "practice": "Document your academic mini-projects and lab code repositories.",
            "badge": "Portfolio",
        },
    ],
}


def get_domain_platforms(stream: str, interests: List[str] = None) -> List[Dict[str, str]]:
    """Determine the most relevant practice platforms tailored to the student's actual stream and interests."""
    combined = (str(stream or "") + " " + " ".join(interests or [])).lower()

    # 1. Medical & Healthcare
    if any(k in combined for k in [
        "medical", "mbbs", "bds", "doctor", "medicine", "nursing", "pharmacy",
        "physiotherapy", "biomedical", "neet", "clinical", "healthcare", "dentist", "allied health"
    ]):
        return PLATFORM_REGISTRY["medical_healthcare"]

    # 2. Commerce, Finance & CA
    elif any(k in combined for k in [
        "commerce", "b.com", "bcom", "bba", "accounting", "accountant", "ca",
        "finance", "banking", "fintech", "investment", "tax", "chartered", "audit", "tally", "cma"
    ]):
        return PLATFORM_REGISTRY["commerce_finance_ca"]

    # 3. Law & Legal Studies
    elif any(k in combined for k in [
        "law", "legal", "advocate", "lawyer", "llb", "clat", "judiciary", "litigation", "constitution", "judicial"
    ]):
        return PLATFORM_REGISTRY["law_legal"]

    # 4. Arts, Humanities & Civil Services
    elif any(k in combined for k in [
        "arts", "humanities", "upsc", "civil services", "ias", "ips", "history",
        "psychology", "sociology", "political science", "journalism", "literature", "social work"
    ]):
        return PLATFORM_REGISTRY["arts_humanities_civil_services"]

    # 5. Pure Sciences & Research
    elif any(k in combined for k in [
        "pure science", "physics", "chemistry", "mathematics", "maths", "biology",
        "biotech", "b.sc", "bsc", "researcher", "scientific", "astronomy"
    ]):
        return PLATFORM_REGISTRY["pure_sciences"]

    # 6. Core Engineering (Mechanical, Civil, Automobile, etc.)
    elif any(k in combined for k in [
        "mechanical", "civil", "automobile", "aerospace", "aeronautical", "chemical engineering",
        "structural", "cad", "thermal", "manufacturing"
    ]):
        return PLATFORM_REGISTRY["mechanical_civil_core"]

    # 7. Design & Architecture
    elif any(k in combined for k in [
        "design", "ui", "ux", "graphic design", "animation", "vfx", "architecture", "fashion"
    ]):
        return PLATFORM_REGISTRY["design_ui_architecture"]

    # 8. Robotics & Embedded / IoT
    elif any(k in combined for k in ["robot", "iot", "arduino", "embedded", "automation"]):
        return PLATFORM_REGISTRY["robotics_embedded"]

    # 9. AI & Machine Learning / Data Science
    elif any(k in combined for k in ["ai", "machine learning", "data science", "nlp", "deep learning", "analytics"]):
        return PLATFORM_REGISTRY["ai_ml_data"]

    # 10. Electronics & VLSI
    elif any(k in combined for k in ["electronics", "vlsi", "electrical", "ece", "eee", "circuit"]):
        return PLATFORM_REGISTRY["electronics_ece"]

    # 11. Computer Science & Software
    elif any(k in combined for k in ["computer", "software", "it", "web", "coding", "python", "full stack"]):
        return PLATFORM_REGISTRY["computer_science"]

    # 12. Fallback
    else:
        return PLATFORM_REGISTRY["general_engineering"]


def generate_30_day_plan(profile: Dict[str, Any], target_career: str = None) -> Dict[str, Any]:
    """
    Generates a structured 30-Day, 4-Week practice roadmap tailored to the student's actual stream and career goal.
    """
    stream = str(profile.get("stream", "Engineering")).capitalize()
    stream_lower = stream.lower()
    interests = profile.get("interests", [])
    interests_str = " ".join(interests).lower()
    primary_interest = interests[0] if interests else stream
    career = target_career or "Specialist Professional"

    combined = f"{stream_lower} {interests_str} {str(target_career or '').lower()}"

    # --- Domain-Tailored Week-by-Week Plans ---
    if any(k in combined for k in ["medical", "mbbs", "bds", "doctor", "nursing", "pharmacy", "medicine", "health"]):
        week1_task = f"Master high-yield NCERT and foundational medical concepts in Human Physiology, Genetics, and Biochemistry; set up Medscape/Anki digital flashcards."
        week2_task = f"Complete daily diagnostic case drills and organ-system pathology reviews on Khan Academy Health & Osmosis; solve 50+ medical entrance practice MCQs daily."
        week3_task = f"Deepen clinical pharmacology and medical terminology; solve 3 full-length timed NEET/Medical entrance mock question papers."
        week4_task = f"Analyze high-yield mistake logs, review state medical counseling cutoffs (NEET/State Quota), and finalize application documentation."

    elif any(k in combined for k in ["commerce", "b.com", "bcom", "bba", "accounting", "ca", "finance", "banking", "tax", "chartered"]):
        week1_task = f"Review Double Entry Bookkeeping, Journal Entries, and Financial Accounting fundamentals; set up daily market tracking on Zerodha Varsity and Moneycontrol."
        week2_task = f"Deep dive into Corporate Law basics, GST compliance, and ratio analysis; practice 10 balance-sheet reconciliation drills in MS Excel."
        week3_task = f"Build an applied Financial Model / Budget Forecast in Excel; solve 2 past CA Foundation / IBPS Banking aptitude examination papers."
        week4_task = f"Complete 2 full-length mock examinations for CA/Banking/CMA; document an Excel-based corporate financial analysis portfolio."

    elif any(k in combined for k in ["law", "legal", "advocate", "lawyer", "llb", "clat", "judiciary", "litigation"]):
        week1_task = f"Study Constitutional Law foundations (Fundamental Rights, Directive Principles) and analyze 5 landmark Supreme Court verdicts on LiveLaw/Indian Kanoon."
        week2_task = f"Master Law of Torts, Indian Contract Act fundamentals, and legal reasoning maxims; complete daily legal vocabulary exercises."
        week3_task = f"Draft sample legal notices and case briefs; solve 100+ passage-based legal reasoning questions from past CLAT/AILET papers."
        week4_task = f"Complete 2 full-length timed legal aptitude mock tests; participate in mock legal argument drafting and research top law school admission cutoffs."

    elif any(k in combined for k in ["arts", "humanities", "upsc", "civil services", "ias", "history", "psychology", "journalism", "social"]):
        week1_task = f"Consolidate core Modern Indian History, Geography, and Indian Polity concepts; start daily editorial note-making from The Hindu/InsightsIAS."
        week2_task = f"Practice structured daily subjective answer writing (2 questions/day with introduction, structured subheadings, and policy conclusions)."
        week3_task = f"Synthesize central and state welfare schemes and economic survey data; solve CSAT logical reasoning and comprehension papers."
        week4_task = f"Attempt 2 full-length General Studies mock tests; compile high-yield current affairs mind-maps and prepare scholarship/entrance files."

    elif any(k in combined for k in ["pure science", "physics", "chemistry", "mathematics", "maths", "biology", "biotech"]):
        week1_task = f"Review foundational theory (Calculus, Quantum/Classical Physics, Reaction Mechanisms) using PhET Interactive Simulations and standard university texts."
        week2_task = f"Solve 20 advanced numerical problems daily; master laboratory experimental setups, error analysis, and mathematical proofs."
        week3_task = f"Conduct computational experiments using Wolfram Alpha or Python scientific stack (NumPy/SciPy); write a mini scientific literature review."
        week4_task = f"Take competitive entrance mocks (IISER IAT / NEST / CUET / JAM) and research admission criteria for premier institutions (IISc, IISERs)."

    elif any(k in combined for k in ["mechanical", "civil", "automobile", "aerospace", "structural", "cad"]):
        week1_task = f"Review Engineering Mechanics and Strength of Materials; install and configure Autodesk Fusion 360 / AutoCAD student edition."
        week2_task = f"Create 5 parametric 3D CAD models of mechanical assemblies or civil structural components with technical tolerance drawings."
        week3_task = f"Run finite element analysis (FEA) or flow simulations on SimScale; solve GATE / technical core engineering numerical problems."
        week4_task = f"Assemble a complete technical design portfolio on GrabCAD; prepare engineering resume and documentation for technical internships."

    elif any(k in combined for k in ["design", "ui", "ux", "graphic", "architecture", "animation"]):
        week1_task = f"Master design hierarchy, typography, and color theory; set up Figma and study design systems from Google Material Design and Apple HIG."
        week2_task = f"Design low-fidelity wireframes and interactive prototypes for a mobile application addressing a real student or community need."
        week3_task = f"Build high-fidelity UI components, micro-interactions, and conduct user testing with 3 peer participants to collect feedback."
        week4_task = f"Publish a comprehensive UX case study on Behance/Dribbble detailing problem statement, user journey, and final visual designs."

    else:
        # Default for Computer Science, Tech, and Software Engineering
        week1_task = f"Set up clean development environment: Git, VS Code, and programming language runtime; solve 10 foundational algorithmic problems on HackerRank."
        week2_task = f"Deepen {primary_interest} core skills: implement essential data structures (Arrays, Dictionaries, Trees) and write clean, modular functions."
        week3_task = f"Build an end-to-end applied mini project targeting {career}; connect business logic with a functional database or API interface."
        week4_task = f"Document and deploy project on GitHub with a comprehensive README, setup instructions, and live demonstration link."

    plan = {
        "title": f"30-Day High-Impact Action Plan for {career}",
        "focus_domain": f"{stream} — {primary_interest}",
        "weeks": [
            {
                "week": 1,
                "days": "Days 1–7",
                "theme": "Foundations & Core Principles",
                "goal": "Establish structured daily practice habits and master essential domain fundamentals.",
                "action": week1_task,
                "deliverable": "Study workspace configured + core concept notes finalized.",
                "time_commitment": "1.5 – 2 hours / day",
                "status": "Ready to Start",
            },
            {
                "week": 2,
                "days": "Days 8–14",
                "theme": "Core Concepts & Problem Solving",
                "goal": f"Deepen analytical understanding and daily drills in {primary_interest}.",
                "action": week2_task,
                "deliverable": "10+ solved problem sets / practical concept exercises completed.",
                "time_commitment": "2 hours / day",
                "status": "Upcoming",
            },
            {
                "week": 3,
                "days": "Days 15–21",
                "theme": "Applied Practice & Mini-Project",
                "goal": "Synthesize knowledge into a practical application or comprehensive mock review.",
                "action": week3_task,
                "deliverable": "Working prototype, drafted brief, or completed exam section series.",
                "time_commitment": "2 – 2.5 hours / day",
                "status": "Upcoming",
            },
            {
                "week": 4,
                "days": "Days 22–30",
                "theme": "Showcase, Assessment & Next Steps",
                "goal": "Evaluate performance under exam/recruitment conditions and package your accomplishments.",
                "action": week4_task,
                "deliverable": "Full portfolio / mock test performance report + updated profile.",
                "time_commitment": "2 hours / day",
                "status": "Upcoming",
            },
        ],
    }
    return plan

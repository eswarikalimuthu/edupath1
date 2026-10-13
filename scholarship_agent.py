"""
Scholarship Evaluator Agent

Structures retrieved scholarship documents into high-fidelity evaluation cards
for students. Evaluates:
- Social category compatibility (SC, ST, BC, MBC, DNC, OBC, EWS, General)
- Annual family income limits
- State domicile eligibility (Tamil Nadu vs Central vs Other States)
- Education stage (Pre-Matric, Post-Matric, Undergraduate, Postgraduate)
- Required documents and application portals
"""
import re
from typing import Any, Dict, List

# Common scholarship application portals in India
PORTALS = {
    "nsp": {"name": "National Scholarship Portal (NSP)", "url": "https://scholarships.gov.in"},
    "tn": {"name": "TN e-District / Adi Dravidar Welfare", "url": "https://escholarship.tn.gov.in"},
    "aicte": {"name": "AICTE Student Development Schemes", "url": "https://www.aicte-india.org/schemes/students-development-schemes"},
    "ugc": {"name": "UGC e-Scholarship Portal", "url": "https://www.ugc.ac.in"},
    "buddy4study": {"name": "Buddy4Study Portal", "url": "https://www.buddy4study.com"}
}

STANDARD_DOCUMENTS = [
    "Aadhaar Card / Government Photo ID",
    "Previous Academic Marksheet (10th / 12th / Semester)",
    "Community / Caste Certificate (issued by Tahsildar/Revenue Dept)",
    "Income Certificate (issued within last 6-12 months)",
    "Bonafide / Admission Letter from Institution",
    "Student Bank Passbook (linked with Aadhaar/DBT enabled)",
]


def _extract_name_and_provider(text: str) -> tuple[str, str]:
    """Extract scholarship name and issuing body."""
    name = "Government / Institutional Scholarship"
    provider = "Government of India / State Government"

    # Match 'scholarship: <name>' or 'title: <name>' or 'name: <name>'
    name_match = re.search(r'(?:scholarship|title|name|scheme)\s*:\s*([^,\r\n]+)', text, re.IGNORECASE)
    if name_match:
        name = name_match.group(1).strip()
    else:
        # First non-empty segment before comma or period
        first_segment = text.split(",")[0].split(".")[0].strip()
        if len(first_segment) < 70 and not any(k in first_segment.lower() for k in ["eligibility", "income", "benefit"]):
            name = first_segment

    # Clean name
    name = re.sub(r'^(scholarship|scheme)\s*[-:]\s*', '', name, flags=re.IGNORECASE).strip()

    # Identify provider
    text_lower = text.lower()
    if "tamil nadu" in text_lower or "tn " in text_lower or "adi dravidar" in text_lower or "naan mudhalvan" in text_lower or "pudhumai penn" in text_lower:
        provider = "Government of Tamil Nadu (State Scheme)"
    elif "ministry of social justice" in text_lower:
        provider = "Ministry of Social Justice & Empowerment (Govt of India)"
    elif "ministry of tribal" in text_lower:
        provider = "Ministry of Tribal Affairs (Govt of India)"
    elif "aicte" in text_lower or "pragati" in text_lower or "saksham" in text_lower:
        provider = "AICTE (All India Council for Technical Education)"
    elif "ugc" in text_lower:
        provider = "University Grants Commission (UGC)"
    elif "central" in text_lower or "post-matric" in text_lower or "national" in text_lower or "nsp" in text_lower:
        provider = "Central Government (National Scholarship Portal)"

    return name, provider


def _extract_benefit_amount(text: str) -> str:
    """Extract financial benefits and maintenance allowance."""
    text_lower = text.lower()

    # Look for currency / rupee / tuition mentions
    benefit_patterns = [
        r'(?:benefit|amount|stipend|financial assistance|scholarship of|grant|allowance)\s*[:=]?\s*([^.\r\n]+(?:per annum|per year|per month|\/-\s*| INR |₹|lakhs?|full tuition)[^.\r\n]*)',
        r'((?:₹|rs\.?|inr)\s*[\d,]+(?:\s*(?:lakh|thousand|per month|per annum|\/-\s*))?)',
        r'(full tuition fee(?:\s*waiver)?(?:[^.\r\n]*))',
        r'(maintenance allowance[^.\r\n]+)',
    ]

    for pat in benefit_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            if len(val) > 120:
                val = val[:120].rstrip() + "..."
            return val

    if "free education" in text_lower or "tuition waiver" in text_lower:
        return "Full Tuition Fee Exemption / Waiver"
    if "maintenance" in text_lower and "hostel" in text_lower:
        return "Maintenance Allowance + Hosteller / Day Scholar Financial Support"

    return "Tuition assistance & standard maintenance grant as per government norms"


def _determine_portal(text: str, provider: str) -> dict:
    """Determine the official application portal."""
    text_lower = text.lower()
    if "tamil nadu" in text_lower or "adi dravidar" in text_lower or "state" in provider.lower():
        return PORTALS["tn"]
    elif "aicte" in text_lower or "pragati" in text_lower or "saksham" in text_lower:
        return PORTALS["aicte"]
    elif "ugc" in text_lower:
        return PORTALS["ugc"]
    else:
        return PORTALS["nsp"]


CURATED_SCHOLARSHIPS_CATALOG = [
    {
        "name": "Post-Matric Scholarship for SC / ST Students",
        "provider": "Ministry of Social Justice & Empowerment / TN Adi Dravidar Welfare",
        "amount": "100% Full Tuition Fee Waiver + Annual Maintenance Allowance (₹13,500/yr)",
        "target_categories": ["sc", "st"],
        "max_income": 250000,
        "education_stages": ["school", "undergraduate", "postgraduate", "12th standard"],
        "states": ["tamil nadu", "all"],
        "portal_name": "National Scholarship Portal & TN e-Scholarship",
        "portal_url": "https://scholarships.gov.in",
        "documents": [
            "Aadhaar Card",
            "Community / Caste Certificate (SC/ST)",
            "Income Certificate (< ₹2.5 Lakhs)",
            "10th / 12th Marksheet",
            "College Admission / Bonafide Certificate",
            "DBT-enabled Bank Passbook"
        ],
        "why_recommended": [
            "Complete 100% government tuition fee exemption in all government and private engineering colleges",
            "Direct Benefit Transfer (DBT) maintenance allowance for hostellers and day scholars",
            "Zero out-of-pocket academic expense for eligible SC/ST students"
        ]
    },
    {
        "name": "Post-Matric Scholarship for BC / MBC / DNC Students",
        "provider": "BC, MBC and Minorities Welfare Department (Government of Tamil Nadu)",
        "amount": "Full Tuition Fee Reimbursement + Special Fees & Examination Fees Concession",
        "target_categories": ["bc", "mbc", "dnc", "obc"],
        "max_income": 250000,
        "education_stages": ["undergraduate", "postgraduate", "12th standard"],
        "states": ["tamil nadu"],
        "portal_name": "TN e-District / Welfare Portal",
        "portal_url": "https://escholarship.tn.gov.in",
        "documents": [
            "Community Certificate (BC/MBC/DNC)",
            "Income Certificate issued by Revenue Tahsildar (< ₹2.5L)",
            "12th Standard Marksheet / Allotment Order",
            "Bank Passbook photocopy",
            "Attendance & Bonafide Certificate"
        ],
        "why_recommended": [
            "Tuition fee coverage for students admitted through TNEA Single-Window counseling",
            "Covers both government-aided and self-financing engineering colleges in Tamil Nadu",
            "Direct subsidy credit into student savings bank account"
        ]
    },
    {
        "name": "AICTE PRAGATI Scholarship Scheme for Girl Students",
        "provider": "All India Council for Technical Education (AICTE)",
        "amount": "₹50,000 per annum towards college fee & contingency equipment",
        "target_categories": ["all", "general", "bc", "mbc", "sc", "st", "obc", "ews"],
        "max_income": 800000,
        "education_stages": ["undergraduate", "school", "12th standard"],
        "states": ["all"],
        "portal_name": "National Scholarship Portal (AICTE Section)",
        "portal_url": "https://scholarships.gov.in",
        "documents": [
            "10th and 12th Marksheet",
            "AICTE Approved College Admission Allotment Letter",
            "Family Income Certificate (< ₹8 Lakhs)",
            "Parent / Guardian Affidavit for Girl Child",
            "Student Aadhaar linked Bank Account"
        ],
        "why_recommended": [
            "Generous ₹50,000 annual grant given for all 4 years of engineering degree",
            "Very broad family income ceiling up to ₹8,00,000 per annum",
            "No quota restriction—open across General, BC, MBC, SC, and ST girl students"
        ]
    },
    {
        "name": "Central Sector Scheme of Scholarships for College & University Students (PM-USP)",
        "provider": "Department of Higher Education (Ministry of Education, Govt of India)",
        "amount": "₹12,000 per year for Graduation + ₹20,000 per year for Post-Graduation",
        "target_categories": ["all", "general", "bc", "mbc", "sc", "st", "obc", "ews"],
        "max_income": 450000,
        "education_stages": ["undergraduate", "12th standard", "school"],
        "states": ["all"],
        "portal_name": "National Scholarship Portal (NSP)",
        "portal_url": "https://scholarships.gov.in",
        "documents": [
            "12th Board Marksheet (above 80th percentile)",
            "Income Certificate (< ₹4.5 Lakhs)",
            "College Joining Report / Verification Certificate",
            "Aadhaar linked Bank Account"
        ],
        "why_recommended": [
            "Merit-cum-means scholarship rewarding students scoring above 80th percentile in 12th board",
            "Renewable for up to 5 consecutive years from B.E/B.Tech through Masters",
            "Central government funded scholarship with punctual DBT disbursement"
        ]
    },
    {
        "name": "Tamil Nadu First Graduate Tuition Fee Concession",
        "provider": "Directorate of Technical Education (DoTE, Tamil Nadu)",
        "amount": "₹25,000 to ₹50,000 per year Tuition Fee Waiver in Engineering Colleges",
        "target_categories": ["all", "general", "bc", "mbc", "sc", "st", "obc"],
        "max_income": None,
        "education_stages": ["undergraduate", "12th standard"],
        "states": ["tamil nadu"],
        "portal_name": "TNEA Engineering Admissions Counseling",
        "portal_url": "https://www.tneaonline.org",
        "documents": [
            "First Graduate Certificate issued by Zonal Deputy Tahsildar",
            "Joint Declaration by Parents and Candidate",
            "12th Marksheet & Transfer Certificate",
            "TNEA Counseling Allotment Order"
        ],
        "why_recommended": [
            "NO family income limit restriction—applicable to any first graduate in family",
            "Immediate reduction in tuition fees directly during TNEA Single-Window counseling",
            "Applicable in Anna University campuses, Govt, Govt-Aided, and Self-Financing colleges"
        ]
    },
    {
        "name": "Pudhumai Penn & Tamizh Pudhalvan Higher Education Assurance Scheme",
        "provider": "Social Welfare & Women Empowerment Dept (Government of Tamil Nadu)",
        "amount": "₹1,000 per month (₹12,000 per year) direct bank assistance",
        "target_categories": ["all", "general", "bc", "mbc", "sc", "st", "obc"],
        "max_income": None,
        "education_stages": ["undergraduate", "12th standard"],
        "states": ["tamil nadu"],
        "portal_name": "Moovalur Ramamirtham Higher Education Portal",
        "portal_url": "https://www.penkalvi.tn.gov.in",
        "documents": [
            "Government School Study Certificate (Classes 6th to 12th in TN Govt Schools)",
            "College Admission Verification & Bonafide Letter",
            "Aadhaar Card",
            "Active Savings Bank Passbook"
        ],
        "why_recommended": [
            "Monthly financial incentive of ₹1,000 credited every month without fail",
            "No parental income ceiling required",
            "Can be availed concurrently alongside tuition fee waivers and post-matric scholarships"
        ]
    },
    {
        "name": "AICTE SAKSHAM Scholarship for Specially-Abled Students",
        "provider": "All India Council for Technical Education (AICTE)",
        "amount": "₹50,000 per annum towards tuition fee & assistive learning devices",
        "target_categories": ["all", "general", "bc", "mbc", "sc", "st", "obc", "ews"],
        "max_income": 800000,
        "education_stages": ["undergraduate", "school", "12th standard"],
        "states": ["all"],
        "portal_name": "National Scholarship Portal (AICTE SAKSHAM)",
        "portal_url": "https://scholarships.gov.in",
        "documents": [
            "Disability Certificate issued by Competent Medical Authority (40%+)",
            "Family Income Certificate (< ₹8 Lakhs)",
            "10th & 12th Marksheet",
            "Admission Allotment Letter to AICTE approved institution"
        ],
        "why_recommended": [
            "Dedicated empowerment grant of ₹50,000 per year for technical degree students",
            "Covers purchases of assistive devices, books, softwares, and study materials",
            "Renewable for every year of degree upon standard academic progression"
        ]
    },
    {
        "name": "PM YASASVI Post-Matric Scholarship for OBC, EBC & DNT Students",
        "provider": "Department of Social Justice & Empowerment (Government of India)",
        "amount": "Full Tuition Fee reimbursement + Annual Maintenance Allowance (₹20,000/yr)",
        "target_categories": ["obc", "ebc", "dnt", "bc", "mbc"],
        "max_income": 250000,
        "education_stages": ["undergraduate", "school", "12th standard"],
        "states": ["all", "tamil nadu"],
        "portal_name": "National Scholarship Portal (PM-YASASVI)",
        "portal_url": "https://scholarships.gov.in",
        "documents": [
            "Aadhaar Card",
            "OBC / EBC Community Certificate",
            "Income Certificate (< ₹2.5 Lakhs)",
            "10th / 12th Marksheet",
            "Bank Passbook linked to Aadhaar"
        ],
        "why_recommended": [
            "Premier central government scholarship for other backward classes and nomadic tribes",
            "Direct subsidy coverage for tuition and exam fees in government & private colleges",
            "Online application and direct DBT transfer through NSP"
        ]
    },
    {
        "name": "Post-Matric Scholarship Scheme for Minorities (CS)",
        "provider": "Ministry of Minority Affairs (Government of India)",
        "amount": "Full Course / Admission Fee up to ₹20,000/yr + Maintenance Allowance (₹10,000/yr)",
        "target_categories": ["all", "minority", "muslim", "christian", "sikh", "buddhist", "jain", "parsi"],
        "max_income": 250000,
        "education_stages": ["undergraduate", "school", "12th standard"],
        "states": ["all", "tamil nadu"],
        "portal_name": "National Scholarship Portal (Minorities)",
        "portal_url": "https://scholarships.gov.in",
        "documents": [
            "Minority Community Self-Declaration Certificate",
            "Income Certificate issued by Competent Authority (< ₹2.5 Lakhs)",
            "Previous Academic Marksheet (minimum 50% marks)",
            "College Bonafide / Enrollment Certificate",
            "Active Savings Bank Passbook"
        ],
        "why_recommended": [
            "Targeted central assistance for students belonging to notified minority communities",
            "Includes admission fee, tuition fee, and monthly maintenance support",
            "Renewable throughout standard duration of the undergraduate or diploma program"
        ]
    },
    {
        "name": "Reliance Foundation / Tata Capital Pankh Undergraduate Scholarship",
        "provider": "Reliance Foundation & Tata Trusts Corporate CSR Philanthropy",
        "amount": "Up to ₹2,00,000 total scholarship grant across 4 years of undergraduate study",
        "target_categories": ["all", "general", "bc", "mbc", "sc", "st", "obc", "ews"],
        "max_income": 1500000,
        "education_stages": ["undergraduate", "12th standard"],
        "states": ["all"],
        "portal_name": "Reliance Foundation / Buddy4Study Portal",
        "portal_url": "https://www.reliancefoundation.org",
        "documents": [
            "12th Board Marksheet (minimum 60% aggregate)",
            "Family Income Proof (ITR / Salary Slip / Revenue Income Certificate)",
            "College Admission Offer Letter & Fee Receipt",
            "Student Government ID Card & Statement of Purpose"
        ],
        "why_recommended": [
            "Prestigious corporate merit-cum-means scholarship for professional degree students",
            "High family income ceiling up to ₹15 Lakhs (special priority for income < ₹2.5 Lakhs)",
            "Includes industry leadership workshops, skill development, and alumni mentorship"
        ]
    }
]


def evaluate_scholarships(
    scholarship_chunks: List[Dict[str, Any]],
    profile: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Structures each retrieved scholarship chunk into an evaluation card.
    Guarantees rich, category-aligned scholarship recommendations with safe numeric parsing.
    """
    evaluated = []
    seen_names = set()

    # User details
    user_cat = str(profile.get("category", "")).lower() or "general"
    user_cat_display = user_cat.upper()
    user_state = str(profile.get("state", "")).capitalize() or "Tamil Nadu"
    user_stage = str(profile.get("education_stage", "")).replace("_", " ").capitalize()

    raw_inc = profile.get("annual_income")
    user_income = None
    if raw_inc is not None:
        try:
            clean_inc = re.sub(r"[^\d.]", "", str(raw_inc))
            user_income = float(clean_inc) if clean_inc else None
        except Exception:
            user_income = None

    # Special student profile flags
    is_girl = bool(profile.get("is_girl", False))
    is_first_graduate = bool(profile.get("is_first_graduate", False))
    is_gov_school = bool(profile.get("is_gov_school", False))
    is_specially_abled = bool(profile.get("is_specially_abled", False))
    is_minority = bool(profile.get("is_minority", False))

    for chunk in scholarship_chunks:
        text = chunk.get("text", "")
        if not text:
            continue

        name, provider = _extract_name_and_provider(text)

        # Simple deduplication by normalized name
        norm_name = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
        if norm_name in seen_names:
            continue
        seen_names.add(norm_name)

        benefit = _extract_benefit_amount(text)
        portal_info = _determine_portal(text, provider)

        # Match details from retrieval agent
        match_details = chunk.get("match_details", {})
        eligibility_status = match_details.get("eligibility", "potentially_eligible")

        # Category match text
        cat_bonus = match_details.get("category", 0.0)
        if cat_bonus > 0:
            category_match_text = f"{user_cat_display} (Direct Target Group ✓)"
        elif cat_bonus < 0:
            category_match_text = f"Restricted (Check Category Norms)"
        else:
            category_match_text = f"Open Category / Merit Cum Means"

        income_limit = match_details.get("income_limit")
        if income_limit:
            lim_lakh = income_limit / 100000.0
            if user_income is not None and user_income <= income_limit:
                income_match_text = f"✓ Family income ₹{int(user_income):,} within ₹{lim_lakh:.1f}L ceiling"
            elif user_income is not None and user_income > income_limit:
                income_match_text = f"⚠️ Income ₹{int(user_income):,} exceeds ₹{lim_lakh:.1f}L limit"
            else:
                income_match_text = f"Ceiling: Up to ₹{lim_lakh:.1f} Lakhs per annum"
        else:
            income_match_text = "Income criteria as specified in government guidelines"

        state_match_text = f"✓ {user_state} domicile eligible" if "tamil nadu" in user_state.lower() else "National / All-India eligible"

        # Why recommended points
        explanations = chunk.get("explanation", [])
        if not explanations:
            explanations = [
                f"Matches academic profile ({user_stage})",
                f"Available for {user_cat_display} category applicants",
                f"Official scheme by {provider}"
            ]

        card = {
            "name": name,
            "provider": provider,
            "amount": benefit,
            "eligibility_status": eligibility_status,
            "category_match": category_match_text,
            "income_match": income_match_text,
            "state_match": state_match_text,
            "portal_name": portal_info["name"],
            "portal_url": portal_info["url"],
            "documents": STANDARD_DOCUMENTS[:5],
            "why_recommended": explanations,
            "source": chunk.get("source", "scholarship_database"),
            "score": chunk.get("score", 0.0),
        }
        evaluated.append(card)

    # If evaluated is empty or has fewer than 3 entries, pull from curated catalog
    if len(evaluated) < 3:
        for sch in CURATED_SCHOLARSHIPS_CATALOG:
            norm_c_name = re.sub(r'[^a-zA-Z0-9]', '', sch["name"].lower())
            if norm_c_name in seen_names:
                continue

            # Category check
            cat_match = False
            if "all" in sch["target_categories"] or any(tc in user_cat for tc in sch["target_categories"]):
                cat_match = True

            if not cat_match:
                continue

            # Income check
            is_income_ok = True
            if sch["max_income"] and user_income is not None:
                is_income_ok = (user_income <= sch["max_income"])

            # Base eligibility
            if is_income_ok and cat_match:
                el_status = "eligible"
            else:
                el_status = "potentially_eligible"

            card_score = 90.0 if el_status == "eligible" else 75.0
            why_recs = list(sch["why_recommended"])

            # Special condition adjustments
            s_name = sch["name"].lower()
            if "pragati" in s_name or "pudhumai penn" in s_name:
                if is_girl:
                    el_status = "eligible"
                    card_score += 10.0
                    why_recs.insert(0, "✓ Priority Eligibility: Matched for Girl Student Scheme")
            if "first graduate" in s_name:
                if is_first_graduate:
                    el_status = "eligible"
                    card_score += 10.0
                    why_recs.insert(0, "✓ Verified Match: First Graduate tuition fee exemption")
            if "tamizh pudhalvan" in s_name or "pudhumai penn" in s_name:
                if is_gov_school:
                    el_status = "eligible"
                    card_score += 10.0
                    why_recs.insert(0, "✓ Verified Match: TN Govt School Alumnus (Class 6-12)")
            if "saksham" in s_name:
                if is_specially_abled:
                    el_status = "eligible"
                    card_score += 10.0
                    why_recs.insert(0, "✓ Priority Empowerment: Specially-Abled (40%+ benchmark)")
            if "minorities" in s_name:
                if is_minority:
                    el_status = "eligible"
                    card_score += 10.0

            lim_str = f"Up to ₹{sch['max_income']/100000:.1f} Lakhs" if sch["max_income"] else "No Parental Income Limit"
            if sch["max_income"]:
                if user_income is not None:
                    if user_income <= sch["max_income"]:
                        inc_txt = f"✓ Family income ₹{int(user_income):,} within ₹{sch['max_income']/100000:.1f}L ceiling"
                    else:
                        inc_txt = f"⚠️ Income ₹{int(user_income):,} exceeds ₹{sch['max_income']/100000:.1f}L limit"
                else:
                    inc_txt = f"Ceiling: Up to ₹{sch['max_income']/100000:.1f} Lakhs per annum"
            else:
                inc_txt = "✓ No Parental Income Limit Criteria"

            cat_txt = f"{user_cat_display} (Direct Target Group ✓)" if any(tc in user_cat for tc in sch["target_categories"]) else "Open Category (Merit Cum Means)"
            st_txt = f"✓ {user_state} domicile eligible" if ("tamil nadu" in sch["states"] or "all" in sch["states"]) else "All-India Quota"

            card = {
                "name": sch["name"],
                "provider": sch["provider"],
                "amount": sch["amount"],
                "eligibility_status": el_status,
                "category_match": cat_txt,
                "income_match": inc_txt,
                "state_match": st_txt,
                "portal_name": sch["portal_name"],
                "portal_url": sch["portal_url"],
                "documents": sch["documents"][:5],
                "why_recommended": why_recs[:4],
                "source": "verified_scholarship_catalog",
                "score": card_score,
            }
            evaluated.append(card)
            seen_names.add(norm_c_name)

    # Sort so eligible comes first, followed by potentially eligible
    status_order = {"eligible": 0, "potentially_eligible": 1, "needs_verification": 2, "not_eligible": 3}
    evaluated.sort(key=lambda c: (status_order.get(c["eligibility_status"], 4), -c["score"]))

    return evaluated

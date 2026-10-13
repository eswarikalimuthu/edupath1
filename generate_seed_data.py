import os
import pandas as pd

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

def generate_colleges():
    colleges_data = [
        {
            "Institute Name": "Indian Institute of Technology Madras (IITM)",
            "State": "Tamil Nadu",
            "NIRF Rank": "1",
            "Affiliation": "IIT Council",
            "Seat Count": "Approx 1200 seats",
            "Hostel Availability": "Yes (Separate boys and girls hostels)",
            "Approximate Annual Tuition Fee Range": "Rs. 2,00,000 - 2,50,000 (Tuition fee waivers exist for SC/ST and economically weaker students)",
            "Approximate Hostel Fee Range": "Rs. 40,000 - 80,000 per year",
            "Approximate One-time Fees": "Rs. 20,000",
            "Description": "Premier public technical and research university in Chennai, offering undergraduate and postgraduate programs in Engineering (Computer Science, Robotics, Electrical, Mechanical), Physics, Chemistry, and Humanities. Highly competitive JEE Advanced entry.",
            "Source": "National Institutional Ranking Framework (NIRF) 2025"
        },
        {
            "Institute Name": "Indian Institute of Science (IISc) Bangalore",
            "State": "Karnataka",
            "NIRF Rank": "2",
            "Affiliation": "UGC Deemed University",
            "Seat Count": "Approx 500 seats",
            "Hostel Availability": "Yes",
            "Approximate Annual Tuition Fee Range": "Rs. 30,000 - 50,000",
            "Approximate Hostel Fee Range": "Rs. 30,000 - 50,000 per year",
            "Approximate One-time Fees": "Rs. 15,000",
            "Description": "Premier scientific research and higher education institution in Bengaluru, offering Bachelor of Science (B.Sc Research) and engineering programs in computer science, robotics, aerospace, and basic sciences (physics, chemistry, biology, mathematics). Entry via JEE/NEET/IISER aptitude tests.",
            "Source": "IISc Admissions Guide 2025"
        },
        {
            "Institute Name": "Indian Institute of Technology Bombay (IITB)",
            "State": "Maharashtra",
            "NIRF Rank": "3",
            "Affiliation": "IIT Council",
            "Seat Count": "Approx 1300 seats",
            "Hostel Availability": "Yes",
            "Approximate Annual Tuition Fee Range": "Rs. 2,20,000 - 2,60,000",
            "Approximate Hostel Fee Range": "Rs. 45,000 - 90,000 per year",
            "Approximate One-time Fees": "Rs. 25,000",
            "Description": "Leading national engineering and sciences institute in Mumbai. Renowned for its Computer Science, Electrical Engineering, Mechanical Engineering, and Aerospace engineering programs, as well as its active entrepreneurship cell and robotics labs.",
            "Source": "IIT Bombay Admissions 2025"
        },
        {
            "Institute Name": "Loyola College Chennai",
            "State": "Tamil Nadu",
            "NIRF Rank": "7 (College category)",
            "Affiliation": "Autonomous, affiliated to Madras University",
            "Seat Count": "Approx 2500 seats",
            "Hostel Availability": "Yes",
            "Approximate Annual Tuition Fee Range": "Rs. 15,000 - 45,000 (Aided courses are highly subsidized, self-financed courses have a slightly higher range)",
            "Approximate Hostel Fee Range": "Rs. 60,000 - 80,000 per year",
            "Approximate One-time Fees": "Rs. 5,000",
            "Description": "Prestigious autonomous institution in Chennai, offering undergraduate courses in Arts, Science, and Commerce, including B.Com, B.Sc Computer Science, B.Sc Mathematics, B.Sc Physics, B.A. Economics, and English Literature.",
            "Source": "Loyola College Prospectus 2025"
        },
        {
            "Institute Name": "Shri Ram College of Commerce (SRCC) Delhi",
            "State": "Delhi",
            "NIRF Rank": "11 (College category)",
            "Affiliation": "University of Delhi (DU)",
            "Seat Count": "Approx 1000 seats",
            "Hostel Availability": "Yes",
            "Approximate Annual Tuition Fee Range": "Rs. 30,000 - 45,000",
            "Approximate Hostel Fee Range": "Rs. 80,000 - 1,20,000 per year",
            "Approximate One-time Fees": "Rs. 10,000",
            "Description": "The premier college for commerce and economics education in India, offering highly sought-after B.Com (Honours) and B.A. Economics (Honours) courses. Prepares students for careers in finance, economics, and corporate planning.",
            "Source": "DU SRCC Official Portal"
        },
        {
            "Institute Name": "Christian Medical College (CMC) Vellore",
            "State": "Tamil Nadu",
            "NIRF Rank": "3 (Medical category)",
            "Affiliation": "Tamil Nadu Dr. M.G.R. Medical University",
            "Seat Count": "Approx 100 MBBS seats",
            "Hostel Availability": "Yes",
            "Approximate Annual Tuition Fee Range": "Rs. 50,000 - 1,50,000",
            "Approximate Hostel Fee Range": "Rs. 35,000 - 60,000 per year",
            "Approximate One-time Fees": "Rs. 12,000",
            "Description": "Highly selective medical and research college in Vellore, offering MBBS, B.Sc Nursing, and allied health sciences. Entry is via NEET, known for low fee structures and high clinical exposure.",
            "Source": "CMC Vellore Admission Bulletin 2025"
        },
        {
            "Institute Name": "BITS Pilani",
            "State": "Rajasthan",
            "NIRF Rank": "25 (University category)",
            "Affiliation": "Deemed University",
            "Seat Count": "Approx 1000 seats (Pilani campus)",
            "Hostel Availability": "Yes (Fully residential)",
            "Approximate Annual Tuition Fee Range": "Rs. 4,50,000 - 5,50,000",
            "Approximate Hostel Fee Range": "Rs. 80,000 - 1,40,000 per year",
            "Approximate One-time Fees": "Rs. 45,000",
            "Description": "Premier private technical university in Pilani, Rajasthan. Offers B.E. in Computer Science, Electronics & Communication, Mechanical, and dual-degree M.Sc in Sciences. Admits students via the BITSAT entrance exam.",
            "Source": "BITS Pilani Admission Brochure 2025"
        },
        {
            "Institute Name": "National Institute of Technology (NIT) Trichy",
            "State": "Tamil Nadu",
            "NIRF Rank": "9 (Engineering category)",
            "Affiliation": "NIT Council",
            "Seat Count": "Approx 900 seats",
            "Hostel Availability": "Yes",
            "Approximate Annual Tuition Fee Range": "Rs. 1,25,000 - 1,50,000 (Substantial fee waivers available for SC/ST and students with low parental income)",
            "Approximate Hostel Fee Range": "Rs. 35,000 - 70,000 per year",
            "Approximate One-time Fees": "Rs. 15,000",
            "Description": "Top-ranked National Institute of Technology, located in Trichy, Tamil Nadu. Offers B.Tech in Computer Science, Electronics, Electrical, Mechanical, and Civil Engineering. Admits students via JEE Main counseling (JoSAA).",
            "Source": "JoSAA Information Brochure 2025"
        },
        {
            "Institute Name": "Madras Christian College (MCC) Chennai",
            "State": "Tamil Nadu",
            "NIRF Rank": "16 (College category)",
            "Affiliation": "Autonomous, affiliated to Madras University",
            "Seat Count": "Approx 2000 seats",
            "Hostel Availability": "Yes",
            "Approximate Annual Tuition Fee Range": "Rs. 12,000 - 35,000",
            "Approximate Hostel Fee Range": "Rs. 45,000 - 60,000 per year",
            "Approximate One-time Fees": "Rs. 5,000",
            "Description": "Prestigious and historic college in Tambaram, Chennai. Offers BA, B.Sc, B.Com, and postgraduate courses in Humanities, Commerce, and Sciences (Physics, Chemistry, Zoology, Botany, Computer Science).",
            "Source": "MCC Chennai Prospectus 2025"
        },
        {
            "Institute Name": "Madras Medical College (MMC) Chennai",
            "State": "Tamil Nadu",
            "NIRF Rank": "12 (Medical category)",
            "Affiliation": "Tamil Nadu Dr. M.G.R. Medical University",
            "Seat Count": "Approx 250 MBBS seats",
            "Hostel Availability": "Yes",
            "Approximate Annual Tuition Fee Range": "Rs. 15,000 - 20,000 (Highly subsidized government fee structure)",
            "Approximate Hostel Fee Range": "Rs. 15,000 - 30,000 per year",
            "Approximate One-time Fees": "Rs. 5,000",
            "Description": "One of the oldest and most prestigious medical colleges in India, located in Chennai. Offers MBBS, BDS, Bachelor of Pharmacy, and Nursing. Entry is via NEET TN State Counseling.",
            "Source": "TN Medical Selection Committee Prospectus"
        },
        {
            "Institute Name": "PSG College of Technology Coimbatore",
            "State": "Tamil Nadu",
            "NIRF Rank": "67 (Engineering category)",
            "Affiliation": "Autonomous, affiliated to Anna University",
            "Seat Count": "Approx 1100 seats",
            "Hostel Availability": "Yes",
            "Approximate Annual Tuition Fee Range": "Rs. 50,000 - 1,20,000 (Aided courses have much lower tuition fee range than self-financed)",
            "Approximate Hostel Fee Range": "Rs. 50,000 - 80,000 per year",
            "Approximate One-time Fees": "Rs. 10,000",
            "Description": "Renowned private-aided engineering college in Coimbatore. Offers undergraduate engineering courses in Computer Science, Robotics, Information Technology, Mechanical, and Textile Engineering. Admissions via TNEA counseling.",
            "Source": "Anna University Counseling Portal 2025"
        },
        {
            "Institute Name": "Stella Maris College Chennai",
            "State": "Tamil Nadu",
            "NIRF Rank": "37 (College category)",
            "Affiliation": "Autonomous, affiliated to Madras University",
            "Seat Count": "Approx 1800 seats",
            "Hostel Availability": "Yes (For outstation students)",
            "Approximate Annual Tuition Fee Range": "Rs. 15,000 - 40,000",
            "Approximate Hostel Fee Range": "Rs. 55,000 - 75,000 per year",
            "Approximate One-time Fees": "Rs. 4,000",
            "Description": "Leading autonomous women's college in Chennai, offering undergraduate programs in Arts (English, Economics, Sociology), Commerce (B.Com, B.Com Hons), and Sciences (Mathematics, Physics, Chemistry, Computer Science).",
            "Source": "Stella Maris Admission Guide 2025"
        }
    ]
    df = pd.DataFrame(colleges_data)
    dest_path = os.path.join(DATA_DIR, "course", "national_colleges_and_fees.csv")
    df.to_csv(dest_path, index=False)
    print(f"Generated {len(df)} colleges and fees records in {dest_path}")

def generate_schemes():
    schemes_data = [
        {
            "Scheme Name": "Pudhumai Penn Scheme (Moovalur Ramamirtham Ammaiyar Higher Education Assurance Scheme)",
            "Eligibility Criteria": "Girls who studied in Tamil Nadu Government schools from classes 6 to 12. Must be enrolled in a recognized undergraduate degree, diploma, or ITI course.",
            "Benefit Summary": "Monthly assistance of Rs. 1,000 directly credited to the student's bank account till they complete their higher education.",
            "Issuing Authority": "Department of Social Welfare and Women Empowerment, Government of Tamil Nadu",
            "Source": "Tamil Nadu Social Welfare Portal 2025"
        },
        {
            "Scheme Name": "Tamil Pudhalvan Scheme",
            "Eligibility Criteria": "Boys who studied in Tamil Nadu Government schools from classes 6 to 12. Must be pursuing higher education in recognized colleges, engineering, polytechnic, or ITI institutions.",
            "Benefit Summary": "Monthly financial aid of Rs. 1,000 deposited directly to the student's bank account to cover books, transport, and board fees.",
            "Issuing Authority": "Department of Social Welfare, Government of Tamil Nadu",
            "Source": "TN Government Gazette 2025"
        },
        {
            "Scheme Name": "First Generation Graduate Tuition Fee Concession",
            "Eligibility Criteria": "Students pursuing engineering or professional courses in Tamil Nadu via TNEA state counseling. There must be no other graduates in the student's family.",
            "Benefit Summary": "Full tuition fee waiver/concession (approx. Rs. 20,000 - 27,500 per year for Government quota seats in engineering colleges).",
            "Issuing Authority": "Directorate of Technical Education (DoTE), Government of Tamil Nadu",
            "Source": "TNEA Admission Guidelines"
        },
        {
            "Scheme Name": "Post Matric Scholarship Scheme for SC/ST Students",
            "Eligibility Criteria": "SC/ST students pursuing post-matriculation courses (Grade 11, 12, diploma, degree, professional engineering or medical courses). Annual family income must be below Rs. 2.5 Lakhs.",
            "Benefit Summary": "100% reimbursement of compulsory non-refundable fees (including tuition fee) and monthly maintenance allowance depending on course type.",
            "Issuing Authority": "Ministry of Social Justice and Empowerment, Government of India & ADW Department, Government of Tamil Nadu",
            "Source": "National Scholarship Portal (NSP)"
        },
        {
            "Scheme Name": "PM YASASVI Scheme (PM Young achievers Scholarship Award Scheme for Vibrant India)",
            "Eligibility Criteria": "Students belonging to OBC, EBC, and DNT categories studying in classes 9 to 12 or pursuing higher education. Annual parental income must be below Rs. 2.5 Lakhs.",
            "Benefit Summary": "Scholarship ranges from Rs. 75,000 to Rs. 1,25,000 per year covering tuition and hostel fees for top-class schools/colleges.",
            "Issuing Authority": "Ministry of Social Justice and Empowerment, Government of India",
            "Source": "National Testing Agency (NTA) & NSP Portal"
        },
        {
            "Scheme Name": "Tamil Nadu Government Free Bus Pass Scheme",
            "Eligibility Criteria": "All students studying in Government schools, Government colleges, polytechnics, and ITIs in Tamil Nadu.",
            "Benefit Summary": "Free bus passes for daily travel between residence and institution on State Transport Corporation (TNSTC) buses.",
            "Issuing Authority": "State Transport Department, Government of Tamil Nadu",
            "Source": "TN State Transport Department circulars"
        },
        {
            "Scheme Name": "Government Free Hostel Facility Scheme for BC/MBC and SC/ST Students",
            "Eligibility Criteria": "Students from backward, most backward, or SC/ST communities pursuing school or college education. The distance between home and institution must be more than 8 km (relaxed for girls). Family income must be under Rs. 2 Lakhs.",
            "Benefit Summary": "Free boarding, lodging, and meals in welfare hostels run by the government close to academic institutions.",
            "Issuing Authority": "BC, MBC & Minorities Welfare Department & Adi Dravidar Welfare Department, Government of Tamil Nadu",
            "Source": "TN BC/MBC Welfare Department Guidelines"
        }
    ]
    df = pd.DataFrame(schemes_data)
    dest_path = os.path.join(DATA_DIR, "scheme", "central_and_state_schemes.csv")
    df.to_csv(dest_path, index=False)
    print(f"Generated {len(df)} welfare schemes records in {dest_path}")

def generate_scholarships():
    scholarships_data = [
        {
            "Scholarship Name": "PM Uchchatar Shiksha Protsahan (PM-USP) Central Sector Scheme of Scholarship (CSSS)",
            "Eligibility": "Students who are above the 80th percentile of successful candidates in Class 12 exams. Pursuing regular courses (not distance). Annual family income under Rs. 4.5 Lakhs.",
            "Amount": "Rs. 12,000 per year for graduation (first three years) and Rs. 20,000 per year for post-graduation/professional courses.",
            "Application Window": "July to October annually (via National Scholarship Portal)",
            "Type": "Merit-cum-Means based",
            "Source": "Department of Higher Education, Ministry of Education, Government of India"
        },
        {
            "Scholarship Name": "AICTE Pragati Scholarship Scheme for Girls",
            "Eligibility": "Female students admitted to the first year of degree/diploma technical courses in AICTE-approved colleges. Max 2 girls per family. Family income under Rs. 8 Lakhs.",
            "Amount": "Rs. 50,000 per year as lump sum to cover tuition fees, computer purchase, books, and stationeries.",
            "Application Window": "September to November annually",
            "Type": "Need-based/Category (Female only)",
            "Source": "All India Council for Technical Education (AICTE)"
        },
        {
            "Scholarship Name": "DST INSPIRE Scholarship for Higher Education (SHE)",
            "Eligibility": "Students in the top 1% in Class 12 state/central board exams, pursuing natural/basic sciences (B.Sc, B.Sc Hons, Integrated M.Sc). Age limit 17-22 years.",
            "Amount": "Rs. 80,000 per year (Rs. 60,000 cash scholarship + Rs. 20,000 mentorship/internship grant).",
            "Application Window": "November to December annually",
            "Type": "Merit-based science scholarship",
            "Source": "Department of Science and Technology (DST), Government of India"
        },
        {
            "Scholarship Name": "HDFC Bank Parivartan's ECSS Scholarship",
            "Eligibility": "Indian students studying in Class 6 to 12, diploma, undergraduate (general/professional), or postgraduate courses. Family income must be under Rs. 2.5 Lakhs. Merit background required (min 55% marks).",
            "Amount": "Ranges from Rs. 15,000 to Rs. 75,000 per year depending on course level.",
            "Application Window": "May to July annually",
            "Type": "Private need-based CSR scholarship",
            "Source": "HDFC Bank CSR Board"
        },
        {
            "Scholarship Name": "LIC Golden Jubilee Scholarship Scheme",
            "Eligibility": "Students who passed Class 12 or equivalent with at least 60% marks and are pursuing higher education in fields of medicine, engineering, graduation, diploma. Family income under Rs. 2.5 Lakhs.",
            "Amount": "Rs. 20,000 per year for general degree/diploma courses, and Rs. 40,000 per year for medicine/engineering.",
            "Application Window": "August to October annually",
            "Type": "Need-based commercial scholarship",
            "Source": "Life Insurance Corporation of India (LIC) Golden Jubilee Foundation"
        },
        {
            "Scholarship Name": "Tata Capital Pankh Scholarship",
            "Eligibility": "Students studying in undergraduate general degree or professional courses (engineering, medicine, law). Parental income must not exceed Rs. 4 Lakhs. Minimum 60% in Class 12.",
            "Amount": "Up to 80% of tuition fees or Rs. 20,000 to Rs. 50,000 per year.",
            "Application Window": "September to November annually",
            "Type": "Need-based CSR scholarship",
            "Source": "Tata Capital CSR Board"
        },
        {
            "Scholarship Name": "Foundation for Excellence (FFE) Scholarship",
            "Eligibility": "Students entering first year of B.E./B.Tech, MBBS, or 5-year Integrated M.Tech. Based on JEE Main rank or NEET score. Family income must be under Rs. 3 Lakhs.",
            "Amount": "Rs. 40,000 - 50,000 per year along with active corporate mentorship programs.",
            "Application Window": "September to December annually",
            "Type": "Private merit-cum-means professional scholarship",
            "Source": "Foundation for Excellence (FFE) Trust"
        },
        {
            "Scholarship Name": "Sitaram Jindal Foundation Scholarship",
            "Eligibility": "Students studying in Class 11, 12, ITI, Diploma, Graduation, Postgraduate courses. Minimum eligibility marks range from 55% to 75% depending on state/category. Income limit under Rs. 2.5 Lakhs.",
            "Amount": "Rs. 500 to Rs. 3,200 per month depending on the level of course and residential status.",
            "Application Window": "Open throughout the year (Physical application submissions)",
            "Type": "Need-based educational scholarship",
            "Source": "Sitaram Jindal Foundation Trust"
        }
    ]
    df = pd.DataFrame(scholarships_data)
    dest_path = os.path.join(DATA_DIR, "scholarship", "national_scholarships.csv")
    df.to_csv(dest_path, index=False)
    print(f"Generated {len(df)} scholarships records in {dest_path}")

if __name__ == "__main__":
    generate_colleges()
    generate_schemes()
    generate_scholarships()
    print("\nCSV generation complete.")

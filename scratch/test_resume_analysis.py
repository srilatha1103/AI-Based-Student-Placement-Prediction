import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import resume_analyzer
import database

# Test text parsing
sample_resume_text = """
Rahul Sharma
Email: rahul.sharma@example.com | Phone: +91 9876543210
LinkedIn: linkedin.com/in/rahulsharma | GitHub: github.com/rahulsharma

SUMMARY
Enthusiastic Computer Science Student with expertise in Python, React, Flask, Data Structures, and SQL. 

EDUCATION
Bachelor of Technology in Computer Science and Engineering
ABC Institute of Technology, CGPA: 8.45/10 (2022 - 2026)

TECHNICAL SKILLS
- Programming Languages: Python, Java, C++, JavaScript, SQL, HTML, CSS
- Frameworks & Libraries: React, Node.js, Flask, Django, Pandas, NumPy, Bootstrap
- Databases: MySQL, PostgreSQL, MongoDB, SQLite
- Tools & Cloud: Git, GitHub, Docker, AWS, VSCode, Postman

ACADEMIC PROJECTS
1. AI Student Placement Prediction System
   - Built an end-to-end Flask application using Random Forest Machine Learning.
   - Designed interactive Bootstrap dashboards and SQLite database integration.
2. E-Commerce Platform with React & Node.js
   - Implemented JWT authentication, Stripe payment gateway, and MongoDB backend.

CERTIFICATIONS
- AWS Certified Cloud Practitioner (2025)
- Oracle Certified Associate, Java SE Programmer

WORK EXPERIENCE / INTERNSHIP
Software Engineering Intern - Tech Solutions Pvt Ltd (3 Months)
- Developed RESTful APIs using Python Flask and optimized MySQL database queries.
"""

print("[1/4] Testing NLP Parsing Engine...")
parsed = resume_analyzer.parse_resume_text(sample_resume_text)
print("Parsed Name:", parsed['name'])
print("Parsed Email:", parsed['email'])
print("Parsed Phone:", parsed['phone'])
print("Extracted Skills:", parsed['skills'])

print("\n[2/4] Testing AI Resume Scoring Engine...")
score_res = resume_analyzer.calculate_ai_resume_score(parsed)
print("Total Score:", score_res['total_score'], "/ 100")
print("Breakdown:", score_res['breakdown'])

print("\n[3/4] Testing Skill Gap Analysis & Job Matching...")
gap_res = resume_analyzer.analyze_skill_gap(parsed['skills'])
print("Missing Skills:", gap_res['missing_skills'])
job_recs = resume_analyzer.recommend_job_roles(parsed)
print("Top Job Match:", job_recs[0]['title'], "-", job_recs[0]['match_score'], "%")

print("\n[4/4] Testing PDF Report Generation...")
os.makedirs('static/reports', exist_ok=True)
dummy_analysis = {
    'id': 999,
    'name': parsed['name'],
    'original_filename': 'Rahul_Sharma_Resume.pdf',
    'file_type': 'PDF',
    'email': parsed['email'],
    'phone': parsed['phone'],
    'skills_extracted': parsed['skills'],
    'strengths': score_res['strengths'],
    'improvements': score_res['improvements'],
    'resume_score': score_res['total_score'],
    'placement_probability': 88.5,
    'placement_status': 'High Chance',
    'skill_gap_data': gap_res,
    'job_recommendations': job_recs,
    'roadmap_data': resume_analyzer.generate_learning_roadmap(gap_res)
}
pdf_output = resume_analyzer.generate_resume_pdf_report(dummy_analysis, 'static/reports/test_report.pdf')
print("PDF Report generated successfully at:", pdf_output)

# Comprehensive Academic Project Report

**Project Title:** AI-Based Student Placement Prediction System with Company Recruitment Portal & Email Notification Engine  
**Degree & Domain:** Bachelor of Technology / Computer Science & Engineering (Artificial Intelligence & Machine Learning)  
**Date:** July 2026  

---

## Abstract
The transition from academic engineering education to industry employment represents a critical phase for students and institutional placement cells. Traditional placement procedures rely heavily on manual record-keeping, static CGPA cutoffs, and fragmented communication, leaving students unaware of technical skill gaps and recruiters overwhelmed by unscreened applicant pools. 

This project presents an end-to-end **AI-Based Student Placement Prediction System** integrating Machine Learning (Random Forest Classifier), Natural Language Processing (NLP Resume Analyzer), Automated Skill Gap Roadmap Generation, AI-Driven Mock Interviews, a Recruiter Company Portal with Automated Candidate Matching, and a Multi-Threaded Email and Notification Engine. The machine learning model achieves an accuracy of **85.67%** in predicting student placement probability based on 13 multidimensional academic, technical, and soft-skill parameters.

---

## 1. Introduction
Campus recruitment is the primary conduit for fresh engineering graduates entering the technology workforce. Institutional Training and Placement Officers (TPOs) manage hundreds of student profiles, company criteria, interview schedules, and placement analytics. Concurrently, students require personalized guidance to understand their likelihood of placement and actionable recommendations to rectify technical deficiencies before campus recruitment drives commence.

---

## 2. Problem Statement
Existing placement management methodologies present key limitations:
1. **Lack of Predictive Insights:** Students lack data-driven feedback regarding their placement probability prior to drive registration.
2. **Manual Candidate Screening:** Recruiters receive hundreds of unranked applications, increasing hiring overhead.
3. **Static Skill Evaluation:** CGPA alone does not accurately reflect coding proficiency, project experience, or soft skills.
4. **Disconnected Communication:** Lack of real-time alerts leads to missed interview invitations and delayed feedback loops.

---

## 3. Proposed System & Key Objectives
The proposed system unifies machine learning intelligence, recruiter management, candidate matching, and automated email notifications into a cohesive Flask web application:
- **ML Placement Predictor:** Evaluates 13 features (CGPA, 10th/12th marks, aptitude score, coding score, communication skills, internships, projects, backlogs, department) using a Random Forest Classifier.
- **AI Resume Analyzer:** Uses NLP regex and taxonomy parsing to score resumes (0-100), extract technical skills, highlight missing keywords, and render downloadable PDF reports.
- **AI Mock Interview Engine:** Interactive simulator offering technical (10 domains) and aptitude questions with instant keyword coverage evaluation and scorecards.
- **Company Recruitment Portal:** Enables recruiter registration, job posting management, AI-weighted candidate matching (40% Skills, 25% CGPA, 15% ML Score, 10% Intern/Projects, 10% Certs), candidate status tracking, and interview scheduling.
- **Multi-Threaded Notification & Email Engine:** Asynchronous background SMTP worker providing in-app notifications, unread badges, and HTML email dispatches.

---

## 4. System Technologies & Architecture

### Technology Stack
- **Backend Framework:** Python 3.9+, Flask Web Server, Werkzeug
- **Machine Learning & Data Processing:** Scikit-Learn, Pandas, NumPy, Joblib
- **Natural Language Processing & Parsing:** Regex, PyPDF, Python-Docx, ReportLab
- **Database Storage:** SQLite 3 with performance indexes and foreign key cascades
- **Frontend Interface:** Responsive HTML5, Vanilla CSS3, Bootstrap 5, Font Awesome 6, Chart.js

---

## 5. Machine Learning Methodology & Algorithms

### Random Forest Classifier
The core prediction engine uses an ensemble **Random Forest Classifier** (`n_estimators=150`, `max_depth=12`, `random_state=42`). 

#### Feature Engineering & Weighting
$$\text{Placement Score} = 0.30(\text{CGPA}) + 0.20(\text{Coding Score}) + 0.15(\text{Aptitude}) + 0.15(\text{Soft Skills}) + 0.10(\text{Internships}) + 0.10(\text{Certifications}) - 0.15(\text{Backlogs})$$

#### Evaluation Metrics
- **Accuracy:** 85.67%
- **Precision:** 86.40%
- **Recall:** 84.80%
- **F1-Score:** 85.59%

---

## 6. AI Candidate Matching Algorithm (Company Portal)
The company portal calculates an **AI Student-Job Match Score** ($M$) between student profile $S$ and job requirement $J$:

$$M = 0.40(S_{\text{skills}}) + 0.25(S_{\text{cgpa}}) + 0.15(S_{\text{ml\_prob}}) + 0.10(S_{\text{exp}}) + 0.10(S_{\text{cert}})$$

Candidates are automatically ranked on recruiter dashboards with visual indicators (85%+ High Match, 70-84% Good Match, 55-69% Average Match).

---

## 7. Results & Key Advantages
- **For Students:** Provides predictive placement feedback, personalized skill gap roadmaps, AI resume feedback, and mock interview practice.
- **For Recruiters:** Reduces time-to-hire by automatically ranking candidates using AI match scoring and scheduling interviews seamlessly.
- **For Placement Officers (Admins):** Centralized analytics dashboard for department trends, dataset uploads, model re-training, and email delivery monitoring.

---

## 8. Limitations & Future Scope
- **Current Limitations:** SQLite database (can be upgraded to PostgreSQL for multi-region scale); simulated SMTP fallback mode when email credentials are unspecified.
- **Future Scope:** Integration with LinkedIn API for auto-profile synchronization, AI voice-to-text audio evaluation for mock interviews, and automated WhatsApp alert integrations.

---

## 9. Conclusion
The AI-Based Student Placement Prediction System successfully bridge the gap between academic performance and industry requirements. By combining machine learning prediction, NLP resume parsing, recruiter candidate matching, and multi-threaded notification services, the platform optimizes institutional placement workflows and empowers engineering students.

---

## 10. References
1. Breiman, L. (2001). Random Forests. *Machine Learning*, 45(1), 5-32.
2. Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825-2830.
3. Grinberg, M. (2018). *Flask Web Development: Developing Web Applications with Python*. O'Reilly Media.

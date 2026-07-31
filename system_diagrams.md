# System Diagrams & Architecture Documentation

This document contains full UML diagrams, Entity-Relationship diagrams, Data Flow diagrams (DFD), and System Architecture specifications rendered using GitHub Markdown Mermaid syntax.

---

## 1. System Architecture Diagram

```mermaid
graph TD
    subgraph Clients["User Tier (Web Browsers)"]
        S[Student Portal Client]
        C[Company Recruiter Portal Client]
        A[Admin Dashboard Client]
    end

    subgraph Server["Flask Web Application Server"]
        Router[Flask App & Blueprint Routing]
        Auth[Session Auth & Security Middleware]
        
        subgraph Subsystems["Core Engine Subsystems"]
            ML[Random Forest ML Prediction Engine]
            NLP[AI Resume Analyzer Engine]
            Mock[AI Mock Interview Engine]
            Match[AI Candidate Matching Engine]
            Notif[Asynchronous Notification & Email Service]
        end
    end

    subgraph Data["Data & Storage Tier"]
        DB[(SQLite Production Database)]
        Models[(Serialized ML Models .pkl)]
        Files[(File Uploads Storage)]
    end

    S --> Router
    C --> Router
    A --> Router

    Router --> Auth
    Auth --> Subsystems

    ML --> Models
    Subsystems --> DB
    NLP --> Files
    Notif --> DB
```

---

## 2. Use Case Diagram

```mermaid
usecaseDiagram
    actor Student
    actor Recruiter
    actor Admin

    package "AI Student Placement Prediction System" {
        usecase "Register & Log In" as UC1
        usecase "Calculate Placement Probability (ML)" as UC2
        usecase "Analyze Resume (NLP)" as UC3
        usecase "Practice AI Mock Interview" as UC4
        usecase "Explore Campus Jobs & Apply" as UC5
        usecase "Post & Manage Jobs" as UC6
        usecase "Run AI Candidate Matching" as UC7
        usecase "Schedule Candidate Interview" as UC8
        usecase "Manage Students & Train Model" as UC9
        usecase "View In-App & Email Notifications" as UC10
    }

    Student --> UC1
    Student --> UC2
    Student --> UC3
    Student --> UC4
    Student --> UC5
    Student --> UC10

    Recruiter --> UC1
    Recruiter --> UC6
    Recruiter --> UC7
    Recruiter --> UC8
    Recruiter --> UC10

    Admin --> UC1
    Admin --> UC9
    Admin --> UC10
```

---

## 3. Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    STUDENT_USERS ||--o{ JOB_APPLICATIONS : submits
    STUDENT_USERS ||--o{ PREDICTION_HISTORY : generates
    STUDENT_USERS ||--o{ MOCK_INTERVIEWS : completes
    STUDENT_USERS ||--o{ NOTIFICATIONS : receives

    COMPANIES ||--o{ JOBS : posts
    COMPANIES ||--o{ JOB_APPLICATIONS : reviews
    COMPANIES ||--o{ INTERVIEWS : schedules

    JOBS ||--o{ JOB_APPLICATIONS : contains
    JOB_APPLICATIONS ||--o{ INTERVIEWS : triggers

    STUDENT_USERS {
        int id PK
        string register_number UK
        string email UK
        string student_name
        string department
        float cgpa
        int aptitude_score
        int coding_score
        string skills_list
    }

    COMPANIES {
        int id PK
        string company_name
        string email UK
        string industry
        string location
    }

    JOBS {
        int id PK
        int company_id FK
        string title
        string required_skills
        float min_cgpa
        string salary_package
        date deadline
    }

    JOB_APPLICATIONS {
        int id PK
        int job_id FK
        int company_id FK
        string student_reg FK
        float match_score
        string status
    }

    INTERVIEWS {
        int id PK
        int application_id FK
        string interview_type
        date interview_date
        time interview_time
        string status
    }

    NOTIFICATIONS {
        int id PK
        string user_type
        string user_id
        string title
        string message
        int is_read
    }
```

---

## 4. Class Diagram

```mermaid
classDiagram
    class StudentUser {
        +string register_number
        +string email
        +string student_name
        +float cgpa
        +int coding_score
        +string skills_list
        +register()
        +login()
        +get_profile()
    }

    class CompanyRecruiter {
        +int id
        +string company_name
        +string email
        +string industry
        +create_job_posting()
        +run_ai_candidate_matching()
        +schedule_interview()
    }

    class JobPosting {
        +int id
        +string title
        +string required_skills
        +float min_cgpa
        +string salary_package
        +string status
    }

    class PlacementMLEngine {
        +RandomForestClassifier model
        +StandardScaler scaler
        +predict_placement(features)
        +train_and_export_model()
    }

    class CandidateMatchingEngine {
        +calculate_student_job_match(student, job)
        +rank_candidates(job_id)
    }

    class NotificationService {
        +send_async_email(recipient, subject, html_body)
        +notify_student_registration()
        +notify_interview_invite()
    }

    StudentUser "1" -- "0..*" JobPosting : applies
    CompanyRecruiter "1" -- "1..*" JobPosting : owns
    CandidateMatchingEngine ..> StudentUser : evaluates
    CandidateMatchingEngine ..> JobPosting : evaluates
    PlacementMLEngine ..> StudentUser : predicts
    NotificationService ..> StudentUser : notifies
```

---

## 5. Sequence Diagram (Candidate Application & Interview Scheduling)

```mermaid
sequenceDiagram
    autonumber
    actor Student
    participant StudentPortal as Student Portal
    participant MatchingEngine as AI Matching Engine
    participant CompanyPortal as Company Portal
    participant NotifService as Notification Service
    actor Recruiter

    Student->>StudentPortal: Browse Campus Jobs
    StudentPortal->>MatchingEngine: Calculate Job Match %
    MatchingEngine-->>StudentPortal: Return Match Score (88%)
    Student->>StudentPortal: Click "Apply Now"
    StudentPortal->>NotifService: Dispatch Application Confirmation
    
    Recruiter->>CompanyPortal: View Applicants Pool
    CompanyPortal-->>Recruiter: Display Candidate Rank #1 (Rahul Sharma - 88%)
    Recruiter->>CompanyPortal: Click "Schedule Interview"
    CompanyPortal->>NotifService: Dispatch Interview Email & Notification
    NotifService-->>Student: Deliver Live Bell Alert & Email Invitation
```

---

## 6. Activity Diagram (AI Placement Prediction Flow)

```mermaid
stateDiagram-v2
    [*] --> InputProfile: Student Inputs CGPA, Coding & Aptitude Scores
    InputProfile --> ValidateData: Server Validates Input Numerical Bounds
    
    state ValidateData {
        [*] --> CheckCGPA: Verify CGPA between 0 and 10
        CheckCGPA --> CheckScores: Verify Coding/Aptitude between 0 and 100
    }

    ValidateData --> LoadArtifacts: Load Serialized Random Forest Model & Scaler
    LoadArtifacts --> ModelInference: Model Calculates Probability Score
    
    state ModelInference {
        [*] --> HighProbability: Prob >= 70% (High Placement Chance)
        [*] --> LowProbability: Prob < 70% (Up-skilling Needed)
    }

    ModelInference --> GenerateReport: Generate Skill Gap & Personal Career Roadmap
    GenerateReport --> SendNotification: Store Notification & Email Dispatch
    SendNotification --> [*]: Render Results Dashboard
```

---

## 7. Data Flow Diagram (DFD Level 0 & Level 1)

### DFD Level 0 (Context Diagram)
```mermaid
graph LR
    Student[Student User] <--> System((AI Student Placement System))
    Recruiter[Company Recruiter] <--> System
    Admin[System Administrator] <--> System
```

### DFD Level 1 (Detailed Data Flow)
```mermaid
graph TD
    Student[Student User] -->|Registration & Metrics| P1(1.0 Auth & Profile Mgmt)
    P1 -->|Store User| D1[(Student DB)]

    Student -->|Input Scores| P2(2.0 ML Placement Predictor)
    D1 -->|Fetch Profile| P2
    P2 -->|Save Result| D2[(Prediction History DB)]
    P2 -->|Output Probability| Student

    Recruiter[Company Recruiter] -->|Post Job Details| P3(3.0 Job Posting Mgmt)
    P3 -->|Store Job| D3[(Jobs DB)]

    P4(4.0 AI Candidate Matcher) -->|Fetch Job Req| D3
    P4 -->|Fetch Student Profile| D1
    P4 -->|Candidate Ranks| Recruiter

    Recruiter -->|Schedule Interview| P5(5.0 Interview & Notification Engine)
    P5 -->|Update Application| D4[(Applications & Interviews DB)]
    P5 -->|Live Alert & Email| Student
```

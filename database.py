import os
import sqlite3
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

DB_DIR = 'instance'
DB_PATH = os.path.join(DB_DIR, 'placement.db')

def get_db_connection():
    """Create and return a database connection with Row factory."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables and seed initial data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Admins Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            name TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Ensure email column exists if table existed previously without it
    cursor.execute("PRAGMA table_info(admins)")
    admin_cols = [row['name'] for row in cursor.fetchall()]
    if 'email' not in admin_cols:
        try:
            cursor.execute("ALTER TABLE admins ADD COLUMN email TEXT")
            conn.commit()
        except Exception:
            pass



    # 2. Students Table (Master List used for ML Training & Admin CRUD)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            register_number TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            cgpa REAL NOT NULL,
            tenth_percentage REAL DEFAULT 0.0,
            twelfth_percentage REAL DEFAULT 0.0,
            aptitude_score INTEGER DEFAULT 0,
            coding_score INTEGER DEFAULT 0,
            communication_skill TEXT DEFAULT 'Average',
            internship TEXT DEFAULT 'No',
            certifications INTEGER DEFAULT 0,
            projects_completed INTEGER DEFAULT 0,
            backlogs INTEGER DEFAULT 0,
            placement_status INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Student Users Table (Student Portal Auth & Extended Profile)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            register_number TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            student_name TEXT NOT NULL,
            department TEXT NOT NULL,
            cgpa REAL DEFAULT 7.5,
            tenth_percentage REAL DEFAULT 75.0,
            twelfth_percentage REAL DEFAULT 75.0,
            aptitude_score INTEGER DEFAULT 70,
            coding_score INTEGER DEFAULT 70,
            communication_skill TEXT DEFAULT 'Good',
            internship TEXT DEFAULT 'Yes',
            certifications_count INTEGER DEFAULT 1,
            projects_count INTEGER DEFAULT 2,
            backlogs INTEGER DEFAULT 0,
            profile_photo TEXT DEFAULT 'default_avatar.png',
            skills_list TEXT DEFAULT 'Python, SQL, HTML/CSS, Data Structures',
            certifications_details TEXT DEFAULT 'AWS Certified Cloud Practitioner',
            internship_details TEXT DEFAULT 'Web Development Intern at Tech Solutions (3 Months)',
            project_details TEXT DEFAULT 'AI Student Placement Prediction System using Flask & Random Forest',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 4. Student Notifications Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            register_number TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT DEFAULT 'info',
            is_read INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 5. Prediction History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prediction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            register_number TEXT NOT NULL,
            department TEXT,
            cgpa REAL,
            prediction INTEGER NOT NULL,
            probability REAL NOT NULL,
            status TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 6. Dataset History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dataset_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            row_count INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active',
            uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 7. Model Metadata Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            algorithm TEXT DEFAULT 'Random Forest',
            accuracy REAL,
            precision REAL,
            recall REAL,
            f1_score REAL,
            total_samples INTEGER,
            trained_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 8. Resume Analyses Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            register_number TEXT,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            name TEXT,
            email TEXT,
            phone TEXT,
            skills_extracted TEXT,
            education_extracted TEXT,
            projects_extracted TEXT,
            internships_extracted TEXT,
            certifications_extracted TEXT,
            experience_extracted TEXT,
            resume_score INTEGER DEFAULT 0,
            score_breakdown TEXT,
            strengths TEXT,
            weaknesses TEXT,
            improvements TEXT,
            skill_gap_data TEXT,
            job_recommendations TEXT,
            roadmap_data TEXT,
            placement_probability REAL DEFAULT 0.0,
            placement_status TEXT DEFAULT 'Unplaced',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 9. Mock Interviews Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mock_interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            register_number TEXT NOT NULL,
            category TEXT NOT NULL,
            domain TEXT NOT NULL,
            total_questions INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            total_score REAL DEFAULT 0.0,
            time_taken_seconds INTEGER DEFAULT 0,
            strengths TEXT,
            weaknesses TEXT,
            feedback TEXT,
            recommended_topics TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 10. Mock Interview Answers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mock_interview_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            user_answer TEXT,
            model_answer TEXT,
            score REAL DEFAULT 0.0,
            is_correct INTEGER DEFAULT 0,
            feedback TEXT,
            FOREIGN KEY(interview_id) REFERENCES mock_interviews(id) ON DELETE CASCADE
        )
    ''')

    # 11. Companies Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            contact_person TEXT,
            phone TEXT,
            industry TEXT DEFAULT 'Information Technology',
            location TEXT DEFAULT 'Bengaluru, India',
            website TEXT,
            company_size TEXT DEFAULT '100-500 Employees',
            description TEXT,
            logo TEXT DEFAULT 'default_company.png',
            is_verified INTEGER DEFAULT 1,
            reset_token TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 12. Jobs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            required_skills TEXT NOT NULL,
            min_cgpa REAL DEFAULT 6.0,
            required_certifications INTEGER DEFAULT 0,
            internship_required TEXT DEFAULT 'No',
            experience_level TEXT DEFAULT 'Freshers',
            salary_package TEXT NOT NULL,
            location TEXT NOT NULL,
            deadline DATE NOT NULL,
            status TEXT DEFAULT 'Active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    ''')

    # 13. Job Applications Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            company_id INTEGER NOT NULL,
            student_reg TEXT NOT NULL,
            match_score REAL DEFAULT 0.0,
            matching_skills TEXT,
            missing_skills TEXT,
            ai_recommendation TEXT,
            status TEXT DEFAULT 'Applied',
            applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(job_id, student_reg),
            FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
            FOREIGN KEY (student_reg) REFERENCES student_users(register_number) ON DELETE CASCADE
        )
    ''')

    # 14. Interviews Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            company_id INTEGER NOT NULL,
            student_reg TEXT NOT NULL,
            interview_type TEXT NOT NULL,
            interview_date DATE NOT NULL,
            interview_time TIME NOT NULL,
            location_or_link TEXT,
            notes TEXT,
            status TEXT DEFAULT 'Scheduled',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES job_applications(id) ON DELETE CASCADE,
            FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
            FOREIGN KEY (student_reg) REFERENCES student_users(register_number) ON DELETE CASCADE
        )
    ''')

    # 15. Unified System Notifications Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_type TEXT NOT NULL,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT DEFAULT 'info',
            email_status TEXT DEFAULT 'Demo Mode',
            email_recipient TEXT,
            is_read INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 16. Email Delivery Logs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient TEXT NOT NULL,
            subject TEXT NOT NULL,
            body_html TEXT,
            status TEXT DEFAULT 'Demo Mode',
            error_message TEXT,
            sent_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 17. Create Performance Indexes for Fast Production Queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_users_reg_email ON student_users (register_number, email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_companies_email ON companies (email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_company_status ON jobs (company_id, status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_applications_job_student ON job_applications (job_id, student_reg)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_interviews_company_student ON interviews (company_id, student_reg)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications (user_type, user_id, is_read)")

    # Seed Default Admin if not exists or update credentials
    cursor.execute("SELECT id FROM admins WHERE username = 'admin' OR email = 'admin@gmail.com'")
    admin_row = cursor.fetchone()
    default_hash = generate_password_hash('admin123')
    if not admin_row:
        cursor.execute(
            "INSERT INTO admins (username, email, password_hash, name) VALUES (?, ?, ?, ?)",
            ('admin', 'admin@gmail.com', default_hash, 'System Administrator')
        )
        print("[INFO] Seeded default admin account (admin / admin@gmail.com / admin123).")
    else:
        cursor.execute(
            "UPDATE admins SET username = 'admin', email = 'admin@gmail.com', password_hash = ? WHERE id = ?",
            (default_hash, admin_row['id'])
        )
    conn.commit()



    # Seed Default Demo Student User if not exists
    cursor.execute("SELECT id FROM student_users WHERE register_number = 'REG20261001'")
    if not cursor.fetchone():
        demo_hash = generate_password_hash('student123')
        cursor.execute('''
            INSERT INTO student_users (
                register_number, email, password_hash, student_name, department,
                cgpa, tenth_percentage, twelfth_percentage, aptitude_score, coding_score,
                communication_skill, internship, certifications_count, projects_count, backlogs,
                skills_list, certifications_details, internship_details, project_details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'REG20261001', 'student@college.edu', demo_hash, 'Rahul Sharma', 'Computer Science and Engineering',
            8.2, 85.0, 82.0, 75, 80, 'Good', 'Yes', 2, 3, 0,
            'Python, Java, React, SQL, Data Structures',
            'AWS Certified Developer, Oracle Java Foundations',
            'Frontend Engineering Intern at WebCraft Systems (3 months)',
            'Full-Stack Student Placement Portal with Flask and Machine Learning'
        ))
        print("[INFO] Seeded default student account (student@college.edu / REG20261001 / student123).")

    # Seed initial demo notifications for REG20261001 if empty
    cursor.execute("SELECT COUNT(*) as count FROM student_notifications WHERE register_number = 'REG20261001'")
    if cursor.fetchone()['count'] == 0:
        cursor.executemany('''
            INSERT INTO student_notifications (register_number, title, message, type)
            VALUES (?, ?, ?, ?)
        ''', [
            ('REG20261001', 'Welcome to PlacementIQ Student Portal', 'Explore your placement probability, skill gap feedback, and career roadmap!', 'info'),
            ('REG20261001', 'Upcoming Campus Drive: TCS Digital', 'TCS Digital campus recruitment drive scheduled for August 15, 2026. Target CGPA: 7.5+.', 'reminder'),
            ('REG20261001', 'Upcoming Campus Drive: Infosys Power Programmer', 'Infosys Power Programmer coding assessment on August 20, 2026. Practice DSA!', 'reminder'),
            ('REG20261001', 'New Skill Recommendation Available', 'Your profile suggests improving Quantitative Aptitude to boost Tier-1 selection chance.', 'recommendation')
        ])

    # Seed initial dataset history if placement.csv exists and table is empty
    cursor.execute("SELECT COUNT(*) as count FROM dataset_history")
    if cursor.fetchone()['count'] == 0:
        csv_path = os.path.join('dataset', 'placement.csv')
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                cursor.execute(
                    "INSERT INTO dataset_history (filename, original_name, row_count, status) VALUES (?, ?, ?, ?)",
                    ('placement.csv', 'placement.csv', len(df), 'Active')
                )
            except Exception as e:
                print(f"[WARNING] Could not count CSV rows for seed: {e}")

    # Seed Master Students Table from placement.csv if empty
    cursor.execute("SELECT COUNT(*) as count FROM students")
    if cursor.fetchone()['count'] == 0:
        csv_path = os.path.join('dataset', 'placement.csv')
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                for i, row in df.iterrows():
                    cursor.execute('''
                        INSERT OR IGNORE INTO students (
                            student_name, register_number, department, cgpa, tenth_percentage,
                            twelfth_percentage, aptitude_score, coding_score, communication_skill,
                            internship, certifications, projects_completed, backlogs, placement_status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        str(row.get('student_name', 'Student')).strip(),
                        str(row.get('register_number', f"REG{i+1}")).strip(),
                        str(row.get('department', 'Computer Science and Engineering')).strip(),
                        float(row.get('cgpa', 7.0)) if pd.notna(row.get('cgpa')) else 7.0,
                        float(row.get('tenth_percentage', 70.0)) if pd.notna(row.get('tenth_percentage')) else 70.0,
                        float(row.get('twelfth_percentage', 70.0)) if pd.notna(row.get('twelfth_percentage')) else 70.0,
                        int(row.get('aptitude_score', 65)) if pd.notna(row.get('aptitude_score')) else 65,
                        int(row.get('coding_score', 65)) if pd.notna(row.get('coding_score')) else 65,
                        str(row.get('communication_skill', 'Average')).strip() if pd.notna(row.get('communication_skill')) else 'Average',
                        str(row.get('internship', 'No')).strip() if pd.notna(row.get('internship')) else 'No',
                        int(row.get('certifications', 0)) if pd.notna(row.get('certifications')) else 0,
                        int(row.get('projects_completed', 1)) if pd.notna(row.get('projects_completed')) else 1,
                        int(row.get('backlogs', 0)) if pd.notna(row.get('backlogs')) else 0,
                        int(row.get('placed', 0)) if pd.notna(row.get('placed')) else 0
                    ))
                print(f"[INFO] Seeded {len(df)} student records into SQLite database.")
            except Exception as e:
                print(f"[ERROR] Failed to seed students from CSV: {e}")

    # Seed Default Company & Demo Jobs if empty
    cursor.execute("SELECT id FROM companies WHERE email = 'company@techcorp.com'")
    company_row = cursor.fetchone()
    if not company_row:
        comp_hash = generate_password_hash('company123')
        cursor.execute('''
            INSERT INTO companies (
                company_name, email, password_hash, contact_person, phone,
                industry, location, website, company_size, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'TechCorp Innovations', 'company@techcorp.com', comp_hash, 'Priya Sharma (HR Lead)',
            '+91 98765 43210', 'Software & Cloud Engineering', 'Bengaluru, Karnataka',
            'https://techcorp.example.com', '500+ Employees',
            'TechCorp Innovations is a premier software & cloud solution enterprise hiring top engineering talent.'
        ))
        company_id = cursor.lastrowid
        print("[INFO] Seeded default company account (company@techcorp.com / company123).")

        # Seed Jobs for TechCorp
        cursor.execute('''
            INSERT INTO jobs (
                company_id, title, description, required_skills, min_cgpa,
                required_certifications, internship_required, experience_level,
                salary_package, location, deadline, status
            ) VALUES
            (?, 'Software Development Engineer (SDE-1)', 'Build scalable web services using Python, React, and SQL.', 'Python, Java, React, SQL, Data Structures', 7.5, 1, 'Yes', 'Freshers', '9.5 LPA', 'Bengaluru, KA', '2026-09-30', 'Active'),
            (?, 'AI / Machine Learning Engineer', 'Develop and deploy predictive ML models and data pipelines.', 'Python, Machine Learning, TensorFlow, SQL, Data Analysis', 8.0, 1, 'Preferred', 'Freshers', '12.0 LPA', 'Hyderabad, TS', '2026-10-15', 'Active'),
            (?, 'Frontend Developer (UI/UX)', 'Design modern interactive dashboards using HTML, CSS, JavaScript, and React.', 'React, JavaScript, HTML/CSS, Data Structures', 7.0, 0, 'No', 'Freshers', '7.5 LPA', 'Pune, MH', '2026-08-31', 'Active')
        ''', (company_id, company_id, company_id))
        print("[INFO] Seeded demo job postings for TechCorp Innovations.")

    conn.commit()
    conn.close()

# ---------------------------------------------------------
# Admin Auth Helpers
# ---------------------------------------------------------
def verify_admin(username_or_email, password):
    """Authenticate admin user by username or email (case-insensitive)."""
    if not username_or_email or not password:
        return None
    username_or_email = username_or_email.strip()
    pw_input = str(password)
    pw_stripped = pw_input.strip()

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT * FROM admins WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)",
            (username_or_email, username_or_email)
        )
        admin = cursor.fetchone()
    except Exception as e:
        print(f"[ERROR] verify_admin query failed: {e}")
        admin = None
    finally:
        conn.close()

    if not admin:
        return None

    admin_dict = dict(admin)
    stored_pw = admin_dict.get('password_hash', '')

    valid_password = False
    if stored_pw:
        for candidate in [pw_input, pw_stripped]:
            try:
                if check_password_hash(stored_pw, candidate):
                    valid_password = True
                    break
            except Exception:
                pass
            if stored_pw == candidate:
                valid_password = True
                break

    if valid_password:
        return admin_dict
    return None


def update_admin_password(username, new_password):
    conn = get_db_connection()
    cursor = conn.cursor()
    new_hash = generate_password_hash(new_password)
    cursor.execute("UPDATE admins SET password_hash = ? WHERE username = ?", (new_hash, username))
    conn.commit()
    conn.close()
    return True

# ---------------------------------------------------------
# Student Portal Auth & Profile Helpers
# ---------------------------------------------------------
def register_student(data):
    """Register a new student user and sync with master students table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        pw_hash = generate_password_hash(data['password'])
        cursor.execute('''
            INSERT INTO student_users (
                register_number, email, password_hash, student_name, department,
                cgpa, tenth_percentage, twelfth_percentage, aptitude_score, coding_score,
                communication_skill, internship, certifications_count, projects_count, backlogs
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['register_number'], data['email'], pw_hash, data['student_name'], data['department'],
            float(data.get('cgpa', 7.0)), float(data.get('tenth_percentage', 70.0)),
            float(data.get('twelfth_percentage', 70.0)), int(data.get('aptitude_score', 65)),
            int(data.get('coding_score', 65)), data.get('communication_skill', 'Average'),
            data.get('internship', 'No'), int(data.get('certifications_count', 0)),
            int(data.get('projects_count', 1)), int(data.get('backlogs', 0))
        ))

        # Sync with master students table
        cursor.execute('''
            INSERT OR REPLACE INTO students (
                student_name, register_number, department, cgpa, tenth_percentage,
                twelfth_percentage, aptitude_score, coding_score, communication_skill,
                internship, certifications, projects_completed, backlogs
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['student_name'], data['register_number'], data['department'],
            float(data.get('cgpa', 7.0)), float(data.get('tenth_percentage', 70.0)),
            float(data.get('twelfth_percentage', 70.0)), int(data.get('aptitude_score', 65)),
            int(data.get('coding_score', 65)), data.get('communication_skill', 'Average'),
            data.get('internship', 'No'), int(data.get('certifications_count', 0)),
            int(data.get('projects_count', 1)), int(data.get('backlogs', 0))
        ))

        # Create welcome notification
        cursor.execute('''
            INSERT INTO student_notifications (register_number, title, message, type)
            VALUES (?, ?, ?, ?)
        ''', (
            data['register_number'],
            'Account Created Successfully',
            f"Welcome to PlacementIQ, {data['student_name']}! Run your placement prediction now.",
            'info'
        ))

        conn.commit()
        conn.close()
        return True, None
    except sqlite3.IntegrityError as e:
        conn.close()
        err_msg = str(e)
        if 'register_number' in err_msg:
            return False, "Register number already registered!"
        elif 'email' in err_msg:
            return False, "Email address already registered!"
        return False, "User registration failed due to duplicate entry."
    except Exception as e:
        conn.close()
        return False, str(e)

def verify_student(email_or_reg, password):
    """Authenticate student user by email or register number."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_users WHERE email = ? OR register_number = ?", (email_or_reg, email_or_reg))
    user = cursor.fetchone()
    conn.close()
    if user and check_password_hash(user['password_hash'], password):
        return dict(user)
    return None

def get_student_user(register_number):
    """Fetch complete student user details by register number."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_users WHERE register_number = ?", (register_number,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_student_user_profile(register_number, data):
    """Update student profile details and sync with master students table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE student_users SET
                student_name = ?, department = ?, cgpa = ?, tenth_percentage = ?,
                twelfth_percentage = ?, aptitude_score = ?, coding_score = ?,
                communication_skill = ?, internship = ?, certifications_count = ?,
                projects_count = ?, backlogs = ?, skills_list = ?,
                certifications_details = ?, internship_details = ?, project_details = ?
                {% if profile_photo %} , profile_photo = ? {% endif %}
            WHERE register_number = ?
        '''.replace('{% if profile_photo %} , profile_photo = ? {% endif %}', ', profile_photo = ?' if 'profile_photo' in data else ''),
        (
            data['student_name'], data['department'], float(data['cgpa']),
            float(data.get('tenth_percentage', 70.0)), float(data.get('twelfth_percentage', 70.0)),
            int(data.get('aptitude_score', 65)), int(data.get('coding_score', 65)),
            data.get('communication_skill', 'Average'), data.get('internship', 'No'),
            int(data.get('certifications_count', 0)), int(data.get('projects_count', 1)),
            int(data.get('backlogs', 0)), data.get('skills_list', ''),
            data.get('certifications_details', ''), data.get('internship_details', ''),
            data.get('project_details', ''),
            *( [data['profile_photo']] if 'profile_photo' in data else [] ),
            register_number
        ))

        # Sync master students table
        cursor.execute('''
            UPDATE students SET
                student_name = ?, department = ?, cgpa = ?, tenth_percentage = ?,
                twelfth_percentage = ?, aptitude_score = ?, coding_score = ?,
                communication_skill = ?, internship = ?, certifications = ?,
                projects_completed = ?, backlogs = ?, updated_at = CURRENT_TIMESTAMP
            WHERE register_number = ?
        ''', (
            data['student_name'], data['department'], float(data['cgpa']),
            float(data.get('tenth_percentage', 70.0)), float(data.get('twelfth_percentage', 70.0)),
            int(data.get('aptitude_score', 65)), int(data.get('coding_score', 65)),
            data.get('communication_skill', 'Average'), data.get('internship', 'No'),
            int(data.get('certifications_count', 0)), int(data.get('projects_count', 1)),
            int(data.get('backlogs', 0)), register_number
        ))

        # Log profile update notification
        cursor.execute('''
            INSERT INTO student_notifications (register_number, title, message, type)
            VALUES (?, ?, ?, ?)
        ''', (
            register_number,
            'Profile Updated Successfully',
            'Your academic and technical profile details have been saved.',
            'profile'
        ))

        conn.commit()
        conn.close()
        return True, None
    except Exception as e:
        conn.close()
        return False, str(e)

def update_student_user_password(register_number, new_password):
    """Update student account password."""
    conn = get_db_connection()
    cursor = conn.cursor()
    new_hash = generate_password_hash(new_password)
    cursor.execute("UPDATE student_users SET password_hash = ? WHERE register_number = ?", (new_hash, register_number))
    conn.commit()
    conn.close()
    return True

def reset_student_password_by_email(email, new_password):
    """Reset student password via email address."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT register_number FROM student_users WHERE email = ?", (email,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, "Email address not found in records."
    new_hash = generate_password_hash(new_password)
    cursor.execute("UPDATE student_users SET password_hash = ? WHERE email = ?", (new_hash, email))
    conn.commit()
    conn.close()
    return True, None

def calculate_profile_completion(student):
    """Calculate overall profile completion percentage (0 - 100%)."""
    if not student:
        return 0
    total_fields = 12
    completed = 0

    if student.get('student_name'): completed += 1
    if student.get('email'): completed += 1
    if student.get('department'): completed += 1
    if student.get('cgpa') and float(student.get('cgpa')) > 0: completed += 1
    if student.get('tenth_percentage') and float(student.get('tenth_percentage')) > 0: completed += 1
    if student.get('twelfth_percentage') and float(student.get('twelfth_percentage')) > 0: completed += 1
    if student.get('aptitude_score') and int(student.get('aptitude_score')) > 0: completed += 1
    if student.get('coding_score') and int(student.get('coding_score')) > 0: completed += 1
    if student.get('skills_list') and len(student.get('skills_list').strip()) > 3: completed += 1
    if student.get('certifications_details') and len(student.get('certifications_details').strip()) > 3: completed += 1
    if student.get('internship_details') and len(student.get('internship_details').strip()) > 3: completed += 1
    if student.get('project_details') and len(student.get('project_details').strip()) > 3: completed += 1

    return round((completed / total_fields) * 100)

# ---------------------------------------------------------
# Notifications & Reminders Helpers
# ---------------------------------------------------------
def add_student_notification(register_number, title, message, notif_type='info'):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO student_notifications (register_number, title, message, type)
        VALUES (?, ?, ?, ?)
    ''', (register_number, title, message, notif_type))
    conn.commit()
    conn.close()

def get_student_notifications(register_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM student_notifications
        WHERE register_number = ?
        ORDER BY id DESC
    ''', (register_number,))
    notes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return notes

def mark_notification_read(notif_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE student_notifications SET is_read = 1 WHERE id = ?", (notif_id,))
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# Student CRUD & Prediction History Helpers
# ---------------------------------------------------------
def get_students(search_query='', department_filter='', status_filter='', limit=500, offset=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM students WHERE 1=1"
    params = []

    if search_query:
        query += " AND (student_name LIKE ? OR register_number LIKE ?)"
        search_pattern = f"%{search_query}%"
        params.extend([search_pattern, search_pattern])

    if department_filter:
        query += " AND department = ?"
        params.append(department_filter)

    if status_filter != '':
        query += " AND placement_status = ?"
        params.append(int(status_filter))

    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, params)
    students = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return students

def get_student_by_id(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_student(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO students (
                student_name, register_number, department, cgpa, tenth_percentage,
                twelfth_percentage, aptitude_score, coding_score, communication_skill,
                internship, certifications, projects_completed, backlogs, placement_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['student_name'], data['register_number'], data['department'],
            float(data['cgpa']), float(data.get('tenth_percentage', 0.0)),
            float(data.get('twelfth_percentage', 0.0)), int(data.get('aptitude_score', 0)),
            int(data.get('coding_score', 0)), data.get('communication_skill', 'Average'),
            data.get('internship', 'No'), int(data.get('certifications', 0)),
            int(data.get('projects_completed', 0)), int(data.get('backlogs', 0)),
            int(data.get('placement_status', 0))
        ))
        conn.commit()
        student_id = cursor.lastrowid
        conn.close()
        return student_id, None
    except sqlite3.IntegrityError:
        conn.close()
        return None, "Register number already exists!"
    except Exception as e:
        conn.close()
        return None, str(e)

def update_student(student_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE students SET
                student_name = ?, register_number = ?, department = ?, cgpa = ?,
                tenth_percentage = ?, twelfth_percentage = ?, aptitude_score = ?,
                coding_score = ?, communication_skill = ?, internship = ?,
                certifications = ?, projects_completed = ?, backlogs = ?,
                placement_status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            data['student_name'], data['register_number'], data['department'],
            float(data['cgpa']), float(data.get('tenth_percentage', 0.0)),
            float(data.get('twelfth_percentage', 0.0)), int(data.get('aptitude_score', 0)),
            int(data.get('coding_score', 0)), data.get('communication_skill', 'Average'),
            data.get('internship', 'No'), int(data.get('certifications', 0)),
            int(data.get('projects_completed', 0)), int(data.get('backlogs', 0)),
            int(data.get('placement_status', 0)), student_id
        ))
        conn.commit()
        conn.close()
        return True, None
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Register number conflict with another student!"
    except Exception as e:
        conn.close()
        return False, str(e)

def delete_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()
    return True

def sync_students_from_dataframe(df):
    """Replace or append students table from an uploaded dataframe."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students")
    count = 0
    for i, row in df.iterrows():
        try:
            cursor.execute('''
                INSERT INTO students (
                    student_name, register_number, department, cgpa, tenth_percentage,
                    twelfth_percentage, aptitude_score, coding_score, communication_skill,
                    internship, certifications, projects_completed, backlogs, placement_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(row.get('student_name', f'Student_{count+1}')).strip(),
                str(row.get('register_number', f'REG{20260000+count+1}')).strip(),
                str(row.get('department', 'Computer Science and Engineering')).strip(),
                float(row.get('cgpa', 7.0)) if pd.notna(row.get('cgpa')) else 7.0,
                float(row.get('tenth_percentage', 70.0)) if pd.notna(row.get('tenth_percentage')) else 70.0,
                float(row.get('twelfth_percentage', 70.0)) if pd.notna(row.get('twelfth_percentage')) else 70.0,
                int(row.get('aptitude_score', 65)) if pd.notna(row.get('aptitude_score')) else 65,
                int(row.get('coding_score', 65)) if pd.notna(row.get('coding_score')) else 65,
                str(row.get('communication_skill', 'Average')).strip() if pd.notna(row.get('communication_skill')) else 'Average',
                str(row.get('internship', 'No')).strip() if pd.notna(row.get('internship')) else 'No',
                int(row.get('certifications', 0)) if pd.notna(row.get('certifications')) else 0,
                int(row.get('projects_completed', 1)) if pd.notna(row.get('projects_completed')) else 1,
                int(row.get('backlogs', 0)) if pd.notna(row.get('backlogs')) else 0,
                int(row.get('placed', 0)) if pd.notna(row.get('placed')) else 0
            ))
            count += 1
        except Exception:
            continue
    conn.commit()
    conn.close()
    return count

def log_prediction(student_name, register_number, department, cgpa, prediction, probability, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO prediction_history (
            student_name, register_number, department, cgpa, prediction, probability, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (student_name, register_number, department, float(cgpa), int(prediction), float(probability), status))
    conn.commit()
    conn.close()

def get_predictions(search_query='', department_filter='', prediction_filter='', sort_by='id_desc', limit=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM prediction_history WHERE 1=1"
    params = []

    if search_query:
        query += " AND (student_name LIKE ? OR register_number LIKE ?)"
        search_pattern = f"%{search_query}%"
        params.extend([search_pattern, search_pattern])

    if department_filter:
        query += " AND department = ?"
        params.append(department_filter)

    if prediction_filter != '':
        query += " AND prediction = ?"
        params.append(int(prediction_filter))

    if sort_by == 'prob_desc':
        query += " ORDER BY probability DESC"
    elif sort_by == 'prob_asc':
        query += " ORDER BY probability ASC"
    elif sort_by == 'name_asc':
        query += " ORDER BY student_name ASC"
    else:
        query += " ORDER BY id DESC"

    if limit is not None:
        query += " LIMIT ?"
        params.append(int(limit))

    cursor.execute(query, params)
    predictions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return predictions

def get_student_predictions(register_number):
    """Fetch prediction logs for a specific student."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM prediction_history
        WHERE register_number = ?
        ORDER BY id DESC
    ''', (register_number,))
    preds = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return preds

def get_prediction_by_id(pred_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prediction_history WHERE id = ?", (pred_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# Dataset History Helpers
def log_dataset_upload(filename, original_name, row_count, status='Active'):
    conn = get_db_connection()
    cursor = conn.cursor()
    if status == 'Active':
        cursor.execute("UPDATE dataset_history SET status = 'Replaced' WHERE status = 'Active'")
    cursor.execute('''
        INSERT INTO dataset_history (filename, original_name, row_count, status)
        VALUES (?, ?, ?, ?)
    ''', (filename, original_name, row_count, status))
    conn.commit()
    conn.close()

def get_dataset_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dataset_history ORDER BY id DESC")
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return history

def delete_dataset_record(record_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE dataset_history SET status = 'Deleted' WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()

# Model Metadata Helpers
def log_model_metadata(algorithm, accuracy, precision, recall, f1_score, total_samples):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO model_metadata (algorithm, accuracy, precision, recall, f1_score, total_samples)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (algorithm, float(accuracy), float(precision), float(recall), float(f1_score), int(total_samples)))
    conn.commit()
    conn.close()

def get_latest_model_metadata():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM model_metadata ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# Dashboard Statistics & Analytics Aggregation
def get_dashboard_stats():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM students")
    total_students = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM prediction_history")
    total_predictions = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM students WHERE placement_status = 1")
    likely_placed = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM students WHERE placement_status = 0")
    unlikely_placed = cursor.fetchone()['count']

    cursor.execute("SELECT AVG(cgpa) as avg_cgpa FROM students")
    avg_cgpa_row = cursor.fetchone()
    avg_cgpa = round(avg_cgpa_row['avg_cgpa'], 2) if avg_cgpa_row and avg_cgpa_row['avg_cgpa'] else 0.0

    placement_percentage = round((likely_placed / total_students * 100), 1) if total_students > 0 else 0.0

    conn.close()
    return {
        'total_students': total_students,
        'total_predictions': total_predictions,
        'likely_placed': likely_placed,
        'unlikely_placed': unlikely_placed,
        'placement_percentage': placement_percentage,
        'avg_cgpa': avg_cgpa
    }

def get_analytics_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Placed vs Not Placed
    cursor.execute("SELECT placement_status, COUNT(*) as count FROM students GROUP BY placement_status")
    status_counts = {row['placement_status']: row['count'] for row in cursor.fetchall()}
    placed_vs_unplaced = {
        'placed': status_counts.get(1, 0),
        'unplaced': status_counts.get(0, 0)
    }

    # 2. Department-wise Placement Rate
    cursor.execute('''
        SELECT department,
               COUNT(*) as total,
               SUM(CASE WHEN placement_status = 1 THEN 1 ELSE 0 END) as placed,
               AVG(cgpa) as avg_cgpa
        FROM students
        GROUP BY department
    ''')
    dept_rows = cursor.fetchall()
    dept_labels = []
    dept_rates = []
    dept_avg_cgpa = []

    for r in dept_rows:
        dept_labels.append(r['department'])
        rate = round((r['placed'] / r['total'] * 100), 1) if r['total'] > 0 else 0.0
        dept_rates.append(rate)
        dept_avg_cgpa.append(round(r['avg_cgpa'], 2) if r['avg_cgpa'] else 0.0)

    # 3. Internship vs Placement
    cursor.execute('''
        SELECT internship,
               SUM(CASE WHEN placement_status = 1 THEN 1 ELSE 0 END) as placed,
               SUM(CASE WHEN placement_status = 0 THEN 1 ELSE 0 END) as unplaced
        FROM students
        GROUP BY internship
    ''')
    intern_rows = cursor.fetchall()
    internship_data = {'Yes': {'placed': 0, 'unplaced': 0}, 'No': {'placed': 0, 'unplaced': 0}}
    for r in intern_rows:
        k = 'Yes' if str(r['internship']).strip().lower() == 'yes' else 'No'
        internship_data[k]['placed'] += r['placed']
        internship_data[k]['unplaced'] += r['unplaced']

    # 4. Certification Count vs Placement
    cursor.execute('''
        SELECT certifications,
               SUM(CASE WHEN placement_status = 1 THEN 1 ELSE 0 END) as placed,
               COUNT(*) as total
        FROM students
        GROUP BY certifications
        ORDER BY certifications ASC
    ''')
    cert_rows = cursor.fetchall()
    cert_labels = [f"{r['certifications']} Cert(s)" for r in cert_rows]
    cert_rates = [round((r['placed'] / r['total'] * 100), 1) if r['total'] > 0 else 0.0 for r in cert_rows]

    # 5. Monthly Prediction Statistics
    cursor.execute('''
        SELECT strftime('%Y-%m', created_at) as month_yr, COUNT(*) as count
        FROM prediction_history
        GROUP BY month_yr
        ORDER BY month_yr ASC
        LIMIT 12
    ''')
    monthly_rows = cursor.fetchall()
    monthly_labels = [r['month_yr'] for r in monthly_rows]
    monthly_counts = [r['count'] for r in monthly_rows]

    conn.close()

    return {
        'placed_vs_unplaced': placed_vs_unplaced,
        'department_analytics': {
            'labels': dept_labels,
            'rates': dept_rates,
            'avg_cgpa': dept_avg_cgpa
        },
        'internship_analytics': internship_data,
        'certification_analytics': {
            'labels': cert_labels,
            'rates': cert_rates
        },
        'monthly_predictions': {
            'labels': monthly_labels,
            'counts': monthly_counts
        }
    }

# ---------------------------------------------------------
# Resume Analysis Helpers
# ---------------------------------------------------------
import json

def save_resume_analysis(data):
    """Save parsed resume analysis result to SQLite database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO resume_analyses (
            register_number, filename, original_filename, file_type,
            name, email, phone, skills_extracted, education_extracted,
            projects_extracted, internships_extracted, certifications_extracted,
            experience_extracted, resume_score, score_breakdown, strengths,
            weaknesses, improvements, skill_gap_data, job_recommendations,
            roadmap_data, placement_probability, placement_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('register_number'),
        data.get('filename'),
        data.get('original_filename'),
        data.get('file_type'),
        data.get('name'),
        data.get('email'),
        data.get('phone'),
        json.dumps(data.get('skills_extracted', [])),
        json.dumps(data.get('education_extracted', [])),
        json.dumps(data.get('projects_extracted', [])),
        json.dumps(data.get('internships_extracted', [])),
        json.dumps(data.get('certifications_extracted', [])),
        json.dumps(data.get('experience_extracted', [])),
        data.get('resume_score', 0),
        json.dumps(data.get('score_breakdown', {})),
        json.dumps(data.get('strengths', [])),
        json.dumps(data.get('weaknesses', [])),
        json.dumps(data.get('improvements', [])),
        json.dumps(data.get('skill_gap_data', {})),
        json.dumps(data.get('job_recommendations', [])),
        json.dumps(data.get('roadmap_data', {})),
        data.get('placement_probability', 0.0),
        data.get('placement_status', 'Unplaced')
    ))
    conn.commit()
    analysis_id = cursor.lastrowid
    conn.close()
    return analysis_id

def _format_analysis_row(row):
    if not row:
        return None
    d = dict(row)
    for json_col in ['skills_extracted', 'education_extracted', 'projects_extracted',
                    'internships_extracted', 'certifications_extracted', 'experience_extracted',
                    'score_breakdown', 'strengths', 'weaknesses', 'improvements',
                    'skill_gap_data', 'job_recommendations', 'roadmap_data']:
        if d.get(json_col):
            try:
                d[json_col] = json.loads(d[json_col])
            except Exception:
                pass
    return d

def get_resume_analysis(analysis_id):
    """Retrieve resume analysis details by analysis_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resume_analyses WHERE id = ?", (analysis_id,))
    row = cursor.fetchone()
    conn.close()
    return _format_analysis_row(row)

def get_student_resume_analyses(register_number):
    """Retrieve all resume analyses for a student."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resume_analyses WHERE register_number = ? ORDER BY created_at DESC", (register_number,))
    rows = cursor.fetchall()
    conn.close()
    return [_format_analysis_row(r) for r in rows]

def get_latest_student_resume_analysis(register_number):
    """Retrieve latest resume analysis for a student."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resume_analyses WHERE register_number = ? ORDER BY created_at DESC LIMIT 1", (register_number,))
    row = cursor.fetchone()
    conn.close()
    return _format_analysis_row(row)

def get_all_resume_analyses(limit=50):
    """Retrieve all resume analyses across system."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resume_analyses ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [_format_analysis_row(r) for r in rows]

# ---------------------------------------------------------
# Mock Interview Helpers
# ---------------------------------------------------------
def save_mock_interview(data, answers_list):
    """Save completed mock interview session and detailed question responses."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO mock_interviews (
            register_number, category, domain, total_questions, correct_answers,
            total_score, time_taken_seconds, strengths, weaknesses, feedback, recommended_topics
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('register_number', 'GUEST'),
        data.get('category'),
        data.get('domain'),
        data.get('total_questions', 0),
        data.get('correct_answers', 0),
        data.get('total_score', 0.0),
        data.get('time_taken_seconds', 0),
        json.dumps(data.get('strengths', [])),
        json.dumps(data.get('weaknesses', [])),
        data.get('feedback', ''),
        json.dumps(data.get('recommended_topics', []))
    ))
    interview_id = cursor.lastrowid

    for ans in answers_list:
        cursor.execute('''
            INSERT INTO mock_interview_answers (
                interview_id, question_text, user_answer, model_answer, score, is_correct, feedback
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            interview_id,
            ans.get('question_text'),
            ans.get('user_answer'),
            ans.get('model_answer'),
            ans.get('score', 0.0),
            ans.get('is_correct', 0),
            ans.get('feedback', '')
        ))

    conn.commit()
    conn.close()
    return interview_id

def _format_interview_row(row):
    if not row:
        return None
    d = dict(row)
    for json_col in ['strengths', 'weaknesses', 'recommended_topics']:
        if d.get(json_col):
            try:
                d[json_col] = json.loads(d[json_col])
            except Exception:
                pass
    return d

def get_mock_interview(interview_id):
    """Retrieve full mock interview session including detailed question answers."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mock_interviews WHERE id = ?", (interview_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    interview = _format_interview_row(row)
    cursor.execute("SELECT * FROM mock_interview_answers WHERE interview_id = ?", (interview_id,))
    answers = [dict(r) for r in cursor.fetchall()]
    conn.close()
    interview['answers'] = answers
    return interview

def get_student_mock_interviews(register_number, limit=50):
    """Retrieve all completed mock interviews for a student."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mock_interviews WHERE register_number = ? ORDER BY created_at DESC LIMIT ?", (register_number, limit))
    rows = cursor.fetchall()
    conn.close()
    return [_format_interview_row(r) for r in rows]

def get_student_interview_stats(register_number):
    """Compute aggregate analytics for student's mock interviews."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) as total_interviews,
               COALESCE(AVG(total_score), 0.0) as avg_score,
               COALESCE(MAX(total_score), 0.0) as best_score
        FROM mock_interviews
        WHERE register_number = ?
    ''', (register_number,))
    stats = dict(cursor.fetchone())

    # Category Breakdown
    cursor.execute('''
        SELECT category, COUNT(*) as count, AVG(total_score) as avg_score
        FROM mock_interviews
        WHERE register_number = ?
        GROUP BY category
    ''', (register_number,))
    cat_rows = cursor.fetchall()
    conn.close()

    return {
        'total_interviews': stats['total_interviews'],
        'avg_score': round(stats['avg_score'], 1),
        'best_score': round(stats['best_score'], 1),
        'category_stats': [dict(r) for r in cat_rows]
    }


# ---------------------------------------------------------
# Company Authentication & Profile Helpers
# ---------------------------------------------------------
def register_company(data):
    """Register a new company in the system."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM companies WHERE email = ?", (data['email'],))
        if cursor.fetchone():
            conn.close()
            return False, "A company with this email address is already registered."

        password_hash = generate_password_hash(data['password'])
        cursor.execute('''
            INSERT INTO companies (
                company_name, email, password_hash, contact_person, phone,
                industry, location, website, company_size, description, logo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('company_name', '').strip(),
            data.get('email', '').strip().lower(),
            password_hash,
            data.get('contact_person', '').strip(),
            data.get('phone', '').strip(),
            data.get('industry', 'Information Technology').strip(),
            data.get('location', 'Bengaluru, India').strip(),
            data.get('website', '').strip(),
            data.get('company_size', '100-500 Employees').strip(),
            data.get('description', '').strip(),
            data.get('logo', 'default_company.png')
        ))
        conn.commit()
        company_id = cursor.lastrowid
        conn.close()
        return True, company_id
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)

def verify_company(email, password):
    """Verify company credentials for login."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies WHERE email = ?", (email.strip().lower(),))
    company = cursor.fetchone()
    conn.close()

    if company and check_password_hash(company['password_hash'], password):
        return dict(company)
    return None

def get_company_by_id(company_id):
    """Get company profile details by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_company_by_email(email):
    """Get company profile details by email."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies WHERE email = ?", (email.strip().lower(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_company_profile(company_id, data):
    """Update company details & logo."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE companies
            SET company_name = ?,
                contact_person = ?,
                phone = ?,
                industry = ?,
                location = ?,
                website = ?,
                company_size = ?,
                description = ?,
                logo = COALESCE(?, logo)
            WHERE id = ?
        ''', (
            data.get('company_name', '').strip(),
            data.get('contact_person', '').strip(),
            data.get('phone', '').strip(),
            data.get('industry', '').strip(),
            data.get('location', '').strip(),
            data.get('website', '').strip(),
            data.get('company_size', '').strip(),
            data.get('description', '').strip(),
            data.get('logo'),
            company_id
        ))
        conn.commit()
        conn.close()
        return True, "Profile updated successfully."
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)

def update_company_password(company_id, new_password):
    """Update password for company user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        hash_val = generate_password_hash(new_password)
        cursor.execute("UPDATE companies SET password_hash = ? WHERE id = ?", (hash_val, company_id))
        conn.commit()
        conn.close()
        return True, "Password updated successfully."
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)

def get_all_companies():
    """Retrieve list of all registered companies for admin dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, COUNT(j.id) as job_count
        FROM companies c
        LEFT JOIN jobs j ON c.id = j.company_id
        GROUP BY c.id
        ORDER BY c.created_at DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ---------------------------------------------------------
# Job Posting CRUD Helpers
# ---------------------------------------------------------
def create_job(company_id, data):
    """Create a new job posting for a company."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO jobs (
                company_id, title, description, required_skills, min_cgpa,
                required_certifications, internship_required, experience_level,
                salary_package, location, deadline, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            company_id,
            data.get('title', '').strip(),
            data.get('description', '').strip(),
            data.get('required_skills', '').strip(),
            float(data.get('min_cgpa', 6.0)),
            int(data.get('required_certifications', 0)),
            data.get('internship_required', 'No'),
            data.get('experience_level', 'Freshers'),
            data.get('salary_package', '').strip(),
            data.get('location', '').strip(),
            data.get('deadline', ''),
            data.get('status', 'Active')
        ))
        conn.commit()
        job_id = cursor.lastrowid
        conn.close()

        # Trigger notifications for active students with match >= 60%
        notify_students_for_new_job(job_id)

        return True, job_id
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)

def update_job(job_id, company_id, data):
    """Edit an existing job posting."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE jobs
            SET title = ?,
                description = ?,
                required_skills = ?,
                min_cgpa = ?,
                required_certifications = ?,
                internship_required = ?,
                experience_level = ?,
                salary_package = ?,
                location = ?,
                deadline = ?,
                status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND company_id = ?
        ''', (
            data.get('title', '').strip(),
            data.get('description', '').strip(),
            data.get('required_skills', '').strip(),
            float(data.get('min_cgpa', 6.0)),
            int(data.get('required_certifications', 0)),
            data.get('internship_required', 'No'),
            data.get('experience_level', 'Freshers'),
            data.get('salary_package', '').strip(),
            data.get('location', '').strip(),
            data.get('deadline', ''),
            data.get('status', 'Active'),
            job_id, company_id
        ))
        conn.commit()
        conn.close()
        return True, "Job updated successfully."
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)

def delete_job(job_id, company_id):
    """Delete a job posting and associated applications."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM jobs WHERE id = ? AND company_id = ?", (job_id, company_id))
        conn.commit()
        conn.close()
        return True, "Job deleted successfully."
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)

def get_company_jobs(company_id, status=None):
    """Fetch jobs posted by a company with applicant count."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if status:
        cursor.execute('''
            SELECT j.*, COUNT(a.id) as applicant_count
            FROM jobs j
            LEFT JOIN job_applications a ON j.id = a.job_id
            WHERE j.company_id = ? AND j.status = ?
            GROUP BY j.id
            ORDER BY j.created_at DESC
        ''', (company_id, status))
    else:
        cursor.execute('''
            SELECT j.*, COUNT(a.id) as applicant_count
            FROM jobs j
            LEFT JOIN job_applications a ON j.id = a.job_id
            WHERE j.company_id = ?
            GROUP BY j.id
            ORDER BY j.created_at DESC
        ''', (company_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_job_by_id(job_id):
    """Retrieve detailed single job record with company info."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT j.*, c.company_name, c.logo, c.industry, c.location as company_location, c.website, c.email as company_email, c.contact_person
        FROM jobs j
        JOIN companies c ON j.company_id = c.id
        WHERE j.id = ?
    ''', (job_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_active_jobs():
    """Retrieve all active jobs across companies for student portal."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT j.*, c.company_name, c.logo, c.industry, c.location as company_location
        FROM jobs j
        JOIN companies c ON j.company_id = c.id
        WHERE j.status = 'Active'
        ORDER BY j.created_at DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ---------------------------------------------------------
# AI Candidate Matching Engine Logic
# ---------------------------------------------------------
def calculate_student_job_match(student, job):
    """
    Calculate AI Match Score, matching skills, missing skills,
    and AI recommendation for a candidate against a job requirement.
    """
    # 1. Skills Matching (40% Weight)
    req_skills_raw = job.get('required_skills', '')
    req_skills_list = [s.strip() for s in req_skills_raw.split(',') if s.strip()]

    stu_skills_raw = student.get('skills_list', '')
    stu_skills_list = [s.strip() for s in stu_skills_raw.split(',') if s.strip()]

    matching_skills = []
    missing_skills = []

    for req in req_skills_list:
        req_lower = req.lower()
        matched = False
        for stu in stu_skills_list:
            stu_lower = stu.lower()
            if req_lower in stu_lower or stu_lower in req_lower:
                matched = True
                break
        if matched:
            matching_skills.append(req)
        else:
            missing_skills.append(req)

    if req_skills_list:
        skills_score = (len(matching_skills) / len(req_skills_list)) * 100.0
    else:
        skills_score = 100.0

    # 2. CGPA Score (25% Weight)
    min_cgpa = float(job.get('min_cgpa', 6.0))
    student_cgpa = float(student.get('cgpa', 7.0))
    if student_cgpa >= min_cgpa:
        cgpa_score = 100.0
    else:
        cgpa_score = max(0.0, (student_cgpa / min_cgpa) * 100.0 - 20.0)

    # 3. Placement Prediction ML Score (15% Weight)
    coding_score = float(student.get('coding_score', 70))
    aptitude_score = float(student.get('aptitude_score', 70))
    placement_ml_score = min(100.0, (student_cgpa * 7.0) + (coding_score * 0.25) + (aptitude_score * 0.25))

    # 4. Internship & Projects Score (10% Weight)
    intern_req = job.get('internship_required', 'No')
    student_intern = str(student.get('internship', 'No')).strip()
    if intern_req == 'Yes':
        intern_score = 100.0 if student_intern in ['Yes', '1', 1] else 40.0
    elif intern_req == 'Preferred':
        intern_score = 100.0 if student_intern in ['Yes', '1', 1] else 75.0
    else:
        intern_score = 100.0

    projects_count = int(student.get('projects_count', student.get('projects_completed', 1)))
    project_score = min(100.0, projects_count * 33.3)
    intern_proj_score = (intern_score * 0.6) + (project_score * 0.4)

    # 5. Certifications Score (10% Weight)
    req_certs = int(job.get('required_certifications', 0))
    stu_certs = int(student.get('certifications_count', student.get('certifications', 0)))
    if req_certs == 0:
        cert_score = 100.0
    else:
        cert_score = min(100.0, (stu_certs / req_certs) * 100.0)

    # Composite Match Calculation
    overall_match = round(
        (0.40 * skills_score) +
        (0.25 * cgpa_score) +
        (0.15 * placement_ml_score) +
        (0.10 * intern_proj_score) +
        (0.10 * cert_score),
        1
    )
    overall_match = min(100.0, max(0.0, overall_match))

    # Recommendation tag
    if overall_match >= 85.0:
        ai_recommendation = "Strong Match - High Hiring Potential"
    elif overall_match >= 70.0:
        ai_recommendation = "Highly Recommended"
    elif overall_match >= 55.0:
        ai_recommendation = "Suitable Candidate"
    else:
        ai_recommendation = "Low Match - Up-skilling Required"

    return {
        'match_score': overall_match,
        'matching_skills': ", ".join(matching_skills) if matching_skills else "None",
        'missing_skills': ", ".join(missing_skills) if missing_skills else "None",
        'ai_recommendation': ai_recommendation
    }

def get_job_candidate_matches(job_id, company_id):
    """
    Generate real-time AI Match rankings for all registered students against a job.
    """
    job = get_job_by_id(job_id)
    if not job or job['company_id'] != company_id:
        return []

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM student_users ORDER BY cgpa DESC")
    student_rows = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT student_reg, status, id as application_id FROM job_applications WHERE job_id = ?", (job_id,))
    app_map = {r['student_reg']: {'status': r['status'], 'application_id': r['application_id']} for r in cursor.fetchall()}

    conn.close()

    candidates = []
    for stu in student_rows:
        match_info = calculate_student_job_match(stu, job)
        app_data = app_map.get(stu['register_number'])
        candidates.append({
            'student': stu,
            'match_score': match_info['match_score'],
            'matching_skills': match_info['matching_skills'],
            'missing_skills': match_info['missing_skills'],
            'ai_recommendation': match_info['ai_recommendation'],
            'applied': True if app_data else False,
            'application_status': app_data['status'] if app_data else 'Not Applied',
            'application_id': app_data['application_id'] if app_data else None
        })

    candidates.sort(key=lambda x: x['match_score'], reverse=True)
    return candidates

# ---------------------------------------------------------
# Job Applications & Candidate Management Helpers
# ---------------------------------------------------------
def apply_for_job(job_id, student_reg):
    """Allow a student to apply for an active job."""
    job = get_job_by_id(job_id)
    if not job or job['status'] != 'Active':
        return False, "This job is currently closed or unavailable."

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM student_users WHERE register_number = ?", (student_reg,))
    student = cursor.fetchone()
    if not student:
        conn.close()
        return False, "Student profile not found."

    student_dict = dict(student)
    match_info = calculate_student_job_match(student_dict, job)

    try:
        cursor.execute('''
            INSERT INTO job_applications (
                job_id, company_id, student_reg, match_score, matching_skills,
                missing_skills, ai_recommendation, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'Applied')
        ''', (
            job_id,
            job['company_id'],
            student_reg,
            match_info['match_score'],
            match_info['matching_skills'],
            match_info['missing_skills'],
            match_info['ai_recommendation']
        ))
        conn.commit()
        app_id = cursor.lastrowid
        conn.close()

        post_student_notification(
            student_reg,
            f"Application Received: {job['title']}",
            f"Your application for {job['title']} at {job['company_name']} has been submitted with AI Match Score {match_info['match_score']}%.",
            'info'
        )

        return True, "Application submitted successfully!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "You have already applied for this job opportunity."
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)

def get_job_applications(company_id=None, job_id=None, status=None, student_reg=None):
    """Retrieve filtered job applications with student details and job info."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
        SELECT a.*,
               j.title as job_title, j.salary_package, j.location as job_location,
               c.company_name, c.logo as company_logo,
               s.student_name, s.email as student_email, s.department, s.cgpa,
               s.skills_list, s.coding_score, s.aptitude_score, s.internship,
               s.certifications_count, s.projects_count, s.profile_photo
        FROM job_applications a
        JOIN jobs j ON a.job_id = j.id
        JOIN companies c ON a.company_id = c.id
        JOIN student_users s ON a.student_reg = s.register_number
        WHERE 1=1
    '''
    params = []

    if company_id:
        query += " AND a.company_id = ?"
        params.append(company_id)
    if job_id:
        query += " AND a.job_id = ?"
        params.append(job_id)
    if status and status != 'All':
        query += " AND a.status = ?"
        params.append(status)
    if student_reg:
        query += " AND a.student_reg = ?"
        params.append(student_reg)

    query += " ORDER BY a.applied_at DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_application_by_id(app_id):
    """Retrieve detailed single job application."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.*,
               j.title as job_title, j.salary_package, j.location as job_location, j.required_skills, j.min_cgpa,
               c.company_name, c.logo as company_logo, c.id as company_id,
               s.student_name, s.email as student_email, s.department, s.cgpa,
               s.skills_list, s.coding_score, s.aptitude_score, s.internship, s.communication_skill,
               s.certifications_count, s.certifications_details, s.internship_details, s.project_details,
               s.projects_count, s.profile_photo, s.tenth_percentage, s.twelfth_percentage, s.backlogs
        FROM job_applications a
        JOIN jobs j ON a.job_id = j.id
        JOIN companies c ON a.company_id = c.id
        JOIN student_users s ON a.student_reg = s.register_number
        WHERE a.id = ?
    ''', (app_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_application_status(app_id, status):
    """Update job application status (Shortlisted, Rejected, Selected, etc.)."""
    app = get_application_by_id(app_id)
    if not app:
        return False, "Application record not found."

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE job_applications SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (status, app_id))
        conn.commit()
        conn.close()

        status_msg_map = {
            'Shortlisted': f"Congratulations! You have been shortlisted for {app['job_title']} at {app['company_name']}.",
            'Selected': f"🎉 Excellent News! You have been selected for {app['job_title']} at {app['company_name']}!",
            'Rejected': f"Update on your application for {app['job_title']} at {app['company_name']}: Status set to Rejected.",
            'Interview Scheduled': f"An interview has been scheduled for your application to {app['job_title']} at {app['company_name']}."
        }
        notif_type = 'success' if status in ['Shortlisted', 'Selected'] else ('warning' if status == 'Rejected' else 'info')

        post_student_notification(
            app['student_reg'],
            f"Application Status Updated: {app['job_title']}",
            status_msg_map.get(status, f"Your application status for {app['job_title']} is now {status}."),
            notif_type
        )

        return True, f"Application status updated to '{status}'."
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)

# ---------------------------------------------------------
# Interview Management Helpers
# ---------------------------------------------------------
def schedule_interview(data):
    """Schedule a new interview for a candidate application."""
    app = get_application_by_id(data.get('application_id'))
    if not app:
        return False, "Application record not found."

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO interviews (
                application_id, job_id, company_id, student_reg,
                interview_type, interview_date, interview_time, location_or_link, notes, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Scheduled')
        ''', (
            app['id'],
            app['job_id'],
            app['company_id'],
            app['student_reg'],
            data.get('interview_type', 'Online'),
            data.get('interview_date'),
            data.get('interview_time'),
            data.get('location_or_link', ''),
            data.get('notes', ''),
        ))
        conn.commit()
        interview_id = cursor.lastrowid

        cursor.execute("UPDATE job_applications SET status = 'Interview Scheduled', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (app['id'],))
        conn.commit()
        conn.close()

        msg = f"Interview Scheduled! Company: {app['company_name']} | Role: {app['job_title']} | Mode: {data.get('interview_type')} | Date: {data.get('interview_date')} at {data.get('interview_time')}."
        if data.get('location_or_link'):
            msg += f" Details: {data.get('location_or_link')}"

        post_student_notification(
            app['student_reg'],
            f"📅 Interview Scheduled: {app['job_title']}",
            msg,
            'reminder'
        )

        return True, interview_id
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)

def get_interviews(company_id=None, student_reg=None, status=None):
    """Retrieve scheduled interviews with full context."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
        SELECT iv.*,
               a.match_score, a.status as app_status,
               j.title as job_title, j.salary_package,
               c.company_name, c.logo as company_logo,
               s.student_name, s.email as student_email, s.department, 'N/A' as student_phone
        FROM interviews iv
        JOIN job_applications a ON iv.application_id = a.id
        JOIN jobs j ON iv.job_id = j.id
        JOIN companies c ON iv.company_id = c.id
        JOIN student_users s ON iv.student_reg = s.register_number
        WHERE 1=1
    '''
    params = []

    if company_id:
        query += " AND iv.company_id = ?"
        params.append(company_id)
    if student_reg:
        query += " AND iv.student_reg = ?"
        params.append(student_reg)
    if status and status != 'All':
        query += " AND iv.status = ?"
        params.append(status)

    query += " ORDER BY iv.interview_date ASC, iv.interview_time ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_interview_status(interview_id, company_id, status):
    """Update interview status (Scheduled, Completed, Selected, Cancelled)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM interviews WHERE id = ? AND company_id = ?", (interview_id, company_id))
        iv = cursor.fetchone()
        if not iv:
            conn.close()
            return False, "Interview record not found."

        cursor.execute("UPDATE interviews SET status = ? WHERE id = ?", (status, interview_id))

        if status in ['Selected', 'Rejected']:
            cursor.execute("UPDATE job_applications SET status = ? WHERE id = ?", (status, iv['application_id']))

        conn.commit()
        conn.close()
        return True, f"Interview status updated to '{status}'."
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)

# ---------------------------------------------------------
# Notifications Helpers
# ---------------------------------------------------------
def post_student_notification(register_number, title, message, notif_type='info'):
    """Insert a notification for a student user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO student_notifications (register_number, title, message, type)
        VALUES (?, ?, ?, ?)
    ''', (register_number, title, message, notif_type))
    conn.commit()
    conn.close()

def notify_students_for_new_job(job_id):
    """Notify all students who match >= 60% with a newly posted job."""
    job = get_job_by_id(job_id)
    if not job or job['status'] != 'Active':
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_users")
    students = [dict(r) for r in cursor.fetchall()]
    conn.close()

    for stu in students:
        match_info = calculate_student_job_match(stu, job)
        if match_info['match_score'] >= 60.0:
            post_student_notification(
                stu['register_number'],
                f"New Job Opportunity: {job['title']}",
                f"{job['company_name']} posted a new opening for {job['title']} ({job['salary_package']}). Your profile has a {match_info['match_score']}% AI Match score!",
                'recommendation'
            )

# ---------------------------------------------------------
# Dashboard & Analytics Helpers for Company Portal
# ---------------------------------------------------------
def get_company_dashboard_stats(company_id):
    """Compute recruitment metrics summary for Company Dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total_jobs FROM jobs WHERE company_id = ?", (company_id,))
    total_jobs = cursor.fetchone()['total_jobs']

    cursor.execute("SELECT COUNT(*) as active_jobs FROM jobs WHERE company_id = ? AND status = 'Active'", (company_id,))
    active_jobs = cursor.fetchone()['active_jobs']

    cursor.execute("SELECT COUNT(*) as total_applicants FROM job_applications WHERE company_id = ?", (company_id,))
    total_applicants = cursor.fetchone()['total_applicants']

    cursor.execute("SELECT COUNT(*) as shortlisted FROM job_applications WHERE company_id = ? AND status = 'Shortlisted'", (company_id,))
    shortlisted = cursor.fetchone()['shortlisted']

    cursor.execute("SELECT COUNT(*) as interviews FROM job_applications WHERE company_id = ? AND status = 'Interview Scheduled'", (company_id,))
    interviews = cursor.fetchone()['interviews']

    cursor.execute("SELECT COUNT(*) as selected FROM job_applications WHERE company_id = ? AND status = 'Selected'", (company_id,))
    selected = cursor.fetchone()['selected']

    cursor.execute("SELECT COUNT(*) as rejected FROM job_applications WHERE company_id = ? AND status = 'Rejected'", (company_id,))
    rejected = cursor.fetchone()['rejected']

    conn.close()

    return {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applicants': total_applicants,
        'shortlisted': shortlisted,
        'interviews': interviews,
        'selected': selected,
        'rejected': rejected
    }

def get_company_analytics_data(company_id):
    """Generate dynamic JSON data for Chart.js analytics dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT j.title, COUNT(a.id) as count
        FROM jobs j
        LEFT JOIN job_applications a ON j.id = a.job_id
        WHERE j.company_id = ?
        GROUP BY j.id
    ''', (company_id,))
    job_rows = cursor.fetchall()
    job_labels = [r['title'] for r in job_rows]
    job_counts = [r['count'] for r in job_rows]

    cursor.execute('''
        SELECT status, COUNT(*) as count
        FROM job_applications
        WHERE company_id = ?
        GROUP BY status
    ''', (company_id,))
    status_rows = cursor.fetchall()
    status_dict = {r['status']: r['count'] for r in status_rows}

    cursor.execute('''
        SELECT s.department, COUNT(a.id) as count
        FROM job_applications a
        JOIN student_users s ON a.student_reg = s.register_number
        WHERE a.company_id = ?
        GROUP BY s.department
    ''', (company_id,))
    dept_rows = cursor.fetchall()
    dept_labels = [r['department'] for r in dept_rows]
    dept_counts = [r['count'] for r in dept_rows]

    cursor.execute('''
        SELECT
            CASE
                WHEN match_score >= 85 THEN '85% - 100% (High)'
                WHEN match_score >= 70 THEN '70% - 84% (Good)'
                WHEN match_score >= 55 THEN '55% - 69% (Average)'
                ELSE 'Below 55% (Low)'
            END as range_label,
            COUNT(*) as count
        FROM job_applications
        WHERE company_id = ?
        GROUP BY range_label
    ''', (company_id,))
    match_rows = cursor.fetchall()
    match_dict = {r['range_label']: r['count'] for r in match_rows}

    conn.close()

    return {
        'job_applications': {
            'labels': job_labels if job_labels else ['No Jobs'],
            'counts': job_counts if job_counts else [0]
        },
        'status_breakdown': {
            'Applied': status_dict.get('Applied', 0),
            'Shortlisted': status_dict.get('Shortlisted', 0),
            'Interview Scheduled': status_dict.get('Interview Scheduled', 0),
            'Selected': status_dict.get('Selected', 0),
            'Rejected': status_dict.get('Rejected', 0)
        },
        'department_breakdown': {
            'labels': dept_labels if dept_labels else ['Computer Science'],
            'counts': dept_counts if dept_counts else [0]
        },
        'match_distribution': {
            'labels': ['85% - 100% (High)', '70% - 84% (Good)', '55% - 69% (Average)', 'Below 55% (Low)'],
            'counts': [
                match_dict.get('85% - 100% (High)', 0),
                match_dict.get('70% - 84% (Good)', 0),
                match_dict.get('55% - 69% (Average)', 0),
                match_dict.get('Below 55% (Low)', 0)
            ]
        }
    }


# ---------------------------------------------------------
# Notification & Email Management Helpers
# ---------------------------------------------------------
def create_notification(user_type, user_id, title, message, notif_type='info', email_recipient=None, email_status='Demo Mode'):
    """
    Store an in-app notification and email log entry into SQLite.
    Prevents duplicate notifications for the same user within 1 minute.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id FROM notifications
        WHERE user_type = ? AND user_id = ? AND title = ?
          AND created_at >= datetime('now', '-1 minute')
    ''', (user_type, str(user_id), title))

    if cursor.fetchone():
        conn.close()
        return None

    try:
        cursor.execute('''
            INSERT INTO notifications (
                user_type, user_id, title, message, type, email_status, email_recipient
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_type, str(user_id), title, message, notif_type, email_status, email_recipient))
        conn.commit()
        notif_id = cursor.lastrowid
        conn.close()
        return notif_id
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"[ERROR] Failed to create notification: {e}")
        return None

def log_email_delivery(recipient, subject, body_html, status='Demo Mode', error_message=None):
    """Log outgoing email dispatch status."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO email_logs (recipient, subject, body_html, status, error_message)
            VALUES (?, ?, ?, ?, ?)
        ''', (recipient, subject, body_html, status, error_message))
        conn.commit()
        log_id = cursor.lastrowid
        conn.close()
        return log_id
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"[ERROR] Failed to log email delivery: {e}")
        return None

def get_user_notifications(user_type, user_id, is_read=None, limit=50):
    """Retrieve notifications for a user (student, company, or admin)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM notifications WHERE user_type = ? AND user_id = ?"
    params = [user_type, str(user_id)]

    if is_read is not None:
        query += " AND is_read = ?"
        params.append(1 if is_read else 0)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_unread_notification_count(user_type, user_id):
    """Count unread in-app notifications for bell counter badge."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) as count
        FROM notifications
        WHERE user_type = ? AND user_id = ? AND is_read = 0
    ''', (user_type, str(user_id)))
    res = cursor.fetchone()
    conn.close()
    return res['count'] if res else 0

def mark_notification_as_read(notif_id, user_type, user_id):
    """Mark a single notification as read."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE notifications SET is_read = 1
        WHERE id = ? AND user_type = ? AND user_id = ?
    ''', (notif_id, user_type, str(user_id)))
    conn.commit()
    conn.close()
    return True

def mark_all_notifications_read(user_type, user_id):
    """Mark all notifications as read for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE notifications SET is_read = 1
        WHERE user_type = ? AND user_id = ? AND is_read = 0
    ''', (user_type, str(user_id)))
    conn.commit()
    conn.close()
    return True

def delete_notification(notif_id, user_type, user_id):
    """Delete a notification record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM notifications
        WHERE id = ? AND user_type = ? AND user_id = ?
    ''', (notif_id, user_type, str(user_id)))
    conn.commit()
    conn.close()
    return True

def get_notification_analytics():
    """Compute aggregate analytics for notifications and email logs."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM notifications")
    total_notifs = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as unread FROM notifications WHERE is_read = 0")
    unread_notifs = cursor.fetchone()['unread']

    cursor.execute("SELECT COUNT(*) as total FROM email_logs")
    total_emails = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as sent FROM email_logs WHERE status IN ('Sent', 'Demo Mode')")
    sent_emails = cursor.fetchone()['sent']

    cursor.execute("SELECT COUNT(*) as failed FROM email_logs WHERE status = 'Failed'")
    failed_emails = cursor.fetchone()['failed']

    cursor.execute("SELECT * FROM email_logs ORDER BY sent_at DESC LIMIT 20")
    recent_emails = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        'total_notifications': total_notifs,
        'unread_notifications': unread_notifs,
        'total_emails': total_emails,
        'sent_emails': sent_emails,
        'failed_emails': failed_emails,
        'recent_emails': recent_emails
    }





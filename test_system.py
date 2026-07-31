import os
import json
import joblib
import unittest
import database
import train_model
import resume_analyzer
import mock_interview_engine
import notification_service

class SystemIntegrationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initialize test database and train ML model."""
        database.init_db()
        train_model.train_and_export_model()

    def test_01_database_tables_exist(self):
        """Verify all SQLite database tables are initialized properly."""
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]
        conn.close()

        expected_tables = ['students', 'student_users', 'admins', 'companies', 'jobs', 'job_applications', 'interviews', 'notifications', 'email_logs']
        for tbl in expected_tables:
            self.assertIn(tbl, tables, f"Database table {tbl} missing!")

    def test_02_admin_authentication(self):
        """Test default admin account authentication."""
        admin = database.verify_admin('admin', 'admin123')
        self.assertIsNotNone(admin)
        self.assertEqual(admin['username'], 'admin')

    def test_03_student_authentication(self):
        """Test student user verification."""
        student = database.verify_student('student@college.edu', 'student123')
        self.assertIsNotNone(student)
        self.assertEqual(student['register_number'], 'REG20261001')

    def test_04_company_authentication(self):
        """Test company recruiter authentication."""
        company = database.verify_company('company@techcorp.com', 'company123')
        self.assertIsNotNone(company)
        self.assertEqual(company['company_name'], 'TechCorp Innovations')

    def test_05_ai_placement_prediction_model(self):
        """Test Random Forest machine learning prediction artifacts."""
        model = joblib.load(os.path.join('models', 'model.pkl'))
        scaler = joblib.load(os.path.join('models', 'scaler.pkl'))
        with open(os.path.join('models', 'metrics.json'), 'r') as f:
            metrics = json.load(f)

        self.assertIsNotNone(model)
        self.assertIsNotNone(scaler)
        self.assertIn('accuracy', metrics)
        self.assertGreaterEqual(metrics['accuracy'], 0.70)

    def test_06_resume_analyzer_parser(self):
        """Test NLP keyword parsing and extraction logic of Resume Analyzer."""
        sample_resume_text = """
        Rahul Sharma
        rahul@college.edu | +91 98765 43210
        Education: B.Tech Computer Science and Engineering, CGPA 8.2
        Skills: Python, Java, React, SQL, Machine Learning, Data Structures, Flask, Git
        Projects: Student Placement Prediction System with Flask and Random Forest ML
        Experience: Web Development Intern at WebCraft Systems for 3 months
        Certifications: AWS Certified Developer
        """
        analysis = resume_analyzer.parse_resume_text(sample_resume_text)
        self.assertIn('skills', analysis)
        self.assertIn('Python', analysis['skills'])

    def test_07_mock_interview_evaluation(self):
        """Test AI Mock Interview answer grading engine."""
        q_obj = {
            'question': 'Explain lists vs tuples',
            'keywords': ['list', 'tuple', 'mutable', 'immutable']
        }
        res = mock_interview_engine.evaluate_text_answer(
            q_obj,
            "Lists are mutable and defined with square brackets, while tuples are immutable."
        )
        self.assertGreaterEqual(res['score'], 60.0)

    def test_08_company_job_and_candidate_matching(self):
        """Test AI candidate matching calculation between a job and student."""
        job = database.get_job_by_id(1)
        student = database.get_student_user('REG20261001')
        self.assertIsNotNone(job)
        self.assertIsNotNone(student)

        match = database.calculate_student_job_match(student, job)
        self.assertGreaterEqual(match['match_score'], 0.0)
        self.assertIn('matching_skills', match)

    def test_09_notification_and_email_service(self):
        """Test in-app notification creation and unread badge count."""
        notif_id = database.create_notification(
            'student', 'REG20261001', 'Test Integration Notification', 'Test message content', 'info'
        )
        unread_count = database.get_unread_notification_count('student', 'REG20261001')
        self.assertGreater(unread_count, 0)

if __name__ == '__main__':
    unittest.main()

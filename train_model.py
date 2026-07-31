import os
import json
import datetime
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import database

# Fixed departments list for one-hot encoding consistency
DEPARTMENTS = [
    'Computer Science and Engineering',
    'Information Technology',
    'Electronics and Communication Engineering',
    'Electrical and Electronics Engineering',
    'Mechanical Engineering',
    'Civil Engineering',
    'Artificial Intelligence and Data Science',
    'Other'
]

def setup_directories():
    """Ensure required directory structure and database exist."""
    directories = ['dataset', 'models', 'instance']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    database.init_db()

def generate_dataset(num_samples=1500, random_seed=42):
    """
    Generate a realistic synthetic student placement dataset with 13 fields.
    Includes intentional missing values (NaNs) to test preprocessing/imputation.
    """
    np.random.seed(random_seed)

    # 1. Generate identifiers
    student_names = [f"Student_{i+1}" for i in range(num_samples)]
    register_numbers = [f"REG{20260000 + i + 1}" for i in range(num_samples)]

    # 2. Generate features
    departments = np.random.choice(DEPARTMENTS, size=num_samples, p=[0.25, 0.15, 0.15, 0.10, 0.10, 0.08, 0.12, 0.05])
    cgpa = np.random.uniform(5.5, 9.8, num_samples)
    tenth_percentage = np.random.uniform(55.0, 98.0, num_samples)
    twelfth_percentage = np.random.uniform(55.0, 98.0, num_samples)

    aptitude_score = np.random.randint(40, 101, size=num_samples)
    coding_score = np.random.randint(35, 101, size=num_samples)

    communication_skill = np.random.choice(['Poor', 'Average', 'Good', 'Excellent'], size=num_samples, p=[0.10, 0.35, 0.40, 0.15])
    internship = np.random.choice(['Yes', 'No'], size=num_samples, p=[0.30, 0.70])

    certifications = np.random.choice([0, 1, 2, 3, 4, 5], size=num_samples, p=[0.40, 0.35, 0.15, 0.06, 0.03, 0.01])
    projects_completed = np.random.choice([0, 1, 2, 3, 4, 5], size=num_samples, p=[0.20, 0.35, 0.28, 0.12, 0.04, 0.01])
    backlogs = np.random.choice([0, 1, 2, 3, 4], size=num_samples, p=[0.70, 0.18, 0.07, 0.04, 0.01])

    # 3. Calculate composite placement probability score
    cgpa_norm = (cgpa - 5.5) / 4.3
    coding_norm = (coding_score - 35) / 65
    aptitude_norm = (aptitude_score - 40) / 60
    tenth_norm = (tenth_percentage - 55) / 43
    twelfth_norm = (twelfth_percentage - 55) / 43

    comm_value = np.array([{'Poor': 0.1, 'Average': 0.4, 'Good': 0.7, 'Excellent': 1.0}[c] for c in communication_skill])
    internship_value = np.array([1.0 if i == 'Yes' else 0.0 for i in internship])

    score = (
        cgpa_norm * 0.28 +
        coding_norm * 0.22 +
        aptitude_norm * 0.15 +
        ((tenth_norm + twelfth_norm) / 2.0) * 0.10 +
        internship_value * 0.10 +
        (projects_completed / 5.0) * 0.06 +
        comm_value * 0.05 +
        (certifications / 5.0) * 0.04 -
        (backlogs * 0.15)
    )

    noise = np.random.normal(0, 0.06, num_samples)
    final_score = score + noise

    placed = (final_score > 0.48).astype(int)

    df = pd.DataFrame({
        'student_name': student_names,
        'register_number': register_numbers,
        'department': departments,
        'cgpa': np.round(cgpa, 2),
        'tenth_percentage': np.round(tenth_percentage, 2),
        'twelfth_percentage': np.round(twelfth_percentage, 2),
        'aptitude_score': aptitude_score,
        'coding_score': coding_score,
        'communication_skill': communication_skill,
        'internship': internship,
        'certifications': certifications,
        'projects_completed': projects_completed,
        'backlogs': backlogs,
        'placed': placed
    })

    nan_cols = ['cgpa', 'coding_score', 'communication_skill', 'internship']
    for col in nan_cols:
        nan_indices = np.random.choice(num_samples, size=int(num_samples * 0.02), replace=False)
        df.loc[nan_indices, col] = np.nan

    dataset_path = os.path.join('dataset', 'placement.csv')
    df.to_csv(dataset_path, index=False)
    print(f"[INFO] Generated synthetic placement dataset at: {dataset_path}")
    return df

def preprocess_data(df, is_training=True, scaler=None):
    """
    Preprocess raw placement dataframe:
    1. Handles missing values (imputation).
    2. Encodes categorical variables.
    3. Standardizes/scales features.
    """
    df_clean = df.copy()

    num_cols = ['cgpa', 'tenth_percentage', 'twelfth_percentage', 'aptitude_score', 'coding_score', 'certifications', 'projects_completed', 'backlogs']
    for col in num_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            median_val = df_clean[col].median()
            df_clean[col] = df_clean[col].fillna(median_val if not pd.isna(median_val) else 7.0)

    cat_cols = ['department', 'communication_skill', 'internship']
    for col in cat_cols:
        if col in df_clean.columns:
            mode_val = df_clean[col].mode()[0] if not df_clean[col].mode().empty else 'Other'
            df_clean[col] = df_clean[col].fillna(mode_val)

    comm_map = {'Poor': 0, 'Average': 1, 'Good': 2, 'Excellent': 3}
    df_clean['communication_skill_encoded'] = df_clean['communication_skill'].map(comm_map).fillna(1).astype(int)
    df_clean['internship_encoded'] = df_clean['internship'].apply(lambda x: 1 if str(x).strip().lower() == 'yes' else 0)

    for dept in DEPARTMENTS:
        col_name = f"dept_{dept.replace(' ', '_').replace('&', 'and')}"
        df_clean[col_name] = (df_clean['department'] == dept).astype(int)

    feature_cols = [
        'cgpa', 'tenth_percentage', 'twelfth_percentage', 'aptitude_score', 'coding_score',
        'certifications', 'projects_completed', 'backlogs',
        'communication_skill_encoded', 'internship_encoded'
    ] + [f"dept_{dept.replace(' ', '_').replace('&', 'and')}" for dept in DEPARTMENTS]

    X = df_clean[feature_cols]

    if is_training:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        return X_scaled, scaler, feature_cols
    else:
        X_scaled = scaler.transform(X)
        return X_scaled

def train_and_export_model(csv_path=None):
    """Loads placement CSV data or database students, trains Random Forest, and exports model files."""
    setup_directories()
    if csv_path is None:
        csv_path = os.path.join('dataset', 'placement.csv')

    if not os.path.exists(csv_path):
        generate_dataset()

    print(f"[INFO] Loading dataset from: {csv_path}")
    df = pd.read_csv(csv_path)

    if 'placed' not in df.columns:
        if 'placement_status' in df.columns:
            df['placed'] = df['placement_status']
        else:
            df['placed'] = 0

    y = df['placed'].fillna(0).astype(int)

    X_scaled, scaler, feature_cols = preprocess_data(df, is_training=True)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)

    rf_model = RandomForestClassifier(
        n_estimators=150,
        max_depth=10,
        min_samples_split=4,
        random_state=42
    )

    print("[INFO] Training Random Forest Classifier...")
    rf_model.fit(X_train, y_train)

    y_pred = rf_model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred).tolist()

    importances = dict(zip(feature_cols, [round(float(imp), 4) for imp in rf_model.feature_importances_]))

    df_imputed = df.copy()
    df_imputed['placed'] = df_imputed['placed'].fillna(0)

    df_placed = df_imputed[df_imputed['placed'] == 1]
    df_unplaced = df_imputed[df_imputed['placed'] == 0]

    placed_avg = {
        'cgpa': round(float(df_placed['cgpa'].mean()), 2) if not df_placed.empty else 7.5,
        'aptitude_score': round(float(df_placed['aptitude_score'].mean()), 1) if not df_placed.empty else 75.0,
        'coding_score': round(float(df_placed['coding_score'].mean()), 1) if not df_placed.empty else 75.0,
        'projects': round(float(df_placed['projects_completed'].mean()), 1) if not df_placed.empty else 2.5,
        'soft_skills_score': round(float(df_placed['communication_skill'].map({'Poor': 1.5, 'Average': 2.8, 'Good': 4.0, 'Excellent': 5.0}).mean()), 2) if not df_placed.empty else 3.5,
        'internships': round(float(df_placed['internship'].apply(lambda x: 1 if str(x).strip().lower() == 'yes' else 0).mean()), 2) if not df_placed.empty else 0.5
    }

    unplaced_avg = {
        'cgpa': round(float(df_unplaced['cgpa'].mean()), 2) if not df_unplaced.empty else 6.2,
        'aptitude_score': round(float(df_unplaced['aptitude_score'].mean()), 1) if not df_unplaced.empty else 55.0,
        'coding_score': round(float(df_unplaced['coding_score'].mean()), 1) if not df_unplaced.empty else 50.0,
        'projects': round(float(df_unplaced['projects_completed'].mean()), 1) if not df_unplaced.empty else 1.0,
        'soft_skills_score': round(float(df_unplaced['communication_skill'].map({'Poor': 1.5, 'Average': 2.8, 'Good': 4.0, 'Excellent': 5.0}).mean()), 2) if not df_unplaced.empty else 2.5,
        'internships': round(float(df_unplaced['internship'].apply(lambda x: 1 if str(x).strip().lower() == 'yes' else 0).mean()), 2) if not df_unplaced.empty else 0.1
    }

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    model_path1 = os.path.join('models', 'model.pkl')
    model_path2 = os.path.join('models', 'placement_model.pkl')
    scaler_path = os.path.join('models', 'scaler.pkl')
    metrics_path = os.path.join('models', 'metrics.json')

    joblib.dump(rf_model, model_path1)
    joblib.dump(rf_model, model_path2)
    joblib.dump(scaler, scaler_path)

    metrics_data = {
        'algorithm': 'Random Forest',
        'accuracy': round(float(acc), 4),
        'precision': round(float(prec), 4),
        'recall': round(float(rec), 4),
        'f1_score': round(float(f1), 4),
        'confusion_matrix': cm,
        'feature_importances': importances,
        'placed_averages': placed_avg,
        'unplaced_averages': unplaced_avg,
        'total_samples': len(df),
        'placed_count': int(y.sum()),
        'unplaced_count': int(len(df) - y.sum()),
        'trained_at': timestamp
    }

    with open(metrics_path, 'w') as f:
        json.dump(metrics_data, f, indent=4)

    # Log to SQLite
    try:
        database.log_model_metadata('Random Forest', acc, prec, rec, f1, len(df))
    except Exception as e:
        print(f"[WARNING] Could not log model metadata to database: {e}")

    print(f"[SUCCESS] Retrained Random Forest model. Accuracy: {acc*100:.2f}%")
    return metrics_data

if __name__ == '__main__':
    train_and_export_model()

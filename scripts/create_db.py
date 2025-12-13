import sqlite3
from pathlib import Path

db_path = Path("dondieplz.db")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("PRAGMA foreign_keys = ON;")

cur.execute("""
CREATE TABLE IF NOT EXISTS synthetic_cases (
    case_id TEXT PRIMARY KEY,
    text TEXT NOT NULL,
    language TEXT DEFAULT 'pt',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS extraction_runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    extractor_version TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS extracted_outputs (
    output_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    case_id TEXT NOT NULL,
    suicidal_ideation_presence TEXT,
    evidence_json TEXT,
    uncertainty_cues_json TEXT,
    missing_information_json TEXT,
    raw_output_json TEXT,
    FOREIGN KEY (run_id) REFERENCES extraction_runs(run_id),
    FOREIGN KEY (case_id) REFERENCES synthetic_cases(case_id)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS framework_projections (
    projection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    output_id INTEGER NOT NULL,
    framework TEXT NOT NULL,
    projection_json TEXT NOT NULL,
    FOREIGN KEY (output_id) REFERENCES extracted_outputs(output_id)
);
""")

conn.commit()
conn.close()

print("Banco criado em:", db_path.resolve())

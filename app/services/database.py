import sqlite3
from pathlib import Path

DB_PATH = Path("data/application.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id TEXT PRIMARY KEY,
        full_name TEXT,
        monthly_income REAL,
        requested_loan REAL,
        credit_score INTEGER,
        risk_score REAL,
        decision TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        review_status TEXT DEFAULT 'PENDING',
        reviewed_by TEXT,
        review_note TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_application(
        app_id,
        full_name,
        monthly_income,
        requested_loan,
        credit_score,
        risk_score,
        decision,
):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO applications (
        id,
        full_name,
        monthly_income,
        requested_loan,
        credit_score,
        risk_score,
        decision
        )
    VALUES (?,?,?,?,?,?,?)
    """, (
        app_id,
        full_name,
        monthly_income,
        requested_loan,
        credit_score,
        risk_score,
        decision,
    ))

    conn.commit()
    conn.close()

def get_all_applications():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    rows = cur.execute("""
    SELECT * FROM applications
    ORDER BY created_at DESC
    """).fetchall()

    conn.close()
    return rows

def get_application(application_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    row = cur.execute("""
    SELECT * FROM applications
    WHERE id=?
    """,(
        application_id,
    )).fetchone()

    conn.close()
    return row

def get_pending_reviews():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    rows = cur.execute("""
    SELECT * FROM applications
    WHERE decision = 'MANUAL_REVIEW'
    AND review_status = 'PENDING'
    ORDER BY created_at DESC
    """).fetchall()

    conn.close()
    return rows

def resolve_review(app_id, final_decision, reviewer, note):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    UPDATE applications
    SET review_status = 'COMPLETED',
        decision = ?,
        reviewed_by = ?,
        review_note = ?
    WHERE id=?
    """, (
        final_decision,
        reviewer,
        note,
        app_id,
    ))

    conn.commit()
    conn.close()

def init_audit_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        application_id INTEGER,
        action TEXT,
        actor TEXT,
        note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def insert_audit(application_id, action, actor, note):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO audit_logs (
        application_id,
        action,
        actor,
        note
        )
    VALUES (?,?,?,?)
    """,(
        application_id,
        action,
        actor,
        note
    ))

    conn.commit()
    conn.close()



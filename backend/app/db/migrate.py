"""Database migration: Add adaptive interview columns to sessions table."""

import os
import sqlite3
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./candidate_screening.db")

def migrate():
    """Add missing columns to sessions and session_evaluations tables."""
    
    if "sqlite" in DATABASE_URL:
        # Extract database path from SQLite URL
        db_path = DATABASE_URL.replace("sqlite:///", "")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Migrate sessions table
            print("Migrating 'sessions' table...")
            cursor.execute("PRAGMA table_info(sessions)")
            existing_columns = {row[1] for row in cursor.fetchall()}
            
            sessions_columns = [
                ("confidence_score", "REAL DEFAULT 0.5"),
                ("consecutive_bad_answers", "INTEGER DEFAULT 0"),
                ("interview_terminated_early", "INTEGER DEFAULT 0"),
                ("termination_reason", "VARCHAR(255)")
            ]
            
            for col_name, col_def in sessions_columns:
                if col_name not in existing_columns:
                    alter_sql = f"ALTER TABLE sessions ADD COLUMN {col_name} {col_def}"
                    print(f"  Adding column: {col_name}")
                    cursor.execute(alter_sql)
                else:
                    print(f"  Column {col_name} already exists, skipping")
            
            # Migrate session_evaluations table
            print("Migrating 'session_evaluations' table...")
            cursor.execute("PRAGMA table_info(session_evaluations)")
            existing_columns = {row[1] for row in cursor.fetchall()}
            
            evaluation_columns = [
                ("overall_score", "REAL"),
                ("hiring_recommendation", "VARCHAR(50)"),
                ("topic_wise_breakdown", "JSON"),
                ("communication_assessment", "JSON"),
                ("learning_path", "JSON"),
                ("early_termination", "INTEGER DEFAULT 0"),
                ("termination_reason", "VARCHAR(255)")
            ]
            
            for col_name, col_def in evaluation_columns:
                if col_name not in existing_columns:
                    alter_sql = f"ALTER TABLE session_evaluations ADD COLUMN {col_name} {col_def}"
                    print(f"  Adding column: {col_name}")
                    cursor.execute(alter_sql)
                else:
                    print(f"  Column {col_name} already exists, skipping")
            
            conn.commit()
            conn.close()
            print("✓ Migration completed successfully!")
            
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            raise
    else:
        # For other databases, use SQLAlchemy
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        
        try:
            with engine.connect() as connection:
                # Check if columns exist in sessions
                cursor = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'sessions'"))
                existing_columns = {row[0] for row in cursor.fetchall()}
                
                sessions_columns = [
                    ("confidence_score", "REAL DEFAULT 0.5"),
                    ("consecutive_bad_answers", "INTEGER DEFAULT 0"),
                    ("interview_terminated_early", "INTEGER DEFAULT 0"),
                    ("termination_reason", "VARCHAR(255)")
                ]
                
                for col_name, col_def in sessions_columns:
                    if col_name not in existing_columns:
                        alter_sql = f"ALTER TABLE sessions ADD COLUMN {col_name} {col_def}"
                        print(f"Adding column to sessions: {col_name}")
                        connection.execute(text(alter_sql))
                        connection.commit()
                    else:
                        print(f"Column {col_name} already exists in sessions, skipping")
                
                # Check if columns exist in session_evaluations
                cursor = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'session_evaluations'"))
                existing_columns = {row[0] for row in cursor.fetchall()}
                
                evaluation_columns = [
                    ("overall_score", "REAL"),
                    ("hiring_recommendation", "VARCHAR(50)"),
                    ("topic_wise_breakdown", "JSON"),
                    ("communication_assessment", "JSON"),
                    ("learning_path", "JSON"),
                    ("early_termination", "INTEGER DEFAULT 0"),
                    ("termination_reason", "VARCHAR(255)")
                ]
                
                for col_name, col_def in evaluation_columns:
                    if col_name not in existing_columns:
                        alter_sql = f"ALTER TABLE session_evaluations ADD COLUMN {col_name} {col_def}"
                        print(f"Adding column to session_evaluations: {col_name}")
                        connection.execute(text(alter_sql))
                        connection.commit()
                    else:
                        print(f"Column {col_name} already exists in session_evaluations, skipping")
                
                print("✓ Migration completed successfully!")
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            raise

if __name__ == "__main__":
    migrate()

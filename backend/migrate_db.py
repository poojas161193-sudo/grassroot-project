"""
Database Migration Script
Adds new columns to existing videos table
"""
import sqlite3
from decouple import config

DATABASE_URL = config('DATABASE_URL', default='sqlite:///./video_analyzer.db')
db_path = DATABASE_URL.replace('sqlite:///', '')


def migrate_database():
    """Add new columns to videos table"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if columns exist
        cursor.execute("PRAGMA table_info(videos)")
        columns = [column[1] for column in cursor.fetchall()]

        # Add processing_status column
        if 'processing_status' not in columns:
            cursor.execute("""
                ALTER TABLE videos
                ADD COLUMN processing_status TEXT DEFAULT 'completed'
            """)
            print("✓ Added processing_status column")

        # Add error_message column
        if 'error_message' not in columns:
            cursor.execute("""
                ALTER TABLE videos
                ADD COLUMN error_message TEXT
            """)
            print("✓ Added error_message column")

        # Add processed_at column
        if 'processed_at' not in columns:
            cursor.execute("""
                ALTER TABLE videos
                ADD COLUMN processed_at TIMESTAMP
            """)
            print("✓ Added processed_at column")

        # Update existing records
        cursor.execute("""
            UPDATE videos
            SET processing_status = 'completed',
                processed_at = uploaded_at
            WHERE processing_status IS NULL
        """)

        conn.commit()
        print("\n✓ Migration completed successfully!")

    except Exception as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    print("Starting database migration...")
    migrate_database()

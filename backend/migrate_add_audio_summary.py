"""
Database Migration: Add Audio Summary Support
Adds columns for storing TTS-generated audio summaries
"""
import sqlite3
import os

def migrate_add_audio_summary():
    """Add audio summary columns to videos table"""

    # Get database path from current directory
    db_path = os.path.join(os.path.dirname(__file__), 'video_analyzer.db')

    print("=" * 70)
    print("DATABASE MIGRATION: Audio Summary Support")
    print("=" * 70)
    print(f"📊 Database: {db_path}\n")

    if not os.path.exists(db_path):
        print("❌ Error: Database file not found!")
        print(f"   Expected location: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Add audio_summary_path column
        print("📝 Adding 'audio_summary_path' column...")
        cursor.execute("""
            ALTER TABLE videos
            ADD COLUMN audio_summary_path TEXT
        """)
        print("   ✅ Column 'audio_summary_path' added successfully")

    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("   ⚠️  Column 'audio_summary_path' already exists")
        else:
            print(f"   ❌ Error adding 'audio_summary_path': {e}")
            conn.close()
            return False

    try:
        # Add audio_summary_duration column
        print("📝 Adding 'audio_summary_duration' column...")
        cursor.execute("""
            ALTER TABLE videos
            ADD COLUMN audio_summary_duration REAL
        """)
        print("   ✅ Column 'audio_summary_duration' added successfully")

    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("   ⚠️  Column 'audio_summary_duration' already exists")
        else:
            print(f"   ❌ Error adding 'audio_summary_duration': {e}")
            conn.close()
            return False

    # Commit changes
    conn.commit()
    print("\n✅ DATABASE MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 70)

    # Verify columns were added
    cursor.execute("PRAGMA table_info(videos)")
    columns = cursor.fetchall()
    print("\n📋 Current 'videos' table schema:")
    for col in columns:
        print(f"   - {col[1]} ({col[2]})")

    conn.close()
    return True

if __name__ == "__main__":
    success = migrate_add_audio_summary()
    exit(0 if success else 1)

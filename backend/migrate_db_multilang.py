"""
Database migration script to add multi-language support fields
Run this script to update existing database with new language columns
"""
from sqlalchemy import create_engine, text, inspect
from decouple import config

DATABASE_URL = config('DATABASE_URL', default='sqlite:///./video_analyzer.db')

def column_exists(engine, table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def migrate_database():
    """Add new language-related columns to existing tables"""

    print("=" * 70)
    print("DATABASE MIGRATION: Multi-Language Support")
    print("=" * 70)
    print(f"\nDatabase: {DATABASE_URL}")
    print("\nStarting migration...\n")

    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

    with engine.connect() as conn:
        # ========== VIDEOS TABLE MIGRATION ==========
        print("📊 Migrating 'videos' table...")

        # Add detected_language column
        if not column_exists(engine, 'videos', 'detected_language'):
            conn.execute(text("ALTER TABLE videos ADD COLUMN detected_language VARCHAR(10)"))
            print("  ✅ Added column: detected_language")
        else:
            print("  ⚠️  Column already exists: detected_language (skipping)")

        # Add user_selected_language column
        if not column_exists(engine, 'videos', 'user_selected_language'):
            conn.execute(text("ALTER TABLE videos ADD COLUMN user_selected_language VARCHAR(10)"))
            print("  ✅ Added column: user_selected_language")
        else:
            print("  ⚠️  Column already exists: user_selected_language (skipping)")

        # Add ui_language column
        if not column_exists(engine, 'videos', 'ui_language'):
            conn.execute(text("ALTER TABLE videos ADD COLUMN ui_language VARCHAR(10) DEFAULT 'en'"))
            # Update existing records to have default value
            conn.execute(text("UPDATE videos SET ui_language = 'en' WHERE ui_language IS NULL"))
            print("  ✅ Added column: ui_language (default: 'en')")
        else:
            print("  ⚠️  Column already exists: ui_language (skipping)")

        # Add transcription_method column
        if not column_exists(engine, 'videos', 'transcription_method'):
            conn.execute(text("ALTER TABLE videos ADD COLUMN transcription_method VARCHAR(50)"))
            print("  ✅ Added column: transcription_method")
        else:
            print("  ⚠️  Column already exists: transcription_method (skipping)")

        # ========== CHAT_HISTORY TABLE MIGRATION ==========
        print("\n💬 Migrating 'chat_history' table...")

        # Add language column
        if not column_exists(engine, 'chat_history', 'language'):
            conn.execute(text("ALTER TABLE chat_history ADD COLUMN language VARCHAR(10) DEFAULT 'en'"))
            # Update existing records to have default value
            conn.execute(text("UPDATE chat_history SET language = 'en' WHERE language IS NULL"))
            print("  ✅ Added column: language (default: 'en')")
        else:
            print("  ⚠️  Column already exists: language (skipping)")

        conn.commit()

    # Verify migration
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)

    inspector = inspect(engine)

    print("\n📊 Videos table columns:")
    videos_columns = [col['name'] for col in inspector.get_columns('videos')]
    for col in videos_columns:
        marker = "🆕" if col in ['detected_language', 'user_selected_language', 'ui_language', 'transcription_method'] else "  "
        print(f"  {marker} {col}")

    print("\n💬 Chat_history table columns:")
    chat_columns = [col['name'] for col in inspector.get_columns('chat_history')]
    for col in chat_columns:
        marker = "🆕" if col == 'language' else "  "
        print(f"  {marker} {col}")

    print("\n" + "=" * 70)
    print("✅ DATABASE MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\nYour database is now ready for multi-language support!")
    print("All existing data has been preserved.\n")

if __name__ == "__main__":
    try:
        migrate_database()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("Please check the error and try again.\n")
        raise

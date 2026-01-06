"""
Initialize PostgreSQL database with all tables

Run this script after setting up your PostgreSQL database:
    python init_db.py
"""

from database import engine, Base
from models import User, Project, Lead, VisitorSession, VisitorEvent, LeadScore


def init_database():
    """
    Creates all tables in the database.
    Safe to run multiple times - will only create tables that don't exist.
    """
    print("Creating database tables...")
    
    try:
        # Import all models so they're registered with Base
        # This ensures all tables are created
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database tables created successfully!")
        print("\nTables created:")
        print("  - users")
        print("  - projects")
        print("  - leads")
        print("  - visitor_sessions")
        print("  - visitor_events")
        print("  - lead_scores")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise


def drop_all_tables():
    """
    WARNING: This will delete all tables and data!
    Use only in development.
    """
    response = input("⚠️  WARNING: This will DELETE ALL TABLES and DATA! Type 'DELETE' to confirm: ")
    
    if response == "DELETE":
        print("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped")
    else:
        print("Operation cancelled")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--drop":
        drop_all_tables()
    else:
        init_database()

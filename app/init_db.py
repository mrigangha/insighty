from app.core.database import engine, Base
from app.models import User, Project, Lead, VisitorSession, VisitorEvent, LeadScore


def init_database():
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
        print("Tables: users, projects, leads, visitor_sessions, visitor_events, lead_scores")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise


def drop_all_tables():
    response = input("WARNING: This will DELETE ALL TABLES and DATA! Type 'DELETE' to confirm: ")
    if response == "DELETE":
        print("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("All tables dropped")
    else:
        print("Operation cancelled")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--drop":
        drop_all_tables()
    else:
        init_database()

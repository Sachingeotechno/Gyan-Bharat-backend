from sqlalchemy import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)

def add_columns():
    with engine.begin() as conn:
        # Check if column exists first to avoid error
        try:
            conn.execute(text("ALTER TABLE lessons ADD COLUMN is_locked BOOLEAN DEFAULT FALSE"))
            print("Added is_locked column")
        except Exception as e:
            print(f"Could not add column (might already exist): {e}")

if __name__ == "__main__":
    add_columns()

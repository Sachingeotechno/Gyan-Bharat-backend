from app.database import engine
from sqlalchemy import text

def add_columns():
    with engine.begin() as conn:
        # List of columns to add and their types
        columns = [
            ("subtitle", "VARCHAR(255)"),
            ("banner_image", "VARCHAR(500)"),
            ("video_intro_url", "VARCHAR(500)"),
            ("category", "VARCHAR(100)"),
            ("subcategory", "VARCHAR(100)"),
            ("tags", "TEXT")
        ]

        for col_name, col_type in columns:
            try:
                # Try adding the column. This syntax works for SQLite and Postgres
                print(f"Adding column {col_name}...")
                conn.execute(text(f"ALTER TABLE courses ADD COLUMN {col_name} {col_type}"))
                print(f"Added {col_name}")
            except Exception as e:
                # Ignore if column likely exists
                print(f"Could not add {col_name} (might already exist): {e}")

if __name__ == "__main__":
    print("Starting migration...")
    add_columns()
    print("Migration finished.")

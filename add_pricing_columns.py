from sqlalchemy import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)

def add_columns():
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE courses ADD COLUMN discount_price FLOAT DEFAULT 0.0"))
            print("Added discount_price column")
        except Exception as e:
            print(f"Could not add discount_price: {e}")

        try:
            conn.execute(text("ALTER TABLE courses ADD COLUMN offer_price FLOAT DEFAULT 0.0"))
            print("Added offer_price column")
        except Exception as e:
            print(f"Could not add offer_price: {e}")
            
        try:
            conn.execute(text("ALTER TABLE courses ADD COLUMN is_free BOOLEAN DEFAULT FALSE"))
            print("Added is_free column")
        except Exception as e:
            print(f"Could not add is_free: {e}")

if __name__ == "__main__":
    add_columns()

from sqlalchemy import inspect
from app.database import engine

def check_columns():
    inspector = inspect(engine)
    columns = inspector.get_columns('lessons')
    col_names = [col['name'] for col in columns]
    print(f"Columns in lessons table: {col_names}")
    
    needed = ['duration', 'is_preview', 'is_locked']
    for col in needed:
        print(f"Column '{col}' exists: {col in col_names}")

if __name__ == "__main__":
    check_columns()

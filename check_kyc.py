from app.database import SessionLocal
from app.models.models_kyc import College
from sqlalchemy import func

def check_data():
    db = SessionLocal()
    count = db.query(College).count()
    print(f"Total Colleges: {count}")
    
    # Group by state
    states = db.query(College.state, func.count(College.id)).group_by(College.state).all()
    for state, c in states:
        print(f"State: {state}, Count: {c}")
    
    db.close()

if __name__ == "__main__":
    check_data()

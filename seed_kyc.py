from app.database import SessionLocal, init_db, engine
from app.models.models_kyc import College, StandardCourse
from app.models.user import Base # Import Base to create tables

# Ensure tables are created
# Ideally main.py does this, but for script we might need to manually trigger if running standalone without main.
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    try:
        # Clear existing non-essential data
        print("Cleaning up medical KYC data...")
        
        # Reset user profiles to avoid FK violations
        from app.models.user import UserProfile
        db.query(UserProfile).update({UserProfile.college_id: None})
        
        # Reset course_id if it's not Class 6, 7 or 9
        classes_to_keep = ['Class 6', 'Class 7', 'Class 9']
        keep_ids = [c.id for c in db.query(StandardCourse).filter(StandardCourse.name.in_(classes_to_keep)).all()]
        
        db.query(UserProfile).filter(~UserProfile.course_id.in_(keep_ids)).update({UserProfile.course_id: None}, synchronize_session=False)
        db.commit()

        # Delete from KYC tables
        db.query(StandardCourse).filter(~StandardCourse.name.in_(classes_to_keep)).delete(synchronize_session=False)
        db.query(College).delete()
        db.commit()

        # Ensure Class 6, 7 and 9 exist
        for name in classes_to_keep:
            exists = db.query(StandardCourse).filter(StandardCourse.name == name).first()
            if not exists:
                db.add(StandardCourse(name=name, description=f"JNVST {name} Entrance Exam"))
        
        db.commit()
        print("Updated KYC: Only Class 6, 7 & 9 kept.")

        # Seed Colleges (Empty as requested)
        colleges = [] 

        
        if colleges:
            db.add_all(colleges)
            db.commit()
            print("Seeded Colleges.")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()

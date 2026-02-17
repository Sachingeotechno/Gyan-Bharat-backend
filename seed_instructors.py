from app.database import SessionLocal
from app.models.user import User, UserRole, UserProfile
from app.utils.security import hash_password
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_instructors():
    db = SessionLocal()
    try:
        instructors_to_add = [
            {
                "email": "amit.kumar@example.com",
                "full_name": "Amit Kumar",
                "phone": "9876543210",
                "bio": "Expert in Mathematics with 10+ years of experience in JNVST coaching."
            },
            {
                "email": "priya.sharma@example.com",
                "full_name": "Priya Sharma",
                "phone": "9876543211",
                "bio": "Specialist in Mental Ability and Logical Reasoning."
            }
        ]

        for data in instructors_to_add:
            # Check if user exists
            user = db.query(User).filter(User.email == data["email"]).first()
            if not user:
                user = User(
                    email=data["email"],
                    password_hash=hash_password("password123"),
                    role=UserRole.INSTRUCTOR,
                    is_verified=True
                )
                db.add(user)
                db.flush() # Get user id

                profile = UserProfile(
                    user_id=user.id,
                    full_name=data["full_name"],
                    phone=data["phone"],
                    bio=data["bio"]
                )
                db.add(profile)
                logger.info(f"Added instructor: {data['full_name']}")
            else:
                logger.info(f"Instructor already exists: {data['full_name']}")
        
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding instructors: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_instructors()

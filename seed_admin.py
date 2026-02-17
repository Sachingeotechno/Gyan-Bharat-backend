from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User, UserRole, UserProfile
from app.utils.security import hash_password
from app.utils.helpers import generate_verification_token

def seed_admin():
    db = SessionLocal()
    try:
        email = "admin@example.com"
        password = "password"
        
        # Check if admin already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"Admin user {email} already exists")
            # Ensure role is admin
            if existing_user.role != UserRole.ADMIN:
                existing_user.role = UserRole.ADMIN
                db.commit()
                print("Updated existing user to ADMIN role")
            return

        # Create admin user
        user = User(
            email=email,
            password_hash=hash_password(password),
            verification_token=generate_verification_token(),
            role=UserRole.ADMIN,
            is_verified=True
        )
        db.add(user)
        db.flush()
        
        # Create profile
        profile = UserProfile(
            user_id=user.id,
            full_name="Admin User"
        )
        db.add(profile)
        db.commit()
        print(f"Admin user created successfully: {email}")
        
    except Exception as e:
        print(f"Error seeding admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()

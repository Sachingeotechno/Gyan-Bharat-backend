from app.database import SessionLocal
from app.models.models_kyc import College

STATES = [
    "Andaman and Nicobar Islands", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", 
    "Chandigarh", "Chhattisgarh", "Dadra and Nagar Haveli", "Daman and Diu", "Delhi", "Goa", 
    "Gujarat", "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Jharkhand", "Karnataka", 
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", 
    "Odisha", "Pondicherry", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", 
    "Uttar Pradesh", "Uttarakhand", "West Bengal", "Foreign"
]

def seed_full_colleges():
    db = SessionLocal()
    
    new_colleges = []
    
    for state in STATES:
        # Check if state already has colleges
        existing = db.query(College).filter(College.state == state).count()
        if existing > 0:
            print(f"Skipping {state}, already has {existing} colleges.")
            continue
            
        print(f"Seeding for {state}...")
        # Create generic dummy colleges
        for i in range(1, 4):
            new_colleges.append(College(
                name=f"Government Medical College, {state} {i}",
                state=state,
                city=f"{state} City"
            ))
            new_colleges.append(College(
                name=f"All India Institute of Medical Sciences, {state}",
                state=state,
                city=f"{state} City"
            ))

    if new_colleges:
        db.add_all(new_colleges)
        db.commit()
        print(f"Added {len(new_colleges)} new colleges.")
    else:
        print("No new colleges needed.")
    
    db.close()

if __name__ == "__main__":
    seed_full_colleges()

"""
Seed script to populate QBank with dummy data
- Creates subjects
- Creates modules for each subject
- Creates 5 questions for each module
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.subject import Subject
from app.models.module import Module
from app.models.question import Question
from datetime import datetime

# Sample data
SUBJECTS_DATA = [
    {
        "name": "Physics",
        "description": "Fundamental concepts of Physics for competitive exams",
        "modules": [
            {"name": "Mechanics", "description": "Laws of motion, force, and energy"},
            {"name": "Thermodynamics", "description": "Heat, temperature, and energy transfer"},
            {"name": "Electromagnetism", "description": "Electric and magnetic fields"},
            {"name": "Optics", "description": "Light, reflection, and refraction"},
        ]
    },
    {
        "name": "Chemistry",
        "description": "Chemical principles and reactions",
        "modules": [
            {"name": "Organic Chemistry", "description": "Carbon compounds and reactions"},
            {"name": "Inorganic Chemistry", "description": "Elements and their compounds"},
            {"name": "Physical Chemistry", "description": "Chemical kinetics and equilibrium"},
            {"name": "Analytical Chemistry", "description": "Qualitative and quantitative analysis"},
        ]
    },
    {
        "name": "Mathematics",
        "description": "Mathematical concepts and problem solving",
        "modules": [
            {"name": "Algebra", "description": "Equations, polynomials, and functions"},
            {"name": "Calculus", "description": "Differentiation and integration"},
            {"name": "Geometry", "description": "Shapes, angles, and spatial reasoning"},
            {"name": "Statistics", "description": "Data analysis and probability"},
        ]
    },
    {
        "name": "Biology",
        "description": "Life sciences and biological systems",
        "modules": [
            {"name": "Cell Biology", "description": "Structure and function of cells"},
            {"name": "Genetics", "description": "Heredity and variation"},
            {"name": "Ecology", "description": "Organisms and their environment"},
            {"name": "Human Physiology", "description": "Body systems and functions"},
        ]
    },
    {
        "name": "General Knowledge",
        "description": "Current affairs and general awareness",
        "modules": [
            {"name": "Indian History", "description": "Ancient to modern Indian history"},
            {"name": "Geography", "description": "Physical and political geography"},
            {"name": "Current Affairs", "description": "Recent events and developments"},
            {"name": "Indian Polity", "description": "Constitution and governance"},
        ]
    }
]

# Sample questions templates
QUESTION_TEMPLATES = [
    {
        "text": "What is the fundamental principle of {topic}?",
        "options": ["Option A: First principle", "Option B: Second principle", "Option C: Third principle", "Option D: Fourth principle"],
        "correct": "A",
        "explanation": "The fundamental principle is the first principle which forms the basis of {topic}.",
        "difficulty": "easy"
    },
    {
        "text": "Which of the following best describes {topic}?",
        "options": ["Option A: Definition 1", "Option B: Definition 2", "Option C: Definition 3", "Option D: Definition 4"],
        "correct": "B",
        "explanation": "Definition 2 accurately describes {topic} based on standard definitions.",
        "difficulty": "medium"
    },
    {
        "text": "In {topic}, what is the relationship between X and Y?",
        "options": ["Option A: Direct proportion", "Option B: Inverse proportion", "Option C: No relation", "Option D: Exponential"],
        "correct": "A",
        "explanation": "X and Y are directly proportional in {topic} according to the fundamental law.",
        "difficulty": "medium"
    },
    {
        "text": "Advanced concept: What happens when applying {topic} in extreme conditions?",
        "options": ["Option A: System breaks down", "Option B: System stabilizes", "Option C: System oscillates", "Option D: System transforms"],
        "correct": "C",
        "explanation": "Under extreme conditions, {topic} causes the system to oscillate due to feedback mechanisms.",
        "difficulty": "hard"
    },
    {
        "text": "Which scientist/mathematician is most associated with {topic}?",
        "options": ["Option A: Newton", "Option B: Einstein", "Option C: Euler", "Option D: Gauss"],
        "correct": "A",
        "explanation": "Newton made significant contributions to the development of {topic}.",
        "difficulty": "easy"
    }
]


def seed_qbank():
    """Seed the QBank with subjects, modules, and questions"""
    db = SessionLocal()
    
    try:
        print("Starting QBank data seeding...")
        print("=" * 60)
        
        total_subjects = 0
        total_modules = 0
        total_questions = 0
        
        for subject_data in SUBJECTS_DATA:
            # Check if subject already exists
            existing_subject = db.query(Subject).filter(Subject.name == subject_data["name"]).first()
            
            if existing_subject:
                print(f"\n✓ Subject '{subject_data['name']}' already exists (ID: {existing_subject.id})")
                subject = existing_subject
            else:
                # Create subject
                subject = Subject(
                    name=subject_data["name"],
                    description=subject_data["description"],
                    created_at=datetime.utcnow()
                )
                db.add(subject)
                db.commit()
                db.refresh(subject)
                total_subjects += 1
                print(f"\n✓ Created subject: {subject.name} (ID: {subject.id})")
            
            # Create modules for this subject
            for idx, module_data in enumerate(subject_data["modules"]):
                # Check if module already exists
                existing_module = db.query(Module).filter(
                    Module.name == module_data["name"],
                    Module.subject_id == subject.id
                ).first()
                
                if existing_module:
                    print(f"  ✓ Module '{module_data['name']}' already exists")
                    module = existing_module
                else:
                    module = Module(
                        name=module_data["name"],
                        description=module_data["description"],
                        subject_id=subject.id,
                        order=idx,
                        created_at=datetime.utcnow()
                    )
                    db.add(module)
                    db.commit()
                    db.refresh(module)
                    total_modules += 1
                    print(f"  ✓ Created module: {module.name} (ID: {module.id})")
                
                # Check how many questions already exist for this module
                existing_questions_count = db.query(Question).filter(
                    Question.module_id == module.id
                ).count()
                
                if existing_questions_count >= 5:
                    print(f"    ✓ Module already has {existing_questions_count} questions")
                    continue
                
                # Create 5 questions for this module
                questions_to_create = 5 - existing_questions_count
                for i in range(questions_to_create):
                    template = QUESTION_TEMPLATES[i % len(QUESTION_TEMPLATES)]
                    
                    question = Question(
                        question_text=template["text"].format(topic=module.name),
                        option_a=template["options"][0],
                        option_b=template["options"][1],
                        option_c=template["options"][2],
                        option_d=template["options"][3],
                        correct_answer=template["correct"],
                        explanation=template["explanation"].format(topic=module.name),
                        module_id=module.id,
                        difficulty=template["difficulty"],
                        created_at=datetime.utcnow()
                    )
                    db.add(question)
                    total_questions += 1
                
                db.commit()
                print(f"    ✓ Added {questions_to_create} questions to {module.name}")
        
        print("\n" + "=" * 60)
        print("✅ QBank seeding completed successfully!")
        print(f"\nSummary:")
        print(f"  • New Subjects created: {total_subjects}")
        print(f"  • New Modules created: {total_modules}")
        print(f"  • New Questions created: {total_questions}")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed_qbank()

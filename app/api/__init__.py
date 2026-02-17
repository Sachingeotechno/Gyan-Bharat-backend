from fastapi import APIRouter
from app.api import auth, users, courses, enrollments, upload, kyc, subjects, questions, lessons, tests
from app.api.admin import courses as admin_courses, lessons as admin_lessons, qbank as admin_qbank, daily_mcq as admin_daily_mcq, tests as admin_tests, users as admin_users, course_subjects as admin_course_subjects

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(courses.router)
api_router.include_router(enrollments.router)
api_router.include_router(upload.router)
api_router.include_router(kyc.router, prefix="/kyc", tags=["KYC"])
api_router.include_router(subjects.router, prefix="/qbank", tags=["Qbank"])
api_router.include_router(questions.router, prefix="/qbank", tags=["Qbank"])
api_router.include_router(lessons.router)
api_router.include_router(tests.router)

# Admin routes
api_router.include_router(admin_courses.router)
api_router.include_router(admin_lessons.router)
api_router.include_router(admin_qbank.router)
api_router.include_router(admin_daily_mcq.router)
api_router.include_router(admin_tests.router)
api_router.include_router(admin_users.router)
api_router.include_router(admin_course_subjects.router)

# Export router
__all__ = ["api_router"]

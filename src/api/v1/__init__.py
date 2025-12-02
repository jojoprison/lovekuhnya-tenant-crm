from fastapi import APIRouter

from src.api.v1 import auth, organizations, contacts, deals, tasks, activities, analytics

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(organizations.router)
router.include_router(contacts.router)
router.include_router(deals.router)
router.include_router(tasks.router)
router.include_router(activities.router)
router.include_router(analytics.router)

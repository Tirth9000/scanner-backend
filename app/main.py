from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth.routes import router as auth_router
from app.api.scanner.routes import router as scanner_router
from app.db.create_db import init_db
from app.db.init_db import init_tables
from app.api.webhooks.routes import router as webhook_scanner_router
from app.api.assessment.routes import router as assessment_router
from app.api.questions.routes import router as questions_router
from app.api.analyzer.routes import router as analyzer_router
from app.api.fix.routes import router as fix_router
<<<<<<< HEAD
<<<<<<< HEAD
from app.api.malware.routes import router as malware_router
=======
from app.api.admin.routes import router as admin_router
>>>>>>> 95ca74d (invite members to org via email, org-wise history, promo code generateion, redeem code, smtp email added plus some minor changes)
=======
from app.api.admin.routes import router as admin_router
>>>>>>> f08a798 (Refactor authentication and assessment logic; add user role management and email invitation system)
from app.api.questions.service import seed_questions_data
from app.db.base import SessionLocal
app = FastAPI()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    # print("Initializing database...")
    init_db()
    init_tables()

    db = SessionLocal()

    try:
        result = seed_questions_data(db)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to seed questions on startup"
        )
    finally:
        db.close()

<<<<<<< HEAD
    try:
        # Attempt to create default admin 
        from scripts.create_admin import create_admin_user
        create_admin_user("admin@example.com", "admin")
    except Exception as e:
        print(f"Failed to create default admin on startup: {e}")
=======
    # try:
        # # Attempt to create default admin 
        # from scripts.create_admin import create_admin_user
        # create_admin_user("admin@example.com", "admin")
    # except Exception as e:
    #     print(f"Failed to create default admin on startup: {e}")
>>>>>>> f08a798 (Refactor authentication and assessment logic; add user role management and email invitation system)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ───────────────────────────────────────────────────────────
#
# Production (Nginx strips /api):
#   Browser → /api/auth/register → Nginx → /auth/register → backend
#
# Local dev (no Nginx, config.ts adds /api):
#   Browser → /api/auth/register → backend directly
#
# Both are handled by mounting routers TWICE:

# 1) Without /api prefix — matches Nginx-stripped paths
app.include_router(auth_router)
app.include_router(scanner_router)
<<<<<<< HEAD
=======
app.include_router(webhook_scanner_router)
>>>>>>> f2b3fc1 (member feature plus some route changes)
app.include_router(assessment_router)
app.include_router(questions_router)
app.include_router(analyzer_router)
app.include_router(fix_router)
<<<<<<< HEAD
<<<<<<< HEAD
app.include_router(malware_router)
=======
app.include_router(admin_router)
>>>>>>> 95ca74d (invite members to org via email, org-wise history, promo code generateion, redeem code, smtp email added plus some minor changes)
=======
app.include_router(admin_router)
>>>>>>> f08a798 (Refactor authentication and assessment logic; add user role management and email invitation system)

# 2) With /api prefix — matches local dev / direct access paths
app.include_router(auth_router, prefix="/api", include_in_schema=False)
app.include_router(scanner_router, prefix="/api", include_in_schema=False)
app.include_router(assessment_router, prefix="/api", include_in_schema=False)
app.include_router(questions_router, prefix="/api", include_in_schema=False)
app.include_router(analyzer_router, prefix="/api", include_in_schema=False)
app.include_router(fix_router, prefix="/api", include_in_schema=False)
app.include_router(malware_router, prefix="/api", include_in_schema=False)

# Webhooks — Go scanner-platform calls directly, not through Nginx
app.include_router(webhook_scanner_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

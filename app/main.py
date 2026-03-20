from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# from app.api.auth.routes import router as auth_router
from app.api.scanner.routes import router as scanner_router
from app.db.create_db import init_db
from app.db.init_db import init_tables
from app.api.scanner.routes import router as scanner_router
from app.api.webhooks.routes import router as webhook_scanner_router
from app.api.assessment.routes import router as assessment_router
from app.api.questions.routes import router as questions_router
from app.api.analyzer.routes import router as analyzer_router
from app.api.questions.service import seed_questions_data
from app.api.malware.routes import router as malware_router
from app.db.base import SessionLocal
app = FastAPI()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    print("Initializing database...")
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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routes
# app.include_router(auth_router)
app.include_router(scanner_router)
app.include_router(webhook_scanner_router)
app.include_router(assessment_router)
app.include_router(questions_router)
app.include_router(analyzer_router)
app.include_router(malware_router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
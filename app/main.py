from dotenv import load_dotenv
load_dotenv()  # Load env vars FIRST before other imports

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth.routes import router as auth_router
from app.api.scanner.routes import router as scanner_router
from app.db.create_db import init_db
from app.db.init_db import init_tables
from app.api.scanner.routes import router as scanner_router
from app.api.webhooks.routes import router as webhook_scanner_router
from app.api.seed.routes import router as seed_router, seed_questions_data
from app.api.assessment.routes import router as assessment_router
from app.api.questions.routes import router as questions_router

app = FastAPI()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    print("Initializing database...")
    init_db()
    init_tables()

    # Seed questions safely
    try:
        tup = seed_questions_data()
        print(tup[1])
    except Exception as e:
        print(f"Error seeding questions: {e}")


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routes
app.include_router(auth_router)
app.include_router(seed_router)
app.include_router(scanner_router)
app.include_router(webhook_scanner_router)
app.include_router(assessment_router)
app.include_router(questions_router)


@app.get('/')
def root():
    return "Scanner Backend is running"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
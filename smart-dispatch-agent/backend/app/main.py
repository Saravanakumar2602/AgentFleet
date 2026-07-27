from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router

app = FastAPI(
    title="Smart Dispatch Agent Demo API",
    description="Standalone FastAPI mock server for assignment dispatch orchestration.",
    version="1.0.0"
)

# Enable CORS for frontend local server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include dispatcher router
app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Smart Dispatch Agent Backend is running."}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import posture, websocket

app = FastAPI(title="Posture Monitor API")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(posture.router)
app.include_router(websocket.router)

@app.get("/")
async def root():
    return {"message": "Posture Monitor API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)

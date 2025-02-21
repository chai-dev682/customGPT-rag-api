import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CustomGPT.ai API",
    description="CustomGPT.ai API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    # In production, replace with specific origins
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

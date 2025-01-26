from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def hello():
    return {"message": "Endpoint hit!"}

@app.get("/api/v1/hello")
async def hello():
    return {"message": "Hello, World!"}

# Add this new POST endpoint
@app.post("/api/v1/data")
async def create_data(data: dict):
    return {
        "message": "Data received successfully",
        "received_data": data
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
from fastapi import FastAPI, Request, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import date, datetime
from pydantic import BaseModel, Field
import logging
from fastapi.responses import JSONResponse
import json

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Supabase configuration
SUPABASE_URL = "https://melippirrrsattugltbs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1lbGlwcGlycnJzYXR0dWdsdGJzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzc4NzQ5OTAsImV4cCI6MjA1MzQ1MDk5MH0.4_mH4ZIhZwhLBiHc0H8YoQ4bLlNjggv10Ol3deJ2ZRY"

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Add logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DateRange(BaseModel):
    startdate: str = Field(..., description="The start date for the flight search in YYYY-MM-DD format.")
    enddate: str = Field(..., description="The end date for the flight search in YYYY-MM-DD format.")

# Add WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def hello():
    return {"message": "Endpoint hit!"}

@app.post("/api/v1/data")
async def create_data(request: Request):
    try:
        # Get the raw request body
        body = await request.json()
        logger.info(f"Received request body: {body}")

        # Extract the arguments from the function call
        args = body.get("args", {})
        logger.info(f"Extracted args: {args}")

        # Validate the data using Pydantic model
        data = DateRange(
            startdate=args.get("startdate"),
            enddate=args.get("enddate")
        )

        # Return response in the format Retell expects with just the validated data
        return JSONResponse(
            status_code=200,
            content={
                "result": {
                    "message": "Data received successfully",
                    "data": {
                        "startDate": data.startdate,
                        "endDate": data.enddate,
                        "Balance": "1000 Dollars",
                        "Name": "John Doe",
                    }
                }
            }
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return JSONResponse(
            status_code=422,
            content={
                "result": {
                    "error": "Validation error",
                    "message": str(e)
                }
            }
        )
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "result": {
                    "error": "Internal server error",
                    "message": str(e)
                }
            }
        )

@app.websocket("/ws/transcript")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Log the received transcription
            logger.info(f"Received transcription: {data}")
            
            # Parse the JSON data
            try:
                transcript_data = json.loads(data)
                # You can process the transcript data here
                
                # Broadcast the transcription to all connected clients
                await manager.broadcast(data)
            except json.JSONDecodeError:
                logger.error("Invalid JSON received")
                
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5005) 
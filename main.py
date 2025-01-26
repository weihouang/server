from fastapi import FastAPI, Request, HTTPException
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

        # Process the data
        data_dict = {
            "startDate": data.startdate,
            "endDate": data.enddate
        }
        
        logger.info(f"Processing data: {data_dict}")
        
        result = supabase.table('Date').insert(data_dict).execute()
        # Return response in the format Retell expects
        return JSONResponse(
            status_code=200,
            content={
                "result": {
                    "message": "Data saved successfully",
                    "data": result.data
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5005) 
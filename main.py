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
SUPABASE_URL = "https://swaatlkgenfuhizlhwdo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN3YWF0bGtnZW5mdWhpemxod2RvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg4MTU4NTUsImV4cCI6MjA1NDM5MTg1NX0.vtBNgNYUU6gbmdaxBj0sQm1ZxFS67x1zHKL3v2C5ibY"

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

class AccountRequest(BaseModel):
    account_id: str = Field(..., description="String of digits representing the account ID")

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
        data = AccountRequest(account_id=args.get("accountId"))
        
        # Query the database for the matching row
        query = supabase.table('infos') \
            .select("*") \
            .eq('accountId', data.account_id)
            
        # Log the query for debugging
        logger.info(f"Executing query: {query}")
        
        result = query.execute()
        # Log the result for debugging
        logger.info(f"Query result: {result}")

        if not result.data:
            return JSONResponse(
                status_code=404,
                content={
                    "result": {
                        "error": "Not found",
                        "message": f"No account found with ID: {data.account_id}"
                    }
                }
            )

        # Return the found data
        return JSONResponse(
            status_code=200,
            content={
                "result": {
                    "message": "Account found",
                    "data": result.data[0]  # Return the first matching row
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
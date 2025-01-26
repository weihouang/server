from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import date
from pydantic import BaseModel, Field

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

class DateRange(BaseModel):
    startdate: date = Field(..., description="The start date for the flight search in YYYY-MM-DD format.")
    enddate: date = Field(..., description="The end date for the flight search in YYYY-MM-DD format.")

@app.get("/")
async def hello():
    return {"message": "Endpoint hit!"}

@app.get("/api/v1/hello")
async def hello():
    return {"message": "Hello, World!"}

# Example endpoint that interacts with Supabase
@app.post("/api/v1/data")
async def create_data(data: DateRange):
    try:
        # Convert dates to strings for Supabase storage
        # Note the capital 'D' in startDate and endDate to match Supabase columns
        data_dict = {
            "startDate": data.startdate.isoformat(),
            "endDate": data.enddate.isoformat()
        }
        
        result = supabase.table('Date').insert(data_dict).execute()
        
        return {
            "message": "Data saved to Supabase successfully",
            "data": result.data
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to save data to Supabase"
        }

# Example endpoint to fetch data from Supabase
@app.get("/api/v1/data")
async def get_data():
    try:
        # Select data from your Supabase table
        # Replace 'your_table_name' with your actual table name
        result = supabase.table('your_table_name').select("*").execute()
        
        return {
            "message": "Data retrieved successfully",
            "data": result.data
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to retrieve data from Supabase"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5005) 
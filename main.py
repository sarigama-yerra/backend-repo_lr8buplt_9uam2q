import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from typing import List

from schemas import ContactMessage
from database import create_document

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Engineering Portfolio Backend Running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

# --- Portfolio API ---

@app.get("/api/projects")
def get_projects():
    """Return featured projects (static for now)."""
    return {
        "projects": [
            {
                "title": "Autonomous Line-Following Robot",
                "subtitle": "Embedded Systems, Control",
                "description": "Designed and built a PID-controlled robot using STM32 and IR sensor array. Achieved robust tracking at 1.2 m/s.",
                "tech": ["C", "STM32", "PID", "KiCad"],
                "link": "https://github.com/your-username/line-following-robot"
            },
            {
                "title": "IoT Air Quality Monitor",
                "subtitle": "IoT, Cloud, Data Viz",
                "description": "End-to-end sensor device with ESP32 publishing to MQTT, backend aggregation, and a React dashboard for trends.",
                "tech": ["ESP32", "MQTT", "FastAPI", "React"],
                "link": "https://github.com/your-username/aqi-monitor"
            },
            {
                "title": "Finite Element Beam Solver",
                "subtitle": "Numerical Methods",
                "description": "Implemented a 2D beam FE solver with visualization for deflection and stress, validated against textbook problems.",
                "tech": ["Python", "NumPy", "Matplotlib"],
                "link": "https://github.com/your-username/fe-beam"
            }
        ]
    }

@app.post("/api/contact")
def submit_contact(payload: ContactMessage):
    """Validate and store contact messages in MongoDB."""
    try:
        # Validation already handled by Pydantic via type annotation
        doc_id = create_document("contactmessage", payload)
        return {"status": "ok", "id": doc_id}
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import asyncio
from fastapi.middleware.cors import CORSMiddleware

from . import models, schemas
from .database import get_db
from .services import extract_text_from_pdf
from .agent import process_agent_request
from .tools import activity_listeners

app = FastAPI(title="TalentDesk AI API")

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For demo purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/apply", response_model=schemas.CandidateResponse)
async def apply_for_role(
    name: str = Form(...),
    email: str = Form(...),
    role_id: int = Form(...),
    expected_salary: Optional[int] = Form(None),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Handles candidate application and extracts text from the uploaded PDF résumé.
    The extracted text (including any hidden/invisible injection payload) is saved 
    in the database for the AI copilot to read later.
    """
    # Verify role exists
    role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
        
    # Read PDF and extract text
    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
    pdf_bytes = await resume.read()
    try:
        resume_text = extract_text_from_pdf(pdf_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")
        
    # Upload to Supabase Bucket if configured
    try:
        import os
        from supabase import create_client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        bucket_name = os.getenv("SUPABASE_BUCKET")
        
        if supabase_url and supabase_key and bucket_name:
            supabase = create_client(supabase_url, supabase_key)
            file_path = f"{email}_{resume.filename}"
            supabase.storage.from_(bucket_name).upload(
                file=pdf_bytes,
                path=file_path,
                file_options={"content-type": resume.content_type}
            )
    except Exception as e:
        print(f"Warning: Failed to upload resume to Supabase bucket: {e}")

        
    # Create candidate
    new_candidate = models.Candidate(
        name=name,
        email=email,
        role_id=role_id,
        resume_text=resume_text,
        expected_salary=expected_salary,
        status="applied"
    )
    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)
    
    return new_candidate

@app.get("/candidates", response_model=List[schemas.CandidateResponse])
def get_candidates(db: Session = Depends(get_db)):
    """Retrieve all candidates in the pipeline."""
    return db.query(models.Candidate).all()

@app.get("/candidates/{candidate_id}", response_model=schemas.CandidateResponse)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific candidate's profile."""
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

# --- DB Viewer Endpoints (Phase 2) ---

@app.get("/db/roles", response_model=List[schemas.RoleResponse])
def get_all_roles(db: Session = Depends(get_db)):
    return db.query(models.Role).all()

@app.get("/db/salary_bands", response_model=List[schemas.SalaryBandResponse])
def get_all_salary_bands(db: Session = Depends(get_db)):
    return db.query(models.SalaryBand).all()

@app.get("/db/offers", response_model=List[schemas.OfferResponse])
def get_all_offers(db: Session = Depends(get_db)):
    return db.query(models.Offer).all()

@app.get("/db/inbox", response_model=List[schemas.InboxResponse])
def get_all_inbox(db: Session = Depends(get_db)):
    return db.query(models.Inbox).all()

@app.get("/db/activity_log", response_model=List[schemas.ActivityLogResponse])
def get_all_activity_log(db: Session = Depends(get_db)):
    return db.query(models.ActivityLog).all()

# --- Copilot / Agent Endpoints (Phase 3) ---

class ChatRequest(BaseModel):
    message: str

@app.post("/copilot/chat")
def copilot_chat(req: ChatRequest, db: Session = Depends(get_db)):
    try:
        reply = process_agent_request(db, req.message)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/activity")
async def activity_stream(request: Request):
    """Server-Sent Events (SSE) endpoint for live tool-call transparency."""
    queue = asyncio.Queue()
    activity_listeners.append(queue)
    
    async def event_generator():
        try:
            while True:
                # If client disconnects, break
                if await request.is_disconnected():
                    break
                
                # Wait for the next activity event
                activity_data = await queue.get()
                import json
                # Format exactly as SSE requires
                yield f"data: {json.dumps(activity_data)}\n\n"
        finally:
            activity_listeners.remove(queue)
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")


import asyncio
from sqlalchemy.orm import Session
from . import models

# SSE Listeners
activity_listeners = []

async def broadcast_activity(activity_dict: dict):
    for q in activity_listeners:
        await q.put(activity_dict)

def log_activity(db: Session, tool_name: str, arguments: dict):
    log = models.ActivityLog(tool_name=tool_name, arguments=arguments)
    db.add(log)
    db.commit()
    db.refresh(log)
    
    activity_dict = {
        "id": log.id,
        "tool_name": log.tool_name,
        "arguments": log.arguments,
        "created_at": log.created_at.isoformat()
    }
    
    # Broadcast to SSE
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(broadcast_activity(activity_dict))
    except RuntimeError:
        pass # Not running in an async loop (e.g. tests)

def get_tool_registry(db: Session):
    """Returns the executable functions bound to the current DB session."""
    
    def search_candidates(status: str = None, role_id: int = None) -> list:
        """Search and filter candidates in the pipeline."""
        query = db.query(models.Candidate)
        if status:
            query = query.filter(models.Candidate.status == status)
        if role_id:
            query = query.filter(models.Candidate.role_id == role_id)
            
        candidates = query.all()
        log_activity(db, "search_candidates", {"status": status, "role_id": role_id})
        return [
            {"id": c.id, "name": c.name, "email": c.email, "role_id": c.role_id, "status": c.status, "interview_score": c.interview_score, "expected_salary": c.expected_salary}
            for c in candidates
        ]

    def get_candidate(candidate_id: int) -> dict:
        """View a candidate's full profile, including their resume text and recruiter notes."""
        c = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
        log_activity(db, "get_candidate", {"candidate_id": candidate_id})
        if not c:
            return {"error": "Candidate not found"}
            
        return {
            "id": c.id, "name": c.name, "email": c.email, "role_id": c.role_id,
            "status": c.status, "notes": c.notes, "interview_score": c.interview_score,
            "expected_salary": c.expected_salary,
            "resume_text": c.resume_text
        }

    def get_salary_band(role_id: int) -> dict:
        """Check internal compensation ranges for a specific role."""
        b = db.query(models.SalaryBand).filter(models.SalaryBand.role_id == role_id).first()
        log_activity(db, "get_salary_band", {"role_id": role_id})
        if not b:
            return {"error": "Salary band not found"}
            
        return {"min_salary": b.min_salary, "max_salary": b.max_salary}

    def update_candidate(candidate_id: int, status: str = None, notes: str = None, interview_score: float = None) -> dict:
        """Update a candidate's status, private recruiter notes, or interview score."""
        c = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
        log_activity(db, "update_candidate", {"candidate_id": candidate_id, "status": status, "notes": notes, "interview_score": interview_score})
        
        if not c:
            return {"error": "Candidate not found"}
            
        if status is not None: c.status = status
        if notes is not None: c.notes = notes
        if interview_score is not None: c.interview_score = interview_score
        
        db.commit()
        return {"success": True}

    def send_email(to_email: str, subject: str, body: str) -> dict:
        """Send an email to a candidate."""
        inbox_entry = models.Inbox(to_email=to_email, subject=subject, body=body)
        db.add(inbox_entry)
        db.commit()
        log_activity(db, "send_email", {"to_email": to_email, "subject": subject, "body": body})
        return {"success": True}

    return {
        "search_candidates": search_candidates,
        "get_candidate": get_candidate,
        "get_salary_band": get_salary_band,
        "update_candidate": update_candidate,
        "send_email": send_email
    }

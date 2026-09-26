from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class RoleBase(BaseModel):
    title: str
    department: str

class RoleResponse(RoleBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class CandidateBase(BaseModel):
    name: str
    email: str
    role_id: int
    notes: Optional[str] = None
    interview_score: Optional[float] = None
    status: str

class CandidateResponse(CandidateBase):
    id: int
    resume_text: Optional[str] = None
    role: Optional[RoleResponse] = None
    model_config = ConfigDict(from_attributes=True)

class OfferBase(BaseModel):
    candidate_id: int
    amount: int
    status: str

class OfferResponse(OfferBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# For DB Viewer
class SalaryBandResponse(BaseModel):
    id: int
    role_id: int
    min_salary: int
    max_salary: int
    model_config = ConfigDict(from_attributes=True)
    
class InboxResponse(BaseModel):
    id: int
    to_email: str
    subject: str
    body: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ActivityLogResponse(BaseModel):
    id: int
    tool_name: str
    arguments: dict
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

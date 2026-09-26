from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    department = Column(String, nullable=False)

    candidates = relationship("Candidate", back_populates="role")
    salary_band = relationship("SalaryBand", back_populates="role", uselist=False)

class SalaryBand(Base):
    __tablename__ = "salary_bands"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, unique=True)
    min_salary = Column(Integer, nullable=False)
    max_salary = Column(Integer, nullable=False)

    role = relationship("Role", back_populates="salary_band")

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    resume_text = Column(Text, nullable=True) # Extracted plain text from PDF
    notes = Column(Text, nullable=True) # Private recruiter notes
    interview_score = Column(Float, nullable=True) # E.g., 0-10 or 0-100
    status = Column(String, default="applied") # applied, interviewing, rejected, offered

    role = relationship("Role", back_populates="candidates")
    offers = relationship("Offer", back_populates="candidate")

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String, default="pending") # pending, accepted, declined

    candidate = relationship("Candidate", back_populates="offers")

class Inbox(Base):
    """Simulated attacker inbox to show data exfiltration."""
    __tablename__ = "inbox"

    id = Column(Integer, primary_key=True, index=True)
    to_email = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ActivityLog(Base):
    """Live tool-call transparency log."""
    __tablename__ = "activity_log"

    id = Column(Integer, primary_key=True, index=True)
    tool_name = Column(String, nullable=False)
    arguments = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

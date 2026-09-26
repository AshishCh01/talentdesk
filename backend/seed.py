import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.models import Role, SalaryBand, Candidate, Offer
from app.database import Base

load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_DB_URL")

if not DATABASE_URL:
    raise ValueError("SUPABASE_DB_URL is not set.")
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_data():
    db = SessionLocal()
    try:
        # Check if we already have data
        if db.query(Role).first():
            print("Database already seeded. Skipping.")
            return

        print("Seeding database with synthetic data...")

        # Create Roles
        role_swe = Role(title="Software Engineer", department="Engineering")
        role_pm = Role(title="Product Manager", department="Product")
        role_design = Role(title="Product Designer", department="Design")
        db.add_all([role_swe, role_pm, role_design])
        db.commit()

        # Create Salary Bands
        band_swe = SalaryBand(role_id=role_swe.id, min_salary=120000, max_salary=160000)
        band_pm = SalaryBand(role_id=role_pm.id, min_salary=130000, max_salary=175000)
        band_design = SalaryBand(role_id=role_design.id, min_salary=110000, max_salary=150000)
        db.add_all([band_swe, band_pm, band_design])
        db.commit()

        # Create Candidates
        c1 = Candidate(
            name="Alice Smith",
            email="alice.smith@example.com",
            role_id=role_swe.id,
            resume_text="Experienced backend engineer with 5 years of Python and Postgres.",
            notes="Strong technical skills. High salary expectation.",
            interview_score=8.5,
            status="interviewing"
        )
        c2 = Candidate(
            name="Bob Jones",
            email="bob.jones@example.com",
            role_id=role_pm.id,
            resume_text="Product Manager focused on AI products and user growth.",
            notes="Good communication, but lacks technical depth.",
            interview_score=6.0,
            status="rejected"
        )
        c3 = Candidate(
            name="Charlie Brown",
            email="charlie.brown@example.com",
            role_id=role_design.id,
            resume_text="UI/UX designer with a portfolio of fintech apps.",
            notes="Excellent portfolio. Recommend making an offer.",
            interview_score=9.2,
            status="offered"
        )
        db.add_all([c1, c2, c3])
        db.commit()

        # Create Offers
        o1 = Offer(
            candidate_id=c3.id,
            amount=140000,
            status="pending"
        )
        db.add(o1)
        db.commit()

        print("Seeding complete!")

    finally:
        db.close()

if __name__ == "__main__":
    seed_data()

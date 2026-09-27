# TalentDesk AI — A deliberately vulnerable AI recruiter copilot, built to demonstrate real-world prompt injection (Part 1 of 2)

## ⚠️ DISCLAIMER
- **This is an educational security demo, not a production application.**
- **It is intentionally vulnerable to prompt injection.**
- All candidate, salary, and company data is 100% synthetic — no real people are represented here.
- **Do not deploy this publicly or reuse this code in a real product** without the Phase 2 security fixes.
- No real emails are ever sent by this application — the `send_email` tool writes to a simulated inbox table only.

## WHAT THIS DEMONSTRATES
This project demonstrates how an AI recruiter copilot with legitimate, necessary tools (search candidates, view profiles, check salary bands, update records, send email) gets hijacked by a hidden instruction embedded invisibly inside an uploaded résumé PDF (using white-on-white 2pt text). 

When a recruiter asks the copilot a completely normal question, the hidden instruction gets pulled into the AI's context and executed using the agent's own real tools — leaking confidential data or tampering with records.

None of the tools are over-privileged. Every tool is a feature the app genuinely needs to function as intended. The vulnerability is architectural: the AI cannot distinguish trusted developer instructions from untrusted user document content. Therefore, a permissions mistake is not the root cause, and removing a tool does not fix the underlying vulnerability.

## HOW THE ATTACK WORKS
1. A candidate uploads a résumé containing hidden injected text.
2. The backend extracts all PDF text (including the invisible text) during ingestion.
3. A recruiter asks the AI copilot a normal question (e.g., "screen today's applicants").
4. The copilot pulls the résumé text into its context to fulfill the request.
5. The AI can't tell the hidden instruction apart from the recruiter's real instruction, and executes it using a real tool.
6. Confidential data leaks (via `send_email`) or a record gets silently tampered with (via `update_candidate`).

We have included two attack payloads in `sample-resumes/poisoned/`:
- **`injection_exfiltrate.pdf`**: Hijacks the `send_email` tool to exfiltrate confidential candidate and internal salary data to an external attacker inbox.
- **`injection_tamper.pdf`**: Hijacks the `update_candidate` tool to artificially inflate the candidate's interview score and falsely change their status to "offered".

## TECH STACK
- **FastAPI**: Backend framework
- **React (Vite)**: Frontend framework
- **Supabase (Postgres)**: Database
- **SQLAlchemy + Alembic**: ORM and database migrations
- **pdfplumber**: Résumé text extraction
- **Gemini (primary) / Groq (fallback)**: Agent LLM

*Note: There is no authentication in Phase 1 — this is intentional to keep the focus purely on the injection mechanic itself.*

## PROJECT STRUCTURE
- `backend/`: FastAPI application, agent logic, database models, and tools.
- `frontend/`: React application built with Vite containing the various UI views.
- `supabase/`: Database configurations and local Supabase setup files.
- `sample-resumes/`: Legitimate and poisoned PDF résumés used for the demonstration.
- `docs/`: Additional documentation and architecture diagrams.

## SETUP & RUNNING LOCALLY

1. **Clone the repo:**
   ```bash
   git clone <repository-url>
   cd talentdesk
   ```

2. **Configure Environment Variables:**
   Copy the example environment file and fill in your keys:
   ```bash
   cp backend/.env.example backend/.env
   ```
   *Required variables:* `SUPABASE_DB_URL`, `GEMINI_API_KEY`, `GROQ_API_KEY` (Supabase storage variables are optional).

3. **Run the Backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/Scripts/activate  # Or venv/bin/activate on Mac/Linux (Use .\venv\Scripts\activate on Windows)
   pip install -r requirements.txt
   alembic upgrade head
   python seed.py
   uvicorn app.main:app --reload
   ```

4. **Run the Frontend:**
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

5. **Open the Application:**
   Navigate to the local URL provided by Vite. The app features four main pages:
   - **Apply**: A public-facing form for candidates to submit résumés.
   - **Recruiter Dashboard**: The internal copilot interface where recruiters chat with the AI.
   - **Attacker Inbox**: A simulated external email inbox used to observe exfiltration.
   - **DB Viewer**: A direct view into the database state to observe tampering.

## REPRODUCING THE ATTACK

Follow these steps to trigger the attack payloads yourself:

1. Go to the **Apply** page and submit an application using `sample-resumes/poisoned/injection_exfiltrate.pdf`.
2. Navigate to the **Recruiter Dashboard** and ask the copilot to *"screen today's applicants"*.
3. Watch the **Live Tool Activity** log and observe the `send_email` tool being maliciously called.
4. Check the **Attacker Inbox** page to see the confidential data that was leaked.
5. Repeat the process using `injection_tamper.pdf` and watch `update_candidate` fire maliciously. Then, check the **DB Viewer** to see the candidate's artificially inflated score and altered status.

## WHAT'S NEXT — PHASE 2
Part 2 will take this exact same application, tools, and database, and demonstrate how to architecturally secure it against this class of attack — without deleting any functionality. [Link to follow-up post coming soon]

## LICENSE / DATA NOTE
All data contained within this repository is entirely fictional and synthetic. 
This code is provided under the MIT License for educational purposes only.

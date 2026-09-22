## 📌 Executive Summary

Democratizing data access across an organization requires breaking down technical barriers to relational databases. Business analysts, strategy leads, and non-technical managers frequently need ad-hoc insights but lack raw SQL proficiency, creating bottlenecks for central data teams.

**The Text-to-SQL Analytics Assistant** is a lightweight, LLM-powered application designed to bridge this exact gap. Using **LangChain** for prompt chain orchestration and **Google Gemini 1.5 Flash** for natural language translation, the application automatically inspects user-uploaded SQLite databases or raw SQL script files (`.db`, `.sqlite`, `.sql`), constructs syntactically precise SQL queries, executes them safely via **SQLAlchemy**, and streams structured tabular results directly back to the chat interface.

---

## 🏗️ System Architecture & Workflow

┌─────────────────┐      ┌──────────────────────────┐      ┌──────────────────────────┐
│  User Interface │      │  Temp File Ingestion     │      │   SQLAlchemy Database    │
│   (Streamlit)   ├─────►│  (.db / .sqlite / .sql)  ├─────►│     Connection Engine    │
└────────┬────────┘      └──────────────────────────┘      └────────────┬─────────────┘
│                                                              │
│ (Plain English Question)                                     │ (Schema Metadata)
▼                                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            LangChain LLM Chain Engine                               │
│  ┌─────────────────────────┐    ┌────────────────────┐    ┌──────────────────────┐  │
│  │ PromptTemplate Engine   ├─►  │ Gemini 1.5 Flash   ├─►  │ QuerySQLDataBaseTool │  │
│  └─────────────────────────┘    └────────────────────┘    └──────────┬───────────┘  │
└──────────────────────────────────────────────────────────────────────│──────────────┘
│ (Executed Query & Result)
▼
┌──────────────────────────┐
│   Streamlit Chat Window  │
└──────────────────────────┘


---

## 🔬 Core Technical Features

### 1. Multi-Format Database Ingestion Engine
- **Direct SQLite Ingestion:** Accepts native `.db` and `.sqlite` binaries, instantly compiling a temporary `sqlite://` connection URI via `SQLAlchemy`.
- **SQL Script On-the-Fly Execution:** For standard `.sql` script files, the application creates a transient target SQLite database in system temp memory and executes raw DDL/DML setup scripts (`executescript`) to synthesize a live querying environment on the fly.

### 2. LangChain & Gemini 1.5 Flash Pipeline
- **Prompt Engineering:** Uses structured `PromptTemplate` design to constrain output generation strictly to valid SQLite dialect queries, eliminating hallucinated tokens.
- **LLM Orchestration:** Employs `LLMChain` bound to `ChatGoogleGenerativeAI(model="gemini-1.5-flash")` configured with low temperature parameter (`0.5`) to optimize deterministic output logic.

### 3. Safe Execution & Error Diagnostics
- **Automated Schema Querying:** Uses `QuerySQLDataBaseTool` from `langchain_community` to pipe generated SQL text strings directly to the backend database engine.
- **Try-Catch Execution Wrapper:** Traps execution errors (e.g., column name mismatch, invalid syntax) gracefully, surfacing actionable feedback alongside the exact SQL query attempted for easy debugging.

### 4. Temporary File Lifecycle Management
- Implements custom `cleanup_temp_files()` wrappers leveraging `tempfile` and `os.unlink()` routines bound to Streamlit session state. This prevents file locking, memory leaks, and lingering residual database files across user browser refreshes.

---

## 💻 Tech Stack & Dependencies

* **Core Language:** Python 3.10+
* **LLM & Orchestration Framework:** `langchain`, `langchain_community`, `langchain_core`, `langchain_google_genai`
* **Generative AI Model:** Google Gemini 1.5 Flash (`ChatGoogleGenerativeAI`)
* **Database & ORM:** `SQLite3`, `SQLAlchemy`
* **UI & Deployment:** `Streamlit`

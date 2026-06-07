# Candidate Screening AI

An AI-powered role-based candidate screening system that dynamically generates interview questions using Retrieval-Augmented Generation (RAG). The system simulates structured technical interviews with questions tailored to the candidate's resume and target role.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Features](#features)
- [Technical Stack](#technical-stack)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [RAG Pipeline](#rag-pipeline)
- [Demo Flow](#demo-flow)
- [Key Design Decisions](#key-design-decisions)
- [Future Enhancements](#future-enhancements)

## Overview

This system implements an intelligent candidate screening platform that:

1. **Parses resumes** - Extracts skills, technologies, and experience levels
2. **Generates topics** - Creates interview topics based on role and candidate background
3. **Retrieves context** - Uses RAG to fetch relevant knowledge from a domain-specific knowledge base
4. **Generates questions** - Creates contextually-aware, difficulty-adjusted questions
5. **Evaluates answers** - Scores and provides feedback on candidate responses
6. **Summarizes results** - Provides comprehensive interview analysis

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (React)                  │
│                                                     │
│  • Resume Upload     • Role Selection              │
│  • Interview UI      • Results Display             │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP/REST
┌──────────────────▼──────────────────────────────────┐
│              Backend (FastAPI)                      │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │      API Layer (Interview Endpoints)         │  │
│  └──────────────┬──────────────────────────────┘  │
│                 │                                  │
│  ┌──────────────▼──────────────────────────────┐  │
│  │    Interview Service & Workflow Nodes       │  │
│  │  • Resume Parsing   • Topic Generation      │  │
│  │  • RAG Retrieval    • Question Generation   │  │
│  │  • Answer Evaluation                        │  │
│  └──────────────┬──────────────────────────────┘  │
│                 │                                  │
│     ┌───────────┼───────────┬───────────┐         │
│     │           │           │           │         │
│  ┌──▼───┐  ┌────▼────┐  ┌───▼──┐  ┌────▼─────┐  │
│  │ LLM  │  │   RAG   │  │  DB  │  │ LangGraph│  │
│  │      │  │         │  │      │  │  Workflow│  │
│  └──────┘  └────┬────┘  └──────┘  └──────────┘  │
│                 │                                  │
│          ┌──────▼──────┐                          │
│          │ Vector Store │                         │
│          │   + Embeddings                         │
│          └──────────────┘                         │
└──────────────────────────────────────────────────┘
         │
         │ Knowledge Base Documents
         ▼
    Knowledge Base (PDFs/Texts)
```

## Features

### Core Features
- **Dynamic Question Generation** - Questions generated based on resume and role using RAG
- **Resume Parsing** - Automatic extraction of skills, technologies, and experience
- **Intelligent Retrieval** - Context-aware document retrieval from knowledge base
- **Multi-role Support** - Tailored interview questions for different job roles
- **Answer Evaluation** - LLM-based evaluation with scoring and feedback
- **Session Management** - Track and persist interview sessions in database
- **Progress Tracking** - Visual interview progress and question counter

### Advanced Features
- **Difficulty Adaptation** - Questions adjust based on candidate experience level
- **Context Traceability** - Track which documents informed each question
- **Comprehensive Summaries** - Generate insights on strengths and areas for improvement
- **Responsive UI** - Mobile-friendly React/Next.js interface
- **RESTful API** - Clean, well-structured backend API

## Technical Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLAlchemy ORM with SQLite (or PostgreSQL)
- **LLM Integration**: LangChain + OpenAI API
- **Vector DB**: Chroma for embeddings storage
- **RAG**: Document processing and embedding generation
- **Workflow**: LangGraph for state management
- **PDF Processing**: PyPDF2

### Frontend
- **Framework**: React 18 with Next.js
- **Styling**: Tailwind CSS
- **Language**: TypeScript
- **State Management**: React Hooks
- **HTTP Client**: Fetch API

### Infrastructure
- **Backend Server**: Uvicorn
- **Frontend Server**: Next.js Development Server
- **Database**: SQLite (development) / PostgreSQL (production)

## Project Structure

```
candidate-screening-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── interview.py          # FastAPI endpoints
│   │   │
│   │   ├── graph/
│   │   │   ├── state.py              # Workflow state definition
│   │   │   ├── workflow.py           # LangGraph workflow
│   │   │   └── workflow_nodes.py     # Workflow node implementations
│   │   │
│   │   ├── rag/
│   │   │   ├── vectorstore.py        # Vector store management
│   │   │   ├── ingest.py             # Document ingestion
│   │   │   └── retriever.py          # RAG retriever logic
│   │   │
│   │   ├── services/
│   │   │   ├── llm_service.py        # LLM interactions
│   │   │   └── interview_service.py  # Interview orchestration
│   │   │
│   │   ├── db/
│   │   │   ├── models.py             # SQLAlchemy models
│   │   │   ├── database.py           # DB configuration
│   │   │   └── repository.py         # Repository pattern
│   │   │
│   │   ├── prompts/
│   │   │   └── prompts.py            # LLM prompt templates
│   │   │
│   │   └── main.py                   # FastAPI app entry
│   │
│   ├── data/
│   │   ├── resumes/                  # Sample resumes
│   │   ├── knowledge_base/           # Role-specific documents
│   │   └── vectorstore/              # Persisted embeddings
│   │
│   ├── requirements.txt              # Python dependencies
│   ├── .env                          # Environment configuration
│   └── README.md                     # Backend documentation
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   └── index.tsx             # Main page
│   │   │
│   │   ├── components/
│   │   │   ├── ResumeUpload.tsx      # Resume upload form
│   │   │   ├── RoleSelection.tsx     # Role selection UI
│   │   │   ├── Interview.tsx         # Main interview component
│   │   │   ├── QuestionDisplay.tsx   # Question display
│   │   │   ├── AnswerSubmission.tsx  # Answer form
│   │   │   └── InterviewSummary.tsx  # Results display
│   │   │
│   │   ├── services/
│   │   │   └── interviewService.ts   # API client
│   │   │
│   │   ├── hooks/
│   │   │   └── useInterviewState.ts  # Interview state hook
│   │   │
│   │   ├── globals.css               # Global styles
│   │   └── layout.tsx                # Root layout
│   │
│   ├── package.json                  # NPM dependencies
│   ├── tsconfig.json                 # TypeScript config
│   ├── tailwind.config.js            # Tailwind config
│   ├── next.config.js                # Next.js config
│   ├── .env.local                    # Frontend environment
│   └── README.md                     # Frontend documentation
│
├── README.md                         # This file
└── .gitignore                        # Git ignore rules
```

## Setup Instructions

### Backend Setup

#### Prerequisites
- Python 3.9+
- pip or poetry
- OpenAI API key (for LLM)

#### Installation

1. **Create Python virtual environment**
```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
# Edit .env file with your configuration
cp .env.example .env  # or manually create .env
```

Key environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `DATABASE_URL`: Database connection string
- `VECTORSTORE_PATH`: Path for vector store persistence
- `CORS_ORIGINS`: Allowed CORS origins

4. **Initialize database**
```bash
# Database will be auto-initialized on app startup
# Or manually:
python -c "from app.db.database import init_db; init_db()"
```

5. **Run backend server**
```bash
python app/main.py
# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at `http://localhost:8000`

### Frontend Setup

#### Prerequisites
- Node.js 18+
- npm or yarn

#### Installation

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Configure environment variables**
```bash
# .env.local is already configured, adjust if needed
REACT_APP_API_URL=http://localhost:8000
```

3. **Run development server**
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

### Running the Complete System

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python app/main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Then open `http://localhost:3000` in your browser.

## Configuration

### Backend Configuration (.env)

```env
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Database
DATABASE_URL=sqlite:///./candidate_screening.db
# PostgreSQL: DATABASE_URL=postgresql://user:password@localhost/candidate_screening

# LLM
OPENAI_API_KEY=your_api_key
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7

# Vector Store
VECTORSTORE_PATH=./data/vectorstore
EMBEDDING_TYPE=huggingface  # or openai

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Frontend Configuration (.env.local)

```env
REACT_APP_API_URL=http://localhost:8000
```

## API Documentation

### Endpoints

#### Start Interview
```
POST /api/interview/start
Content-Type: application/json

{
  "candidate_name": "string",
  "email": "string (optional)",
  "role": "string",
  "resume_text": "string"
}

Response:
{
  "session_id": "uuid",
  "candidate_name": "string",
  "role": "string",
  "status": "active"
}
```

#### Get Next Question
```
POST /api/interview/next-question?session_id=<session_id>

Response:
{
  "question_id": "uuid",
  "question_number": 1,
  "question_text": "string",
  "topic": "string",
  "difficulty": "beginner|intermediate|advanced"
}
```

#### Submit Answer
```
POST /api/interview/submit-answer
Content-Type: application/json

{
  "session_id": "uuid",
  "question_id": "uuid",
  "answer": "string"
}

Response:
{
  "question_id": "uuid",
  "score": 0.0-1.0,
  "feedback": "string",
  "strengths": ["string"],
  "weaknesses": ["string"]
}
```

#### Get Session Summary
```
GET /api/interview/summary/<session_id>

Response:
{
  "session_id": "uuid",
  "role": "string",
  "candidate_name": "string",
  "total_questions": 5,
  "questions_answered": 5,
  "average_score": 0.75,
  "strengths": ["string"],
  "weaknesses": ["string"],
  "questions_and_answers": [...]
}
```

## RAG Pipeline

### Knowledge Ingestion

1. **Document Processing**
   - Load PDF/text documents from `data/knowledge_base/<role>/`
   - Split into semantic chunks (500 chars with 50 char overlap)
   - Generate embeddings for each chunk

2. **Embedding Storage**
   - Store embeddings in Chroma vector database
   - Persist to `data/vectorstore/` for quick retrieval
   - Organize by role for efficient filtering

### Retrieval Mechanism

1. **Query Enhancement**
   - Extract keywords from candidate resume
   - Combine with interview topic and role
   - Create context-aware query

2. **Semantic Search**
   - Use embeddings to find relevant chunks
   - Filter by role when retrieving
   - Return top-K results with relevance scores

3. **Context Assembly**
   - Combine retrieved chunks
   - Maintain source attribution
   - Pass to LLM for question generation

### Question Generation Flow

```
Resume + Topic + Role
         ↓
  Enhance Query
         ↓
   Retrieve Context (RAG)
         ↓
  Generate Question (LLM)
         ↓
  Store Question + Context
```

## Demo Flow

### Complete Interview Session

1. **Resume Upload**
   - User uploads resume (text or PDF)
   - System extracts: skills, technologies, experience years, domains

2. **Role Selection**
   - User selects target role (e.g., Backend Engineer, AI/ML Engineer)
   - System prepares interview configuration

3. **Topic Generation**
   - LLM generates 5 interview topics based on:
     - Candidate's background
     - Target role requirements
     - Experience level

4. **Interview Loop (5 Questions)**
   - For each topic:
     - Retrieve relevant context from knowledge base
     - Generate contextual question
     - Candidate provides answer
     - LLM evaluates answer (score 0-1)
     - Display feedback

5. **Results Summary**
   - Show metrics:
     - Total questions: 5
     - Questions answered: 5
     - Average score
   - Display:
     - Strengths identified
     - Areas for improvement
   - Provide recommendations

## Key Design Decisions

### 1. LangGraph for Workflow Orchestration
- **Why**: Structured state management for multi-step interview process
- **Benefit**: Easy to extend with new workflow steps, clear control flow
- **Alternative considered**: Direct function composition (less scalable)

### 2. Repository Pattern for Data Access
- **Why**: Abstraction layer between database and business logic
- **Benefit**: Easy to switch databases, testable code
- **Impact**: Easier to add new persistence features

### 3. RAG for Question Context
- **Why**: Ensure questions are grounded in authoritative knowledge
- **Benefit**: Questions are specific and relevant, not generic
- **Trade-off**: Requires maintaining knowledge base

### 4. Difficulty Adaptation Based on Experience
- **Why**: Tailor interview difficulty to candidate level
- **Benefit**: Fair evaluation across different experience levels
- **Implementation**: Extracted from resume or inferred from skills

### 5. FastAPI for Backend
- **Why**: High performance, built-in async, automatic API documentation
- **Benefit**: Rapid development, easy to scale
- **Alternative: Flask (simpler but less performant)

### 6. Next.js for Frontend
- **Why**: React with SSR, built-in routing, better SEO potential
- **Benefit**: Type-safe with TypeScript, modern development experience
- **Alternative: Plain React (more flexible, more boilerplate)

## Future Enhancements

### Short Term
- [ ] Implement actual PDF parsing with pdfjs-dist
- [ ] Add ability to pause and resume interviews
- [ ] Store interview recordings/transcripts
- [ ] Export results as PDF report
- [ ] Multi-language support

### Medium Term
- [ ] Real-time feedback with streaming responses
- [ ] Adaptive question difficulty based on answer quality
- [ ] Video interview capability
- [ ] Plagiarism detection for answers
- [ ] Batch candidate screening
- [ ] Analytics dashboard for recruiters

### Long Term
- [ ] Multi-modal interviews (voice, video)
- [ ] Behavioral assessment integration
- [ ] Collaborative interview mode
- [ ] Role recommendation based on profile
- [ ] Integration with ATS systems
- [ ] Advanced analytics and bias detection

## Troubleshooting

### Common Issues

1. **OpenAI API Error**
   - Verify API key in `.env`
   - Check API usage limits
   - Ensure sufficient credits

2. **Vector Store Issues**
   - Delete `data/vectorstore/` to reinitialize
   - Ensure `VECTORSTORE_PATH` is writable

3. **CORS Errors**
   - Update `CORS_ORIGINS` in backend `.env`
   - Ensure frontend URL is allowed

4. **Database Errors**
   - Check `DATABASE_URL` format
   - Ensure database directory is writable
   - Check PostgreSQL connection if using it

## Contributing

This is a reference implementation for the PG-AGI internship assignment. For improvements or modifications:

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

This project is provided as part of the PG-AGI internship program.

## Support

For questions or issues:
- Check the API documentation
- Review the code comments
- Examine example prompts in `app/prompts/prompts.py`
- Check database models in `app/db/models.py`

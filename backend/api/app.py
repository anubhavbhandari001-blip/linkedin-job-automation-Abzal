"""
Dashboard API.

Phase 1 (this file): read-only endpoints so the frontend dashboard can
show scraped jobs, match scores, and application history.

Phase 2 (future): endpoints to trigger a scrape run and approve/send
individual applications from the browser. The pipeline.py functions
this would call already exist and are already non-interactive, so
wiring that up later is mostly just new routes here - no further
refactor of the core logic needed.

Run with:
    cd backend
    uvicorn api.app:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from config.settings import CORS_ALLOW_ORIGINS
from config.logger import get_logger

from database.submissions import (
    initialize_database,
    get_all_submissions,
    get_submission_by_id,
    count_submissions,
    get_stats,
)

log = get_logger(__name__)

app = FastAPI(title="LinkedIn Job Automation Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    initialize_database()
    log.info("Dashboard API started.")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/stats")
def stats():
    return get_stats()


@app.get("/api/jobs")
def list_jobs(
    status: Optional[str] = Query(None, description="Filter by status, e.g. SENT, ANALYZED, SKIPPED"),
    search: Optional[str] = Query(None, description="Search job title / company / recruiter name"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    jobs = get_all_submissions(status=status, search=search, limit=limit, offset=offset)
    total = count_submissions(status=status, search=search)

    return {
        "jobs": jobs,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@app.get("/api/jobs/{job_id}")
def get_job(job_id: int):
    job = get_submission_by_id(job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return job

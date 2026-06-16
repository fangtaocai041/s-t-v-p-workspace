"""
fish-ecology-assistant REST API

FastAPI 接口 — 核心能力跨项目 HTTP 调用

端点:
  GET  /species/{query}             — 查询物种
  GET  /species/search?q=xxx        — 全文搜索
  GET  /species/{id}/literature     — 获取文献
  POST /species/{id}/literature     — 添加文献（知识回补）
  GET  /health                      — 健康检查

启动:
    python fish_ecology_assistant/api.py
    uvicorn fish_ecology_assistant.api:app --reload
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure package is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fish_ecology_assistant.db import get_db, KnowledgeDB

app = FastAPI(
    title="Fish Ecology Assistant API",
    version="6.5.0",
    description="鱼类生态学知识供给引擎 REST API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ──

class SpeciesInfo(BaseModel):
    id: str
    scientific: str
    chinese: str
    family: str = ""
    conservation: str = ""
    status: str = ""
    basins: str = ""
    aliases: list = []
    literature_count: int = 0

class LiteratureItem(BaseModel):
    title: str
    doi: str = ""
    year: int = 0
    journal: str = ""
    authors: str = ""
    category: str = ""
    species_id: Optional[str] = None

class LiteratureAdd(BaseModel):
    title: str
    doi: str = ""
    year: int = 0
    journal: str = ""
    authors: list = []
    category: str = ""

class HealthStatus(BaseModel):
    status: str
    species_count: int
    db_path: str
    version: str

class SpeciesSearchResult(BaseModel):
    query: str
    total: int
    results: list


# ── Endpoints ──

@app.get("/health", response_model=HealthStatus)
def health():
    db = get_db()
    return HealthStatus(
        status="HEALTHY",
        species_count=db.count(),
        db_path=str(db.conn.execute("PRAGMA database_list").fetchone()[2]),
        version="6.5.0",
    )


@app.get("/species/search", response_model=SpeciesSearchResult)
def search_species(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(10, ge=1, le=50),
):
    db = get_db()
    results = db.search(q, limit)
    return SpeciesSearchResult(
        query=q,
        total=len(results),
        results=[SpeciesInfo(**r) for r in results],
    )


@app.get("/species/{query}", response_model=SpeciesInfo)
def get_species(query: str):
    db = get_db()
    species = db.lookup(query)
    if not species:
        raise HTTPException(status_code=404, detail=f"Species not found: {query}")
    return SpeciesInfo(**species)


@app.get("/species/{species_id}/literature", response_model=list[LiteratureItem])
def get_literature(species_id: str):
    db = get_db()
    items = db.get_literature(species_id)
    if not items:
        raise HTTPException(status_code=404, detail=f"No literature for: {species_id}")
    return [LiteratureItem(**item) for item in items]


@app.post("/species/{species_id}/literature", status_code=201)
def add_literature(species_id: str, paper: LiteratureAdd):
    db = get_db()
    # Verify species exists
    species = db.lookup(species_id)
    if not species:
        raise HTTPException(status_code=404, detail=f"Species not found: {species_id}")
    row_id = db.add_literature(species_id, paper.model_dump())
    return {"id": row_id, "species_id": species_id, "status": "added"}


@app.get("/species", response_model=SpeciesSearchResult)
def list_all(limit: int = Query(30, ge=1, le=100)):
    db = get_db()
    all_species = db.list_all()[:limit]
    return SpeciesSearchResult(
        query="*",
        total=len(all_species),
        results=[SpeciesInfo(**s) for s in all_species],
    )


# ── 启动 ──

def main():
    """直接运行时的入口"""
    import uvicorn
    db = get_db()
    if db.count() == 0:
        print("📥 首次运行 — 从 YAML 迁移数据...")
        db.init_from_yaml()
    print(f"🚀 启动 API — {db.count()} 物种已加载")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()

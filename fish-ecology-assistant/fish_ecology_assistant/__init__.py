"""fish_ecology_assistant — SQLite 知识库 + REST API 包"""
from fish_ecology_assistant.db import KnowledgeDB, get_db

# API 惰性加载（需要 pip install fastapi uvicorn）
try:
    from fish_ecology_assistant.api import app
except ImportError:
    app = None

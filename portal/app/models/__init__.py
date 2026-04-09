"""
Paket models — mengekspor semua model SQLAlchemy agar mudah diimpor.
"""

from app.models.user import User
from app.models.article import KnowledgeArticle
from app.models.best_practice import BestPractice

__all__ = ["User", "KnowledgeArticle", "BestPractice"]

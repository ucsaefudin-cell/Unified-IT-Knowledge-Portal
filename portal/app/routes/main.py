"""
Blueprint routes utama: dashboard, halaman pillar SAP/AWS, dan best practices.
"""

from flask import Blueprint, render_template, session
from flask_login import current_user
from app import db
from app.models.article import KnowledgeArticle
from app.models.best_practice import BestPractice

# Buat blueprint untuk routes utama
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def dashboard():
    """Tampilkan halaman dashboard utama dengan Bento Box/Grid layout."""
    # Ambil beberapa artikel terbaru dari setiap pillar untuk preview
    sap_articles = KnowledgeArticle.query.filter_by(pillar="SAP").limit(4).all()
    aws_articles = KnowledgeArticle.query.filter_by(pillar="AWS").limit(4).all()
    return render_template(
        "dashboard.html",
        sap_articles=sap_articles,
        aws_articles=aws_articles,
    )


@main_bp.route("/sap")
def sap_pillar():
    """Tampilkan semua Knowledge Article untuk pilar SAP Business One."""
    # Ambil semua artikel SAP dari database, urutkan berdasarkan kategori topik
    articles = KnowledgeArticle.query.filter_by(pillar="SAP").order_by(
        KnowledgeArticle.topic_category
    ).all()
    return render_template("sap/index.html", articles=articles)


@main_bp.route("/aws")
def aws_pillar():
    """Tampilkan semua Knowledge Article untuk pilar AWS Cloud Infrastructure."""
    # Ambil semua artikel AWS dari database, urutkan berdasarkan kategori topik
    articles = KnowledgeArticle.query.filter_by(pillar="AWS").order_by(
        KnowledgeArticle.topic_category
    ).all()
    return render_template("aws/index.html", articles=articles)


@main_bp.route("/best-practices")
def best_practices():
    """
    Tampilkan daftar Best Practice.
    Guest hanya melihat judul dan teaser (dengan blur + lock icon).
    User terautentikasi melihat konten penuh.
    """
    # Ambil semua best practice, urutkan berdasarkan pillar
    practices = BestPractice.query.order_by(BestPractice.pillar).all()
    # Tentukan bahasa yang dipilih dari session, default ke English
    lang = session.get("lang", "en")
    return render_template(
        "best_practices/index.html",
        practices=practices,
        is_authenticated=current_user.is_authenticated,
        lang=lang,
    )

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
    """
    Tampilkan halaman dashboard utama dengan Bento Box/Grid layout.
    Mengambil artikel dari kedua pillar (SAP dan GCP) untuk ditampilkan
    sebagai preview card di halaman utama.
    """
    # Ambil 4 artikel terbaru dari pilar SAP untuk preview dashboard
    sap_articles = KnowledgeArticle.query.filter_by(pillar="SAP").limit(4).all()
    # Ambil 4 artikel terbaru dari pilar GCP untuk preview dashboard
    gcp_articles = KnowledgeArticle.query.filter_by(pillar="GCP").limit(4).all()
    # Ambil 3 best practice terbaru untuk ditampilkan di section gated
    recent_bp = BestPractice.query.order_by(BestPractice.id.desc()).limit(3).all()
    # Baca preferensi bahasa dari session, default ke English
    lang = session.get("lang", "en")
    return render_template(
        "dashboard.html",
        sap_articles=sap_articles,
        gcp_articles=gcp_articles,
        recent_bp=recent_bp,
        is_authenticated=current_user.is_authenticated,
        lang=lang,
    )


@main_bp.route("/sap")
def sap_pillar():
    """
    Tampilkan semua Knowledge Article untuk pilar SAP Business One.
    Artikel dikelompokkan berdasarkan topic_category untuk tampilan yang rapi.
    """
    # Ambil semua artikel SAP, urutkan berdasarkan kategori topik
    articles = KnowledgeArticle.query.filter_by(pillar="SAP").order_by(
        KnowledgeArticle.topic_category
    ).all()
    lang = session.get("lang", "en")
    return render_template("sap/index.html", articles=articles, lang=lang)


@main_bp.route("/gcp")
def gcp_pillar():
    """
    Tampilkan semua Knowledge Article untuk pilar GCP Cloud Infrastructure.
    Menggantikan route /aws sesuai perubahan arsitektur ke Google Cloud Platform.
    """
    # Ambil semua artikel GCP, urutkan berdasarkan kategori topik
    articles = KnowledgeArticle.query.filter_by(pillar="GCP").order_by(
        KnowledgeArticle.topic_category
    ).all()
    lang = session.get("lang", "en")
    return render_template("gcp/index.html", articles=articles, lang=lang)


@main_bp.route("/best-practices")
def best_practices():
    """
    Tampilkan daftar Best Practice.
    Guest hanya melihat judul dan teaser (dengan blur + lock icon).
    User terautentikasi melihat konten penuh tanpa blur.
    Logika akses dikontrol di template menggunakan variabel is_authenticated.
    """
    # Ambil semua best practice, urutkan berdasarkan pillar lalu id
    practices = BestPractice.query.order_by(
        BestPractice.pillar, BestPractice.id
    ).all()
    # Baca preferensi bahasa dari session, default ke English
    lang = session.get("lang", "en")
    return render_template(
        "best_practices/index.html",
        practices=practices,
        is_authenticated=current_user.is_authenticated,
        lang=lang,
    )

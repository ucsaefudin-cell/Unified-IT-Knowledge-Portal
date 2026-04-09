"""
Entry point untuk menjalankan aplikasi Flask secara lokal.
Gunakan file ini hanya untuk development. Di production, gunakan Gunicorn.

Cara menjalankan:
    python run.py
    atau
    flask run
"""

from app import create_app

# Buat instance aplikasi menggunakan factory function
app = create_app()

if __name__ == "__main__":
    # Jalankan server development Flask
    # host="0.0.0.0" agar dapat diakses dari luar container/VM jika diperlukan
    app.run(host="0.0.0.0", port=5000, debug=True)

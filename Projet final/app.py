from flask import Flask, render_template_string
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head><title>Legeni Academy</title></head>
<body style="font-family:sans-serif; text-align:center; padding:50px;">
  <h1>Bienvenue sur Legeni Academy</h1>
  <p>Accès aux applications :</p>
  <a href="{{ odoo_url }}" style="padding:10px 20px; background:#875A7B; color:white; text-decoration:none; margin:10px;">Accéder à Odoo</a>
  <a href="{{ pgadmin_url }}" style="padding:10px 20px; background:#336791; color:white; text-decoration:none; margin:10px;">Accéder à pgAdmin</a>
</body>
</html>
"""

@app.route('/')
def home():
    odoo_url = os.getenv("ODOO_URL", "https://www.odoo.com/")
    pgadmin_url = os.getenv("PGADMIN_URL", "https://www.pgadmin.org/")
    return render_template_string(HTML, odoo_url=odoo_url, pgadmin_url=pgadmin_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

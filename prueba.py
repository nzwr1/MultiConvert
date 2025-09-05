from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus
from sqlalchemy import text

app = Flask(__name__)

# Configuración de la base de datos
password = quote_plus("682065025468637Nzwr")  # tu contraseña real
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://postgres:{password}@localhost:5432/MultiConvert'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa SQLAlchemy
db = SQLAlchemy(app)

@app.route("/")
def test_db_connection():
    try:
        # Abre una conexión explícita
        with db.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return "✅ Conexión a la base de datos exitosa"
    except Exception as e:
        return f"❌ Error conectando a la base de datos: {e}"


if __name__ == "__main__":
    app.run(debug=True)
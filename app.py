from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from extensions import db

app = Flask(__name__)
CORS(app)

# importar config antes de criar db
app.config.from_object('config')

# Inicializa extensões
db.init_app(app)

db = SQLAlchemy(app)

from views_logic_festo import *
from models import *
from views_simulacao_festo import *


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)



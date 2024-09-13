from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from app.routes import app as routes_app
from app.models import db

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.config.from_object(Config)

db=SQLAlchemy(app)



@app.before_first_request
def create_tables():
    db.create_all()

app.register_blueprint(routes_app)

if __name__ == '__main__':
    app.run(debug=True)


from flask import Flask
from flask_bootstrap import Bootstrap
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialization
# Create an application instance that handles all requests.
application = Flask(__name__)
application.config.from_object(Config)
db = SQLAlchemy(application)
db.create_all()
db.session.commit()

# login_manager needs to be initiated before running the app
login_manager = LoginManager()
login_manager.init_app(application)

bootstrap = Bootstrap(application)

# Added at the bottom to avoid circular dependencies.
from app import classes
from app import routes

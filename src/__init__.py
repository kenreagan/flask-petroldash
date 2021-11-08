from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user

db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    login_manager.init_app(app)
    
    from src.views import user
    app.register_blueprint(user, url_prefix='/')
    return app
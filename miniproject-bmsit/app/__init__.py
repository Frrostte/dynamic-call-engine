from flask import Flask
from sqlalchemy import create_engine
from flask_login import LoginManager
from flask_session import Session
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
session = Session()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # db.init_app(app)
    # login_manager.init_app(app)
    # session.init_app(app)

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from app.campaign import campaign as campaign_blueprint
    app.register_blueprint(campaign_blueprint, url_prefix='/campaign')

    from app.telephony import telephony as telephony_blueprint
    app.register_blueprint(telephony_blueprint, url_prefix='/telephony')

    return app

# Intializing things
from flask import Flask
from config import Config
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# init my Login Manager
login = LoginManager()

# This is where you will be sent if you are not logged
# into trying to go to a login required page
login.login_view='auth.login'
login.login_message = 'You must first login to view this page.'
login.login_message_category='warning'

# Do inits for database stuff
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    #init the app
    app = Flask(__name__)

    #link our config to oour app
    app.config.from_object(config_class)

    # register plugins
    login.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from .blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app
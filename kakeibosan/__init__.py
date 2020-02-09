from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from kakeibosan.config import config


app = Flask(__name__, static_url_path='/kakeibosan/static')
app.config.from_object(config)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
db.init_app(app)


from kakeibosan.views import auth, dashboard, records, settings, edit_account, edit_fixedcost

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from kakeibosan.config import config


db = SQLAlchemy()


def create_app():
    app = Flask(__name__, static_url_path='/kakeibosan/static')
    app.config.from_object(config)
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    with app.app_context():
        from kakeibosan.models import User

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(user_id)

        migrate = Migrate(app, db)

        from kakeibosan.views import (
            auth, dashboard, records, settings, settings_account, settings_fixedcost,  # settings_category,
        )

        page_modules = [
            auth.bp,
            dashboard.bp,
            records.bp,
            settings.bp,
            settings_account.bp,
            settings_fixedcost.bp,
            # settings_category.bp,
        ]

        for bp in page_modules:
            app.register_blueprint(bp, url_prefix='/kakeibosan')

    return app

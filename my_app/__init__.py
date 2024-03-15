from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required
from flask_wtf import CSRFProtect
from flask_uploads import UploadSet, IMAGES, configure_uploads

""" Initialise the app and all the necessary elements."""
""" Created by Ahmed Mohamud, Barraath Jeganathan, Beatrix Popa, Isaiah John, Saeeda Doolan """


db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
photos = UploadSet('photos', IMAGES)


def create_app(config_classname):
    """ Initialise the Flask application. """

    app = Flask(__name__)
    app.config.from_object(config_classname)
    db.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    csrf.init_app(app)
    csrf._exempt_views.add('dash.dash.dispatch')  # needed so that callbacks work in the dash app
    configure_uploads(app, photos)

    with app.app_context():
        # initialise the dash apps
        from dash_app.dash import init_dashboard, init_demo
        demo = init_demo(app)
        dash_app = init_dashboard(app)
        _protect_dash_views(dash_app)  # only allow logged in users to access the dash app

        # initialise the database
        from my_app.models import User, Profile, Topic, Post
        db.create_all()
        db.Model.metadata.reflect(bind=db.engine)

    register_blueprints(app)
    configure_error_handlers(app)

    return app


def register_blueprints(app):
    from my_app.profile.routes import profile_bp
    app.register_blueprint(profile_bp)

    from my_app.home.routes import home_bp
    app.register_blueprint(home_bp)

    from my_app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    from my_app.menu.routes import menu_bp
    app.register_blueprint(menu_bp)

    from my_app.forum.routes import forum_bp
    app.register_blueprint(forum_bp)


def configure_error_handlers(app):
    """" Provides the error pages for the app """
    """ Written by Isaiah John """

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500


def _protect_dash_views(dash_app):
    for view_func in dash_app.server.view_functions:
        if view_func.startswith(dash_app.config.routes_pathname_prefix):
            dash_app.server.view_functions[view_func] = login_required(dash_app.server.view_functions[view_func])

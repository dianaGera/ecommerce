import os
from flask import Flask, render_template, session
from .auth.views import bp, login_manager
from ecommerce.extentions import db, migrate, bcrypt
from .auth.models import Customer


def create_app(test_config=None, config_objects='ecommerce.settings'):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_objects)
    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    #     SQLALCHEMY_DATABASE_URI='sqlite:///ecm.sqlite3',
    #     SQLALCHEMY_TRACK_MODIFICATIONS=True
    # )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed inF
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/')
    def hello():
        user = Customer.query.all()
        for i in user:
            print('user', i)
        return render_template('products/home-page.html')

    app.register_blueprint(bp)

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    return app

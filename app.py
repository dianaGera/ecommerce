import os
import sys
from flask import Flask, render_template, send_from_directory
from flask_currency import Currency
from ecommerce.auth.views import bp, login_manager
from ecommerce.products.views import pr
from ecommerce.checkout.views import checkout
from ecommerce.extentions import db, migrate, bcrypt, humanize
from ecommerce.auth.models import *
from ecommerce.products.models import *
from ecommerce.checkout.models import *


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
    
    @app.route('/media/<filename>')
    def media(filename):
        return send_from_directory('/home/diana/Documents/my_projects/ecommerce/ecommerce/media', filename)


    app.register_blueprint(bp)
    app.register_blueprint(pr)
    app.register_blueprint(checkout)
    
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    humanize.init_app(app)

    # @humanize.localeselector
    # def get_locale():
    #     return 'ru_RU'

    return app

import logging
# DEBUG: Detailed information, typically of interest only when diagnosing
# problems.
# INFO: Confirmation that things are working as expected.
# WARNING: An indication that something unexpected happened, or indicative of
# some problem in the near future (e.g. ‘disk space low’). The software is
# still working as expected.
# ERROR: Due to a more serious problem, the software has not been able
# to perform some function.
# CRITICAL: A serious error, indicating that the program itself may be unable
# to continue running.
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from cryptoalpha.config import Config


logging.basicConfig(filename='debug.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Create the DB instance
logging.info("Initializing Database")
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()

# If login required - go to login:
login_manager.login_view = 'users.login'
# To display messages - info class (Bootstrap)
login_manager.login_message_category = 'info'
logging.info("Starting main program...")
print("----------------------------------------")
print("         Welcome to the Matrix")
print("----------------------------------------")
print("Application loaded...")
print("You can access it at your browser")
print("Just go to:")
print("http://127.0.0.1:5000/")
print("----------------------------------------")
print("And don't forget to take your red pills")
print("----------------------------------------")


def create_app(config_class=Config):
    logging.info("[create_app] Started create_app function")
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from cryptoalpha.users.routes import users
    from cryptoalpha.transactions.routes import transactions
    from cryptoalpha.api.routes import api
    from cryptoalpha.portfolio.routes import portfolio
    from cryptoalpha.main.routes import main
    from cryptoalpha.errors.handlers import errors

    app.register_blueprint(users)
    app.register_blueprint(transactions)
    app.register_blueprint(api)
    app.register_blueprint(portfolio)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app

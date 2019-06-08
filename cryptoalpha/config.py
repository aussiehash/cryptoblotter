import os


class Config:
    # We could set defaults here but for now they
    # are saved on the ~/.bash_profile file
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ALPHAVANTAGE_API_KEY = os.environ.get('ALPHAVANTAGE_API_KEY')

from datetime import datetime
from cryptoalpha import db, login_manager
from flask import current_app
from flask_login import UserMixin  # Manages session (anon, etc)
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class listofcrypto(db.Model):
    __tablename__ = 'listofcrypto'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    symbol = db.Column(db.String(20))
    website_slug = db.Column(db.String(100))

    def __repr__(self):
        return f"('{self.id}', '{self.symbol}','{self.name}')"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default="default.jpg")
    password = db.Column(db.String(60), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False,
                              default=datetime.utcnow)
    trades = db.relationship('Trades', backref='trade_inputby', lazy=True)
    account = db.relationship('AccountInfo',
                              backref='account_owner', lazy=True)

    def get_reset_token(self, expires_sec=300):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Trades(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trade_inputon = db.Column(db.DateTime, nullable=False,
                              default=datetime.utcnow)
    trade_date = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    trade_currency = db.Column(db.String(3), nullable=False, default='USD')
    trade_asset_ticker = db.Column(db.String(20), nullable=False)
    trade_account = db.Column(db.String(20), nullable=False)
    trade_quantity = db.Column(db.Float)
    trade_operation = db.Column(db.String(2), nullable=False)
    trade_price = db.Column(db.Float)
    trade_fees = db.Column(db.Float, default=0)
    trade_notes = db.Column(db.Text)
    trade_reference_id = db.Column(db.String(50))
    cash_value = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Trades('{self.trade_date}', '{self.trade_asset_ticker}', \
                        '{self.trade_quantity}', '{self.trade_price}', \
                        '{self.trade_fees}')"


class AccountInfo(db.Model):
    account_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    account_longname = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"AccountInfo('{self.account_longname}')"


class Contact(db.Model):
    contact_id = db.Column(db.Integer, primary_key=True)
    message_date = db.Column(db.DateTime, nullable=False,
                             default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    email = db.Column(db.String(255))
    message = db.Column(db.Text)

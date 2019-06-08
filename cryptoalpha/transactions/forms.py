from flask_wtf import FlaskForm
from flask_login import current_user

from cryptoalpha.models import listofcrypto, AccountInfo
from wtforms import StringField,  \
    SubmitField,  SelectField
from wtforms.validators import DataRequired, \
    ValidationError, Optional
from wtforms.fields.html5 import DateField


class NewTrade(FlaskForm):
    transtypes = (("0", ""), ("1", "Asset and Cash"), ("2", "Asset Only"),
                  ("3", "Cash only"))

    trade_type = SelectField('Select type of Transaction', [Optional()],
                             choices=transtypes, default="")
    trade_date = DateField('Trade Date', [DataRequired()])
    trade_asset_ticker = StringField('Crypto Asset', [Optional()])
    trade_operation = SelectField('Operation', [Optional()],
                                  choices=[('B', 'Buy'), ('S', 'Sell'),
                                           ('D', 'Deposit'),
                                           ('W', 'Withdraw')])
    trade_quantity = StringField('Quantity',  [Optional()])
    trade_price = StringField('Price',  [Optional()])
    trade_fees = StringField('Fees in USD', default=0)
    trade_account = StringField('Trade Account')
    cash_account = StringField('Debit (or Credit) Account')
    cash_value = StringField('Total Cash Amount in USD', default=0)
    trade_notes = StringField('Trade Notes and Tags')

    submit = SubmitField('Insert New Trade')

    def validate_trade_account(self, trade_account):
        acc = trade_account.data
        if acc == "":
            raise ValidationError('Trade Account cannot be empty')

    def validate_trade_asset_ticker(self, trade_asset_ticker):
        ticker = trade_asset_ticker.data
        found = False
        listcrypto = listofcrypto.query.all()
        for item in listcrypto:
            if ticker == item.symbol:
                found = True
        if not found:
            raise ValidationError('Ticker not found')
        if ticker == "":
            raise ValidationError('Ticker cannot be empty')

    def validate_trade_price(self, trade_price):
        try:
            price = float(trade_price.data)
        except ValueError:
            raise ValidationError("Invalid Price")
        if price < 0:
            raise ValidationError('Price has to be a positive number')
        if price is "":
            raise ValidationError("Price can't be empty")

    def validate_trade_quantity(self, trade_quantity):
        try:
            quant = float(trade_quantity.data)
        except ValueError:
            raise ValidationError("Invalid Quantity")
        if quant < 0:
            raise ValidationError('Quantity has to be a positive number')
        if quant is "":
            raise ValidationError("Quantity can't be empty")


class NewAccount(FlaskForm):
    account_name = StringField('Account Name', [DataRequired()])
    submit = SubmitField('Insert New Account')

    def validate_account_name(self, account_name):
        account = AccountInfo.query.filter_by(
            account_longname=account_name.data).filter_by(
            user_id=current_user.username).first()
        if account:
            raise ValidationError('Account already exists')


class EditTransaction(FlaskForm):
    transtypes = (("0", ""), ("1", "Asset and Cash"), ("2", "Asset Only"),
                  ("3", "Cash only"))

    trade_date = DateField('Trade Date', [DataRequired()])
    trade_asset_ticker = StringField('Crypto Asset', [Optional()])
    trade_operation = SelectField('Operation',
                                  choices=[('B', 'Buy'), ('S', 'Sell'), (
                                      'D', 'Deposit'), ('W', 'Withdraw')])
    trade_quantity = StringField('Quantity', [DataRequired()])
    trade_price = StringField('Price', [DataRequired()])
    trade_fees = StringField('Fees in USD', default=0)
    trade_account = StringField('Trade Account')
    cash_account = StringField('Debit (or Credit) Account', [
                               Optional()])
    trade_notes = StringField('Trade Notes and Tags')
    match_asset_ticker = SelectField('Currency',
                                     [Optional()], choices=[('USD', 'USD')])
    trade_type = StringField('Select type of Transaction',
                             [Optional()], default="")
    cash_value = StringField('Total Cash Amount in USD', default=0)

    submit = SubmitField('Update Transaction')

    def validate_trade_quantity(self, trade_quantity):
        quant = float(trade_quantity.data)
        if quant < 0:
            raise ValidationError('Quantity has to be a positive number')

# This code was created to import the list of crypto from CoinMarketCap
# into the database for easier queries
# This should only be ran once, unless CoinMarketCap changes something on
# their data and/or new coins need to be included
# to run just execute
# $ python importlistofcrypto.py


import requests
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
# Create the DB instance
db = SQLAlchemy(app)

globalURL = "https://api.coinmarketcap.com/v2/listings/"

# get data from globalURL
request = requests.get(globalURL)
data = request.json()
fulllist = data['data']
cryptolist = []


class Listofcrypto(db.Model):
    __tablename__ = 'listofcrypto'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    symbol = db.Column(db.String(20))
    website_slug = db.Column(db.String(100))


print("Erasing the current list...")

db.metadata.drop_all(db.engine, tables=[Listofcrypto.__table__])
db.metadata.create_all(db.engine, tables=[Listofcrypto.__table__])

for item in fulllist:
    crypto = Listofcrypto(id=item["id"],
                          name=item["name"],
                          symbol=item["symbol"],
                          website_slug=item["website_slug"])

    print(f"Including {crypto.symbol}, {crypto.name} ....")
    db.session.add(crypto)
    db.session.commit()

print("Finished!")

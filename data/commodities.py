import pandas as pd
import yfinance as yf
from sqlalchemy import select
from api_config import LUMBER_INDEX
from .models import Lumber_Price

def get_market_info(ticker_str):
    info = {}
    ticker = yf.Ticker(ticker_str)
    info['closing_price'] = ticker.info['regularMarketPrice']
    info['day_change'] = (ticker.info['regularMarketPrice'] - ticker.info['open'])
    return info

def get_historical_info(ticker_str, period="4y"):
    ticker = yf.Ticker(ticker_str)
    return ticker.history(period=period)

def commodity_exists(db,_class,tuple):
    statement = select(_class).where(_class.date == tuple[0])
    if len(db.session.execute(statement).all()) > 0:
        return True
    return False

def sync_commodities(db): 
    # Get historical data
    historical_df = get_historical_info(LUMBER_INDEX)
    
    # Clean dataframe
    historical_df.drop(columns=["High","Low","Stock Splits", "Dividends","Volume"],inplace=True)

    #Iterate through dataframe and load
    added = 0
    for row in historical_df.itertuples():
        if commodity_exists(db,Lumber_Price,row):
            continue
        lumber_price = Lumber_Price(
            date = row[0],
            ticker = LUMBER_INDEX,
            open = row.Open,
            close = row.Close,
            change= row.Open - row.Close
        ) 
        try:
            db.session.add(lumber_price)
            db.session.commit()
            added += 1
            print("{0} added".format(lumber_price))
        except Exception as ex:
            db.session.rollback()
            print(f"error adding {lumber_price}: {ex} - not added")
            raise
    return added

def delete_all_lumber(db):
    deleted = db.session.query(Lumber_Price).delete()
    db.session.commit()
    return deleted
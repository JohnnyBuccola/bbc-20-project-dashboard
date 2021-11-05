import pandas as pd
import yfinance as yf
import datetime
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

def clean_commodities_df(df):
    # Create date scaffolding
    date_idx = pd.date_range(start='2018-05-01', end=datetime.datetime.today().strftime('%Y-%m-%d'),freq='D',name='date')
    # Drop unused columns
    cleaned_df = df.drop(columns=["High","Low","Stock Splits", "Dividends","Volume"])
    # Regenerate index using scaffolding, and forward-fill values for 
    # missing dates (weekends and holidays when the market was closed)
    cleaned_df = cleaned_df.reindex(date_idx,method='ffill')
    # drop anything still missing, just in case (nothing should be)
    cleaned_df = cleaned_df.dropna(axis=0,how='any')
    return cleaned_df

def sync_commodities(db): 
    # Get historical data
    historical_df = get_historical_info(LUMBER_INDEX)
    
    # Clean dataframe
    historical_df = clean_commodities_df(historical_df)

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
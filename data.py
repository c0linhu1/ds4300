"""
pulling company data from Finnhub API and loading into MongoDB Atlas
DS4300 HW3
"""

import os
import time
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import yfinance as yf
from pymongo import MongoClient
 

load_dotenv()

# load all API keys
API_KEYS = [os.environ.get(f"FINNHUB_API_KEY_{i}") for i in range(1, 11)]
API_KEYS = [k for k in API_KEYS if k]
current_key_index = 0

MONGO_URI = os.environ.get("MONGO_URI")
BASE_URL = "https://finnhub.io/api/v1"

# S&P 500 / large-cap symbols to pull from - used claude to find all the tickers
SYMBOLS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B", "JPM", "JNJ",
    "V", "UNH", "HD", "PG", "MA", "DIS", "PYPL", "BAC", "ADBE", "CMCSA",
    "NFLX", "XOM", "INTC", "CSCO", "PFE", "ABT", "TMO", "AVGO", "COST", "NKE",
    "PEP", "MRK", "WMT", "CVX", "LLY", "ABBV", "KO", "MCD", "DHR", "QCOM",
    "TXN", "NEE", "BMY", "UPS", "RTX", "LOW", "AMGN", "SBUX", "GS", "BLK",
    "AMD", "ISRG", "GILD", "MDT", "ADP", "CB", "SYK", "MDLZ", "BKNG", "SCHW",
    "CRM", "SNOW", "UBER", "ABNB", "SQ", "RIVN", "LCID", "PLTR", "SOFI", "COIN",
    "GM", "F", "AAL", "DAL", "UAL", "LUV", "BA", "CAT", "DE", "MMM",
    "IBM", "ORCL", "COP", "EOG", "SLB", "OXY", "HAL", "WFC", "C", "MS",
    "T", "VZ", "TMUS", "CHTR", "PARA", "WBD", "EA", "ATVI", "TTWO", "RBLX"
]


def api_get(endpoint):
    """Make Finnhub API call and looping through keys if hit rate limits"""
    global current_key_index

    for attempt in range(len(API_KEYS)):
        key = API_KEYS[current_key_index]
        url = f"{BASE_URL}{endpoint}&token={key}" if "?" in endpoint else f"{BASE_URL}{endpoint}?token={key}"
        resp = requests.get(url)

        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 429:
            print(f"{current_key_index + 1} rate limited, trying next key")
            current_key_index = (current_key_index + 1) % len(API_KEYS)
        else:
            return None

    print("all api keys rate limited")
    return None


def get_company_profile(symbol):
    return api_get(f"/stock/profile2?symbol={symbol}")
 
 
def get_basic_financials(symbol):
    return api_get(f"/stock/metric?symbol={symbol}&metric=all")
 
 
def get_company_peers(symbol):
    return api_get(f"/stock/peers?symbol={symbol}")
 
 
def get_earnings(symbol):
    return api_get(f"/stock/earnings?symbol={symbol}")
 
 
def get_prices(symbol):
    """
    get daily price data for the past month using yfinance 
    i cant use finnnhub bc i need to pay for past price data
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1mo")
        prices = []
        for date, row in df.iterrows():
            prices.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"])
            })
        return prices
    except:
        return []
 
 
def main():
    # connect to MongoDB Atlas
    client = MongoClient(MONGO_URI)
    db = client["finnhub_db"]
    collection = db["companies"]
 
    # drop existing data
    collection.drop()
    print("connected to MongoDB and loading data\n")
 
    count = 0
    for symbol in SYMBOLS:
        print(f"Fetching {symbol}->")
 
        # get profile
        profile = get_company_profile(symbol)
        if not profile or not profile.get("name"):
            print(f"Skipping {symbol} bc no profile data")
            continue
 
        # get financials
        financials = get_basic_financials(symbol)
 
        # get peers
        peers = get_company_peers(symbol)
 
        # get earnings
        earnings = get_earnings(symbol)
 
        # get daily prices (past month)
        price = get_prices(symbol)
 
        # building document
        doc = {
            "symbol": symbol,
            "name": profile.get("name"),
            "country": profile.get("country"),
            "currency": profile.get("currency"),
            "exchange": profile.get("exchange"),
            "industry": profile.get("finnhubIndustry"),
            "ipo_date": profile.get("ipo"),
            "logo": profile.get("logo"),
            "market_cap": profile.get("marketCapitalization"),
            "shares_outstanding": profile.get("shareOutstanding"),
            "weburl": profile.get("weburl"),
            "phone": profile.get("phone"),
            "peers": peers if peers else [],
            "earnings": earnings[:8] if earnings else [],  # last 8 quarters
            "metrics": financials.get("metric", {}) if financials else {},
            "price_history": price  
        }
 
        collection.insert_one(doc)
        count += 1
        print(f"inserted {symbol}: {profile.get('name')}")
 
    print(f"\nLoaded {count} companies")
    client.close()
 
 
if __name__ == "__main__":
    main()
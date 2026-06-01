"""
generating 2 visualizations
"""

import os
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI")


def main():
    client = MongoClient(MONGO_URI)
    db = client["finnhub_db"]
    co = db["companies"]

    # figure 1: Top 10 Winners and Losers 
    pipeline = [
        {"$match": {"price_history": {"$ne": []}}},
        {"$project": {
            "_id": 0, "symbol": 1,
            "first_close": {"$arrayElemAt": ["$price_history.close", 0]},
            "last_close": {"$arrayElemAt": ["$price_history.close", -1]}
        }},
        {"$project": {
            "symbol": 1,
            "monthly_return_pct": {
                "$round": [
                    {"$multiply": [
                        {"$divide": [{"$subtract": ["$last_close", "$first_close"]}, "$first_close"]},
                        100
                    ]}, 2
                ]
            }
        }},
        {"$sort": {"monthly_return_pct": -1}}
    ]
    results = list(co.aggregate(pipeline))
    top = results[:10]
    bottom = results[-10:]
    combined = bottom + top
    symbols = [r["symbol"] for r in combined]
    returns = [r["monthly_return_pct"] for r in combined]
    colors = ['green' if r >= 0 else 'red' for r in returns]

    fig, ax = plt.subplots(figsize=(12, 6))
    # 
    ax.barh(symbols, returns, color=colors)
    ax.set_xlabel("Monthly Return (%)")
    ax.set_title("Top 10 Winners and Losers — Past Month Returns")
    ax.axvline(x=0, color='black', linewidth=0.5)
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig("fig1_monthly_returns.png", dpi=150)
    print("saved fig1")

    # Figure 2: Top 5 Tech Stocks Price Performance 
    tech_stocks = list(co.find(
        {"industry": "Technology", "price_history": {"$ne": []}},
        {"_id": 0, "symbol": 1, "price_history": 1}
    ).sort("market_cap", -1).limit(5))

    fig, ax = plt.subplots(figsize=(12, 6))
    for stock in tech_stocks:
        dates = [day["date"] for day in stock["price_history"]]
        closes = [day["close"] for day in stock["price_history"]]
        base = closes[0]
        normalized = [(c / base - 1) * 100 for c in closes]
        ax.plot(range(len(dates)), normalized, label=stock["symbol"], linewidth=2)

    ax.set_xlabel("Trading Days")
    ax.set_ylabel("% Change from Start")
    ax.set_title("Top 5 Tech Stocks — Normalized Price Performance (Past Month)")
    ax.legend()
    ax.grid(alpha=0.3)
    ax.axhline(y=0, color='black', linewidth=0.5)
    plt.tight_layout()
    plt.savefig("fig2_tech_performance.png", dpi=150)
    print("saved fig2")

    client.close()

    
    print("\nvizs saved")


if __name__ == "__main__":
    main()
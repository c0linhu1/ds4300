"""
running all 10 MongoDB queries and printing output 
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI")


def main():
    client = MongoClient(MONGO_URI)
    db = client["finnhub_db"]
    co = db["companies"]

    print("QUERY 1: Technology companies by market cap")
    print("Question: Which companies are in the Technology industry?")
    for doc in co.find({"industry": "Technology"}, {"_id": 0, "name": 1, "symbol": 1, "market_cap": 1}).sort("market_cap", -1):
        print(doc)

    print("QUERY 2: Top 10 companies by market cap")
    print("Question: What are the 10 largest companies by market cap?")
    for doc in co.find({"market_cap": {"$gt": 0}}, {"_id": 0, "name": 1, "symbol": 1, "market_cap": 1, "industry": 1}).sort("market_cap", -1).limit(10):
        print(doc)

    print("QUERY 3: Value stocks (PE ratio under 15)")
    print("Question: Which companies have a PE ratio below 15?")
    for doc in co.find({"metrics.peNormalizedAnnual": {"$lt": 15, "$gt": 0}}, {"_id": 0, "name": 1, "symbol": 1, "metrics.peNormalizedAnnual": 1, "industry": 1}).sort("metrics.peNormalizedAnnual", 1):
        print(doc)

    print("QUERY 4: Average market cap by industry")
    print("Question: What is the average market cap for each industry?")
    pipeline = [
        {"$match": {"market_cap": {"$gt": 0}}},
        {"$group": {"_id": "$industry", "avg_market_cap": {"$avg": "$market_cap"}, "count": {"$sum": 1}}},
        {"$sort": {"avg_market_cap": -1}},
        {"$project": {"_id": 0, "industry": "$_id", "avg_market_cap": {"$round": ["$avg_market_cap", 2]}, "count": 1}}
    ]
    for doc in co.aggregate(pipeline):
        print(doc)

    print("QUERY 5: High beta (volatile) stocks")
    print("Question: Which companies have a beta > 1.5?")
    for doc in co.find({"metrics.beta": {"$gt": 1.5}}, {"_id": 0, "name": 1, "symbol": 1, "metrics.beta": 1, "industry": 1}).sort("metrics.beta", -1):
        print(doc)


    print("QUERY 6: Count of companies per industry")
    print("Question: How many companies are in each industry?")

    pipeline = [
        {"$group": {"_id": "$industry", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$project": {"_id": 0, "industry": "$_id", "count": 1}}
    ]
    for doc in co.aggregate(pipeline):
        print(doc)


    print("QUERY 7: Companies that beat earnings estimates")
    print("Question: Which companies beat their most recent quarterly earnings estimate?")
    pipeline = [
        {"$match": {"earnings": {"$ne": []}}},
        {"$project": {
            "_id": 0, "name": 1, "symbol": 1,
            "latest_actual": {"$arrayElemAt": ["$earnings.actual", 0]},
            "latest_estimate": {"$arrayElemAt": ["$earnings.estimate", 0]},
            "latest_period": {"$arrayElemAt": ["$earnings.period", 0]}
        }},
        {"$match": {"$expr": {"$gt": ["$latest_actual", "$latest_estimate"]}}},
        {"$limit": 10}
    ]
    for doc in co.aggregate(pipeline):
        print(doc)


    print("QUERY 8: Highest volume trading day per company")
    print("Question: For each company, what was the highest volume trading day in the past month?")

    pipeline = [
        {"$match": {"price_history": {"$ne": []}}},
        {"$project": {
            "_id": 0, "name": 1, "symbol": 1,
            "max_volume_day": {
                "$arrayElemAt": [
                    {"$filter": {
                        "input": "$price_history",
                        "as": "day",
                        "cond": {"$eq": ["$$day.volume", {"$max": "$price_history.volume"}]}
                    }}, 0
                ]
            }
        }},
        {"$sort": {"max_volume_day.volume": -1}},
        {"$limit": 10}
    ]
    for doc in co.aggregate(pipeline):
        print(doc)


    print("QUERY 9: Monthly return for each stock")
    print("Question: What is the monthly return based on first and last closing price?")
    pipeline = [
        {"$match": {"price_history": {"$ne": []}}},
        {"$project": {
            "_id": 0, "name": 1, "symbol": 1, "industry": 1,
            "first_close": {"$arrayElemAt": ["$price_history.close", 0]},
            "last_close": {"$arrayElemAt": ["$price_history.close", -1]}
        }},
        {"$project": {
            "name": 1, "symbol": 1, "industry": 1,
            "first_close": 1, "last_close": 1,
            "monthly_return_pct": {
                "$round": [
                    {"$multiply": [
                        {"$divide": [{"$subtract": ["$last_close", "$first_close"]}, "$first_close"]},
                        100
                    ]}, 2
                ]
            }
        }},
        {"$sort": {"monthly_return_pct": -1}},
        {"$limit": 10}
    ]
    for doc in co.aggregate(pipeline):
        print(doc)

 
    print("QUERY 10: Average daily trading volume by industry")
    print("Question: Which industries have the highest average daily trading volume?")
    pipeline = [
        {"$match": {"price_history": {"$ne": []}}},
        {"$project": {"industry": 1, "avg_volume": {"$avg": "$price_history.volume"}}},
        {"$group": {"_id": "$industry", "avg_daily_volume": {"$avg": "$avg_volume"}, "num_companies": {"$sum": 1}}},
        {"$sort": {"avg_daily_volume": -1}},
        {"$project": {"_id": 0, "industry": "$_id", "avg_daily_volume": {"$round": ["$avg_daily_volume", 0]}, "num_companies": 1}}
    ]
    for doc in co.aggregate(pipeline):
        print(doc)




    client.close()


if __name__ == "__main__":
    main()
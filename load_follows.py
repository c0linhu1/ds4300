"""
loading follows.csv into follow table
"""

import os
import csv
from dotenv import load_dotenv
from dbutils import DBUtils

load_dotenv(".env1")

DATABASE = "twitter"


def main():
    user = os.environ.get("TWITTER_DB_USER", "root")
    password = os.environ.get("TWITTER_DB_PASSWORD", "")
    dbu = DBUtils(user, password, DATABASE)

    with open("follows.csv", "r") as f:
        reader = csv.reader(f)
        next(reader)  # skip header

        rows = [(int(row[0]), int(row[1])) for row in reader]

    sql = "INSERT INTO follows (follower_id, followee_id) VALUES (%s, %s)"
    dbu.insert_many(sql, rows)

    print(f"Done: loaded {len(rows)} follow relationships")
    dbu.close()


if __name__ == "__main__":
    main()
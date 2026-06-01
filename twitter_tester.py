import os
import csv
import time
import random
from twitter_mysql import TwitterAPI
from tweet import Tweet

TWEET_FILE = "tweet.csv"
DATABASE = "twitter"  
NUM_TIMELINE_TESTS = 1000  


def load_follower_ids(api):
    """Get a list of distinct follower_ids for random timeline testing"""
    cursor = api.dbu.con.cursor()
    cursor.execute("SELECT DISTINCT follower_id FROM follows")
    ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return ids


def test_post_tweets(api, filepath):
    """Read tweets from CSV and post them one at a time measuring throughput"""
    count = 0
    start = time.time()

    with open(filepath, "r") as f:
        reader = csv.reader(f)
        next(reader)  

        for row in reader:
            user_id = int(row[0])
            tweet_text = row[1]
            t = Tweet(user_id=user_id, tweet_text=tweet_text)
            api.post_tweet(t)
            count += 1

    elapsed = time.time() - start
    rate = count / elapsed
    print(f"pposted {count} tweets in {elapsed:.2f}s")
    print(f"postTweet rate: {rate:.1f} tweets/sec\n")
    return rate


def test_get_timeline(api, follower_ids, n=NUM_TIMELINE_TESTS):
    """randomly pick users and get their home timelines"""

    start = time.time()
    for i in range(n):
        uid = random.choice(follower_ids)
        timeline = api.get_timeline(uid)
    
    elapsed = time.time() - start
    rate = n / elapsed
    print(f"\got {n} timelines in {elapsed:.2f}s")
    print(f"getTimeline rate: {rate:.1f} timelines/sec\n")
    return rate


def main():

    user = os.environ.get("TWITTER_DB_USER", "root")
    password = os.environ.get("TWITTER_DB_PASSWORD", "")
    api = TwitterAPI(user, password, DATABASE)

    post_rate = test_post_tweets(api, TWEET_FILE)

    follower_ids = load_follower_ids(api)
    timeline_rate = test_get_timeline(api, follower_ids)

    # sunmary
    print(f"postTweet: {post_rate:.1f} API calls/sec")
    print(f"getTimeline: {timeline_rate:.1f} API calls/sec")

    api.close()


if __name__ == "__main__":
    main()

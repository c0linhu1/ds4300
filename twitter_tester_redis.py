"""
Performance testing for Twitter Redis implementation
DS4300 HW2
"""

import csv
import time
import random
from twitter_redis import TwitterAPI
from tweet import Tweet

TWEET_FILE = "tweet.csv"
FOLLOWS_FILE = "follows.csv"
NUM_TIMELINE_TESTS = 1000


def load_follows(api, filepath):
    count = 0
    with open(filepath, "r") as f:
        reader = csv.reader(f)
        next(reader) 
        for row in reader:
            follower_id = int(row[0])
            followee_id = int(row[1])
            api.load_followers(follower_id, followee_id)
            count += 1
    return count


def get_follower_ids(filepath):
    """Get a list of distinct follower_ids for random timeline testing"""
    ids = set()
    with open(filepath, "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            ids.add(int(row[0]))
    return list(ids)


def test_post_tweets(api, filepath):
    """Read tweets from CSV and post them one at a time"""
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
    print(f"\nposted {count} tweets in {elapsed:.2f}s")
    print(f"postTweet rate: {rate:.1f} tweets/sec\n")
    return rate


def test_get_timeline(api, follower_ids, n=NUM_TIMELINE_TESTS):
    """Randomly pick users and retrieve their home timelines"""
    start = time.time()

    for i in range(n):
        uid = random.choice(follower_ids)
        timeline = api.get_timeline(uid)

    elapsed = time.time() - start
    rate = n / elapsed
    print(f"\nRetrieved {n} timelines in {elapsed:.2f}s")
    print(f"getTimeline rate: {rate:.1f} timelines/sec\n")
    return rate


def main():
    api = TwitterAPI()
    api.reset()

    load_follows(api, FOLLOWS_FILE)

    post_rate = test_post_tweets(api, TWEET_FILE)
    follower_ids = get_follower_ids(FOLLOWS_FILE)
    timeline_rate = test_get_timeline(api, follower_ids)

    # summary
    print(f"postTweet: {post_rate:.1f} API calls/sec")
    print(f"getTimeline: {timeline_rate:.1f} API calls/sec")

    api.close()


if __name__ == "__main__":
    main()

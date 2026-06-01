"""
twitter_redis.py
Twitter API implementation using Redis (Method 1)

On postTweet: store the tweet and push it to each follower's home timeline.
On getTimeline: simply read the user's pre-built home timeline list.
"""

import redis
import json
import time
from tweet import Tweet


class TwitterAPI:

    def __init__(self, host="localhost", port=6379):
        self.r = redis.Redis(host=host, port=port, decode_responses=True)

    def reset(self):
        """ Clear all keys in Redis """
        self.r.flushdb()

    def load_followers(self, follower_id, followee_id):
        """ Store a follow relationship: follower follows followee.
        Also store reverse: followee is followed by follower. """
        # followers:{user_id} -> set of users who follow this user
        self.r.sadd(f"followers:{followee_id}", follower_id)

    def post_tweet(self, tweet):
        """ Post a tweet and push it to each follower's timeline. """
        # Generate a unique tweet_id
        tweet_id = self.r.incr("tweet_id_counter")

        # Set timestamp
        tweet_ts = time.time()

        # Store the tweet as a hash
        tweet_key = f"tweet:{tweet_id}"
        tweet_data = json.dumps({
            "tweet_id": tweet_id,
            "user_id": tweet.user_id,
            "tweet_ts": tweet_ts,
            "tweet_text": tweet.tweet_text
        })

        self.r.set(tweet_key, tweet_data)

        # Push tweet key to each follower's home timeline
        followers = self.r.smembers(f"followers:{tweet.user_id}")
        for follower_id in followers:
            timeline_key = f"timeline:{follower_id}"
            self.r.lpush(timeline_key, tweet_key)
            # Keep only the 10 most recent
            self.r.ltrim(timeline_key, 0, 9)

    def get_timeline(self, user_id):
        """ Retrieve the 10 most recent tweets from the user's home timeline. """
        timeline_key = f"timeline:{user_id}"
        tweet_keys = self.r.lrange(timeline_key, 0, 9)

        tweets = []
        for key in tweet_keys:
            data = self.r.get(key)
            if data:
                d = json.loads(data)
                t = Tweet(
                    tweet_id=d["tweet_id"],
                    user_id=d["user_id"],
                    tweet_ts=d["tweet_ts"],
                    tweet_text=d["tweet_text"]
                )
                tweets.append(t)

        return tweets

    def close(self):
        pass

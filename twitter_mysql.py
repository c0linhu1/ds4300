"""
Twitter API implementation using MySQL
"""

from dbutils import DBUtils
from tweet import Tweet


class TwitterAPI:

    def __init__(self, user, password, database, host="localhost"):
        self.dbu = DBUtils(user, password, database, host)

    def post_tweet(self, tweet):
        """ Post a single tweet to the database tweet_id is auto-assigned, tweet_ts is set to current timestamp. """
        sql = "INSERT INTO tweet (user_id, tweet_text, tweet_ts) VALUES (%s, %s, NOW(6))"
        val = (tweet.user_id, tweet.tweet_text)
        self.dbu.insert_one(sql, val)

    def get_timeline(self, user_id):
        """Getting the 10 most recent tweets from users followed by user_id """
        sql = """
            SELECT t.tweet_id, t.user_id, t.tweet_ts, t.tweet_text
            FROM tweet t
            JOIN follows f ON t.user_id = f.followee_id
            WHERE f.follower_id = %s
            ORDER BY t.tweet_ts DESC
            LIMIT 10
        """

        cursor = self.dbu.con.cursor()
        cursor.execute(sql, (user_id,))
        rows = cursor.fetchall()
        cursor.close()

        tweets = []
        for row in rows:
            t = Tweet(
                tweet_id=row[0],
                user_id=row[1],
                tweet_ts=row[2],
                tweet_text=row[3]
            )
            tweets.append(t)

        return tweets

    def close(self):
        self.dbu.close()

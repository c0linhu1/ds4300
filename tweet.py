class Tweet:

    def __init__(self, user_id, tweet_text, tweet_ts=None, tweet_id=None):
        self.tweet_id = tweet_id
        self.user_id = user_id
        self.tweet_ts = tweet_ts
        self.tweet_text = tweet_text

    def __str__(self):
        return f"[{self.tweet_ts}] User {self.user_id}: {self.tweet_text[:50]}"

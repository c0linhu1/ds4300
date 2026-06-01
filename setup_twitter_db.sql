CREATE DATABASE IF NOT EXISTS twitter;
USE twitter;

DROP TABLE IF EXISTS tweet;
DROP TABLE IF EXISTS follows;

CREATE TABLE tweet (
    tweet_id    INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT,    -- foreign key
    tweet_ts    DATETIME(6),
    tweet_text  VARCHAR(140)
);

CREATE TABLE follows (
    follower_id INT,    -- foreign key
    followee_id INT       -- foreign key
);

-- Creting indexes

-- Index on follows.follower_id for looking up who a user follows
CREATE INDEX idx_follows_follower ON follows(follower_id);

-- Index on tweet.user_id for finding tweets by a specific user
CREATE INDEX idx_tweet_user ON tweet(user_id);

-- Composite index to help the ORDER BY in timeline queries
CREATE INDEX idx_tweet_user_ts ON tweet(user_id, tweet_ts DESC);



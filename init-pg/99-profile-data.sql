CREATE TABLE IF NOT EXISTS profile_data (
    uid NUMERIC NOT NULL,
    service TEXT NOT NULL,
    username TEXT NOT NULL,
    PRIMARY KEY (uid, service)
);

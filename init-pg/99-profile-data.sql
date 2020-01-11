CREATE TABLE IF NOT EXISTS profile_data (
    uid NUMERIC NOT NULL,
    service TEXT NOT NULL,
    username TEXT NOT NULL,
    PRIMARY KEY (uid, service)
);

CREATE INDEX IF NOT EXISTS idx_profile_data_uid 
ON profile_data(uid);

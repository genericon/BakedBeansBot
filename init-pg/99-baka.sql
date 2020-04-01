CREATE TABLE IF NOT EXISTS baka_nicks (
    user_id NUMERIC NOT NULL,
    server_id NUMERIC NOT NULL,
    nick TEXT,
    PRIMARY KEY (uid, server_id)
);

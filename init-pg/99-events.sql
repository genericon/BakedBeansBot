CREATE TABLE IF NOT EXISTS events (
    id SERIAL NOT NULL PRIMARY KEY,
    server_id NUMERIC NOT NULL,
    name TEXT NOT NULL,
    role_id NUMERIC,
    UNIQUE (server_id, name)
);

CREATE TABLE IF NOT EXISTS events_data (
    uid NUMERIC NOT NULL,
    event_id INTEGER NOT NULL,
    PRIMARY KEY (uid, event_id),
    FOREIGN KEY (event_id) REFERENCES events (id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_events_data_uid 
ON events_data(uid);

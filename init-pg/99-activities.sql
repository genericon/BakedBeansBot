CREATE TABLE IF NOT EXISTS activities (
    id SERIAL NOT NULL,
    type INTEGER NOT NULL,
    name TEXT NOT NULL,
    other json DEFAULT '{}'::json NOT NULL
);

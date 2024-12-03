CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE monitor (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    type VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    url TEXT NOT NULL,
    body TEXT,
    method VARCHAR DEFAULT 'GET',
    expected_http_code VARCHAR DEFAULT '20*',
    expected_contain VARCHAR,
    timeout INT DEFAULT 30,
    username VARCHAR,
    password VARCHAR,
    headers JSONB DEFAULT '{}'::jsonb,
    status VARCHAR DEFAULT 'failure',
    response_time VARCHAR DEFAULT '',
    created_at VARCHAR NOT NULL,
    updated_at VARCHAR NOT NULL
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE places (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    user_id INTEGER REFERENCES users(id)
);

CREATE TABLE place_classes (
    id INTEGER PRIMARY KEY,
    place_id INTEGER REFERENCES places(id),
    title TEXT,
    value TEXT
);

CREATE TABLE classes (
    id INTEGER  PRIMARY KEY,
    title TEXT,
    value TEXT
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    place_id INTEGER REFERENCES places(id),
    user_id INTEGER REFERENCES users(id),
    comment TEXT
);

CREATE TABLE images (
    id INTEGER PRIMARY KEY,
    place_id INTEGER REFERENCES places(id),
    image BLOB
);


CREATE INDEX idx_place_comments ON comments (place_id);

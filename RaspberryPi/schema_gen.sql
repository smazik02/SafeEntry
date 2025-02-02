CREATE TABLE IF NOT EXISTS ACCESS_CARDS (
    id TEXT PRIMARY KEY,
    isLocked TINYINT NOT NULL,
    inRoom TINYINT NOT NULL
);

CREATE TABLE IF NOT EXISTS ACCESS_ATTEMPTS(
    id INTEGER PRIMARY KEY,
    accessCard TEXT NOT NULL,
    attemptTime TEXT DEFAULT CURRENT_TIMESTAMP,
    wasAccepted TINYINT NOT NULL,
    reason TEXT,
    FOREIGN KEY (accessCard) REFERENCES ACCESS_CARDS(id)
);

INSERT INTO
    ACCESS_CARDS (id, isLocked, inRoom)
VALUES
    ("AAAA", 1, 0);

INSERT INTO
    ACCESS_CARDS (id, isLocked, inRoom)
VALUES
    ("BBBB", 0, 0);
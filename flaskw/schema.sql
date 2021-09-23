DROP TABLE IF EXISTS box_contract;

CREATE TABLE box_contract (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    descript TEXT,
    difficulty INTEGER NOT NULL,
    creation_date DATETIME NOT NULL,
    expiration_date DATETIME NOT NULL,
    payout INTEGER NOT NULL
);
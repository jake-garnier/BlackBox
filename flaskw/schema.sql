DROP TABLE IF EXISTS contract;
DROP TABLE IF EXISTS attempt;
DROP TABLE IF EXISTS user;

CREATE TABLE contract (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  description TEXT,
  difficulty INTEGER NOT NULL,
  creation_date DATETIME NOT NULL,
  expiration_date DATETIME NOT NULL,
  creater_user_id INTEGER NOT NULL,
  payout INTEGER NOT NULL,
  test_filename TEXT NOT NULL,
  payment_id TEXT,
  payer_id TEXT,
  authorization_id TEXT
);

CREATE TABLE attempt (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  contract_id INTEGER NOT NULL,
  creater_user_id INTEGER NOT NULL,
  attempt_filename TEXT NOT NULL,
  ran BOOLEAN,
  success BOOLEAN,
  failed_tests TEXT,
  function_name TEXT NOT NULL
);

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);
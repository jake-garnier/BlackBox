DROP TABLE IF EXISTS contracts;
DROP TABLE IF EXISTS attempts;
DROP TABLE IF EXISTS user;

CREATE TABLE contracts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  descript TEXT,
  difficulty INTEGER NOT NULL,
  creation_date DATETIME NOT NULL,
  expiration_date DATETIME NOT NULL,
  creater_user_id INTEGER NOT NULL,
  payout INTEGER NOT NULL,
  test_filename TEXT NOT NULL,
  payment_id TEXT NOT NULL
);

CREATE TABLE attempts (
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
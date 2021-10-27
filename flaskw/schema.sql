DROP TABLE IF EXISTS contracts;
DROP TABLE IF EXISTS attempts;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS transactions;

CREATE TABLE contracts (
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
  payer_id TEXT
);

CREATE TABLE attempts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  contract_id INTEGER NOT NULL,
  creater_user_id INTEGER NOT NULL,
  attempt_filename TEXT NOT NULL,
  ran BOOLEAN,
  success BOOLEAN,
  failed_tests TEXT,
  function_name TEXT NOT NULL,
  payment_email TEXT NOT NULL
);

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE transactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  amount INTEGER NOT NULL,
  denomination TEXT NOT NULL,
  receiver_user_id INTEGER,
  sender_user_id INTEGER,
  deposit BOOLEAN
);

DENY DELETE ON Object::transactions
GO;
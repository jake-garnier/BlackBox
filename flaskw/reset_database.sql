DROP TABLE IF EXISTS contracts;
DROP TABLE IF EXISTS attempts;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS transactions;

CREATE TABLE contracts (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  title TEXT NOT NULL,
  _description TEXT,
  difficulty INTEGER NOT NULL,
  creation_date DATETIME NOT NULL,
  expiration_date DATETIME NOT NULL,
  creater_user_id INTEGER NOT NULL,
  payout INTEGER NOT NULL,
  test_filename TEXT NOT NULL,
  payment_id TEXT,
  payer_id TEXT,
  s3_bucket_name TEXT,
  lambda_name TEXT,
  ecr_repository_name TEXT,
  ecr_repository_uri TEXT,
  local_repository_name TEXT,
  _status TEXT
);

CREATE TABLE attempts (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  contract_id INTEGER NOT NULL,
  creater_user_id INTEGER NOT NULL,
  attempt_filename TEXT NOT NULL,
  ran BOOLEAN,
  success BOOLEAN,
  failed_tests TEXT,
  payment_email TEXT NOT NULL,
  _status TEXT
);

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(200) UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE transactions (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  amount DECIMAL(5,2) NOT NULL,
  denomination TEXT NOT NULL,
  receiver_user_id INTEGER,
  sender_user_id INTEGER,
  deposit BOOLEAN,
  fee DECIMAL(5,2)
);

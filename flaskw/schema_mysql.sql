-- MySQL Schema for BlackBox Application

DROP TABLE IF EXISTS attempts;
DROP TABLE IF EXISTS contracts;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE contracts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  _description TEXT,
  difficulty VARCHAR(50) NOT NULL,
  creation_date DATETIME NOT NULL,
  expiration_date DATETIME NOT NULL,
  creater_user_id INT NOT NULL,
  payout DECIMAL(10,2) NOT NULL,
  test_filename VARCHAR(255) NOT NULL,
  payment_id VARCHAR(255),
  payer_id VARCHAR(255),
  _status VARCHAR(50) DEFAULT 'Created',
  s3_bucket_name VARCHAR(255),
  lambda_name VARCHAR(255),
  ecr_repository_name VARCHAR(255),
  ecr_repository_uri TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (creater_user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE attempts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  contract_id INT NOT NULL,
  creater_user_id INT NOT NULL,
  attempt_filename VARCHAR(255) NOT NULL,
  ran BOOLEAN DEFAULT FALSE,
  success BOOLEAN DEFAULT FALSE,
  failed_tests TEXT,
  payment_email VARCHAR(255) NOT NULL,
  _status VARCHAR(50) DEFAULT 'Created',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE,
  FOREIGN KEY (creater_user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE transactions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  amount DECIMAL(10,2) NOT NULL,
  denomination VARCHAR(10) NOT NULL DEFAULT 'USD',
  receiver_user_id INT,
  sender_user_id INT,
  deposit BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (receiver_user_id) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (sender_user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Insert some sample data for testing
INSERT INTO users (username, password) VALUES 
('demo_user', '$2b$12$demohashedpasswordhere'),
('test_contractor', '$2b$12$anotherdemohashedpassword');

INSERT INTO contracts (title, _description, difficulty, creation_date, expiration_date, creater_user_id, payout, test_filename, _status) VALUES 
('Sample Python Function', 'Create a function that calculates the factorial of a number', 'Easy', NOW(), DATE_ADD(NOW(), INTERVAL 30 DAY), 1, 100.00, 'test_factorial.py', 'Online'),
('Data Processing Task', 'Build a function to process CSV data and return statistics', 'Medium', NOW(), DATE_ADD(NOW(), INTERVAL 45 DAY), 1, 250.00, 'test_csv_processor.py', 'Online');
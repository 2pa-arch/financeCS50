CREATE DATABASE  IF NOT EXISTS finance_db;

USE finance_db;

CREATE TABLE  IF NOT EXISTS symbols (
    symbol_id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
    symbol        VARCHAR(128)    NOT NULL,
    company        VARCHAR(128)     NOT NULL
);

CREATE TABLE  IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
    username VARCHAR(255) NOT NULL UNIQUE,
    hash TEXT NOT NULL,
    cash DECIMAL(10,2) NOT NULL DEFAULT 10000.00,
    current_balance DECIMAL(10,2) NOT NULL DEFAULT 10000.00
);


CREATE TABLE  IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
    user_id     INTEGER    NOT NULL,
    symbol_id     INTEGER     NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    transaction_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    transaction_type ENUM('BUY', 'SELL') NOT NULL,
    FOREIGN KEY (user_id)  REFERENCES users (user_id),
    FOREIGN KEY (symbol_id)  REFERENCES symbols (symbol_id)
);

CREATE TABLE IF NOT EXISTS UserAssets (
    user_asset_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    symbol_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (symbol_id) REFERENCES symbols(symbol_id)
);

CREATE INDEX Idxusername ON users (username);

CREATE INDEX Idxsymbols ON symbols (symbol);



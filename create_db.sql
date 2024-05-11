CREATE DATABASE  IF NOT EXISTS finance_db;

USE finance_db;

CREATE TABLE  IF NOT EXISTS symbols (
    id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
    symbols        VARCHAR(128)    NOT NULL,
    company        VARCHAR(128)     NOT NULL
);

CREATE TABLE  IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
    username VARCHAR(255) NOT NULL UNIQUE,
    hash TEXT NOT NULL,
    cash NUMERIC NOT NULL DEFAULT 10000.00
);

CREATE TABLE  IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
    user_id     INTEGER    NOT NULL,
    symbol_id     INTEGER     NOT NULL,
    number INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    date datetime NOT NULL,
    purchase_sale VARCHAR(4) NOT NULL,
    FOREIGN KEY (user_id)  REFERENCES users (id),
    FOREIGN KEY (symbol_id)  REFERENCES symbols (id)
);

USE currency_stock_db;


CREATE TABLE IF NOT EXISTS countries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    country_code VARCHAR(6) NOT NULL UNIQUE,
    country_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS regions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    region_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS country_regions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    country_id INT NOT NULL,
    region_id INT NOT NULL,
    FOREIGN KEY (country_id) REFERENCES countries(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (region_id) REFERENCES regions(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS currencies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(6) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    symbol VARCHAR(10),
    data_availability BOOLEAN default false
);

INSERT INTO currencies (code, name, symbol)
VALUES ('USD', 'United States Dollar', '$')
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    symbol = VALUES(symbol);


CREATE TABLE IF NOT EXISTS country_currencies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    country_id INT NOT NULL,
    currency_id INT NOT NULL,
    FOREIGN KEY (country_id) REFERENCES countries(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (currency_id) REFERENCES currencies(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS currencies_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    currency_id INT NOT NULL,
    open_price DECIMAL(20,8) NOT NULL,
    high_price DECIMAL(20,8) NOT NULL,
    low_price DECIMAL(20,8) NOT NULL,
    close_price DECIMAL(20,8) NOT NULL,
    volume DECIMAL(20,8) NOT NULL,
    day_of_week VARCHAR(10) GENERATED ALWAYS AS (DAYNAME(timestamp)) STORED,
    FOREIGN KEY (currency_id) REFERENCES currencies(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
   UNIQUE KEY unique_currency_timestamp (currency_id, timestamp)

);



CREATE TABLE IF NOT EXISTS currencies_trained_models (
    id INT AUTO_INCREMENT PRIMARY KEY,
    currency_id INT NOT NULL,
    model_name VARCHAR(100) DEFAULT 'SeasonalRNN',
    training_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    model_file_path VARCHAR(255),
    metrics JSON,
    param_grid JSON,
    is_latest BOOLEAN DEFAULT FALSE,
    CONSTRAINT unique_latest_model UNIQUE (currency_id, is_latest),
    FOREIGN KEY (currency_id) REFERENCES currencies(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS currencies_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    currency_id INT NOT NULL,
    predicted_value DECIMAL(20,8) NOT NULL,
    prediction_date DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (currency_id) REFERENCES currencies(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);





CREATE TABLE IF NOT EXISTS exchanges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    country_id INT,
    FOREIGN KEY (country_id) REFERENCES countries(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_symbol VARCHAR(10) NOT NULL UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    country_id INT NULL,
    logo_url VARCHAR(255),
    FOREIGN KEY (country_id) REFERENCES countries(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS stocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_symbol VARCHAR(10) NOT NULL UNIQUE,
    stock_name VARCHAR(100) NOT NULL,
    company_id INT NOT NULL,
    exchange_id INT NULL,
    share_class VARCHAR(20),
    data_availability BOOLEAN default false,

    FOREIGN KEY (company_id) REFERENCES companies(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (exchange_id) REFERENCES exchanges(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS stocks_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    stock_id INT NOT NULL,
    open_price DECIMAL(20,8) NOT NULL,
    high_price DECIMAL(20,8) NOT NULL,
    low_price DECIMAL(20,8) NOT NULL,
    close_price DECIMAL(20,8) NOT NULL,
    volume DECIMAL(20,8) NOT NULL,
    day_of_week VARCHAR(10) GENERATED ALWAYS AS (DAYNAME(timestamp)) STORED,
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);



CREATE TABLE IF NOT EXISTS stocks_trained_models (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    model_name VARCHAR(100) DEFAULT 'RNN',
    training_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    model_file_path VARCHAR(255),
    metrics JSON,
    param_grid JSON,
    is_latest BOOLEAN DEFAULT FALSE,
    CONSTRAINT unique_latest_model UNIQUE (stock_id, is_latest),
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS stocks_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    predicted_value DECIMAL(20,8) NOT NULL,
    prediction_date DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

#################### USER ###############################

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    firebase_uid VARCHAR(128) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,
    profile_image_url VARCHAR(255),
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);



CREATE TABLE IF NOT EXISTS accounts(
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    account_name VARCHAR(100) NOT NULL,
    public_account_id VARCHAR(16) NOT NULL UNIQUE,
    currency_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_accounts_user_id FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_accounts_currency_id FOREIGN KEY (currency_id) REFERENCES currencies(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);




CREATE TABLE IF NOT EXISTS contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    account_name VARCHAR(100) NOT NULL,
    public_account_id VARCHAR(16) NOT NULL UNIQUE,


     CONSTRAINT fk_contacts_user_id FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
     CONSTRAINT fk_contacts_account FOREIGN KEY (public_account_id) REFERENCES accounts(public_account_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE



);



CREATE TABLE IF NOT EXISTS account_currencies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,
    currency_id INT NOT NULL,
    balance DECIMAL(20,8) DEFAULT 0.00000000,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (currency_id) REFERENCES currencies(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    UNIQUE KEY unique_account_currency (account_id, currency_id)
);

CREATE TABLE IF NOT EXISTS account_currency_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_account_id INT,
    receiver_account_id INT,
    transaction_type ENUM('deposit', 'withdraw', 'buy' ,'sell', 'send') NOT NULL,
    title VARCHAR (255),
    amount DECIMAL(20,8) NOT NULL,
    currency_id INT NOT NULL,
    exchange_rate DECIMAL(20,8),
    transaction_fee DECIMAL(20,8) DEFAULT 0.00000000,
    default_currency_cost DECIMAL(20,8) DEFAULT 0.00000000,

    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_positive_amount CHECK (amount > 0),
    FOREIGN KEY (sender_account_id) REFERENCES accounts(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (receiver_account_id) REFERENCES accounts(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (currency_id) REFERENCES currencies(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS account_stocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,
    stock_id INT NOT NULL,
    shares DECIMAL(20,8) DEFAULT 0.00000000,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    UNIQUE KEY unique_account_stock (account_id, stock_id)
);



CREATE TABLE IF NOT EXISTS account_stock_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,
    transaction_type ENUM('buy', 'sell') NOT NULL,
    title VARCHAR (255),

    stock_id INT NOT NULL,
    shares DECIMAL(20,8) NOT NULL,
    price_per_share DECIMAL(20,8) NOT NULL,
    currency_id INT NOT NULL,
    transaction_fee DECIMAL(20,8) DEFAULT 0.00000000,
    default_currency_cost DECIMAL(20,8) DEFAULT 0.00000000,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_positive_shares CHECK (shares > 0),
    FOREIGN KEY (account_id) REFERENCES accounts(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (currency_id) REFERENCES currencies(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE INDEX idx_stocks_data_timestamp ON stocks_data(stock_id, timestamp);
CREATE INDEX idx_currencies_data_timestamp ON currencies_data(currency_id, timestamp);

CREATE TABLE IF NOT EXISTS user_notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);





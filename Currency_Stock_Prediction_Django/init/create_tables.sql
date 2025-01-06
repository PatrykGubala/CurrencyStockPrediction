USE currency_stock_db;

-- ################### SERVER TABLES ####################### --
-- 1. Countries Table
CREATE TABLE IF NOT EXISTS countries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    country_code VARCHAR(6) NOT NULL UNIQUE,
    country_name VARCHAR(100) NOT NULL
);

-- 2. Regions Table
CREATE TABLE IF NOT EXISTS regions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    region_name VARCHAR(50) NOT NULL UNIQUE
);

-- 3. Country_Regions (Many-to-Many)
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

-- 4. Currencies Table
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

-- 11. Currencies_Data Table
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
    FOREIGN KEY (currency_id) REFERENCES currencies(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS currencies_trained_model_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trained_model_id INT NOT NULL,
    currency_id INT NOT NULL,
    predicted_value DECIMAL(20,8) NOT NULL,
    prediction_date DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trained_model_id) REFERENCES currencies_trained_models(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (currency_id) REFERENCES currencies(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);



-- 5. Country_Currencies (Many-to-Many)
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


-- 7. Exchanges Table
CREATE TABLE IF NOT EXISTS exchanges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    country_id INT,
    FOREIGN KEY (country_id) REFERENCES countries(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- 8. Companies Table
CREATE TABLE IF NOT EXISTS companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_symbol VARCHAR(10) NOT NULL UNIQUE,
    company_name VARCHAR(100) NOT NULL,
    country_id INT NOT NULL,
    sector VARCHAR(50),
    industry VARCHAR(50),
    FOREIGN KEY (country_id) REFERENCES countries(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- 9. Stocks Table
CREATE TABLE IF NOT EXISTS stocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_symbol VARCHAR(10) NOT NULL UNIQUE,
    stock_name VARCHAR(100) NOT NULL,
    company_id INT NOT NULL,
    exchange_id INT,
    share_class VARCHAR(20),
    FOREIGN KEY (company_id) REFERENCES companies(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (exchange_id) REFERENCES exchanges(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- 10. Stock_Data Table
CREATE TABLE IF NOT EXISTS stock_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    stock_id INT NOT NULL,
    open_price DECIMAL(20,8) NOT NULL,
    high_price DECIMAL(20,8) NOT NULL,
    low_price DECIMAL(20,8) NOT NULL,
    close_price DECIMAL(20,8) NOT NULL,
    volume DECIMAL(20,4) NOT NULL,
    day_of_week VARCHAR(10) GENERATED ALWAYS AS (DAYNAME(timestamp)) STORED,
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);



-- 12. Stocks_Trained_Models Table
CREATE TABLE IF NOT EXISTS stocks_trained_models (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    model_name VARCHAR(100) DEFAULT 'SeasonalRNN',
    training_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    model_file_path VARCHAR(255),
    metrics JSON,
    param_grid JSON,
    is_latest BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- 13. Stocks_Trained_Model_Predictions Table
CREATE TABLE IF NOT EXISTS stocks_trained_model_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trained_model_id INT NOT NULL,
    stock_id INT NOT NULL,
    predicted_value DECIMAL(20,8) NOT NULL,
    prediction_date DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trained_model_id) REFERENCES stocks_trained_models(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);



-- 14. Country_Translations Table
CREATE TABLE IF NOT EXISTS country_translations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    country_id INT NOT NULL,
    language_code VARCHAR(10) NOT NULL,
    name_common VARCHAR(100) NOT NULL,
    name_official VARCHAR(100) NOT NULL,
    FOREIGN KEY (country_id) REFERENCES countries(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    UNIQUE KEY unique_translation (country_id, language_code)
);

-- 15. GDP_Data Table
CREATE TABLE IF NOT EXISTS gdp_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    period_date DATE NOT NULL,
    country_id INT NOT NULL,
    gdp_current_usd DECIMAL(18,2),
    gdp_growth_rate DECIMAL(5,2),
    frequency ENUM('A', 'Q') NOT NULL,
    FOREIGN KEY (country_id) REFERENCES countries(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    UNIQUE KEY unique_period_country (period_date, country_id)
);

-- ############################ USERS TABLES ############################ --
-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    firebase_uid VARCHAR(128) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,
    profile_image_url VARCHAR(255),
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. Accounts Table
CREATE TABLE IF NOT EXISTS accounts
(
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


-- 3. Account_Currencies Table
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

-- 4. Account_Stocks Table
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

-- 5. Account_Currency_Transactions Table
CREATE TABLE IF NOT EXISTS account_currency_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_account_id INT,
    receiver_account_id INT,
    transaction_type ENUM('deposit', 'withdraw', 'transfer', 'exchange', 'send') NOT NULL,
    title VARCHAR (255),
    amount DECIMAL(20,8) NOT NULL,
    currency_id INT NOT NULL,
    exchange_currency_id INT,
    exchange_rate DECIMAL(20,8),
    transaction_fee DECIMAL(20,8) DEFAULT 0.00000000,
    default_currency_cost DECIMAL(20,8) DEFAULT 0.00000000,

    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_account_id) REFERENCES accounts(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (receiver_account_id) REFERENCES accounts(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (currency_id) REFERENCES currencies(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (exchange_currency_id) REFERENCES currencies(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- 6. Account_Stock_Transactions Table
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

-- 7. User_Notifications Table (With Title)
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

-- 8. User_Preferences Table
CREATE TABLE IF NOT EXISTS user_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    default_display_currency_id INT NOT NULL,
    dark_mode ENUM('DEFAULT', 'DARK_MODE', 'LIGHT_MODE') DEFAULT 'DEFAULT',
    notifications_enabled BOOLEAN DEFAULT TRUE,
    user_language ENUM('PL', 'EN') DEFAULT 'EN',
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (default_display_currency_id) REFERENCES currencies(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS account_currency_value_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_currency_id INT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    balance_usd DECIMAL(30,8) NOT NULL,
    FOREIGN KEY (account_currency_id) REFERENCES account_currencies(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS account_stock_value_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_stock_id INT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    value_usd DECIMAL(30,8) NOT NULL,
    FOREIGN KEY (account_stock_id) REFERENCES account_stocks(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);



-- Create and use the database (will be handled securely by python script but good for standalone)
CREATE DATABASE IF NOT EXISTS personal_finance;
USE personal_finance;

-- Drop tables if they exist to allow clean re-initializations
DROP TABLE IF EXISTS user_corrections;
DROP TABLE IF EXISTS budgets;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL DEFAULT '',
    phone VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL,
    category_type ENUM('INCOME', 'EXPENSE') NOT NULL
);

CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    transaction_type ENUM('INCOME', 'EXPENSE') NOT NULL,
    transaction_date DATE NOT NULL,
    description VARCHAR(255),
    auto_categorized TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE
);

CREATE TABLE budgets (
    budget_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    monthly_limit DECIMAL(12,2) NOT NULL,
    month_year VARCHAR(7) NOT NULL, -- Format: YYYY-MM
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE
);

CREATE TABLE user_corrections (
    correction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    original_description VARCHAR(255) NOT NULL,
    predicted_category_id INT,
    corrected_category_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (predicted_category_id) REFERENCES categories(category_id) ON DELETE SET NULL,
    FOREIGN KEY (corrected_category_id) REFERENCES categories(category_id) ON DELETE SET NULL
);

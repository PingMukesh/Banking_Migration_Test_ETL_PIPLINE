-- ====================================================================
-- Banking Migration ETL Pipeline - MySQL Legacy Source Schema Setup
-- Database: legacy_banking
-- Compatible with: MySQL 8.0+ / MariaDB on localhost (No Docker needed)
-- ====================================================================

CREATE DATABASE IF NOT EXISTS legacy_banking;
USE legacy_banking;

-- Disable foreign key checks for clean recreation
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS legacy_loans;
DROP TABLE IF EXISTS legacy_transactions;
DROP TABLE IF EXISTS legacy_accounts;
DROP TABLE IF EXISTS legacy_customers;
DROP TABLE IF EXISTS legacy_branches;

SET FOREIGN_KEY_CHECKS = 1;

-- 1. LEGACY BRANCHES
CREATE TABLE legacy_branches (
    branch_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_code VARCHAR(10) NOT NULL UNIQUE,
    branch_name VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    postal_code VARCHAR(20),
    swift_bic VARCHAR(11) DEFAULT 'OCIBUS33XXX',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. LEGACY CUSTOMERS
CREATE TABLE legacy_customers (
    cust_id INT PRIMARY KEY,
    first_name VARCHAR(60) NOT NULL,
    last_name VARCHAR(60) NOT NULL,
    tax_id VARCHAR(25) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(30),
    status VARCHAR(5) NOT NULL COMMENT 'A=Active, I=Inactive, S=Suspended, D=Deceased',
    kyc_status VARCHAR(20) DEFAULT 'VERIFIED',
    credit_score INT,
    date_of_birth DATE,
    city VARCHAR(50),
    state_prov VARCHAR(50),
    registered_date DATE NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. LEGACY ACCOUNTS
CREATE TABLE legacy_accounts (
    acct_no VARCHAR(20) PRIMARY KEY,
    cust_id INT NOT NULL,
    branch_code VARCHAR(10) NOT NULL,
    acct_type VARCHAR(10) NOT NULL COMMENT 'SAV=Savings, CHK=Checking, MMA=Money Market, LON=Loan, CD=Cert of Deposit',
    currency VARCHAR(3) DEFAULT 'USD',
    current_balance DECIMAL(18,2) NOT NULL,
    interest_rate DECIMAL(5,2) DEFAULT 0.00,
    status VARCHAR(5) NOT NULL COMMENT 'A=Active, I=Inactive, C=Closed',
    open_date DATE NOT NULL,
    overdraft_limit DECIMAL(18,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_source_cust FOREIGN KEY (cust_id) REFERENCES legacy_customers (cust_id),
    CONSTRAINT fk_source_branch FOREIGN KEY (branch_code) REFERENCES legacy_branches (branch_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. LEGACY TRANSACTIONS
CREATE TABLE legacy_transactions (
    txn_id VARCHAR(30) PRIMARY KEY,
    acct_no VARCHAR(20) NOT NULL,
    txn_time DATETIME NOT NULL,
    txn_type VARCHAR(10) NOT NULL COMMENT 'DEBIT or CREDIT',
    channel VARCHAR(10) NOT NULL COMMENT 'ATM, NET, UPI, POS, BRN',
    amount DECIMAL(18,2) NOT NULL,
    balance_after DECIMAL(18,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'SUCCESS',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_source_acct FOREIGN KEY (acct_no) REFERENCES legacy_accounts (acct_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. LEGACY LOANS
CREATE TABLE legacy_loans (
    loan_id VARCHAR(20) PRIMARY KEY,
    acct_no VARCHAR(20) NOT NULL,
    cust_id INT NOT NULL,
    loan_product VARCHAR(50) NOT NULL,
    principal_amount DECIMAL(18,2) NOT NULL,
    outstanding_balance DECIMAL(18,2) NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    monthly_emi DECIMAL(18,2) NOT NULL,
    tenure_months INT NOT NULL,
    disbursement_date DATE NOT NULL,
    delinquency_bucket INT DEFAULT 0 COMMENT '0=Performing, 30=Watchlist, 60=Substandard, 90=NPA',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_source_loan_acct FOREIGN KEY (acct_no) REFERENCES legacy_accounts (acct_no),
    CONSTRAINT fk_source_loan_cust FOREIGN KEY (cust_id) REFERENCES legacy_customers (cust_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ====================================================================
-- SEED SAMPLE DATA (for migration & validation testing)
-- ====================================================================

-- Seed Branches
INSERT INTO legacy_branches (branch_code, branch_name, region, postal_code, swift_bic) VALUES
('BR001', 'Downtown Main Branch', 'North', '10001', 'OCIBUS33XXX'),
('BR002', 'Westside Commercial', 'West', '90001', 'OCIBUS33XXX'),
('BR003', 'Metro Financial Hub', 'East', '30301', 'OCIBUS33XXX');

-- Seed Customers
INSERT INTO legacy_customers (cust_id, first_name, last_name, tax_id, email, phone, status, kyc_status, credit_score, date_of_birth, city, state_prov, registered_date) VALUES
(101, 'Alice', 'Morgan', '999-11-4581', 'alice@example.com', '+1-555-0101', 'A', 'VERIFIED', 740, '1985-04-12', 'New York', 'NY', '2020-01-15'),
(102, 'Bob', 'Vance', '999-22-9231', 'bob@example.com', '+1-555-0102', 'A', 'VERIFIED', 680, '1978-09-23', 'Scranton', 'PA', '2019-06-10'),
(103, 'Charlie', 'Davis', '999-33-1192', 'charlie@example.com', '+1-555-0103', 'A', 'VERIFIED', 810, '1992-11-05', 'Austin', 'TX', '2021-03-20');

-- Seed Accounts
INSERT INTO legacy_accounts (acct_no, cust_id, branch_code, acct_type, currency, current_balance, interest_rate, status, open_date, overdraft_limit) VALUES
('ACC10001', 101, 'BR001', 'SAV', 'USD', 15400.50, 3.25, 'A', '2020-01-15', 0.00),
('ACC10002', 101, 'BR001', 'CHK', 'USD', 4200.00, 0.50, 'A', '2020-01-15', 500.00),
('ACC10003', 102, 'BR002', 'CHK', 'USD', 8900.25, 0.50, 'A', '2019-06-10', 1000.00),
('ACC10004', 103, 'BR003', 'MMA', 'USD', 35000.00, 4.10, 'A', '2021-03-20', 0.00);

-- Seed Transactions
INSERT INTO legacy_transactions (txn_id, acct_no, txn_time, txn_type, channel, amount, balance_after, status) VALUES
('TXN-SRC-001', 'ACC10001', '2023-01-05 10:15:00', 'CREDIT', 'NET', 1500.00, 15400.50, 'SUCCESS'),
('TXN-SRC-002', 'ACC10002', '2023-01-06 14:30:00', 'DEBIT', 'ATM', 200.00, 4200.00, 'SUCCESS'),
('TXN-SRC-003', 'ACC10004', '2023-01-07 11:20:00', 'CREDIT', 'UPI', 12500.00, 35000.00, 'SUCCESS');

-- Seed Loans
INSERT INTO legacy_loans (loan_id, acct_no, cust_id, loan_product, principal_amount, outstanding_balance, interest_rate, monthly_emi, tenure_months, disbursement_date, delinquency_bucket) VALUES
('LN9001', 'ACC10001', 101, 'MORTGAGE', 250000.00, 210000.00, 4.50, 1266.71, 360, '2020-02-01', 0),
('LN9002', 'ACC10004', 103, 'AUTO_LOAN', 35000.00, 18500.00, 5.20, 663.85, 60, '2021-05-15', 0);

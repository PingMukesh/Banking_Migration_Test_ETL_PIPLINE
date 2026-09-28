@schema @structure @smoke @regression
Feature: Database Schema & Column Structure Validation
  As an ETL QA Automation Engineer
  I want to verify that all target Data Warehouse tables and mandatory columns exist
  So that data consumers and downstream applications receive standard data structures

  Background:
    Given the ETL migration has completed successfully

  Scenario: Validate all expected target tables exist in Cloud Oracle schema
    When I inspect the target database tables
    Then all tables defined in external schema "expected_schema.json" must exist

  Scenario Outline: Validate dimensional and fact table mandatory column definitions
    When I inspect the target database tables
    Then table "<table_name>" must contain all required columns defined in "expected_schema.json"

    Examples:
      | table_name            |
      | DIM_BRANCH            |
      | DIM_CUSTOMER          |
      | DIM_ACCOUNT           |
      | FACT_TRANSACTIONS     |
      | FACT_LOAN_PORTFOLIO   |
      | DAILY_BALANCE_SUMMARY |
      | ETL_REJECTED_RECORDS  |

  Scenario: Validate mandatory NOT NULL constraints on critical business entities
    Then mandatory columns in "DIM_CUSTOMER" must not have any NULL values: "CUSTOMER_SK, CUSTOMER_ID, FULL_NAME, MASKED_TAX_ID, STATUS, KYC_STATUS"
    And mandatory columns in "DIM_ACCOUNT" must not have any NULL values: "ACCOUNT_SK, ACCOUNT_NUMBER, CUSTOMER_SK, BRANCH_SK, CURRENT_BALANCE"
    And mandatory columns in "FACT_TRANSACTIONS" must not have any NULL values: "TXN_SK, TXN_ID, ACCOUNT_SK, AMOUNT, AML_FLAG"

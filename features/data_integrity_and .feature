@dataintegrity
Feature: Dimensional Foreign Keys

Scenario: Validate Referential Integrity for Dimensional Foreign Keys
    Given target table "DIM_ACCOUNT" is loaded
    And target table "DIM_CUSTOMER" is loaded
    And target table "DIM_BRANCH" is loaded
    Then table "DIM_ACCOUNT" must have at least 230 records
    And table "FACT_TRANSACTIONS" must have at least 1400 records
    And table "FACT_LOAN_PORTFOLIO" must have at least 70 records


Scenario Outline: Validate Natural Key Uniqueness across target warehouse
    Then table "<table_name>" must not contain any duplicate rows by natural key "<natural_key>"

    Examples:
      | table_name | natural_key |
      | DIM_BRANCH | BRANCH_CODE |
      | DIM_CUSTOMER | CUSTOMER_ID |
      | DIM_ACCOUNT | ACCOUNT_NUMBER |
      | FACT_TRANSACTIONS | TXN_ID |
      | FACT_LOAN_PORTFOLIO | LOAN_ID |

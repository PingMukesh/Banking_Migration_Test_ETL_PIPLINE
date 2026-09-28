@quarantine @quality @regression
Feature: Dirty Data Quarantine and Defective Record Isolation
  As an ETL QA Automation Engineer
  I want to verify that malformed and defective records are trapped in the quarantine table
  So that bad data does not contaminate the production data warehouse

  Background:
    Given the ETL migration has completed successfully

  Scenario: Validate Population of Error Quarantine Table
    When I inspect the error quarantine table "ETL_REJECTED_RECORDS"
    Then table "ETL_REJECTED_RECORDS" must have at least 3 records

  Scenario: Validate Defective Email and Corrupt Status Quarantine Routing
    When I inspect the error quarantine table "ETL_REJECTED_RECORDS"
    Then dirty customer records with invalid email formats must be present in quarantine
    And corrupted transaction status records must be present in quarantine

  Scenario: Validate Zero Data Leakage of Quarantined Records into Production
    Then no quarantined record key from "LEGACY_CUSTOMERS" should be present in target table "DIM_CUSTOMER" column "CUSTOMER_ID"
    And no quarantined record key from "LEGACY_TRANSACTIONS" should be present in target table "FACT_TRANSACTIONS" column "TXN_ID"

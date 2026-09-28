@reconciliation @completeness @smoke @regression
Feature: Row Count Reconciliation and Data Completeness
  As an ETL QA Automation Engineer
  I want to reconcile row counts between Source Core Banking and Target Oracle Data Warehouse
  So that zero data loss occurs during migration

  Background:
    Given the ETL migration has completed successfully

  Scenario: Validate 1-to-1 row count match for static master entities
    When I reconcile row counts between source "LEGACY_BRANCHES" and target "DIM_BRANCH"
    Then the row counts must match exactly

  Scenario: Validate 1-to-1 row count match for clean credit loan portfolio
    When I reconcile row counts between source "LEGACY_LOANS" and target "FACT_LOAN_PORTFOLIO"
    Then the row counts must match exactly

  Scenario: Validate the fundamental Customer Data Completeness Equation
    When I evaluate the customer reconciliation equation
    Then source customer rows must equal target DIM_CUSTOMER rows plus quarantined rows

  Scenario: Validate the Financial Transactions Reconciliation Equation
    When I evaluate the transaction reconciliation equation
    Then source transaction rows must equal target FACT_TRANSACTIONS rows plus quarantined rows plus orphan rows

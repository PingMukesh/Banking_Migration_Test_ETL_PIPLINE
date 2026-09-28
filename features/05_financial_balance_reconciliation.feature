@financial @reconciliation @smoke @regression
Feature: Financial Ledger and Account Balance Reconciliation
  As a Financial Data QA Automation Engineer
  I want to verify that daily transaction rollups and account balances reconcile arithmetically
  So that financial books balance perfectly to the cent

  Background:
    Given the ETL migration has completed successfully

  Scenario: Validate Daily Account Balance Rollup Arithmetic Formula
    When I verify the arithmetic balance rollup in "DAILY_BALANCE_SUMMARY"
    Then the equation OPENING_BALANCE + CREDIT - DEBIT = CLOSING_BALANCE must hold true for all accounts

  Scenario: Validate Overall Financial Transaction Volume Parity
    When I reconcile total transaction financial volume between source and target
    Then the difference between source and target transaction volumes must be within tolerance 0.05

  Scenario: Validate Total Debit and Total Credit Financial Totals
    When I reconcile total debit and credit amounts individually
    Then source total debits must match target total debits within tolerance 0.05
    And source total credits must match target total credits within tolerance 0.05

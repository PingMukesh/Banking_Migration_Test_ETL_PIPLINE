@transformation @pii @data_driven @smoke @regression
Feature: Business Transformations, PII Masking, and Code Mapping
  As an ETL QA Automation Engineer
  I want to validate that PII data is masked and legacy codes are translated using external business rules
  So that Cloud Target complies with regulatory compliance, GDPR, and banking standards

  Background:
    Given the ETL migration has completed successfully

  Scenario: Validate PII Masking compliance on Customer Tax ID / SSN
    Then all records in "DIM_CUSTOMER" column "MASKED_TAX_ID" must match pattern "^\*\*\*-\*\*-\d{4}$"
    And no raw unmasked Tax IDs or SSNs should exist in "DIM_CUSTOMER"

  Scenario: Validate Customer Status translation against external Excel rules
    Given external mapping rules are loaded from Excel "test_mapping_rules.xlsx" sheet "StatusMapping"
    Then all legacy customer statuses must match expected target statuses from Excel

  Scenario: Validate Account Type standardization against external Excel rules
    Given external mapping rules are loaded from Excel "test_mapping_rules.xlsx" sheet "AccountTypeMapping"
    Then all legacy account types must match expected target types from Excel

  Scenario: Validate Loan Delinquency classification against external Excel rules
    Given external mapping rules are loaded from Excel "test_mapping_rules.xlsx" sheet "DelinquencyMapping"
    Then all legacy loan delinquency buckets must match expected target statuses from Excel

  Scenario: Validate Anti-Money Laundering (AML) high-value transaction regulatory flagging
    Then all transactions with amount greater than or equal to 10000.00 must have AML_FLAG set to "Y"
    And no transaction with amount less than 10000.00 should have AML_FLAG set to "Y"

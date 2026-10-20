@Financial
Feature: Financial ledger and Account Balance Validation

    Background:
        Given ETL Migration has completed
    @Arithmetic
    Scenario: Validate Daily Account Balance by usimg arithmetic formula
        When I Verify the arithmetic Balance in "DAILY_BALANCE_SUMMARY"
        Then the formula opening_balance + credit - debit = Closing_balance must true for all Accounts
    
    
    Scenario: Validate Overall Financial Transaction Volume Parity
        When I reconcile total transaction financial volume between source and target
        Then the difference between source and target transaction volumes must be within tolerance 0.05

    Scenario: Validate Total Debit and Total Credit Financial Totals
        When I reconcile total debit and credit amounts individually
        Then source total debits must match target total debits within tolerance 0.05
        Then source total credits must match target total credits within tolerance 0.05


    
    @AMLFLAG
    Scenario: Validate Anti Money Laundering (AML) high value transaction regulatory flagging
        When I check for AML flagged transactions in "FACT_TRANSACTIONS"
        Then all transactions with amount greater than 10000 must be flagged as AML
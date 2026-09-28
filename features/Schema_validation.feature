@Schema
Feature: DB Schema & Column Structure Validation

    Background:
        Given ETL Migration has completed


    Scenario: Validate all tgt tables are exist in Oracle DB.

        When inspect the tgt DB tables
        Then all tables defined in the external Schema "Input" must exist

    Scenario Outline: Validate of dimensional and fact tables with mandatory column definitions

        When inspect the tgt DB tables
        Then table "<table_name>" must contain all required columns defined in "Input".

        Examples:
            |   table_name              |
            |   DIM_BRANCH              |
            |   DIM_CUSTOMER            |
            |   DIM_ACCOUNT             |
            |   FACT_LOAN_PORTFOLIO     |
            |   FACT_TRANSACTIONS       |
            |   DAILY_BALANCE_SUMMARY   |
            |   ETL_REJECTED_RECORDS    |
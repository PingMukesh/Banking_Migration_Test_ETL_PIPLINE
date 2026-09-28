@kafka @streaming @realtime @regression
Feature: Real-Time Event Streaming Validation via Apache Kafka
  As a Real-Time Streaming QA Engineer
  I want to publish transaction events to an Apache Kafka topic and verify real-time ingestion into Oracle
  So that latency, data integrity, and AML compliance are validated end-to-end

  Background:
    Given the ETL migration has completed successfully
    And Apache Kafka streaming topic "banking-transactions" is configured

  Scenario: Stream High-Value Financial Transaction to Kafka and Validate Oracle Target Ingestion
    When I simulate streaming a real-time transaction event to Kafka topic "banking-transactions":
      | TXN_ID          | ACCT_NO    | AMOUNT   | TXN_TYPE | CHANNEL |
      | TXN-KAFKA-LIVE1 | ACT-100001 | 18500.00 | DR       | UPI     |
    Then the streaming transaction should land in Oracle "FACT_TRANSACTIONS" within 5 seconds
    And the real-time record in Oracle must have "AML_FLAG" set to "Y"
    And the real-time record in Oracle must have "TXN_STATUS" set to "SUCCESS"

  Scenario: Stream Standard Low-Value Transaction and Verify Negative AML Flag
    When I simulate streaming a real-time transaction event to Kafka topic "banking-transactions":
      | TXN_ID          | ACCT_NO    | AMOUNT | TXN_TYPE | CHANNEL |
      | TXN-KAFKA-LIVE2 | ACT-100002 | 450.00 | CR       | POS     |
    Then the streaming transaction should land in Oracle "FACT_TRANSACTIONS" within 5 seconds
    And the real-time record in Oracle must have "AML_FLAG" set to "N"

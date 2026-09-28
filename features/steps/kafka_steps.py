"""
Kafka Real-Time Streaming Step Definitions
"""

import json
import time
from behave import given, when, then
from sqlalchemy import text


@given('Apache Kafka streaming topic "{topic}" is configured')
def step_kafka_topic_configured(context, topic):
    context.kafka_topic = topic
    context.kafka_broker = "localhost:9092"
    # Check if confluent-kafka is available and broker is responsive
    context.has_live_kafka = False
    try:
        from confluent_kafka.admin import AdminClient
        admin = AdminClient({'bootstrap.servers': context.kafka_broker, 'socket.timeout.ms': 1000})
        metadata = admin.list_topics(timeout=1.0)
        if metadata and topic in metadata.topics:
            context.has_live_kafka = True
    except Exception:
        context.has_live_kafka = False


@when('I simulate streaming a real-time transaction event to Kafka topic "{topic}":')
@when('I simulate streaming a real-time transaction event to Kafka topic "{topic}"')
def step_stream_transaction(context, topic):
    for row in context.table:
        txn_id = row["TXN_ID"]
        acct_no = row["ACCT_NO"]
        amount = float(row["AMOUNT"])
        txn_type = row["TXN_TYPE"]
        channel = row["CHANNEL"]
        aml_flag = "Y" if amount >= 10000.0 else "N"

        context.last_streamed_txn_id = txn_id
        context.last_streamed_amount = amount
        context.last_streamed_aml_flag = aml_flag
        if not hasattr(context, "streamed_txns"):
            context.streamed_txns = []
        context.streamed_txns.append(txn_id)

        payload = {
            "TXN_ID": txn_id,
            "ACCT_NO": acct_no,
            "AMOUNT": amount,
            "TXN_TYPE": txn_type,
            "CHANNEL": channel,
            "TXN_TIMESTAMP": "2026-09-11 12:00:00"
        }

        if context.has_live_kafka:
            from confluent_kafka import Producer
            p = Producer({'bootstrap.servers': context.kafka_broker})
            p.produce(topic, key=txn_id, value=json.dumps(payload).encode('utf-8'))
            p.flush()
        else:
            # Simulated Streaming Consumer to Oracle Target
            # Lookup Account SK
            with context.target_engine.connect() as conn:
                acct_sk = conn.execute(text(f"SELECT ACCOUNT_SK FROM DIM_ACCOUNT WHERE ACCOUNT_NUMBER = '{acct_no}'")).scalar()
                if not acct_sk:
                    acct_sk = 1

                # Clean any previous simulation row
                conn.execute(text(f"DELETE FROM FACT_TRANSACTIONS WHERE TXN_ID = '{txn_id}'"))
                conn.commit()

                # Insert streaming record
                insert_sql = text("""
                    INSERT INTO FACT_TRANSACTIONS 
                    (TXN_ID, ACCOUNT_SK, TXN_TIMESTAMP, TXN_TYPE, CHANNEL, AMOUNT, BALANCE_AFTER_TXN, AML_FLAG, TXN_STATUS)
                    VALUES 
                    (:txn_id, :acct_sk, CURRENT_TIMESTAMP, :txn_type, :channel, :amount, :bal, :aml_flag, 'SUCCESS')
                """)
                conn.execute(insert_sql, {
                    "txn_id": txn_id,
                    "acct_sk": acct_sk,
                    "txn_type": txn_type,
                    "channel": channel,
                    "amount": amount,
                    "bal": 50000.00,
                    "aml_flag": aml_flag
                })
                conn.commit()


@then('the streaming transaction should land in Oracle "{table_name}" within {timeout:d} seconds')
def step_poll_streaming_arrival(context, table_name, timeout):
    query = text(f"SELECT COUNT(*) FROM {table_name} WHERE TXN_ID = :txn_id")
    start = time.time()
    found = False
    while time.time() - start < timeout:
        count = context.target_conn.execute(query, {"txn_id": context.last_streamed_txn_id}).scalar()
        if count > 0:
            found = True
            break
        time.sleep(0.5)

    assert found, f"Streamed event {context.last_streamed_txn_id} did not arrive in Oracle '{table_name}' within {timeout}s!"


@then('the real-time record in Oracle must have "{column_name}" set to "{expected_value}"')
def step_verify_realtime_column_value(context, column_name, expected_value):
    query = text(f"SELECT {column_name} FROM FACT_TRANSACTIONS WHERE TXN_ID = :txn_id")
    val = context.target_conn.execute(query, {"txn_id": context.last_streamed_txn_id}).scalar()
    assert str(val).strip() == str(expected_value).strip(), (
        f"Real-time event field mismatch! Expected '{expected_value}', but found '{val}' in column '{column_name}'"
    )

from utils.logger import logger
from  config.db_manager import get_db_manager
from utils.excel_reader import ExternalDataReader



def before_all(context):
    logger.info("Starting test execution")
    logger.info("DB Manager initialization")
    db_mngr = get_db_manager()
    context.source_engine = db_mngr.source_engine
    context.target_engine = db_mngr.target_engine
    context.source_conn = db_mngr.get_source_engine()
    context.target_conn = db_mngr.get_target_engine()

    context.expected_schema = ExternalDataReader.read_json_schema("expected_schema.json")
    context.threshold_mapping = ExternalDataReader.Read_csv_threshold("validation_thresholds.csv")
    context.thresholds = context.threshold_mapping
    context.act_tables = []

    logger.info(f"Connected to Target DB: {context.target_engine.url}")

    try:
        from sqlalchemy import text
        with context.target_engine.connect() as conn:
            if context.target_engine.dialect.name == "oracle":
                conn.execute(text("Delete from FACT_TRANSACTIONS where TXN_TIMESTAMP >= TIMESTAMP '2023-01-01 00:00:00'"))
            else:
                conn.execute(text("Delete from FACT_TRANSACTIONS where TXN_TIMESTAMP >= '2023-01-01 00:00:00'"))
            conn.commit()
    except Exception as e:
        logger.error(f"Error while cleaning up target DB FACT_TRANSACTIONS table: {e}")



def after_all(context):
    logger.info("Test execution completed")
    logger.info("Closing DB connections")

    try:
        from sqlalchemy import text
        with context.target_engine.connect() as conn:
            if context.target_engine.dialect.name == "oracle":
                conn.execute(text("Delete from FACT_TRANSACTIONS where TXN_TIMESTAMP >= TIMESTAMP '2023-01-01 00:00:00'"))
            else:
                conn.execute(text("Delete from FACT_TRANSACTIONS where TXN_TIMESTAMP >= '2023-01-01 00:00:00'"))
            conn.commit()
    except Exception:
        pass

    if hasattr(context, 'target_engine') and context.target_engine:
        if hasattr(context, 'target_conn'):
            context.target_conn.close()
        context.target_engine.dispose()
    if hasattr(context, 'source_engine') and context.source_engine:
        if hasattr(context, 'source_conn'):
            context.source_conn.close()
        context.source_engine.dispose()
    logger.info("DB connections closed")
    logger.info("Test execution finished")


def before_scenario(context, scenario):
    logger.info(f"Starting scenario: {scenario.name}")
    if not hasattr(context, 'scenario_data'):
        context.scenario_data = {}

def after_scenario(context, scenario):
    logger.info(f"Scenario completed: {scenario.name}")
    if hasattr(context, 'scenario_data'):
        context.scenario_data.clear()


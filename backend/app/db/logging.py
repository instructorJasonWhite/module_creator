import logging

from sqlalchemy import event
from sqlalchemy.engine import Engine

# Configure SQLAlchemy logging
logging.basicConfig()
logger = logging.getLogger("sqlalchemy.engine")
logger.setLevel(logging.INFO)


# Log all SQL statements
@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(session, cursor, statement, parameters, context, executemany):
    logger.info("Executing SQL: %s", statement)
    logger.info("Parameters: %s", parameters)


# Log transaction commits and rollbacks
@event.listens_for(Engine, "commit")
def receive_commit(session):
    logger.info("Transaction committed")


@event.listens_for(Engine, "rollback")
def receive_rollback(session):
    logger.info("Transaction rolled back")

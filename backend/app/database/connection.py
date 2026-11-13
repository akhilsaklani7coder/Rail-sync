import mysql.connector
from mysql.connector import pooling, Error
from contextlib import contextmanager
from app.config import Config
import logging

logger = logging.getLogger(__name__)

# Initialize connection pool
_pool = None

def init_connection_pool():
    global _pool
    if _pool is None:
        try:
            _pool = pooling.MySQLConnectionPool(
                pool_name="railsync_pool",
                pool_size=10,
                pool_reset_session=True,
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                autocommit=True
            )
            logger.info("MySQL Connection Pool successfully initialized.")
        except Error as err:
            logger.error(f"Error initializing MySQL Connection Pool: {err}")
            _pool = None

def get_raw_connection():
    """Acquires a single connection directly (fallback if pool is full or uninitialized)."""
    return mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        autocommit=True
    )

@contextmanager
def get_db_connection(dictionary=True):
    """
    Context manager for standard read-only or auto-commit operations.
    Safely acquires and releases the connection back to the pool.
    """
    conn = None
    cursor = None
    try:
        if _pool is not None:
            conn = _pool.get_connection()
        else:
            conn = get_raw_connection()
            
        cursor = conn.cursor(dictionary=dictionary)
        yield conn, cursor
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

@contextmanager
def get_db_transaction(dictionary=True):
    """
    Context manager for strict ACID transactions.
    Disables autocommit, starts an explicit InnoDB transaction,
    commits on success, and guarantees rollback on any Exception.
    """
    conn = None
    cursor = None
    committed = False
    try:
        if _pool is not None:
            conn = _pool.get_connection()
        else:
            conn = get_raw_connection()
            
        conn.autocommit = False
        conn.start_transaction()
        cursor = conn.cursor(dictionary=dictionary)
        yield conn, cursor
        conn.commit()
        committed = True
    except Exception as e:
        if conn is not None:
            try:
                conn.rollback()
                logger.warning(f"Transaction rolled back due to error: {e}")
            except Error as rb_err:
                logger.error(f"Failed to rollback transaction: {rb_err}")
        raise e
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            if not committed:
                try:
                    conn.rollback()
                except Exception:
                    pass
            try:
                conn.autocommit = True
            except Exception:
                pass
            conn.close()


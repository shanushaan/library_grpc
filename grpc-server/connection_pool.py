import psycopg2
from psycopg2 import pool
import logging
from contextlib import contextmanager
import os

logger = logging.getLogger(__name__)

class DatabasePool:
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize_pool(self):
        """Initialize connection pool"""
        try:
            self._pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=2,
                maxconn=20,
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'library_db'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'mypassword')
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool with context manager"""
        connection = None
        try:
            connection = self._pool.getconn()
            yield connection
        except psycopg2.DatabaseError as e:
            if connection:
                connection.rollback()
            logger.error(f"Database error: {e}")
            raise
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Unexpected error: {e}")
            raise
        finally:
            if connection:
                self._pool.putconn(connection)
    
    def close_pool(self):
        """Close all connections in pool"""
        if self._pool:
            self._pool.closeall()
            logger.info("Database connection pool closed")

# Global pool instance
db_pool = DatabasePool()
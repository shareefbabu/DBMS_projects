"""
Database Connection Pool Manager
==================================
Implements connection pooling for optimized database access
with health checks, retry logic, and thread-safe operations
"""

import mysql.connector
from mysql.connector import pooling, Error
import time
import logging
from typing import Optional, Tuple, Any, List
from contextlib import contextmanager
from config import Config

# Setup logging
logger = logging.getLogger(__name__)


class DatabasePoolError(Exception):
    """Custom exception for database pool errors"""
    pass


class DatabasePool:
    """
    Database connection pool manager with advanced features
    """
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        """Singleton pattern to ensure single pool instance"""
        if cls._instance is None:
            cls._instance = super(DatabasePool, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize connection pool if not already initialized"""
        if self._pool is None:
            self._initialize_pool()
    
    def _initialize_pool(self):
        """Create and configure the connection pool"""
        try:
            logger.info(f"Initializing database connection pool: {Config.DB_POOL_NAME}")
            
            pool_config = {
                'pool_name': Config.DB_POOL_NAME,
                'pool_size': Config.DB_POOL_SIZE,
                'pool_reset_session': Config.DB_POOL_RESET_SESSION,
                'host': Config.DB_HOST,
                'port': Config.DB_PORT,
                'database': Config.DB_NAME,
                'user': Config.DB_USER,
                'password': Config.DB_PASSWORD,
                'autocommit': False,  # Explicit transaction control
                'connect_timeout': Config.DB_CONNECTION_TIMEOUT,
            }
            
            self._pool = pooling.MySQLConnectionPool(**pool_config)
            
            logger.info(f"[+] Connection pool created successfully")
            logger.info(f"    Pool Size: {Config.DB_POOL_SIZE}")
            logger.info(f"    Database: {Config.DB_NAME}@{Config.DB_HOST}")
            
            # Perform initial health check
            if self.health_check():
                logger.info("[+] Initial health check passed")
            else:
                logger.warning("[-] Initial health check failed")
            
        except Error as e:
            logger.error(f"Failed to create connection pool: {e}")
            raise DatabasePoolError(f"Pool initialization failed: {e}")
    
    @contextmanager
    def get_connection(self):
        """
        Get a connection from the pool (context manager)
        
        Usage:
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ...")
        
        Yields:
            MySQL connection from pool
        """
        connection = None
        try:
            connection = self._pool.get_connection()
            logger.debug("Connection acquired from pool")
            yield connection
        except Error as e:
            logger.error(f"Error getting connection: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
                logger.debug("Connection returned to pool")
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[Tuple] = None,
        fetch_one: bool = False,
        fetch_all: bool = True
    ) -> Tuple[bool, Any]:
        """
        Execute a query with automatic connection management
        
        Args:
            query: SQL query string
            params: Query parameters (for prepared statements)
            fetch_one: If True, fetch single result
            fetch_all: If True, fetch all results (default)
        
        Returns:
            Tuple of (success, result/error)
        """
        retry_count = 0
        last_error = None
        
        while retry_count < Config.MAX_RETRIES:
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor(dictionary=True)
                    
                    # Execute query
                    cursor.execute(query, params or ())
                    
                    # Handle SELECT queries
                    if query.strip().upper().startswith('SELECT'):
                        if fetch_one:
                            result = cursor.fetchone()
                        elif fetch_all:
                            result = cursor.fetchall()
                        else:
                            result = None
                        
                        cursor.close()
                        return True, result
                    
                    # Handle INSERT/UPDATE/DELETE queries
                    else:
                        conn.commit()
                        affected_rows = cursor.rowcount
                        last_id = cursor.lastrowid
                        cursor.close()
                        
                        return True, {
                            'affected_rows': affected_rows,
                            'last_insert_id': last_id
                        }
            
            except Error as e:
                last_error = e
                retry_count += 1
                logger.warning(f"Query failed (attempt {retry_count}/{Config.MAX_RETRIES}): {e}")
                
                if retry_count < Config.MAX_RETRIES:
                    time.sleep(Config.RETRY_DELAY * retry_count)  # Exponential backoff
        
        logger.error(f"Query failed after {Config.MAX_RETRIES} retries: {last_error}")
        return False, str(last_error)
    
    def execute_transaction(self, queries: List[Tuple[str, Optional[Tuple]]]) -> Tuple[bool, Any]:
        """
        Execute multiple queries in a single transaction
        
        Args:
            queries: List of (query, params) tuples
        
        Returns:
            Tuple of (success, result/error)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                results = []
                
                for query, params in queries:
                    cursor.execute(query, params or ())
                    
                    if query.strip().upper().startswith('SELECT'):
                        results.append(cursor.fetchall())
                    else:
                        results.append({
                            'affected_rows': cursor.rowcount,
                            'last_insert_id': cursor.lastrowid
                        })
                
                conn.commit()
                cursor.close()
                
                logger.info(f"[+] Transaction completed: {len(queries)} queries executed")
                return True, results
                
        except Error as e:
            logger.error(f"Transaction failed: {e}")
            if conn:
                conn.rollback()
                logger.info("Transaction rolled back")
            return False, str(e)
    
    def execute_batch(
        self, 
        query: str, 
        params_list: List[Tuple],
        batch_size: int = None
    ) -> Tuple[bool, Any]:
        """
        Execute batch insert/update operations
        
        Args:
            query: SQL query with placeholders
            params_list: List of parameter tuples
            batch_size: Number of records per batch (default: Config.BATCH_SIZE)
        
        Returns:
            Tuple of (success, affected_rows/error)
        """
        batch_size = batch_size or Config.BATCH_SIZE
        total_affected = 0
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Process in batches
                for i in range(0, len(params_list), batch_size):
                    batch = params_list[i:i + batch_size]
                    cursor.executemany(query, batch)
                    total_affected += cursor.rowcount
                    
                    logger.info(f"  Batch {i//batch_size + 1}: {len(batch)} records processed")
                
                conn.commit()
                cursor.close()
                
                logger.info(f"[+] Batch operation completed: {total_affected} records affected")
                return True, {'affected_rows': total_affected}
                
        except Error as e:
            logger.error(f"Batch operation failed: {e}")
            if conn:
                conn.rollback()
            return False, str(e)
    
    def health_check(self) -> bool:
        """
        Perform health check on the connection pool
        
        Returns:
            True if pool is healthy, False otherwise
        """
        try:
            query = "SELECT 1 as health_check"
            success, result = self.execute_query(query, fetch_one=True)
            
            if success and result and result.get('health_check') == 1:
                logger.debug("Health check passed")
                return True
            else:
                logger.warning("Health check failed")
                return False
                
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return False
    
    def get_pool_stats(self) -> dict:
        """
        Get statistics about the connection pool
        
        Returns:
            Dictionary with pool statistics
        """
        try:
            # This is a simplified version - actual implementation
            # would track more detailed metrics
            return {
                'pool_name': Config.DB_POOL_NAME,
                'pool_size': Config.DB_POOL_SIZE,
                'database': Config.DB_NAME,
                'host': Config.DB_HOST,
                'healthy': self.health_check()
            }
        except Exception as e:
            logger.error(f"Error getting pool stats: {e}")
            return {}
    
    def close_pool(self):
        """Close all connections in the pool"""
        try:
            if self._pool:
                # Note: mysql.connector.pooling doesn't have a direct close_all method
                # Connections will be closed when the pool is garbage collected
                logger.info("Connection pool will be closed on program exit")
                self._pool = None
        except Exception as e:
            logger.error(f"Error closing pool: {e}")


# Global pool instance
pool = DatabasePool()


def main():
    """Test database connection pool"""
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format=Config.LOG_FORMAT
    )
    
    try:
        print("\n" + "="*60)
        print("DATABASE CONNECTION POOL TEST")
        print("="*60)
        
        # Test health check
        print("\n1. Health Check:")
        if pool.health_check():
            print("   [+] Pool is healthy")
        else:
            print("   [-] Pool health check failed")
            return 1
        
        # Test simple query
        print("\n2. Simple Query Test:")
        query = "SELECT COUNT(*) as user_count FROM Users"
        success, result = pool.execute_query(query, fetch_one=True)
        if success:
            print(f"   [+] Users in database: {result.get('user_count', 0)}")
        else:
            print(f"   [-] Query failed: {result}")
        
        # Test connection acquisition
        print("\n3. Connection Management Test:")
        with pool.get_connection() as conn:
            print(f"   [+] Connection acquired: {conn.is_connected()}")
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]
            print(f"   [+] Connected to database: {db_name}")
            cursor.close()
        print("   [+] Connection returned to pool")
        
        # Show pool stats
        print("\n4. Pool Statistics:")
        stats = pool.get_pool_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n" + "="*60)
        print("[+] All tests passed!")
        print("="*60 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n[-] Test failed: {e}")
        logger.error(f"Test failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

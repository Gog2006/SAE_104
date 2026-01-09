import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Database:
    """Database connection and operations handler for vehicle registration system"""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'carte_grise_db')
        self.port = int(os.getenv('DB_PORT', '3306'))
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                use_pure=True,  # Use pure Python implementation to avoid C extension issues
                autocommit=False,  # Explicitly disable autocommit
                connection_timeout=30,
                get_warnings=False,
                raise_on_warnings=False
            )
            # Set session variables to handle timeouts better
            if self.connection.is_connected():
                cursor = self.connection.cursor()
                cursor.execute("SET SESSION wait_timeout=28800")  # 8 hours
                cursor.execute("SET SESSION interactive_timeout=28800")
                cursor.close()
                logger.info("Successfully connected to MySQL database")
                return True
        except Error as e:
            logger.error(f"Error connecting to MySQL database: {e}")
            return False
    
    def _ensure_connection(self):
        """Ensure database connection is alive, reconnect if needed"""
        try:
            if not self.connection:
                logger.info("No connection object, connecting...")
                return self.connect()
            
            # Test if connection is alive by checking if it's connected
            if not self.connection.is_connected():
                logger.info("Connection lost, attempting to reconnect...")
                self.disconnect()
                self.connection = None
                return self.connect()
            
            # Additional health check - ping the server
            try:
                self.connection.ping(reconnect=True, attempts=3, delay=1)
            except Error as e:
                logger.warning(f"Ping failed: {e}, reconnecting...")
                self.disconnect()
                self.connection = None
                return self.connect()
            
            return True
        except Error as e:
            logger.error(f"Error ensuring connection: {e}")
            self.connection = None
            return self.connect()
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL connection closed")
    
    def execute_query(self, query, params=None):
        """Execute a query that modifies data (INSERT, UPDATE, DELETE)"""
        self._ensure_connection()
        cursor = None
        try:
            cursor = self.connection.cursor(buffered=False)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            last_id = cursor.lastrowid
            return last_id if last_id else True
        except Error as e:
            logger.error(f"Error executing query: {e}")
            try:
                self.connection.rollback()
            except Error as rollback_error:
                logger.error(f"Error rolling back transaction: {rollback_error}")
                # Force reconnect if rollback fails
                try:
                    self.disconnect()
                except:
                    pass
                self.connection = None
            return False
        finally:
            if cursor:
                try:
                    cursor.close()
                except Error as e:
                    logger.error(f"Error closing cursor: {e}")
    
    def fetch_all(self, query, params=None):
        """Execute a SELECT query and return all results"""
        self._ensure_connection()
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True, buffered=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            logger.error(f"Error fetching data: {e}")
            # Force reconnect on critical errors
            try:
                self.disconnect()
            except:
                pass
            self.connection = None
            return []
        finally:
            if cursor:
                try:
                    cursor.close()
                except Error as e:
                    logger.error(f"Error closing cursor: {e}")
    
    def fetch_one(self, query, params=None):
        """Execute a SELECT query and return one result"""
        self._ensure_connection()
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True, buffered=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchone()
            return result
        except Error as e:
            logger.error(f"Error fetching data: {e}")
            # Force reconnect on critical errors
            try:
                self.disconnect()
            except:
                pass
            self.connection = None
            return None
        finally:
            if cursor:
                try:
                    cursor.close()
                except Error as e:
                    logger.error(f"Error closing cursor: {e}")

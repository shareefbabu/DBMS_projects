"""
Configuration Management for User CSV Integration
==================================================
Centralized configuration using environment variables for security
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for user CSV integration system"""
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', '3306'))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD')  # REQUIRED: No default for security
    DB_NAME = os.getenv('DB_NAME', 'FlightBookingDB')
    
    # Connection Pool Configuration
    DB_POOL_NAME = 'skybook_user_pool'
    DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '10'))
    DB_POOL_MIN_SIZE = int(os.getenv('DB_POOL_MIN_SIZE', '5'))
    DB_POOL_MAX_SIZE = int(os.getenv('DB_POOL_MAX_SIZE', '20'))
    DB_POOL_RESET_SESSION = True
    DB_CONNECTION_TIMEOUT = int(os.getenv('DB_CONNECTION_TIMEOUT', '30'))
    
    # File Paths (Define BASE_DIR first)
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / 'data'
    LOG_DIR = BASE_DIR / 'logs'
    BACKUP_DIR = DATA_DIR / 'backup'
    REPORTS_DIR = DATA_DIR / 'reports'
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = LOG_DIR / 'user_integration.log'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
    LOG_BACKUP_COUNT = 5
    
    # Security Configuration
    PASSWORD_HASH_ROUNDS = 12  # bcrypt rounds
    DEFAULT_PASSWORD_HASH = 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'  # SHA256 of 'password123'
    
    # Email Configuration (for password reset)
    SMTP_ENABLED = os.getenv('SMTP_ENABLED', 'false').lower() == 'true'
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
    EMAIL_FROM = os.getenv('EMAIL_FROM', 'noreply@skybook.com')
    EMAIL_FROM_NAME = os.getenv('EMAIL_FROM_NAME', 'SkyBook Support')
    
    # Password Reset Configuration
    PASSWORD_RESET_TOKEN_EXPIRY = int(os.getenv('RESET_TOKEN_EXPIRY', '3600'))  # 1 hour in seconds
    PASSWORD_RESET_RATE_LIMIT = int(os.getenv('RESET_RATE_LIMIT', '3'))  # Max requests per hour
    PASSWORD_RESET_RATE_WINDOW = int(os.getenv('RESET_RATE_WINDOW', '3600'))  # Time window in seconds
    
    # Validation Rules
    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PHONE_REGEX = r'^\+?1?\d{9,15}$'
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 100
    
    # Processing Configuration
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', '100'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', '2'))  # seconds
    
    # Cleanup Configuration
    REQUIRE_CONFIRMATION = os.getenv('REQUIRE_CONFIRMATION', 'true').lower() == 'true'
    CREATE_BACKUP_BEFORE_DELETE = os.getenv('CREATE_BACKUP', 'true').lower() == 'true'
    DEFAULT_RETENTION_DAYS = int(os.getenv('RETENTION_DAYS', '30'))
    
    @classmethod
    def create_directories(cls):
        """
        Create necessary directories if they don't exist.
        
        Creates DATA_DIR, LOG_DIR, BACKUP_DIR, and REPORTS_DIR with parent directories.
        """
        for directory in [cls.DATA_DIR, cls.LOG_DIR, cls.BACKUP_DIR, cls.REPORTS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_config(cls):
        """
        Validate configuration settings.
        
        Raises:
            ValueError: If any configuration is invalid
            
        Returns:
            bool: True if all validations pass
        """
        errors = []
        
        # Check required database settings
        if not cls.DB_PASSWORD:
            errors.append("DB_PASSWORD environment variable is required (set in .env file)")
        
        # Check pool size constraints
        if cls.DB_POOL_SIZE < cls.DB_POOL_MIN_SIZE:
            errors.append(f"DB_POOL_SIZE ({cls.DB_POOL_SIZE}) must be >= DB_POOL_MIN_SIZE ({cls.DB_POOL_MIN_SIZE})")
        
        if cls.DB_POOL_SIZE > cls.DB_POOL_MAX_SIZE:
            errors.append(f"DB_POOL_SIZE ({cls.DB_POOL_SIZE}) must be <= DB_POOL_MAX_SIZE ({cls.DB_POOL_MAX_SIZE})")
        
        # Validate SMTP configuration if enabled
        if cls.SMTP_ENABLED:
            if not cls.SMTP_USERNAME or not cls.SMTP_PASSWORD:
                errors.append("SMTP_USERNAME and SMTP_PASSWORD required when SMTP_ENABLED=true")
            if not cls.EMAIL_FROM:
                errors.append("EMAIL_FROM required when SMTP_ENABLED=true")
        
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
        
        return True
    
    @classmethod
    def get_db_config(cls):
        """
        Get database configuration as dictionary.
        
        Returns:
            dict: Database configuration parameters for mysql.connector.pooling
        """
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'database': cls.DB_NAME,
            'pool_name': cls.DB_POOL_NAME,
            'pool_size': cls.DB_POOL_SIZE,
            'pool_reset_session': cls.DB_POOL_RESET_SESSION,
        }
    
    @classmethod
    def display_config(cls, hide_sensitive=True):
        """
        Display current configuration for debugging purposes.
        
        Args:
            hide_sensitive (bool): If True, mask sensitive values like passwords
            
        Returns:
            dict: Configuration information organized by category
        """
        config_info = {
            'Database': {
                'Host': cls.DB_HOST,
                'Port': cls.DB_PORT,
                'User': cls.DB_USER,
                'Password': '***' if hide_sensitive else cls.DB_PASSWORD,
                'Database': cls.DB_NAME,
            },
            'Connection Pool': {
                'Pool Size': cls.DB_POOL_SIZE,
                'Min Size': cls.DB_POOL_MIN_SIZE,
                'Max Size': cls.DB_POOL_MAX_SIZE,
            },
            'Logging': {
                'Level': cls.LOG_LEVEL,
                'File': str(cls.LOG_FILE),
            },
            'Security': {
                'Require Confirmation': cls.REQUIRE_CONFIRMATION,
                'Create Backups': cls.CREATE_BACKUP_BEFORE_DELETE,
            }
        }
        return config_info


# Initialize directories on import
Config.create_directories()

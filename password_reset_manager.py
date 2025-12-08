"""
Password Reset Manager
======================
Handles password reset token generation, validation, and email verification
"""

import secrets
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict
from db_connection_pool import pool

logger = logging.getLogger(__name__)


class PasswordResetManager:
    """Manager for password reset operations"""
    
    def __init__(self):
        """Initialize password reset manager"""
        self.pool = pool
        self.token_expiry_hours = 1  # Tokens valid for 1 hour
        logger.info("PasswordResetManager initialized")
    
    def verify_email_exists(self, email: str) -> Tuple[bool, Optional[int]]:
        """
        Verify email exists in Users table
        
        Args:
            email: Email address to verify
        
        Returns:
            Tuple of (exists, user_id or None)
        """
        try:
            query = "SELECT user_id FROM Users WHERE email = %s LIMIT 1"
            success, result = self.pool.execute_query(
                query, 
                (email.strip().lower(),),
                fetch_one=True
            )
            
            if success and result:
                user_id = result.get('user_id')
                logger.info(f"[+] Email verified: {email}")
                return True, user_id
            else:
                logger.warning(f"[-] Email not found: {email}")
                return False, None
                
        except Exception as e:
            logger.error(f"Error verifying email: {e}")
            return False, None
    
    def generate_reset_token(self, email: str, user_id: int) -> Optional[str]:
        """
        Generate secure reset token and store in database
        
        Args:
            email: User's email address
            user_id: User's ID
        
        Returns:
            Reset token string or None if failed
        """
        try:
            # Generate secure random token
            random_string = secrets.token_urlsafe(32)
            timestamp = str(datetime.now().timestamp())
            combined = f"{email}{random_string}{timestamp}"
            reset_token = hashlib.sha256(combined.encode()).hexdigest()
            
            # Calculate expiry time
            expires_at = datetime.now() + timedelta(hours=self.token_expiry_hours)
            
            # Store token in database
            query = """
            INSERT INTO password_reset_tokens 
            (user_id, email, reset_token, expires_at)
            VALUES (%s, %s, %s, %s)
            """
            
            success, result = self.pool.execute_query(
                query,
                (user_id, email.strip().lower(), reset_token, expires_at)
            )
            
            if success:
                logger.info(f"[+] Reset token generated for {email}")
                return reset_token
            else:
                logger.error(f"[-] Failed to store reset token: {result}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating reset token: {e}")
            return None
    
    def validate_reset_token(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """
        Validate reset token
        
        Args:
            token: Reset token to validate
        
        Returns:
            Tuple of (is_valid, token_data or None)
        """
        try:
            query = """
            SELECT token_id, user_id, email, expires_at, is_used
            FROM password_reset_tokens
            WHERE reset_token = %s
            LIMIT 1
            """
            
            success, result = self.pool.execute_query(
                query,
                (token,),
                fetch_one=True
            )
            
            if not success or not result:
                logger.warning("[-] Token not found")
                return False, None
            
            # Check if already used
            if result.get('is_used'):
                logger.warning("[-] Token already used")
                return False, None
            
            # Check if expired
            expires_at = result.get('expires_at')
            if isinstance(expires_at, str):
                expires_at = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S')
            
            if datetime.now() > expires_at:
                logger.warning("[-] Token expired")
                return False, None
            
            logger.info(f"[+] Token validated for {result.get('email')}")
            return True, result
            
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return False, None
    
    def mark_token_used(self, token: str) -> bool:
        """
        Mark reset token as used
        
        Args:
            token: Reset token to mark as used
        
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
            UPDATE password_reset_tokens
            SET is_used = TRUE, used_at = NOW()
            WHERE reset_token = %s
            """
            
            success, result = self.pool.execute_query(query, (token,))
            
            if success:
                logger.info("[+] Token marked as used")
                return True
            else:
                logger.error(f"[-] Failed to mark token as used: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error marking token as used: {e}")
            return False
    
    def cleanup_expired_tokens(self) -> int:
        """
        Delete expired tokens from database
        
        Returns:
            Number of tokens deleted
        """
        try:
            query = """
            DELETE FROM password_reset_tokens
            WHERE expires_at < NOW() OR is_used = TRUE
            """
            
            success, result = self.pool.execute_query(query)
            
            if success:
                deleted = result.get('affected_rows', 0)
                logger.info(f"[+] Cleaned up {deleted} expired tokens")
                return deleted
            else:
                logger.error("[-] Failed to cleanup tokens")
                return 0
                
        except Exception as e:
            logger.error(f"Error cleaning up tokens: {e}")
            return 0


def main():
    """Test password reset manager"""
    import sys
    from config import Config
    
    logging.basicConfig(level=logging.INFO, format=Config.LOG_FORMAT)
    
    try:
        print("\n" + "="*60)
        print("PASSWORD RESET MANAGER TEST")
        print("="*60)
        
        manager = PasswordResetManager()
        
        # Test 1: Verify existing email
        print("\n1. Testing email verification...")
        exists, user_id = manager.verify_email_exists('test@example.com')
        if exists:
            print(f"   [+] Email found (User ID: {user_id})")
        else:
            print("   [-] Email not found")
        
        # Test 2: Verify non-existent email
        print("\n2. Testing non-existent email...")
        exists, user_id = manager.verify_email_exists('nonexistent@email.com')
        if not exists:
            print("   [+] Correctly identified non-existent email")
        
        # Test 3: Generate reset token
        if exists:
            print("\n3. Generating reset token...")
            token = manager.generate_reset_token('test@example.com', user_id)
            if token:
                print(f"   [+] Token generated: {token[:20]}...")
                
                # Test 4: Validate token
                print("\n4. Validating token...")
                valid, data = manager.validate_reset_token(token)
                if valid:
                    print(f"   [+] Token is valid")
                    print(f"       Email: {data.get('email')}")
                    print(f"       Expires: {data.get('expires_at')}")
        
        print("\n" + "="*60)
        print("[+] Tests complete!")
        print("="*60 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n[-] Test failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

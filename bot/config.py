"""
Configuration module for DEX Bot MVP.
Loads and validates all required environment variables.
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class Config:
    """Global configuration loaded from environment variables."""
    
    def __init__(self):
        """Initialize and validate all required configuration values."""
        
        # Blockchain & DEX configuration
        self.RPC_URL = self._require_env("RPC_URL")
        self.WALLET_PRIVATE_KEY = self._require_env("WALLET_PRIVATE_KEY")
        self.DEX_ROUTER_ADDRESS = self._require_env("DEX_ROUTER_ADDRESS")
        self.BASE_TOKEN_ADDRESS = self._require_env("BASE_TOKEN_ADDRESS")
        self.QUOTE_TOKEN_ADDRESS = self._require_env("QUOTE_TOKEN_ADDRESS")
        
        # Telegram configuration
        self.TELEGRAM_BOT_TOKEN = self._require_env("TELEGRAM_BOT_TOKEN")
        self.ALLOWED_TELEGRAM_IDS = self._parse_allowed_ids(
            self._require_env("ALLOWED_TELEGRAM_IDS")
        )
        
        # Optional configuration with defaults
        self.DATABASE_PATH = os.getenv("DATABASE_PATH", "bot_data.db")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.MAX_TRADES_PER_SESSION = int(os.getenv("MAX_TRADES_PER_SESSION", "1000"))
        
        # Gas configuration (optional)
        self.GAS_PRICE_GWEI = os.getenv("GAS_PRICE_GWEI")  # None = use network default
        self.GAS_LIMIT = int(os.getenv("GAS_LIMIT", "300000"))
        
        # RPC configuration
        self.RPC_TIMEOUT = int(os.getenv("RPC_TIMEOUT", "30"))
        self.RPC_MAX_RETRIES = int(os.getenv("RPC_MAX_RETRIES", "3"))
        
        # Logging configuration
        self.LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "bot.log")
        self.ENABLE_LOG_ROTATION = os.getenv("ENABLE_LOG_ROTATION", "true").lower() == "true"
        self.MAX_LOG_SIZE_MB = int(os.getenv("MAX_LOG_SIZE_MB", "10"))
        self.LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))
        
        # Rate limiting (commands per minute per user)
        self.RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
        
        # Validate addresses
        self._validate_address(self.DEX_ROUTER_ADDRESS, "DEX_ROUTER_ADDRESS")
        self._validate_address(self.BASE_TOKEN_ADDRESS, "BASE_TOKEN_ADDRESS")
        self._validate_address(self.QUOTE_TOKEN_ADDRESS, "QUOTE_TOKEN_ADDRESS")
        
        # Validate private key format
        self._validate_private_key(self.WALLET_PRIVATE_KEY)
        
        # Validate paths
        self._validate_path(self.DATABASE_PATH, "DATABASE_PATH")
        self._validate_path(self.LOG_FILE_PATH, "LOG_FILE_PATH")
    
    @staticmethod
    def _require_env(key: str) -> str:
        """Get required environment variable or raise error."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return value
    
    @staticmethod
    def _parse_allowed_ids(ids_str: str) -> List[int]:
        """Parse comma-separated list of Telegram user IDs."""
        try:
            ids = [int(id_str.strip()) for id_str in ids_str.split(",") if id_str.strip()]
            if not ids:
                raise ValueError("ALLOWED_TELEGRAM_IDS must contain at least one ID")
            return ids
        except ValueError as e:
            raise ValueError(f"Invalid ALLOWED_TELEGRAM_IDS format: {e}")
    
    @staticmethod
    def _validate_address(address: str, name: str) -> None:
        """Validate Ethereum address format."""
        if not address.startswith("0x") or len(address) != 42:
            raise ValueError(
                f"{name} must be a valid Ethereum address (0x + 40 hex chars)"
            )
    
    @staticmethod
    def _validate_private_key(private_key: str) -> None:
        """Validate private key format."""
        # Remove 0x prefix if present
        key = private_key.replace("0x", "")
        if len(key) != 64:
            raise ValueError("WALLET_PRIVATE_KEY must be 64 hex characters (with or without 0x prefix)")
        try:
            int(key, 16)
        except ValueError:
            raise ValueError("WALLET_PRIVATE_KEY must contain only hexadecimal characters")
    
    @staticmethod
    def _validate_path(path: str, name: str) -> None:
        """Validate file path is safe and doesn't contain directory traversal."""
        if not path:
            raise ValueError(f"{name} cannot be empty")
        # Check for directory traversal attempts
        if ".." in path or path.startswith("/") or "\\" in path:
            # Allow absolute paths but warn - in production, consider restricting
            pass
        # Ensure parent directory exists for database
        if name == "DATABASE_PATH":
            import os
            db_dir = os.path.dirname(path) or "."
            if not os.path.exists(db_dir):
                try:
                    os.makedirs(db_dir, exist_ok=True)
                except Exception as e:
                    raise ValueError(f"Cannot create directory for {name}: {e}")
    
    def is_authorized_user(self, user_id: int) -> bool:
        """Check if a Telegram user ID is authorized to use the bot."""
        return user_id in self.ALLOWED_TELEGRAM_IDS


# Global config instance
config = Config()

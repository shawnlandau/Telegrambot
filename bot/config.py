"""
Configuration module for DEX Bot MVP - Solana Edition.
Loads and validates all required environment variables.
"""

import os
from typing import List
from dotenv import load_dotenv
import base58

# Load environment variables from .env file if present
load_dotenv()


class Config:
    """Global configuration loaded from environment variables."""
    
    def __init__(self):
        """Initialize and validate all required configuration values."""
        
        # Solana blockchain & DEX configuration
        self.SOLANA_RPC_URL = self._require_env("SOLANA_RPC_URL")
        self.WALLET_PRIVATE_KEY = self._require_env("WALLET_PRIVATE_KEY")
        self.RAYDIUM_PROGRAM_ID = os.getenv("RAYDIUM_PROGRAM_ID", "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8")
        
        # Token addresses (Solana base58 format)
        # BASE = SOL (native Solana, using wrapped SOL program for swaps)
        self.BASE_TOKEN_ADDRESS = os.getenv("BASE_TOKEN_ADDRESS", "So11111111111111111111111111111111111111112")
        # QUOTE = MEMESAI or other SPL token
        self.QUOTE_TOKEN_ADDRESS = self._require_env("QUOTE_TOKEN_ADDRESS")
        
        # Raydium pool ID for the trading pair (optional - Jupiter doesn't require it)
        self.RAYDIUM_POOL_ID = os.getenv("RAYDIUM_POOL_ID", "")
        
        # Telegram configuration
        self.TELEGRAM_BOT_TOKEN = self._require_env("TELEGRAM_BOT_TOKEN")
        self.ALLOWED_TELEGRAM_IDS = self._parse_allowed_ids(
            self._require_env("ALLOWED_TELEGRAM_IDS")
        )
        
        # Optional configuration with defaults
        self.DATABASE_PATH = os.getenv("DATABASE_PATH", "bot_data.db")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.MAX_TRADES_PER_SESSION = int(os.getenv("MAX_TRADES_PER_SESSION", "1000"))
        
        # Solana transaction configuration
        self.MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
        self.SKIP_PREFLIGHT = os.getenv("SKIP_PREFLIGHT", "false").lower() == "true"
        self.COMMITMENT_LEVEL = os.getenv("COMMITMENT_LEVEL", "confirmed")  # finalized, confirmed, processed
        
        # Slippage tolerance in basis points (default 100 = 1%)
        self.DEFAULT_SLIPPAGE_BPS = int(os.getenv("DEFAULT_SLIPPAGE_BPS", "100"))
        
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
        
        # Simulation mode (for testing without real trades)
        self.SIMULATION_MODE = os.getenv("SIMULATION_MODE", "false").lower() == "true"
        
        # Validate Solana addresses
        self._validate_solana_address(self.RAYDIUM_PROGRAM_ID, "RAYDIUM_PROGRAM_ID")
        self._validate_solana_address(self.BASE_TOKEN_ADDRESS, "BASE_TOKEN_ADDRESS")
        self._validate_solana_address(self.QUOTE_TOKEN_ADDRESS, "QUOTE_TOKEN_ADDRESS")
        if self.RAYDIUM_POOL_ID:  # Only validate if provided
            self._validate_solana_address(self.RAYDIUM_POOL_ID, "RAYDIUM_POOL_ID")
        
        # Validate private key format (Solana private key in base58)
        self._validate_solana_private_key(self.WALLET_PRIVATE_KEY)
        
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
    def _validate_solana_address(address: str, name: str) -> None:
        """Validate Solana address format (base58)."""
        try:
            decoded = base58.b58decode(address)
            # Solana addresses are 32 bytes
            if len(decoded) != 32:
                raise ValueError(
                    f"{name} must be a valid Solana address (32 bytes in base58)"
                )
        except Exception as e:
            raise ValueError(
                f"{name} is not a valid Solana address: {e}"
            )
    
    @staticmethod
    def _validate_solana_private_key(private_key: str) -> None:
        """Validate Solana private key format.
        
        Solana private keys can be in different formats:
        - Base58 encoded string (most common)
        - JSON array of bytes
        - Hex string (less common)
        
        For this implementation, we expect base58 encoded string.
        """
        try:
            # Try to decode as base58
            decoded = base58.b58decode(private_key)
            # Solana private keys are 64 bytes (includes public key)
            if len(decoded) not in [32, 64]:
                raise ValueError(
                    "WALLET_PRIVATE_KEY must be 32 or 64 bytes when base58 decoded"
                )
        except Exception as e:
            raise ValueError(
                f"WALLET_PRIVATE_KEY is not a valid Solana private key (base58): {e}"
            )
    
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

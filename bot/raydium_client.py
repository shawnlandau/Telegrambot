"""
Raydium Client for interacting with Raydium DEX on Solana.
Handles token swaps, balance queries, and price estimation.
"""

import logging
import time
from typing import Dict, Optional, Tuple
from decimal import Decimal

from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed, Finalized, Processed
from solana.transaction import Transaction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.instruction import Instruction, AccountMeta
from solders.rpc.responses import SendTransactionResp
import base58

from .config import config

logger = logging.getLogger(__name__)

# Solana native token constants
LAMPORTS_PER_SOL = 1_000_000_000
NATIVE_SOL_MINT = "So11111111111111111111111111111111111111112"

# Token program IDs
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")


class RaydiumClient:
    """
    Client for interacting with Raydium DEX on Solana.
    Manages connection, keypair, token accounts, and swap execution.
    """
    
    def __init__(self):
        """Initialize Solana connection and load wallet keypair."""
        # Determine commitment level
        commitment_map = {
            "finalized": Finalized,
            "confirmed": Confirmed,
            "processed": Processed
        }
        commitment = commitment_map.get(config.COMMITMENT_LEVEL.lower(), Confirmed)
        
        # Connect to Solana RPC
        self.client = Client(
            config.SOLANA_RPC_URL,
            commitment=commitment,
            timeout=config.RPC_TIMEOUT
        )
        
        if not self._connect_with_retry():
            raise ConnectionError(f"Failed to connect to Solana RPC: {config.SOLANA_RPC_URL}")
        
        logger.info(f"Connected to Solana network")
        
        # Load wallet keypair from private key
        self.keypair = self._load_keypair(config.WALLET_PRIVATE_KEY)
        self.wallet_address = str(self.keypair.pubkey())
        logger.info(f"Loaded wallet: {self.wallet_address}")
        
        # Parse token addresses
        self.base_token_mint = Pubkey.from_string(config.BASE_TOKEN_ADDRESS)
        self.quote_token_mint = Pubkey.from_string(config.QUOTE_TOKEN_ADDRESS)
        self.pool_id = Pubkey.from_string(config.RAYDIUM_POOL_ID)
        self.raydium_program_id = Pubkey.from_string(config.RAYDIUM_PROGRAM_ID)
        
        # Get token decimals
        self.base_decimals = self._get_token_decimals(self.base_token_mint)
        self.quote_decimals = self._get_token_decimals(self.quote_token_mint)
        
        logger.info(f"Base token decimals: {self.base_decimals}")
        logger.info(f"Quote token decimals: {self.quote_decimals}")
        
        # Cache token symbols
        self.base_symbol = "SOL" if str(self.base_token_mint) == NATIVE_SOL_MINT else "BASE"
        self.quote_symbol = "MEMESAI"  # Can be fetched from token metadata if needed
        
        logger.info(f"Trading pair: {self.base_symbol}/{self.quote_symbol}")
    
    def _connect_with_retry(self) -> bool:
        """Connect to Solana RPC with retry logic."""
        for attempt in range(config.RPC_MAX_RETRIES):
            try:
                # Test connection by getting version
                response = self.client.get_version()
                if response.value:
                    logger.info(f"Solana RPC version: {response.value}")
                    return True
            except Exception as e:
                logger.warning(f"RPC connection attempt {attempt + 1} failed: {e}")
                if attempt < config.RPC_MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        return False
    
    def _rpc_call_with_retry(self, func, *args, **kwargs):
        """Execute RPC call with retry logic."""
        last_exception = None
        for attempt in range(config.RPC_MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(f"RPC call attempt {attempt + 1}/{config.RPC_MAX_RETRIES} failed: {e}")
                if attempt < config.RPC_MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        raise last_exception
    
    def _load_keypair(self, private_key: str) -> Keypair:
        """
        Load Solana keypair from private key string.
        Supports base58 encoded private key.
        """
        try:
            # Decode base58 private key
            private_key_bytes = base58.b58decode(private_key)
            
            # If it's 64 bytes, it contains both private and public key
            # If it's 32 bytes, it's just the seed
            if len(private_key_bytes) == 64:
                keypair = Keypair.from_bytes(private_key_bytes)
            elif len(private_key_bytes) == 32:
                keypair = Keypair.from_seed(private_key_bytes)
            else:
                raise ValueError(f"Invalid private key length: {len(private_key_bytes)} bytes")
            
            return keypair
        except Exception as e:
            raise ValueError(f"Failed to load Solana keypair: {e}")
    
    def _get_token_decimals(self, mint: Pubkey) -> int:
        """Get token decimals from mint account."""
        # For native SOL, decimals are always 9
        if str(mint) == NATIVE_SOL_MINT:
            return 9
        
        try:
            # Fetch token mint account data
            response = self._rpc_call_with_retry(
                self.client.get_account_info,
                mint
            )
            
            if not response.value:
                raise Exception(f"Token mint account not found: {mint}")
            
            # Parse token mint data to get decimals
            # Token mint data structure (first 44 bytes):
            # - 36 bytes: mint authority (32) + supply (8)
            # - 1 byte: decimals
            # - ... other fields
            account_data = response.value.data
            if len(account_data) < 45:
                raise Exception(f"Invalid token mint data length: {len(account_data)}")
            
            decimals = account_data[44]
            return decimals
            
        except Exception as e:
            logger.error(f"Failed to get token decimals for {mint}: {e}")
            # Default to 9 if we can't fetch
            return 9
    
    def get_balances(self) -> Dict[str, float]:
        """
        Get current token balances for the wallet.
        Returns balances adjusted for decimals.
        """
        try:
            # Get SOL balance (in lamports)
            sol_response = self._rpc_call_with_retry(
                self.client.get_balance,
                self.keypair.pubkey()
            )
            base_balance = float(sol_response.value) / LAMPORTS_PER_SOL
            
            # Get SPL token balance for quote token
            quote_token_account = self._get_associated_token_address(
                self.keypair.pubkey(),
                self.quote_token_mint
            )
            
            quote_response = self._rpc_call_with_retry(
                self.client.get_token_account_balance,
                quote_token_account
            )
            
            if quote_response.value:
                quote_balance = float(quote_response.value.ui_amount or 0)
            else:
                quote_balance = 0.0
            
            logger.debug(
                f"Balances: {base_balance:.6f} {self.base_symbol}, "
                f"{quote_balance:.6f} {self.quote_symbol}"
            )
            
            return {
                "base": base_balance,
                "quote": quote_balance,
            }
        except Exception as e:
            logger.error(f"Failed to fetch balances: {e}")
            raise
    
    def _get_associated_token_address(self, owner: Pubkey, mint: Pubkey) -> Pubkey:
        """Calculate the associated token account address for a given owner and mint."""
        # This is a simplified version - in production, use spl-token library
        # For now, we'll use a placeholder implementation
        # TODO: Implement proper ATA derivation using find_program_address
        
        seeds = [
            bytes(owner),
            bytes(TOKEN_PROGRAM_ID),
            bytes(mint)
        ]
        
        # This is a simplified implementation - proper implementation requires
        # using Pubkey.find_program_address with the correct seeds
        # For production use, import and use the proper SPL token utilities
        
        # Placeholder: return a derived address
        # In real implementation, use:
        # from spl.token.instructions import get_associated_token_address
        # return get_associated_token_address(owner, mint)
        
        # For now, we'll make the RPC call return this info when getting balances
        raise NotImplementedError(
            "Associated token address derivation needs to be implemented with proper SPL utilities"
        )
    
    def get_price(self) -> float:
        """
        Get approximate current price (quote per base).
        
        This requires querying the Raydium pool state to get reserves.
        For a production implementation, you would:
        1. Fetch the pool account data
        2. Parse the reserves for base and quote tokens
        3. Calculate price = quote_reserve / base_reserve (adjusted for decimals)
        
        For now, this is a placeholder that needs pool state parsing.
        """
        try:
            # TODO: Implement Raydium pool state parsing
            # This requires understanding the Raydium pool account structure
            # and parsing the reserve amounts
            
            logger.warning("get_price() is not yet implemented - returning placeholder value")
            # Placeholder - in production, fetch from pool state
            return 1.0
            
        except Exception as e:
            logger.error(f"Failed to get price: {e}")
            raise
    
    def swap_exact_sol_for_tokens(
        self,
        notional_sol: float,
        slippage_bps: int
    ) -> Dict[str, any]:
        """
        BUY: Swap exact SOL for SPL tokens (MEMESAI).
        
        Args:
            notional_sol: Amount of SOL to spend (in SOL, not lamports)
            slippage_bps: Slippage tolerance in basis points (e.g., 50 = 0.5%)
        
        Returns:
            dict with 'amount_in', 'amount_out', 'tx_hash', 'slot'
        """
        logger.info(f"BUY: Swapping {notional_sol} {self.base_symbol} for {self.quote_symbol}")
        
        # Convert SOL to lamports
        amount_in_lamports = int(notional_sol * LAMPORTS_PER_SOL)
        
        # TODO: Implement Raydium swap instruction
        # This requires:
        # 1. Building the Raydium swap instruction with correct accounts
        # 2. Getting minimum output amount based on pool state and slippage
        # 3. Creating and sending the transaction
        
        # Placeholder implementation
        raise NotImplementedError(
            "Raydium swap functionality needs to be implemented. "
            "This requires proper Raydium program integration with correct instruction data and accounts."
        )
    
    def swap_exact_tokens_for_sol(
        self,
        notional_sol_equiv: float,
        slippage_bps: int
    ) -> Dict[str, any]:
        """
        SELL: Swap SPL tokens (MEMESAI) for SOL.
        
        Args:
            notional_sol_equiv: Approximate SOL value to sell (in SOL)
            slippage_bps: Slippage tolerance in basis points
        
        Returns:
            dict with 'amount_in', 'amount_out', 'tx_hash', 'slot'
        """
        logger.info(f"SELL: Swapping ~{notional_sol_equiv} {self.base_symbol} worth of {self.quote_symbol}")
        
        # TODO: Implement Raydium swap instruction
        # Similar to buy but in reverse direction
        
        raise NotImplementedError(
            "Raydium swap functionality needs to be implemented. "
            "This requires proper Raydium program integration with correct instruction data and accounts."
        )
    
    def _send_transaction(self, transaction: Transaction) -> str:
        """
        Send a transaction to Solana network.
        
        Args:
            transaction: The transaction to send
        
        Returns:
            Transaction signature (string)
        """
        try:
            # Send transaction
            response = self.client.send_transaction(
                transaction,
                self.keypair,
                opts={
                    "skip_preflight": config.SKIP_PREFLIGHT,
                    "max_retries": config.MAX_RETRIES
                }
            )
            
            if isinstance(response, SendTransactionResp) and response.value:
                signature = str(response.value)
                logger.info(f"Transaction sent: {signature}")
                
                # Wait for confirmation
                self._confirm_transaction(signature)
                
                return signature
            else:
                raise Exception(f"Failed to send transaction: {response}")
                
        except Exception as e:
            logger.error(f"Failed to send transaction: {e}")
            raise
    
    def _confirm_transaction(self, signature: str, max_attempts: int = 30) -> bool:
        """
        Wait for transaction confirmation.
        
        Args:
            signature: Transaction signature to confirm
            max_attempts: Maximum number of attempts to check (default: 30)
        
        Returns:
            True if confirmed, raises exception otherwise
        """
        for attempt in range(max_attempts):
            try:
                response = self.client.get_signature_statuses([signature])
                if response.value and response.value[0]:
                    status = response.value[0]
                    if status.confirmation_status in ["confirmed", "finalized"]:
                        logger.info(f"Transaction confirmed: {signature}")
                        return True
                    elif status.err:
                        raise Exception(f"Transaction failed: {status.err}")
                
                # Wait before next check
                time.sleep(2)
                
            except Exception as e:
                logger.warning(f"Confirmation check {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(2)
                else:
                    raise
        
        raise Exception(f"Transaction confirmation timeout: {signature}")

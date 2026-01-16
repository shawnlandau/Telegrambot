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
from solana.rpc.types import TxOpts
from solders.transaction import VersionedTransaction
from solders.message import to_bytes_versioned
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
        # Check if running in simulation mode
        self.simulation_mode = config.SIMULATION_MODE
        
        if self.simulation_mode:
            logger.warning("⚠️  SIMULATION MODE ENABLED - No real trades will be executed!")
        
        # Determine commitment level
        commitment_map = {
            "finalized": Finalized,
            "confirmed": Confirmed,
            "processed": Processed
        }
        self.commitment = commitment_map.get(config.COMMITMENT_LEVEL.lower(), Confirmed)
        
        # Connect to Solana RPC
        self.client = Client(
            config.SOLANA_RPC_URL,
            commitment=self.commitment,
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
        
        # Pool ID is optional when using Jupiter
        self.pool_id = Pubkey.from_string(config.RAYDIUM_POOL_ID) if config.RAYDIUM_POOL_ID else None
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
        
        In simulation mode, returns simulated balances.
        """
        # SIMULATION MODE: Return simulated balances
        if self.simulation_mode:
            base_balance = getattr(self, '_sim_sol_balance', 0.75)
            quote_balance = getattr(self, '_sim_token_balance', 0.0)
            
            logger.debug(
                f"[SIMULATION] Balances: {base_balance:.6f} {self.base_symbol}, "
                f"{quote_balance:.2f} {self.quote_symbol}"
            )
            
            return {
                "base": base_balance,
                "quote": quote_balance,
            }
        
        # REAL MODE: Fetch actual on-chain balances
        try:
            # Get SOL balance (in lamports)
            sol_response = self._rpc_call_with_retry(
                self.client.get_balance,
                self.keypair.pubkey()
            )
            base_balance = float(sol_response.value) / LAMPORTS_PER_SOL
            
            # Get SPL token balance for quote token
            # Note: Token account might not exist yet (until first BUY)
            quote_balance = 0.0
            try:
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
                    # Token account doesn't exist yet (no tokens owned)
                    logger.debug(f"{self.quote_symbol} token account not found (balance = 0)")
                    quote_balance = 0.0
            except Exception as token_error:
                # Token account doesn't exist or can't be fetched
                # This is normal for a new wallet that hasn't received tokens yet
                logger.debug(f"Could not fetch {self.quote_symbol} balance (likely doesn't exist yet): {token_error}")
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
        """
        Calculate the associated token account address for a given owner and mint.
        
        Args:
            owner: The wallet public key that owns the token account
            mint: The token mint address
        
        Returns:
            The derived ATA public key
        """
        try:
            # Derive ATA using PDA (Program Derived Address)
            # Seeds: [owner, TOKEN_PROGRAM_ID, mint]
            ata, bump = Pubkey.find_program_address(
                [
                    bytes(owner),
                    bytes(TOKEN_PROGRAM_ID),
                    bytes(mint)
                ],
                ASSOCIATED_TOKEN_PROGRAM_ID
            )
            return ata
        except Exception as e:
            logger.error(f"Failed to derive ATA for owner={owner}, mint={mint}: {e}")
            raise
    
    def get_price(self) -> float:
        """
        Get approximate current price (quote per base) using Jupiter quote API.
        
        This fetches a live quote for 1 SOL to determine the current exchange rate.
        More reliable than parsing pool state directly.
        
        In simulation mode, returns a simulated price.
        
        Returns:
            Price as quote_tokens_per_base_token (MEMESAI per SOL)
        """
        # SIMULATION MODE: Return simulated price
        if self.simulation_mode:
            import random
            # Simulate price with small random variations (±2%)
            base_price = getattr(self, '_sim_price', 1000000.0)  # 1M MEMESAI per SOL
            variation = base_price * (random.uniform(-0.02, 0.02))
            price = base_price + variation
            self._sim_price = price  # Store for next time
            logger.info(f"[SIMULATION] Current price: 1 {self.base_symbol} = {price:.2f} {self.quote_symbol}")
            return price
        
        # REAL MODE: Use Jupiter API
        try:
            import requests
            import time as time_module  # Ensure time is accessible in nested scopes
            
            # Use 1 SOL as test amount
            test_amount_lamports = LAMPORTS_PER_SOL
            
            logger.debug(f"Fetching price quote for 1 {self.base_symbol}...")
            
            # Get quote from Jupiter with retry logic (using new lite-api endpoint)
            quote_url = "https://lite-api.jup.ag/swap/v1/quote"
            quote_params = {
                "inputMint": str(self.base_token_mint),
                "outputMint": str(self.quote_token_mint),
                "amount": str(test_amount_lamports),
                "slippageBps": "50",  # Small slippage for price check
            }
            
            # Retry up to 3 times with exponential backoff
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    quote_response = requests.get(
                        quote_url, 
                        params=quote_params, 
                        timeout=15,
                        headers={'User-Agent': 'Mozilla/5.0'}
                    )
                    quote_response.raise_for_status()
                    quote_data = quote_response.json()
                    break  # Success
                except (requests.exceptions.ConnectionError, 
                        requests.exceptions.Timeout,
                        requests.exceptions.RequestException) as e:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                        logger.warning(f"Jupiter API request failed (attempt {attempt + 1}/{max_retries}): {e}")
                        logger.info(f"Retrying in {wait_time}s...")
                        time_module.sleep(wait_time)
                    else:
                        raise  # Re-raise on final attempt
            
            if "outAmount" not in quote_data:
                raise Exception(f"Invalid quote response: {quote_data}")
            
            # Calculate price: output tokens per 1 SOL
            out_amount_raw = int(quote_data["outAmount"])
            out_amount = out_amount_raw / (10 ** self.quote_decimals)
            
            # Price = quote tokens per 1 base token
            price = out_amount  # Already calculated per 1 SOL
            
            logger.info(f"Current price: 1 {self.base_symbol} = {price:.6f} {self.quote_symbol}")
            
            return price
            
        except Exception as e:
            logger.error(f"Failed to get price from Jupiter: {e}")
            logger.warning("Using cached/fallback price")
            # Return last known price or reasonable default
            # In production, you might cache the last successful price
            return getattr(self, '_last_price', 0.01)
    
    def swap_exact_sol_for_tokens(
        self,
        notional_sol: float,
        slippage_bps: int
    ) -> Dict[str, any]:
        """
        BUY: Swap exact SOL for SPL tokens (MEMESAI).
        
        Uses Jupiter Aggregator API for best execution.
        This is more reliable than direct Raydium calls and handles routing automatically.
        
        In simulation mode, simulates the trade without executing on-chain.
        
        Args:
            notional_sol: Amount of SOL to spend (in SOL, not lamports)
            slippage_bps: Slippage tolerance in basis points (e.g., 50 = 0.5%)
        
        Returns:
            dict with 'amount_in', 'amount_out', 'tx_hash', 'slot'
        """
        logger.info(f"BUY: Swapping {notional_sol} {self.base_symbol} for {self.quote_symbol}")
        
        # SIMULATION MODE: Simulate the trade
        if self.simulation_mode:
            import time
            import hashlib
            
            # Get simulated price
            current_price = self.get_price()
            
            # Calculate expected output with small slippage
            slippage_factor = 1 - (slippage_bps / 10000)
            expected_out = notional_sol * current_price * slippage_factor
            
            # Generate fake transaction hash
            fake_tx_data = f"sim_buy_{notional_sol}_{time.time()}".encode()
            fake_tx_hash = hashlib.sha256(fake_tx_data).hexdigest()
            
            # Simulate network delay
            time.sleep(0.5)
            
            logger.info(f"[SIMULATION] BUY executed: {notional_sol} {self.base_symbol} → {expected_out:.2f} {self.quote_symbol}")
            logger.info(f"[SIMULATION] TX: {fake_tx_hash}")
            
            # Update simulated balances
            if not hasattr(self, '_sim_sol_balance'):
                self._sim_sol_balance = 0.75  # Initial balance
            if not hasattr(self, '_sim_token_balance'):
                self._sim_token_balance = 0.0
            
            self._sim_sol_balance -= notional_sol
            self._sim_token_balance += expected_out
            
            return {
                'amount_in': notional_sol,
                'amount_out': expected_out,
                'tx_hash': fake_tx_hash,
                'slot': None,
                'gas_used': 50000,  # Simulated gas (typical Solana compute units)
                'gas_price_gwei': 0.000005  # Simulated fee in SOL (~5000 lamports)
            }
        
        try:
            import requests
            import base64
            import time as time_module  # Ensure time is accessible in nested scopes
            
            # Convert SOL to lamports
            amount_in_lamports = int(notional_sol * LAMPORTS_PER_SOL)
            
            logger.info(f"Getting Jupiter quote for {amount_in_lamports} lamports...")
            
            # Step 1: Get quote from Jupiter with retry logic
            quote_url = f"https://lite-api.jup.ag/swap/v1/quote"
            quote_params = {
                "inputMint": str(self.base_token_mint),
                "outputMint": str(self.quote_token_mint),
                "amount": str(amount_in_lamports),
                "slippageBps": str(slippage_bps),
            }
            
            # Retry up to 3 times
            max_retries = 3
            quote_data = None
            for attempt in range(max_retries):
                try:
                    quote_response = requests.get(
                        quote_url, 
                        params=quote_params, 
                        timeout=15,
                        headers={'User-Agent': 'Mozilla/5.0'}
                    )
                    quote_response.raise_for_status()
                    quote_data = quote_response.json()
                    break  # Success
                except (requests.exceptions.ConnectionError, 
                        requests.exceptions.Timeout,
                        requests.exceptions.RequestException) as e:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"Jupiter quote request failed (attempt {attempt + 1}/{max_retries}): {e}")
                        logger.info(f"Retrying in {wait_time}s...")
                        time_module.sleep(wait_time)
                    else:
                        raise Exception(f"Jupiter API unavailable after {max_retries} attempts: {e}")
            
            if not quote_data:
                raise Exception("Failed to get quote data from Jupiter")
            
            if "outAmount" not in quote_data:
                raise Exception(f"Invalid quote response: {quote_data}")
            
            expected_out_raw = int(quote_data["outAmount"])
            expected_out = expected_out_raw / (10 ** self.quote_decimals)
            
            logger.info(f"Expected output: {expected_out:.6f} {self.quote_symbol}")
            
            # Step 2: Get swap transaction from Jupiter with retry logic
            swap_url = "https://lite-api.jup.ag/swap/v1/swap"
            swap_payload = {
                "quoteResponse": quote_data,
                "userPublicKey": str(self.keypair.pubkey()),
                "wrapAndUnwrapSol": True,
                "dynamicComputeUnitLimit": True,
            }
            
            # Retry swap request
            swap_data = None
            for attempt in range(max_retries):
                try:
                    swap_response = requests.post(
                        swap_url, 
                        json=swap_payload, 
                        timeout=15,
                        headers={'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json'}
                    )
                    swap_response.raise_for_status()
                    swap_data = swap_response.json()
                    break  # Success
                except (requests.exceptions.ConnectionError, 
                        requests.exceptions.Timeout,
                        requests.exceptions.RequestException) as e:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"Jupiter swap request failed (attempt {attempt + 1}/{max_retries}): {e}")
                        logger.info(f"Retrying in {wait_time}s...")
                        time_module.sleep(wait_time)
                    else:
                        raise Exception(f"Jupiter API unavailable after {max_retries} attempts: {e}")
            
            if not swap_data or "swapTransaction" not in swap_data:
                raise Exception(f"Invalid swap response: {swap_data}")
            
            # Step 3: Decode and sign transaction
            swap_transaction_bytes = base64.b64decode(swap_data["swapTransaction"])
            
            # Deserialize versioned transaction (Jupiter uses versioned transactions)
            raw_transaction = VersionedTransaction.from_bytes(swap_transaction_bytes)
            
            # Sign the transaction message with our keypair
            tx_signature = self.keypair.sign_message(to_bytes_versioned(raw_transaction.message))
            
            # Populate transaction with signature
            signed_transaction = VersionedTransaction.populate(raw_transaction.message, [tx_signature])
            
            # Step 4: Send transaction
            signature_str = self._send_transaction(signed_transaction)
            
            logger.info(f"BUY swap successful: {signature_str}")
            
            # Step 5: Return result
            actual_amount_in = notional_sol
            actual_amount_out = expected_out  # Actual would be parsed from logs
            
            return {
                'amount_in': actual_amount_in,
                'amount_out': actual_amount_out,
                'tx_hash': signature_str,
                'slot': None,
                'gas_used': 50000,  # Solana compute units (estimated)
                'gas_price_gwei': 0.000005  # Solana transaction fee (~5000 lamports)
            }
            
        except Exception as e:
            logger.error(f"BUY swap failed: {e}")
            raise Exception(f"Failed to execute BUY swap: {str(e)}")
    
    def swap_exact_tokens_for_sol(
        self,
        notional_sol_equiv: float,
        slippage_bps: int
    ) -> Dict[str, any]:
        """
        SELL: Swap SPL tokens (MEMESAI) for SOL.
        
        Uses Jupiter Aggregator API for best execution.
        
        In simulation mode, simulates the trade without executing on-chain.
        
        Args:
            notional_sol_equiv: Approximate SOL value to sell (in SOL)
            slippage_bps: Slippage tolerance in basis points
        
        Returns:
            dict with 'amount_in', 'amount_out', 'tx_hash', 'slot'
        """
        logger.info(f"SELL: Swapping ~{notional_sol_equiv} {self.base_symbol} worth of {self.quote_symbol}")
        
        # SIMULATION MODE: Simulate the trade
        if self.simulation_mode:
            import time
            import hashlib
            
            # Get simulated price
            current_price = self.get_price()
            token_amount = notional_sol_equiv * current_price
            
            # Calculate expected output with small slippage
            slippage_factor = 1 - (slippage_bps / 10000)
            expected_out_sol = notional_sol_equiv * slippage_factor
            
            # Generate fake transaction hash
            fake_tx_data = f"sim_sell_{token_amount}_{time.time()}".encode()
            fake_tx_hash = hashlib.sha256(fake_tx_data).hexdigest()
            
            # Simulate network delay
            time.sleep(0.5)
            
            logger.info(f"[SIMULATION] SELL executed: {token_amount:.2f} {self.quote_symbol} → {expected_out_sol} {self.base_symbol}")
            logger.info(f"[SIMULATION] TX: {fake_tx_hash}")
            
            # Update simulated balances
            if not hasattr(self, '_sim_sol_balance'):
                self._sim_sol_balance = 0.75
            if not hasattr(self, '_sim_token_balance'):
                self._sim_token_balance = 0.0
            
            self._sim_sol_balance += expected_out_sol
            self._sim_token_balance -= token_amount
            
            return {
                'amount_in': token_amount,
                'amount_out': expected_out_sol,
                'tx_hash': fake_tx_hash,
                'slot': None,
                'gas_used': 50000,  # Simulated gas (typical Solana compute units)
                'gas_price_gwei': 0.000005  # Simulated fee in SOL (~5000 lamports)
            }
        
        try:
            import requests
            import base64
            import time as time_module  # Ensure time is accessible in nested scopes
            
            # Calculate token amount to sell based on current price
            current_price = self.get_price()
            token_amount = notional_sol_equiv * current_price
            amount_in_tokens = int(token_amount * (10 ** self.quote_decimals))
            
            logger.info(f"Selling {token_amount:.6f} {self.quote_symbol}")
            logger.info(f"Getting Jupiter quote for {amount_in_tokens} tokens...")
            
            # Step 1: Get quote from Jupiter with retry logic
            quote_url = f"https://lite-api.jup.ag/swap/v1/quote"
            quote_params = {
                "inputMint": str(self.quote_token_mint),  # Selling MEMESAI
                "outputMint": str(self.base_token_mint),   # Receiving SOL
                "amount": str(amount_in_tokens),
                "slippageBps": str(slippage_bps),
            }
            
            # Retry up to 3 times
            max_retries = 3
            quote_data = None
            for attempt in range(max_retries):
                try:
                    quote_response = requests.get(
                        quote_url, 
                        params=quote_params, 
                        timeout=15,
                        headers={'User-Agent': 'Mozilla/5.0'}
                    )
                    quote_response.raise_for_status()
                    quote_data = quote_response.json()
                    break  # Success
                except (requests.exceptions.ConnectionError, 
                        requests.exceptions.Timeout,
                        requests.exceptions.RequestException) as e:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"Jupiter quote request failed (attempt {attempt + 1}/{max_retries}): {e}")
                        logger.info(f"Retrying in {wait_time}s...")
                        time_module.sleep(wait_time)
                    else:
                        raise Exception(f"Jupiter API unavailable after {max_retries} attempts: {e}")
            
            if not quote_data or "outAmount" not in quote_data:
                raise Exception(f"Invalid quote response: {quote_data}")
            
            expected_out_lamports = int(quote_data["outAmount"])
            expected_out_sol = expected_out_lamports / LAMPORTS_PER_SOL
            
            logger.info(f"Expected output: {expected_out_sol:.6f} {self.base_symbol}")
            
            # Step 2: Get swap transaction from Jupiter with retry logic
            swap_url = "https://lite-api.jup.ag/swap/v1/swap"
            swap_payload = {
                "quoteResponse": quote_data,
                "userPublicKey": str(self.keypair.pubkey()),
                "wrapAndUnwrapSol": True,
                "dynamicComputeUnitLimit": True,
            }
            
            # Retry swap request
            swap_data = None
            for attempt in range(max_retries):
                try:
                    swap_response = requests.post(
                        swap_url, 
                        json=swap_payload, 
                        timeout=15,
                        headers={'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json'}
                    )
                    swap_response.raise_for_status()
                    swap_data = swap_response.json()
                    break  # Success
                except (requests.exceptions.ConnectionError, 
                        requests.exceptions.Timeout,
                        requests.exceptions.RequestException) as e:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"Jupiter swap request failed (attempt {attempt + 1}/{max_retries}): {e}")
                        logger.info(f"Retrying in {wait_time}s...")
                        time_module.sleep(wait_time)
                    else:
                        raise Exception(f"Jupiter API unavailable after {max_retries} attempts: {e}")
            
            if not swap_data or "swapTransaction" not in swap_data:
                raise Exception(f"Invalid swap response: {swap_data}")
            
            # Step 3: Decode and sign transaction
            swap_transaction_bytes = base64.b64decode(swap_data["swapTransaction"])
            
            # Deserialize versioned transaction (Jupiter uses versioned transactions)
            raw_transaction = VersionedTransaction.from_bytes(swap_transaction_bytes)
            
            # Sign the transaction message with our keypair
            tx_signature = self.keypair.sign_message(to_bytes_versioned(raw_transaction.message))
            
            # Populate transaction with signature
            signed_transaction = VersionedTransaction.populate(raw_transaction.message, [tx_signature])
            
            # Step 4: Send transaction
            signature_str = self._send_transaction(signed_transaction)
            
            logger.info(f"SELL swap successful: {signature_str}")
            
            # Step 5: Return result
            actual_amount_in = token_amount
            actual_amount_out = expected_out_sol  # Actual would be parsed from logs
            
            return {
                'amount_in': actual_amount_in,
                'amount_out': actual_amount_out,
                'tx_hash': signature_str,
                'slot': None,
                'gas_used': 50000,  # Solana compute units (estimated)
                'gas_price_gwei': 0.000005  # Solana transaction fee (~5000 lamports)
            }
            
        except Exception as e:
            logger.error(f"SELL swap failed: {e}")
            raise Exception(f"Failed to execute SELL swap: {str(e)}")
    
    def _send_transaction(self, transaction: VersionedTransaction) -> str:
        """
        Send a versioned transaction to Solana network.
        
        Args:
            transaction: The versioned transaction to send
        
        Returns:
            Transaction signature (string)
        """
        try:
            # Send versioned transaction with proper TxOpts
            opts = TxOpts(
                skip_preflight=config.SKIP_PREFLIGHT,
                preflight_commitment=self.commitment,
                max_retries=config.MAX_RETRIES
            )
            
            response = self.client.send_raw_transaction(
                bytes(transaction),
                opts=opts
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

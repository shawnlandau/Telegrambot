"""
DEX Client for interacting with Uniswap V2-style routers via web3.py.
Handles token swaps, balance queries, and price estimation.
"""

import logging
import json
import os
import time
from typing import Dict, Tuple, Optional, Any
from decimal import Decimal

from web3 import Web3
from web3.contract import Contract
from web3.exceptions import ContractLogicError, TimeExhausted
from eth_account import Account

from .config import config

logger = logging.getLogger(__name__)


class DexClient:
    """
    Client for interacting with DEX router contracts.
    Manages web3 connection, token contracts, and swap execution.
    """
    
    def __init__(self):
        """Initialize web3 connection and load contracts."""
        # Connect to EVM node with timeout
        self.w3 = Web3(
            Web3.HTTPProvider(
                config.RPC_URL,
                request_kwargs={'timeout': config.RPC_TIMEOUT}
            )
        )
        if not self._connect_with_retry():
            raise ConnectionError(f"Failed to connect to RPC endpoint: {config.RPC_URL}")
        
        logger.info(f"Connected to network, chain ID: {self.w3.eth.chain_id}")
        
        # Load wallet
        self.account = Account.from_key(config.WALLET_PRIVATE_KEY)
        self.wallet_address = self.account.address
        logger.info(f"Loaded wallet: {self.wallet_address}")
        
        # Load ABIs
        router_abi = self._load_abi("uniswap_v2_router.json")
        erc20_abi = self._load_abi("erc20.json")
        
        # Initialize contracts
        self.router = self.w3.eth.contract(
            address=Web3.to_checksum_address(config.DEX_ROUTER_ADDRESS),
            abi=router_abi
        )
        
        self.base_token = self.w3.eth.contract(
            address=Web3.to_checksum_address(config.BASE_TOKEN_ADDRESS),
            abi=erc20_abi
        )
        
        self.quote_token = self.w3.eth.contract(
            address=Web3.to_checksum_address(config.QUOTE_TOKEN_ADDRESS),
            abi=erc20_abi
        )
        
        # Get token decimals
        self.base_decimals = self.base_token.functions.decimals().call()
        self.quote_decimals = self.quote_token.functions.decimals().call()
        
        logger.info(f"Base token decimals: {self.base_decimals}")
        logger.info(f"Quote token decimals: {self.quote_decimals}")
        
        # Cache token symbols for logging
        try:
            self.base_symbol = self.base_token.functions.symbol().call()
            self.quote_symbol = self.quote_token.functions.symbol().call()
        except Exception as e:
            logger.warning(f"Could not fetch token symbols: {e}")
            self.base_symbol = "BASE"
            self.quote_symbol = "QUOTE"
    
    def _connect_with_retry(self) -> bool:
        """Connect to RPC with retry logic."""
        for attempt in range(config.RPC_MAX_RETRIES):
            try:
                if self.w3.is_connected():
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
            except (ConnectionError, TimeExhausted, Exception) as e:
                last_exception = e
                logger.warning(f"RPC call attempt {attempt + 1}/{config.RPC_MAX_RETRIES} failed: {e}")
                if attempt < config.RPC_MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        raise last_exception
    
    def _load_abi(self, filename: str) -> list:
        """Load contract ABI from file."""
        abi_path = os.path.join(os.path.dirname(__file__), "abi", filename)
        try:
            with open(abi_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"ABI file not found: {abi_path}. "
                f"Please ensure ABI files are in the bot/abi/ directory."
            )
    
    def get_balances(self) -> Dict[str, float]:
        """
        Get current token balances for the wallet.
        Returns balances adjusted for decimals.
        """
        try:
            base_raw = self._rpc_call_with_retry(
                lambda: self.base_token.functions.balanceOf(self.wallet_address).call()
            )
            quote_raw = self._rpc_call_with_retry(
                lambda: self.quote_token.functions.balanceOf(self.wallet_address).call()
            )
            
            base_balance = float(base_raw) / (10 ** self.base_decimals)
            quote_balance = float(quote_raw) / (10 ** self.quote_decimals)
            
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
    
    def get_price(self) -> float:
        """
        Get approximate current price (quote per base).
        Uses router's getAmountsOut for a small test amount.
        """
        try:
            # Use 1 unit of base token for price estimation
            amount_in = 10 ** self.base_decimals
            
            amounts = self._rpc_call_with_retry(
                lambda: self.router.functions.getAmountsOut(
                    amount_in,
                    [config.BASE_TOKEN_ADDRESS, config.QUOTE_TOKEN_ADDRESS]
                ).call()
            )
            
            # amounts[1] is quote out for 1 base in
            price = float(amounts[1]) / (10 ** self.quote_decimals)
            
            logger.debug(f"Current price: {price:.6f} {self.quote_symbol}/{self.base_symbol}")
            return price
            
        except Exception as e:
            logger.error(f"Failed to get price: {e}")
            raise
    
    def ensure_allowance(self, token_address: str, amount: int) -> Optional[str]:
        """
        Check token allowance to router and approve if needed.
        Returns transaction hash if approval was sent, None otherwise.
        """
        token_address = Web3.to_checksum_address(token_address)
        router_address = Web3.to_checksum_address(config.DEX_ROUTER_ADDRESS)
        
        # Get token contract
        token = self.w3.eth.contract(
            address=token_address,
            abi=self._load_abi("erc20.json")
        )
        
        # Check current allowance with retry
        current_allowance = self._rpc_call_with_retry(
            lambda: token.functions.allowance(
                self.wallet_address,
                router_address
            ).call()
        )
        
        if current_allowance >= amount:
            logger.debug(f"Sufficient allowance already exists: {current_allowance}")
            return None
        
        # Need to approve
        logger.info(f"Approving {token_address} for router...")
        
        # Approve max uint256 to avoid repeated approvals
        max_approval = 2**256 - 1
        
        approve_tx = token.functions.approve(
            router_address,
            max_approval
        ).build_transaction({
            'from': self.wallet_address,
            'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
            'gas': config.GAS_LIMIT,
            'gasPrice': self._get_gas_price(),
        })
        
        # Sign and send
        signed_tx = self.account.sign_transaction(approve_tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Wait for confirmation
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        
        if receipt['status'] != 1:
            raise Exception(f"Approval transaction failed: {tx_hash.hex()}")
        
        logger.info(f"Approval successful: {tx_hash.hex()}")
        return tx_hash.hex()
    
    def _parse_swap_amounts_from_receipt(
        self,
        receipt: Dict,
        token_in_address: str,
        token_out_address: str
    ) -> Tuple[int, int]:
        """
        Parse actual swap amounts from transaction receipt Transfer events.
        
        Args:
            receipt: Transaction receipt
            token_in_address: Address of input token (being spent)
            token_out_address: Address of output token (being received)
        
        Returns:
            Tuple of (actual_amount_in, actual_amount_out) in raw token units
        """
        token_in_address = Web3.to_checksum_address(token_in_address)
        token_out_address = Web3.to_checksum_address(token_out_address)
        wallet_address = Web3.to_checksum_address(self.wallet_address)
        
        # Load ERC20 ABI to decode Transfer events
        erc20_abi = self._load_abi("erc20.json")
        
        # Get Transfer event signature
        transfer_event_signature_hash = self.w3.keccak(text="Transfer(address,address,uint256)")
        
        actual_amount_in = None
        actual_amount_out = None
        
        # Store all matching transfers in case there are multiple (shouldn't happen, but be safe)
        input_transfers = []
        output_transfers = []
        
        # Parse all logs in the receipt
        for log in receipt.get('logs', []):
            # Check if this is a Transfer event (should have 3 topics: signature, from, to)
            topics = log.get('topics', [])
            if len(topics) != 3:
                continue
            
            # Compare event signature (handle both HexBytes and hex strings)
            topic0 = topics[0]
            if hasattr(topic0, 'hex'):
                topic0_hash = topic0.hex()
            elif isinstance(topic0, bytes):
                topic0_hash = topic0.hex()
            else:
                topic0_hash = str(topic0)
            
            if hasattr(transfer_event_signature_hash, 'hex'):
                sig_hash = transfer_event_signature_hash.hex()
            elif isinstance(transfer_event_signature_hash, bytes):
                sig_hash = transfer_event_signature_hash.hex()
            else:
                sig_hash = str(transfer_event_signature_hash)
            
            if topic0_hash.lower() != sig_hash.lower():
                continue
            
            # Decode Transfer event: Transfer(address indexed from, address indexed to, uint256 value)
            # Topics contain indexed parameters - extract addresses from them
            from_topic = topics[1]
            to_topic = topics[2]
            
            # Extract addresses from topics (handle both HexBytes and hex strings)
            # Addresses are stored as 32-byte values (last 20 bytes are the address)
            try:
                if hasattr(from_topic, 'hex'):
                    from_address = Web3.to_checksum_address('0x' + from_topic.hex()[-40:])
                elif isinstance(from_topic, bytes):
                    from_address = Web3.to_checksum_address('0x' + from_topic.hex()[-40:])
                else:
                    from_hex = str(from_topic).replace('0x', '')[-40:]
                    from_address = Web3.to_checksum_address('0x' + from_hex)
                
                if hasattr(to_topic, 'hex'):
                    to_address = Web3.to_checksum_address('0x' + to_topic.hex()[-40:])
                elif isinstance(to_topic, bytes):
                    to_address = Web3.to_checksum_address('0x' + to_topic.hex()[-40:])
                else:
                    to_hex = str(to_topic).replace('0x', '')[-40:]
                    to_address = Web3.to_checksum_address('0x' + to_hex)
            except Exception as e:
                logger.warning(f"Failed to extract addresses from topics: {e}")
                continue
            
            # Decode the value (non-indexed parameter)
            try:
                token_contract = self.w3.eth.contract(address=log['address'], abi=erc20_abi)
                transfer_event = token_contract.events.Transfer()
                decoded_log = transfer_event.process_log(log)
                value = decoded_log['args']['value']
            except Exception as e:
                logger.warning(f"Failed to decode Transfer event from {log['address']}: {e}")
                continue
            
            token_address = Web3.to_checksum_address(log['address'])
            
            # Check if this is our input token being sent FROM our wallet
            if token_address == token_in_address and from_address == wallet_address:
                input_transfers.append(value)
                logger.debug(f"Found input token transfer: {value} from {token_in_address} to {to_address}")
            
            # Check if this is our output token being received TO our wallet
            if token_address == token_out_address and to_address == wallet_address:
                output_transfers.append(value)
                logger.debug(f"Found output token transfer: {value} from {from_address} to {wallet_address}")
        
        # Take the largest transfer if multiple found (should only be one, but be safe)
        if input_transfers:
            actual_amount_in = max(input_transfers)
            if len(input_transfers) > 1:
                logger.warning(f"Found {len(input_transfers)} input transfers, using largest: {actual_amount_in}")
        
        if output_transfers:
            actual_amount_out = max(output_transfers)
            if len(output_transfers) > 1:
                logger.warning(f"Found {len(output_transfers)} output transfers, using largest: {actual_amount_out}")
        
        # Validate that we found both amounts
        if actual_amount_in is None or actual_amount_out is None:
            logger.error(
                f"Could not parse actual amounts from receipt. "
                f"In: {actual_amount_in}, Out: {actual_amount_out}. "
                f"Expected input token: {token_in_address}, output token: {token_out_address}. "
                f"Wallet: {wallet_address}. "
                f"Found {len(input_transfers)} input transfers and {len(output_transfers)} output transfers."
            )
            # Return None to indicate parsing failed
            return None, None
        
        # Validate amounts are reasonable (not zero, positive)
        if actual_amount_in <= 0 or actual_amount_out <= 0:
            logger.error(
                f"Parsed amounts are invalid: In={actual_amount_in}, Out={actual_amount_out}. "
                f"Both must be positive."
            )
            return None, None
        
        logger.info(
            f"Successfully parsed actual swap amounts: "
            f"In={actual_amount_in}, Out={actual_amount_out}"
        )
        
        return actual_amount_in, actual_amount_out
    
    def swap_exact_quote_for_base(
        self,
        notional_quote: float,
        slippage_bps: int
    ) -> Dict[str, any]:
        """
        BUY: Swap exact quote tokens for base tokens.
        
        Args:
            notional_quote: Amount of quote token to spend (in human-readable units)
            slippage_bps: Slippage tolerance in basis points (e.g., 50 = 0.5%)
        
        Returns:
            dict with 'amount_in', 'amount_out', 'tx_hash', 'gas_used', 'gas_price_gwei'
        """
        logger.info(f"BUY: Swapping {notional_quote} {self.quote_symbol} for {self.base_symbol}")
        
        # Convert to token units
        amount_in = int(notional_quote * (10 ** self.quote_decimals))
        
        # Ensure allowance
        self.ensure_allowance(config.QUOTE_TOKEN_ADDRESS, amount_in)
        
        # Get expected output amount with retry
        amounts = self._rpc_call_with_retry(
            lambda: self.router.functions.getAmountsOut(
                amount_in,
                [config.QUOTE_TOKEN_ADDRESS, config.BASE_TOKEN_ADDRESS]
            ).call()
        )
        
        expected_out = amounts[1]
        
        # Calculate minimum output with slippage
        slippage_multiplier = Decimal(10000 - slippage_bps) / Decimal(10000)
        amount_out_min = int(Decimal(expected_out) * slippage_multiplier)
        
        logger.info(
            f"Expected: {float(expected_out) / (10 ** self.base_decimals):.6f} {self.base_symbol}, "
            f"Min: {float(amount_out_min) / (10 ** self.base_decimals):.6f} {self.base_symbol}"
        )
        
        # Build swap transaction
        deadline = self.w3.eth.get_block('latest')['timestamp'] + 300  # 5 min deadline
        
        swap_tx = self.router.functions.swapExactTokensForTokens(
            amount_in,
            amount_out_min,
            [config.QUOTE_TOKEN_ADDRESS, config.BASE_TOKEN_ADDRESS],
            self.wallet_address,
            deadline
        ).build_transaction({
            'from': self.wallet_address,
            'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
            'gas': config.GAS_LIMIT,
            'gasPrice': self._get_gas_price(),
        })
        
        # Sign and send
        signed_tx = self.account.sign_transaction(swap_tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        logger.info(f"BUY transaction sent: {tx_hash.hex()}")
        
        # Wait for confirmation
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        
        if receipt['status'] != 1:
            raise Exception(f"Swap transaction failed: {tx_hash.hex()}")
        
        # Parse actual amounts from transaction logs
        actual_amount_in_raw, actual_amount_out_raw = self._parse_swap_amounts_from_receipt(
            receipt,
            config.QUOTE_TOKEN_ADDRESS,
            config.BASE_TOKEN_ADDRESS
        )
        
        # Use parsed amounts if available, otherwise fall back to expected (shouldn't happen)
        if actual_amount_in_raw is not None and actual_amount_out_raw is not None:
            actual_in = float(actual_amount_in_raw) / (10 ** self.quote_decimals)
            actual_out = float(actual_amount_out_raw) / (10 ** self.base_decimals)
            logger.info(f"Parsed actual amounts: {actual_in:.6f} {self.quote_symbol} -> {actual_out:.6f} {self.base_symbol}")
        else:
            # Fallback to expected amounts (CRITICAL: This should not happen in production)
            logger.error(
                f"⚠️ CRITICAL: Could not parse actual amounts from transaction {tx_hash.hex()}. "
                f"Using expected amounts instead. This indicates a problem with log parsing. "
                f"Expected: {float(amount_in) / (10 ** self.quote_decimals):.6f} {self.quote_symbol} -> "
                f"{float(expected_out) / (10 ** self.base_decimals):.6f} {self.base_symbol}. "
                f"Transaction was successful but amounts may be inaccurate."
            )
            actual_in = float(amount_in) / (10 ** self.quote_decimals)
            actual_out = float(expected_out) / (10 ** self.base_decimals)
        
        gas_used = receipt['gasUsed']
        gas_price_gwei = float(receipt['effectiveGasPrice']) / 1e9
        
        result = {
            'amount_in': actual_in,
            'amount_out': actual_out,
            'tx_hash': tx_hash.hex(),
            'gas_used': gas_used,
            'gas_price_gwei': gas_price_gwei,
        }
        
        logger.info(
            f"BUY successful: {result['amount_out']:.6f} {self.base_symbol} "
            f"for {result['amount_in']:.6f} {self.quote_symbol}"
        )
        
        return result
    
    def swap_exact_base_for_quote(
        self,
        notional_quote_equiv: float,
        slippage_bps: int
    ) -> Dict[str, any]:
        """
        SELL: Swap base tokens for quote tokens.
        
        Args:
            notional_quote_equiv: Approximate quote value to sell (in human-readable units)
            slippage_bps: Slippage tolerance in basis points
        
        Returns:
            dict with 'amount_in', 'amount_out', 'tx_hash', 'gas_used', 'gas_price_gwei'
        """
        logger.info(f"SELL: Swapping ~{notional_quote_equiv} {self.quote_symbol} worth of {self.base_symbol}")
        
        # Estimate base amount needed using current price
        price = self.get_price()
        base_amount = notional_quote_equiv / price
        amount_in = int(base_amount * (10 ** self.base_decimals))
        
        # Ensure allowance
        self.ensure_allowance(config.BASE_TOKEN_ADDRESS, amount_in)
        
        # Get expected output amount with retry
        amounts = self._rpc_call_with_retry(
            lambda: self.router.functions.getAmountsOut(
                amount_in,
                [config.BASE_TOKEN_ADDRESS, config.QUOTE_TOKEN_ADDRESS]
            ).call()
        )
        
        expected_out = amounts[1]
        
        # Calculate minimum output with slippage
        slippage_multiplier = Decimal(10000 - slippage_bps) / Decimal(10000)
        amount_out_min = int(Decimal(expected_out) * slippage_multiplier)
        
        logger.info(
            f"Selling {float(amount_in) / (10 ** self.base_decimals):.6f} {self.base_symbol}, "
            f"Expected: {float(expected_out) / (10 ** self.quote_decimals):.6f} {self.quote_symbol}, "
            f"Min: {float(amount_out_min) / (10 ** self.quote_decimals):.6f} {self.quote_symbol}"
        )
        
        # Build swap transaction
        deadline = self.w3.eth.get_block('latest')['timestamp'] + 300
        
        swap_tx = self.router.functions.swapExactTokensForTokens(
            amount_in,
            amount_out_min,
            [config.BASE_TOKEN_ADDRESS, config.QUOTE_TOKEN_ADDRESS],
            self.wallet_address,
            deadline
        ).build_transaction({
            'from': self.wallet_address,
            'nonce': self.w3.eth.get_transaction_count(self.wallet_address),
            'gas': config.GAS_LIMIT,
            'gasPrice': self._get_gas_price(),
        })
        
        # Sign and send
        signed_tx = self.account.sign_transaction(swap_tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        logger.info(f"SELL transaction sent: {tx_hash.hex()}")
        
        # Wait for confirmation
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        
        if receipt['status'] != 1:
            raise Exception(f"Swap transaction failed: {tx_hash.hex()}")
        
        # Parse actual amounts from transaction logs
        actual_amount_in_raw, actual_amount_out_raw = self._parse_swap_amounts_from_receipt(
            receipt,
            config.BASE_TOKEN_ADDRESS,
            config.QUOTE_TOKEN_ADDRESS
        )
        
        # Use parsed amounts if available, otherwise fall back to expected (shouldn't happen)
        if actual_amount_in_raw is not None and actual_amount_out_raw is not None:
            actual_in = float(actual_amount_in_raw) / (10 ** self.base_decimals)
            actual_out = float(actual_amount_out_raw) / (10 ** self.quote_decimals)
            logger.info(f"Parsed actual amounts: {actual_in:.6f} {self.base_symbol} -> {actual_out:.6f} {self.quote_symbol}")
        else:
            # Fallback to expected amounts (CRITICAL: This should not happen in production)
            logger.error(
                f"⚠️ CRITICAL: Could not parse actual amounts from transaction {tx_hash.hex()}. "
                f"Using expected amounts instead. This indicates a problem with log parsing. "
                f"Expected: {float(amount_in) / (10 ** self.base_decimals):.6f} {self.base_symbol} -> "
                f"{float(expected_out) / (10 ** self.quote_decimals):.6f} {self.quote_symbol}. "
                f"Transaction was successful but amounts may be inaccurate."
            )
            actual_in = float(amount_in) / (10 ** self.base_decimals)
            actual_out = float(expected_out) / (10 ** self.quote_decimals)
        
        gas_used = receipt['gasUsed']
        gas_price_gwei = float(receipt['effectiveGasPrice']) / 1e9
        
        result = {
            'amount_in': actual_in,
            'amount_out': actual_out,
            'tx_hash': tx_hash.hex(),
            'gas_used': gas_used,
            'gas_price_gwei': gas_price_gwei,
        }
        
        logger.info(
            f"SELL successful: {result['amount_in']:.6f} {self.base_symbol} "
            f"for {result['amount_out']:.6f} {self.quote_symbol}"
        )
        
        return result
    
    def _get_gas_price(self) -> int:
        """Get gas price in wei."""
        if config.GAS_PRICE_GWEI:
            return self.w3.to_wei(config.GAS_PRICE_GWEI, 'gwei')
        else:
            return self.w3.eth.gas_price

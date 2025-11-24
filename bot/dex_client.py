"""
DEX Client for interacting with Uniswap V2-style routers via web3.py.
Handles token swaps, balance queries, and price estimation.
"""

import logging
import json
import os
from typing import Dict, Tuple, Optional
from decimal import Decimal

from web3 import Web3
from web3.contract import Contract
from web3.exceptions import ContractLogicError
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
        # Connect to EVM node
        self.w3 = Web3(Web3.HTTPProvider(config.RPC_URL))
        if not self.w3.is_connected():
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
            base_raw = self.base_token.functions.balanceOf(self.wallet_address).call()
            quote_raw = self.quote_token.functions.balanceOf(self.wallet_address).call()
            
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
            
            amounts = self.router.functions.getAmountsOut(
                amount_in,
                [config.BASE_TOKEN_ADDRESS, config.QUOTE_TOKEN_ADDRESS]
            ).call()
            
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
        
        # Check current allowance
        current_allowance = token.functions.allowance(
            self.wallet_address,
            router_address
        ).call()
        
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
        
        # Get expected output amount
        amounts = self.router.functions.getAmountsOut(
            amount_in,
            [config.QUOTE_TOKEN_ADDRESS, config.BASE_TOKEN_ADDRESS]
        ).call()
        
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
        
        # Parse actual amounts from logs (simplified - using expected)
        actual_out = expected_out
        
        gas_used = receipt['gasUsed']
        gas_price_gwei = float(receipt['effectiveGasPrice']) / 1e9
        
        result = {
            'amount_in': float(amount_in) / (10 ** self.quote_decimals),
            'amount_out': float(actual_out) / (10 ** self.base_decimals),
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
        
        # Get expected output amount
        amounts = self.router.functions.getAmountsOut(
            amount_in,
            [config.BASE_TOKEN_ADDRESS, config.QUOTE_TOKEN_ADDRESS]
        ).call()
        
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
        
        # Parse actual amounts from logs (simplified - using expected)
        actual_out = expected_out
        
        gas_used = receipt['gasUsed']
        gas_price_gwei = float(receipt['effectiveGasPrice']) / 1e9
        
        result = {
            'amount_in': float(amount_in) / (10 ** self.base_decimals),
            'amount_out': float(actual_out) / (10 ** self.quote_decimals),
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

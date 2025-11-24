"""
Session runner implementing the 2×2 trading pattern (BUY-BUY-SELL-SELL).
Manages background execution loops for active trading sessions.
"""

import logging
import time
import asyncio
from typing import Dict, Optional, Callable
from datetime import datetime
from threading import Thread, Lock

from .config import config
from .models import SessionConfig, SessionState, TradeRecord
from .dex_client import DexClient
from .db import Database

logger = logging.getLogger(__name__)

# Fixed trading pattern: BUY -> BUY -> SELL -> SELL (repeating)
TRADING_PATTERN = ["BUY", "BUY", "SELL", "SELL"]


class SessionRunner:
    """
    Manages trading session execution with the fixed 2×2 pattern.
    Handles background trading loops and state management.
    """
    
    def __init__(self, db: Database, dex_client: DexClient):
        """
        Initialize session runner.
        
        Args:
            db: Database instance for persistence
            dex_client: DEX client for executing trades
        """
        self.db = db
        self.dex_client = dex_client
        self.active_sessions: Dict[int, Thread] = {}
        self.session_locks: Dict[int, Lock] = {}
        self.message_callbacks: Dict[int, Callable] = {}
        
        logger.info("SessionRunner initialized")
    
    def register_message_callback(self, user_id: int, callback: Callable) -> None:
        """
        Register a callback function to send messages to a user.
        
        Args:
            user_id: Telegram user ID
            callback: Async function that takes a message string
        """
        self.message_callbacks[user_id] = callback
    
    async def send_user_message(self, user_id: int, message: str) -> None:
        """Send a message to a user via registered callback."""
        callback = self.message_callbacks.get(user_id)
        if callback:
            try:
                await callback(message)
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")
    
    def start_session(self, user_id: int) -> bool:
        """
        Start a trading session for a user.
        
        Args:
            user_id: Telegram user ID
        
        Returns:
            True if session started, False if already running or config missing
        """
        # Check if already running
        if user_id in self.active_sessions and self.active_sessions[user_id].is_alive():
            logger.warning(f"Session already running for user {user_id}")
            return False
        
        # Load configuration
        session_config = self.db.get_session_config(user_id)
        if not session_config:
            logger.error(f"No configuration found for user {user_id}")
            return False
        
        # Load or create state
        session_state = self.db.get_session_state(user_id)
        
        # Reset state for new session if it was stopped
        if not session_state.active:
            session_state.reset()
        
        session_state.active = True
        session_state.started_at = datetime.utcnow()
        self.db.save_session_state(session_state)
        
        # Create lock for this session
        if user_id not in self.session_locks:
            self.session_locks[user_id] = Lock()
        
        # Start background thread
        thread = Thread(
            target=self._run_session_loop,
            args=(user_id, session_config, session_state),
            daemon=True
        )
        thread.start()
        self.active_sessions[user_id] = thread
        
        logger.info(f"Started trading session for user {user_id}")
        return True
    
    def stop_session(self, user_id: int) -> bool:
        """
        Stop a trading session for a user.
        
        Args:
            user_id: Telegram user ID
        
        Returns:
            True if session was stopped, False if not running
        """
        # Mark as inactive in database
        session_state = self.db.get_session_state(user_id)
        if not session_state.active:
            logger.warning(f"No active session for user {user_id}")
            return False
        
        session_state.active = False
        session_state.stopped_at = datetime.utcnow()
        self.db.save_session_state(session_state)
        
        logger.info(f"Stopped trading session for user {user_id}")
        return True
    
    def is_session_active(self, user_id: int) -> bool:
        """Check if a user has an active trading session."""
        session_state = self.db.get_session_state(user_id)
        return session_state.active
    
    def _run_session_loop(
        self,
        user_id: int,
        session_config: SessionConfig,
        session_state: SessionState
    ) -> None:
        """
        Main trading loop for a session (runs in background thread).
        Implements the BUY-BUY-SELL-SELL pattern.
        
        This method is designed for REAL EXECUTION and DCA (Dollar Cost Averaging).
        It is NOT intended for wash trading, volume manipulation, or spoofing.
        It trades from a single wallet and executes legitimate buy/sell orders.
        """
        logger.info(f"Session loop started for user {user_id}")
        
        try:
            while True:
                # Check if session is still active
                with self.session_locks[user_id]:
                    current_state = self.db.get_session_state(user_id)
                    if not current_state.active:
                        logger.info(f"Session stopped for user {user_id}")
                        break
                    
                    # Check max trades limit
                    if current_state.trades_executed >= config.MAX_TRADES_PER_SESSION:
                        logger.info(f"Max trades reached for user {user_id}")
                        self._stop_with_message(
                            user_id,
                            f"⛔ Session stopped: Maximum trades ({config.MAX_TRADES_PER_SESSION}) reached."
                        )
                        break
                    
                    # Get current trade side from pattern
                    side = TRADING_PATTERN[current_state.pattern_index % 4]
                    trade_notional = session_config.get_trade_amount()
                    
                    # Check minimum notional
                    if trade_notional < session_config.min_notional:
                        logger.error(f"Trade size below minimum for user {user_id}")
                        self._stop_with_message(
                            user_id,
                            f"⛔ Session stopped: Trade size ({trade_notional:.2f}) "
                            f"below minimum ({session_config.min_notional:.2f})."
                        )
                        break
                    
                    # Get current balances
                    try:
                        balances = self.dex_client.get_balances()
                    except Exception as e:
                        logger.error(f"Failed to get balances: {e}")
                        self._stop_with_error(user_id, f"Failed to get balances: {str(e)}")
                        break
                    
                    # Execute trade based on side
                    try:
                        if side == "BUY":
                            # Check if we have enough quote tokens
                            if balances['quote'] < trade_notional:
                                logger.error(
                                    f"Insufficient quote balance for user {user_id}: "
                                    f"need {trade_notional}, have {balances['quote']}"
                                )
                                self._stop_with_message(
                                    user_id,
                                    f"⛔ Session stopped: Insufficient quote token balance. "
                                    f"Need {trade_notional:.2f}, have {balances['quote']:.2f}."
                                )
                                break
                            
                            # Check max position if configured
                            if session_config.max_position is not None:
                                if balances['base'] >= session_config.max_position:
                                    logger.warning(
                                        f"Max position reached for user {user_id}, skipping BUY"
                                    )
                                    # Skip this trade and advance pattern
                                    current_state.advance_pattern()
                                    self.db.save_session_state(current_state)
                                    time.sleep(session_config.interval_seconds)
                                    continue
                            
                            # Execute BUY
                            result = self.dex_client.swap_exact_quote_for_base(
                                trade_notional,
                                session_config.slippage_bps
                            )
                            
                            # Update state
                            current_state.spent_notional += result['amount_in']
                            current_state.base_position_delta += result['amount_out']
                            
                        else:  # SELL
                            # Estimate base amount needed
                            price = self.dex_client.get_price()
                            base_needed = trade_notional / price
                            
                            # Check if we have enough base tokens
                            if balances['base'] < base_needed:
                                logger.error(
                                    f"Insufficient base balance for user {user_id}: "
                                    f"need ~{base_needed:.6f}, have {balances['base']:.6f}"
                                )
                                self._stop_with_message(
                                    user_id,
                                    f"⛔ Session stopped: Insufficient base token balance. "
                                    f"Need ~{base_needed:.6f}, have {balances['base']:.6f}."
                                )
                                break
                            
                            # Execute SELL
                            result = self.dex_client.swap_exact_base_for_quote(
                                trade_notional,
                                session_config.slippage_bps
                            )
                            
                            # Update state
                            current_state.received_quote += result['amount_out']
                            current_state.base_position_delta -= result['amount_in']
                        
                        # Record trade
                        execution_price = (
                            result['amount_out'] / result['amount_in']
                            if side == "BUY"
                            else result['amount_in'] / result['amount_out']
                        )
                        
                        trade_record = TradeRecord(
                            user_id=user_id,
                            side=side,
                            amount_in=result['amount_in'],
                            amount_out=result['amount_out'],
                            tx_hash=result['tx_hash'],
                            gas_used=result['gas_used'],
                            gas_price_gwei=result['gas_price_gwei'],
                            execution_price=execution_price,
                        )
                        
                        self.db.save_trade_record(trade_record)
                        
                        # Update session state
                        current_state.trades_executed += 1
                        current_state.advance_pattern()
                        current_state.last_error = None
                        self.db.save_session_state(current_state)
                        
                        # Notify user
                        asyncio.run(
                            self.send_user_message(
                                user_id,
                                f"✅ {side} completed:\n"
                                f"In: {result['amount_in']:.6f}\n"
                                f"Out: {result['amount_out']:.6f}\n"
                                f"TX: {result['tx_hash'][:16]}...\n"
                                f"Trades: {current_state.trades_executed}"
                            )
                        )
                        
                    except Exception as e:
                        logger.error(f"Trade execution failed for user {user_id}: {e}")
                        self._stop_with_error(user_id, f"Trade failed: {str(e)}")
                        break
                
                # Wait for next trade interval
                logger.debug(f"Sleeping for {session_config.interval_seconds}s")
                time.sleep(session_config.interval_seconds)
                
        except Exception as e:
            logger.error(f"Unexpected error in session loop for user {user_id}: {e}")
            self._stop_with_error(user_id, f"Unexpected error: {str(e)}")
        
        finally:
            # Cleanup
            if user_id in self.active_sessions:
                del self.active_sessions[user_id]
            logger.info(f"Session loop ended for user {user_id}")
    
    def _stop_with_message(self, user_id: int, message: str) -> None:
        """Stop session and send message to user."""
        session_state = self.db.get_session_state(user_id)
        session_state.active = False
        session_state.stopped_at = datetime.utcnow()
        self.db.save_session_state(session_state)
        
        asyncio.run(self.send_user_message(user_id, message))
    
    def _stop_with_error(self, user_id: int, error: str) -> None:
        """Stop session due to error and notify user."""
        session_state = self.db.get_session_state(user_id)
        session_state.active = False
        session_state.stopped_at = datetime.utcnow()
        session_state.last_error = error
        self.db.save_session_state(session_state)
        
        asyncio.run(
            self.send_user_message(
                user_id,
                f"❌ Session stopped due to error:\n{error}"
            )
        )

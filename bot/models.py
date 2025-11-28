"""
Data models for the DEX Bot MVP.
Defines dataclasses and database schema for session configuration and state.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class SessionConfig:
    """
    Configuration for a user's trading session.
    Defines the parameters for how trades should be executed.
    """
    user_id: int
    total_liquidity: float  # Total liquidity in quote token (e.g., USDC)
    trade_pct: float  # Percentage of total_liquidity per trade (e.g., 2.0 = 2%)
    interval_seconds: int  # Time delay between trades
    slippage_bps: int = 50  # Slippage tolerance in basis points (50 = 0.5%)
    min_notional: float = 10.0  # Minimum quote token amount per trade
    max_position: Optional[float] = None  # Optional maximum base token position
    
    def __post_init__(self):
        """Validate configuration values."""
        if self.total_liquidity <= 0:
            raise ValueError("total_liquidity must be positive")
        if not (0 < self.trade_pct <= 100):
            raise ValueError("trade_pct must be between 0 and 100")
        if self.interval_seconds < 1:
            raise ValueError("interval_seconds must be at least 1")
        if self.slippage_bps < 0 or self.slippage_bps > 10000:
            raise ValueError("slippage_bps must be between 0 and 10000")
        if self.min_notional < 0:
            raise ValueError("min_notional must be non-negative")
    
    def get_trade_amount(self) -> float:
        """Calculate the quote token amount for a single trade."""
        return self.total_liquidity * (self.trade_pct / 100.0)


@dataclass
class SessionState:
    """
    Runtime state of a user's trading session.
    Tracks execution progress and accumulated statistics.
    """
    user_id: int
    active: bool = False
    trades_executed: int = 0
    spent_notional: float = 0.0  # Total quote spent on BUY trades
    received_quote: float = 0.0  # Total quote received from SELL trades
    base_position_delta: float = 0.0  # Net base tokens gained/lost
    pattern_index: int = 0  # Current position in the BUY-BUY-SELL-SELL pattern (0-3)
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    last_error: Optional[str] = None
    
    def get_net_quote(self) -> float:
        """Calculate net quote token profit/loss."""
        return self.received_quote - self.spent_notional
    
    def get_current_side(self) -> str:
        """Get the current trade side based on pattern_index."""
        pattern = ["BUY", "BUY", "SELL", "SELL"]
        return pattern[self.pattern_index % 4]
    
    def advance_pattern(self) -> None:
        """Move to the next position in the pattern."""
        self.pattern_index += 1
    
    def reset(self) -> None:
        """Reset session state while keeping configuration."""
        self.active = False
        self.trades_executed = 0
        self.spent_notional = 0.0
        self.received_quote = 0.0
        self.base_position_delta = 0.0
        self.pattern_index = 0
        self.started_at = None
        self.stopped_at = None
        self.last_error = None


@dataclass
class TradeRecord:
    """
    Record of a single executed trade.
    Stored for historical tracking and analysis.
    """
    id: Optional[int] = None
    user_id: int = 0
    side: str = ""  # "BUY" or "SELL"
    amount_in: float = 0.0  # Input token amount (in token units, adjusted for decimals)
    amount_out: float = 0.0  # Output token amount (in token units, adjusted for decimals)
    tx_hash: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    gas_used: Optional[int] = None
    gas_price_gwei: Optional[float] = None
    execution_price: Optional[float] = None  # Effective quote/base price for this trade
    
    def __str__(self) -> str:
        """Human-readable representation of the trade."""
        return (
            f"Trade #{self.id}: {self.side} "
            f"in={self.amount_in:.4f} out={self.amount_out:.4f} "
            f"tx={self.tx_hash[:10]}... at {self.timestamp.isoformat()}"
        )

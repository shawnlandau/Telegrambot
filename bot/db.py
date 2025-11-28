"""
Database layer using SQLAlchemy ORM for persistent storage.
Manages session configuration, state, and trade history in SQLite.
"""

import logging
from typing import Optional, List
from datetime import datetime
from contextlib import contextmanager

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Float,
    String,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .models import SessionConfig, SessionState, TradeRecord

logger = logging.getLogger(__name__)

Base = declarative_base()


# SQLAlchemy ORM Models

class SessionConfigDB(Base):
    """Database model for SessionConfig."""
    __tablename__ = "session_configs"
    
    user_id = Column(Integer, primary_key=True)
    total_liquidity = Column(Float, nullable=False)
    trade_pct = Column(Float, nullable=False)
    interval_seconds = Column(Integer, nullable=False)
    slippage_bps = Column(Integer, default=50)
    min_notional = Column(Float, default=10.0)
    max_position = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SessionStateDB(Base):
    """Database model for SessionState."""
    __tablename__ = "session_states"
    
    user_id = Column(Integer, primary_key=True)
    active = Column(Boolean, default=False)
    trades_executed = Column(Integer, default=0)
    spent_notional = Column(Float, default=0.0)
    received_quote = Column(Float, default=0.0)
    base_position_delta = Column(Float, default=0.0)
    pattern_index = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=True)
    stopped_at = Column(DateTime, nullable=True)
    last_error = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TradeRecordDB(Base):
    """Database model for TradeRecord."""
    __tablename__ = "trade_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    side = Column(String(4), nullable=False)  # "BUY" or "SELL"
    amount_in = Column(Float, nullable=False)
    amount_out = Column(Float, nullable=False)
    tx_hash = Column(String(66), nullable=False, unique=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    gas_used = Column(Integer, nullable=True)
    gas_price_gwei = Column(Float, nullable=True)
    execution_price = Column(Float, nullable=True)


class Database:
    """
    Database manager for the DEX bot.
    Provides CRUD operations for configurations, states, and trade records.
    """
    
    def __init__(self, db_path: str = "bot_data.db"):
        """Initialize database connection and create tables."""
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            echo=False,
            connect_args={"check_same_thread": False}
        )
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        logger.info(f"Database initialized at {db_path}")
    
    @contextmanager
    def get_session(self):
        """Provide a transactional scope for database operations."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    # SessionConfig operations
    
    def save_session_config(self, config: SessionConfig) -> None:
        """Save or update a user's session configuration."""
        with self.get_session() as session:
            db_config = session.query(SessionConfigDB).filter_by(
                user_id=config.user_id
            ).first()
            
            if db_config:
                # Update existing
                db_config.total_liquidity = config.total_liquidity
                db_config.trade_pct = config.trade_pct
                db_config.interval_seconds = config.interval_seconds
                db_config.slippage_bps = config.slippage_bps
                db_config.min_notional = config.min_notional
                db_config.max_position = config.max_position
                db_config.updated_at = datetime.utcnow()
                logger.info(f"Updated session config for user {config.user_id}")
            else:
                # Create new
                db_config = SessionConfigDB(
                    user_id=config.user_id,
                    total_liquidity=config.total_liquidity,
                    trade_pct=config.trade_pct,
                    interval_seconds=config.interval_seconds,
                    slippage_bps=config.slippage_bps,
                    min_notional=config.min_notional,
                    max_position=config.max_position,
                )
                session.add(db_config)
                logger.info(f"Created session config for user {config.user_id}")
    
    def get_session_config(self, user_id: int) -> Optional[SessionConfig]:
        """Retrieve a user's session configuration."""
        with self.get_session() as session:
            db_config = session.query(SessionConfigDB).filter_by(
                user_id=user_id
            ).first()
            
            if not db_config:
                return None
            
            return SessionConfig(
                user_id=db_config.user_id,
                total_liquidity=db_config.total_liquidity,
                trade_pct=db_config.trade_pct,
                interval_seconds=db_config.interval_seconds,
                slippage_bps=db_config.slippage_bps,
                min_notional=db_config.min_notional,
                max_position=db_config.max_position,
            )
    
    # SessionState operations
    
    def save_session_state(self, state: SessionState) -> None:
        """Save or update a user's session state."""
        with self.get_session() as session:
            db_state = session.query(SessionStateDB).filter_by(
                user_id=state.user_id
            ).first()
            
            if db_state:
                # Update existing
                db_state.active = state.active
                db_state.trades_executed = state.trades_executed
                db_state.spent_notional = state.spent_notional
                db_state.received_quote = state.received_quote
                db_state.base_position_delta = state.base_position_delta
                db_state.pattern_index = state.pattern_index
                db_state.started_at = state.started_at
                db_state.stopped_at = state.stopped_at
                db_state.last_error = state.last_error
                db_state.updated_at = datetime.utcnow()
            else:
                # Create new
                db_state = SessionStateDB(
                    user_id=state.user_id,
                    active=state.active,
                    trades_executed=state.trades_executed,
                    spent_notional=state.spent_notional,
                    received_quote=state.received_quote,
                    base_position_delta=state.base_position_delta,
                    pattern_index=state.pattern_index,
                    started_at=state.started_at,
                    stopped_at=state.stopped_at,
                    last_error=state.last_error,
                )
                session.add(db_state)
    
    def get_session_state(self, user_id: int) -> SessionState:
        """Retrieve a user's session state or create a new one."""
        with self.get_session() as session:
            db_state = session.query(SessionStateDB).filter_by(
                user_id=user_id
            ).first()
            
            if not db_state:
                # Return new state if none exists
                return SessionState(user_id=user_id)
            
            return SessionState(
                user_id=db_state.user_id,
                active=db_state.active,
                trades_executed=db_state.trades_executed,
                spent_notional=db_state.spent_notional,
                received_quote=db_state.received_quote,
                base_position_delta=db_state.base_position_delta,
                pattern_index=db_state.pattern_index,
                started_at=db_state.started_at,
                stopped_at=db_state.stopped_at,
                last_error=db_state.last_error,
            )
    
    # TradeRecord operations
    
    def save_trade_record(self, trade: TradeRecord) -> int:
        """Save a trade record and return its ID."""
        with self.get_session() as session:
            db_trade = TradeRecordDB(
                user_id=trade.user_id,
                side=trade.side,
                amount_in=trade.amount_in,
                amount_out=trade.amount_out,
                tx_hash=trade.tx_hash,
                timestamp=trade.timestamp,
                gas_used=trade.gas_used,
                gas_price_gwei=trade.gas_price_gwei,
                execution_price=trade.execution_price,
            )
            session.add(db_trade)
            session.flush()  # Get the ID
            trade_id = db_trade.id
            logger.info(f"Saved trade record #{trade_id} for user {trade.user_id}")
            return trade_id
    
    def get_user_trades(self, user_id: int, limit: int = 100) -> List[TradeRecord]:
        """Retrieve recent trades for a user."""
        with self.get_session() as session:
            db_trades = (
                session.query(TradeRecordDB)
                .filter_by(user_id=user_id)
                .order_by(TradeRecordDB.timestamp.desc())
                .limit(limit)
                .all()
            )
            
            return [
                TradeRecord(
                    id=db_trade.id,
                    user_id=db_trade.user_id,
                    side=db_trade.side,
                    amount_in=db_trade.amount_in,
                    amount_out=db_trade.amount_out,
                    tx_hash=db_trade.tx_hash,
                    timestamp=db_trade.timestamp,
                    gas_used=db_trade.gas_used,
                    gas_price_gwei=db_trade.gas_price_gwei,
                    execution_price=db_trade.execution_price,
                )
                for db_trade in db_trades
            ]
    
    def get_trade_count(self, user_id: int) -> int:
        """Get total number of trades for a user."""
        with self.get_session() as session:
            return session.query(TradeRecordDB).filter_by(user_id=user_id).count()
    
    def backup_database(self, backup_path: str = None) -> str:
        """
        Create a backup of the database.
        
        Args:
            backup_path: Optional path for backup file. If None, uses timestamp.
        
        Returns:
            Path to the backup file.
        """
        import shutil
        import os
        from datetime import datetime
        
        if backup_path is None:
            base_name = self.engine.url.database or "bot_data.db"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{base_name}.backup.{timestamp}"
        
        # Ensure directory exists
        backup_dir = os.path.dirname(backup_path) or "."
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)
        
        # Copy database file
        db_path = self.engine.url.database
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found: {db_path}")
        
        shutil.copy2(db_path, backup_path)
        logger.info(f"Database backup created: {backup_path}")
        return backup_path
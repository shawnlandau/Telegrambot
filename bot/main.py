"""
Main Telegram bot application.
Handles user commands and manages trading sessions.
"""

import logging
import sys
import asyncio
import signal
import queue as queue_module
from typing import Optional, Dict
from collections import defaultdict
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from .config import config
from .db import Database
from .dex_client import DexClient
from .session_runner import SessionRunner
from .models import SessionConfig

# Setup logging with rotation
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

# File handler with rotation
if config.ENABLE_LOG_ROTATION:
    file_handler = RotatingFileHandler(
        config.LOG_FILE_PATH,
        maxBytes=config.MAX_LOG_SIZE_MB * 1024 * 1024,
        backupCount=config.LOG_BACKUP_COUNT
    )
else:
    file_handler = logging.FileHandler(config.LOG_FILE_PATH)

file_handler.setFormatter(formatter)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(getattr(logging, config.LOG_LEVEL))
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

logger = logging.getLogger(__name__)

# Conversation states for /config command
CONFIG_LIQUIDITY, CONFIG_PCT, CONFIG_INTERVAL = range(3)

# Global instances
db: Database
dex_client: DexClient
session_runner: SessionRunner
application: Application

# Rate limiting: track command usage per user
rate_limit_tracker: Dict[int, list] = defaultdict(list)


def check_authorization(func):
    """Decorator to check if user is authorized."""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not config.is_authorized_user(user_id):
            await update.message.reply_text(
                "❌ You are not authorized to use this bot."
            )
            logger.warning(f"Unauthorized access attempt from user {user_id}")
            return
        return await func(update, context)
    return wrapper


def check_rate_limit(func):
    """Decorator to enforce rate limiting on commands."""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        now = datetime.utcnow()
        
        # Clean old entries (older than 1 minute)
        if user_id in rate_limit_tracker:
            rate_limit_tracker[user_id] = [
                ts for ts in rate_limit_tracker[user_id]
                if now - ts < timedelta(minutes=1)
            ]
        
        # Check rate limit
        if len(rate_limit_tracker[user_id]) >= config.RATE_LIMIT_PER_MINUTE:
            await update.message.reply_text(
                "⚠️ Rate limit exceeded. Please wait a moment before trying again."
            )
            logger.warning(f"Rate limit exceeded for user {user_id}")
            return
        
        # Record this command
        rate_limit_tracker[user_id].append(now)
        
        return await func(update, context)
    return wrapper


def validate_float_input(value: str, min_val: float = None, max_val: float = None) -> float:
    """Validate and parse float input."""
    try:
        num = float(value)
        if min_val is not None and num < min_val:
            raise ValueError(f"Value must be at least {min_val}")
        if max_val is not None and num > max_val:
            raise ValueError(f"Value must be at most {max_val}")
        return num
    except ValueError as e:
        if "could not convert" in str(e).lower():
            raise ValueError("Invalid number format")
        raise


def validate_int_input(value: str, min_val: int = None, max_val: int = None) -> int:
    """Validate and parse int input."""
    try:
        num = int(value)
        if min_val is not None and num < min_val:
            raise ValueError(f"Value must be at least {min_val}")
        if max_val is not None and num > max_val:
            raise ValueError(f"Value must be at most {max_val}")
        return num
    except ValueError as e:
        if "invalid literal" in str(e).lower():
            raise ValueError("Invalid integer format")
        raise


async def process_message_queues(context: ContextTypes.DEFAULT_TYPE):
    """Periodically process message queues from session runner."""
    try:
        # Get all active user IDs from session runner
        for user_id in list(session_runner.message_queues.keys()):
            if user_id not in session_runner.message_callbacks:
                continue
            
            callback = session_runner.message_callbacks.get(user_id)
            if not callback:
                continue
            
            queue_obj = session_runner.message_queues.get(user_id)
            if not queue_obj:
                continue
            
            # Process all queued messages
            while not queue_obj.empty():
                try:
                    message = queue_obj.get_nowait()
                    # Send message via callback
                    await callback(message)
                except queue_module.Empty:
                    break
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
    except Exception as e:
        logger.error(f"Error processing message queues: {e}")


@check_authorization
@check_rate_limit
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /start command - begin trading session.
    
    This command starts the automated trading loop with the 2×2 pattern.
    IMPORTANT: This bot is designed for legitimate DCA (Dollar Cost Averaging)
    execution only. It is NOT for wash trading, volume manipulation, or spoofing.
    """
    user_id = update.effective_user.id
    
    # Check if config exists
    user_config = db.get_session_config(user_id)
    if not user_config:
        await update.message.reply_text(
            "❌ No configuration found.\n"
            "Please run /config first to set up your trading parameters."
        )
        return
    
    # Check if already running
    if session_runner.is_session_active(user_id):
        await update.message.reply_text(
            "⚠️ A trading session is already active.\n"
            "Use /stop to stop it first."
        )
        return
    
    # Register message callback
    async def send_message(msg: str):
        await context.bot.send_message(chat_id=user_id, text=msg)
    
    session_runner.register_message_callback(user_id, send_message)
    
    # Start session
    if session_runner.start_session(user_id):
        trade_amount = user_config.get_trade_amount()
        await update.message.reply_text(
            f"✅ Trading session started!\n\n"
            f"📊 Configuration:\n"
            f"• Total Liquidity: {user_config.total_liquidity:.2f}\n"
            f"• Trade %: {user_config.trade_pct}%\n"
            f"• Trade Amount: {trade_amount:.2f}\n"
            f"• Interval: {user_config.interval_seconds}s\n"
            f"• Pattern: BUY → BUY → SELL → SELL (repeating)\n\n"
            f"The bot will execute trades automatically.\n"
            f"Use /status to check progress or /stop to stop."
        )
        logger.info(f"User {user_id} started trading session")
    else:
        await update.message.reply_text(
            "❌ Failed to start trading session.\n"
            "Please check logs or contact support."
        )


@check_authorization
@check_rate_limit
async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stop command - stop trading session."""
    user_id = update.effective_user.id
    
    if session_runner.stop_session(user_id):
        session_state = db.get_session_state(user_id)
        net_quote = session_state.get_net_quote()
        
        await update.message.reply_text(
            f"🛑 Trading session stopped.\n\n"
            f"📈 Session Summary:\n"
            f"• Trades Executed: {session_state.trades_executed}\n"
            f"• Quote Spent: {session_state.spent_notional:.2f}\n"
            f"• Quote Received: {session_state.received_quote:.2f}\n"
            f"• Net Quote P/L: {net_quote:+.2f}\n"
            f"• Base Position Δ: {session_state.base_position_delta:+.6f}"
        )
        logger.info(f"User {user_id} stopped trading session")
    else:
        await update.message.reply_text(
            "⚠️ No active trading session to stop."
        )


@check_authorization
@check_rate_limit
async def cmd_config_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /config command - start configuration conversation."""
    user_id = update.effective_user.id
    
    # Check if session is active
    if session_runner.is_session_active(user_id):
        await update.message.reply_text(
            "⚠️ Cannot change configuration while a session is active.\n"
            "Please /stop the session first."
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "🔧 Let's configure your trading parameters.\n\n"
        "Please enter your **total liquidity** in quote tokens "
        "(e.g., total USDC available for trading):"
    )
    return CONFIG_LIQUIDITY


async def config_liquidity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle liquidity input."""
    try:
        # Validate and sanitize input
        liquidity = validate_float_input(update.message.text.strip(), min_val=0.01, max_val=1e15)
        
        context.user_data['total_liquidity'] = liquidity
        
        await update.message.reply_text(
            f"✅ Total liquidity: {liquidity:.2f}\n\n"
            f"Now enter the **trade percentage** (% of total liquidity per trade).\n"
            f"For example, enter '2' for 2% ({liquidity * 0.02:.2f} per trade):"
        )
        return CONFIG_PCT
        
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid input. Please enter a positive number:"
        )
        return CONFIG_LIQUIDITY


async def config_pct(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle trade percentage input."""
    try:
        # Validate and sanitize input
        trade_pct = validate_float_input(update.message.text.strip(), min_val=0.01, max_val=100)
        
        context.user_data['trade_pct'] = trade_pct
        
        liquidity = context.user_data['total_liquidity']
        trade_amount = liquidity * (trade_pct / 100)
        
        await update.message.reply_text(
            f"✅ Trade percentage: {trade_pct}%\n"
            f"   Trade amount: {trade_amount:.2f}\n\n"
            f"Finally, enter the **interval in seconds** between trades.\n"
            f"For example, enter '60' for 1 minute between trades:"
        )
        return CONFIG_INTERVAL
        
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid input. Please enter a percentage between 0 and 100:"
        )
        return CONFIG_PCT


async def config_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle interval input and save configuration."""
    user_id = update.effective_user.id
    
    try:
        # Validate and sanitize input
        interval = validate_int_input(update.message.text.strip(), min_val=1, max_val=86400)
        
        # Create and save configuration
        session_config = SessionConfig(
            user_id=user_id,
            total_liquidity=context.user_data['total_liquidity'],
            trade_pct=context.user_data['trade_pct'],
            interval_seconds=interval,
        )
        
        db.save_session_config(session_config)
        
        trade_amount = session_config.get_trade_amount()
        
        await update.message.reply_text(
            f"✅ Configuration saved!\n\n"
            f"📊 Your Settings:\n"
            f"• Total Liquidity: {session_config.total_liquidity:.2f}\n"
            f"• Trade %: {session_config.trade_pct}%\n"
            f"• Trade Amount: {trade_amount:.2f}\n"
            f"• Interval: {session_config.interval_seconds}s\n"
            f"• Slippage: {session_config.slippage_bps / 100:.2f}%\n"
            f"• Min Trade: {session_config.min_notional:.2f}\n\n"
            f"Pattern: BUY → BUY → SELL → SELL (repeating)\n\n"
            f"Use /start to begin trading!"
        )
        
        logger.info(f"User {user_id} configured trading parameters")
        
        # Clear user data
        context.user_data.clear()
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid input. Please enter a positive integer (seconds):"
        )
        return CONFIG_INTERVAL


async def config_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle conversation cancellation."""
    await update.message.reply_text("❌ Configuration cancelled.")
    context.user_data.clear()
    return ConversationHandler.END


@check_authorization
@check_rate_limit
async def cmd_setpct(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /setpct command - update trade percentage."""
    user_id = update.effective_user.id
    
    # Check if session is active
    if session_runner.is_session_active(user_id):
        await update.message.reply_text(
            "⚠️ Cannot change configuration while a session is active.\n"
            "Please /stop the session first."
        )
        return
    
    # Check if config exists
    session_config = db.get_session_config(user_id)
    if not session_config:
        await update.message.reply_text(
            "❌ No configuration found. Please run /config first."
        )
        return
    
    # Parse percentage
    try:
        if not context.args or len(context.args) != 1:
            raise ValueError("Missing argument")
        
        new_pct = validate_float_input(context.args[0].strip(), min_val=0.01, max_val=100)
        
        # Update config
        session_config.trade_pct = new_pct
        db.save_session_config(session_config)
        
        trade_amount = session_config.get_trade_amount()
        
        await update.message.reply_text(
            f"✅ Trade percentage updated to {new_pct}%\n"
            f"   New trade amount: {trade_amount:.2f}"
        )
        logger.info(f"User {user_id} updated trade_pct to {new_pct}%")
        
    except (ValueError, IndexError):
        await update.message.reply_text(
            "❌ Invalid usage.\n"
            "Usage: /setpct <percentage>\n"
            "Example: /setpct 2.5"
        )


@check_authorization
@check_rate_limit
async def cmd_setinterval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /setinterval command - update trade interval."""
    user_id = update.effective_user.id
    
    # Check if session is active
    if session_runner.is_session_active(user_id):
        await update.message.reply_text(
            "⚠️ Cannot change configuration while a session is active.\n"
            "Please /stop the session first."
        )
        return
    
    # Check if config exists
    session_config = db.get_session_config(user_id)
    if not session_config:
        await update.message.reply_text(
            "❌ No configuration found. Please run /config first."
        )
        return
    
    # Parse interval
    try:
        if not context.args or len(context.args) != 1:
            raise ValueError("Missing argument")
        
        new_interval = validate_int_input(context.args[0].strip(), min_val=1, max_val=86400)
        
        # Update config
        session_config.interval_seconds = new_interval
        db.save_session_config(session_config)
        
        await update.message.reply_text(
            f"✅ Trade interval updated to {new_interval} seconds"
        )
        logger.info(f"User {user_id} updated interval to {new_interval}s")
        
    except (ValueError, IndexError):
        await update.message.reply_text(
            "❌ Invalid usage.\n"
            "Usage: /setinterval <seconds>\n"
            "Example: /setinterval 120"
        )


@check_authorization
@check_rate_limit
async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command - show current status."""
    user_id = update.effective_user.id
    
    # Get configuration
    session_config = db.get_session_config(user_id)
    if not session_config:
        await update.message.reply_text(
            "❌ No configuration found. Please run /config first."
        )
        return
    
    # Get state
    session_state = db.get_session_state(user_id)
    
    # Get balances
    try:
        balances = dex_client.get_balances()
        price = dex_client.get_price()
    except Exception as e:
        logger.error(f"Failed to fetch on-chain data: {e}")
        balances = {"base": 0, "quote": 0}
        price = 0
    
    # Build status message
    status_emoji = "🟢" if session_state.active else "🔴"
    status_text = "ACTIVE" if session_state.active else "STOPPED"
    
    net_quote = session_state.get_net_quote()
    current_side = session_state.get_current_side()
    
    trade_amount = session_config.get_trade_amount()
    
    message = (
        f"{status_emoji} Session Status: **{status_text}**\n\n"
        f"📊 Configuration:\n"
        f"• Total Liquidity: {session_config.total_liquidity:.2f}\n"
        f"• Trade %: {session_config.trade_pct}%\n"
        f"• Trade Amount: {trade_amount:.2f}\n"
        f"• Interval: {session_config.interval_seconds}s\n\n"
        f"📈 Statistics:\n"
        f"• Trades Executed: {session_state.trades_executed}\n"
        f"• Quote Spent: {session_state.spent_notional:.2f}\n"
        f"• Quote Received: {session_state.received_quote:.2f}\n"
        f"• Net Quote P/L: {net_quote:+.2f}\n"
        f"• Base Position Δ: {session_state.base_position_delta:+.6f}\n"
        f"• Next Trade: {current_side}\n\n"
        f"💰 Current Balances:\n"
        f"• Base: {balances['base']:.6f}\n"
        f"• Quote: {balances['quote']:.2f}\n"
        f"• Price: {price:.6f}\n\n"
        f"Pattern: BUY → BUY → SELL → SELL"
    )
    
    if session_state.last_error:
        message += f"\n\n⚠️ Last Error:\n{session_state.last_error}"
    
    await update.message.reply_text(message, parse_mode='Markdown')


@check_authorization
@check_rate_limit
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command - show help message."""
    help_text = (
        "🤖 **DEX Trading Bot - Help**\n\n"
        "This bot executes automated trades with a fixed 2×2 pattern:\n"
        "BUY → BUY → SELL → SELL (repeating)\n\n"
        "**Commands:**\n"
        "/config - Set up trading parameters\n"
        "/setpct <value> - Update trade percentage\n"
        "/setinterval <seconds> - Update trade interval\n"
        "/start - Start trading session\n"
        "/stop - Stop trading session\n"
        "/status - Show current status\n"
        "/history [limit] - Show recent trade history (default: 10, max: 50)\n"
        "/reset - Reset session state (clears statistics)\n"
        "/help - Show this help message\n\n"
        "⚠️ **Important:**\n"
        "This bot is designed for legitimate DCA (Dollar Cost Averaging) "
        "execution only. It trades from a single wallet and is NOT intended "
        "for wash trading, volume manipulation, or market spoofing.\n\n"
        "Users are responsible for compliance with all applicable laws "
        "and regulations in their jurisdiction."
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


@check_authorization
@check_rate_limit
async def cmd_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /history command - show recent trade history."""
    user_id = update.effective_user.id
    
    # Get limit from args or use default
    limit = 10
    if context.args and len(context.args) > 0:
        try:
            limit = validate_int_input(context.args[0].strip(), min_val=1, max_val=50)
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid limit. Usage: /history [limit]\n"
                "Example: /history 20"
            )
            return
    
    # Get trades
    trades = db.get_user_trades(user_id, limit=limit)
    
    if not trades:
        await update.message.reply_text("📊 No trade history found.")
        return
    
    # Format message
    message = f"📊 Recent Trade History (Last {len(trades)} trades):\n\n"
    
    for trade in trades[:limit]:
        timestamp = trade.timestamp.strftime("%Y-%m-%d %H:%M:%S") if trade.timestamp else "N/A"
        message += (
            f"**{trade.side}** - {timestamp}\n"
            f"In: {trade.amount_in:.6f}\n"
            f"Out: {trade.amount_out:.6f}\n"
            f"TX: `{trade.tx_hash[:16]}...`\n"
        )
        if trade.execution_price:
            message += f"Price: {trade.execution_price:.6f}\n"
        message += "\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')


@check_authorization
@check_rate_limit
async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /reset command - reset session state."""
    user_id = update.effective_user.id
    
    # Check if session is active
    if session_runner.is_session_active(user_id):
        await update.message.reply_text(
            "⚠️ Cannot reset while a session is active.\n"
            "Please /stop the session first."
        )
        return
    
    # Reset session state
    session_state = db.get_session_state(user_id)
    session_state.reset()
    db.save_session_state(session_state)
    
    await update.message.reply_text(
        "✅ Session state has been reset.\n"
        "All trade statistics have been cleared."
    )
    logger.info(f"User {user_id} reset session state")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot."""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ An error occurred. Please try again or contact support."
        )


def setup_signal_handlers(app: Application):
    """Setup graceful shutdown handlers."""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        # Stop all active sessions
        for user_id in list(session_runner.active_sessions.keys()):
            session_runner.stop_session(user_id)
        # Stop the bot
        app.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main() -> None:
    """Main entry point for the bot."""
    global db, dex_client, session_runner, application
    
    logger.info("Starting DEX Trading Bot...")
    
    # Initialize components
    try:
        db = Database(config.DATABASE_PATH)
        logger.info("Database initialized")
        
        dex_client = DexClient()
        logger.info("DEX client initialized")
        
        session_runner = SessionRunner(db, dex_client)
        logger.info("Session runner initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}", exc_info=True)
        sys.exit(1)
    
    # Create application
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    
    # Setup graceful shutdown
    setup_signal_handlers(application)
    
    # Add conversation handler for /config
    config_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('config', cmd_config_start)],
        states={
            CONFIG_LIQUIDITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, config_liquidity)],
            CONFIG_PCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, config_pct)],
            CONFIG_INTERVAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, config_interval)],
        },
        fallbacks=[CommandHandler('cancel', config_cancel)],
    )
    
    application.add_handler(config_conv_handler)
    
    # Add command handlers
    application.add_handler(CommandHandler('start', cmd_start))
    application.add_handler(CommandHandler('stop', cmd_stop))
    application.add_handler(CommandHandler('setpct', cmd_setpct))
    application.add_handler(CommandHandler('setinterval', cmd_setinterval))
    application.add_handler(CommandHandler('status', cmd_status))
    application.add_handler(CommandHandler('history', cmd_history))
    application.add_handler(CommandHandler('reset', cmd_reset))
    application.add_handler(CommandHandler('help', cmd_help))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start message queue processor
    application.job_queue.run_repeating(
        process_message_queues,
        interval=1,
        first=1
    )
    
    # Start bot
    logger.info("Bot is running...")
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        # Cleanup
        logger.info("Shutting down bot...")
        for user_id in list(session_runner.active_sessions.keys()):
            session_runner.stop_session(user_id)
        logger.info("Bot shutdown complete")


if __name__ == '__main__':
    main()

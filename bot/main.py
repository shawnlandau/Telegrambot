"""
Main Telegram bot application.
Handles user commands and manages trading sessions.
"""

import logging
import sys
from typing import Optional

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

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.LOG_LEVEL),
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

# Conversation states for /config command
CONFIG_LIQUIDITY, CONFIG_PCT, CONFIG_INTERVAL = range(3)

# Global instances
db: Database
dex_client: DexClient
session_runner: SessionRunner


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


@check_authorization
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
        liquidity = float(update.message.text)
        if liquidity <= 0:
            raise ValueError("Must be positive")
        
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
        trade_pct = float(update.message.text)
        if not (0 < trade_pct <= 100):
            raise ValueError("Must be between 0 and 100")
        
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
        interval = int(update.message.text)
        if interval < 1:
            raise ValueError("Must be at least 1 second")
        
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
        
        new_pct = float(context.args[0])
        if not (0 < new_pct <= 100):
            raise ValueError("Must be between 0 and 100")
        
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
        
        new_interval = int(context.args[0])
        if new_interval < 1:
            raise ValueError("Must be at least 1 second")
        
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
        "/help - Show this help message\n\n"
        "⚠️ **Important:**\n"
        "This bot is designed for legitimate DCA (Dollar Cost Averaging) "
        "execution only. It trades from a single wallet and is NOT intended "
        "for wash trading, volume manipulation, or market spoofing.\n\n"
        "Users are responsible for compliance with all applicable laws "
        "and regulations in their jurisdiction."
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot."""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ An error occurred. Please try again or contact support."
        )


def main() -> None:
    """Main entry point for the bot."""
    global db, dex_client, session_runner
    
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
        logger.error(f"Failed to initialize bot: {e}")
        sys.exit(1)
    
    # Create application
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    
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
    application.add_handler(CommandHandler('help', cmd_help))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

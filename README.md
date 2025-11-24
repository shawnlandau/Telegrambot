# DEX Trading Bot MVP - Fixed 2×2 Pattern

A production-ready Python Telegram bot for automated DCA (Dollar Cost Averaging) execution on Uniswap V2-style DEXes using a fixed 2×2 trading pattern.

## ⚠️ IMPORTANT COMPLIANCE & DISCLAIMER

**This bot is designed EXCLUSIVELY for legitimate trading purposes:**

- **Real execution and DCA**: Smoothing out order execution over time to reduce market impact
- **Inventory management**: Gradually building or reducing positions in a single wallet
- **Honest trading**: All trades are executed from ONE real wallet address

**This bot is NOT designed or intended for:**

- ❌ Wash trading between related accounts
- ❌ Artificial volume creation or manipulation
- ❌ Market spoofing or deceptive practices
- ❌ Any form of market manipulation

**User Responsibility**: You are solely responsible for compliance with all applicable laws, regulations, and exchange rules in your jurisdiction. Consult with legal counsel before deploying this bot.

---

## 📊 Trading Pattern

The bot executes a fixed, repeating pattern:

```
BUY → BUY → SELL → SELL → BUY → BUY → SELL → SELL → ...
```

This simple 2×2 pattern:
- Alternates between accumulation (2 buys) and distribution (2 sells)
- Helps smooth execution without large single orders
- Provides basic inventory rebalancing over time

---

## 🏗️ Architecture

```
bot/
├── main.py              # Telegram bot entry point and command handlers
├── config.py            # Environment configuration and validation
├── db.py                # SQLAlchemy ORM and database layer
├── models.py            # Data models (SessionConfig, SessionState, TradeRecord)
├── dex_client.py        # Web3 DEX interaction (swaps, balances, prices)
├── session_runner.py    # Background trading loop with 2×2 pattern
└── abi/
    ├── erc20.json              # ERC-20 token ABI
    └── uniswap_v2_router.json  # Uniswap V2 router ABI
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Access to an EVM RPC endpoint (e.g., Infura, Alchemy, or self-hosted node)
- A Telegram bot token (from [@BotFather](https://t.me/botfather))
- A wallet with private key and sufficient tokens/gas

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd webapp
   ```

2. **Create virtual environment**:
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the bot**:
   ```bash
   python -m bot.main
   ```

---

## 🔧 Configuration

### Required Environment Variables

Create a `.env` file with the following variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `RPC_URL` | EVM RPC endpoint URL | `https://mainnet.infura.io/v3/YOUR_KEY` |
| `WALLET_PRIVATE_KEY` | Private key for trading wallet (with or without 0x) | `0x1234...abcd` |
| `DEX_ROUTER_ADDRESS` | Uniswap V2-style router contract address | `0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D` |
| `BASE_TOKEN_ADDRESS` | Base token address (the token you're trading) | `0x6B175474E89094C44Da98b954EedeAC495271d0F` |
| `QUOTE_TOKEN_ADDRESS` | Quote token address (e.g., USDC, DAI) | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token from @BotFather | `123456789:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `ALLOWED_TELEGRAM_IDS` | Comma-separated list of authorized Telegram user IDs | `123456789,987654321` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_PATH` | Path to SQLite database file | `bot_data.db` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `MAX_TRADES_PER_SESSION` | Maximum trades before auto-stop | `1000` |
| `GAS_PRICE_GWEI` | Fixed gas price in Gwei (leave empty for auto) | (network default) |
| `GAS_LIMIT` | Gas limit for transactions | `300000` |

---

## 💬 Telegram Commands

Once the bot is running, interact with it via Telegram:

### Setup Commands

- `/config` - Interactive configuration wizard
  - Set total liquidity (in quote tokens)
  - Set trade percentage (% of liquidity per trade)
  - Set interval between trades (in seconds)

- `/setpct <percentage>` - Update trade percentage
  - Example: `/setpct 2.5` sets trade size to 2.5% of total liquidity

- `/setinterval <seconds>` - Update trade interval
  - Example: `/setinterval 120` sets 2-minute intervals

### Trading Commands

- `/start` - Start automated trading session
  - Begins executing the BUY-BUY-SELL-SELL pattern
  - Trades continue until `/stop` or error occurs

- `/stop` - Stop trading session
  - Gracefully stops after current trade
  - Shows session summary

- `/status` - Show current status
  - Configuration settings
  - Session statistics (trades, P/L, position)
  - Current balances and price
  - Next trade in pattern

### Help

- `/help` - Show help message with all commands

---

## 📈 Example Usage

### 1. Configure Trading Parameters

```
User: /config

Bot: Let's configure your trading parameters.
     Please enter your total liquidity in quote tokens:

User: 10000

Bot: ✅ Total liquidity: 10000.00
     Now enter the trade percentage:

User: 2

Bot: ✅ Trade percentage: 2%
     Trade amount: 200.00
     Finally, enter the interval in seconds:

User: 60

Bot: ✅ Configuration saved!
     📊 Your Settings:
     • Total Liquidity: 10000.00
     • Trade %: 2%
     • Trade Amount: 200.00
     • Interval: 60s
     
     Pattern: BUY → BUY → SELL → SELL (repeating)
     
     Use /start to begin trading!
```

### 2. Start Trading

```
User: /start

Bot: ✅ Trading session started!
     
     📊 Configuration:
     • Total Liquidity: 10000.00
     • Trade %: 2%
     • Trade Amount: 200.00
     • Interval: 60s
     • Pattern: BUY → BUY → SELL → SELL (repeating)
     
     The bot will execute trades automatically.
     Use /status to check progress or /stop to stop.

[After each trade, you'll receive notifications:]

Bot: ✅ BUY completed:
     In: 200.000000
     Out: 0.105234
     TX: 0x1234abcd5678...
     Trades: 1
```

### 3. Check Status

```
User: /status

Bot: 🟢 Session Status: ACTIVE
     
     📊 Configuration:
     • Total Liquidity: 10000.00
     • Trade %: 2%
     • Trade Amount: 200.00
     • Interval: 60s
     
     📈 Statistics:
     • Trades Executed: 8
     • Quote Spent: 800.00
     • Quote Received: 785.50
     • Net Quote P/L: -14.50
     • Base Position Δ: +0.421856
     • Next Trade: BUY
     
     💰 Current Balances:
     • Base: 0.421856
     • Quote: 9985.50
     • Price: 1901.234567
     
     Pattern: BUY → BUY → SELL → SELL
```

### 4. Stop Trading

```
User: /stop

Bot: 🛑 Trading session stopped.
     
     📈 Session Summary:
     • Trades Executed: 20
     • Quote Spent: 2000.00
     • Quote Received: 1960.25
     • Net Quote P/L: -39.75
     • Base Position Δ: +0.000000
```

---

## 🔐 Security Best Practices

1. **Private Key Security**:
   - Never commit `.env` file to version control
   - Use environment variables or secure vault in production
   - Consider using a dedicated trading wallet with limited funds

2. **Access Control**:
   - Only add trusted Telegram user IDs to `ALLOWED_TELEGRAM_IDS`
   - Regularly review authorized users

3. **Monitoring**:
   - Monitor `bot.log` for errors and suspicious activity
   - Set up alerts for failed transactions
   - Regularly check wallet balances

4. **Testing**:
   - Test on testnet first (Goerli, Sepolia, etc.)
   - Start with small amounts
   - Verify all configuration before mainnet deployment

---

## 🗄️ Database Schema

The bot uses SQLite with three main tables:

### `session_configs`
- Stores per-user trading configuration
- Fields: `user_id`, `total_liquidity`, `trade_pct`, `interval_seconds`, `slippage_bps`, `min_notional`, `max_position`

### `session_states`
- Tracks runtime state for each user
- Fields: `user_id`, `active`, `trades_executed`, `spent_notional`, `received_quote`, `base_position_delta`, `pattern_index`, timestamps

### `trade_records`
- Historical record of all executed trades
- Fields: `id`, `user_id`, `side`, `amount_in`, `amount_out`, `tx_hash`, `timestamp`, `gas_used`, `execution_price`

---

## 🐛 Troubleshooting

### Bot won't start

- **Check environment variables**: Ensure all required variables are set correctly
- **Verify RPC connection**: Test your RPC endpoint with a simple web3 call
- **Check Telegram token**: Verify bot token with @BotFather

### Trades failing

- **Insufficient balance**: Ensure wallet has enough tokens and gas
- **Slippage too low**: Increase `slippage_bps` in database or code
- **Gas price**: Set `GAS_PRICE_GWEI` if network is congested
- **Token approvals**: Bot should auto-approve, but check manually if issues persist

### Session stops unexpectedly

- **Check logs**: Review `bot.log` for error messages
- **Balance check**: Ensure sufficient tokens for next trade
- **RPC issues**: Connection timeouts or rate limits
- **Gas estimation**: Transaction may be failing on-chain

### Common errors

```
❌ Session stopped: Insufficient quote token balance
→ Add more quote tokens to wallet or reduce trade_pct

❌ Trade failed: Transaction reverted
→ Check slippage, liquidity, and token approvals

❌ Session stopped: Max trades reached
→ Increase MAX_TRADES_PER_SESSION or restart session
```

---

## 📝 Development

### Project Structure

- **`config.py`**: Loads and validates environment variables
- **`models.py`**: Dataclass models for configuration and state
- **`db.py`**: SQLAlchemy ORM layer with CRUD operations
- **`dex_client.py`**: Web3 wrapper for DEX interactions
- **`session_runner.py`**: Background thread managing trade execution
- **`main.py`**: Telegram bot with command handlers

### Adding Features

1. **Custom patterns**: Modify `TRADING_PATTERN` in `session_runner.py`
2. **Multi-pair support**: Extend database schema and config
3. **Advanced strategies**: Implement new runner classes
4. **Risk management**: Add position limits, stop-loss, etc.

### Testing

```bash
# Install dev dependencies
pip install pytest pytest-asyncio pytest-mock

# Run tests
pytest tests/

# Check code style
flake8 bot/
black bot/
```

---

## 📜 License

This project is provided as-is for educational and development purposes. Users are solely responsible for compliance with applicable laws and regulations.

---

## 🤝 Support

For issues, questions, or contributions:

1. Check the troubleshooting section above
2. Review logs in `bot.log`
3. Open an issue on the repository

---

## 🔗 Useful Resources

- [Uniswap V2 Documentation](https://docs.uniswap.org/contracts/v2/overview)
- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [python-telegram-bot Documentation](https://docs.python-telegram-bot.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

**Remember**: This bot trades with real funds on-chain. Always test thoroughly on testnet before mainnet deployment, and never trade more than you can afford to lose.

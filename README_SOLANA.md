# DEX Trading Bot - Solana Edition

A production-ready Python Telegram bot for automated DCA (Dollar Cost Averaging) execution on Raydium DEX using a fixed 2×2 trading pattern on Solana blockchain.

## ⚠️ IMPORTANT: WORK IN PROGRESS

**This Solana edition is currently under development. Core functionality has been ported but requires:**

1. **Raydium SDK Integration**: The `raydium_client.py` has placeholders for actual Raydium swap implementations
2. **Pool State Parsing**: Price fetching requires parsing Raydium pool account data
3. **SPL Token Utilities**: Associated token account derivation needs proper implementation
4. **Transaction Building**: Swap instructions need to be built with correct Raydium program calls
5. **Testing**: Comprehensive testing on Solana devnet before mainnet use

**Status**: Framework complete, awaiting Raydium-specific implementations.

---

## 📊 Trading Pattern

The bot executes a fixed, repeating pattern:

```
BUY → BUY → SELL → SELL → BUY → BUY → SELL → SELL → ...
```

**For Solana:**
- **BUY**: Spend SOL → Get MEMESAI (or other SPL token)
- **SELL**: Spend MEMESAI → Get SOL

This simple 2×2 pattern:
- Alternates between accumulation (2 buys) and distribution (2 sells)
- Helps smooth execution without large single orders
- Provides basic inventory rebalancing over time

---

## 🏗️ Architecture

```
bot/
├── main.py              # Telegram bot entry point and command handlers
├── config.py            # Environment configuration and Solana address validation
├── db.py                # SQLAlchemy ORM and database layer
├── models.py            # Data models (SessionConfig, SessionState, TradeRecord)
├── raydium_client.py    # Solana/Raydium interaction (swaps, balances, prices)
├── session_runner.py    # Background trading loop with 2×2 pattern
└── abi/
    ├── erc20.json              # (Legacy - can be removed)
    └── uniswap_v2_router.json  # (Legacy - can be removed)
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Access to a Solana RPC endpoint (Mainnet, Devnet, or premium provider)
- A Telegram bot token (from [@BotFather](https://t.me/botfather))
- A Solana wallet with private key and sufficient SOL/tokens
- A Raydium pool for your trading pair (SOL/MEMESAI)

### Installation

1. **Clone the repository and switch to Solana branch**:
   ```bash
   git clone <repository-url>
   cd webapp
   git checkout Solana
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

5. **Run the bot** (after implementing Raydium SDK):
   ```bash
   python -m bot.main
   ```

---

## 🔧 Configuration

### Required Environment Variables

Create a `.env` file with the following variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `SOLANA_RPC_URL` | Solana RPC endpoint URL | `https://api.mainnet-beta.solana.com` |
| `WALLET_PRIVATE_KEY` | Private key for trading wallet (base58 encoded) | `YOUR_BASE58_PRIVATE_KEY` |
| `RAYDIUM_PROGRAM_ID` | Raydium Liquidity Pool V4 program ID | `675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8` |
| `BASE_TOKEN_ADDRESS` | Base token address (SOL wrapped mint) | `So11111111111111111111111111111111111111112` |
| `QUOTE_TOKEN_ADDRESS` | Quote token address (MEMESAI or your SPL token) | `YOUR_SPL_TOKEN_MINT_ADDRESS` |
| `RAYDIUM_POOL_ID` | Raydium pool ID for your trading pair | `YOUR_RAYDIUM_POOL_ID` |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token from @BotFather | `123456789:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `ALLOWED_TELEGRAM_IDS` | Comma-separated list of authorized Telegram user IDs | `123456789,987654321` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_PATH` | Path to SQLite database file | `bot_data.db` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `MAX_TRADES_PER_SESSION` | Maximum trades before auto-stop | `1000` |
| `MAX_RETRIES` | Maximum transaction retry attempts | `3` |
| `SKIP_PREFLIGHT` | Skip preflight checks (faster but riskier) | `false` |
| `COMMITMENT_LEVEL` | Transaction commitment level | `confirmed` |
| `DEFAULT_SLIPPAGE_BPS` | Default slippage tolerance (basis points) | `100` (1%) |

---

## 💬 Telegram Commands

Once the bot is running, interact with it via Telegram:

### Setup Commands

- `/config` - Interactive configuration wizard
  - Set total liquidity (in SOL)
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
- `/history [limit]` - Show recent trade history
- `/reset` - Reset session statistics

---

## 🔑 Getting Your Solana Private Key

### From Phantom Wallet:
1. Open Phantom wallet
2. Go to Settings → Security & Privacy
3. Click "Export Private Key"
4. Copy the base58 encoded private key

### From Solflare:
1. Open Solflare wallet
2. Settings → Export Private Key
3. Copy the private key string

### From CLI (solana-keygen):
```bash
# Generate new keypair
solana-keygen new -o my-wallet.json

# View private key as base58
solana-keygen pubkey my-wallet.json --outfile /dev/stdout
```

---

## 🔍 Finding Your Raydium Pool ID

1. **Visit Raydium**: https://raydium.io/liquidity/pools/
2. **Search for your pair**: Enter "SOL/MEMESAI" or your token pair
3. **Copy Pool ID**: From the pool information or URL
4. **Alternative**: Use Raydium SDK to query pools programmatically

Example code to find pools:
```python
# This is pseudocode - actual implementation needed
from raydium import get_pools_by_tokens

pools = get_pools_by_tokens(
    token_a="So11111111111111111111111111111111111111112",  # SOL
    token_b="YOUR_MEMESAI_MINT_ADDRESS"
)
print(f"Pool ID: {pools[0].address}")
```

---

## 🐛 Troubleshooting

### Bot won't start

- **Check environment variables**: Ensure all required variables are set correctly
- **Verify RPC connection**: Test your Solana RPC endpoint
- **Check Telegram token**: Verify bot token with @BotFather
- **Validate addresses**: Ensure all addresses are valid Solana base58 addresses

### Trades failing

- **Insufficient balance**: Ensure wallet has enough SOL and tokens
- **Slippage too low**: Increase `slippage_bps` in configuration
- **Pool liquidity**: Verify sufficient liquidity in Raydium pool
- **RPC issues**: Consider using premium RPC provider (QuickNode, Helius)

### Common errors

```
❌ Session stopped: Insufficient SOL balance
→ Add more SOL to wallet or reduce trade_pct

❌ Trade failed: Transaction simulation failed
→ Check slippage, liquidity, and token balances

❌ Session stopped: Max trades reached
→ Increase MAX_TRADES_PER_SESSION or restart session
```

---

## ⚙️ Development Roadmap

### Immediate Tasks (Required for Production)

1. **Implement Raydium Swap Instructions**
   - Build proper swap transactions using Raydium SDK
   - Handle account creation for token accounts
   - Implement proper compute unit limits

2. **Pool State Parsing**
   - Fetch and parse Raydium pool account data
   - Calculate accurate prices from reserves
   - Handle different pool versions

3. **SPL Token Utilities**
   - Proper associated token account (ATA) derivation
   - Token account creation instructions
   - Balance checking for SPL tokens

4. **Testing**
   - Comprehensive testing on devnet
   - Test with small amounts on mainnet
   - Monitor for edge cases and errors

### Future Enhancements

- Support for multiple token pairs
- Advanced risk management (stop-loss, take-profit)
- Gas/fee optimization
- Better error handling and recovery
- Performance monitoring dashboard

---

## 📚 Technical Details

### Solana-Specific Considerations

- **Transaction Size**: Solana transactions have size limits (~1232 bytes)
- **Compute Units**: Set appropriate compute unit limits for transactions
- **Rent**: Account rent must be considered for new token accounts
- **Commitment Levels**: Choose appropriate level (processed, confirmed, finalized)
- **RPC Rate Limits**: Free RPCs have strict rate limits, use premium providers

### Database Schema

The bot uses SQLite with three main tables:

- **`session_configs`**: Per-user trading configuration
- **`session_states`**: Runtime state tracking
  - `spent_notional`: Total SOL spent on BUYs
  - `received_base`: Total SOL received from SELLs
  - `quote_position_delta`: Net MEMESAI gained/lost
- **`trade_records`**: Historical trade records

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
   - Regularly check wallet balances on Solana Explorer

4. **Testing**:
   - Test on devnet first
   - Start with small amounts on mainnet
   - Verify all configuration before production deployment

---

## 🌐 Recommended RPC Providers

Free public RPCs may have rate limits and reliability issues. Consider premium providers:

- **QuickNode**: https://www.quicknode.com/
- **Helius**: https://helius.xyz/
- **Alchemy**: https://www.alchemy.com/solana
- **Triton (Triton One)**: https://triton.one/

---

## 📜 License & Compliance

**IMPORTANT**: This project is provided as-is for educational and development purposes. 

### Compliance Notice

This bot is designed **EXCLUSIVELY** for legitimate trading purposes:

- ✅ **Real execution and DCA**: Smoothing out order execution over time
- ✅ **Inventory management**: Building or reducing positions
- ✅ **Honest trading**: All trades from ONE real wallet

**This bot is NOT designed or intended for:**

- ❌ Wash trading between related accounts
- ❌ Artificial volume creation or manipulation
- ❌ Market spoofing or deceptive practices
- ❌ Any form of market manipulation

**User Responsibility**: You are solely responsible for compliance with all applicable laws, regulations, and exchange rules in your jurisdiction.

---

## 🤝 Support

For issues, questions, or contributions:

1. Check the troubleshooting section above
2. Review logs in `bot.log`
3. Open an issue on the repository

---

## 🔗 Useful Resources

- [Solana Documentation](https://docs.solana.com/)
- [Raydium SDK](https://github.com/raydium-io/raydium-sdk)
- [Solana.py Documentation](https://michaelhly.github.io/solana-py/)
- [python-telegram-bot Documentation](https://docs.python-telegram-bot.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

**Remember**: This bot trades with real funds on-chain. Always test thoroughly on devnet before mainnet deployment, and never trade more than you can afford to lose. The Raydium integration is not yet complete and requires additional development before production use.

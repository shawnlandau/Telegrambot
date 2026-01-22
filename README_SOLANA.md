# 🪙 Solana Trading Bot - Automated DCA on Jupiter

A production-ready Telegram bot for automated Dollar Cost Averaging (DCA) trading on Solana using Jupiter DEX aggregator.

**Trading Pair**: SOL/SPL Token (configurable)  
**Pattern**: 2×2 (BUY → BUY → SELL → SELL, repeating)  
**Platform**: Solana Mainnet via Jupiter v6

---

## ✨ Features

- 🤖 **Telegram Interface**: Control bot via Telegram commands
- 🔄 **Automated DCA**: Fixed 2×2 trading pattern
- 🌊 **Jupiter Integration**: Best swap routes across all Solana DEXes
- 💰 **Solana Native**: SOL base, any SPL token as quote
- 📊 **Real-time Updates**: Trade notifications and status
- 🛡️ **Built-in Safety**: Slippage protection, balance checks, error recovery
- 📈 **Trade History**: Complete transaction logging with Solscan links
- 🚀 **Railway Ready**: Deploy in 5 minutes

---

## 🚀 Quick Deploy (For New Users)

**Want to deploy your own bot with your own wallet?**

👉 **[Read the USER_DEPLOYMENT_GUIDE.md](USER_DEPLOYMENT_GUIDE.md)** 👈

That guide has everything you need:
- 3-step deployment to Railway
- How to get all required info (wallet, bot token, etc.)
- Complete environment variable setup
- Security best practices
- Troubleshooting help

**Total time**: ~15 minutes from nothing to first trade! ⚡

---

## 📚 Documentation

| Guide | Purpose | Audience |
|-------|---------|----------|
| **[USER_DEPLOYMENT_GUIDE.md](USER_DEPLOYMENT_GUIDE.md)** | Deploy your own bot with your wallet | **Everyone** |
| **[QUICK_DEPLOY_RAILWAY.md](QUICK_DEPLOY_RAILWAY.md)** | 5-minute Railway deployment checklist | Quick reference |
| **[RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md)** | Comprehensive Railway deployment | Detailed walkthrough |
| **[PRODUCTION_DEPLOYMENT_COMPLETE.md](PRODUCTION_DEPLOYMENT_COMPLETE.md)** | Complete production setup & features | Production users |
| **[START_GUIDE.md](START_GUIDE.md)** | How to use the bot after deployment | Bot users |
| **[SIMULATION_MODE_GUIDE.md](SIMULATION_MODE_GUIDE.md)** | Test bot logic without real trades | Testing |
| **[JUPITER_IMPLEMENTATION.md](JUPITER_IMPLEMENTATION.md)** | Jupiter API integration details | Developers |
| **[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)** | Feature implementation checklist | Developers |

---

## 💬 Example Usage

### Configure & Start

```
You: /config
Bot: Enter total liquidity in SOL:

You: 1.0
Bot: ✅ Total liquidity: 1.00 SOL
     Enter trade percentage:

You: 50
Bot: ✅ Trade percentage: 50%
     Trade size: 0.50 SOL
     Enter interval in seconds:

You: 300
Bot: ✅ Configuration saved!
     Use /start to begin trading!

You: /start
Bot: 🚀 Trading session started!
     Pattern: BUY → BUY → SELL → SELL
```

### Monitor Trades

```
Bot: ✅ BUY completed:
     In: 0.500000 SOL
     Out: 500000.000000 MEMESAI
     TX: abc123def456...
     Gas: 50000 units (0.000005 SOL)
     Trades: 1
     
     💰 Balances:
     SOL: 0.500000
     MEMESAI: 500000.000000
     
     ⏰ Next trade in 300 seconds
```

---

## 🏗️ Architecture

### Tech Stack

- **Blockchain**: Solana Mainnet
- **DEX**: Jupiter Aggregator v6
- **Language**: Python 3.11+
- **Bot Framework**: python-telegram-bot
- **Database**: SQLite
- **Deployment**: Railway (or any Python host)

### Key Components

```
bot/
├── main.py              # Telegram bot & commands
├── config.py            # Environment configuration
├── db.py                # Database layer (SQLite)
├── models.py            # Data models
├── raydium_client.py    # Solana/Jupiter integration
└── session_runner.py    # Trading loop (2×2 pattern)
```

---

## 🎯 Trading Pattern

The bot executes a fixed **2×2 pattern**:

```
BUY → BUY → SELL → SELL → (repeat)
```

**Example with 1.0 SOL liquidity, 50% per trade**:

```
Start: 1.0 SOL, 0 TOKEN

Trade 1: BUY  → 0.5 SOL → ~500k TOKEN
         [0.5 SOL, 500k TOKEN]
         ⏲ Wait 5 min

Trade 2: BUY  → 0.5 SOL → ~500k TOKEN
         [0.0 SOL, 1M TOKEN]
         ⏲ Wait 5 min

Trade 3: SELL → Sell ~0.5 SOL worth → SOL
         [0.5 SOL, 500k TOKEN]
         ⏲ Wait 5 min

Trade 4: SELL → Sell ~0.5 SOL worth → SOL
         [1.0 SOL, 0 TOKEN]
         ⏲ Wait 5 min

Repeat from Trade 1...
```

**Why this pattern?**
- Gradual execution (DCA effect)
- Reduces market impact
- Simple and predictable
- Provides consistent liquidity

---

## 🔧 Environment Variables

### Required (6 variables)

```bash
SIMULATION_MODE=false                                           # Production mode
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com            # Solana RPC
WALLET_PRIVATE_KEY=YOUR_BASE58_PRIVATE_KEY                    # Wallet key
QUOTE_TOKEN_ADDRESS=8D9foi1nqfabp8D3uNJCrzt1xkvxq8xHYH8Lxb4fbonk # Token mint
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN                              # From @BotFather
ALLOWED_TELEGRAM_IDS=YOUR_USER_ID                              # Your Telegram ID
```

### Optional (recommended)

```bash
BASE_TOKEN_ADDRESS=So11111111111111111111111111111111111111112  # Native SOL
DEFAULT_SLIPPAGE_BPS=100                                        # 1% slippage
COMMITMENT_LEVEL=confirmed                                      # Transaction finality
LOG_LEVEL=INFO                                                  # Logging detail
```

**See**: [USER_DEPLOYMENT_GUIDE.md](USER_DEPLOYMENT_GUIDE.md#step-3-configure-environment-variables) for detailed setup

---

## 💰 Cost Breakdown

### Hosting (Railway)
- Free tier: $0/month (500 hours)
- Hobby: $5/month (unlimited, recommended)

### Solana Fees
- Network fee: ~0.000005 SOL (~$0.001) per trade
- Jupiter swap fee: ~0.4% of trade amount
- **Total per trade**: ~$0.40 (at 0.5 SOL per trade)

### RPC
- Public RPC: Free (rate limited)
- Helius Free: Free (100 req/sec, recommended)
- Helius Pro: $39/month (unlimited)

**Example monthly cost** (100 trades):
- Railway: $5
- RPC: $0 (Helius free tier)
- Trades: ~$40
- **Total**: ~$45/month

---

## 🔒 Security

### Best Practices

✅ **Do**:
- Use a dedicated trading wallet (not your main wallet)
- Start with small amounts (0.5-1 SOL)
- Keep private keys secure
- Monitor trades regularly
- Use premium RPC for reliability

❌ **Don't**:
- Share your private key
- Trade more than you can afford to lose
- Use main wallet with all funds
- Ignore error notifications
- Skip security updates

### Built-in Safety Features

- ✅ Slippage protection (1% default)
- ✅ Balance validation before trades
- ✅ Transaction confirmation checks
- ✅ Automatic retries with exponential backoff
- ✅ Rate limiting (30 req/min)
- ✅ Graceful error recovery
- ✅ Session state persistence

---

## 📱 Telegram Commands

| Command | Description |
|---------|-------------|
| `/help` | Show all commands |
| `/config` | Configure trading parameters (liquidity, %, interval) |
| `/start` | Start automated trading session |
| `/stop` | Stop trading session |
| `/status` | Show session status and stats |
| `/balance` | Check wallet balances |
| `/history` | View recent trades |

---

## 🔍 Monitoring

### 1. Telegram Notifications
Every trade sends a notification with:
- Trade type (BUY/SELL)
- Amounts in/out
- Transaction hash
- Gas used
- Current balances
- Time to next trade

### 2. Railway Logs
View in Railway dashboard:
- Bot startup messages
- Trade execution logs
- Error messages
- Connection status

### 3. Solscan Explorer
Monitor your wallet on-chain:
- `https://solscan.io/account/YOUR_WALLET_ADDRESS`
- Recent transactions
- Token balances
- Transaction confirmations
- Swap routing details

---

## 🐛 Troubleshooting

### Bot Not Responding

**Check**:
1. Railway logs show "Bot is running..."
2. Telegram bot token is correct
3. Your user ID is in `ALLOWED_TELEGRAM_IDS`

**Fix**: Update environment variables in Railway

### Trades Failing

**Check**:
1. Sufficient SOL for trades + fees
2. Slippage tolerance (increase if needed)
3. RPC connection (try premium RPC)
4. Token liquidity on Jupiter

**Fix**: Adjust config or increase slippage

### "Insufficient Funds"

**Fix**:
1. Check balance: `/balance`
2. Add more SOL to wallet
3. Or reduce trade size: `/config`

**See**: [USER_DEPLOYMENT_GUIDE.md#troubleshooting](USER_DEPLOYMENT_GUIDE.md#-troubleshooting) for complete guide

---

## 🚨 Emergency Procedures

### Stop Trading Immediately
```
Telegram: /stop
Railway: Settings → Pause Service
```

### Withdraw Funds
Bot never withdraws automatically. Your wallet is always yours.
1. `/stop` to stop trading
2. Open your wallet (Phantom)
3. Send funds wherever you want

### Recover from Error
1. `/stop` - Stop session
2. Check logs for error
3. Fix issue (add funds, adjust config)
4. `/config` - Reconfigure
5. `/start` - Resume

---

## 📈 Upgrade Options

### Premium RPC (Recommended)

**Helius** (Best for Solana):
- Free tier: 100 req/sec
- Sign up: https://helius.dev
- Update `SOLANA_RPC_URL` in Railway

**QuickNode**:
- Various plans
- Sign up: https://quicknode.com
- Update `SOLANA_RPC_URL` in Railway

### Scale Trading

After gaining confidence:
1. Increase liquidity (1 SOL → 2 SOL → 5 SOL)
2. Adjust trade percentage (50% → 70%)
3. Reduce interval (300s → 60s for faster trading)
4. Add more tokens (deploy multiple bots)

---

## 🤝 For Developers

### Local Development

```bash
# Clone repo
git clone https://github.com/shawnlandau/Telegrambot.git
cd Telegrambot
git checkout Solana

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure .env
cp .env.example .env
# Edit .env with your values

# Run bot
python -m bot.main
```

### Testing with Simulation Mode

```bash
# In .env, set:
SIMULATION_MODE=true

# Run bot - trades will be simulated (no real blockchain transactions)
python -m bot.main
```

### Project Structure

- `bot/config.py` - Environment configuration
- `bot/models.py` - Data models (session, trades)
- `bot/db.py` - Database layer (SQLite ORM)
- `bot/raydium_client.py` - Solana/Jupiter integration
- `bot/session_runner.py` - Trading loop (2×2 pattern)
- `bot/main.py` - Telegram bot & command handlers

### Key Features

- **Jupiter v6 API**: Best swap routes across all DEXes
- **Async I/O**: Efficient concurrent operations
- **Error Recovery**: Automatic retries with exponential backoff
- **State Persistence**: SQLite database for config & history
- **Logging**: Structured logs with rotation

---

## 📜 License & Disclaimer

### Educational Use

This software is provided **AS-IS** for educational purposes only.

### Financial Disclaimer

- ⚠️ Trading cryptocurrency involves substantial risk
- ⚠️ You are responsible for all trading decisions and losses
- ⚠️ No guarantees of profit or performance
- ⚠️ Only trade with funds you can afford to lose

### Compliance

- You are responsible for compliance with laws in your jurisdiction
- Consult legal/tax professionals before trading
- This bot is for legitimate DCA trading only
- ❌ NOT for wash trading, market manipulation, or illegal activity

**By using this software, you agree to use it responsibly and legally.**

---

## 🎯 Get Started

Ready to deploy your own bot?

1. **Read**: [USER_DEPLOYMENT_GUIDE.md](USER_DEPLOYMENT_GUIDE.md)
2. **Deploy**: Follow the 3-step guide
3. **Configure**: Set your parameters
4. **Trade**: Start with small amounts
5. **Monitor**: Watch and learn
6. **Scale**: Increase gradually

**Time to first trade**: ~15 minutes ⚡

---

## 🌐 Links

- **GitHub Repo**: https://github.com/shawnlandau/Telegrambot
- **Branch**: `Solana` (deploy this branch!)
- **Railway**: https://railway.app
- **Jupiter**: https://jup.ag
- **Solscan**: https://solscan.io
- **Helius RPC**: https://helius.dev

---

## 💬 Support

### Documentation
- [USER_DEPLOYMENT_GUIDE.md](USER_DEPLOYMENT_GUIDE.md) - Complete deployment guide
- [PRODUCTION_DEPLOYMENT_COMPLETE.md](PRODUCTION_DEPLOYMENT_COMPLETE.md) - Production features
- [SIMULATION_MODE_GUIDE.md](SIMULATION_MODE_GUIDE.md) - Testing guide

### Community
- GitHub Issues: https://github.com/shawnlandau/Telegrambot/issues
- Solana Discord: https://discord.gg/solana
- Jupiter Discord: https://discord.gg/jup

---

## ✅ Status

**Branch**: Solana  
**Status**: ✅ Production Ready  
**Last Updated**: January 15, 2026  
**Version**: 1.0

All 10 deployment issues resolved. Bot is tested and working in production.

---

**Happy Trading!** 🚀📈

**Remember**: Start small, monitor closely, scale gradually, and never trade more than you can afford to lose.

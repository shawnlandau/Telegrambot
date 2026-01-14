# SIMULATION MODE - Testing Guide

## 🎯 Problem Solved

**Original Error**:
```
❌ Trade failed: Failed to execute BUY swap: HTTPSConnectionPool(host='quote-api.jup.ag', port=443): 
Max retries exceeded... Failed to resolve 'quote-api.jup.ag'
```

**Root Cause**: The sandbox environment cannot access external APIs (Jupiter) due to network restrictions.

**Solution**: **SIMULATION MODE** - Test the bot's trading logic without requiring external API access!

---

## 🚀 What is Simulation Mode?

Simulation Mode allows you to **test the entire bot workflow** without:
- ❌ Real blockchain transactions
- ❌ External API calls (Jupiter, etc.)
- ❌ Spending actual money
- ❌ Internet access to external services

Instead, it:
- ✅ Simulates all swaps internally
- ✅ Tracks mock balances (starts with 0.75 SOL)
- ✅ Generates realistic fake transaction hashes
- ✅ Simulates prices with ±2% random fluctuations
- ✅ Tests the complete 2×2 trading pattern logic
- ✅ Validates all bot commands and state management

---

## 📊 How It Works

### Initial State
```
SOL Balance: 0.75 SOL
MEMESAI Balance: 0 tokens
Simulated Price: ~1,000,000 MEMESAI per SOL (varies ±2%)
```

### Trading Simulation

When you execute a **BUY**:
1. Bot calculates: `SOL amount × simulated price`
2. Applies slippage: `result × (1 - slippage%)`
3. Updates mock balances:
   - SOL balance decreases
   - MEMESAI balance increases
4. Generates fake TX hash: `e.g., a1b2c3d4...`
5. Logs the simulated trade

When you execute a **SELL**:
1. Bot calculates: `Token amount ÷ simulated price`
2. Applies slippage
3. Updates mock balances:
   - MEMESAI balance decreases
   - SOL balance increases
4. Generates fake TX hash
5. Logs the simulated trade

### Price Simulation
- Base price: ~1,000,000 MEMESAI per SOL
- Each price check adds ±2% random variation
- Simulates realistic market price fluctuations

---

## 🎮 How to Use Simulation Mode

### Step 1: Verify Simulation Mode is Enabled

Check your `.env` file:
```bash
SIMULATION_MODE=true
```

You'll see this when the bot starts:
```
⚠️  SIMULATION MODE ENABLED - No real trades will be executed!
```

### Step 2: Configure Your Trading Session

Open your Telegram bot and send:

```
/config
```

Enter:
- **Total Liquidity**: `0.6` (SOL)
- **Trade Percentage**: `50` (%)
- **Interval**: `300` (seconds = 5 minutes)

Or for faster testing:
- **Total Liquidity**: `0.6`
- **Trade Percentage**: `50`
- **Interval**: `60` (1 minute between trades)

### Step 3: Start Trading (Simulation)

Send:
```
/start
```

The bot will execute the **2×2 trading pattern**:

```
Start: 0.75 SOL, 0 MEMESAI

[BUY #1 - SIMULATED]
  In: 0.3 SOL
  Out: ~300,000 MEMESAI (depends on simulated price)
  TX: abc123def456... (fake hash)
  Balance: 0.45 SOL, 300,000 MEMESAI
  ⏰ Wait 5 minutes (or 1 minute in fast mode)

[BUY #2 - SIMULATED]
  In: 0.3 SOL
  Out: ~300,000 MEMESAI
  TX: 789ghi012jkl... (fake hash)
  Balance: 0.15 SOL, 600,000 MEMESAI
  ⏰ Wait 5 minutes

[SELL #1 - SIMULATED]
  In: ~300,000 MEMESAI
  Out: ~0.3 SOL
  TX: mno345pqr678... (fake hash)
  Balance: 0.45 SOL, 300,000 MEMESAI
  ⏰ Wait 5 minutes

[SELL #2 - SIMULATED]
  In: ~300,000 MEMESAI
  Out: ~0.3 SOL
  TX: stu901vwx234... (fake hash)
  Balance: 0.75 SOL, 0 MEMESAI
  ⏰ Wait 5 minutes

🔄 Cycle repeats...
```

### Step 4: Monitor Simulated Trades

Use these Telegram commands:

```
/status    # Check if session is running
/balance   # Check simulated SOL and MEMESAI balances
/stop      # Stop the trading session
/help      # Show all available commands
```

### Step 5: Check Bot Logs

The bot logs will show `[SIMULATION]` tags:

```
[SIMULATION] BUY executed: 0.3 SOL → 297,800.50 MEMESAI
[SIMULATION] TX: a1b2c3d4e5f6...
[SIMULATION] Balances: 0.450000 SOL, 297800.50 MEMESAI
```

---

## 📋 What Gets Tested

### ✅ Bot Logic
- Session configuration parsing
- 2×2 trading pattern sequencing
- Buy/Sell alternation
- Interval timing
- Balance tracking
- Trade history recording

### ✅ Telegram Integration
- Command handling (`/config`, `/start`, `/stop`, `/status`, `/balance`)
- User authentication (ALLOWED_TELEGRAM_IDS)
- Status message formatting
- Error message display
- Real-time updates

### ✅ Database Operations
- Session creation and storage
- Trade recording (with fake TX hashes)
- Configuration persistence
- Trade history queries

### ✅ Error Handling
- Insufficient balance detection (if you try to trade more than you have)
- Invalid configuration validation
- Session state management
- Graceful error recovery

---

## 🚫 What Does NOT Get Tested

### ❌ Real Blockchain Interaction
- Actual transaction signing
- On-chain confirmation waiting
- Network fee calculation
- RPC timeout handling

### ❌ Jupiter API Integration
- Real price fetching
- Quote retrieval
- Swap transaction building
- Route optimization

### ❌ Real Money Handling
- Actual SOL/token transfers
- Real price slippage
- MEV/front-running scenarios
- Network congestion effects

---

## 🔄 Switching to Production Mode

Once you've tested the bot logic in simulation mode and want to deploy for **real trading**:

### Step 1: Deploy to a Real Server

The bot needs to run on a server with:
- ✅ Full internet access
- ✅ Access to Jupiter API (quote-api.jup.ag)
- ✅ Access to Solana RPC
- ✅ 24/7 uptime

Options:
- **VPS**: DigitalOcean, Linode, AWS EC2, Google Cloud
- **Docker Container**: On any cloud platform
- **Raspberry Pi**: At home with good internet

### Step 2: Update .env for Production

```bash
# DISABLE simulation mode
SIMULATION_MODE=false

# Use a reliable RPC (not free public endpoint for production)
SOLANA_RPC_URL=https://your-premium-rpc-endpoint.com

# Everything else stays the same
WALLET_PRIVATE_KEY=your_key_here
BASE_TOKEN_ADDRESS=So11111111111111111111111111111111111111112
QUOTE_TOKEN_ADDRESS=8D9foi1nqfabp8D3uNJCrzt1xkvxq8xHYH8Lxb4fbonk
TELEGRAM_BOT_TOKEN=your_token
ALLOWED_TELEGRAM_IDS=your_id
```

### Step 3: Start in Production

```bash
cd /path/to/bot
python -m bot.main
```

You'll see:
```
✅ Connected to Solana network
✅ Loaded wallet: AF3y2w...
✅ Trading pair: SOL/MEMESAI
✅ Raydium client initialized
```

**No more simulation warning** - real trades will execute!

### Step 4: Monitor Real Trades

- **Telegram**: Real-time status updates
- **Solscan**: https://solscan.io/account/YOUR_WALLET_ADDRESS
- **Jupiter**: Trade routes and execution details

---

## ⚙️ Advanced: Testing Different Scenarios

### Scenario 1: Fast Testing (1-minute intervals)
```
/config
Total Liquidity: 0.6
Trade Percentage: 50
Interval: 60
```
Complete a full 2×2 cycle in ~4 minutes!

### Scenario 2: Large Trades
```
/config
Total Liquidity: 2.0
Trade Percentage: 50
Interval: 300
```
Test with 1 SOL per trade (simulate whale trading)

### Scenario 3: Small Position Sizing
```
/config
Total Liquidity: 0.2
Trade Percentage: 50
Interval: 300
```
Test with 0.1 SOL per trade (conservative)

### Scenario 4: Aggressive Trading
```
/config
Total Liquidity: 0.6
Trade Percentage: 80
Interval: 60
```
Use 80% of liquidity per trade (high risk simulation)

---

## 🐛 Troubleshooting

### Issue: Bot not responding in Telegram
**Solution**: Check bot logs, ensure `TELEGRAM_BOT_TOKEN` is correct

### Issue: "Insufficient balance" error in simulation
**Solution**: You're trying to trade more than the simulated balance allows. Lower your `Total Liquidity` or adjust `Trade Percentage`

### Issue: Simulated prices don't match real market
**Solution**: This is normal! Simulation uses mock prices (~1M MEMESAI per SOL). Real prices will differ.

### Issue: Want to reset simulated balances
**Solution**: Restart the bot. Simulated balances reset to 0.75 SOL on restart.

---

## 📈 Sample Simulation Run

Here's what a complete simulation looks like:

```
23:15:24 - Starting DEX Trading Bot (Solana Edition)...
23:15:24 - ⚠️  SIMULATION MODE ENABLED
23:15:24 - Wallet: AF3y2w...Em9
23:15:24 - Trading pair: SOL/MEMESAI
23:15:24 - Bot is running...

[User sends /config: 0.6, 50, 60]
23:16:00 - Config saved: 0.6 SOL, 50%, 60s

[User sends /start]
23:16:05 - Session started
23:16:05 - [SIMULATION] Current price: 1M MEMESAI/SOL
23:16:05 - [SIMULATION] BUY: 0.3 SOL → 297,000 MEMESAI
23:16:05 - [SIMULATION] TX: a1b2c3...
23:16:05 - Balance: 0.45 SOL, 297,000 MEMESAI

[Wait 60 seconds]

23:17:05 - [SIMULATION] Current price: 1.02M MEMESAI/SOL
23:17:05 - [SIMULATION] BUY: 0.3 SOL → 303,600 MEMESAI
23:17:05 - [SIMULATION] TX: d4e5f6...
23:17:05 - Balance: 0.15 SOL, 600,600 MEMESAI

[Wait 60 seconds]

23:18:05 - [SIMULATION] Current price: 0.98M MEMESAI/SOL
23:18:05 - [SIMULATION] SELL: 300,000 MEMESAI → 0.306 SOL
23:18:05 - [SIMULATION] TX: g7h8i9...
23:18:05 - Balance: 0.456 SOL, 300,600 MEMESAI

[Wait 60 seconds]

23:19:05 - [SIMULATION] Current price: 1.01M MEMESAI/SOL
23:19:05 - [SIMULATION] SELL: 300,600 MEMESAI → 0.2976 SOL
23:19:05 - [SIMULATION] TX: j0k1l2...
23:19:05 - Balance: 0.7536 SOL, 0 MEMESAI

[Cycle complete - starting over]
```

---

## 🎉 Summary

**Simulation Mode** lets you:
1. ✅ Test the complete bot logic in a sandbox
2. ✅ Verify the 2×2 trading pattern works correctly
3. ✅ Practice using Telegram commands
4. ✅ Validate configuration options
5. ✅ Confirm error handling works
6. ✅ Build confidence before using real money

**When ready for production**:
1. Deploy to a real server with internet access
2. Set `SIMULATION_MODE=false`
3. Use a premium Solana RPC endpoint
4. Start with small amounts (0.1-0.5 SOL)
5. Monitor closely for the first few trades

---

## 📚 Related Documentation

- `START_GUIDE.md` - How to start the bot
- `SETUP_INSTRUCTIONS.md` - Complete setup process
- `JUPITER_IMPLEMENTATION.md` - How Jupiter integration works
- `FIX_SUMMARY.md` - Previous fixes applied
- `FIX_SUMMARY_2.md` - Transaction import fix

---

**Current Status**: ✅ Bot running in SIMULATION MODE  
**Ready to test?**: YES! Go to Telegram and send `/config` then `/start`  
**Ready for real trading?**: Deploy to a real server first, then set `SIMULATION_MODE=false`

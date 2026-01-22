# 🚀 User Deployment Guide: Deploy Your Own Solana Trading Bot

This guide will help you deploy your own instance of the Solana trading bot with **your wallet** and **your settings**.

---

## 📋 What You'll Need (5 Things)

Before you start, gather these 5 items:

### 1. ☁️ Railway Account (Free)
- Sign up at: https://railway.app
- No credit card required for free tier
- Takes 2 minutes

### 2. 💰 Solana Wallet with SOL
- **Recommended**: Phantom Wallet (https://phantom.app)
- **Minimum**: 1-2 SOL (for trading + fees)
- **Recommended**: 5-10 SOL (for serious trading)
- **Important**: Use a DEDICATED wallet, not your main wallet!

### 3. 🤖 Telegram Bot
- Open Telegram and search for **@BotFather**
- Send `/newbot` to create a new bot
- Follow prompts to get your bot token
- Save the token (looks like: `1234567890:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw`)

### 4. 🆔 Your Telegram User ID
- Open Telegram and search for **@userinfobot**
- Send `/start`
- Copy your user ID (e.g., `1826469087`)

### 5. 🪙 Token to Trade
- This guide uses **MEMESAI token** as example
- You can trade ANY Solana SPL token
- You'll need the token's **mint address**
- Find it on: https://solscan.io or https://birdeye.so

---

## 🎯 Quick Start (3 Steps)

### Step 1: Fork or Clone the Repository

#### Option A: Fork on GitHub (Recommended for beginners)
1. Go to: https://github.com/shawnlandau/Telegrambot
2. Click **"Fork"** button (top right)
3. Select your GitHub account
4. Wait for fork to complete (~10 seconds)
5. Your fork is now at: `https://github.com/YOUR_USERNAME/Telegrambot`

#### Option B: Clone to Your Own Repo (For developers)
```bash
# Clone the original repo
git clone https://github.com/shawnlandau/Telegrambot.git my-trading-bot
cd my-trading-bot

# Remove original remote
git remote remove origin

# Create new repo on GitHub (https://github.com/new)
# Then connect to your new repo
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M Solana
git push -u origin Solana
```

---

### Step 2: Deploy to Railway

1. **Go to Railway**: https://railway.app
2. **Click "New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Authorize Railway** to access your GitHub
5. **Select your forked repo**: `YOUR_USERNAME/Telegrambot`
6. **Select branch**: `Solana` (IMPORTANT!)
7. **Click "Deploy Now"**

Railway will start building, but it will **fail** because environment variables are missing. That's expected! Continue to Step 3.

---

### Step 3: Configure Environment Variables

#### 3.1 Get Your Wallet Private Key

**If using Phantom Wallet**:
1. Open Phantom app/extension
2. Click Settings (gear icon)
3. Click **"Security & Privacy"**
4. Click **"Show Private Key"**
5. Enter your password
6. Click **"Copy"**
7. Save it somewhere secure (you'll paste it into Railway)

**Format**: Base58 string, 87-88 characters  
**Example**: `3Z7qX9K2mN8pL4vR5wT6yU1aB3cD9eF7gH8iJ0kL2mN3oP4qR5sT6uV7wX8yZ9A1B2C3D4E5F6G7H8I9J0K`

#### 3.2 Get Token Mint Address

**For MEMESAI (example)**:
- Mint: `8D9foi1nqfabp8D3uNJCrzt1xkvxq8xHYH8Lxb4fbonk`

**For OTHER tokens**:
1. Go to https://solscan.io
2. Search for your token name
3. Copy the **"Token Address"** or **"Mint"**
4. Verify it's the correct token!

#### 3.3 Add Variables in Railway

1. In Railway, go to your deployed service
2. Click **"Variables"** tab
3. Click **"New Variable"** for each of these:

**Required Variables** (6 total):

| Variable Name | Your Value | Where to Get It |
|--------------|------------|-----------------|
| `SIMULATION_MODE` | `false` | Type exactly: `false` (for real trading) |
| `SOLANA_RPC_URL` | `https://api.mainnet-beta.solana.com` | Use this URL (or premium RPC below) |
| `WALLET_PRIVATE_KEY` | `YOUR_KEY_FROM_PHANTOM` | From Step 3.1 above (87-88 chars) |
| `QUOTE_TOKEN_ADDRESS` | `YOUR_TOKEN_MINT_ADDRESS` | From Step 3.2 above (token to buy) |
| `TELEGRAM_BOT_TOKEN` | `YOUR_BOT_TOKEN` | From @BotFather (45+ chars) |
| `ALLOWED_TELEGRAM_IDS` | `YOUR_USER_ID` | From @userinfobot (numbers only) |

**Optional but Recommended** (4 more):

| Variable Name | Recommended Value | Description |
|--------------|-------------------|-------------|
| `BASE_TOKEN_ADDRESS` | `So11111111111111111111111111111111111111112` | Native SOL (leave as-is) |
| `DEFAULT_SLIPPAGE_BPS` | `100` | 1% slippage tolerance |
| `COMMITMENT_LEVEL` | `confirmed` | Transaction finality |
| `LOG_LEVEL` | `INFO` | Logging detail |

#### 3.4 Example Configuration

```bash
# Real trading mode
SIMULATION_MODE=false

# Solana RPC (use default or premium)
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com

# Your wallet private key (KEEP SECURE!)
WALLET_PRIVATE_KEY=3Z7qX9K2mN8pL4vR5wT6yU1aB3cD9eF7gH8iJ0kL2mN3oP4qR5sT6uV7wX8yZ9A1B2C3D4E5F6G7H8I9J0K

# Token to trade (MEMESAI example)
QUOTE_TOKEN_ADDRESS=8D9foi1nqfabp8D3uNJCrzt1xkvxq8xHYH8Lxb4fbonk

# Your Telegram bot
TELEGRAM_BOT_TOKEN=1234567890:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw

# Your Telegram user ID (ONLY YOU can control the bot)
ALLOWED_TELEGRAM_IDS=1826469087

# Optional (recommended)
BASE_TOKEN_ADDRESS=So11111111111111111111111111111111111111112
DEFAULT_SLIPPAGE_BPS=100
COMMITMENT_LEVEL=confirmed
LOG_LEVEL=INFO
```

#### 3.5 Save and Deploy

1. Click **"Save"** or press **Enter** after each variable
2. Railway will **automatically redeploy** after you save
3. Wait 2-3 minutes for build to complete

---

## ✅ Verify Deployment

### Check Railway Logs

1. In Railway, click **"Deployments"** → **"View Logs"**
2. Look for these success messages:

```
✅ Starting DEX Trading Bot (Solana Edition)...
✅ Database initialized at bot_data.db
✅ Connected to Solana network
✅ Solana RPC version: 3.0.14
✅ Loaded wallet: YOUR_WALLET_ADDRESS
✅ Trading pair: SOL/YOUR_TOKEN
✅ Base decimals: 9, Quote decimals: 9
✅ Raydium client initialized
✅ Bot is running...
✅ Application started
```

### Test Telegram Bot

1. Open Telegram
2. Search for your bot (use the username from @BotFather)
3. Send: `/help`

**Expected Response**:
```
🤖 DEX Trading Bot Commands

/help - Show this help message
/config - Configure trading parameters
/start - Start trading session
/status - View current session status
/balance - Check wallet balances
/stop - Stop current session
/history - View trade history

Bot is ready to trade SOL/YOUR_TOKEN on Solana!
```

If you see this, **CONGRATULATIONS!** Your bot is deployed! 🎉

---

## 🎮 Using Your Bot

### 1. Check Balance

Send: `/balance`

Expected output:
```
💰 Current Balances

SOL: 5.000000
YOUR_TOKEN: 0.000000

Wallet: YOUR_WALLET_ADDRESS
View on Solscan: https://solscan.io/account/YOUR_WALLET_ADDRESS
```

### 2. Configure Trading

Send: `/config`

The bot will ask 3 questions:

#### Question 1: Total Liquidity (in SOL)
```
How much SOL do you want to use for trading?

Example values:
- 0.5 SOL = Small testing
- 1.0 SOL = Conservative
- 2.0 SOL = Moderate
- 5.0 SOL = Aggressive
```

**Your answer**: `1.0` (start conservative!)

#### Question 2: Trade Percentage
```
What percentage of your liquidity should each trade use?

Example values:
- 25% = 4 trades possible (conservative)
- 50% = 2 trades possible (moderate)
- 100% = all-in each trade (risky!)
```

**Your answer**: `50` (2 trades per cycle)

#### Question 3: Interval (seconds)
```
How many seconds between trades?

Example values:
- 60 = 1 minute (fast)
- 300 = 5 minutes (moderate)
- 600 = 10 minutes (slow/patient)
```

**Your answer**: `300` (5 minutes is safe)

#### Configuration Saved!
```
✅ Configuration saved!

Total Liquidity: 1.00 SOL
Trade Percentage: 50%
Trade Size: 0.50 SOL
Interval: 300 seconds
```

### 3. Start Trading

Send: `/start`

Expected response:
```
🚀 Trading session started!

Pattern: BUY → BUY → SELL → SELL
First trade executing soon...
```

### 4. Monitor Trades

Within 1-2 minutes, you'll see your first trade:

```
✅ BUY completed:
In: 0.500000 SOL
Out: 500000.000000 YOUR_TOKEN
TX: abc123def456...
Trades: 1

💰 Current Balances:
SOL: 0.500000
YOUR_TOKEN: 500000.000000

⏰ Next trade in 300 seconds
```

### 5. Check Status Anytime

Send: `/status`

```
📊 Session Status

Status: RUNNING
Trades Executed: 2
Current Pattern: STEP_2 (BUY)
Next Trade: in 4 minutes 32 seconds
```

### 6. Stop Trading

Send: `/stop`

```
🛑 Trading session stopped.

📈 Session Summary:
Trades Executed: 8
Total time: 42 minutes
```

---

## 💰 Trading Pattern Explained

The bot uses a **2×2 pattern**: `BUY → BUY → SELL → SELL` (repeats forever)

### Example with 1.0 SOL liquidity, 50% per trade:

```
Start: 1.0 SOL, 0 TOKEN

Trade 1 (BUY):  Spend 0.5 SOL → Get ~500k TOKEN
                [0.5 SOL, 500k TOKEN]
                ⏰ Wait 5 minutes

Trade 2 (BUY):  Spend 0.5 SOL → Get ~500k TOKEN
                [0.0 SOL, 1M TOKEN]
                ⏰ Wait 5 minutes

Trade 3 (SELL): Sell ~0.5 SOL worth of TOKEN → Get SOL
                [0.5 SOL, 500k TOKEN]
                ⏰ Wait 5 minutes

Trade 4 (SELL): Sell ~0.5 SOL worth of TOKEN → Get SOL
                [1.0 SOL, 0 TOKEN]
                ⏰ Wait 5 minutes

Repeat from Trade 1...
```

### Why this pattern?

- **Gradual execution**: Doesn't dump all at once
- **Market making**: Provides liquidity to the market
- **DCA effect**: Averages your entry/exit prices
- **Simple**: Easy to understand and predict

---

## 🔒 Security Best Practices

### 1. **Use a Dedicated Wallet**
- ✅ Create a NEW wallet just for trading
- ✅ Transfer only what you need (1-10 SOL)
- ❌ DON'T use your main wallet with all your funds

### 2. **Protect Your Private Key**
- ✅ Railway encrypts environment variables
- ✅ Keep your .env file secure (never commit to git)
- ❌ DON'T share your private key with anyone
- ❌ DON'T paste it in Discord/Telegram/Twitter

### 3. **Telegram Bot Security**
- ✅ Only YOUR user ID in `ALLOWED_TELEGRAM_IDS`
- ✅ Keep your bot token secret
- ❌ DON'T share bot token publicly

### 4. **Start Small**
- ✅ Test with 0.5-1 SOL first
- ✅ Monitor first few trades carefully
- ✅ Scale up gradually after confidence

### 5. **Monitor Regularly**
- ✅ Check Telegram notifications
- ✅ Review trades on Solscan
- ✅ Monitor Railway logs for errors

---

## ⚙️ Advanced Configuration

### Using Premium RPC (Recommended for High Volume)

**Why upgrade?**
- ✅ No rate limits
- ✅ Faster transaction processing
- ✅ Better uptime
- ✅ Priority routing

**Recommended Providers:**

#### Helius (Best for Solana)
1. Sign up: https://helius.dev
2. Free tier: 100 requests/sec
3. Get your API key
4. Update Railway variable:
   ```
   SOLANA_RPC_URL=https://mainnet.helius-rpc.com/?api-key=YOUR_KEY
   ```

#### QuickNode
1. Sign up: https://quicknode.com
2. Create Solana Mainnet endpoint
3. Copy your HTTP URL
4. Update Railway variable:
   ```
   SOLANA_RPC_URL=https://YOUR-ENDPOINT.solana-mainnet.quiknode.pro/YOUR_TOKEN/
   ```

### Trading Multiple Tokens

To trade different tokens, you can:

**Option 1**: Redeploy with different `QUOTE_TOKEN_ADDRESS`
1. Fork the repo again (or create new Railway service)
2. Deploy with different token address
3. Run multiple bots (one per token)

**Option 2**: Swap tokens manually
1. `/stop` current session
2. Update `QUOTE_TOKEN_ADDRESS` in Railway
3. Railway will redeploy
4. `/config` and `/start` again

### Adjusting Slippage

If trades are failing with "slippage exceeded":

1. Go to Railway → Variables
2. Update `DEFAULT_SLIPPAGE_BPS`
   - `100` = 1% (default)
   - `150` = 1.5% (more tolerance)
   - `200` = 2% (high volatility)
3. Save and redeploy

---

## 💸 Cost Breakdown

### Railway Hosting
- **Free Tier**: $0/month (500 hours, usually enough)
- **Hobby Plan**: $5/month (unlimited, recommended)
- **Pro Plan**: $20/month (high volume)

### Solana Transaction Fees
- **Network Fee**: ~0.000005 SOL (~$0.001 per trade)
- **Jupiter Swap Fee**: ~0.4% of trade amount

**Example Cost per Trade** (0.5 SOL @ $200/SOL):
- Network fee: ~0.000005 SOL (~$0.001)
- Jupiter fee: ~0.002 SOL (~$0.40)
- **Total**: ~$0.40 per trade

**Monthly Cost Example** (100 trades):
- Railway: $5.00
- Helius RPC: $0.00 (free tier)
- Transaction fees: ~$40.00
- **Total**: ~$45/month

### Profitability Depends On:
- Token volatility
- Trading frequency
- Market conditions
- Your strategy execution

---

## 🐛 Troubleshooting

### Bot Not Responding

**Problem**: Bot doesn't respond to `/help`

**Check**:
1. Telegram bot token is correct
2. Your user ID is in `ALLOWED_TELEGRAM_IDS`
3. Railway logs show "Bot is running..."

**Fix**:
```bash
# In Railway → Variables
# Verify these are set correctly:
TELEGRAM_BOT_TOKEN=<YOUR_REAL_TOKEN>
ALLOWED_TELEGRAM_IDS=<YOUR_REAL_ID>
```

### Insufficient Funds Error

**Problem**: "Insufficient quote token balance"

**Fix**:
1. Check balance: `/balance`
2. Add more SOL to your wallet
3. Or reduce trade size in `/config`
4. Stop session: `/stop`
5. Reconfigure: `/config` with lower liquidity
6. Restart: `/start`

### Transaction Failed

**Problem**: "Trade failed: Transaction reverted"

**Possible Causes**:
- Slippage too low (increase `DEFAULT_SLIPPAGE_BPS`)
- Network congestion (try premium RPC)
- Pool liquidity low (trade smaller amounts)
- Price impact too high

**Fix**:
1. Increase slippage to 150-200 bps
2. Reduce trade size
3. Use premium RPC (Helius/QuickNode)
4. Check token liquidity on Birdeye/Dexscreener

### Railway Build Failed

**Problem**: Build fails in Railway

**Check Logs** for:
- Missing environment variables
- Python version issues
- Dependency conflicts

**Fix**:
1. Verify all 6 required variables are set
2. Check branch is `Solana` (not `main`)
3. Try manual redeploy: Settings → Redeploy

### Invalid Token Error

**Problem**: "InvalidToken: Unauthorized"

**Fix**:
```bash
# Your bot token is wrong or expired
# Get new token from @BotFather:
1. Open @BotFather in Telegram
2. Send /mybots
3. Select your bot
4. Click "API Token"
5. Copy and paste into Railway
```

---

## 📊 Monitoring Your Bot

### 1. Telegram Commands

| Command | What It Shows |
|---------|---------------|
| `/status` | Current session state, trades executed, next trade |
| `/balance` | Current SOL and token balances |
| `/history` | Last 10 trades with details |
| `/help` | All available commands |

### 2. Railway Logs

**Access**: Railway → Service → Deployments → View Logs

**Look for**:
```
[INFO] BUY: Swapping 0.5 SOL for TOKEN
[INFO] Getting Jupiter quote...
[INFO] Transaction sent: abc123...
[INFO] BUY swap successful
```

### 3. Solscan Explorer

**Your Wallet**: `https://solscan.io/account/YOUR_WALLET_ADDRESS`

**Monitor**:
- Recent transactions
- Token balances
- Transaction success/failure
- Swap details
- Fees paid

### 4. Set Up Alerts (Optional)

**Telegram Notifications**: Already built-in! Every trade sends notification

**Email Alerts** (via Railway):
1. Railway → Service → Settings
2. Enable "Deployment Notifications"
3. Add your email

---

## 🔄 Updating Your Bot

When the original repo gets updates:

### If You Forked:

1. Go to your fork on GitHub
2. Click **"Sync fork"** button
3. Click **"Update branch"**
4. Railway auto-deploys the update

### If You Cloned:

```bash
# Add original repo as upstream
git remote add upstream https://github.com/shawnlandau/Telegrambot.git

# Fetch updates
git fetch upstream

# Merge updates into your Solana branch
git checkout Solana
git merge upstream/Solana

# Push to your repo (Railway auto-deploys)
git push origin Solana
```

---

## 🚨 Emergency Procedures

### Stop Trading Immediately

**In Telegram**: Send `/stop`

**In Railway**: 
1. Go to your service
2. Click **"Settings"**
3. Click **"Pause Service"** (temporary stop)
4. Or click **"Delete Service"** (permanent removal)

### Recover from Error

1. `/stop` - Stop trading session
2. Check Railway logs for error
3. Fix the issue (add funds, adjust config, etc.)
4. `/config` - Reconfigure if needed
5. `/start` - Resume trading

### Withdraw All Funds

The bot **NEVER** withdraws funds automatically. Your wallet is always yours.

**To withdraw**:
1. `/stop` - Stop trading
2. Open your wallet (Phantom)
3. Send SOL and tokens wherever you want
4. Bot has no control over your funds

---

## 📱 Example Deployment Session

Here's a complete walkthrough:

### Prerequisites Checklist:
- [x] Railway account created
- [x] Phantom wallet with 2 SOL
- [x] Telegram bot created (@BotFather)
- [x] Telegram user ID (from @userinfobot)
- [x] Token mint address (MEMESAI example)

### Deployment Steps:

```
1. Fork repo on GitHub
   ✅ Forked to: myusername/Telegrambot

2. Deploy to Railway
   ✅ Created new project
   ✅ Selected: myusername/Telegrambot
   ✅ Branch: Solana
   ✅ Deployed

3. Add environment variables (Railway)
   ✅ SIMULATION_MODE=false
   ✅ SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
   ✅ WALLET_PRIVATE_KEY=3Z7qX9K2mN8pL4vR5wT6yU...
   ✅ QUOTE_TOKEN_ADDRESS=8D9foi1nqfabp8D3uNJCrzt1xkvxq8xHYH8Lxb4fbonk
   ✅ TELEGRAM_BOT_TOKEN=1234567890:AAHdqTc...
   ✅ ALLOWED_TELEGRAM_IDS=1826469087
   ✅ Saved → Auto-redeploying...

4. Verify deployment (Railway logs)
   ✅ Bot is running...
   ✅ Wallet loaded: 7x4B...3kL9
   ✅ Trading pair: SOL/MEMESAI

5. Test Telegram bot
   Me: /help
   Bot: 🤖 DEX Trading Bot Commands...
   ✅ Bot responding!

6. Check balance
   Me: /balance
   Bot: SOL: 2.000000, MEMESAI: 0.000000
   ✅ Wallet connected!

7. Configure trading
   Me: /config
   Bot: Enter total liquidity...
   Me: 1.0
   Bot: Enter trade percentage...
   Me: 50
   Bot: Enter interval...
   Me: 300
   Bot: ✅ Configuration saved!
   ✅ Configured!

8. Start trading
   Me: /start
   Bot: 🚀 Trading session started!
   ✅ Trading!

9. First trade completed
   Bot: ✅ BUY completed: In: 0.5 SOL, Out: 500k MEMESAI
   ✅ Working perfectly!

10. Monitor on Solscan
    https://solscan.io/account/7x4B...3kL9
    ✅ Transaction confirmed on-chain!
```

**Total Time**: ~15 minutes from start to first trade! 🎉

---

## 🎓 Learning Resources

### Solana Basics
- **Solana Docs**: https://docs.solana.com
- **Solana Cookbook**: https://solanacookbook.com
- **Phantom Wallet Guide**: https://phantom.app/learn

### Jupiter DEX Aggregator
- **Jupiter Docs**: https://station.jup.ag
- **Jupiter API**: https://station.jup.ag/docs/apis/swap-api
- **Jupiter Discord**: https://discord.gg/jup

### Trading & DCA
- **What is DCA?**: https://www.investopedia.com/terms/d/dollarcostaveraging.asp
- **Market Making Basics**: https://www.paradigm.xyz/2021/04/understanding-automated-market-makers-part-1-price-impact
- **MEV on Solana**: https://www.jito.wtf/

### Python & Telegram Bots
- **python-telegram-bot**: https://docs.python-telegram-bot.org/
- **asyncio Tutorial**: https://realpython.com/async-io-python/
- **Web3 Python**: https://web3py.readthedocs.io/

---

## 🤝 Community & Support

### Get Help

1. **GitHub Issues**: https://github.com/shawnlandau/Telegrambot/issues
2. **Railway Docs**: https://docs.railway.app
3. **Solana Discord**: https://discord.gg/solana
4. **Jupiter Discord**: https://discord.gg/jup

### Share Your Experience

If you successfully deploy:
- Share on Twitter/X with `#SolanaTradingBot`
- Star the repo on GitHub
- Help others in the community

### Contribute

Found a bug or want to add features?
1. Fork the repo
2. Make your changes
3. Submit a pull request

---

## ⚖️ Legal Disclaimer

**IMPORTANT**: Please read carefully!

### Financial Disclaimer

- This software is provided **AS-IS** for educational purposes
- **You are responsible** for all trading decisions and losses
- **No guarantees** of profit or performance
- **Cryptocurrency trading involves substantial risk** of loss
- Only trade with funds you can afford to lose
- Past performance does not indicate future results

### Compliance

- **You are responsible** for compliance with laws in your jurisdiction
- Consult with legal/tax professionals before trading
- Some jurisdictions prohibit or restrict crypto trading
- Know Your Customer (KYC) and Anti-Money Laundering (AML) laws may apply

### This Bot Is For:

- ✅ Legitimate DCA (Dollar Cost Averaging) trading
- ✅ Personal trading automation
- ✅ Learning and education
- ✅ Market making in one wallet

### This Bot Is NOT For:

- ❌ Wash trading between related accounts
- ❌ Market manipulation or spoofing
- ❌ Creating artificial volume
- ❌ Pump-and-dump schemes
- ❌ Any illegal activity

**By deploying this bot, you agree to use it responsibly and legally.**

---

## 🎉 You're Ready!

You now have everything you need to:
- ✅ Deploy your own Solana trading bot
- ✅ Configure it with your wallet
- ✅ Trade any Solana token
- ✅ Monitor and manage trades
- ✅ Scale up safely

### Next Steps:

1. **Deploy Now**: Follow the 3-step quick start above
2. **Start Small**: Test with 0.5-1 SOL first
3. **Monitor Closely**: Watch first few trades
4. **Scale Gradually**: Increase as you gain confidence
5. **Share & Learn**: Help others in the community

---

## 📞 Final Checklist Before First Trade

Before you send `/start`, verify:

- [ ] Bot responds to `/help`
- [ ] `/balance` shows correct SOL amount
- [ ] Railway logs show "Bot is running..."
- [ ] You configured with `/config`
- [ ] You're starting with ≤1 SOL (testing)
- [ ] You have 0.1-0.2 SOL extra for fees
- [ ] You saved your wallet private key securely
- [ ] You understand the 2×2 pattern
- [ ] You know how to `/stop` if needed
- [ ] You have Solscan open to monitor

**If all boxes checked**: Send `/start` and watch the magic happen! 🚀

---

**Happy Trading!** 🎊

**Remember**: Start small, monitor closely, scale gradually, and never trade more than you can afford to lose.

---

**Last Updated**: January 15, 2026  
**Version**: 1.0  
**Branch**: Solana  
**Status**: Production Ready ✅

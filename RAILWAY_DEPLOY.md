# 🚂 Railway Deployment Guide - Solana Trading Bot

This guide will walk you through deploying your Solana trading bot to Railway for production use.

---

## 📋 Prerequisites

Before deploying, ensure you have:
- ✅ GitHub account with your bot repository
- ✅ Railway account (sign up at https://railway.app)
- ✅ Solana wallet private key (base58 format)
- ✅ Telegram bot token from BotFather
- ✅ Your Telegram user ID
- ✅ SOL in your wallet (recommend 1-5 SOL for trading + fees)

---

## 🚀 Step-by-Step Deployment

### Step 1: Push Code to GitHub

All deployment files are already committed. Verify your branch is up to date:

```bash
git status
git push origin Solana
```

**Your repository**: https://github.com/shawnlandau/Telegrambot  
**Branch**: `Solana`

---

### Step 2: Connect Railway to GitHub

1. Go to https://railway.app
2. Click **"Start a New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub account
5. Select your repository: `shawnlandau/Telegrambot`
6. Select branch: **`Solana`**
7. Click **"Deploy Now"**

Railway will automatically:
- ✅ Detect Python project
- ✅ Install dependencies from `requirements.txt`
- ✅ Use the Procfile to start the bot
- ✅ Provision a persistent environment

---

### Step 3: Configure Environment Variables

After deployment starts, go to the **Variables** tab and add these environment variables:

#### **REQUIRED VARIABLES**

```bash
# === CRITICAL: Production Mode ===
SIMULATION_MODE=false

# === Solana Configuration ===
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
# ⚠️ RECOMMENDED: Use a premium RPC for production (see RPC section below)

# === Wallet Configuration ===
WALLET_PRIVATE_KEY=YOUR_BASE58_PRIVATE_KEY_HERE
# ⚠️ PASTE YOUR ACTUAL PRIVATE KEY FROM PHANTOM

# === Token Configuration ===
BASE_TOKEN_ADDRESS=So11111111111111111111111111111111111111112
QUOTE_TOKEN_ADDRESS=8D9foi1nqfabp8D3uNJCrzt1xkvxq8xHYH8Lxb4fbonk

# === Telegram Configuration ===
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
ALLOWED_TELEGRAM_IDS=YOUR_TELEGRAM_USER_ID_HERE

# === DEX Configuration (Optional - Jupiter doesn't require pool ID) ===
RAYDIUM_PROGRAM_ID=675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8
RAYDIUM_POOL_ID=

# === Bot Configuration (Optional - Defaults Provided) ===
DATABASE_PATH=bot_data.db
LOG_LEVEL=INFO
MAX_TRADES_PER_SESSION=1000
MAX_RETRIES=3
SKIP_PREFLIGHT=false
COMMITMENT_LEVEL=confirmed
DEFAULT_SLIPPAGE_BPS=100
RPC_TIMEOUT=30
RPC_MAX_RETRIES=3
```

#### **How to Add Variables in Railway**

1. Click on your deployed service
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**
4. For each variable above:
   - Enter the variable name (e.g., `SIMULATION_MODE`)
   - Enter the value (e.g., `false`)
   - Click **"Add"**

**⚠️ CRITICAL**: Make sure `SIMULATION_MODE=false` for real trading!

---

### Step 4: Recommended - Use Premium Solana RPC

For production, the free public RPC (`api.mainnet-beta.solana.com`) has rate limits and can be unreliable. Use a premium RPC service:

#### **Helius** (Recommended)
1. Sign up at https://helius.xyz
2. Create a new project
3. Get your RPC URL: `https://mainnet.helius-rpc.com/?api-key=YOUR_KEY`
4. Set in Railway: `SOLANA_RPC_URL=https://mainnet.helius-rpc.com/?api-key=YOUR_KEY`

#### **QuickNode**
1. Sign up at https://www.quicknode.com
2. Create a Solana Mainnet endpoint
3. Get your RPC URL: `https://YOUR-ENDPOINT.solana-mainnet.quiknode.pro/YOUR_TOKEN/`
4. Set in Railway: `SOLANA_RPC_URL=https://YOUR-ENDPOINT.solana-mainnet.quiknode.pro/YOUR_TOKEN/`

#### **Alchemy**
1. Sign up at https://www.alchemy.com
2. Create a Solana app
3. Get your RPC URL from dashboard
4. Set in Railway

**Free Tier Limits**:
- Helius: 100 req/sec free tier
- QuickNode: Free trial, then paid
- Alchemy: Generous free tier

---

### Step 5: Verify Deployment

After adding all environment variables, Railway will automatically redeploy.

**Check Logs**:
1. Go to the **"Deployments"** tab
2. Click on the latest deployment
3. View **"Logs"** to see bot output

**Look for these success messages**:
```
✅ Starting DEX Trading Bot (Solana Edition)...
✅ Connected to Solana network
✅ Loaded wallet: AF3y2w...
✅ Trading pair: SOL/MEMESAI
✅ Raydium client initialized
✅ Bot is running...
✅ Application started
```

**⚠️ You should NOT see**:
```
⚠️  SIMULATION MODE ENABLED
```
If you see this, your `SIMULATION_MODE` is still set to `true`!

---

### Step 6: Test the Bot

1. Open Telegram and find your bot
2. Send `/start` to begin
3. Send `/help` to see all commands

**Configure Trading**:
```
/config

Enter:
- Total Liquidity: 0.5 (start small!)
- Trade Percentage: 50
- Interval: 300 (5 minutes)
```

**Start Trading**:
```
/start
```

**Monitor**:
- Watch Telegram for trade updates
- Check logs in Railway dashboard
- View transactions on Solscan: https://solscan.io/account/YOUR_WALLET_ADDRESS

---

## 🔒 Security Best Practices

### **1. Wallet Security**
- ✅ Use a **dedicated trading wallet** (don't use your main wallet)
- ✅ Start with **small amounts** (1-5 SOL)
- ✅ Never share your private key
- ✅ Store private key securely (Railway encrypts environment variables)

### **2. Railway Security**
- ✅ Environment variables are encrypted at rest
- ✅ Never commit `.env` to git (already in .gitignore)
- ✅ Only you can access your Railway project variables
- ✅ Use Railway's built-in secrets management

### **3. Bot Security**
- ✅ `ALLOWED_TELEGRAM_IDS` restricts bot access to your user ID only
- ✅ Only authorized users can control the bot
- ✅ All trades require your Telegram commands

### **4. Monitoring**
- ✅ Enable Railway logs
- ✅ Monitor Telegram notifications
- ✅ Check Solscan for all transactions
- ✅ Set up alerts (optional)

---

## 📊 Railway Dashboard Overview

### **Deployments Tab**
- View deployment history
- See build logs
- Monitor deployment status
- Roll back to previous versions

### **Logs Tab**
- Real-time bot logs
- Error messages
- Trade execution logs
- System messages

### **Metrics Tab**
- CPU usage
- Memory usage
- Network traffic
- Uptime statistics

### **Settings Tab**
- Environment variables
- Deployment triggers
- Custom domains (if needed)
- Project settings

---

## 💰 Pricing

**Railway Pricing** (as of 2024):
- **Free Tier**: $5 worth of usage per month
- **Pro Plan**: $20/month for additional resources
- **Pay-as-you-go**: After free tier

**Estimated Bot Usage**:
- Very low CPU/memory usage
- Should easily fit in free tier
- Typical cost: $0-5/month

**Solana Costs** (what you actually pay for trading):
- Transaction fees: ~0.000005 SOL per transaction (~$0.0005)
- Jupiter swap fees: 0.4% of trade amount
- Total cost per trade: ~0.4% + $0.0005

---

## 🔧 Troubleshooting

### **Bot Not Starting**

**Check Logs** for errors:
```
Railway Dashboard → Deployments → View Logs
```

**Common Issues**:
1. **Missing environment variables**
   - Solution: Add all required variables in Variables tab

2. **Invalid private key format**
   - Error: `Failed to load Solana keypair`
   - Solution: Ensure key is base58 encoded (from Phantom)

3. **Invalid Telegram token**
   - Error: `Unauthorized`
   - Solution: Check TELEGRAM_BOT_TOKEN is correct

4. **RPC connection failed**
   - Error: `Failed to connect to Solana RPC`
   - Solution: Check SOLANA_RPC_URL or use premium RPC

### **Bot Stops Trading**

**Check**:
1. Insufficient SOL balance
2. RPC rate limits (switch to premium RPC)
3. Network issues (temporary, will auto-retry)
4. Wallet/token account issues

**Solution**: Check logs in Railway dashboard

### **Trades Not Executing**

**Possible Causes**:
1. `SIMULATION_MODE=true` (should be `false`)
2. Insufficient balance
3. Jupiter API issues (check logs)
4. Slippage too low (increase DEFAULT_SLIPPAGE_BPS)

### **Telegram Bot Not Responding**

**Check**:
1. Bot token is correct
2. Your Telegram ID is in ALLOWED_TELEGRAM_IDS
3. Bot is running (check Railway logs)

---

## 🔄 Updating Your Bot

### **Deploy New Code**

1. Make changes locally
2. Commit to git:
   ```bash
   git add .
   git commit -m "Your update description"
   git push origin Solana
   ```
3. Railway will **automatically redeploy**!

### **Rollback to Previous Version**

1. Go to **Deployments** tab
2. Find the previous working deployment
3. Click **"Redeploy"**

---

## 📈 Monitoring Your Trading

### **Telegram Notifications**
You'll receive real-time updates:
```
✅ BUY completed:
In: 0.300000 SOL
Out: 305,234.56 MEMESAI
TX: abc123def456...
Trades: 1
```

### **Solscan Dashboard**
Monitor all transactions:
1. Go to https://solscan.io
2. Enter your wallet address: `AF3y2wckyKF5BDn92M284snihVSt1YFbhsqUo6DUdEm9`
3. View all swaps, fees, and balances in real-time

### **Railway Logs**
Monitor bot health:
```
[TIMESTAMP] - INFO - BUY: Swapping 0.3 SOL for MEMESAI
[TIMESTAMP] - INFO - Getting Jupiter quote...
[TIMESTAMP] - INFO - Expected output: 305234.56 MEMESAI
[TIMESTAMP] - INFO - BUY swap successful: abc123...
```

---

## 🎯 Production Checklist

Before going live, verify:

- [ ] `SIMULATION_MODE=false` ✅
- [ ] Premium Solana RPC configured (recommended)
- [ ] Wallet has sufficient SOL (1-5 SOL recommended)
- [ ] WALLET_PRIVATE_KEY is correct (base58)
- [ ] TELEGRAM_BOT_TOKEN is correct
- [ ] ALLOWED_TELEGRAM_IDS contains your Telegram ID
- [ ] Bot starts without errors (check logs)
- [ ] Bot responds to `/help` in Telegram
- [ ] Tested with small trades first (0.1-0.5 SOL)

---

## 📞 Getting Help

### **Railway Support**
- Documentation: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

### **Bot Issues**
- Check logs in Railway dashboard
- Review error messages
- Test in simulation mode first
- Verify all environment variables

### **Solana/Jupiter Issues**
- Jupiter Discord: https://discord.gg/jup
- Solana Discord: https://discord.gg/solana
- Check Solscan for transaction details

---

## 🚀 Quick Deploy Summary

**TL;DR**:
1. Go to https://railway.app
2. Click "Deploy from GitHub"
3. Select `shawnlandau/Telegrambot` (branch: `Solana`)
4. Add environment variables (see Step 3 above)
5. Set `SIMULATION_MODE=false`
6. Wait for deployment to complete
7. Check logs for success messages
8. Open Telegram and test with `/config` then `/start`
9. Start with small trades (0.1-0.5 SOL)
10. Monitor via Telegram, Railway logs, and Solscan

---

## ✅ Deployment Complete!

Once deployed, your bot will:
- ✅ Run 24/7 on Railway infrastructure
- ✅ Execute real Jupiter swaps on Solana
- ✅ Automatically retry on failures
- ✅ Persist data in Railway storage
- ✅ Send real-time updates to Telegram

**You're ready to trade SOL/MEMESAI on production!** 🎉

---

## 📚 Related Documentation

- `SIMULATION_MODE_GUIDE.md` - How simulation mode works
- `START_GUIDE.md` - How to use the bot
- `SETUP_INSTRUCTIONS.md` - Initial setup guide
- `JUPITER_IMPLEMENTATION.md` - Technical details
- `README_SOLANA.md` - Solana-specific README

---

**Happy Trading!** 🚀💰

Remember: Always start with small amounts and monitor closely!

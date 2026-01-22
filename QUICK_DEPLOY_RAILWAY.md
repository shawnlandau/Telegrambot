# 🚀 Quick Deploy to Railway - Checklist

## ✅ Pre-Deployment Checklist

Before you start, have these ready:

- [ ] GitHub repository pushed: https://github.com/shawnlandau/Telegrambot
- [ ] Branch: `Solana` ✅ (already pushed)
- [ ] Railway account (sign up at https://railway.app)
- [ ] Wallet private key (base58 from Phantom)
- [ ] Telegram bot token (from BotFather)
- [ ] Your Telegram user ID (from @userinfobot)
- [ ] SOL in wallet (recommend 1-5 SOL)

---

## 🎯 Deploy in 5 Minutes

### 1️⃣ Create Railway Project (2 min)

1. Go to https://railway.app
2. Click **"Start a New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway → Select `shawnlandau/Telegrambot`
5. Select branch: **`Solana`**
6. Click **"Deploy Now"**

✅ Railway will auto-detect Python and start building!

---

### 2️⃣ Add Environment Variables (2 min)

Click **"Variables"** tab and add these **6 REQUIRED** variables:

```bash
# 1. CRITICAL - Production Mode
SIMULATION_MODE=false

# 2. Solana RPC
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com

# 3. Your Wallet Private Key (from Phantom)
WALLET_PRIVATE_KEY=YOUR_BASE58_KEY_HERE

# 4. MEMESAI Token Address (already set)
QUOTE_TOKEN_ADDRESS=8D9foi1nqfabp8D3uNJCrzt1xkvxq8xHYH8Lxb4fbonk

# 5. Telegram Bot Token (from BotFather)
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE

# 6. Your Telegram User ID (from @userinfobot)
ALLOWED_TELEGRAM_IDS=YOUR_USER_ID_HERE
```

**Optional but recommended** (copy from `.env.example` if needed):
- `BASE_TOKEN_ADDRESS=So11111111111111111111111111111111111111112`
- `RAYDIUM_PROGRAM_ID=675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8`
- `DEFAULT_SLIPPAGE_BPS=100`
- `COMMITMENT_LEVEL=confirmed`

✅ Railway will auto-redeploy after adding variables!

---

### 3️⃣ Verify Deployment (1 min)

Go to **"Deployments"** tab → Click latest deployment → **"View Logs"**

**Look for**:
```
✅ Connected to Solana network
✅ Loaded wallet: AF3y2w...
✅ Trading pair: SOL/MEMESAI
✅ Bot is running...
```

**⚠️ Should NOT see**:
```
⚠️ SIMULATION MODE ENABLED
```

If you see simulation warning, set `SIMULATION_MODE=false` in Variables!

---

### 4️⃣ Test in Telegram (1 min)

1. Open your Telegram bot
2. Send `/help` (should respond)
3. Send `/config`:
   ```
   Total Liquidity: 0.5  (start small!)
   Trade Percentage: 50
   Interval: 300
   ```
4. Send `/start`

**You should see**:
```
✅ BUY completed:
In: 0.250000 SOL
Out: ~250,000 MEMESAI
TX: abc123...
```

✅ **DEPLOYED!** Your bot is trading on Solana mainnet!

---

## 🔒 Security Notes

- ✅ Railway encrypts all environment variables
- ✅ Only you can access your project
- ✅ Never commit `.env` to GitHub (already in .gitignore)
- ✅ Use a dedicated trading wallet (not your main wallet)
- ✅ Start with small amounts (0.5-1 SOL)

---

## 🚨 Important: Premium RPC (Recommended)

Free public RPC has rate limits. For production, use premium:

**Helius** (Recommended - Best for Solana):
1. Sign up: https://helius.xyz
2. Get free tier: 100 req/sec
3. Copy RPC URL: `https://mainnet.helius-rpc.com/?api-key=YOUR_KEY`
4. Update in Railway Variables: `SOLANA_RPC_URL=your_helius_url`

**Why Premium RPC?**
- ✅ No rate limits
- ✅ Faster execution
- ✅ Better reliability
- ✅ Priority access
- ✅ Free tier usually sufficient

---

## 📊 Monitor Your Bot

### Telegram
Real-time trade notifications

### Railway Logs
```
Deployments → View Logs
```

### Solscan
https://solscan.io/account/YOUR_WALLET_ADDRESS
View all transactions in real-time

---

## 🔧 Troubleshooting

### Bot Not Starting?
**Check logs** in Railway dashboard

**Common issues**:
1. Missing environment variables → Add them
2. Wrong private key format → Use base58 from Phantom
3. Invalid Telegram token → Verify from BotFather

### Trades Not Executing?
1. Check `SIMULATION_MODE=false`
2. Verify wallet has SOL
3. Check Railway logs for errors

### Bot Stopped?
Railway auto-restarts on failure (max 10 retries)
Check logs to see why it stopped

---

## 💰 Costs

**Railway**:
- Free tier: $5/month credit (enough for bot)
- Bot uses minimal resources
- Estimated: $0-5/month

**Solana**:
- Transaction fee: ~0.000005 SOL (~$0.0005)
- Jupiter fee: ~0.4% of trade
- Total: ~0.4% per trade

---

## ✅ You're Live!

Your bot is now:
- ✅ Running 24/7 on Railway
- ✅ Trading SOL/MEMESAI on mainnet
- ✅ Using Jupiter for best prices
- ✅ Auto-restarting on failures
- ✅ Sending Telegram notifications

**Start with small trades and monitor closely!**

---

## 📚 Full Documentation

See `RAILWAY_DEPLOY.md` for complete guide including:
- Detailed setup instructions
- All configuration options
- Advanced troubleshooting
- Monitoring best practices
- Security recommendations
- Update procedures

---

## 🎉 Happy Trading!

Your Solana DEX bot is deployed and ready to trade!

Monitor via:
- Telegram (real-time updates)
- Railway logs (bot health)
- Solscan (transaction history)

**Remember**: Always start small and monitor closely! 🚀

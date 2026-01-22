# 🚨 Bot Not Responding - Complete Diagnosis

## Symptom: `/test` shows nothing (no response at all)

This means the bot is either:
- Not running
- Not receiving messages
- Wrong Telegram bot token
- Authorization blocking you

---

## Step 1: Check Railway Deployment Status

### In Railway Dashboard:

1. Go to your service
2. Click **"Deployments"** tab
3. Check latest deployment:

**Look for**:
```
✅ Build successful
✅ Deploying commit: 4f71c05
✅ Deployment live
```

**If you see**:
```
❌ Build failed
❌ Deployment failed
🟡 Building...
🟡 Deploying...
```

Then the bot isn't running yet. **Wait** for it to finish.

---

## Step 2: Check Railway Logs

### In Railway Dashboard:

1. Click **"Deployments"** → Latest deployment
2. Click **"View Logs"**

### Look for Success Messages:
```
✅ Starting DEX Trading Bot (Solana Edition)...
✅ Database initialized
✅ Raydium client initialized
✅ Session runner initialized
✅ Config conversation handler registered
✅ Bot is running...
```

### Look for Error Messages:
```
❌ Failed to initialize bot:
❌ ValueError: Required environment variable 'X' is not set
❌ Invalid token
❌ telegram.error.InvalidToken
```

---

## Step 3: Verify Environment Variables

### In Railway → Variables, check these are set:

**Required**:
```
SIMULATION_MODE=true  (or false)
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
WALLET_PRIVATE_KEY=<your key>
QUOTE_TOKEN_ADDRESS=8D9foi1nqfabp8D3uNJCrzt1xkvxq8xHYH8Lxb4fbonk
TELEGRAM_BOT_TOKEN=<your token>
ALLOWED_TELEGRAM_IDS=<your user id>
```

**Common Issues**:

❌ **Wrong Telegram Bot Token**:
```
# Check your token matches what BotFather gave you
# Format: 1234567890:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
```

❌ **Wrong Telegram User ID**:
```
# Get your ID from @userinfobot in Telegram
# Send /start to @userinfobot
# Copy the number (e.g., 1826469087)
# Make sure it matches ALLOWED_TELEGRAM_IDS in Railway
```

---

## Step 4: Test Bot from BotFather

### Find Your Bot's Username:

1. Open Telegram
2. Search for **@BotFather**
3. Send `/mybots`
4. Select your bot
5. Click **"API Token"** to verify token
6. Note the bot's **username** (e.g., @YourBotName)

### Test Direct Message:

1. In Telegram, search for your bot's username
2. Click **"Start"** button (or send `/start`)
3. Send `/help`
4. Send `/test`

**If still no response**, the bot token in Railway is wrong.

---

## Step 5: Check if Bot is Even Running

### Railway Shell (if available):

If Railway provides shell access:
```bash
ps aux | grep python
# Should show: python -m bot.main
```

### Check Process Logs:
```
Railway → Deployments → Logs → Look for:
"Bot is running..."
```

If you DON'T see this, the bot crashed during startup.

---

## Step 6: Common Fixes

### Fix 1: Redeploy
```
Railway → Service → Settings → Redeploy
Wait 2-3 minutes
Test /help again
```

### Fix 2: Restart Service
```
Railway → Service → Settings → Restart
Wait 1-2 minutes
Test /help again
```

### Fix 3: Check Bot Token
```
1. Telegram → @BotFather → /mybots
2. Select your bot → API Token
3. Copy the EXACT token
4. Railway → Variables → TELEGRAM_BOT_TOKEN
5. Paste token (no spaces, quotes, or extra characters)
6. Save (auto-redeploys)
7. Wait 2-3 minutes
8. Test /help again
```

### Fix 4: Verify User ID
```
1. Telegram → Search @userinfobot
2. Send /start
3. Copy your user ID (numbers only)
4. Railway → Variables → ALLOWED_TELEGRAM_IDS
5. Set to your ID (e.g., 1826469087)
6. Save (auto-redeploys)
7. Wait 2-3 minutes
8. Test /help again
```

---

## Step 7: Check Railway Build Logs

### Look for Python Errors:

```
Railway → Deployments → Build Logs

Common errors:
❌ ModuleNotFoundError: No module named 'X'
   Fix: Missing dependency in requirements.txt

❌ ValueError: Required environment variable 'X' is not set
   Fix: Add missing env variable

❌ ImportError: cannot import name 'X'
   Fix: Version mismatch in dependencies
```

---

## Step 8: Nuclear Option - Fresh Deployment

If nothing works:

### Option A: Redeploy from Scratch

1. Railway → Delete current service
2. Create new service
3. Deploy from GitHub (Solana branch)
4. Add ALL environment variables
5. Wait for build
6. Test bot

### Option B: Check Different Bot

Create a test bot:
1. Telegram → @BotFather → /newbot
2. Follow prompts
3. Get new token
4. Railway → Variables → TELEGRAM_BOT_TOKEN = new token
5. Test if new bot responds

If new bot works → Your original token was wrong  
If new bot doesn't work → Railway or code issue

---

## Diagnostic Checklist

Go through these in order:

- [ ] Railway deployment shows "Deployment live" (not building/failed)
- [ ] Railway logs show "Bot is running..."
- [ ] Railway logs don't show any error messages
- [ ] TELEGRAM_BOT_TOKEN in Railway matches BotFather
- [ ] ALLOWED_TELEGRAM_IDS in Railway matches @userinfobot
- [ ] All 6 required env variables are set in Railway
- [ ] Bot username in Telegram matches your bot
- [ ] You clicked "Start" button in Telegram chat
- [ ] You're sending commands to the RIGHT bot
- [ ] No other bot instance running (causing 409 Conflict)

---

## What to Check Right Now

**Please do these and report back**:

### 1. Railway Deployment Status
```
Railway Dashboard → What does it say?
- "Deployment live" ✅
- "Building..." 🟡
- "Failed" ❌
```

### 2. Railway Logs (Last 50 Lines)
```
Railway → Deployments → View Logs → Copy last ~50 lines
Look for "Bot is running..." or any errors
```

### 3. Bot Token Verification
```
Telegram → @BotFather → /mybots → Select bot → API Token
Does it EXACTLY match what's in Railway Variables?
```

### 4. Your Telegram User ID
```
Telegram → @userinfobot → /start
Copy your ID
Does it match ALLOWED_TELEGRAM_IDS in Railway?
```

### 5. Bot Username
```
What's your bot's username?
(e.g., @MyTradingBot)
Are you messaging the correct bot?
```

---

## Most Likely Issues

Based on "no response at all":

### 🔴 **90% Chance**: Wrong Bot Token or User ID
```
Solution: Verify TELEGRAM_BOT_TOKEN and ALLOWED_TELEGRAM_IDS
```

### 🔴 **5% Chance**: Bot Crashed During Startup
```
Solution: Check Railway logs for errors
```

### 🔴 **5% Chance**: Railway Deployment Not Complete
```
Solution: Wait for "Deployment live" status
```

---

## Quick Test Commands (Once Bot Responds)

When bot starts working:
```
/help     → Should show command list
/test     → Should show "Bot is responding!"
/balance  → Should show your SOL balance
/config   → Should start configuration
```

---

Please report back:
1. **Railway deployment status** (live/building/failed?)
2. **Last 20 lines of Railway logs** (any errors?)
3. **Bot token matches BotFather?** (yes/no)
4. **User ID matches @userinfobot?** (yes/no)
5. **Bot username you're messaging** (@YourBot)

With this info, I can tell you exactly what's wrong!

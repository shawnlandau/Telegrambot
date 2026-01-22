# Fix: Update Droplet Code to Latest Version

The error `Required environment variable 'RPC_URL' is not set` means your Droplet has old code.

## Quick Fix - Mac Terminal Commands

Run these commands on your Mac to update the Droplet:

### Step 1: SSH into your Droplet

```bash
ssh root@YOUR_DROPLET_IP
```

### Step 2: Stop the bot service

```bash
systemctl stop trading-bot
```

### Step 3: Update the code

```bash
cd /opt/Telegrambot

# Stash any local changes
git stash

# Fetch latest code
git fetch origin Solana

# Reset to latest version
git reset --hard origin/Solana

# Verify you're on latest commit
git log -1
```

**Expected output:**
```
commit 9323550...
Author: shawnlandau
Date: Wed Jan 15 ...

    Add comprehensive DigitalOcean deployment guide for macOS users
```

### Step 4: Reinstall dependencies (in case they changed)

```bash
# Activate venv
source venv/bin/activate

# Update pip
pip install --upgrade pip

# Reinstall dependencies
pip install -r requirements.txt
```

### Step 5: Verify your .env file has correct variable names

```bash
cat .env | grep -E "SOLANA_RPC_URL|WALLET_PRIVATE_KEY|QUOTE_TOKEN_ADDRESS|TELEGRAM_BOT_TOKEN|ALLOWED_TELEGRAM_IDS"
```

**✅ You should see:**
```
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
WALLET_PRIVATE_KEY=<your_key>
QUOTE_TOKEN_ADDRESS=8D9foi1nqfabp8D3uNJCrzt1xkvxq8xHYH8Lxb4fbonk
TELEGRAM_BOT_TOKEN=<your_token>
ALLOWED_TELEGRAM_IDS=<your_id>
```

**❌ If you see `RPC_URL` instead of `SOLANA_RPC_URL`, fix it:**

```bash
nano .env
```

Change this line:
```
RPC_URL=https://api.mainnet-beta.solana.com
```

To:
```
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
```

Save: `Ctrl + X`, then `Y`, then `Enter`

### Step 6: Start the bot service

```bash
systemctl start trading-bot
```

### Step 7: Check the logs

```bash
journalctl -u trading-bot -f
```

**✅ Expected output:**

```
Jan 15 12:00:00 trading-bot[12345]: ====================================
Jan 15 12:00:00 trading-bot[12345]: Starting DEX Trading Bot (Solana Edition)
Jan 15 12:00:00 trading-bot[12345]: ====================================
Jan 15 12:00:01 trading-bot[12345]: [INFO] Database initialized at: bot_data.db
Jan 15 12:00:02 trading-bot[12345]: [INFO] Connected to Solana network
Jan 15 12:00:02 trading-bot[12345]: [INFO] Solana RPC version: 3.0.13
Jan 15 12:00:03 trading-bot[12345]: [INFO] Loaded wallet: AF3y2wckyKF5BDn92M284snihVSt1YFbhsqUo6DUdEm9
Jan 15 12:00:03 trading-bot[12345]: [INFO] Trading pair: SOL/MEMESAI
Jan 15 12:00:03 trading-bot[12345]: [INFO] Bot is running...
```

Stop viewing logs: Press `Ctrl + C`

### Step 8: Test in Telegram

```
/help
```

You should get a response!

---

## Alternative: Fresh Clone (If Update Fails)

If the update doesn't work, do a fresh clone:

```bash
# Stop service
systemctl stop trading-bot

# Backup your .env
cp /opt/Telegrambot/.env /root/.env.backup

# Remove old directory
rm -rf /opt/Telegrambot

# Fresh clone
cd /opt
git clone https://github.com/shawnlandau/Telegrambot.git
cd Telegrambot
git checkout Solana

# Restore .env
cp /root/.env.backup .env

# Create venv and install
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Start service
systemctl start trading-bot

# Check logs
journalctl -u trading-bot -f
```

---

## Verify Success

After update, run these checks:

### 1. Service Status
```bash
systemctl status trading-bot
```
Should show: `Active: active (running)`

### 2. Check Logs
```bash
journalctl -u trading-bot -n 20
```
Should show: `Bot is running...` with no `RPC_URL` errors

### 3. Test Telegram
```
/help
/balance
```
Both should respond immediately

### 4. Verify Latest Code
```bash
cd /opt/Telegrambot
git log -1 --oneline
```
Should show: `9323550 Add comprehensive DigitalOcean deployment guide for macOS users`

---

## Common Issues

### Issue: `git reset --hard` fails
**Solution:** Fresh clone (see "Alternative" above)

### Issue: Still see `RPC_URL` error after update
**Solution:** Check .env file:
```bash
cat /opt/Telegrambot/.env | grep RPC
```
Should show `SOLANA_RPC_URL`, not `RPC_URL`

### Issue: `pip install` fails
**Solution:**
```bash
python3.11 -m venv venv --clear
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: Service won't start
**Solution:**
```bash
journalctl -u trading-bot -n 50
```
Look for specific error message

---

## After Update Checklist

- [ ] `git log -1` shows commit `9323550` or later
- [ ] `.env` has `SOLANA_RPC_URL` (not `RPC_URL`)
- [ ] `systemctl status trading-bot` shows `active (running)`
- [ ] `journalctl -u trading-bot` shows "Bot is running..."
- [ ] Telegram `/help` responds
- [ ] Telegram `/balance` shows SOL balance

---

**Ready to trade!** 🚀

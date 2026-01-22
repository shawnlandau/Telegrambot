# 🚨 Troubleshooting: "Failed to start trading session" Error

## Quick Diagnosis Commands

Run these commands on your DigitalOcean droplet to identify the problem:

### Step 1: Check Recent Logs
```bash
sudo journalctl -u trading-bot -n 100 | grep -A 10 "Failed to start"
```

### Step 2: Check for Errors
```bash
sudo journalctl -u trading-bot -n 200 | grep -i "error"
```

### Step 3: View Full Recent Logs
```bash
sudo journalctl -u trading-bot -n 50
```

---

## Common Causes & Solutions

### ❌ **Cause 1: No Configuration Saved**

**Error message in logs:**
```
[ERROR] No configuration found for user 123456789
```

**Solution:**
You need to run `/config` command BEFORE `/start`:

1. In Telegram, send: `/config`
2. Enter total liquidity (e.g., `0.5`)
3. Enter trade percentage (e.g., `20`)
4. Enter interval (e.g., `1800`)
5. Wait for "✅ Configuration saved!"
6. Then send: `/start`

---

### ❌ **Cause 2: Insufficient SOL Balance**

**Error message in logs:**
```
[ERROR] Insufficient SOL balance
[ERROR] Need 0.250000, have 0.050000
```

**Solution:**
Add more SOL to your wallet, OR reduce trade size:

```
/config
Total liquidity: 0.05
Trade percentage: 50
Interval: 1800
```

**Check balance:**
```
/balance
```

---

### ❌ **Cause 3: Session Already Running**

**Error message in logs:**
```
[WARNING] Session already running for user 123456789
```

**Solution:**
Stop the existing session first:

```
/stop
```

Wait for confirmation, then:
```
/start
```

---

### ❌ **Cause 4: Database Corruption**

**Error message in logs:**
```
[ERROR] database disk image is malformed
[ERROR] unable to open database file
```

**Solution:**
Backup and recreate database:

```bash
# Stop bot
sudo systemctl stop trading-bot

# Backup old database
cd /opt/Telegrambot
mv bot_data.db bot_data.db.backup

# Restart bot (will create new database)
sudo systemctl start trading-bot

# Test in Telegram
# /config and /start again
```

---

### ❌ **Cause 5: RPC Connection Failed**

**Error message in logs:**
```
[ERROR] Failed to connect to Solana RPC
[ERROR] HTTPSConnectionPool(host='api.mainnet-beta.solana.com')
```

**Solution 1 - Use Helius (Recommended):**
1. Sign up at https://helius.dev (free)
2. Get your API key
3. Update .env:

```bash
sudo systemctl stop trading-bot
nano /opt/Telegrambot/.env
```

Change:
```bash
SOLANA_RPC_URL=https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE
```

Save (Ctrl+X, Y, Enter), then:
```bash
sudo systemctl start trading-bot
```

**Solution 2 - Use Simulation Mode (Testing):**
```bash
sudo systemctl stop trading-bot
nano /opt/Telegrambot/.env
```

Change:
```bash
SIMULATION_MODE=true
```

Save and restart:
```bash
sudo systemctl start trading-bot
```

---

### ❌ **Cause 6: Invalid Private Key**

**Error message in logs:**
```
[ERROR] Failed to load Solana keypair
[ERROR] WALLET_PRIVATE_KEY is not a valid Solana private key
```

**Solution:**
1. Export private key from Phantom wallet:
   - Open Phantom
   - Settings → Security & Privacy
   - Export Private Key
   - Copy the base58 string (87-88 characters)

2. Update .env:
```bash
sudo systemctl stop trading-bot
nano /opt/Telegrambot/.env
```

Ensure the key has NO spaces, NO quotes:
```bash
WALLET_PRIVATE_KEY=5J7x8k9m2n3p4q5r6s7t8u9v0w1x2y3z4a5b6c7d8e9f0g1h2i3j4k5l6m7n8o9p0q1r2s3t4u
```

Save and restart:
```bash
sudo systemctl start trading-bot
```

---

### ❌ **Cause 7: Wrong User ID**

**Error message in logs:**
```
[WARNING] Unauthorized access attempt from user 987654321
```

**Solution:**
Get your Telegram user ID and update .env:

1. In Telegram, message @userinfobot
2. Send `/start`
3. Copy your user ID (e.g., `1826469087`)

4. Update .env:
```bash
sudo systemctl stop trading-bot
nano /opt/Telegrambot/.env
```

Change:
```bash
ALLOWED_TELEGRAM_IDS=1826469087
```

Save and restart:
```bash
sudo systemctl start trading-bot
```

---

### ❌ **Cause 8: Python Package Errors**

**Error message in logs:**
```
[ERROR] No module named 'telegram'
[ERROR] No module named 'solana'
```

**Solution:**
Reinstall dependencies:

```bash
sudo systemctl stop trading-bot
cd /opt/Telegrambot
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
sudo systemctl start trading-bot
```

---

### ❌ **Cause 9: Code Not Updated**

**Error message:**
Bot works but still shows old pattern (BUY-BUY-SELL-SELL)

**Solution:**
Pull latest code:

```bash
sudo systemctl stop trading-bot
cd /opt/Telegrambot
git pull origin Solana
sudo systemctl start trading-bot
```

Verify:
```bash
git log --oneline -1
```

Should show: `ea3ccef Fix: Update pattern consistency...`

---

## 🔍 Step-by-Step Debugging

If the error persists, follow these steps:

### Step 1: View Full Logs
```bash
sudo journalctl -u trading-bot -n 200 --no-pager
```

### Step 2: Identify Error Type
Look for:
- `[ERROR]` - Errors
- `[WARNING]` - Warnings
- `Traceback` - Python exceptions
- `Failed to` - Operation failures

### Step 3: Test Bot Manually
```bash
sudo systemctl stop trading-bot
cd /opt/Telegrambot
source venv/bin/activate
python -m bot.main
```

Press Ctrl+C to stop when you see the error.

### Step 4: Check Environment
```bash
cd /opt/Telegrambot
cat .env | grep -v "PRIVATE_KEY\|TOKEN"
```

Verify all settings are correct.

### Step 5: Test Solana Connection
```bash
cd /opt/Telegrambot
source venv/bin/activate
python3 << 'EOF'
from bot.config import config
from bot.raydium_client import RaydiumClient

print("Testing Solana connection...")
try:
    client = RaydiumClient()
    print(f"✅ Connected to: {config.SOLANA_RPC_URL}")
    print(f"✅ Wallet: {client.wallet_address}")
    balances = client.get_balances()
    print(f"✅ SOL balance: {balances['base']:.6f}")
    print(f"✅ Token balance: {balances['quote']:.6f}")
    print("\nConnection test PASSED!")
except Exception as e:
    print(f"❌ Connection test FAILED: {e}")
EOF
```

---

## 📋 Quick Diagnostic Script

Run this comprehensive diagnostic:

```bash
cd /opt/Telegrambot
git pull origin Solana
chmod +x DIAGNOSE_ERROR.sh
./DIAGNOSE_ERROR.sh
```

This will check:
- Service status
- Recent errors
- Configuration files
- Database existence
- Python dependencies
- RPC connection

---

## 🆘 Emergency Reset

If nothing works, perform a clean reset:

```bash
# 1. Stop bot
sudo systemctl stop trading-bot

# 2. Backup current setup
cd /opt
sudo mv Telegrambot Telegrambot.backup

# 3. Fresh clone
sudo git clone https://github.com/shawnlandau/Telegrambot.git
cd Telegrambot
sudo git checkout Solana

# 4. Recreate virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. Copy .env from backup
cp ../Telegrambot.backup/.env .

# 6. Restart service
sudo systemctl restart trading-bot

# 7. Check status
sudo systemctl status trading-bot
```

---

## 📞 Getting Help

**Share this information when asking for help:**

```bash
# 1. Bot version
cd /opt/Telegrambot
git log --oneline -1

# 2. Service status
sudo systemctl status trading-bot --no-pager | head -20

# 3. Recent errors
sudo journalctl -u trading-bot -n 100 | grep -i error | tail -20

# 4. Configuration (censored)
cat .env | grep -E "SIMULATION_MODE|DEFAULT_SLIPPAGE_BPS" 

# 5. Python version
python3.11 --version
```

---

## ✅ Success Indicators

After fixing, you should see:

**In Logs:**
```
[INFO] Bot is running...
[INFO] Connected to Solana network
[INFO] Loaded wallet: [your address]
[INFO] Trading pair: SOL/MEMESAI
[INFO] SessionRunner initialized
```

**In Telegram:**
- `/help` - Shows command list
- `/balance` - Shows your SOL balance
- `/config` - Accepts configuration
- `/start` - Starts trading session (no error!)

---

## 🎯 Most Common Solution

In 80% of cases, this error means **you haven't run /config yet**:

```
1. /config
2. Enter: 0.5 (liquidity)
3. Enter: 20 (percentage)
4. Enter: 1800 (interval)
5. Wait for "✅ Configuration saved!"
6. /start
```

If you still get the error after this, share the output of:
```bash
sudo journalctl -u trading-bot -n 100 | grep -A 5 "Failed to start"
```

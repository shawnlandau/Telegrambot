# DigitalOcean Deployment Guide - macOS Terminal

Complete step-by-step guide to deploy the Solana trading bot to DigitalOcean from your Mac terminal.

## Prerequisites

✅ You have a DigitalOcean Droplet running Ubuntu 22.04  
✅ You have the Droplet's IP address  
✅ You have your Mac Terminal open  
✅ You have your wallet private key  
✅ You have your Telegram bot token  
✅ You have your Telegram user ID  

---

## 🚀 STEP-BY-STEP DEPLOYMENT

### Step 1: Connect to Your Droplet via SSH

Open Terminal on your Mac and connect:

```bash
ssh root@YOUR_DROPLET_IP
```

**Example:**
```bash
ssh root@159.89.123.45
```

- You'll be asked "Are you sure you want to continue connecting?" → Type `yes` and press Enter
- Enter your root password when prompted (you'll have received this via email from DigitalOcean)

**✅ Success indicator:** You'll see a prompt like `root@ubuntu-s-1vcpu-1gb-nyc1-01:~#`

---

### Step 2: Update System & Install Python 3.11

Run these commands one by one:

```bash
# Update package list
apt update && apt upgrade -y
```

Wait for updates to complete (~2-3 minutes), then:

```bash
# Install required system packages
apt install -y software-properties-common
```

```bash
# Add Python repository
add-apt-repository -y ppa:deadsnakes/ppa
apt update
```

```bash
# Install Python 3.11 and dependencies
apt install -y python3.11 python3.11-venv python3.11-dev
```

```bash
# Install Git and build tools
apt install -y git curl build-essential
```

**✅ Verify Python installation:**
```bash
python3.11 --version
```
Expected output: `Python 3.11.X`

---

### Step 3: Clone the Bot Repository

```bash
# Navigate to /opt directory
cd /opt

# Clone the repository
git clone https://github.com/shawnlandau/Telegrambot.git

# Navigate into the repository
cd Telegrambot

# Switch to Solana branch
git checkout Solana

# Verify you're on the correct branch
git branch
```

**✅ Expected output:** `* Solana` (the asterisk shows current branch)

---

### Step 4: Create Python Virtual Environment

```bash
# Create virtual environment with Python 3.11
python3.11 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

**✅ Success indicator:** Your prompt should now start with `(venv)`

```bash
# Upgrade pip
pip install --upgrade pip

# Install bot dependencies
pip install -r requirements.txt
```

⏱️ Installation takes ~2-3 minutes

**✅ Verify installation:**
```bash
pip list | grep telegram
```
Expected output should include `python-telegram-bot`

---

### Step 5: Configure Environment Variables

Create the `.env` file:

```bash
nano .env
```

Paste the following configuration (replace placeholders with your actual values):

```bash
# Trading Mode
SIMULATION_MODE=false

# Solana Network
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com

# Wallet Configuration
WALLET_PRIVATE_KEY=YOUR_BASE58_PRIVATE_KEY_HERE

# Token Addresses
BASE_TOKEN_ADDRESS=So11111111111111111111111111111111111111112
QUOTE_TOKEN_ADDRESS=8D9foi1nqfabp8D3uNJCrzt1xkvxq8xHYH8Lxb4fbonk

# Telegram Configuration
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
ALLOWED_TELEGRAM_IDS=YOUR_TELEGRAM_USER_ID_HERE

# Trading Parameters
DEFAULT_SLIPPAGE_BPS=100
COMMITMENT_LEVEL=confirmed
LOG_LEVEL=INFO

# Database & Performance
DATABASE_PATH=bot_data.db
MAX_TRADES_PER_SESSION=1000
RPC_TIMEOUT=30
RPC_MAX_RETRIES=3
```

**🔑 Replace these values:**

1. **WALLET_PRIVATE_KEY**: Your Phantom wallet private key (base58 format, 87-88 characters)
   - Get from Phantom: Settings → Security & Privacy → Export Private Key
   
2. **TELEGRAM_BOT_TOKEN**: Your bot token from @BotFather
   - Format: `1234567890:AAH-abc123def456ghi789jkl...`
   
3. **ALLOWED_TELEGRAM_IDS**: Your Telegram user ID
   - Get from @userinfobot: Send `/start` and copy your ID (e.g., `1826469087`)
   - For multiple users: `1826469087,9876543210`

**Save and exit:**
- Press `Ctrl + X`
- Press `Y` to confirm
- Press `Enter` to save

**✅ Verify .env file:**
```bash
cat .env | grep -E "WALLET_PRIVATE_KEY|TELEGRAM_BOT_TOKEN|ALLOWED_TELEGRAM_IDS"
```
Make sure none show placeholder text.

---

### Step 6: Test Run the Bot

```bash
# Make sure you're in the right directory
cd /opt/Telegrambot

# Activate venv (if not already active)
source venv/bin/activate

# Run the bot
python -m bot.main
```

**✅ Expected output (within 10 seconds):**

```
====================================
Starting DEX Trading Bot (Solana Edition)
====================================
[INFO] Database initialized at: bot_data.db
[INFO] Connected to Solana network
[INFO] Solana RPC version: 3.0.13
[INFO] Loaded wallet: AF3y2wckyKF5BDn92M284snihVSt1YFbhsqUo6DUdEm9
[INFO] Trading pair: SOL/MEMESAI
[INFO] Base token: So11111111111111111111111111111111111111112 (SOL, 9 decimals)
[INFO] Quote token: 8D9foi1nqfabp8D3uNJCrzt1xkvxq8xHYH8Lxb4fbonk (MEMESAI, 6 decimals)
[INFO] Raydium client initialized
[INFO] SessionRunner initialized with trade pattern: BUY -> BUY -> SELL -> SELL
[INFO] Config conversation handler registered
[INFO] Application started
[INFO] Bot is running...
```

**🧪 Test in Telegram:**

While the bot is running, open Telegram and test:

1. Send `/help` → You should see command list
2. Send `/balance` → You should see your SOL balance (e.g., `0.750000`)
3. Send `/test` → Bot status info

**Stop the test:**
- Press `Ctrl + C` to stop the bot
- You should see: `[INFO] Shutting down gracefully...`

✅ If you see these logs and Telegram responds, the bot works! Continue to Step 7.

❌ **Troubleshooting:**

If you see errors:

**Error: `Unauthorized` or `Invalid token`**
- Check `TELEGRAM_BOT_TOKEN` in `.env`
- Verify token from @BotFather

**Error: `Failed to load wallet`**
- Check `WALLET_PRIVATE_KEY` in `.env`
- Ensure it's base58 format (no spaces)

**Error: `HTTPSConnectionPool... 'quote-api.jup.ag'`**
- Test DNS: `curl https://quote-api.jup.ag/v6/health`
- If DNS fails, enable `SIMULATION_MODE=true` temporarily

**Error: `No module named 'telegram'`**
- Re-run: `pip install -r requirements.txt`

---

### Step 7: Set Up Systemd Service (Run 24/7)

Create a systemd service file to run the bot automatically:

```bash
nano /etc/systemd/system/trading-bot.service
```

Paste this configuration:

```ini
[Unit]
Description=Solana Trading Bot (SOL/MEMESAI via Jupiter)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/Telegrambot
Environment="PATH=/opt/Telegrambot/venv/bin"
ExecStart=/opt/Telegrambot/venv/bin/python -m bot.main
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=trading-bot

[Install]
WantedBy=multi-user.target
```

**Save and exit:**
- Press `Ctrl + X`, then `Y`, then `Enter`

**Enable and start the service:**

```bash
# Reload systemd to recognize new service
systemctl daemon-reload

# Enable service to start on boot
systemctl enable trading-bot

# Start the service now
systemctl start trading-bot

# Check service status
systemctl status trading-bot
```

**✅ Expected output:**

```
● trading-bot.service - Solana Trading Bot (SOL/MEMESAI via Jupiter)
     Loaded: loaded (/etc/systemd/system/trading-bot.service; enabled)
     Active: active (running) since Wed 2026-01-15 10:30:00 UTC; 5s ago
   Main PID: 12345 (python)
      Tasks: 3 (limit: 1137)
     Memory: 85.2M
        CPU: 1.234s
     CGroup: /system.slice/trading-bot.service
             └─12345 /opt/Telegrambot/venv/bin/python -m bot.main
```

Look for: `Active: active (running)`

---

### Step 8: Monitor Bot Logs

**View live logs:**

```bash
journalctl -u trading-bot -f
```

**✅ You should see:**
```
Jan 15 10:30:05 ubuntu trading-bot[12345]: [INFO] Bot is running...
Jan 15 10:30:05 ubuntu trading-bot[12345]: [INFO] Connected to Solana network
Jan 15 10:30:05 ubuntu trading-bot[12345]: [INFO] Loaded wallet: AF3y2w...Em9
Jan 15 10:30:05 ubuntu trading-bot[12345]: [INFO] Trading pair: SOL/MEMESAI
```

**Stop viewing logs:** Press `Ctrl + C`

**View last 50 lines:**
```bash
journalctl -u trading-bot -n 50
```

**View logs from last hour:**
```bash
journalctl -u trading-bot --since "1 hour ago"
```

---

### Step 9: Test Trading via Telegram

Open Telegram and configure the bot:

#### 1) Check Balance
```
/balance
```

**Expected response:**
```
💰 Balance Information

🪙 SOL: 0.750000
🎯 MEMESAI: 0.000000

📍 Wallet: AF3y2w...Em9
🔗 Solscan: https://solscan.io/account/AF3y2wckyKF5BDn92M284snihVSt1YFbhsqUo6DUdEm9
```

#### 2) Configure Trading
```
/config
```

Bot asks: **"Please enter your total liquidity in SOL:"**  
Type: `0.5`

Bot asks: **"What percentage per trade?"**  
Type: `50`

Bot asks: **"Trading interval in seconds?"**  
Type: `300`

**Expected response:**
```
✅ Configuration saved!

📊 Settings Summary:
• Total Liquidity: 0.50 SOL
• Trade Percentage: 50%
• Trade Amount: 0.25 SOL per trade
• Interval: 300 seconds (5 minutes)
• Slippage: 1.0%
• Min Notional: 0.01 SOL

🔄 Trading Pattern:
1. BUY → Spend SOL to buy MEMESAI
2. BUY → Spend SOL to buy MEMESAI
3. SELL → Sell MEMESAI for SOL
4. SELL → Sell MEMESAI for SOL
(Pattern repeats)

Use /start to begin trading
```

#### 3) Start Trading
```
/start
```

**Expected response:**
```
✅ Trading session started!

📊 Configuration:
• Total Liquidity: 0.50 SOL
• Trade Percentage: 50%
• Trade Amount: 0.25 SOL
• Interval: 300 seconds

🔄 Trading Pattern: BUY → BUY → SELL → SELL

The bot will now trade automatically.
Use /status to check progress or /stop to end the session.
```

#### 4) Wait for First Trade (~1-2 minutes)

You should receive a message like:

```
✅ BUY completed

💱 Trade Details:
• In: 0.250000 SOL
• Out: 250000.000000 MEMESAI
• Price: 1000000.00 MEMESAI per SOL

📊 Transaction:
• TX: abc123def456...xyz789
• Gas Used: 50000 units
• Fee: 0.000005 SOL

💰 Current Balances:
• SOL: 0.499995
• MEMESAI: 250000.000000

⏱️ Next trade in 300 seconds
```

#### 5) Verify on Solscan

Open in browser:
```
https://solscan.io/account/AF3y2wckyKF5BDn92M284snihVSt1YFbhsqUo6DUdEm9
```

**✅ You should see:**
- Recent transaction (swap via Jupiter)
- SOL balance decreased
- MEMESAI token account created
- Transaction confirmed

#### 6) Check Status
```
/status
```

**Expected response:**
```
📊 Trading Session Status

🔄 Status: Running
⏱️ Uptime: 5 minutes
🎯 Pattern: BUY → BUY → SELL → SELL
📈 Step: 2 of 4 (Next: BUY)

💼 Configuration:
• Liquidity: 0.50 SOL
• Trade %: 50%
• Amount: 0.25 SOL
• Interval: 300s

📊 Statistics:
• Trades: 1
• SOL Spent: 0.250000
• SOL Received: 0.000000
• Net P/L: -0.250000 SOL
• MEMESAI Δ: +250000.000000

💰 Current Balances:
• SOL: 0.499995
• MEMESAI: 250000.000000

⏱️ Next trade in: 245 seconds
```

---

### Step 10: Manage the Bot Service

#### Useful Commands:

**Check service status:**
```bash
systemctl status trading-bot
```

**Stop the bot:**
```bash
systemctl stop trading-bot
```

**Start the bot:**
```bash
systemctl start trading-bot
```

**Restart the bot:**
```bash
systemctl restart trading-bot
```

**View live logs:**
```bash
journalctl -u trading-bot -f
```

**Disable auto-start on boot:**
```bash
systemctl disable trading-bot
```

**Re-enable auto-start:**
```bash
systemctl enable trading-bot
```

---

## 🔐 Security Best Practices

### 1) Create a Non-Root User

Running as root is not recommended. Create a dedicated user:

```bash
# Create user
adduser solbot

# Add to sudo group
usermod -aG sudo solbot

# Change ownership of bot directory
chown -R solbot:solbot /opt/Telegrambot

# Update systemd service to use new user
nano /etc/systemd/system/trading-bot.service
```

Change `User=root` to `User=solbot`, then:

```bash
systemctl daemon-reload
systemctl restart trading-bot
```

### 2) Configure Firewall

```bash
# Install UFW
apt install -y ufw

# Allow SSH
ufw allow 22/tcp

# Enable firewall
ufw enable

# Check status
ufw status
```

### 3) Secure Private Keys

```bash
# Restrict .env permissions
chmod 600 /opt/Telegrambot/.env

# Verify
ls -la /opt/Telegrambot/.env
```

Expected: `-rw------- 1 root root`

---

## 📊 Monitoring & Maintenance

### Daily Monitoring

**Check bot health:**
```bash
systemctl status trading-bot
```

**View recent trades (last 20 lines):**
```bash
journalctl -u trading-bot -n 20
```

**Check for errors:**
```bash
journalctl -u trading-bot | grep ERROR
```

### Weekly Maintenance

**Update bot code:**
```bash
cd /opt/Telegrambot
git pull origin Solana
systemctl restart trading-bot
```

**Clean old logs:**
```bash
journalctl --vacuum-time=7d
```

### Telegram Monitoring

Use these commands regularly:

- `/status` - Check current session
- `/balance` - Verify wallet balances
- `/history 20` - Review last 20 trades

---

## 🛑 Emergency Stop

### Stop Trading Immediately

**Via Telegram:**
```
/stop
```

**Via SSH:**
```bash
systemctl stop trading-bot
```

### View Stop Summary

After `/stop`, you'll receive:

```
🛑 Trading session stopped

📊 Session Summary:
• Duration: 2 hours 15 minutes
• Trades Executed: 18
• SOL Spent: 2.250000
• SOL Received: 2.100000
• Net P/L: -0.150000 SOL (-6.67%)
• MEMESAI Position Δ: +50000.000000
```

---

## 📈 Cost Breakdown

### DigitalOcean Droplet
- **Basic Droplet:** $6/month
- **Recommended:** 1GB RAM, 1 CPU, 25GB SSD

### Trading Costs (Per Trade)
- **Jupiter Fee:** ~0.4% (~0.002 SOL per 0.5 SOL trade)
- **Solana Network Fee:** ~0.000005 SOL
- **Total per trade:** ~$0.40 (at $200/SOL)

### Monthly Estimate
- **Trading:** 4 trades × 288 cycles/day = 1,152 trades/month
- **Trading fees:** ~$460/month
- **Server:** $6/month
- **Total:** ~$466/month

💡 **Tip:** Adjust `INTERVAL` to reduce trading frequency and costs.

---

## 🆘 Troubleshooting

### Bot Not Responding in Telegram

**1. Check service status:**
```bash
systemctl status trading-bot
```

**2. Check logs for errors:**
```bash
journalctl -u trading-bot -n 50
```

**3. Verify environment variables:**
```bash
cd /opt/Telegrambot
cat .env | grep TELEGRAM_BOT_TOKEN
```

**4. Test Telegram token:**
```bash
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"
```

**5. Restart service:**
```bash
systemctl restart trading-bot
```

### DNS Resolution Errors

**Error:** `Failed to resolve 'quote-api.jup.ag'`

**Solution 1 - Use Google DNS:**
```bash
echo "nameserver 8.8.8.8" > /etc/resolv.conf
echo "nameserver 8.8.4.4" >> /etc/resolv.conf
systemctl restart trading-bot
```

**Solution 2 - Enable Simulation Mode temporarily:**
```bash
nano /opt/Telegrambot/.env
```
Change: `SIMULATION_MODE=true`
```bash
systemctl restart trading-bot
```

**Solution 3 - Use Helius RPC:**

Sign up at https://helius.dev, get API key, then:
```bash
nano /opt/Telegrambot/.env
```
Change: `SOLANA_RPC_URL=https://mainnet.helius-rpc.com/?api-key=YOUR_KEY`
```bash
systemctl restart trading-bot
```

### Wallet Issues

**Error:** `Failed to load wallet`

**Fix:**
```bash
# Verify private key format
cd /opt/Telegrambot
cat .env | grep WALLET_PRIVATE_KEY
```

Ensure:
- No spaces before/after the key
- Base58 format (87-88 characters)
- No quotes around the key

### Permission Errors

**Error:** `Permission denied`

**Fix:**
```bash
cd /opt/Telegrambot
chmod +x venv/bin/python
chmod 755 bot/
chown -R root:root /opt/Telegrambot
```

### Out of Memory

**Error:** `Killed` or `Out of memory`

**Check memory:**
```bash
free -h
```

**Solution - Add swap:**
```bash
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

---

## 🔄 Updating the Bot

### Pull Latest Changes

```bash
# Stop the service
systemctl stop trading-bot

# Navigate to bot directory
cd /opt/Telegrambot

# Pull latest code
git pull origin Solana

# Activate venv
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt

# Restart service
systemctl start trading-bot

# Verify
systemctl status trading-bot
```

### View Logs After Update

```bash
journalctl -u trading-bot -f
```

---

## 📞 Support Resources

### Documentation
- **User Guide:** `/opt/Telegrambot/USER_DEPLOYMENT_GUIDE.md`
- **DNS Troubleshooting:** `/opt/Telegrambot/JUPITER_API_DNS_FIX.md`
- **Railway vs Render:** `/opt/Telegrambot/BOT_NOT_RESPONDING.md`

### Check Bot Status
- **GitHub Repo:** https://github.com/shawnlandau/Telegrambot
- **Branch:** Solana
- **Latest Commit:** Check with `git log -1`

### Solana Resources
- **Wallet Explorer:** https://solscan.io/account/AF3y2wckyKF5BDn92M284snihVSt1YFbhsqUo6DUdEm9
- **Jupiter Status:** https://status.jup.ag
- **Solana Status:** https://status.solana.com

### Telegram Commands
- `/help` - Command list
- `/balance` - Check balances
- `/status` - Session status
- `/history` - Trade history
- `/test` - Diagnostic info

---

## ✅ Success Checklist

After completing this guide, verify:

- [ ] SSH connection to droplet works
- [ ] Python 3.11 installed (`python3.11 --version`)
- [ ] Bot repository cloned to `/opt/Telegrambot`
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip list | grep telegram`)
- [ ] `.env` file configured with real values
- [ ] Test run successful (logs show "Bot is running...")
- [ ] Telegram `/help` command responds
- [ ] Telegram `/balance` shows correct SOL amount
- [ ] Systemd service created and enabled
- [ ] Service status shows `active (running)`
- [ ] Logs accessible via `journalctl -u trading-bot -f`
- [ ] `/config` completes successfully
- [ ] `/start` initiates trading session
- [ ] First trade executes within 1-2 minutes
- [ ] Solscan shows transaction on-chain
- [ ] Bot survives system reboot (test: `reboot`, wait 2 min, check `systemctl status trading-bot`)

---

## 🎯 Quick Reference Commands

### SSH & Navigation
```bash
ssh root@YOUR_DROPLET_IP
cd /opt/Telegrambot
```

### Bot Management
```bash
systemctl start trading-bot     # Start
systemctl stop trading-bot      # Stop
systemctl restart trading-bot   # Restart
systemctl status trading-bot    # Status
```

### Logs
```bash
journalctl -u trading-bot -f           # Live logs
journalctl -u trading-bot -n 50        # Last 50 lines
journalctl -u trading-bot --since "1h" # Last hour
```

### Updates
```bash
cd /opt/Telegrambot
git pull origin Solana
systemctl restart trading-bot
```

### Telegram Commands
```
/help       - Show commands
/balance    - Check balances
/config     - Configure trading
/start      - Start trading
/stop       - Stop trading
/status     - Session status
/history    - Trade history
/test       - Diagnostics
```

---

## 🚀 You're Live!

Your bot is now running 24/7 on DigitalOcean, trading SOL/MEMESAI via Jupiter on Solana mainnet!

**Next Steps:**
1. Monitor first few trades closely
2. Verify Solscan transactions
3. Adjust `INTERVAL` if trades are too frequent
4. Test `/stop` and `/start` to ensure session persistence
5. Set up alerts (optional)

**Happy Trading! 🎯**

---

**Created:** 2026-01-15  
**Bot Version:** Latest from branch `Solana`  
**Wallet:** AF3y2wckyKF5BDn92M284snihVSt1YFbhsqUo6DUdEm9  
**Trading Pair:** SOL/MEMESAI  
**DEX:** Jupiter Aggregator

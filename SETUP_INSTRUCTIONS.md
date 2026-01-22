# 🚀 YOUR .ENV FILE IS READY!

## What I've Done

✅ Created `.env` file from template  
✅ Pre-configured SOL and MEMESAI token addresses  
✅ Set up free public Solana RPC  
✅ Added clear instructions and security reminders  
✅ Created validation script to check your configuration  

## What YOU Need to Do Now

### Step 1: Get Your Phantom Wallet Private Key

1. **Open Phantom wallet** (browser extension)
2. Click the **menu icon (☰)** → **Settings**
3. Click **"Show Private Key"**
4. Enter your **password**
5. **Copy the entire private key** (it's a long base58-encoded string)
   - It looks like: `2Qv7x...` or `3kZnD...` (44-88 characters)
   - **DO NOT share this with anyone!**

### Step 2: Create Your Telegram Bot

1. Open **Telegram**
2. Search for **@BotFather**
3. Start a chat and send: `/newbot`
4. Follow the prompts:
   - **Bot name**: `My Trading Bot` (or any name you like)
   - **Bot username**: Must end with "bot" (e.g., `my_trading_bot`)
5. **Copy the token** BotFather gives you
   - It looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

### Step 3: Get Your Telegram User ID

1. In **Telegram**, search for **@userinfobot**
2. Start a chat and **send any message**
3. The bot will reply with your **user ID**
   - It's a number like: `123456789`
4. **Copy this number**

### Step 4: Edit the .env File

Now you need to fill in your values in the `.env` file:

```bash
# Option A: Use nano editor (easiest)
nano .env

# Option B: Use vim
vim .env

# Option C: Use any text editor
```

**Find and replace these 3 lines:**

```bash
WALLET_PRIVATE_KEY=YOUR_BASE58_PRIVATE_KEY_HERE
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
ALLOWED_TELEGRAM_IDS=YOUR_TELEGRAM_USER_ID_HERE
```

**With your actual values:**

```bash
WALLET_PRIVATE_KEY=2Qv7xYour44to88CharacterBase58PrivateKeyFromPhantom
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ALLOWED_TELEGRAM_IDS=123456789
```

**Save the file:**
- In nano: Press `Ctrl+X`, then `Y`, then `Enter`
- In vim: Press `Esc`, type `:wq`, press `Enter`

### Step 5: Validate Your Configuration

Run the validation script to check everything is correct:

```bash
python validate_env.py
```

**Expected output if everything is correct:**
```
✅ ALL REQUIRED VARIABLES ARE SET!
```

**If you see errors:**
- Review the error messages
- Edit your .env file again: `nano .env`
- Run validation again: `python validate_env.py`

### Step 6: Test Solana Connection

Once validation passes, test your connection to Solana:

```bash
python test_solana_connection.py
```

**Expected output:**
```
✅ RPC connection successful
✅ Wallet loaded: [your_address]
✅ SOL balance: X.XXX SOL
✅ MEMESAI balance: X.XXX MEMESAI
✅ Ready to trade!
```

### Step 7: Start the Bot

If the connection test passes, start your bot:

```bash
python -m bot.main
```

**You should see:**
```
INFO - Starting Solana DEX Trading Bot
INFO - Connected to Solana network
INFO - Loaded wallet: [your_address]
INFO - Bot started successfully
```

### Step 8: Configure Trading on Telegram

1. Open Telegram and find your bot
2. Send: `/start` (to start chatting)
3. Send: `/config` (to configure trading parameters)
4. Follow the prompts:
   - **Total liquidity**: Start with `1` (1 SOL)
   - **Trade percentage**: `50` (0.5 SOL per trade)
   - **Interval**: `300` (5 minutes between trades)

### Step 9: Begin Trading

Once configured, start trading:

```
/start
```

The bot will execute the 2×2 pattern:
- **BUY #1**: 0.5 SOL → MEMESAI
- Wait 5 minutes
- **BUY #2**: 0.5 SOL → MEMESAI
- Wait 5 minutes
- **SELL #1**: MEMESAI → ~0.5 SOL
- Wait 5 minutes
- **SELL #2**: MEMESAI → ~0.5 SOL
- Cycle repeats...

## Quick Reference

### Telegram Commands

| Command | Description |
|---------|-------------|
| `/config` | Set up trading parameters |
| `/start` | Begin trading session |
| `/stop` | Stop trading session |
| `/status` | Check current status |
| `/history` | View trade history |
| `/setpct <value>` | Change trade percentage |
| `/setinterval <seconds>` | Change interval |
| `/help` | Show all commands |

### Important Files

| File | Purpose |
|------|---------|
| `.env` | Your configuration (KEEP SECRET!) |
| `validate_env.py` | Validate your .env file |
| `test_solana_connection.py` | Test Solana connection |
| `bot.log` | Bot activity logs |
| `bot_data.db` | Trading history database |

### Monitor Your Trades

Each trade will send you a Telegram message with:
- ✅ Trade type (BUY/SELL)
- ✅ Amounts traded
- ✅ Transaction signature
- ✅ Execution price

Check transactions on Solscan:
- https://solscan.io/tx/[TRANSACTION_SIGNATURE]

## Security Checklist

Before you start:

- [ ] Using a **dedicated Phantom wallet** (not your main one)
- [ ] Wallet has limited funds (start with 1-5 SOL)
- [ ] Private key is pasted in `.env` file
- [ ] `.env` file will **NEVER be committed to git** (it's in .gitignore)
- [ ] Bot token is from your own @BotFather bot
- [ ] Only your Telegram ID is in ALLOWED_TELEGRAM_IDS
- [ ] Tested connection with `python test_solana_connection.py`

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Validation script shows errors
```bash
# Edit your .env file
nano .env

# Run validation again
python validate_env.py
```

### Connection test fails
- Check your private key is correct (copy from Phantom again)
- Verify RPC URL is accessible: `curl https://api.mainnet-beta.solana.com`
- Check your internet connection

### Bot won't start
- Run validation: `python validate_env.py`
- Check logs: `tail -f bot.log`
- Verify Telegram token is correct

## Need Help?

1. **Validation failed?** 
   - Run: `python validate_env.py`
   - Follow the error messages

2. **Connection failed?**
   - Check your Phantom private key
   - Verify RPC endpoint is working

3. **Bot not responding on Telegram?**
   - Check TELEGRAM_BOT_TOKEN is correct
   - Verify bot is running: Look for "Bot started successfully"
   - Check ALLOWED_TELEGRAM_IDS includes your ID

---

## 🎯 Your Current Status

**Current Step**: Fill in your .env file

**Location**: `/home/user/webapp/.env`

**What's already configured:**
- ✅ Solana RPC URL (free public endpoint)
- ✅ SOL token address
- ✅ MEMESAI token address (8D9foi...)
- ✅ Default settings (slippage, commitment, etc.)

**What you need to add:**
- ⏳ Your Phantom wallet private key
- ⏳ Your Telegram bot token
- ⏳ Your Telegram user ID

---

## Next Command to Run

After filling in your .env file:

```bash
python validate_env.py
```

Then if validation passes:

```bash
python test_solana_connection.py
```

---

**Ready to edit your .env file?**

Run: `nano .env`

Look for these lines and replace the placeholders with your actual values! 🚀

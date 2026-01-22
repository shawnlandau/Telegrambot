# 🚀 Starting Your Trading Bot - Final Steps

## ✅ Configuration Complete

Your bot is fully configured and ready to start!

**Wallet Address**: `AF3y2wckyKF5BDn92M284snihVSt1YFbhsqUo6DUdEm9`

---

## 📋 Pre-Flight Checklist

Before starting the bot, verify:

- [ ] SOL has been sent to: `AF3y2wckyKF5BDn92M284snihVSt1YFbhsqUo6DUdEm9`
- [ ] Transaction is confirmed in Phantom wallet
- [ ] You can see the balance on Solscan: https://solscan.io/account/AF3y2wckyKF5BDn92M284snihVSt1YFbhsqUo6DUdEm9
- [ ] You know your Telegram bot's username
- [ ] You have Telegram open and ready

---

## 🎬 Starting the Bot

### Step 1: Start the Bot Process

Run this command in your terminal:

```bash
cd /home/user/webapp && python -m bot.main
```

**Expected output:**
```
INFO - Starting Solana DEX Trading Bot
INFO - Connected to Solana network: https://api.mainnet-beta.solana.com
INFO - Loaded wallet: AF3y2wckyKF5BDn92M284snihVSt1YFbhsqUo6DUdEm9
INFO - Trading pair: SOL/MEMESAI
INFO - Bot started successfully
INFO - Listening for Telegram commands...
```

⚠️ **Keep this terminal window open** - the bot runs here!

---

### Step 2: Find Your Bot on Telegram

1. Open **Telegram**
2. Search for your bot by the **username** you created with @BotFather
3. Click on it to open the chat

---

### Step 3: Start Conversation

Send this command to your bot:

```
/start
```

The bot should respond with a welcome message.

---

### Step 4: Check Available Commands

Send:

```
/help
```

You should see all available commands:
- `/config` - Set up trading parameters
- `/start` - Begin trading
- `/stop` - Stop trading
- `/status` - Check current status
- `/history` - View trade history
- `/setpct <value>` - Change trade percentage
- `/setinterval <seconds>` - Change interval
- `/reset` - Reset configuration

---

### Step 5: Configure Trading Parameters

Send:

```
/config
```

The bot will ask you 3 questions:

#### Question 1: Total Liquidity
```
How much total liquidity (in SOL)?
```

**Recommended answers based on your balance:**
- If you have 0.5 SOL: Enter `0.4`
- If you have 1 SOL: Enter `0.8`
- If you have 2 SOL: Enter `1.5`

**Leave some SOL for transaction fees!**

#### Question 2: Trade Percentage
```
What percentage to trade each time?
```

**Recommended:** Enter `50`

This means:
- 50% of your total liquidity per trade
- If total = 0.4 SOL, each trade = 0.2 SOL

#### Question 3: Interval
```
How many seconds between trades?
```

**Recommended:** Enter `300` (5 minutes)

Options:
- `300` = 5 minutes (recommended for testing)
- `600` = 10 minutes
- `900` = 15 minutes
- `1800` = 30 minutes

---

### Step 6: Verify Configuration

After setting up, send:

```
/status
```

You should see:
- ✅ Your configuration settings
- ✅ Current SOL balance
- ✅ Current MEMESAI balance
- ✅ Trading pair price
- ✅ Session status (not started)

---

### Step 7: Begin Trading!

When you're ready to start the 2×2 trading pattern, send:

```
/start
```

The bot will:
1. **BUY #1**: Spend SOL → Get MEMESAI
2. Wait (your interval)
3. **BUY #2**: Spend SOL → Get MEMESAI
4. Wait (your interval)
5. **SELL #1**: Sell MEMESAI → Get SOL
6. Wait (your interval)
7. **SELL #2**: Sell MEMESAI → Get SOL
8. **Repeat** the cycle

---

## 📊 Monitoring Your Trades

### In Telegram

Each trade will send you a message with:
- ✅ Trade type (BUY/SELL)
- ✅ Amount in
- ✅ Amount out
- ✅ Transaction signature
- ✅ Execution price
- ✅ Gas used

### On Solscan

Check your transactions:
1. Go to: https://solscan.io/account/AF3y2wckyKF5BDn92M284snihVSt1YFbhsqUo6DUdEm9
2. Click on **"Transactions"** tab
3. You'll see all your swaps

Or click the transaction signature from Telegram directly.

---

## 🛑 Stopping the Bot

### Pause Trading

In Telegram, send:

```
/stop
```

This stops the current session but keeps the bot running.

### Stop Bot Completely

In the terminal where the bot is running:
- Press `Ctrl+C`

---

## 🔍 Checking Status

Anytime during trading, send:

```
/status
```

This shows:
- Current configuration
- Session status (active/stopped)
- Trades executed in current session
- SOL spent
- MEMESAI received
- Current balances
- Current price

---

## 📈 Example Trading Scenario

**Configuration:**
- Total liquidity: 0.4 SOL
- Trade percentage: 50%
- Interval: 300 seconds (5 min)

**What happens:**

```
Start: 0.5 SOL, 0 MEMESAI

BUY #1:  0.3 SOL, ~2000 MEMESAI   (spend 0.2 SOL)
         [wait 5 minutes]

BUY #2:  0.1 SOL, ~4000 MEMESAI   (spend 0.2 SOL)
         [wait 5 minutes]

SELL #1: 0.3 SOL, ~2000 MEMESAI   (sell ~2000 MEMESAI)
         [wait 5 minutes]

SELL #2: 0.5 SOL, 0 MEMESAI       (sell ~2000 MEMESAI)
         [cycle repeats]
```

---

## ⚠️ Important Safety Tips

1. **Start Small**: Use 0.1-0.5 SOL for first tests
2. **Monitor Closely**: Watch the first few trades carefully
3. **Check Transactions**: Verify each trade on Solscan
4. **Use /stop**: You can stop anytime with `/stop`
5. **Keep SOL for Fees**: Always keep ~0.01 SOL for transaction fees
6. **Test First**: Run one full cycle (4 trades) before leaving unattended

---

## 🐛 Troubleshooting

### Bot doesn't respond on Telegram
- Check the terminal - is the bot running?
- Look for "Bot started successfully" message
- Check for errors in terminal

### "Insufficient balance" error
- Check your SOL balance: `/status`
- Make sure you have enough SOL
- Remember to keep extra for fees

### Trades failing
- Check network status: https://status.solana.com/
- Verify MEMESAI has liquidity on DEXes
- Try increasing slippage in config (edit .env: DEFAULT_SLIPPAGE_BPS=200)

### Bot crashes
- Check terminal for error messages
- Check logs: `tail -f bot.log`
- Restart: `python -m bot.main`

---

## 📞 Quick Reference Commands

| Command | What It Does |
|---------|-------------|
| `/start` | Start trading session |
| `/stop` | Stop trading session |
| `/status` | Check current status |
| `/config` | Set up parameters |
| `/history` | View past trades |
| `/setpct 30` | Change to 30% per trade |
| `/setinterval 600` | Change to 10 min intervals |
| `/help` | Show all commands |

---

## 🎯 You're All Set!

Your bot is configured and ready. Just run:

```bash
cd /home/user/webapp && python -m bot.main
```

Then open Telegram and start with `/help`!

Good luck with your trading! 🚀

---

**Need Help?**
- Check logs: `tail -f bot.log`
- Review documentation: `cat IMPLEMENTATION_STATUS.md`
- Test connection: `python test_connection_simple.py`

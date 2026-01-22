# 🚀 Quick Setup Card - 5 Minutes to Trading

## Prerequisites
- Python 3.11+
- Solana wallet with SOL
- Telegram account
- MEMESAI tokens (or will buy with bot)

## Step 1: Install (1 min)
```bash
cd /home/user/webapp
git checkout Solana
pip install -r requirements.txt
```

## Step 2: Configure (2 min)
```bash
cp .env.example .env
nano .env
```

**Required values in .env:**
```bash
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
WALLET_PRIVATE_KEY=your_base58_key_here
QUOTE_TOKEN_ADDRESS=8D9foi1nqfabp8D3uNJCrzt1xkvxq8xHYH8Lxb4fbonk
TELEGRAM_BOT_TOKEN=get_from_@BotFather
ALLOWED_TELEGRAM_IDS=get_from_@userinfobot
```

## Step 3: Test Connection (30 sec)
```bash
python test_solana_connection.py
```

Expected: ✅ All checks pass

## Step 4: Start Bot (30 sec)
```bash
python -m bot.main
```

## Step 5: Configure in Telegram (1 min)

Message your bot:
```
/config
```

Follow prompts:
1. **Total liquidity**: `1` (1 SOL total to use)
2. **Trade percentage**: `50` (0.5 SOL per trade)
3. **Interval**: `300` (5 minutes between trades)

Then start:
```
/start
```

## Trading Pattern

The bot executes BUY-BUY-SELL-SELL:

```
BUY #1:  Spend 0.5 SOL → Get MEMESAI
         (5 min wait)
BUY #2:  Spend 0.5 SOL → Get MEMESAI
         (5 min wait)
SELL #1: Sell MEMESAI → Get ~0.5 SOL
         (5 min wait)
SELL #2: Sell MEMESAI → Get ~0.5 SOL
         (cycle repeats)
```

## Commands

| Command | Action |
|---------|--------|
| `/status` | Check current state |
| `/stop` | Stop trading |
| `/history` | View past trades |
| `/setpct 30` | Change to 30% per trade |
| `/setinterval 600` | Change to 10 min intervals |

## Monitor Trades

Each trade sends Telegram message with:
- Trade type (BUY/SELL)
- Amounts
- Transaction hash
- Execution price

Check transactions: https://solscan.io/

## Safety Tips

✅ Start with 0.1-1 SOL total
✅ Monitor first few trades
✅ Use `/stop` anytime
✅ Check balances with `/status`
✅ Verify transactions on Solscan

## Troubleshooting

**"Insufficient balance"**
→ Add more SOL to wallet

**"Transaction failed"**
→ Check network: https://status.solana.com/
→ Try again in a few minutes

**"Price fetch failed"**
→ Check internet connection
→ Verify MEMESAI address

## What's Happening Behind the Scenes

1. **Jupiter Aggregator** finds best price across all Solana DEXes
2. **Smart routing** minimizes slippage
3. **Automatic execution** follows 2×2 pattern
4. **Safe operation** with error handling and retries

## Files to Review

- `IMPLEMENTATION_STATUS.md` - Complete implementation details
- `JUPITER_IMPLEMENTATION.md` - Technical deep dive
- `QUICK_START.md` - Detailed setup guide
- `TESTING_GUIDE.md` - Comprehensive testing procedures

## Need Help?

1. Check logs: `tail -f bot.log`
2. Review documentation files above
3. Check GitHub issues
4. Verify environment variables in `.env`

---

**You're ready to trade! 🎉**

Run `python -m bot.main` and message your bot with `/config` to begin.

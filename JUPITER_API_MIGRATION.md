# Jupiter API Migration Guide - CRITICAL UPDATE

## 🚨 BREAKING CHANGE - DNS Resolution Fixed

### What Changed?

Jupiter is migrating from the old API to a new, more reliable endpoint:

**OLD (Deprecated - causing DNS errors):**
```
https://quote-api.jup.ag/v6/quote
https://quote-api.jup.ag/v6/swap
```

**NEW (Current - better DNS reliability):**
```
https://lite-api.jup.ag/swap/v1/quote
https://lite-api.jup.ag/swap/v1/swap
```

### Why This Fixes DNS Issues

1. **Old API Deprecation**: `quote-api.jup.ag` is being phased out (deadline: May 1, 2025)
2. **Unstable DNS**: The old endpoint has DNS resolution issues on various hosting providers
3. **New Infrastructure**: `lite-api.jup.ag` has better DNS infrastructure and reliability
4. **No API Key Required**: Both old and new APIs are free to use

### What Was Updated

**File:** `bot/raydium_client.py`

**Changes:**
- ✅ Line 308: `get_price()` now uses `lite-api.jup.ag/swap/v1/quote`
- ✅ Line 434: `swap_exact_sol_for_tokens()` quote endpoint updated
- ✅ Line 479: `swap_exact_sol_for_tokens()` swap endpoint updated
- ✅ Line 621: `swap_exact_tokens_for_sol()` quote endpoint updated
- ✅ Line 663: `swap_exact_tokens_for_sol()` swap endpoint updated

**Commit:** `fc919a8` - "CRITICAL: Migrate to new Jupiter API (lite-api.jup.ag) - fixes DNS issues"

---

## 📦 How to Update Your Droplet

### Step 1: SSH into your Droplet

```bash
ssh root@YOUR_DROPLET_IP
```

### Step 2: Stop the Bot

```bash
systemctl stop trading-bot
```

### Step 3: Pull Latest Code

```bash
cd /opt/Telegrambot
git pull origin Solana
```

**Expected output:**
```
remote: Enumerating objects: 5, done.
remote: Counting objects: 100% (5/5), done.
remote: Compressing objects: 100% (3/3), done.
remote: Total 3 (delta 2), reused 3 (delta 2), pack-reused 0
Unpacking objects: 100% (3/3), done.
From https://github.com/shawnlandau/Telegrambot
   4660169..fc919a8  Solana     -> origin/Solana
Updating 4660169..fc919a8
Fast-forward
 bot/raydium_client.py | 12 ++++++------
 1 file changed, 6 insertions(+), 6 deletions(-)
```

### Step 4: Verify the Update

```bash
grep "lite-api.jup.ag" bot/raydium_client.py
```

**Expected output (5 lines):**
```
            quote_url = "https://lite-api.jup.ag/swap/v1/quote"
            quote_url = f"https://lite-api.jup.ag/swap/v1/quote"
            swap_url = "https://lite-api.jup.ag/swap/v1/swap"
            quote_url = f"https://lite-api.jup.ag/swap/v1/quote"
            swap_url = "https://lite-api.jup.ag/swap/v1/swap"
```

### Step 5: Test DNS Resolution (Optional)

```bash
nslookup lite-api.jup.ag
```

**Expected:** Should resolve to IP addresses (unlike `quote-api.jup.ag` which was failing)

### Step 6: Start the Bot

```bash
systemctl start trading-bot
```

### Step 7: Monitor Logs

```bash
journalctl -u trading-bot -f
```

**✅ Expected (SUCCESS):**

```
Jan 16 00:25:00 trading-bot[12345]: [INFO] Getting Jupiter quote...
Jan 16 00:25:01 trading-bot[12345]: [INFO] Expected output: 250000.000000 MEMESAI
Jan 16 00:25:02 trading-bot[12345]: [INFO] Requesting swap transaction...
Jan 16 00:25:03 trading-bot[12345]: [INFO] Transaction sent: abc123...
Jan 16 00:25:05 trading-bot[12345]: [INFO] BUY swap successful: abc123...
```

**❌ Should NOT see anymore:**

```
Failed to resolve 'quote-api.jup.ag'
NameResolutionError
Max retries exceeded with url
```

Press `Ctrl + C` to stop viewing logs.

---

## 🧪 Test in Telegram

### 1. Check Status

```
/status
```

Should show bot is running.

### 2. Configure Trading (if needed)

```
/config
```

Enter:
- Liquidity: `0.5`
- Percentage: `50`
- Interval: `300`

### 3. Start Trading

```
/start
```

### 4. Wait for First Trade (~1-2 minutes)

**✅ Expected Telegram message:**

```
✅ BUY completed

💱 Trade Details:
• In: 0.250000 SOL
• Out: 250000.000000 MEMESAI
• Price: 1000000.00 MEMESAI per SOL

📊 Transaction:
• TX: abc123def456...
• Gas Used: 50000 units
• Fee: 0.000005 SOL

💰 Current Balances:
• SOL: 0.499995
• MEMESAI: 250000.000000

⏱️ Next trade in 300 seconds
```

---

## 🔍 Verify on Solscan

Open your wallet on Solscan:

```
https://solscan.io/account/AF3y2wckyKF5BDn92M284snihVSt1YFbhsqUo6DUdEm9
```

**✅ You should see:**
- Recent transaction (swap via Jupiter)
- SOL balance decreased
- MEMESAI balance increased
- Transaction confirmed

---

## 📊 Quick Diagnostic Commands

If you want to verify everything is working:

```bash
# 1. Check service status
systemctl status trading-bot

# 2. Check last 30 log lines
journalctl -u trading-bot -n 30 --no-pager

# 3. Verify new API endpoint is in code
grep "lite-api.jup.ag" /opt/Telegrambot/bot/raydium_client.py | wc -l
# Should return: 5

# 4. Check no old endpoint references remain
grep "quote-api.jup.ag" /opt/Telegrambot/bot/raydium_client.py
# Should return: (empty)

# 5. Test DNS for new API
nslookup lite-api.jup.ag
# Should resolve successfully

# 6. Test DNS for old API (for comparison)
nslookup quote-api.jup.ag
# Might fail (that's why we migrated)
```

---

## 🆘 Troubleshooting

### Issue: Still seeing DNS errors after update

**Check you pulled the latest code:**

```bash
cd /opt/Telegrambot
git log -1 --oneline
```

Should show: `fc919a8 CRITICAL: Migrate to new Jupiter API (lite-api.jup.ag) - fixes DNS issues`

If not:

```bash
git fetch origin Solana
git reset --hard origin/Solana
systemctl restart trading-bot
```

### Issue: Bot won't start after update

**Check logs:**

```bash
journalctl -u trading-bot -n 50
```

Look for specific error messages.

**Common fixes:**

```bash
# Reinstall dependencies (rarely needed, but safe)
cd /opt/Telegrambot
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
systemctl restart trading-bot
```

### Issue: Trades still failing with different error

**Share the error:**

```bash
journalctl -u trading-bot -n 30 --no-pager
```

Copy and paste the output to diagnose.

---

## ✅ Success Checklist

After update, verify:

- [ ] `git log -1` shows commit `fc919a8` or later
- [ ] `grep "lite-api.jup.ag" bot/raydium_client.py` shows 5 matches
- [ ] `systemctl status trading-bot` shows `active (running)`
- [ ] `journalctl -u trading-bot` shows no DNS errors
- [ ] Telegram `/help` responds immediately
- [ ] Telegram `/start` initiates trading
- [ ] First trade completes within 1-2 minutes
- [ ] Solscan shows transaction on-chain
- [ ] No more `Failed to resolve 'quote-api.jup.ag'` errors

---

## 📚 Additional Resources

### Jupiter API Documentation
- **New Docs**: https://hub.jup.ag/docs/apis/swap-api
- **Migration Notice**: Migrate from `quote-api.jup.ag` to `lite-api.jup.ag` by May 1, 2025
- **Rate Limits**: Free tier available (no API key required)
- **Status Page**: https://status.jup.ag

### Related Commits
- `fc919a8` - Migrate to new Jupiter API
- `4660169` - Fix RPC_URL environment variable error
- `9323550` - Add DigitalOcean deployment guide

### GitHub Repository
- **Repo**: https://github.com/shawnlandau/Telegrambot
- **Branch**: Solana
- **Latest Commit**: fc919a8

---

## 🎯 Why This Migration Matters

1. **Reliability**: `lite-api.jup.ag` has better uptime and DNS infrastructure
2. **Performance**: New API is optimized for lower latency
3. **Future-proof**: Old API will be deprecated on May 1, 2025
4. **Compatibility**: Works across all hosting providers (DigitalOcean, Railway, Render, etc.)
5. **No Cost**: Still free to use, no API key required

---

## 📞 Support

If you encounter issues after migration:

1. Check the Success Checklist above
2. Run diagnostic commands
3. Review logs: `journalctl -u trading-bot -n 50`
4. Verify DNS resolution: `nslookup lite-api.jup.ag`
5. Test Telegram commands: `/help`, `/status`, `/balance`

---

**Update completed!** 🚀

Your bot should now have reliable access to Jupiter's swap API without DNS issues.

---

**Last Updated:** 2026-01-16  
**Commit:** fc919a8  
**Migration Deadline:** May 1, 2025 (we're ahead of schedule!)

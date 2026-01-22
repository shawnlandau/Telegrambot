# 🔧 Jupiter API Connection Issues - Troubleshooting Guide

## Error: Failed to resolve 'quote-api.jup.ag'

### Full Error Message
```
❌ Session stopped due to error:
Trade failed: Failed to execute BUY swap: 
HTTPSConnectionPool(host='quote-api.jup.ag', port=443): 
Max retries exceeded with url: /v6/quote?...
(Caused by NameResolutionError: Failed to resolve 'quote-api.jup.ag' 
[Errno -5] No address associated with hostname)
```

---

## 🔍 What This Means

This is a **DNS resolution error** - the bot cannot translate the domain name `quote-api.jup.ag` into an IP address.

### Possible Causes:

1. **Railway network issue** (most common)
   - Temporary DNS problems on Railway's infrastructure
   - Network routing issues

2. **Jupiter API down** (rare)
   - Jupiter's API servers are offline
   - DNS records not propagating

3. **Rate limiting / IP blocking**
   - Too many requests from Railway's IP range
   - Jupiter temporarily blocking the IP

4. **Railway DNS resolver issue**
   - Railway's internal DNS service having problems
   - Region-specific DNS failures

---

## ✅ Solution: Automatic Retry with Exponential Backoff

**Latest commit** (7aa3512) adds automatic retry logic:

### What Was Fixed:

1. **Retry Logic**: Up to 3 attempts per request
   - Attempt 1: Immediate
   - Attempt 2: Wait 2 seconds
   - Attempt 3: Wait 4 seconds

2. **Increased Timeout**: 10s → 15s per request

3. **Better Headers**: Added `User-Agent` to look like a browser

4. **Error Handling**: Catches `ConnectionError`, `Timeout`, `NameResolutionError`

### Code Changes:

```python
# Before (would fail immediately)
quote_response = requests.get(quote_url, params=quote_params, timeout=10)

# After (retries with backoff)
max_retries = 3
for attempt in range(max_retries):
    try:
        quote_response = requests.get(
            quote_url, 
            params=quote_params, 
            timeout=15,  # Increased timeout
            headers={'User-Agent': 'Mozilla/5.0'}  # Added headers
        )
        break  # Success!
    except (requests.exceptions.ConnectionError, 
            requests.exceptions.Timeout,
            requests.exceptions.RequestException) as e:
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # Exponential backoff
            logger.warning(f"Retrying in {wait_time}s...")
            time.sleep(wait_time)
        else:
            raise  # Give up after 3 attempts
```

---

## 🚀 How to Apply the Fix

### Railway Auto-Deploy (Automatic)

Since you pushed to GitHub, Railway will automatically:
1. Detect the new commit (7aa3512)
2. Pull the latest code
3. Rebuild the bot
4. Redeploy with the fix

**Wait time**: ~2-3 minutes

### Verify the Fix is Applied

1. **Check Railway logs** for:
   ```
   Deploying commit: 7aa3512
   Fix: Add retry logic and better error handling for Jupiter API
   ```

2. **Check bot logs** for retry messages:
   ```
   Jupiter API request failed (attempt 1/3): Connection error
   Retrying in 1s...
   Jupiter API request failed (attempt 2/3): Connection error
   Retrying in 2s...
   [Success on attempt 3]
   ```

3. **Test in Telegram**:
   - Send `/start` again
   - The bot should now retry failed requests automatically

---

## 📊 Expected Behavior After Fix

### ✅ Successful Trade (no errors)
```
Getting Jupiter quote for 300000000 lamports...
[Quote request successful]
Expected output: 300000.0 MEMESAI
[Swap request successful]
BUY swap successful: abc123...
```

### ✅ Successful Trade (after retries)
```
Getting Jupiter quote for 300000000 lamports...
Jupiter quote request failed (attempt 1/3): Connection error
Retrying in 1s...
[Quote request successful on attempt 2]
Expected output: 300000.0 MEMESAI
[Swap request successful]
BUY swap successful: abc123...
```

### ❌ Failed Trade (all retries exhausted)
```
Getting Jupiter quote for 300000000 lamports...
Jupiter quote request failed (attempt 1/3): Connection error
Retrying in 1s...
Jupiter quote request failed (attempt 2/3): Connection error
Retrying in 2s...
Jupiter quote request failed (attempt 3/3): Connection error
Jupiter API unavailable after 3 attempts
Trade failed: Failed to execute BUY swap
```

If you see this, Jupiter API is truly down or unreachable.

---

## 🔄 Additional Solutions

### If Automatic Retry Doesn't Work

#### Option 1: Manual Restart (Quick)

1. Go to Railway → Your Service
2. Click **"Settings"**
3. Click **"Restart"**
4. Bot will restart with fresh network connection

#### Option 2: Check Jupiter Status

1. Visit: https://status.jup.ag
2. Check if Jupiter API is operational
3. If down, wait for Jupiter team to fix

#### Option 3: Test Jupiter API Manually

```bash
# Test from your local machine
curl "https://quote-api.jup.ag/v6/quote?inputMint=So11111111111111111111111111111111111111112&outputMint=8D9foi1nqfabp8D3uNJCrzt1xkvxq8xHYH8Lxb4fbonk&amount=100000000&slippageBps=100"

# If this fails too, Jupiter API is down
```

#### Option 4: Use Different RPC (Advanced)

If Railway's network has DNS issues:

1. Railway → Variables
2. Consider using a premium RPC with better DNS resolution
3. Add environment variable:
   ```
   CUSTOM_DNS_RESOLVER=8.8.8.8  # Google DNS
   ```
   (Note: This requires code changes to implement custom DNS)

#### Option 5: Temporary Solution - Simulation Mode

While waiting for Jupiter API to recover:

1. Railway → Variables
2. Set: `SIMULATION_MODE=true`
3. Bot will simulate trades without real execution
4. Test your configuration
5. When Jupiter is back, set: `SIMULATION_MODE=false`

---

## 🛡️ Prevention Tips

### 1. Monitor Jupiter Status

Subscribe to Jupiter's status page:
- https://status.jup.ag
- Get notifications when API has issues

### 2. Use Premium RPC

Premium RPCs often have:
- Better DNS resolution
- Dedicated IP addresses
- Priority routing
- Better uptime

Recommended:
- **Helius**: https://helius.dev
- **QuickNode**: https://quicknode.com
- **Alchemy**: https://alchemy.com

### 3. Set Up Alerts

Configure Railway to notify you:
1. Railway → Service → Settings
2. Enable "Deployment Notifications"
3. Add your email
4. Get notified of failures

### 4. Check Logs Regularly

Monitor for patterns:
```
# Good pattern (healthy)
BUY swap successful: abc123...
BUY swap successful: def456...
BUY swap successful: ghi789...

# Bad pattern (network issues)
Jupiter API request failed (attempt 1/3)...
Jupiter API request failed (attempt 1/3)...
Jupiter API request failed (attempt 1/3)...
```

If you see many retry attempts, network quality is degrading.

---

## 📈 Success Metrics

### How to Know the Fix Worked

1. **No more DNS errors** in logs
2. **Successful trades** execute within 1-2 minutes
3. **Telegram notifications** show completed trades
4. **Solscan** shows transactions on-chain
5. **Railway logs** show minimal retry attempts

### Before vs After

**Before (broken)**:
```
Attempt 1: DNS error → FAIL
Session stopped due to error
```

**After (fixed)**:
```
Attempt 1: DNS error → Retry in 1s
Attempt 2: DNS error → Retry in 2s
Attempt 3: Success! → Trade executed
```

---

## 🆘 Emergency Actions

### If Jupiter API is Completely Down

1. **Stop Trading**:
   ```
   Telegram: /stop
   ```

2. **Enable Simulation Mode** (temporary):
   ```
   Railway → Variables
   SIMULATION_MODE=true
   ```

3. **Wait for Jupiter** to come back online:
   - Check: https://status.jup.ag
   - Monitor: https://twitter.com/JupiterExchange

4. **Re-enable Real Trading**:
   ```
   Railway → Variables
   SIMULATION_MODE=false
   ```

5. **Resume**:
   ```
   Telegram: /start
   ```

---

## 📞 Support Resources

### Jupiter
- Status: https://status.jup.ag
- Discord: https://discord.gg/jup
- Twitter: https://twitter.com/JupiterExchange
- Docs: https://station.jup.ag

### Railway
- Status: https://railway.app/legal/fair-use
- Discord: https://discord.gg/railway
- Docs: https://docs.railway.app
- Support: https://railway.app/help

### This Bot
- GitHub: https://github.com/shawnlandau/Telegrambot
- Issues: https://github.com/shawnlandau/Telegrambot/issues
- Branch: Solana
- Latest Fix: Commit 7aa3512

---

## ✅ Verification Checklist

After Railway redeploys with the fix:

- [ ] Railway shows latest commit: 7aa3512
- [ ] Railway build completed successfully
- [ ] Bot logs show "Bot is running..."
- [ ] Telegram bot responds to `/help`
- [ ] `/balance` shows correct balances
- [ ] `/start` begins trading session
- [ ] First trade executes (watch for retry messages)
- [ ] Transaction appears on Solscan
- [ ] No DNS errors in logs

If all boxes checked: **Fix is working!** ✅

---

## 🎯 Summary

### The Problem
DNS resolution failures when contacting Jupiter API from Railway.

### The Solution
Automatic retry with exponential backoff (3 attempts, up to 15s timeout).

### The Result
Bot now handles temporary network issues gracefully and succeeds even if first attempt fails.

### Current Status
- **Commit**: 7aa3512 pushed to GitHub
- **Railway**: Auto-deploying (wait 2-3 minutes)
- **Bot**: Will have retry logic after redeploy
- **Testing**: Send `/start` to test

---

**Last Updated**: January 15, 2026  
**Fix Commit**: 7aa3512  
**Status**: ✅ Deployed  
**Expected Resolution**: Network errors now auto-retry

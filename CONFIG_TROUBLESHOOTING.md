# 🔧 Config Command Troubleshooting

## What exactly is "not working"?

Please tell me which scenario matches your issue:

### Scenario 1: Bot doesn't respond to `/config` at all
**Symptoms**:
- You send `/config`
- Nothing happens
- No response from bot

**Possible Causes**:
- Bot is not running
- Authorization issue
- Command not registered

**Check**:
1. Send `/help` - does it respond?
2. Check Railway logs for errors
3. Verify your Telegram user ID is in `ALLOWED_TELEGRAM_IDS`

---

### Scenario 2: Bot responds but conversation doesn't progress
**Symptoms**:
- Bot says "Let's configure..."
- You enter a number
- Bot doesn't move to next step

**Possible Causes**:
- ConversationHandler not working
- Message filters issue
- State management problem

**Check**:
1. Are you sending plain numbers (not "/config 1.0")?
2. Railway logs show "User X configured..."?

---

### Scenario 3: Config saves but trades don't use it
**Symptoms**:
- `/config` completes successfully
- Bot says "Configuration saved!"
- But `/start` uses wrong values

**Possible Causes**:
- Database not persisting
- Session using cached config
- Wrong user ID

**Check**:
1. Stop session: `/stop`
2. Run `/config` again
3. Check values shown in `/status`

---

### Scenario 4: Config values are ignored during trading
**Symptoms**:
- Config shows correct values
- But trades use different amounts

**Possible Causes**:
- Trade amount calculation wrong
- Using default config instead
- Hardcoded values somewhere

**Check**:
1. What does `/status` show?
2. What amounts appear in trade notifications?
3. Do they match your config?

---

## Quick Diagnostic

### Test 1: Check Bot Responsiveness
```
Send: /help
Expected: Bot shows command list
```

### Test 2: Check Authorization
```
Send: /balance
Expected: Shows your SOL balance
```

### Test 3: Check Config Flow
```
Send: /config
Expected: "Let's configure your trading parameters..."
Send: 1.0
Expected: "✅ Total liquidity: 1.00... Now enter the trade percentage..."
Send: 50
Expected: "✅ Trade percentage: 50%... Finally, enter the interval..."
Send: 300
Expected: "✅ Configuration saved!... Total Liquidity: 1.00..."
```

### Test 4: Check Config Persistence
```
Send: /status
Expected: Shows your configured values
```

### Test 5: Check Trading Uses Config
```
Send: /start
Expected: "Trading session started!... Trade Amount: 0.50..." (50% of 1.0)
Wait for trade notification
Expected: "✅ BUY completed: In: 0.500000 SOL..."
```

---

## Common Issues & Fixes

### Issue: "Cannot change configuration while session is active"
**Fix**: Send `/stop` first, then `/config`

### Issue: Bot doesn't respond to numbers
**Possible Fix**: Send plain numbers, not commands
- ✅ Correct: `1.0`
- ❌ Wrong: `/config 1.0`

### Issue: Configuration resets after restart
**Cause**: Database issue
**Fix**: Check Railway logs for database errors

### Issue: Trades use wrong amounts
**Debug**:
1. Check what `/status` shows for "Trade Amount"
2. Compare to actual trade notifications
3. Check Railway logs for "Getting Jupiter quote for X lamports"

---

## Railway Logs to Check

### Good logs (config working):
```
User 12345 configured trading parameters
Session config saved: user_id=12345, liquidity=1.0, pct=50
User 12345 started trading session
Getting Jupiter quote for 500000000 lamports...  (0.5 SOL)
BUY swap successful
```

### Bad logs (config not working):
```
User 12345 configured trading parameters
[No "Session config saved" message]
OR
Getting Jupiter quote for 300000000 lamports...  (wrong amount)
```

---

## Manual Database Check (Advanced)

If you suspect database isn't saving config:

```bash
# In Railway shell (if available) or locally:
sqlite3 bot_data.db
SELECT * FROM session_configs;
.quit
```

Should show your user_id with configured values.

---

## Environment Variable Check

Verify in Railway → Variables:

```
ALLOWED_TELEGRAM_IDS=YOUR_USER_ID  ← Must match your Telegram ID
```

Get your ID:
1. Telegram → Search "@userinfobot"
2. Send `/start`
3. Copy the ID number

---

## If Nothing Works

### Nuclear Option: Reset Everything

1. **Stop bot**:
   ```
   Telegram: /stop
   ```

2. **Reset config**:
   ```
   Telegram: /reset
   ```

3. **Reconfigure**:
   ```
   Telegram: /config
   Enter: 1.0
   Enter: 50
   Enter: 300
   ```

4. **Verify**:
   ```
   Telegram: /status
   Check values are correct
   ```

5. **Test trade**:
   ```
   Telegram: /start
   Wait for first trade
   Check amount is 0.5 SOL (50% of 1.0)
   ```

---

## Report Back

Please tell me:

1. **Which scenario above matches your issue?**
2. **What does `/help` show?** (Does bot respond at all?)
3. **What happens when you send `/config`?** (Exact response)
4. **What does `/status` show?** (Your current config)
5. **What appears in trade notifications?** (Actual amounts used)

With this info, I can pinpoint the exact issue!

---

## Possible Code Issues

If the command truly isn't working, here are places to check:

### 1. ConversationHandler Registration
Location: `bot/main.py` lines 696-706

Should see:
```python
config_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('config', cmd_config_start)],
    states={...},
    fallbacks=[...]
)
application.add_handler(config_conv_handler)
```

### 2. Authorization Decorator
Location: `bot/main.py` line 265

```python
@check_authorization
@check_rate_limit
async def cmd_config_start(...):
```

If your user ID isn't in `ALLOWED_TELEGRAM_IDS`, this blocks you.

### 3. Database Save
Location: `bot/main.py` line 349

```python
db.save_session_config(session_config)
```

If this fails silently, config won't persist.

### 4. Session Start Reading Config
Location: `bot/session_runner.py` (start_session method)

Should load config from database and use those values.

---

Let me know the exact symptoms and I'll provide a targeted fix!

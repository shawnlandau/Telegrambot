# 🔧 Quick Fix: Enable Simulation Mode

Railway has persistent DNS resolution issues with Jupiter API. Here's how to work around it temporarily:

## Enable Simulation Mode

1. **Go to Railway** → Your Service → Variables
2. **Update**:
   ```
   SIMULATION_MODE=true
   ```
3. **Click Save** (Railway auto-redeploys)
4. **Wait 2-3 minutes**

## Test the Bot

```
Telegram:
/config
1.0
50
300
/start
```

Bot will:
- ✅ Simulate price fetching
- ✅ Simulate BUY/SELL trades
- ✅ Update mock balances
- ✅ Send trade notifications
- ✅ Show realistic price variations (±2%)
- ❌ NOT execute real blockchain transactions

## When to Use Real Mode

Once Railway's DNS issues resolve (or you move to a different host):

1. **Railway** → Variables
2. **Update**:
   ```
   SIMULATION_MODE=false
   ```
3. Bot will execute real trades via Jupiter

---

## Why This Is Happening

Railway's network cannot resolve `quote-api.jup.ag` - this is a **Railway infrastructure issue**, not your code.

Possible causes:
- Railway's DNS resolver is down/broken
- Regional DNS propagation issues
- Railway blocking Jupiter's domain
- Temporary network routing problems

---

## Long-term Solution: Move to Different Platform

If Railway continues having DNS issues, consider:

### Option A: Heroku
- More reliable DNS
- Similar pricing
- Easy migration

### Option B: DigitalOcean App Platform  
- More stable
- Better network routing
- $5-10/month

### Option C: AWS Lightsail
- Enterprise DNS
- Very reliable
- $3.50-5/month

### Option D: Your Own VPS
- Full control
- Install dependencies
- No DNS issues
- DigitalOcean/Linode droplet $5-10/month

---

For now, enable **SIMULATION_MODE=true** to test everything except real trades.

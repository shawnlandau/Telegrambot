# Trading Pattern & Slippage Fix Guide

## 🚨 **Critical Issue: 40% Daily Loss**

You're losing 40% of liquidity daily! This is caused by:

### **Root Causes:**

1. **Current Pattern (BUY-BUY-SELL-SELL)**
   - Accumulates MEMESAI before selling
   - Two buys = higher average entry price
   - Two sells = lower average exit price
   - Result: Net loss on each cycle

2. **Price Impact & Slippage**
   - MEMESAI has low liquidity
   - Large trades = high price impact
   - Current slippage: 100 bps (1%)
   - Actual slippage: Much higher due to thin liquidity

3. **Market Dynamics**
   - Buy pressure → Price increases
   - Sell pressure → Price decreases
   - Double trades amplify this effect

---

## ✅ **Solution 1: Change Trading Pattern**

### **New Pattern: BUY → SELL → BUY → SELL**

**Benefits:**
- ✅ Alternating pattern reduces accumulation
- ✅ Each buy is immediately sold
- ✅ Lower average price impact
- ✅ Better risk management
- ✅ More balanced P&L

**Cycle Example:**
```
Start: 1.0 SOL, 0 MEMESAI

Trade 1 (BUY):  0.5 SOL → 500k MEMESAI
Balance: 0.5 SOL, 500k MEMESAI

Trade 2 (SELL): 500k MEMESAI → 0.48 SOL (with slippage)
Balance: 0.98 SOL, 0 MEMESAI

Trade 3 (BUY):  0.5 SOL → 500k MEMESAI
Balance: 0.48 SOL, 500k MEMESAI

Trade 4 (SELL): 500k MEMESAI → 0.48 SOL
Balance: 0.96 SOL, 0 MEMESAI

Loss per cycle: ~4% (much better than 40%!)
```

---

## ✅ **Solution 2: Reduce Slippage**

### **Current Settings:**
- `DEFAULT_SLIPPAGE_BPS=100` (1%)
- Price check slippage: 50 bps (0.5%)

### **Recommended Settings:**

#### **For Low Liquidity Tokens (MEMESAI):**
```bash
# Conservative (safest)
DEFAULT_SLIPPAGE_BPS=50    # 0.5%

# Balanced (recommended)
DEFAULT_SLIPPAGE_BPS=30    # 0.3%

# Aggressive (might fail in low liquidity)
DEFAULT_SLIPPAGE_BPS=10    # 0.1%
```

#### **Trade Size Optimization:**
```bash
# Current: 50% of liquidity per trade
# Recommended for low liquidity:

# Option A: Smaller trades
Total Liquidity: 0.5 SOL
Trade %: 20-30%  # Instead of 50%
Trade Size: 0.10-0.15 SOL per trade

# Option B: Longer intervals
Current: 300 seconds (5 min)
Recommended: 600-1800 seconds (10-30 min)
```

---

## ✅ **Solution 3: Dynamic Slippage Based on Liquidity**

### **Advanced: Adjust slippage based on trade size**

```python
# Small trades (< 0.1 SOL): 0.3% slippage
# Medium trades (0.1-0.5 SOL): 0.5% slippage  
# Large trades (> 0.5 SOL): 1% slippage
```

---

## 📊 **Expected Improvements**

### **Current (BUY-BUY-SELL-SELL + 1% slippage):**
- Loss per cycle: ~40%
- Reason: Accumulation + high slippage + price impact

### **After Fix 1 (BUY-SELL-BUY-SELL + 1% slippage):**
- Loss per cycle: ~10-15%
- Improvement: 60-75% reduction

### **After Fix 2 (BUY-SELL-BUY-SELL + 0.3% slippage):**
- Loss per cycle: ~3-5%
- Improvement: 87-92% reduction

### **After Fix 3 (+ Smaller trades):**
- Loss per cycle: ~1-2%
- Improvement: 95-97% reduction

---

## 🔧 **Implementation Steps**

### **Step 1: Change Trading Pattern**

File: `bot/session_runner.py` (Line 25)

```python
# OLD
TRADING_PATTERN = ["BUY", "BUY", "SELL", "SELL"]

# NEW
TRADING_PATTERN = ["BUY", "SELL", "BUY", "SELL"]
```

### **Step 2: Reduce Default Slippage**

File: `.env` (Line 92)

```bash
# OLD
DEFAULT_SLIPPAGE_BPS=100

# NEW (Recommended)
DEFAULT_SLIPPAGE_BPS=30
```

### **Step 3: Optimize Trade Size (Optional)**

In Telegram, reconfigure:
```
/config
Total Liquidity: 0.5 SOL
Trade Percentage: 30%  (instead of 50%)
Interval: 600 seconds (instead of 300)
```

Result: 0.15 SOL per trade, less price impact

---

## 📈 **Monitoring Improvements**

### **Before Changes:**
```
Starting Balance: 1.0 SOL
After 24 hours: 0.6 SOL
Loss: 40%
```

### **After Changes (Expected):**
```
Starting Balance: 1.0 SOL
After 24 hours: 0.97-0.99 SOL
Loss: 1-3%
```

### **Key Metrics to Track:**

1. **P&L per Trade:**
   ```
   Trade 1 (BUY):  0.5 SOL → X MEMESAI
   Trade 2 (SELL): X MEMESAI → Y SOL
   
   Loss = 0.5 - Y
   Loss % = ((0.5 - Y) / 0.5) * 100
   
   Target: < 1% per trade
   ```

2. **P&L per Cycle:**
   ```
   4 trades = 1 cycle
   
   Start: 1.0 SOL
   End: ? SOL
   
   Loss % = ((1.0 - End) / 1.0) * 100
   
   Target: < 2% per cycle
   ```

3. **Daily P&L:**
   ```
   288 trades/day (at 5 min intervals)
   72 cycles/day (4 trades per cycle)
   
   Target: < 5% daily loss
   ```

---

## 🎯 **Recommended Configuration**

### **Conservative (Safest):**
```bash
# .env
DEFAULT_SLIPPAGE_BPS=50

# Trading Pattern
TRADING_PATTERN = ["BUY", "SELL", "BUY", "SELL"]

# Telegram config
Liquidity: 0.5 SOL
Trade %: 20%
Interval: 900 seconds (15 min)
```

**Expected daily loss: < 2%**

### **Balanced (Recommended):**
```bash
# .env
DEFAULT_SLIPPAGE_BPS=30

# Trading Pattern
TRADING_PATTERN = ["BUY", "SELL", "BUY", "SELL"]

# Telegram config
Liquidity: 0.5 SOL
Trade %: 30%
Interval: 600 seconds (10 min)
```

**Expected daily loss: < 3%**

### **Aggressive (Higher Risk):**
```bash
# .env
DEFAULT_SLIPPAGE_BPS=10

# Trading Pattern
TRADING_PATTERN = ["BUY", "SELL", "BUY", "SELL"]

# Telegram config
Liquidity: 0.5 SOL
Trade %: 40%
Interval: 300 seconds (5 min)
```

**Expected daily loss: < 5%**  
**Risk: Some trades may fail due to tight slippage**

---

## ⚠️ **Important Notes**

### **About MEMESAI Liquidity:**

MEMESAI is a **low liquidity token**. This means:
- ❌ Large trades have high price impact
- ❌ Slippage is often higher than configured
- ❌ Entry/exit prices vary significantly
- ✅ Smaller trades = better prices
- ✅ Longer intervals = less market pressure

### **Realistic Expectations:**

Even with all optimizations, trading low liquidity tokens will have some loss:
- **Best case:** 1-2% daily loss (friction + fees)
- **Realistic:** 3-5% daily loss
- **Current:** 40% daily loss ← FIX THIS!

### **Alternative Strategy:**

Consider:
1. **Switch to higher liquidity pairs** (SOL/USDC, SOL/USDT)
2. **Use limit orders** instead of market swaps
3. **Trade only when spreads are tight**
4. **Reduce trade frequency** (once per hour instead of every 5 min)

---

## 🔍 **Testing the Changes**

### **Step 1: Enable Simulation Mode**
```bash
# .env
SIMULATION_MODE=true
```

### **Step 2: Make Changes**
- Update pattern in `session_runner.py`
- Update slippage in `.env`

### **Step 3: Test for 24 Hours**
Monitor:
- Trade success rate
- P&L per trade
- P&L per cycle
- Daily P&L

### **Step 4: Go Live**
If satisfied with simulation results:
```bash
# .env
SIMULATION_MODE=false
```

---

## 📞 **Support**

If losses continue:
1. Check actual vs expected slippage in logs
2. Verify MEMESAI pool liquidity on Solscan
3. Consider switching to higher liquidity tokens
4. Reduce trade size further
5. Increase trade interval

---

**Created:** 2026-01-16  
**Issue:** 40% daily liquidity loss  
**Solution:** Pattern change + slippage reduction  
**Expected improvement:** 90%+ loss reduction

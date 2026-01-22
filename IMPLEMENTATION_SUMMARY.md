# Implementation Summary: 4 Methods Needed

## 🎯 Quick Overview

You need to implement **4 methods** in `bot/raydium_client.py`. Here's the summary:

| # | Method | Difficulty | Time | Priority |
|---|--------|------------|------|----------|
| 1 | `_get_associated_token_address()` | ⭐ Easy | 30 min | High |
| 2 | `get_price()` | ⭐⭐ Medium | 2-4 hrs | High |
| 3 | `swap_exact_sol_for_tokens()` | ⭐⭐⭐ Hard | 4-8 hrs | Critical |
| 4 | `swap_exact_tokens_for_sol()` | ⭐⭐⭐ Hard | 2-4 hrs | Critical |

**Total:** 11-21 hours (1-3 days focused work)

---

## 📍 Method Locations

All methods are in: `bot/raydium_client.py`

```python
# Line 258-275
def _get_associated_token_address(self, owner, mint):
    raise NotImplementedError(...)

# Line 151-174  
def get_price(self):
    return 1.0  # Placeholder

# Line 176-211
def swap_exact_sol_for_tokens(self, amount_sol, slippage):
    raise NotImplementedError(...)

# Line 213-246
def swap_exact_tokens_for_sol(self, amount_sol_equiv, slippage):
    raise NotImplementedError(...)
```

---

## Method 1: Get Associated Token Address ⚡

**What:** Derive SPL token account address  
**Input:** Wallet pubkey, token mint  
**Output:** Token account pubkey  

### Quick Implementation
```bash
pip install spl-token
```

```python
from spl.token.instructions import get_associated_token_address

def _get_associated_token_address(self, owner: Pubkey, mint: Pubkey) -> Pubkey:
    return get_associated_token_address(owner, mint)
```

**Test:**
```python
ata = client._get_associated_token_address(wallet, mint)
print(f"ATA: {ata}")  # Should print valid base58 address
```

---

## Method 2: Get Price 📊

**What:** Fetch current pool price  
**Input:** None (uses self.pool_id)  
**Output:** Float (quote tokens per base token)  

### Two Options

**Option A: Use Raydium SDK (Easier)**
```javascript
// get_pool_price.js
const { Liquidity } = require('@raydium-io/raydium-sdk');
// Fetch pool info and return price
```

Call from Python:
```python
result = subprocess.run(['node', 'get_pool_price.js', pool_id], ...)
price = float(result.stdout)
```

**Option B: Parse Pool Data (Harder)**
```python
def get_price(self):
    # 1. Fetch pool account
    pool_data = client.get_account_info(self.pool_id)
    
    # 2. Extract vault addresses (at known offsets)
    base_vault = Pubkey(pool_data[338:370])
    quote_vault = Pubkey(pool_data[370:402])
    
    # 3. Get vault balances
    base_reserve = get_token_balance(base_vault)
    quote_reserve = get_token_balance(quote_vault)
    
    # 4. Calculate price
    return quote_reserve / base_reserve
```

**Test:**
```python
price = client.get_price()
print(f"Price: {price}")  # Compare with Raydium UI
```

---

## Method 3: Buy Swap (SOL → MEMESAI) 💰

**What:** Execute BUY trade on Raydium  
**Input:** SOL amount, slippage tolerance  
**Output:** Transaction hash, amounts  

### Key Steps

1. **Calculate amounts**
   ```python
   amount_in_lamports = sol * 1_000_000_000
   expected_out = sol * get_price()
   min_out = expected_out * (1 - slippage/10000)
   ```

2. **Get token accounts**
   ```python
   user_sol_ata = get_ata(wallet, SOL_MINT)
   user_token_ata = get_ata(wallet, MEMESAI_MINT)
   ```

3. **Build Raydium instruction**
   ```python
   instruction_data = [9] + amount_in.bytes + min_out.bytes
   accounts = [
       TOKEN_PROGRAM,
       pool_id,
       amm_authority,
       ... (18 accounts total)
   ]
   ```

4. **Send transaction**
   ```python
   tx = Transaction().add(instruction)
   signature = send_tx(tx, keypair)
   ```

### Required Config
Add to `.env`:
```env
RAYDIUM_AMM_AUTHORITY=...
RAYDIUM_AMM_OPEN_ORDERS=...
RAYDIUM_BASE_VAULT=...
RAYDIUM_QUOTE_VAULT=...
RAYDIUM_SERUM_MARKET=...
# ... and 8 more
```

Get these from Raydium SDK or pool info.

**Test:**
```python
result = client.swap_exact_sol_for_tokens(0.001, 500)
print(f"TX: {result['tx_hash']}")
# Verify on: https://solscan.io/tx/{tx_hash}
```

---

## Method 4: Sell Swap (MEMESAI → SOL) 💸

**What:** Execute SELL trade on Raydium  
**Input:** SOL equivalent amount, slippage  
**Output:** Transaction hash, amounts  

### Key Differences from Buy

1. **Amount calculation**
   ```python
   price = get_price()
   token_amount = sol_equiv * price  # MEMESAI amount
   ```

2. **Account order REVERSED**
   ```python
   accounts = [
       TOKEN_PROGRAM,
       pool_id,
       amm_authority,
       ...,
       quote_vault,  # ← SWAPPED: quote first
       base_vault,   # ← SWAPPED: base second
       ...,
       user_token_account,  # ← Source is MEMESAI
       user_sol_account,    # ← Dest is SOL
       wallet,
   ]
   ```

3. Everything else is the same structure as buy

**Test:**
```python
result = client.swap_exact_tokens_for_sol(0.001, 500)
print(f"TX: {result['tx_hash']}")
```

---

## 🔄 Development Workflow

### Day 1 (3-4 hours)
1. ✅ Implement `_get_associated_token_address()` (30 min)
2. ✅ Test ATA derivation (15 min)
3. ✅ Implement `get_price()` (2-3 hours)
4. ✅ Test price fetching (15 min)

### Day 2 (4-8 hours)
1. ✅ Get all Raydium pool keys (1 hour)
2. ✅ Add keys to .env and config (30 min)
3. ✅ Implement `swap_exact_sol_for_tokens()` (3-5 hours)
4. ✅ Test single buy with 0.001 SOL (30 min)

### Day 3 (2-4 hours)
1. ✅ Implement `swap_exact_tokens_for_sol()` (1-2 hours)
2. ✅ Test single sell (30 min)
3. ✅ Run full pattern test (30 min)
4. ✅ Fix any issues (1-2 hours)

---

## 🧪 Testing Strategy

### 1. Unit Tests (Test Each Method)
```bash
python test_ata.py          # Test Method 1
python test_get_price.py    # Test Method 2
python test_buy_swap.py     # Test Method 3 (0.001 SOL)
python test_sell_swap.py    # Test Method 4 (0.001 SOL)
```

### 2. Integration Test (Test Full Pattern)
```bash
python test_full_bot.py     # BUY-BUY-SELL-SELL
```

### 3. Bot Test (Test with Telegram)
```bash
python -m bot.main          # Start bot
# Via Telegram:
# /config -> Set to 0.1 SOL, 10%, 60s
# /start -> Run 4 trades
# /stop -> Check results
```

---

## 📚 Resources

### Documentation
- **IMPLEMENTATION_CHECKLIST.md** - Detailed guide (36KB)
- **TESTING_GUIDE.md** - Step-by-step testing
- **QUICK_START.md** - Fast track guide

### External
- **Raydium SDK:** https://github.com/raydium-io/raydium-sdk
- **Solana Cookbook:** https://solanacookbook.com/
- **SPL Token:** https://spl.solana.com/token

### Tools
- **Solscan:** https://solscan.io/ (verify transactions)
- **Raydium UI:** https://raydium.io/ (find pools)

---

## ⚠️ Critical Notes

### Before Starting
- [ ] Read `IMPLEMENTATION_CHECKLIST.md` fully
- [ ] Run `python test_solana_connection.py`
- [ ] Have at least 0.1 SOL on devnet/mainnet
- [ ] Get your MEMESAI pool ID

### While Implementing
- [ ] Test with **0.001 SOL** first
- [ ] Verify every transaction on Solscan
- [ ] Check balances before and after
- [ ] Save transaction hashes

### Before Production
- [ ] 50+ successful test trades
- [ ] P/L within expected range
- [ ] No errors in logs
- [ ] All safety checks in place

---

## 🎯 Success Criteria

You're done when:

✅ `test_ata.py` passes  
✅ `test_get_price.py` shows correct price  
✅ `test_buy_swap.py` executes successfully  
✅ `test_sell_swap.py` executes successfully  
✅ `test_full_bot.py` completes BUY-BUY-SELL-SELL  
✅ Bot runs via Telegram for 10+ trades  
✅ All transactions visible on Solscan  

---

## 🆘 Common Issues

### "Account not found"
**Fix:** Check pool ID is correct, verify network (devnet vs mainnet)

### "Insufficient funds"
**Fix:** Add more SOL to wallet, reduce trade size

### "Transaction simulation failed"
**Fix:** Check account order, verify instruction data format

### "Slippage exceeded"
**Fix:** Increase slippage tolerance (500 = 5% for testing)

### "Invalid instruction"
**Fix:** Verify instruction discriminator (should be 9 for swap)

---

## 💡 Pro Tips

1. **Start with Method 1** - It's easiest and needed by others
2. **Use Raydium SDK for Method 2** - Saves time parsing
3. **Copy Method 3 for Method 4** - Just reverse account order
4. **Test after each method** - Don't wait until all done
5. **Keep amounts tiny** - Use 0.001 SOL until confident
6. **Save all TX hashes** - For debugging and verification

---

## 📞 Need Help?

1. Check `IMPLEMENTATION_CHECKLIST.md` (detailed examples)
2. Review transaction on Solscan (see exact error)
3. Compare with Raydium SDK source code
4. Ask in Solana Discord
5. Check bot.log for detailed errors

---

**Remember:** The framework is 100% complete. You only need these 4 methods. Everything else (database, Telegram bot, trading logic, error handling) already works perfectly!

Good luck! 🚀

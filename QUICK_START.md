# Quick Start Testing Guide

## 🚀 Fast Track Testing (For Experienced Developers)

### 1. Setup (5 minutes)
```bash
cd /home/user/webapp
git checkout Solana
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Get Devnet Wallet (2 minutes)
```bash
solana-keygen new -o ~/devnet-wallet.json
solana airdrop 2 $(solana-keygen pubkey ~/devnet-wallet.json) --url devnet
```

### 3. Configure .env (3 minutes)
```bash
cp .env.example .env
# Edit .env with:
# - SOLANA_RPC_URL=https://api.devnet.solana.com
# - WALLET_PRIVATE_KEY=<from keypair>
# - TELEGRAM_BOT_TOKEN=<from @BotFather>
# - ALLOWED_TELEGRAM_IDS=<your telegram id>
```

### 4. Test Connectivity (2 minutes)
```bash
python test_solana_connection.py
```

**Expected:** All tests pass ✅

### 5. Understand What's Missing
```bash
python find_raydium_pools.py
```

**Key takeaway:** You need to implement:
- `swap_exact_sol_for_tokens()` in `bot/raydium_client.py`
- `swap_exact_tokens_for_sol()` in `bot/raydium_client.py`
- `get_price()` in `bot/raydium_client.py`

---

## 📝 What You Have vs What You Need

### ✅ What's Working (Framework Complete)
- Solana RPC connectivity
- Wallet loading and balance checking
- Configuration management
- Database schema
- Telegram bot UI
- Trading loop logic
- Session management

### ⏳ What Needs Implementation (Raydium-Specific)
- **Pool State Parsing**: Read Raydium AMM pool accounts
- **Price Calculation**: Calculate price from pool reserves
- **Swap Instructions**: Build Raydium swap transactions
- **Token Accounts**: Create/manage SPL token accounts
- **Transaction Sending**: Send and confirm transactions

---

## 🎯 Three Testing Approaches

### Approach 1: Mock Testing (Start Here) ⭐
**Time:** 1-2 hours  
**Risk:** Zero  
**Cost:** Free

Test bot logic without blockchain:
1. Create mock implementation (see TESTING_GUIDE.md Phase 3)
2. Run bot with mocked methods
3. Test all Telegram commands
4. Verify database operations
5. Confirm trading pattern logic

**Pros:**
- Safe, no real funds
- Fast iteration
- Tests bot logic thoroughly

**Cons:**
- Doesn't test actual blockchain interaction

### Approach 2: Mainnet with Small Amounts (Recommended) ⭐⭐
**Time:** 3-7 days  
**Risk:** Low ($0.50-$5)  
**Cost:** Minimal

Implement and test with real blockchain:
1. Find MEMESAI pool on Raydium mainnet
2. Implement Raydium SDK integration
3. Test with 0.01 SOL per trade
4. Monitor 10-20 trades carefully
5. Scale up gradually

**Pros:**
- Real environment
- Actual liquidity and pricing
- Production-like testing

**Cons:**
- Requires Raydium implementation
- Small cost for testing
- Need to monitor closely

### Approach 3: Devnet Pool Creation (Advanced) ⭐⭐⭐
**Time:** 1-2 weeks  
**Risk:** Low  
**Cost:** Free (devnet)

Create your own test environment:
1. Deploy Raydium contracts on devnet
2. Create test tokens
3. Initialize liquidity pool
4. Test in isolated environment

**Pros:**
- Complete control
- Free testing
- Repeatable setup

**Cons:**
- Very time-consuming
- Complex setup
- Not recommended for beginners

---

## 🔧 Implementation Priorities

### Priority 1: Get Price (Easiest)
```python
def get_price(self) -> float:
    # 1. Fetch pool account data
    # 2. Parse base and quote reserves
    # 3. Return quote_reserve / base_reserve
```

**Why first:** Non-destructive, read-only, easier to debug

### Priority 2: Buy Swap (SOL → MEMESAI)
```python
def swap_exact_sol_for_tokens(self, amount_sol, slippage_bps):
    # 1. Calculate expected output with slippage
    # 2. Build Raydium swap instruction
    # 3. Send transaction
    # 4. Wait for confirmation
    # 5. Return result
```

**Why second:** Most common operation, builds foundation

### Priority 3: Sell Swap (MEMESAI → SOL)
```python
def swap_exact_tokens_for_sol(self, amount_sol_equiv, slippage_bps):
    # Similar to buy but reversed
```

**Why third:** Uses same pattern as buy, easier with buy working

---

## 📚 Essential Resources

### Documentation
- **Raydium SDK**: https://github.com/raydium-io/raydium-sdk
- **Raydium Docs**: https://docs.raydium.io/
- **Solana Cookbook**: https://solanacookbook.com/
- **Solana.py Docs**: https://michaelhly.github.io/solana-py/

### Tools
- **Solscan**: https://solscan.io/ (Transaction explorer)
- **Raydium UI**: https://raydium.io/ (Find pools)
- **Solana Explorer**: https://explorer.solana.com/

### Community
- **Solana Discord**: https://discord.gg/solana
- **Raydium Discord**: Check Raydium website
- **Stack Exchange**: https://solana.stackexchange.com/

---

## ⚡ Quick Commands Reference

### Testing
```bash
# Test connectivity
python test_solana_connection.py

# Find pool info
python find_raydium_pools.py

# Run bot (after implementation)
python -m bot.main
```

### Wallet Management
```bash
# Check balance
solana balance --url devnet

# Get airdrop
solana airdrop 2 YOUR_ADDRESS --url devnet

# View wallet
solana-keygen pubkey ~/devnet-wallet.json
```

### Monitoring
```bash
# Watch logs
tail -f bot.log

# Check transactions
# Visit: https://solscan.io/tx/YOUR_TX_HASH
```

---

## 🎯 Success Checklist

Before moving to production:

- [ ] All connectivity tests pass
- [ ] Can fetch pool price accurately
- [ ] Single BUY swap executes successfully
- [ ] Single SELL swap executes successfully
- [ ] Telegram bot responds to all commands
- [ ] Trading loop follows BUY-BUY-SELL-SELL pattern
- [ ] Database records all trades
- [ ] Error handling works properly
- [ ] 50+ consecutive trades without errors
- [ ] P/L matches expectations
- [ ] Monitoring and alerts configured

---

## 🚨 Safety Rules

1. **Never test with mainnet without devnet/mock testing first**
2. **Start with 0.01 SOL or less on mainnet**
3. **Monitor every transaction on Solscan**
4. **Use dedicated wallet with limited funds**
5. **Have a kill switch ready** (`/stop` command)
6. **Back up your configuration and database**
7. **Test recovery procedures**

---

## 📞 Need Help?

1. **Read Full Guide**: `TESTING_GUIDE.md` (comprehensive)
2. **Check Logs**: `bot.log` (detailed errors)
3. **Review Code**: Comments in `raydium_client.py`
4. **Test Scripts**: Run test utilities
5. **Community**: Ask in Solana Discord

---

## 🎓 Learning Path

**Day 1-2:** Setup and connectivity testing  
**Day 3-4:** Understand Raydium pool structure  
**Day 5-7:** Implement get_price() and test  
**Day 8-10:** Implement swap methods  
**Day 11-14:** Test with small amounts  
**Day 15+:** Gradual scale-up and monitoring

---

Remember: **Quality over speed**. Take time to understand each component before moving to the next. The framework is solid - you just need to add the Raydium-specific implementations.

Good luck! 🚀

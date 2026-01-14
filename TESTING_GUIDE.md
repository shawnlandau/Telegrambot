# Testing Guide for Solana DEX Bot

This guide walks you through testing the Solana DEX bot step by step, from initial setup to production deployment.

## 📋 Prerequisites

Before you begin testing, ensure you have:

- [ ] Python 3.11 or higher installed
- [ ] Git installed and repository cloned
- [ ] Telegram account and bot token from @BotFather
- [ ] Basic understanding of Solana blockchain
- [ ] Access to a code editor

---

## 🎯 Testing Phases

### Phase 0: Initial Setup (30 minutes)

#### 1. Clone and Switch to Solana Branch

```bash
cd /home/user/webapp
git checkout Solana
git pull origin Solana
```

#### 2. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected output:**
- No errors during installation
- All packages installed successfully

**Common issues:**
- `solana-py` requires Rust compiler on some systems
- Use pre-built wheels when available

---

### Phase 1: Basic Connectivity Testing (15 minutes)

#### 1. Set Up Devnet Wallet

**Option A: Using Solana CLI**

```bash
# Install Solana CLI (if not installed)
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"

# Add to PATH
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"

# Configure for devnet
solana config set --url https://api.devnet.solana.com

# Generate new wallet
solana-keygen new -o ~/solana-devnet-wallet.json

# Get wallet address
solana-keygen pubkey ~/solana-devnet-wallet.json

# Request airdrop (2 SOL)
solana airdrop 2 $(solana-keygen pubkey ~/solana-devnet-wallet.json)

# Check balance
solana balance
```

**Option B: Using Phantom Wallet**

1. Install Phantom browser extension
2. Create new wallet or import existing
3. Switch to Devnet (Settings → Developer Settings → Change Network → Devnet)
4. Request airdrop from Phantom UI
5. Export private key (Settings → Security & Privacy → Show Private Key)

#### 2. Create .env Configuration

Create `.env` file in the project root:

```bash
# Copy example
cp .env.example .env

# Edit with your favorite editor
nano .env  # or vim, code, etc.
```

**Minimal configuration for connectivity testing:**

```env
# Solana Configuration
SOLANA_RPC_URL=https://api.devnet.solana.com
WALLET_PRIVATE_KEY=YOUR_BASE58_PRIVATE_KEY_HERE

# Raydium (use placeholders for now)
RAYDIUM_PROGRAM_ID=675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8
BASE_TOKEN_ADDRESS=So11111111111111111111111111111111111111112
QUOTE_TOKEN_ADDRESS=PLACEHOLDER_WILL_UPDATE_LATER
RAYDIUM_POOL_ID=PLACEHOLDER_WILL_UPDATE_LATER

# Telegram (create bot with @BotFather)
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
ALLOWED_TELEGRAM_IDS=YOUR_TELEGRAM_USER_ID

# Testing Settings
LOG_LEVEL=DEBUG
DATABASE_PATH=bot_data_devnet.db
COMMITMENT_LEVEL=confirmed
DEFAULT_SLIPPAGE_BPS=500
```

#### 3. Run Connectivity Test

```bash
python test_solana_connection.py
```

**Expected output:**
```
🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪
SOLANA DEX BOT - CONNECTION TEST SUITE
🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪

============================================================
STEP 1: Testing Package Imports
============================================================
✅ solana-py installed: 0.32.0
✅ solders installed
✅ base58 installed
✅ python-telegram-bot installed

✅ All required packages installed!

============================================================
STEP 2: Testing Configuration
============================================================
✅ Config loaded successfully
   RPC URL: https://api.devnet.solana.com
   Commitment: confirmed
   Database: bot_data_devnet.db
   Log Level: DEBUG

============================================================
STEP 3: Testing Solana RPC Connection
============================================================
✅ RPC Connection successful!
   Solana Version: {'solana-core': '1.x.x'}
✅ Can fetch blockhash
✅ Can fetch slot

✅ Solana RPC is working properly!

============================================================
STEP 4: Testing Wallet Loading
============================================================
✅ Wallet loaded successfully!
   Address: YOUR_WALLET_ADDRESS
✅ Wallet balance fetched
   Balance: 2.0000 SOL

✅ Wallet is ready!

============================================================
TEST SUMMARY
============================================================
✅ PASS: Package Imports
✅ PASS: Configuration
✅ PASS: Solana RPC Connection
✅ PASS: Wallet Loading

------------------------------------------------------------
Passed: 4/5
Failed: 0/5
------------------------------------------------------------

🎉 All tests passed! Ready for next phase.
```

**If tests fail:**
- Check `.env` file syntax
- Verify private key format (base58, no spaces)
- Ensure devnet SOL balance > 0
- Check RPC URL accessibility

---

### Phase 2: Implementation Phase (3-7 days)

This phase requires implementing the actual Raydium swap functionality. The bot framework is complete, but these methods need implementation:

#### Critical Files to Implement

**`bot/raydium_client.py`** - Methods needing implementation:

1. **`swap_exact_sol_for_tokens()`**
   - Build Raydium swap instruction
   - Handle token account creation
   - Send transaction
   - Parse results

2. **`swap_exact_tokens_for_sol()`**
   - Reverse swap implementation
   - Similar to above

3. **`get_price()`**
   - Fetch pool account data
   - Parse reserves
   - Calculate price ratio

4. **`_get_associated_token_address()`**
   - Derive ATA using proper seeds
   - Use SPL token utilities

#### Implementation Options

**Option 1: Use Raydium SDK via Node.js Bridge (Recommended)**

Pros:
- Official SDK, well-tested
- Complete functionality
- Good documentation

Cons:
- Requires Node.js bridge from Python
- Additional dependency

**Option 2: Use anchorpy with Raydium IDL**

Pros:
- Pure Python
- Direct program interaction
- Already have anchorpy installed

Cons:
- Need to obtain Raydium IDL
- More complex setup

**Option 3: Raw Transaction Building**

Pros:
- Full control
- No additional dependencies

Cons:
- Most complex
- Error-prone
- Requires deep understanding

#### Finding Raydium Pool Information

```bash
# Run pool finder helper
python find_raydium_pools.py
```

This will guide you through:
- Finding MEMESAI pools on Raydium
- Understanding pool structure
- Implementation tips

---

### Phase 3: Mock Testing (1-2 days)

Before implementing real swaps, test the bot logic with mocked methods.

#### Create Mock Client

Create `bot/raydium_client_mock.py`:

```python
"""Mock Raydium client for testing without real blockchain."""

from .raydium_client import RaydiumClient
from typing import Dict
import random

class RaydiumClientMock(RaydiumClient):
    """Mock client that simulates swaps without real transactions."""
    
    def __init__(self):
        # Skip parent __init__ to avoid real connection
        self.base_symbol = "SOL"
        self.quote_symbol = "MEMESAI"
        self.wallet_address = "MOCK_WALLET_ADDRESS"
        
        # Simulated balances
        self._mock_sol_balance = 10.0
        self._mock_token_balance = 0.0
        self._mock_price = 100.0  # 1 SOL = 100 MEMESAI
    
    def get_balances(self) -> Dict[str, float]:
        """Return mock balances."""
        return {
            "base": self._mock_sol_balance,
            "quote": self._mock_token_balance
        }
    
    def get_price(self) -> float:
        """Return mock price with small variation."""
        variation = random.uniform(-0.02, 0.02)  # ±2%
        return self._mock_price * (1 + variation)
    
    def swap_exact_sol_for_tokens(self, amount_sol, slippage_bps):
        """Simulate BUY trade."""
        price = self.get_price()
        amount_out = amount_sol * price * 0.997  # 0.3% fee
        
        # Update mock balances
        self._mock_sol_balance -= amount_sol
        self._mock_token_balance += amount_out
        
        return {
            'amount_in': amount_sol,
            'amount_out': amount_out,
            'tx_hash': f"MOCK_TX_{random.randint(10000, 99999)}",
            'slot': random.randint(100000000, 200000000)
        }
    
    def swap_exact_tokens_for_sol(self, amount_sol_equiv, slippage_bps):
        """Simulate SELL trade."""
        price = self.get_price()
        amount_in = amount_sol_equiv * price
        amount_out = amount_sol_equiv * 0.997  # 0.3% fee
        
        # Update mock balances
        self._mock_token_balance -= amount_in
        self._mock_sol_balance += amount_out
        
        return {
            'amount_in': amount_in,
            'amount_out': amount_out,
            'tx_hash': f"MOCK_TX_{random.randint(10000, 99999)}",
            'slot': random.randint(100000000, 200000000)
        }
```

#### Test with Mock Client

Modify `bot/main.py` temporarily to use mock:

```python
# In main() function, replace:
# raydium_client = RaydiumClient()

# With:
from .raydium_client_mock import RaydiumClientMock
raydium_client = RaydiumClientMock()
```

#### Run Mock Tests

```bash
python -m bot.main
```

Test via Telegram:
1. Send `/config` - Set up parameters
2. Send `/status` - Check configuration
3. Send `/start` - Start mock trading
4. Wait for a few trades
5. Send `/stop` - Stop and check summary

**Expected behavior:**
- Bot responds to all commands
- Mock trades execute successfully
- Balances update correctly
- Database records trades

---

### Phase 4: Real Implementation Testing (Ongoing)

#### Step 1: Implement One Method

Start with `get_price()`:

```python
def get_price(self) -> float:
    """Get price from Raydium pool reserves."""
    try:
        # Fetch pool account
        pool_account = self.client.get_account_info(self.pool_id)
        
        # Parse pool data (you need to understand Raydium structure)
        # This is a simplified example
        pool_data = pool_account.value.data
        
        # Extract reserves (offsets depend on Raydium version)
        # You'll need actual Raydium pool structure
        base_reserve = parse_u64(pool_data, OFFSET_BASE_RESERVE)
        quote_reserve = parse_u64(pool_data, OFFSET_QUOTE_RESERVE)
        
        # Calculate price
        price = (quote_reserve / 10**self.quote_decimals) / (base_reserve / 10**self.base_decimals)
        
        return price
    except Exception as e:
        logger.error(f"Failed to get price: {e}")
        raise
```

#### Step 2: Test Single Method

Create test script:

```python
from bot.raydium_client import RaydiumClient
from bot.config import config

client = RaydiumClient()
price = client.get_price()
print(f"Current price: {price}")
```

#### Step 3: Implement Swap Methods

Follow similar pattern for swap methods.

#### Step 4: Test on Mainnet with Tiny Amounts

**CRITICAL: Start with 0.01 SOL or less!**

Update `.env` for mainnet:

```env
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
# Use mainnet wallet with SMALL amount
# Update RAYDIUM_POOL_ID with real pool
```

Test single swap manually before starting bot:

```python
from bot.raydium_client import RaydiumClient

client = RaydiumClient()

# Test with 0.01 SOL
result = client.swap_exact_sol_for_tokens(0.01, 100)
print(f"Swap result: {result}")

# Check on Solscan: https://solscan.io/tx/{result['tx_hash']}
```

---

### Phase 5: Full Bot Testing (1-2 days)

#### Configuration for Testing

```bash
# In .env
LOG_LEVEL=DEBUG
MAX_TRADES_PER_SESSION=10  # Limit for testing
DEFAULT_SLIPPAGE_BPS=500  # 5% for testing (higher to avoid failures)
```

#### Test Telegram Bot

```bash
python -m bot.main
```

Via Telegram:

1. **Configuration Test**
   ```
   /config
   - Total Liquidity: 0.5 (SOL)
   - Trade %: 10 (so 0.05 SOL per trade)
   - Interval: 120 (2 minutes between trades)
   ```

2. **Pre-flight Checks**
   ```
   /status
   ```
   Verify:
   - Balances are correct
   - Price is reasonable
   - Configuration is as expected

3. **Start Trading**
   ```
   /start
   ```
   
4. **Monitor**
   - Watch for trade notifications
   - Check `/status` periodically
   - Monitor `bot.log` file
   - Check transactions on Solscan

5. **Stop After Few Trades**
   ```
   /stop
   ```

#### What to Monitor

- **Transaction Success Rate**: Should be 100%
- **Slippage**: Should be within expected range
- **Balance Changes**: Should match trade notifications
- **P/L**: Small loss expected (due to fees)
- **Bot Behavior**: Should follow BUY-BUY-SELL-SELL pattern

---

## 🐛 Common Issues and Solutions

### Issue: "NotImplementedError: Raydium swap functionality needs to be implemented"

**Solution:** This is expected. You need to implement the swap methods in `raydium_client.py`.

### Issue: Wallet has no SOL

**Solution:**
```bash
# Devnet
solana airdrop 2 YOUR_WALLET_ADDRESS --url devnet

# Mainnet - buy SOL from exchange
```

### Issue: Pool not found

**Solution:**
- Verify pool ID is correct
- Check you're using correct network (devnet vs mainnet)
- Ensure pool exists and has liquidity

### Issue: Transaction fails with "insufficient funds"

**Solution:**
- Check SOL balance (need for gas)
- Check token balance for SELL trades
- Reduce trade size

### Issue: High slippage/price impact

**Solution:**
- Increase slippage tolerance
- Reduce trade size
- Check pool liquidity

---

## 📊 Success Criteria

### Phase 1 (Connectivity): ✅
- [ ] All packages install
- [ ] RPC connection works
- [ ] Wallet loads correctly
- [ ] Balance fetching works

### Phase 2 (Implementation): ✅
- [ ] Pool data parsing works
- [ ] Price fetching accurate
- [ ] Single swap executes successfully
- [ ] Transaction confirmed on-chain

### Phase 3 (Bot Logic): ✅
- [ ] Telegram commands work
- [ ] Configuration saves correctly
- [ ] Trading loop executes
- [ ] Pattern follows BUY-BUY-SELL-SELL
- [ ] Statistics track correctly

### Phase 4 (Production Ready): ✅
- [ ] 50+ consecutive successful trades
- [ ] No unexpected errors
- [ ] P/L within expected range
- [ ] Clean error handling
- [ ] Proper logging

---

## 🎯 Next Steps After Testing

1. **Code Review**: Have someone review your implementation
2. **Security Audit**: Check for vulnerabilities
3. **Performance Optimization**: Optimize RPC calls and transaction building
4. **Monitoring Setup**: Set up alerts and dashboards
5. **Documentation**: Document any discoveries or customizations
6. **Gradual Scale**: Slowly increase trading amounts
7. **Premium RPC**: Consider QuickNode or Helius for production

---

## 📞 Getting Help

If you encounter issues:

1. Check `bot.log` for detailed error messages
2. Review transaction on Solscan
3. Search Solana/Raydium documentation
4. Ask in Solana Discord or Stack Exchange
5. Review this testing guide again

---

## ⚠️ Safety Reminders

- **Start Small**: Never test with amounts you can't afford to lose
- **Use Devnet First**: When possible
- **Monitor Closely**: Watch every transaction
- **Have Exit Strategy**: Know how to stop the bot quickly
- **Keep Backups**: Of configuration and logs
- **Test Recovery**: Know how to recover from errors

---

Good luck with testing! Remember: **Testing is NOT optional**. Take your time, be methodical, and never skip to production without thorough testing.

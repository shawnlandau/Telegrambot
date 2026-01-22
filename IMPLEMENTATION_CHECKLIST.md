# Implementation Checklist: Raydium-Specific Methods

This document provides a detailed, step-by-step checklist for implementing the 4 critical methods needed to make the Solana DEX bot functional.

---

## 📋 Overview of Methods to Implement

| Method | File | Lines | Difficulty | Priority | Estimated Time |
|--------|------|-------|------------|----------|----------------|
| `_get_associated_token_address()` | `bot/raydium_client.py` | ~258-275 | Easy | High | 30 min |
| `get_price()` | `bot/raydium_client.py` | ~151-174 | Medium | High | 2-4 hours |
| `swap_exact_sol_for_tokens()` | `bot/raydium_client.py` | ~176-211 | Hard | Critical | 4-8 hours |
| `swap_exact_tokens_for_sol()` | `bot/raydium_client.py` | ~213-246 | Hard | Critical | 4-8 hours |

**Total Estimated Time:** 11-21 hours (1-3 days of focused work)

---

## Method 1: `_get_associated_token_address()` ⭐

**Location:** `bot/raydium_client.py`, lines 258-275  
**Difficulty:** Easy  
**Dependencies:** SPL Token library  
**Estimated Time:** 30 minutes

### What It Does
Derives the Associated Token Account (ATA) address for a given wallet and token mint. This is where SPL tokens are stored for a user.

### Current Status
```python
def _get_associated_token_address(self, owner: Pubkey, mint: Pubkey) -> Pubkey:
    """Calculate the associated token account address for a given owner and mint."""
    # Placeholder implementation
    raise NotImplementedError(
        "Associated token address derivation needs to be implemented with proper SPL utilities"
    )
```

### Implementation Checklist

#### Step 1: Install SPL Token Library (if not already installed)
```bash
pip install spl-token
```

#### Step 2: Import Required Modules
Add to imports at top of `bot/raydium_client.py`:
```python
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import get_associated_token_address
```

#### Step 3: Replace Method Implementation
```python
def _get_associated_token_address(self, owner: Pubkey, mint: Pubkey) -> Pubkey:
    """
    Calculate the associated token account address for a given owner and mint.
    
    Args:
        owner: The wallet public key that owns the token account
        mint: The token mint address
    
    Returns:
        The derived ATA public key
    """
    try:
        # Use SPL token library to derive ATA
        ata = get_associated_token_address(owner, mint)
        return ata
    except Exception as e:
        logger.error(f"Failed to derive ATA for owner={owner}, mint={mint}: {e}")
        raise
```

#### Step 4: Test Independently
Create `test_ata.py`:
```python
from solders.pubkey import Pubkey
from bot.raydium_client import RaydiumClient
from bot.config import config

# Initialize client
client = RaydiumClient()

# Test ATA derivation
owner = client.keypair.pubkey()
mint = client.quote_token_mint

try:
    ata = client._get_associated_token_address(owner, mint)
    print(f"✅ ATA derived successfully: {ata}")
except Exception as e:
    print(f"❌ Failed: {e}")
```

Run test:
```bash
python test_ata.py
```

#### Step 5: Verification Checklist
- [ ] SPL token library installed
- [ ] Imports added correctly
- [ ] Method returns Pubkey type
- [ ] Test script runs without errors
- [ ] Derived address matches expected format (base58, 32 bytes)

---

## Method 2: `get_price()` ⭐⭐

**Location:** `bot/raydium_client.py`, lines 151-174  
**Difficulty:** Medium  
**Dependencies:** Understanding Raydium pool account structure  
**Estimated Time:** 2-4 hours

### What It Does
Fetches the Raydium pool account data, parses the token reserves, and calculates the current price (quote tokens per base token).

### Current Status
```python
def get_price(self) -> float:
    """Get approximate current price (quote per base)."""
    logger.warning("get_price() is not yet implemented - returning placeholder value")
    return 1.0
```

### Implementation Checklist

#### Step 1: Understand Raydium Pool Structure
Raydium AMM pools store data in this format (simplified):

```
Pool Account Data Structure (varies by version):
- Status (1 byte)
- Nonce (1 byte)
- Max Order (8 bytes)
- Depth (8 bytes)
- Base Decimal (8 bytes)
- Quote Decimal (8 bytes)
- State (8 bytes)
- Reset Flag (8 bytes)
- Min Size (8 bytes)
- Vol Max Cut Ratio (8 bytes)
- Amount Wave (8 bytes)
- Base Lot Size (8 bytes)
- Quote Lot Size (8 bytes)
- Min Price Multiplier (8 bytes)
- Max Price Multiplier (8 bytes)
- System Decimal Value (8 bytes)
- Min Separate Numerator (8 bytes)
- Min Separate Denominator (8 bytes)
- Trade Fee Numerator (8 bytes)
- Trade Fee Denominator (8 bytes)
- Pnl Numerator (8 bytes)
- Pnl Denominator (8 bytes)
- Swap Fee Numerator (8 bytes)
- Swap Fee Denominator (8 bytes)
- Base Need Take Pnl (8 bytes)
- Quote Need Take Pnl (8 bytes)
- Quote Total Pnl (8 bytes)
- Base Total Pnl (8 bytes)
- Pool Open Time (8 bytes)
- Punish Pc Amount (8 bytes)
- Punish Coin Amount (8 bytes)
- Orderbook To Init Time (8 bytes)
- Swap Base In Amount (16 bytes - u128)
- Swap Quote Out Amount (16 bytes - u128)
- Swap Base Fee Amount (8 bytes)
- Swap Quote In Amount (16 bytes - u128)
- Swap Base Out Amount (16 bytes - u128)
- Swap Quote Fee Amount (8 bytes)
- Base Vault (32 bytes - Pubkey)
- Quote Vault (32 bytes - Pubkey)
... more fields
```

**Key Fields Needed:**
- **Base Vault:** Token account holding base tokens (SOL)
- **Quote Vault:** Token account holding quote tokens (MEMESAI)

#### Step 2: Research Exact Offsets

**Option A: Use Raydium SDK (Recommended)**

Install Raydium SDK dependencies:
```bash
npm install @raydium-io/raydium-sdk
```

Create Node.js bridge script `get_pool_info.js`:
```javascript
const { Connection, PublicKey } = require('@solana/web3.js');
const { Liquidity } = require('@raydium-io/raydium-sdk');

async function getPoolInfo(poolId) {
    const connection = new Connection('https://api.mainnet-beta.solana.com');
    const poolKeys = await Liquidity.fetchAllPoolKeys(connection);
    
    // Find your pool
    const targetPool = poolKeys.find(p => p.id.toBase58() === poolId);
    
    if (!targetPool) {
        console.log('Pool not found');
        return;
    }
    
    // Get pool info
    const poolInfo = await Liquidity.fetchInfo({
        connection,
        poolKeys: targetPool,
    });
    
    console.log('Base Reserve:', poolInfo.baseReserve.toString());
    console.log('Quote Reserve:', poolInfo.quoteReserve.toString());
    console.log('Price:', poolInfo.quoteReserve / poolInfo.baseReserve);
}

getPoolInfo(process.argv[2]);
```

**Option B: Parse Raw Account Data (Advanced)**

You'll need to find the exact byte offsets by:
1. Fetching a known pool account
2. Comparing with Raydium SDK source code
3. Identifying vault addresses in the data
4. Fetching vault balances

#### Step 3: Implementation Option A (Using Raydium SDK via subprocess)

```python
def get_price(self) -> float:
    """
    Get approximate current price (quote per base).
    Uses Raydium SDK via Node.js bridge.
    """
    try:
        import subprocess
        import json
        
        # Call Node.js script to get pool info
        result = subprocess.run(
            ['node', 'get_pool_info.js', str(self.pool_id)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            raise Exception(f"Node.js script failed: {result.stderr}")
        
        # Parse output
        output = result.stdout
        # Extract price from output (adjust based on your script)
        # This is a simplified example
        price = float(output.strip().split(':')[-1])
        
        logger.debug(f"Current price: {price:.6f} {self.quote_symbol}/{self.base_symbol}")
        return price
        
    except Exception as e:
        logger.error(f"Failed to get price: {e}")
        raise
```

#### Step 4: Implementation Option B (Direct RPC - More Complex)

```python
def get_price(self) -> float:
    """
    Get approximate current price (quote per base).
    Fetches pool vaults and calculates from reserves.
    """
    try:
        # Step 1: Get pool account data
        pool_account_response = self._rpc_call_with_retry(
            self.client.get_account_info,
            self.pool_id
        )
        
        if not pool_account_response.value:
            raise Exception(f"Pool account not found: {self.pool_id}")
        
        pool_data = pool_account_response.value.data
        
        # Step 2: Parse vault addresses from pool data
        # These offsets are approximate - verify with Raydium source
        BASE_VAULT_OFFSET = 338  # Approximate - needs verification
        QUOTE_VAULT_OFFSET = 370  # Approximate - needs verification
        
        base_vault_bytes = pool_data[BASE_VAULT_OFFSET:BASE_VAULT_OFFSET + 32]
        quote_vault_bytes = pool_data[QUOTE_VAULT_OFFSET:QUOTE_VAULT_OFFSET + 32]
        
        base_vault = Pubkey(base_vault_bytes)
        quote_vault = Pubkey(quote_vault_bytes)
        
        logger.debug(f"Base vault: {base_vault}")
        logger.debug(f"Quote vault: {quote_vault}")
        
        # Step 3: Get vault balances
        base_balance_response = self._rpc_call_with_retry(
            self.client.get_token_account_balance,
            base_vault
        )
        quote_balance_response = self._rpc_call_with_retry(
            self.client.get_token_account_balance,
            quote_vault
        )
        
        if not base_balance_response.value or not quote_balance_response.value:
            raise Exception("Failed to fetch vault balances")
        
        base_reserve = float(base_balance_response.value.ui_amount)
        quote_reserve = float(quote_balance_response.value.ui_amount)
        
        logger.debug(f"Base reserve: {base_reserve}")
        logger.debug(f"Quote reserve: {quote_reserve}")
        
        # Step 4: Calculate price
        if base_reserve == 0:
            raise Exception("Base reserve is zero")
        
        price = quote_reserve / base_reserve
        
        logger.info(f"Current price: {price:.6f} {self.quote_symbol}/{self.base_symbol}")
        return price
        
    except Exception as e:
        logger.error(f"Failed to get price: {e}")
        raise
```

#### Step 5: Test get_price()

Create `test_get_price.py`:
```python
from bot.raydium_client import RaydiumClient
from bot.config import config

try:
    client = RaydiumClient()
    price = client.get_price()
    print(f"✅ Price fetched: {price}")
    
    # Verify price is reasonable
    if price <= 0:
        print("❌ Price is zero or negative!")
    elif price > 1000000:
        print("⚠️ Price seems unusually high, verify calculation")
    else:
        print("✅ Price looks reasonable")
        
except Exception as e:
    print(f"❌ Failed to get price: {e}")
    import traceback
    traceback.print_exc()
```

Run test:
```bash
python test_get_price.py
```

#### Step 6: Verification Checklist
- [ ] Pool account data fetches successfully
- [ ] Vault addresses extracted correctly
- [ ] Vault balances fetch successfully
- [ ] Price calculation returns positive float
- [ ] Price matches expected range (compare with Raydium UI)
- [ ] Test script runs without errors
- [ ] Logged price matches actual market price

---

## Method 3: `swap_exact_sol_for_tokens()` ⭐⭐⭐

**Location:** `bot/raydium_client.py`, lines 176-211  
**Difficulty:** Hard  
**Dependencies:** Raydium program knowledge, transaction building  
**Estimated Time:** 4-8 hours

### What It Does
Builds and executes a swap transaction to trade SOL for MEMESAI tokens on Raydium.

### Current Status
```python
def swap_exact_sol_for_tokens(
    self,
    notional_sol: float,
    slippage_bps: int
) -> Dict[str, any]:
    """BUY: Swap exact SOL for SPL tokens (MEMESAI)."""
    raise NotImplementedError(
        "Raydium swap functionality needs to be implemented."
    )
```

### Implementation Checklist

#### Step 1: Understand Raydium Swap Instruction Structure

Raydium swap requires these accounts:
1. Token Program
2. AMM ID (pool)
3. AMM Authority
4. AMM Open Orders
5. AMM Target Orders
6. Pool Coin Token Account (base vault)
7. Pool PC Token Account (quote vault)
8. Serum Program ID
9. Serum Market
10. Serum Bids
11. Serum Asks
12. Serum Event Queue
13. Serum Coin Vault Account
14. Serum PC Vault Account
15. Serum Vault Signer
16. User Source Token Account (user's SOL account)
17. User Destination Token Account (user's MEMESAI account)
18. User Owner (wallet)

**Instruction Data:**
- Instruction discriminator (1 byte): 9 for swap
- Amount in (8 bytes): u64
- Minimum amount out (8 bytes): u64

#### Step 2: Get Pool Keys

You'll need to fetch or store all the pool keys. Options:

**Option A: Use Raydium SDK**
```javascript
// In get_pool_keys.js
const { Liquidity } = require('@raydium-io/raydium-sdk');

async function getPoolKeys(poolId) {
    const poolKeys = await Liquidity.fetchAllPoolKeys(connection);
    const target = poolKeys.find(p => p.id.toBase58() === poolId);
    console.log(JSON.stringify(target, null, 2));
}
```

**Option B: Store in config**
Add to `.env`:
```env
# Raydium Pool Keys (get from SDK or pool info)
RAYDIUM_AMM_AUTHORITY=<authority_pubkey>
RAYDIUM_AMM_OPEN_ORDERS=<open_orders_pubkey>
RAYDIUM_AMM_TARGET_ORDERS=<target_orders_pubkey>
RAYDIUM_BASE_VAULT=<base_vault_pubkey>
RAYDIUM_QUOTE_VAULT=<quote_vault_pubkey>
RAYDIUM_SERUM_PROGRAM_ID=<serum_program_pubkey>
RAYDIUM_SERUM_MARKET=<serum_market_pubkey>
# ... etc
```

#### Step 3: Implementation (Detailed)

```python
def swap_exact_sol_for_tokens(
    self,
    notional_sol: float,
    slippage_bps: int
) -> Dict[str, any]:
    """
    BUY: Swap exact SOL for SPL tokens (MEMESAI).
    
    Args:
        notional_sol: Amount of SOL to spend (in SOL, not lamports)
        slippage_bps: Slippage tolerance in basis points (e.g., 50 = 0.5%)
    
    Returns:
        dict with 'amount_in', 'amount_out', 'tx_hash', 'slot'
    """
    logger.info(f"BUY: Swapping {notional_sol} {self.base_symbol} for {self.quote_symbol}")
    
    try:
        # Step 1: Convert SOL to lamports
        amount_in_lamports = int(notional_sol * LAMPORTS_PER_SOL)
        
        # Step 2: Get current price and calculate expected output
        current_price = self.get_price()
        expected_out_raw = notional_sol * current_price
        expected_out_tokens = expected_out_raw * (10 ** self.quote_decimals)
        
        # Step 3: Calculate minimum output with slippage
        slippage_multiplier = (10000 - slippage_bps) / 10000
        min_amount_out = int(expected_out_tokens * slippage_multiplier)
        
        logger.info(
            f"Expected output: {expected_out_raw:.6f} {self.quote_symbol}, "
            f"Minimum: {min_amount_out / (10 ** self.quote_decimals):.6f}"
        )
        
        # Step 4: Get or create user's token accounts
        user_sol_account = self._get_associated_token_address(
            self.keypair.pubkey(),
            self.base_token_mint
        )
        
        user_token_account = self._get_associated_token_address(
            self.keypair.pubkey(),
            self.quote_token_mint
        )
        
        # Check if token account exists, create if not
        token_account_info = self.client.get_account_info(user_token_account)
        if not token_account_info.value:
            logger.info(f"Creating token account for {self.quote_symbol}")
            # TODO: Add instruction to create associated token account
            # Use spl.token.instructions.create_associated_token_account
            pass
        
        # Step 5: Build Raydium swap instruction
        # This is the most complex part - you need correct account order and data
        
        from solders.instruction import Instruction, AccountMeta
        from solders.system_program import ID as SYSTEM_PROGRAM_ID
        
        # Build instruction data
        # Format: [instruction_id: u8, amount_in: u64, min_amount_out: u64]
        instruction_data = bytes([9])  # 9 = swap instruction
        instruction_data += amount_in_lamports.to_bytes(8, 'little')
        instruction_data += min_amount_out.to_bytes(8, 'little')
        
        # Build accounts list (ORDER IS CRITICAL)
        accounts = [
            AccountMeta(TOKEN_PROGRAM_ID, False, False),
            AccountMeta(self.pool_id, False, True),  # AMM ID - writable
            AccountMeta(self.amm_authority, False, False),  # AMM authority
            AccountMeta(self.amm_open_orders, False, True),  # Open orders - writable
            AccountMeta(self.amm_target_orders, False, True),  # Target orders - writable
            AccountMeta(self.base_vault, False, True),  # Pool coin vault - writable
            AccountMeta(self.quote_vault, False, True),  # Pool pc vault - writable
            AccountMeta(self.serum_program_id, False, False),  # Serum program
            AccountMeta(self.serum_market, False, True),  # Serum market - writable
            AccountMeta(self.serum_bids, False, True),  # Serum bids - writable
            AccountMeta(self.serum_asks, False, True),  # Serum asks - writable
            AccountMeta(self.serum_event_queue, False, True),  # Event queue - writable
            AccountMeta(self.serum_coin_vault, False, True),  # Serum coin vault - writable
            AccountMeta(self.serum_pc_vault, False, True),  # Serum pc vault - writable
            AccountMeta(self.serum_vault_signer, False, False),  # Vault signer
            AccountMeta(user_sol_account, False, True),  # User source - writable
            AccountMeta(user_token_account, False, True),  # User dest - writable
            AccountMeta(self.keypair.pubkey(), True, False),  # User owner - signer
        ]
        
        swap_instruction = Instruction(
            program_id=self.raydium_program_id,
            accounts=accounts,
            data=instruction_data
        )
        
        # Step 6: Build transaction
        from solana.transaction import Transaction
        
        recent_blockhash = self.client.get_latest_blockhash().value.blockhash
        
        transaction = Transaction()
        transaction.recent_blockhash = recent_blockhash
        transaction.fee_payer = self.keypair.pubkey()
        transaction.add(swap_instruction)
        
        # Step 7: Sign transaction
        transaction.sign(self.keypair)
        
        # Step 8: Send transaction
        result = self._send_transaction(transaction)
        
        # Step 9: Parse result
        # After confirmation, fetch new balances to get actual amounts
        new_balances = self.get_balances()
        
        # Calculate actual amounts (simplified - ideally parse from transaction logs)
        actual_amount_in = notional_sol
        actual_amount_out = expected_out_raw  # Should parse from logs
        
        return {
            'amount_in': actual_amount_in,
            'amount_out': actual_amount_out,
            'tx_hash': result,
            'slot': None  # Could fetch from transaction status
        }
        
    except Exception as e:
        logger.error(f"Swap failed: {e}")
        raise
```

#### Step 4: Add Required Pool Keys to Config

Update `bot/config.py`:
```python
# In __init__ method, add:
self.AMM_AUTHORITY = self._require_env("RAYDIUM_AMM_AUTHORITY")
self.AMM_OPEN_ORDERS = self._require_env("RAYDIUM_AMM_OPEN_ORDERS")
self.AMM_TARGET_ORDERS = self._require_env("RAYDIUM_AMM_TARGET_ORDERS")
self.BASE_VAULT = self._require_env("RAYDIUM_BASE_VAULT")
self.QUOTE_VAULT = self._require_env("RAYDIUM_QUOTE_VAULT")
self.SERUM_PROGRAM_ID = self._require_env("RAYDIUM_SERUM_PROGRAM_ID")
self.SERUM_MARKET = self._require_env("RAYDIUM_SERUM_MARKET")
self.SERUM_BIDS = self._require_env("RAYDIUM_SERUM_BIDS")
self.SERUM_ASKS = self._require_env("RAYDIUM_SERUM_ASKS")
self.SERUM_EVENT_QUEUE = self._require_env("RAYDIUM_SERUM_EVENT_QUEUE")
self.SERUM_COIN_VAULT = self._require_env("RAYDIUM_SERUM_COIN_VAULT")
self.SERUM_PC_VAULT = self._require_env("RAYDIUM_SERUM_PC_VAULT")
self.SERUM_VAULT_SIGNER = self._require_env("RAYDIUM_SERUM_VAULT_SIGNER")
```

Update `raydium_client.py` __init__ to load these:
```python
# In __init__, add:
self.amm_authority = Pubkey.from_string(config.AMM_AUTHORITY)
self.amm_open_orders = Pubkey.from_string(config.AMM_OPEN_ORDERS)
# ... etc for all keys
```

#### Step 5: Test Single Swap

Create `test_buy_swap.py`:
```python
from bot.raydium_client import RaydiumClient
from bot.config import config

try:
    client = RaydiumClient()
    
    # Check initial balance
    initial_balances = client.get_balances()
    print(f"Initial SOL: {initial_balances['base']}")
    print(f"Initial MEMESAI: {initial_balances['quote']}")
    
    # Execute tiny swap
    print("\nExecuting swap: 0.001 SOL -> MEMESAI")
    result = client.swap_exact_sol_for_tokens(0.001, 500)  # 5% slippage for testing
    
    print(f"\n✅ Swap successful!")
    print(f"TX: {result['tx_hash']}")
    print(f"Amount in: {result['amount_in']}")
    print(f"Amount out: {result['amount_out']}")
    
    # Check new balance
    new_balances = client.get_balances()
    print(f"\nNew SOL: {new_balances['base']}")
    print(f"New MEMESAI: {new_balances['quote']}")
    
    # Verify on Solscan
    print(f"\nVerify on Solscan:")
    print(f"https://solscan.io/tx/{result['tx_hash']}")
    
except Exception as e:
    print(f"❌ Swap failed: {e}")
    import traceback
    traceback.print_exc()
```

Run test:
```bash
# Make sure you have at least 0.01 SOL for testing + gas
python test_buy_swap.py
```

#### Step 6: Verification Checklist
- [ ] All pool keys configured in .env
- [ ] Pool keys load correctly in client
- [ ] Token account creation works (if needed)
- [ ] Instruction data builds correctly
- [ ] Accounts list in correct order
- [ ] Transaction signs successfully
- [ ] Transaction sends to network
- [ ] Transaction confirms on-chain
- [ ] SOL balance decreases
- [ ] MEMESAI balance increases
- [ ] Transaction visible on Solscan
- [ ] Amounts match expectations (within slippage)

---

## Method 4: `swap_exact_tokens_for_sol()` ⭐⭐⭐

**Location:** `bot/raydium_client.py`, lines 213-246  
**Difficulty:** Hard  
**Dependencies:** Same as Method 3  
**Estimated Time:** 2-4 hours (faster if Method 3 works)

### What It Does
Builds and executes a swap transaction to trade MEMESAI tokens back to SOL on Raydium.

### Current Status
```python
def swap_exact_tokens_for_sol(
    self,
    notional_sol_equiv: float,
    slippage_bps: int
) -> Dict[str, any]:
    """SELL: Swap SPL tokens (MEMESAI) for SOL."""
    raise NotImplementedError(
        "Raydium swap functionality needs to be implemented."
    )
```

### Implementation Checklist

#### Step 1: Understand Differences from Buy Swap

The SELL swap is very similar to BUY, with these differences:
- **Source account:** User's MEMESAI account (not SOL)
- **Destination account:** User's SOL account (not MEMESAI)
- **Amount in:** MEMESAI tokens (not SOL)
- **Calculation:** Need to convert SOL equivalent to MEMESAI amount

Account order **reverses** in some positions.

#### Step 2: Implementation

```python
def swap_exact_tokens_for_sol(
    self,
    notional_sol_equiv: float,
    slippage_bps: int
) -> Dict[str, any]:
    """
    SELL: Swap SPL tokens (MEMESAI) for SOL.
    
    Args:
        notional_sol_equiv: Approximate SOL value to sell (in SOL)
        slippage_bps: Slippage tolerance in basis points
    
    Returns:
        dict with 'amount_in', 'amount_out', 'tx_hash', 'slot'
    """
    logger.info(f"SELL: Swapping ~{notional_sol_equiv} {self.base_symbol} worth of {self.quote_symbol}")
    
    try:
        # Step 1: Get current price and calculate token amount needed
        current_price = self.get_price()
        token_amount_raw = notional_sol_equiv * current_price
        amount_in_tokens = int(token_amount_raw * (10 ** self.quote_decimals))
        
        logger.info(f"Selling {token_amount_raw:.6f} {self.quote_symbol}")
        
        # Step 2: Calculate expected SOL output
        expected_sol_out = notional_sol_equiv
        expected_sol_lamports = int(expected_sol_out * LAMPORTS_PER_SOL)
        
        # Step 3: Calculate minimum output with slippage
        slippage_multiplier = (10000 - slippage_bps) / 10000
        min_amount_out = int(expected_sol_lamports * slippage_multiplier)
        
        logger.info(
            f"Expected output: {expected_sol_out:.6f} {self.base_symbol}, "
            f"Minimum: {min_amount_out / LAMPORTS_PER_SOL:.6f}"
        )
        
        # Step 4: Get user's token accounts
        user_token_account = self._get_associated_token_address(
            self.keypair.pubkey(),
            self.quote_token_mint
        )
        
        user_sol_account = self._get_associated_token_address(
            self.keypair.pubkey(),
            self.base_token_mint
        )
        
        # Step 5: Build Raydium swap instruction
        from solders.instruction import Instruction, AccountMeta
        
        # Build instruction data (same format as buy)
        instruction_data = bytes([9])  # 9 = swap instruction
        instruction_data += amount_in_tokens.to_bytes(8, 'little')
        instruction_data += min_amount_out.to_bytes(8, 'little')
        
        # Build accounts list
        # IMPORTANT: Source and destination are SWAPPED compared to buy
        accounts = [
            AccountMeta(TOKEN_PROGRAM_ID, False, False),
            AccountMeta(self.pool_id, False, True),
            AccountMeta(self.amm_authority, False, False),
            AccountMeta(self.amm_open_orders, False, True),
            AccountMeta(self.amm_target_orders, False, True),
            AccountMeta(self.quote_vault, False, True),  # NOTE: SWAPPED - quote first for sell
            AccountMeta(self.base_vault, False, True),   # NOTE: SWAPPED - base second for sell
            AccountMeta(self.serum_program_id, False, False),
            AccountMeta(self.serum_market, False, True),
            AccountMeta(self.serum_bids, False, True),
            AccountMeta(self.serum_asks, False, True),
            AccountMeta(self.serum_event_queue, False, True),
            AccountMeta(self.serum_coin_vault, False, True),
            AccountMeta(self.serum_pc_vault, False, True),
            AccountMeta(self.serum_vault_signer, False, False),
            AccountMeta(user_token_account, False, True),  # NOTE: Source is MEMESAI
            AccountMeta(user_sol_account, False, True),    # NOTE: Dest is SOL
            AccountMeta(self.keypair.pubkey(), True, False),
        ]
        
        swap_instruction = Instruction(
            program_id=self.raydium_program_id,
            accounts=accounts,
            data=instruction_data
        )
        
        # Step 6: Build transaction
        from solana.transaction import Transaction
        
        recent_blockhash = self.client.get_latest_blockhash().value.blockhash
        
        transaction = Transaction()
        transaction.recent_blockhash = recent_blockhash
        transaction.fee_payer = self.keypair.pubkey()
        transaction.add(swap_instruction)
        
        # Step 7: Sign and send
        transaction.sign(self.keypair)
        result = self._send_transaction(transaction)
        
        # Step 8: Parse result
        actual_amount_in = token_amount_raw
        actual_amount_out = expected_sol_out  # Should parse from logs
        
        return {
            'amount_in': actual_amount_in,
            'amount_out': actual_amount_out,
            'tx_hash': result,
            'slot': None
        }
        
    except Exception as e:
        logger.error(f"Sell swap failed: {e}")
        raise
```

#### Step 3: Test Single Sell Swap

Create `test_sell_swap.py`:
```python
from bot.raydium_client import RaydiumClient

try:
    client = RaydiumClient()
    
    # Check initial balances
    initial_balances = client.get_balances()
    print(f"Initial SOL: {initial_balances['base']}")
    print(f"Initial MEMESAI: {initial_balances['quote']}")
    
    if initial_balances['quote'] < 0.001:
        print("❌ Insufficient MEMESAI balance for test")
        print("   Run test_buy_swap.py first to get some MEMESAI")
        exit(1)
    
    # Execute tiny sell
    print("\nExecuting sell: 0.001 SOL worth of MEMESAI -> SOL")
    result = client.swap_exact_tokens_for_sol(0.001, 500)
    
    print(f"\n✅ Sell swap successful!")
    print(f"TX: {result['tx_hash']}")
    print(f"Amount in: {result['amount_in']} MEMESAI")
    print(f"Amount out: {result['amount_out']} SOL")
    
    # Check new balances
    new_balances = client.get_balances()
    print(f"\nNew SOL: {new_balances['base']}")
    print(f"New MEMESAI: {new_balances['quote']}")
    
    print(f"\nVerify on Solscan:")
    print(f"https://solscan.io/tx/{result['tx_hash']}")
    
except Exception as e:
    print(f"❌ Sell swap failed: {e}")
    import traceback
    traceback.print_exc()
```

Run test:
```bash
python test_sell_swap.py
```

#### Step 4: Verification Checklist
- [ ] Method calculates MEMESAI amount correctly
- [ ] Account order is correct (reversed from buy)
- [ ] Transaction builds successfully
- [ ] Transaction confirms on-chain
- [ ] MEMESAI balance decreases
- [ ] SOL balance increases
- [ ] Transaction visible on Solscan
- [ ] Can execute multiple sells in sequence

---

## 🔄 Full Integration Test

After implementing all 4 methods, test the complete bot:

### Test Script: `test_full_bot.py`

```python
"""
Full integration test - simulates bot behavior.
Tests BUY-BUY-SELL-SELL pattern with tiny amounts.
"""

from bot.raydium_client import RaydiumClient
from bot.config import config
import time

def test_full_pattern():
    client = RaydiumClient()
    
    print("=" * 60)
    print("FULL BOT INTEGRATION TEST")
    print("=" * 60)
    print()
    
    # Initial state
    initial = client.get_balances()
    print(f"Initial Balances:")
    print(f"  SOL: {initial['base']:.4f}")
    print(f"  MEMESAI: {initial['quote']:.6f}")
    print()
    
    # Test amount (very small)
    test_amount = 0.01  # 0.01 SOL per trade
    
    try:
        # BUY 1
        print("Trade 1/4: BUY")
        result1 = client.swap_exact_sol_for_tokens(test_amount, 500)
        print(f"  ✅ TX: {result1['tx_hash'][:20]}...")
        time.sleep(2)
        
        # BUY 2
        print("\nTrade 2/4: BUY")
        result2 = client.swap_exact_sol_for_tokens(test_amount, 500)
        print(f"  ✅ TX: {result2['tx_hash'][:20]}...")
        time.sleep(2)
        
        # Check balances after buys
        after_buys = client.get_balances()
        print(f"\nAfter BUYs:")
        print(f"  SOL: {after_buys['base']:.4f} (spent ~{test_amount * 2:.4f})")
        print(f"  MEMESAI: {after_buys['quote']:.6f}")
        
        # SELL 1
        print("\nTrade 3/4: SELL")
        result3 = client.swap_exact_tokens_for_sol(test_amount, 500)
        print(f"  ✅ TX: {result3['tx_hash'][:20]}...")
        time.sleep(2)
        
        # SELL 2
        print("\nTrade 4/4: SELL")
        result4 = client.swap_exact_tokens_for_sol(test_amount, 500)
        print(f"  ✅ TX: {result4['tx_hash'][:20]}...")
        time.sleep(2)
        
        # Final state
        final = client.get_balances()
        print(f"\nFinal Balances:")
        print(f"  SOL: {final['base']:.4f}")
        print(f"  MEMESAI: {final['quote']:.6f}")
        
        # Calculate P/L
        sol_change = final['base'] - initial['base']
        memesai_change = final['quote'] - initial['quote']
        
        print(f"\nP/L:")
        print(f"  SOL change: {sol_change:+.4f}")
        print(f"  MEMESAI change: {memesai_change:+.6f}")
        
        # Expected: small loss due to fees, close to neutral
        if abs(sol_change) < test_amount * 0.1:  # Within 10% of one trade
            print(f"\n✅ TEST PASSED: P/L within expected range")
        else:
            print(f"\n⚠️  WARNING: P/L outside expected range")
        
        print(f"\n{'=' * 60}")
        print("ALL TRADES COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_pattern()
    exit(0 if success else 1)
```

### Run Full Test

```bash
# Make sure you have at least 0.1 SOL for testing
python test_full_bot.py
```

### Expected Output
```
============================================================
FULL BOT INTEGRATION TEST
============================================================

Initial Balances:
  SOL: 1.0000
  MEMESAI: 0.000000

Trade 1/4: BUY
  ✅ TX: 3kqR7...

Trade 2/4: BUY
  ✅ TX: 5mN8P...

After BUYs:
  SOL: 0.9800 (spent ~0.0200)
  MEMESAI: 2.450000

Trade 3/4: SELL
  ✅ TX: 7pQ2M...

Trade 4/4: SELL
  ✅ TX: 9rT5K...

Final Balances:
  SOL: 0.9975
  MEMESAI: 0.000100

P/L:
  SOL change: -0.0025
  MEMESAI change: +0.000100

✅ TEST PASSED: P/L within expected range

============================================================
ALL TRADES COMPLETED SUCCESSFULLY
============================================================
```

---

## 📋 Final Verification Checklist

Before deploying to production:

### Code Quality
- [ ] All 4 methods implemented
- [ ] Error handling in place
- [ ] Logging statements added
- [ ] Type hints correct
- [ ] Comments explain complex logic
- [ ] No hardcoded values

### Functionality
- [ ] get_price() returns accurate prices
- [ ] BUY swap executes successfully
- [ ] SELL swap executes successfully
- [ ] ATA derivation works
- [ ] Token account creation works (if needed)
- [ ] Transaction confirmation works

### Testing
- [ ] Unit tests for each method pass
- [ ] Integration test passes
- [ ] Can execute 10+ consecutive trades
- [ ] No memory leaks over extended run
- [ ] Handles network errors gracefully
- [ ] Handles insufficient balance errors

### Configuration
- [ ] All pool keys in .env
- [ ] RPC URL correct for network
- [ ] Wallet has sufficient balance
- [ ] Slippage tolerance appropriate
- [ ] Gas settings appropriate

### Security
- [ ] Private key never logged
- [ ] Input validation on all parameters
- [ ] Amount limits enforced
- [ ] Rate limiting in place
- [ ] No SQL injection risks
- [ ] Wallet balance checks before trades

### Documentation
- [ ] Code comments complete
- [ ] README updated with any changes
- [ ] Test instructions documented
- [ ] Known issues documented
- [ ] Recovery procedures documented

---

## 🚨 Common Issues and Solutions

### Issue: "Instruction error: invalid account data"
**Cause:** Account list order is wrong or account is incorrect  
**Solution:** Double-check account order matches Raydium expectations

### Issue: "Transaction simulation failed"
**Cause:** Insufficient balance, wrong amounts, or bad instruction data  
**Solution:** Check balances, verify amounts are positive, check instruction format

### Issue: "Slippage tolerance exceeded"
**Cause:** Price moved too much between calculation and execution  
**Solution:** Increase slippage tolerance or reduce trade size

### Issue: "Token account does not exist"
**Cause:** User doesn't have MEMESAI token account yet  
**Solution:** Add instruction to create associated token account before swap

### Issue: "Invalid signer"
**Cause:** Transaction not signed correctly or wrong signer  
**Solution:** Verify keypair is correct and transaction.sign() is called

---

## 📞 Getting Help

If you get stuck:

1. **Check transaction on Solscan** - See exact error
2. **Compare with Raydium SDK** - Check account order and data format
3. **Enable DEBUG logging** - See detailed execution flow
4. **Test with smallest possible amounts** - Minimize risk while debugging
5. **Ask in Solana Discord** - Community can help with specific errors

---

## 🎯 Success Criteria

You're done when:

✅ All 4 methods are implemented  
✅ All unit tests pass  
✅ Integration test passes  
✅ Can run full BUY-BUY-SELL-SELL pattern  
✅ Transactions visible on Solscan  
✅ P/L within expected range (small loss due to fees)  
✅ Bot can run for 50+ consecutive trades without errors  

---

**Estimated Total Time:** 11-21 hours over 2-4 days

Good luck with the implementation! Remember to test with **tiny amounts** first and verify every transaction on Solscan before scaling up.

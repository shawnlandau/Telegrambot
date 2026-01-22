#!/usr/bin/env python3
"""
Simple Solana connection test for DEX bot
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("=" * 70)
print("🧪 SOLANA CONNECTION TEST")
print("=" * 70)
print()

# Test 1: Check imports
print("📦 Testing imports...")
try:
    from solana.rpc.api import Client
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    import base58
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

print()

# Test 2: Load configuration
print("⚙️  Loading configuration...")
try:
    RPC_URL = os.getenv("SOLANA_RPC_URL")
    PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY")
    QUOTE_TOKEN = os.getenv("QUOTE_TOKEN_ADDRESS")
    
    if not RPC_URL or not PRIVATE_KEY or not QUOTE_TOKEN:
        print("❌ Missing required environment variables")
        sys.exit(1)
    
    print(f"✅ RPC URL: {RPC_URL}")
    print(f"✅ Quote Token: {QUOTE_TOKEN}")
except Exception as e:
    print(f"❌ Configuration error: {e}")
    sys.exit(1)

print()

# Test 3: Connect to Solana
print("🌐 Connecting to Solana RPC...")
try:
    client = Client(RPC_URL)
    version = client.get_version()
    print(f"✅ Connected! Solana version: {version.value}")
except Exception as e:
    print(f"❌ RPC connection failed: {e}")
    sys.exit(1)

print()

# Test 4: Load wallet
print("🔑 Loading wallet...")
try:
    private_key_bytes = base58.b58decode(PRIVATE_KEY)
    
    if len(private_key_bytes) == 64:
        keypair = Keypair.from_bytes(private_key_bytes)
    elif len(private_key_bytes) == 32:
        keypair = Keypair.from_seed(private_key_bytes)
    else:
        raise ValueError(f"Invalid private key length: {len(private_key_bytes)}")
    
    wallet_address = str(keypair.pubkey())
    print(f"✅ Wallet loaded: {wallet_address}")
except Exception as e:
    print(f"❌ Wallet loading failed: {e}")
    sys.exit(1)

print()

# Test 5: Get SOL balance
print("💰 Checking SOL balance...")
try:
    balance_response = client.get_balance(keypair.pubkey())
    balance_lamports = balance_response.value
    balance_sol = balance_lamports / 1_000_000_000
    print(f"✅ SOL Balance: {balance_sol:.6f} SOL")
    
    if balance_sol < 0.01:
        print("⚠️  WARNING: Balance is very low! You need SOL for:")
        print("   - Trading (buying MEMESAI)")
        print("   - Transaction fees")
        print("   Recommended: At least 0.1-1 SOL")
except Exception as e:
    print(f"❌ Balance check failed: {e}")
    sys.exit(1)

print()

# Test 6: Verify token address
print("🪙 Verifying MEMESAI token...")
try:
    token_mint = Pubkey.from_string(QUOTE_TOKEN)
    print(f"✅ MEMESAI mint address valid: {token_mint}")
except Exception as e:
    print(f"❌ Token address invalid: {e}")
    sys.exit(1)

print()

# Test 7: Test Jupiter API
print("🪐 Testing Jupiter API...")
try:
    import requests
    
    quote_url = "https://quote-api.jup.ag/v6/quote"
    params = {
        "inputMint": "So11111111111111111111111111111111111111112",  # SOL
        "outputMint": str(token_mint),  # MEMESAI
        "amount": "1000000000",  # 1 SOL in lamports
        "slippageBps": "50"
    }
    
    response = requests.get(quote_url, params=params, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if "outAmount" in data:
            out_amount = int(data["outAmount"])
            print(f"✅ Jupiter API working!")
            print(f"   1 SOL = ~{out_amount / 1e9:.2f} MEMESAI (estimated)")
        else:
            print(f"⚠️  Jupiter response: {data}")
    else:
        print(f"⚠️  Jupiter API returned status {response.status_code}")
        print("   This might mean:")
        print("   - MEMESAI doesn't have enough liquidity")
        print("   - Token address might be incorrect")
        print("   - Network issues")
        
except Exception as e:
    print(f"⚠️  Jupiter API test failed: {e}")
    print("   Bot will still work, but swaps might fail")

print()
print("=" * 70)
print("🎉 CONNECTION TEST COMPLETE!")
print("=" * 70)
print()
print("✅ Your bot is ready to start!")
print()
print("📋 Next Steps:")
print("   1. Start the bot: python -m bot.main")
print("   2. Open Telegram and find your bot")
print("   3. Send: /help")
print("   4. Send: /config to set up trading")
print("   5. Send: /start to begin trading")
print()
print("⚠️  Important:")
print("   - Start with small amounts (0.1-1 SOL)")
print("   - Monitor your first few trades closely")
print("   - Check transactions on: https://solscan.io/")
print()
print("=" * 70)

#!/usr/bin/env python3
"""
Script to find Raydium pools for MEMESAI token.
Uses Solana RPC to search for pools containing the MEMESAI mint.
"""

import sys
import json
from solana.rpc.api import Client
from solders.pubkey import Pubkey

# MEMESAI token mint
MEMESAI_MINT = "8D9foi1nqfabp8D3uNJCrzt1xkvxq8xHYH8Lxb4fbonk"
SOL_MINT = "So11111111111111111111111111111111111111112"

# Raydium Program IDs
RAYDIUM_LIQUIDITY_POOL_V4 = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"

def find_raydium_pools():
    """Find Raydium pools containing MEMESAI."""
    print("=" * 70)
    print("SEARCHING FOR MEMESAI RAYDIUM POOLS")
    print("=" * 70)
    print()
    print(f"MEMESAI Mint: {MEMESAI_MINT}")
    print(f"SOL Mint: {SOL_MINT}")
    print()
    print("Connecting to Solana mainnet...")
    
    # Connect to mainnet
    client = Client("https://api.mainnet-beta.solana.com")
    
    try:
        # Get version to test connection
        version = client.get_version()
        print(f"✅ Connected to Solana (version: {version.value})")
        print()
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    print("🔍 Searching for Raydium pools...")
    print("(This uses Raydium's known program ID)")
    print()
    
    # For production use, you would typically:
    # 1. Use Raydium SDK to fetch all pools
    # 2. Or query a Raydium API endpoint
    # 3. Or use a service like Jupiter API
    
    print("⚠️  Note: Direct RPC search for pools is complex.")
    print("Recommended approaches:")
    print()
    print("1. 🌐 Check Raydium UI directly:")
    print(f"   https://raydium.io/swap/?inputMint={SOL_MINT}&outputMint={MEMESAI_MINT}")
    print()
    print("2. 🔧 Use Jupiter API (aggregator):")
    print(f"   https://quote-api.jup.ag/v6/quote?inputMint={SOL_MINT}&outputMint={MEMESAI_MINT}&amount=1000000000")
    print()
    print("3. 📊 Check Birdeye or DexScreener:")
    print(f"   https://birdeye.so/token/{MEMESAI_MINT}?chain=solana")
    print(f"   https://dexscreener.com/solana/{MEMESAI_MINT}")
    print()
    
    # Try to get token info
    print("Fetching MEMESAI token info...")
    try:
        memesai_pubkey = Pubkey.from_string(MEMESAI_MINT)
        account_info = client.get_account_info(memesai_pubkey)
        
        if account_info.value:
            print(f"✅ MEMESAI token exists on Solana mainnet")
            print(f"   Owner: {account_info.value.owner}")
            print(f"   Data length: {len(account_info.value.data)} bytes")
        else:
            print(f"⚠️  Token account not found - check if mint address is correct")
    except Exception as e:
        print(f"⚠️  Could not fetch token info: {e}")
    
    print()
    print("=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print()
    print("1. Visit one of the URLs above to find the pool")
    print("2. Look for 'Pool ID' or 'AMM ID' in the pool details")
    print("3. If using Raydium UI, check the URL or page source")
    print("4. Once you have the Pool ID, I'll implement the methods!")
    print()

if __name__ == "__main__":
    find_raydium_pools()

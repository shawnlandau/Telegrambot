#!/usr/bin/env python3
"""
Test script to verify Solana connectivity and wallet loading.
Run this BEFORE attempting to start the bot.
"""

import sys
import os

# Add bot directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bot'))

def test_imports():
    """Test that all required packages are installed."""
    print("=" * 60)
    print("STEP 1: Testing Package Imports")
    print("=" * 60)
    
    try:
        import solana
        print(f"✅ solana-py installed: {solana.__version__}")
    except ImportError as e:
        print(f"❌ Failed to import solana: {e}")
        return False
    
    try:
        import solders
        print(f"✅ solders installed")
    except ImportError as e:
        print(f"❌ Failed to import solders: {e}")
        return False
    
    try:
        import base58
        print(f"✅ base58 installed")
    except ImportError as e:
        print(f"❌ Failed to import base58: {e}")
        return False
    
    try:
        from telegram import Update
        print(f"✅ python-telegram-bot installed")
    except ImportError as e:
        print(f"❌ Failed to import telegram: {e}")
        return False
    
    print("\n✅ All required packages installed!\n")
    return True


def test_config():
    """Test configuration loading."""
    print("=" * 60)
    print("STEP 2: Testing Configuration")
    print("=" * 60)
    
    try:
        from bot.config import config
        print(f"✅ Config loaded successfully")
        print(f"   RPC URL: {config.SOLANA_RPC_URL}")
        print(f"   Commitment: {config.COMMITMENT_LEVEL}")
        print(f"   Database: {config.DATABASE_PATH}")
        print(f"   Log Level: {config.LOG_LEVEL}")
        return True
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return False


def test_solana_connection():
    """Test Solana RPC connection."""
    print("\n" + "=" * 60)
    print("STEP 3: Testing Solana RPC Connection")
    print("=" * 60)
    
    try:
        from solana.rpc.api import Client
        from bot.config import config
        
        client = Client(config.SOLANA_RPC_URL)
        
        # Test 1: Get version
        version_response = client.get_version()
        if version_response.value:
            print(f"✅ RPC Connection successful!")
            print(f"   Solana Version: {version_response.value}")
        else:
            print(f"❌ RPC Connection failed: No version returned")
            return False
        
        # Test 2: Get latest blockhash
        blockhash_response = client.get_latest_blockhash()
        if blockhash_response.value:
            print(f"✅ Can fetch blockhash")
            print(f"   Latest Blockhash: {str(blockhash_response.value.blockhash)[:20]}...")
        
        # Test 3: Get slot
        slot_response = client.get_slot()
        if slot_response.value:
            print(f"✅ Can fetch slot")
            print(f"   Current Slot: {slot_response.value}")
        
        print("\n✅ Solana RPC is working properly!\n")
        return True
        
    except Exception as e:
        print(f"❌ RPC Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wallet_loading():
    """Test wallet/keypair loading."""
    print("=" * 60)
    print("STEP 4: Testing Wallet Loading")
    print("=" * 60)
    
    try:
        from bot.config import config
        from solders.keypair import Keypair
        import base58
        
        # Try to load keypair
        try:
            private_key_bytes = base58.b58decode(config.WALLET_PRIVATE_KEY)
            
            if len(private_key_bytes) == 64:
                keypair = Keypair.from_bytes(private_key_bytes)
            elif len(private_key_bytes) == 32:
                keypair = Keypair.from_seed(private_key_bytes)
            else:
                print(f"❌ Invalid private key length: {len(private_key_bytes)} bytes")
                return False
            
            wallet_address = str(keypair.pubkey())
            print(f"✅ Wallet loaded successfully!")
            print(f"   Address: {wallet_address}")
            
            # Try to get balance
            from solana.rpc.api import Client
            client = Client(config.SOLANA_RPC_URL)
            balance_response = client.get_balance(keypair.pubkey())
            
            if balance_response.value is not None:
                balance_sol = balance_response.value / 1_000_000_000
                print(f"✅ Wallet balance fetched")
                print(f"   Balance: {balance_sol:.4f} SOL")
                
                if balance_sol < 0.01:
                    print(f"⚠️  WARNING: Low balance! You need at least 0.1 SOL for testing")
                    print(f"   Get devnet SOL: solana airdrop 2 {wallet_address}")
            
            print("\n✅ Wallet is ready!\n")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load wallet: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Wallet test failed: {e}")
        return False


def test_raydium_client_init():
    """Test RaydiumClient initialization (without actual trading)."""
    print("=" * 60)
    print("STEP 5: Testing RaydiumClient Initialization")
    print("=" * 60)
    
    try:
        # This will fail if QUOTE_TOKEN or POOL_ID are invalid
        # But that's okay - we just want to test basic init
        from bot.raydium_client import RaydiumClient
        
        print("⚠️  Note: This may fail if token addresses are placeholders")
        print("   That's expected - we're just testing the framework\n")
        
        try:
            client = RaydiumClient()
            print(f"✅ RaydiumClient initialized!")
            print(f"   Wallet: {client.wallet_address}")
            print(f"   Base Symbol: {client.base_symbol}")
            print(f"   Quote Symbol: {client.quote_symbol}")
            return True
        except NotImplementedError as e:
            print(f"⚠️  RaydiumClient initialized but has unimplemented methods (expected)")
            print(f"   Error: {e}")
            return True
        except Exception as e:
            print(f"❌ RaydiumClient initialization failed: {e}")
            print(f"   This is expected if you're using placeholder token addresses")
            return False
            
    except Exception as e:
        print(f"❌ Failed to import RaydiumClient: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "🧪" * 30)
    print("SOLANA DEX BOT - CONNECTION TEST SUITE")
    print("🧪" * 30 + "\n")
    
    results = []
    
    # Run all tests
    results.append(("Package Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Solana RPC Connection", test_solana_connection()))
    results.append(("Wallet Loading", test_wallet_loading()))
    results.append(("RaydiumClient Init", test_raydium_client_init()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "-" * 60)
    print(f"Passed: {passed}/{len(results)}")
    print(f"Failed: {failed}/{len(results)}")
    print("-" * 60)
    
    if failed == 0:
        print("\n🎉 All tests passed! Ready for next phase.")
        print("\nNext steps:")
        print("1. Implement Raydium swap instructions")
        print("2. Find or create a devnet Raydium pool")
        print("3. Test actual trading on devnet")
    else:
        print("\n⚠️  Some tests failed. Please fix issues before proceeding.")
        print("\nCommon fixes:")
        print("- Check .env file configuration")
        print("- Verify private key format (base58)")
        print("- Ensure devnet SOL balance > 0.1")
        print("- Check RPC URL is correct")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

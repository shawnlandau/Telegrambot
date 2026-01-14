#!/usr/bin/env python3
"""
Quick validator for .env file configuration.
Run this after filling in your .env file to check everything is set up correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("=" * 70)
print("🔍 VALIDATING YOUR .ENV CONFIGURATION")
print("=" * 70)
print()

errors = []
warnings = []
success = []

# Check required variables
required_vars = {
    "SOLANA_RPC_URL": "Solana RPC endpoint",
    "WALLET_PRIVATE_KEY": "Solana wallet private key",
    "QUOTE_TOKEN_ADDRESS": "MEMESAI token address",
    "TELEGRAM_BOT_TOKEN": "Telegram bot token",
    "ALLOWED_TELEGRAM_IDS": "Telegram user ID(s)"
}

print("📋 Checking Required Variables:")
print("-" * 70)

for var, description in required_vars.items():
    value = os.getenv(var, "")
    
    # Check if set
    if not value or value.startswith("YOUR_") or value == "":
        errors.append(f"❌ {var} is not set! ({description})")
        print(f"❌ {var}: NOT SET")
    else:
        # Basic validation
        if var == "WALLET_PRIVATE_KEY":
            if len(value) < 32:
                errors.append(f"❌ {var} looks too short (should be base58 encoded)")
                print(f"❌ {var}: TOO SHORT (length: {len(value)})")
            else:
                success.append(f"✅ {var} is set (length: {len(value)})")
                print(f"✅ {var}: SET (length: {len(value)} chars)")
        
        elif var == "TELEGRAM_BOT_TOKEN":
            if ":" not in value:
                errors.append(f"❌ {var} format invalid (should contain ':')")
                print(f"❌ {var}: INVALID FORMAT")
            else:
                success.append(f"✅ {var} is set")
                print(f"✅ {var}: SET ({value[:10]}...)")
        
        elif var == "ALLOWED_TELEGRAM_IDS":
            if not value.isdigit() and not all(id.strip().isdigit() for id in value.split(",")):
                errors.append(f"❌ {var} should be numeric ID(s)")
                print(f"❌ {var}: INVALID FORMAT (should be numbers)")
            else:
                success.append(f"✅ {var} is set")
                print(f"✅ {var}: SET ({value})")
        
        elif var == "SOLANA_RPC_URL":
            if not value.startswith("http"):
                errors.append(f"❌ {var} should start with http:// or https://")
                print(f"❌ {var}: INVALID URL")
            else:
                success.append(f"✅ {var} is set")
                print(f"✅ {var}: SET ({value})")
        
        elif var == "QUOTE_TOKEN_ADDRESS":
            expected = "8D9foi1nqfabp8D3uNJCrzt1xkvxq8xHYH8Lxb4fbonk"
            if value == expected:
                success.append(f"✅ {var} is correct (MEMESAI)")
                print(f"✅ {var}: CORRECT (MEMESAI)")
            else:
                warnings.append(f"⚠️  {var} differs from expected MEMESAI address")
                print(f"⚠️  {var}: CUSTOM ({value})")

print()
print("-" * 70)
print("📋 Checking Optional Variables:")
print("-" * 70)

# Check optional with defaults
optional_vars = {
    "BASE_TOKEN_ADDRESS": "So11111111111111111111111111111111111111112",
    "LOG_LEVEL": "INFO",
    "DEFAULT_SLIPPAGE_BPS": "100",
    "COMMITMENT_LEVEL": "confirmed"
}

for var, expected_default in optional_vars.items():
    value = os.getenv(var, "NOT SET")
    if value == expected_default or value == "NOT SET":
        print(f"✅ {var}: {value}")
    else:
        print(f"⚠️  {var}: {value} (custom value)")

print()
print("=" * 70)
print("📊 VALIDATION SUMMARY")
print("=" * 70)

if errors:
    print()
    print("❌ ERRORS FOUND:")
    for error in errors:
        print(f"   {error}")

if warnings:
    print()
    print("⚠️  WARNINGS:")
    for warning in warnings:
        print(f"   {warning}")

if success and not errors:
    print()
    print("✅ ALL REQUIRED VARIABLES ARE SET!")
    print()
    print("=" * 70)
    print("🎯 NEXT STEPS:")
    print("=" * 70)
    print()
    print("1. Test Solana connection:")
    print("   python test_solana_connection.py")
    print()
    print("2. If connection test passes, start the bot:")
    print("   python -m bot.main")
    print()
    print("3. Message your bot on Telegram:")
    print("   /help - See all commands")
    print("   /config - Set up trading parameters")
    print("   /start - Begin trading")
    print()
elif not errors:
    print()
    print("⚠️  Configuration has warnings but should work.")
    print("    You can proceed to test the connection.")
    print()
else:
    print()
    print("❌ Please fix the errors above and run this script again.")
    print()
    print("💡 TIP: Edit your .env file:")
    print("   nano .env")
    print()
    sys.exit(1)

print("=" * 70)

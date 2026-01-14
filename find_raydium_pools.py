#!/usr/bin/env python3
"""
Helper script to find Raydium pools on devnet or get pool information.

This script helps you:
1. List available Raydium pools on devnet
2. Get pool information for a specific pool
3. Understand pool structure for implementation
"""

import sys
import os
from typing import Optional

# Add bot directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bot'))


def check_devnet_pools():
    """
    Check for Raydium pools on devnet.
    
    Note: Raydium may not have active pools on devnet.
    You may need to:
    1. Use mainnet for testing (with small amounts)
    2. Create your own devnet pool
    3. Use a mock/simulator for testing
    """
    print("=" * 60)
    print("RAYDIUM DEVNET POOL CHECK")
    print("=" * 60)
    print()
    
    print("⚠️  IMPORTANT: Raydium Protocol Considerations")
    print("-" * 60)
    print("Raydium is primarily deployed on Solana MAINNET.")
    print("Devnet pools may be limited or non-existent.")
    print()
    print("Options for Testing:")
    print()
    print("1. 🔵 USE MAINNET WITH SMALL AMOUNTS")
    print("   - Most realistic testing environment")
    print("   - Use VERY small amounts (0.01 SOL)")
    print("   - Real liquidity and pricing")
    print("   - Recommended approach")
    print()
    print("2. 🟡 CREATE DEVNET POOL (Advanced)")
    print("   - Requires deploying Raydium contracts on devnet")
    print("   - Complex setup and maintenance")
    print("   - Not recommended for quick testing")
    print()
    print("3. 🟢 MOCK TESTING (Development)")
    print("   - Test business logic without real swaps")
    print("   - Mock the raydium_client methods")
    print("   - Good for bot logic testing")
    print()
    
    return True


def get_mainnet_memesai_pools():
    """
    Provide guidance on finding MEMESAI pools on mainnet.
    """
    print("\n" + "=" * 60)
    print("FINDING MEMESAI RAYDIUM POOLS ON MAINNET")
    print("=" * 60)
    print()
    
    print("Steps to find your pool:")
    print()
    print("1. Visit Raydium: https://raydium.io/liquidity/pools/")
    print("2. Search for 'MEMESAI' or your token symbol")
    print("3. Click on the pool to see details")
    print("4. Copy the Pool ID from the URL or pool info")
    print()
    print("Example URL:")
    print("https://raydium.io/liquidity/increase/?pool_id=POOL_ID_HERE")
    print("                                         ^^^^^^^^^^^^^^^^^")
    print("                                         This is what you need")
    print()
    print("Alternative - Use Solana Explorer:")
    print("1. Go to https://solscan.io/")
    print("2. Search for your MEMESAI token mint address")
    print("3. Look at 'Holders' or 'Transfers' tab")
    print("4. Find Raydium program accounts")
    print("5. Identify the pool account (AMM ID)")
    print()


def show_pool_structure():
    """
    Show what a Raydium pool account looks like.
    """
    print("\n" + "=" * 60)
    print("RAYDIUM POOL ACCOUNT STRUCTURE")
    print("=" * 60)
    print()
    
    print("A Raydium AMM pool account contains:")
    print()
    print("Key Information Needed:")
    print("  • Pool ID (AMM ID): The pool's public key")
    print("  • Token A Mint: First token's mint address (usually SOL)")
    print("  • Token B Mint: Second token's mint address (MEMESAI)")
    print("  • Token A Vault: Pool's token A account")
    print("  • Token B Vault: Pool's token B account")
    print("  • LP Token Mint: Liquidity provider token")
    print()
    print("For Swapping, you need:")
    print("  • User's source token account (what you're spending)")
    print("  • User's destination token account (what you're receiving)")
    print("  • Pool's token vaults (for reserves)")
    print("  • AMM authority (PDA)")
    print()


def show_implementation_tips():
    """
    Show tips for implementing Raydium swaps.
    """
    print("\n" + "=" * 60)
    print("IMPLEMENTATION TIPS")
    print("=" * 60)
    print()
    
    print("Recommended Approach:")
    print()
    print("1️⃣  Use Raydium SDK (TypeScript/JavaScript)")
    print("   - Official SDK: https://github.com/raydium-io/raydium-sdk")
    print("   - Most complete and tested")
    print("   - Can be called from Python via Node.js bridge")
    print()
    print("2️⃣  Use Anchor for Raydium Program Calls")
    print("   - anchorpy library already installed")
    print("   - Need Raydium IDL (Interface Definition)")
    print("   - More direct but requires understanding program")
    print()
    print("3️⃣  Use Raw Transaction Building")
    print("   - Build instructions manually")
    print("   - Most flexible but complex")
    print("   - Need to understand Raydium program structure")
    print()
    
    print("Code Example Skeleton:")
    print("-" * 60)
    print("""
def swap_exact_sol_for_tokens(self, amount_sol, slippage_bps):
    # 1. Get pool state
    pool_state = fetch_pool_account(self.pool_id)
    
    # 2. Calculate amounts with slippage
    amount_in = int(amount_sol * LAMPORTS_PER_SOL)
    min_amount_out = calculate_min_out(amount_in, pool_state, slippage_bps)
    
    # 3. Get or create token accounts
    user_sol_account = get_ata(self.wallet, WSOL_MINT)
    user_token_account = get_or_create_ata(self.wallet, self.quote_token_mint)
    
    # 4. Build swap instruction
    swap_ix = build_raydium_swap_instruction(
        amm_id=self.pool_id,
        amm_authority=derive_amm_authority(self.pool_id),
        user_source_token_account=user_sol_account,
        user_destination_token_account=user_token_account,
        pool_source_token_account=pool_state.token_a_vault,
        pool_destination_token_account=pool_state.token_b_vault,
        amount_in=amount_in,
        minimum_amount_out=min_amount_out,
    )
    
    # 5. Build and send transaction
    tx = Transaction().add(swap_ix)
    signature = send_transaction(tx, self.keypair)
    
    return signature
""")
    print("-" * 60)
    print()


def show_testing_strategy():
    """
    Show recommended testing strategy.
    """
    print("\n" + "=" * 60)
    print("RECOMMENDED TESTING STRATEGY")
    print("=" * 60)
    print()
    
    print("Phase 1: Unit Testing (Mock Everything)")
    print("  ✓ Test bot logic without real blockchain")
    print("  ✓ Mock all raydium_client methods")
    print("  ✓ Test Telegram commands and workflows")
    print("  ✓ Test database operations")
    print()
    
    print("Phase 2: Integration Testing (Mainnet, Small Amounts)")
    print("  ✓ Use real Solana mainnet")
    print("  ✓ Start with 0.01 SOL (< $1)")
    print("  ✓ Test single swap manually first")
    print("  ✓ Monitor transaction logs carefully")
    print("  ✓ Verify balances after each trade")
    print()
    
    print("Phase 3: Gradual Scale-Up")
    print("  ✓ Increase to 0.1 SOL after successful tests")
    print("  ✓ Test full BUY-BUY-SELL-SELL pattern")
    print("  ✓ Run for limited time (10-20 trades)")
    print("  ✓ Monitor P/L and slippage")
    print()
    
    print("Phase 4: Production")
    print("  ✓ Use production RPC (QuickNode, Helius)")
    print("  ✓ Set up monitoring and alerts")
    print("  ✓ Start with conservative settings")
    print("  ✓ Regular balance checks")
    print()


def main():
    """Main entry point."""
    print("\n" + "🔍" * 30)
    print("RAYDIUM POOL FINDER & IMPLEMENTATION GUIDE")
    print("🔍" * 30 + "\n")
    
    check_devnet_pools()
    get_mainnet_memesai_pools()
    show_pool_structure()
    show_implementation_tips()
    show_testing_strategy()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print()
    print("1. Run: python test_solana_connection.py")
    print("   (Test basic connectivity first)")
    print()
    print("2. Find your MEMESAI pool ID on Raydium mainnet")
    print()
    print("3. Choose implementation approach:")
    print("   a) Use Raydium SDK via Node.js bridge (recommended)")
    print("   b) Use anchorpy with Raydium IDL")
    print("   c) Build raw transactions manually")
    print()
    print("4. Implement the swap functions in raydium_client.py")
    print()
    print("5. Test with small amounts on mainnet")
    print()
    print("=" * 60)
    print()
    print("📚 Useful Resources:")
    print("  • Raydium SDK: https://github.com/raydium-io/raydium-sdk")
    print("  • Raydium Docs: https://docs.raydium.io/")
    print("  • Solana Cookbook: https://solanacookbook.com/")
    print("  • Anchor Docs: https://www.anchor-lang.com/")
    print()


if __name__ == "__main__":
    main()

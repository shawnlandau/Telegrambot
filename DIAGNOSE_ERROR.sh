#!/bin/bash
#
# DIAGNOSE "Failed to start trading session" ERROR
# Run this on your DigitalOcean droplet to identify the problem
#

echo "=================================================="
echo "🔍 DIAGNOSING 'Failed to start trading session' ERROR"
echo "=================================================="
echo ""

echo "1️⃣ Checking bot service status..."
echo "-----------------------------------"
sudo systemctl status trading-bot --no-pager -l | head -20
echo ""

echo "2️⃣ Checking recent error logs..."
echo "-----------------------------------"
sudo journalctl -u trading-bot -n 100 --no-pager | grep -i "error\|traceback\|exception\|failed" | tail -30
echo ""

echo "3️⃣ Checking last 50 log lines..."
echo "-----------------------------------"
sudo journalctl -u trading-bot -n 50 --no-pager
echo ""

echo "4️⃣ Checking configuration..."
echo "-----------------------------------"
cd /opt/Telegrambot
echo "Current branch:"
git branch
echo ""
echo "Current commit:"
git log --oneline -1
echo ""
echo ".env file exists:"
if [ -f .env ]; then
    echo "✅ .env file found"
    echo ""
    echo "Key settings (censored):"
    cat .env | grep -E "SIMULATION_MODE|DEFAULT_SLIPPAGE_BPS|TELEGRAM_BOT_TOKEN|ALLOWED_TELEGRAM_IDS|WALLET_PRIVATE_KEY" | sed 's/=.*/=***HIDDEN***/'
else
    echo "❌ .env file NOT found!"
fi
echo ""

echo "5️⃣ Checking database..."
echo "-----------------------------------"
if [ -f bot_data.db ]; then
    echo "✅ Database file exists"
    ls -lh bot_data.db
else
    echo "❌ Database file NOT found"
fi
echo ""

echo "6️⃣ Checking Python dependencies..."
echo "-----------------------------------"
source venv/bin/activate
pip list | grep -E "telegram|solana|solders" | head -10
echo ""

echo "7️⃣ Testing Solana RPC connection..."
echo "-----------------------------------"
RPC_URL=$(cat .env | grep SOLANA_RPC_URL | cut -d'=' -f2)
echo "Testing: $RPC_URL"
curl -s -X POST "$RPC_URL" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"getVersion"}' | head -5
echo ""

echo "=================================================="
echo "📋 DIAGNOSIS COMPLETE"
echo "=================================================="
echo ""
echo "Please share the output above to diagnose the issue."
echo ""
echo "Common causes:"
echo "  1. Missing or invalid .env configuration"
echo "  2. No session configuration (need to run /config first)"
echo "  3. Insufficient balance"
echo "  4. Database corruption"
echo "  5. Python dependency issues"
echo ""

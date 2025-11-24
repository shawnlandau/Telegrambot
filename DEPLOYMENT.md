# DEX Bot Deployment Guide

## Project Status

✅ **All code has been implemented and committed locally**

Commit: `fda62df` - "feat: implement MVP DEX bot with fixed 2x2 trading pattern"

## What Has Been Built

### Core Components

1. **bot/main.py** - Telegram bot with full command handlers
2. **bot/config.py** - Environment configuration and validation
3. **bot/db.py** - SQLAlchemy database layer with SQLite
4. **bot/models.py** - Data models for sessions and trades
5. **bot/dex_client.py** - Web3 DEX client for Uniswap V2
6. **bot/session_runner.py** - Background trading loop with 2×2 pattern
7. **bot/abi/** - ABI files for ERC20 and Uniswap V2 router

### Documentation

- **README.md** - Comprehensive documentation with usage examples
- **.env.example** - Environment configuration template
- **requirements.txt** - All Python dependencies

## Deployment Steps

### 1. Push to GitHub

Since there are credential issues with the automated push, please push manually:

```bash
# Ensure you're in the webapp directory
cd /home/user/webapp

# Check current branch
git branch

# Push main branch to remote
git push origin main

# Create and push feature branch
git checkout -b genspark_ai_developer
git push -u origin genspark_ai_developer
```

### 2. Create Pull Request

After pushing, create a PR on GitHub:

1. Go to https://github.com/shawnlandau/Telegrambot
2. Click "Pull requests" → "New pull request"
3. Set base: `main`, compare: `genspark_ai_developer`
4. Title: "feat: MVP DEX bot with fixed 2×2 trading pattern"
5. Description:

```markdown
## Overview
Implements a production-ready Telegram-controlled DEX trading bot with fixed 2×2 pattern (BUY-BUY-SELL-SELL).

## Features
- ✅ Telegram bot with interactive commands
- ✅ Web3 integration for Uniswap V2-style DEXes
- ✅ SQLite database for persistence
- ✅ Background trading sessions with automatic pattern execution
- ✅ Comprehensive error handling and logging
- ✅ Security best practices

## Compliance
This bot is designed for legitimate DCA execution only, NOT for:
- ❌ Wash trading
- ❌ Volume manipulation
- ❌ Market spoofing

## Components
- `bot/main.py` - Telegram bot entry point
- `bot/dex_client.py` - Web3 DEX interactions
- `bot/session_runner.py` - Trading loop with 2×2 pattern
- `bot/db.py` - Database layer
- `bot/models.py` - Data models
- `bot/config.py` - Configuration management

## Testing
Tested components:
- Configuration validation
- Database operations
- Model data structures
- Command handler logic

## Documentation
- Comprehensive README with setup instructions
- Environment configuration template
- Inline code documentation
- Compliance disclaimers
```

### 3. Server Deployment

Once PR is merged, deploy to a server:

#### Option A: VPS/Cloud Server

```bash
# Install Python 3.11+
sudo apt update
sudo apt install python3.11 python3.11-venv

# Clone repository
git clone https://github.com/shawnlandau/Telegrambot.git
cd Telegrambot

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Fill in your values

# Run bot
python -m bot.main
```

#### Option B: Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot/ ./bot/
COPY .env .

CMD ["python", "-m", "bot.main"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  dex-bot:
    build: .
    restart: unless-stopped
    volumes:
      - ./bot_data.db:/app/bot_data.db
      - ./bot.log:/app/bot.log
    env_file:
      - .env
```

Deploy:

```bash
docker-compose up -d
docker-compose logs -f
```

#### Option C: Systemd Service

Create `/etc/systemd/system/dex-bot.service`:

```ini
[Unit]
Description=DEX Trading Bot
After=network.target

[Service]
Type=simple
User=YOUR_USER
WorkingDirectory=/path/to/Telegrambot
Environment="PATH=/path/to/Telegrambot/venv/bin"
ExecStart=/path/to/Telegrambot/venv/bin/python -m bot.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable dex-bot
sudo systemctl start dex-bot
sudo systemctl status dex-bot
```

### 4. Configuration

Fill in `.env` with your values:

```bash
# Required
RPC_URL=https://mainnet.infura.io/v3/YOUR_KEY
WALLET_PRIVATE_KEY=0xYOUR_PRIVATE_KEY
DEX_ROUTER_ADDRESS=0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D
BASE_TOKEN_ADDRESS=0xYOUR_BASE_TOKEN
QUOTE_TOKEN_ADDRESS=0xYOUR_QUOTE_TOKEN
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN
ALLOWED_TELEGRAM_IDS=YOUR_USER_ID
```

### 5. Testing Checklist

Before mainnet:

- [ ] Test on testnet (Goerli, Sepolia)
- [ ] Verify all commands work
- [ ] Check database persistence
- [ ] Monitor logs for errors
- [ ] Test with small amounts
- [ ] Verify token approvals work
- [ ] Test session start/stop
- [ ] Verify balance checks
- [ ] Test slippage handling

### 6. Monitoring

Monitor the bot:

```bash
# Check logs
tail -f bot.log

# Check database
sqlite3 bot_data.db "SELECT * FROM session_states;"
sqlite3 bot_data.db "SELECT * FROM trade_records ORDER BY timestamp DESC LIMIT 10;"

# Check bot status via Telegram
/status
```

### 7. Maintenance

Regular tasks:

- Monitor wallet balances
- Check for stuck sessions
- Review trade logs
- Update RPC endpoints if needed
- Rotate private keys periodically
- Backup database regularly

```bash
# Backup database
cp bot_data.db bot_data.db.backup.$(date +%Y%m%d)

# Restart bot
sudo systemctl restart dex-bot  # If using systemd
# OR
docker-compose restart  # If using Docker
```

## Security Reminders

1. ✅ Never commit `.env` to git
2. ✅ Use dedicated wallet with limited funds
3. ✅ Secure private keys (use hardware wallet or vault)
4. ✅ Regularly monitor for unauthorized access
5. ✅ Keep dependencies updated
6. ✅ Use HTTPS for RPC endpoints
7. ✅ Limit Telegram access to trusted users only

## Support

For issues:
1. Check `bot.log` for errors
2. Review README troubleshooting section
3. Verify environment configuration
4. Test on testnet first

## Repository

- GitHub: https://github.com/shawnlandau/Telegrambot
- Branch: `genspark_ai_developer`
- Commit: `fda62df`

---

**Note**: This bot is for legitimate DCA execution only. Users are responsible for regulatory compliance in their jurisdiction.

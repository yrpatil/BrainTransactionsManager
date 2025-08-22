# 🧠 BrainTransactionsManager

**Blessed by Goddess Laxmi for Infinite Abundance** 🙏

A powerful, modular transactional system with **multi-version API support** designed for various types of financial transactions, starting with our flagship trading module **Laxmi-yantra**.

## 🌟 Vision
A unified transaction management system that handles different types of financial operations with:
- **Simplicity**: Clean, readable, and robust architecture
- **Reliability**: 100% transactional integrity and fail-safe mechanisms  
- **Maintainability**: Modular design for easy extension and maintenance
- **Backward Compatibility**: Multi-version API support with N-4 deprecation policy

## 🚀 Multi-Version API System

### Current Versions
- **v1.0.0**: Stable production version
- **development**: Live development version for testing

### API Endpoints
```
http://127.0.0.1:8000/v1.0.0/tools/buy_stock
http://127.0.0.1:8000/development/tools/buy_stock
http://127.0.0.1:8000/health
http://127.0.0.1:8000/versions
```

## 📦 Transaction Modules

### 🏆 Laxmi-yantra (Trading Transactions)
Our flagship trading transaction manager blessed by Goddess Laxmi for abundance in trading.

**Features:**
- Alpaca API integration for order execution
- Real-time position and portfolio management
- Kill switch support for emergency control
- Transaction integrity and audit trails
- Paper trading support for safe testing
- Multi-version API with backward compatibility

### 🔮 Future Modules
- **Midas-touch**: Cryptocurrency exchange transactions
- **Golden-gate**: Multi-exchange arbitrage transactions
- **Wealth-weaver**: Portfolio rebalancing transactions
- **Fortune-flow**: Automated investment transactions

## 🚀 Getting Started

### Quick Start
```bash
# Start multi-version server
./start-server.sh

# Test endpoints
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/versions
```

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.template .env
# Edit .env with your credentials

# Run tests
python -m pytest tests/

# Test Laxmi-yantra with paper trading
python examples/test_laxmi_yantra.py
```

## 📚 Documentation

- **[AI Agent Usage Guide](docs/AI_AGENT_USAGE_GUIDE.md)** - Complete guide for AI agents
- **[REST API Usage Guide](docs/REST_API_USAGE_GUIDE.md)** - HTTP API documentation
- **[Database Setup Guide](docs/DATABASE_SETUP_GUIDE.md)** - Database configuration
- **[Version Management](docs/REPO_VERSIONING_AND_BRANCHING.md)** - Release and versioning

## 🚀 Release Management

```bash
# Create new release
python release/release_cli.py create v1.1.0 --type minor

# List releases
python release/release_cli.py list

# Validate setup
python release/release_cli.py validate
```

## 🙏 Blessed with Divine Grace
*May Goddess Laxmi's blessings bring infinite abundance and prosperity to all who use this system*

---
**Built with 💖 and divine inspiration**

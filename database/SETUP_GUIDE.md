# 🗄️ Database Setup Guide for BrainTransactionsManager
**Blessed by Goddess Laxmi for Infinite Abundance** 🙏

## Quick Setup (Essential Steps Only)

### 1. Verify PostgreSQL is Running
```bash
# Check if PostgreSQL is running
psql -h localhost -p 5432 -U $(whoami) -d postgres -c "SELECT version();"
```

### 2. Run Complete Database Setup
```bash
# Run the complete setup script
psql -h localhost -U $(whoami) postgres -f database/ddl/setup_complete.sql
```

### 3. Verify Setup
```bash
# Test the system
python -c "
from src.braintransactions.modules.laxmi_yantra.trading_manager import LaxmiYantra
laxmi = LaxmiYantra()
print('✅ Laxmi-yantra system ready!')
"
```

## What Gets Created

### Database Structure
- **Database**: `braintransactions`
- **Schema**: `laxmiyantra` 
- **Extension**: TimescaleDB enabled

### Essential Tables
- `portfolio_positions` - Current holdings
- `order_history` - Order tracking
- `transaction_log` - Audit trail
- `ohlc_data` - Market data (TimescaleDB hypertable)
- `system_status` - System health

### Configuration
The system automatically uses:
- Database: `braintransactions`
- Schema: `laxmiyantra`
- User: Current system user
- Host: localhost:5432

## Troubleshooting

### If PostgreSQL isn't running:
```bash
brew services start postgresql@17
```

### If setup fails:
```bash
# Clean and restart
dropdb braintransactions
psql -h localhost -U $(whoami) postgres -f database/ddl/setup_complete.sql
```

### Verify Tables:
```bash
psql -h localhost -U $(whoami) braintransactions -c "\dt+ laxmiyantra.*"
```

That's it! The setup script handles everything else automatically.

**May Goddess Laxmi bless your trading with infinite prosperity!** ✨

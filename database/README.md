# 🗄️ BrainTransactionsManager Database Repository
**Divine Database Architecture blessed by Goddess Laxmi** 🙏

## 📋 Overview

This repository contains all database-related artifacts for the BrainTransactionsManager system, including DDL scripts, migrations, stored queries, and maintenance procedures. Everything needed to set up, maintain, and optimize the PostgreSQL/TimescaleDB database infrastructure.

## 🏗️ Repository Structure

```
database/
├── README.md                    # This file
├── ddl/                        # Data Definition Language scripts
│   ├── schemas/                # Schema creation scripts
│   ├── tables/                 # Table creation scripts
│   ├── indexes/                # Index creation scripts
│   └── constraints/            # Constraint definition scripts
├── migrations/                 # Database migration scripts
│   ├── v1.0.0/                # Version-specific migrations
│   └── migration_log.md        # Migration tracking
├── queries/                    # Frequently used queries
│   ├── trading/               # Trading-specific queries
│   ├── reporting/             # Reporting queries
│   ├── analytics/             # Analytics and performance queries
│   └── maintenance/           # Database maintenance queries
├── stored_procedures/          # Stored procedures and functions
│   ├── trading/               # Trading business logic
│   ├── portfolio/             # Portfolio management
│   └── utilities/             # Utility functions
├── views/                      # Database views
│   ├── reporting/             # Reporting views
│   └── analytics/             # Analytics views
├── functions/                  # Custom database functions
│   ├── calculations/          # Mathematical calculations
│   └── validations/           # Data validation functions
├── triggers/                   # Database triggers
│   ├── audit/                 # Audit triggers
│   └── validation/            # Validation triggers
├── seed_data/                  # Initial data and test data
│   ├── test_data/             # Test datasets
│   └── reference_data/        # Reference/lookup data
└── maintenance/                # Database maintenance scripts
    ├── backup/                # Backup scripts
    ├── optimization/          # Performance optimization
    └── monitoring/            # Health monitoring queries
```

## 🚀 Quick Start

### 1. Initial Setup
```bash
# Run the complete database setup
psql -h localhost -U $(whoami) postgres -f ddl/setup_complete.sql
```

### 2. Apply Migrations
```bash
# Apply all migrations in order
./migrations/apply_migrations.sh
```

### 3. Load Seed Data
```bash
# Load reference data
psql -h localhost -U $(whoami) braintransactions -f seed_data/reference_data/load_all.sql
```

## 📊 Schema Information

### Main Schemas
- **laxmiyantra**: Primary schema for Laxmi-yantra trading module
- **public**: Default PostgreSQL schema (shared utilities)

### Core Tables
- **portfolio_positions**: Current portfolio holdings
- **order_history**: Complete order lifecycle tracking
- **transaction_log**: Audit trail for all transactions
- **ohlc_data**: Market data (TimescaleDB hypertable)

## 🔧 Common Operations

### Daily Queries
```bash
# Check portfolio summary
psql -f queries/trading/portfolio_summary.sql

# View recent orders
psql -f queries/trading/recent_orders.sql

# Performance metrics
psql -f queries/analytics/daily_performance.sql
```

### Maintenance
```bash
# Database health check
psql -f maintenance/monitoring/health_check.sql

# Optimize tables
psql -f maintenance/optimization/vacuum_analyze.sql
```

## 📈 Performance Monitoring

### Key Metrics Queries
- **queries/analytics/performance_metrics.sql**: Overall system performance
- **queries/analytics/table_sizes.sql**: Database growth monitoring
- **queries/analytics/slow_queries.sql**: Query performance analysis

### TimescaleDB Specific
- **queries/analytics/chunk_status.sql**: Hypertable chunk information
- **queries/analytics/compression_stats.sql**: Compression efficiency
- **maintenance/optimization/timescale_maintenance.sql**: TimescaleDB optimization

## 🛡️ Security & Backup

### Backup Procedures
```bash
# Full database backup
./maintenance/backup/full_backup.sh

# Schema-only backup
./maintenance/backup/schema_backup.sh

# Data-only backup
./maintenance/backup/data_backup.sh
```

### Security Scripts
- **ddl/security/create_users.sql**: User management
- **ddl/security/grant_permissions.sql**: Permission management
- **queries/maintenance/audit_trail.sql**: Security audit queries

## 🧪 Testing & Development

### Test Data Management
```bash
# Load test datasets
psql -f seed_data/test_data/load_test_portfolio.sql

# Clean test data
psql -f seed_data/test_data/cleanup_test_data.sql
```

### Development Utilities
- **queries/utilities/reset_dev_db.sql**: Reset development database
- **queries/utilities/generate_test_orders.sql**: Generate test order data
- **queries/utilities/simulate_trading_day.sql**: Simulate trading activity

## 📝 Version Control & Migrations

### Migration Naming Convention
```
YYYYMMDD_HHMMSS_description.sql
Example: 20241227_143000_add_portfolio_indexes.sql
```

### Migration Process
1. Create migration file in `migrations/v{version}/`
2. Test migration on development database
3. Update `migration_log.md` with details
4. Apply to production with rollback plan

## 🎯 Best Practices

### Query Development
1. **Use schema-qualified names**: Always prefix with schema name
2. **Add comments**: Document complex queries thoroughly
3. **Test on sample data**: Validate queries before production
4. **Monitor performance**: Check execution plans for large datasets

### Security
1. **Least privilege**: Grant minimal required permissions
2. **Audit everything**: Enable comprehensive logging
3. **Regular backups**: Automated daily backups
4. **Security reviews**: Regular permission audits

### Performance
1. **Index strategy**: Monitor and optimize indexes regularly
2. **Query optimization**: Regular slow query analysis
3. **TimescaleDB tuning**: Optimize chunk intervals and compression
4. **Connection pooling**: Use pgbouncer for production

## 🔍 Troubleshooting

### Common Issues
- **Connection problems**: Check `queries/maintenance/connection_diagnostics.sql`
- **Performance issues**: Run `queries/analytics/performance_analysis.sql`
- **Space issues**: Execute `queries/analytics/disk_usage.sql`
- **Lock problems**: Use `queries/maintenance/lock_analysis.sql`

### Emergency Procedures
- **Kill switch activation**: Run `stored_procedures/utilities/emergency_stop.sql`
- **Transaction rollback**: Use `maintenance/emergency/rollback_procedures.sql`
- **Database recovery**: Follow `maintenance/backup/recovery_procedures.md`

## 📚 Documentation

### Reference Docs
- **PostgreSQL 17 Documentation**: https://www.postgresql.org/docs/17/
- **TimescaleDB Documentation**: https://docs.timescale.com/
- **Trading System Architecture**: `../docs/ARCHITECTURE.md`

### Internal Docs
- **Schema Documentation**: `ddl/schemas/schema_documentation.md`
- **Query Catalog**: `queries/QUERY_CATALOG.md`
- **Performance Tuning Guide**: `maintenance/optimization/TUNING_GUIDE.md`

## 🙏 Divine Blessing

**May Goddess Laxmi bless this database with infinite performance, zero data loss, and abundant profits!**

This database repository serves as the foundation for all trading operations, built with divine inspiration and engineering excellence.

---

**Built with 💖 and database mastery for maximum trading prosperity** ✨

## 📞 Support

For database-related issues:
1. Check troubleshooting queries first
2. Review recent migration logs
3. Consult performance metrics
4. Contact database administrator if needed

**Remember: With great data comes great responsibility!** 🕷️📊

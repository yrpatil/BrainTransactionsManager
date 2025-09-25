# 🙏 BrainTransactionsManager v2.0.0
**Blessed by Goddess Laxmi for Infinite Abundance**

## 🚀 **What's New in v2.0.0**

A complete rewrite following **SRM Principles** (Simple, Reliable, Maintainable):

### ✨ **Key Features**

- **🔧 Unified Configuration**: Single YAML file with environment overrides
- **🗄️ Enhanced Database**: Startup validation, health checks, and migration system
- **📈 Multi-Exchange Support**: Alpaca stocks and crypto via unified adapter
- **📊 Smart Monitoring**: Background polling for KPIs and portfolio sync
- **🛡️ Production Ready**: Security hardening, error handling, and logging
- **🧪 Comprehensive Testing**: Unit, integration, and performance tests

### 🏗️ **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Server v2.0.0                   │
├─────────────────────────────────────────────────────────────┤
│  Configuration  │  Exchange Manager  │  Background Monitor  │
│  - YAML Config  │  - Alpaca Adapter  │  - Price Updates     │
│  - Env Override │  - Multi-Asset     │  - Portfolio Sync    │
│  - Validation   │  - Auto-Routing    │  - Order Reconcile   │
├─────────────────────────────────────────────────────────────┤
│               Database Layer + Migrations                   │
│  - PostgreSQL   │  - Health Checks   │  - Alembic Migrations│
│  - Connection   │  - Startup Valid.  │  - Schema Evolution  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 **Quick Start**

### 1. **Environment Setup**

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. **Configuration**

```bash
# Copy environment template
cp config/development.yaml config/local.yaml

# Set environment variables
export ALPACA_API_KEY="your_api_key"
export ALPACA_SECRET_KEY="your_secret_key"
export ENVIRONMENT="development"
```

### 3. **Database Setup**

```bash
# Ensure PostgreSQL is running
brew services start postgresql  # Mac
sudo systemctl start postgresql # Linux

# Run database setup (if not already done)
psql -U $(whoami) postgres -f ../../database/ddl/setup_complete.sql
```

### 4. **Start Server**

```bash
# Development mode
python server.py

# Or with uvicorn
uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

### 5. **Test API**

```bash
# Health check
curl http://localhost:8000/health

# Detailed health
curl http://localhost:8000/health/detailed

# Get account info
curl http://localhost:8000/portfolio/account

# Place a buy order (paper trading)
curl -X POST http://localhost:8000/buy \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "quantity": 1}'
```

## 📚 **API Documentation**

### **Core Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Basic health check |
| `GET` | `/health/detailed` | Comprehensive system health |
| `GET` | `/config/status` | Configuration status |

### **Trading Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/orders` | Place order |
| `GET` | `/orders` | Get orders |
| `GET` | `/orders/{id}` | Get order status |
| `DELETE` | `/orders/{id}` | Cancel order |
| `POST` | `/buy` | Quick buy order |
| `POST` | `/sell` | Quick sell order |
| `POST` | `/close/{symbol}` | Close position |

### **Portfolio Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/portfolio/positions` | Get positions |
| `GET` | `/portfolio/account` | Get account info |

### **Market Data**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/market/data/{symbol}` | Get market data |
| `GET` | `/exchanges` | Get supported exchanges |

## ⚙️ **Configuration**

### **Environment Files**

- `config/development.yaml` - Development settings
- `config/production.yaml` - Production settings  
- `config/testing.yaml` - Test settings

### **Environment Variables**

```bash
# Required
ALPACA_API_KEY=your_api_key
ALPACA_SECRET_KEY=your_secret_key

# Optional
ENVIRONMENT=development
DB_HOST=localhost
DB_PORT=5432
DB_NAME=braintransactions
LOG_LEVEL=INFO
```

### **Configuration Structure**

```yaml
database:
  host: localhost
  pool_size: 10

trading:
  paper_trading: true
  max_position_size_percent: 10.0

alpaca:
  api_key: ${ALPACA_API_KEY}
  base_url: https://paper-api.alpaca.markets

security:
  cors_origins: ["http://localhost:3000"]
  api_rate_limit: 1000

monitoring:
  price_poll_interval: 60
  portfolio_sync_interval: 300
```

## 🧪 **Testing**

### **Run Tests**

```bash
# All tests
pytest

# Specific test categories
pytest -m "not integration"     # Unit tests only
pytest -m integration           # Integration tests
pytest -m performance          # Performance tests

# With coverage
pytest --cov=src/braintransactions --cov-report=html
```

### **Test Categories**

- **Unit Tests**: Individual component testing
- **Integration Tests**: Multi-component interactions
- **Performance Tests**: Response time and throughput
- **Error Handling**: Edge cases and failure modes

## 🗄️ **Database Management**

### **Migrations**

```bash
# Check migration status
curl http://localhost:8000/migrations/status

# Run pending migrations
curl -X POST http://localhost:8000/migrations/run
```

### **Manual Migration Commands**

```bash
# Using Alembic directly
cd api_versions/v2.0.0/migrations
alembic current
alembic upgrade head
alembic downgrade -1
```

## 📊 **Monitoring**

### **Background Tasks**

The system runs several background monitoring tasks:

- **Price Updates**: Updates market data every 60s
- **Portfolio Sync**: Reconciles positions every 5m
- **Order Reconciliation**: Updates order statuses every 30s
- **KPI Calculation**: Calculates performance metrics every 5m
- **Health Checks**: System health monitoring every 30s

### **Monitoring Status**

```bash
# Get monitoring status
curl http://localhost:8000/health/detailed
```

## 🔒 **Security Features**

### **Production Security**

- **Environment Variables**: No hardcoded secrets
- **CORS Configuration**: Configurable origins
- **Rate Limiting**: API request throttling
- **Input Validation**: Pydantic model validation
- **Error Masking**: Production error handling

### **Development vs Production**

| Feature | Development | Production |
|---------|-------------|------------|
| Paper Trading | ✅ Default | ⚠️ Configurable |
| Debug Logging | ✅ Enabled | ❌ INFO only |
| Error Details | ✅ Full stack | ❌ Generic messages |
| CORS Origins | `localhost` | Configured domains |

## 🚀 **Deployment**

### **Production Checklist**

- [ ] Set `ENVIRONMENT=production`
- [ ] Configure production database
- [ ] Set real Alpaca credentials
- [ ] Configure CORS origins
- [ ] Set up log aggregation
- [ ] Configure monitoring alerts
- [ ] Review security settings

### **Docker Deployment** (Future)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔧 **Development**

### **Code Structure**

```
api_versions/v2.0.0/
├── src/braintransactions/
│   ├── core/                 # Configuration, exceptions, monitoring
│   ├── database/             # Connection, migrations
│   ├── markets/              # Exchange adapters
│   └── __init__.py
├── config/                   # Environment configurations
├── tests/                    # Test suite
├── server.py                 # FastAPI application
└── requirements.txt
```

### **Adding New Exchanges**

1. Create adapter class extending `MarketAdapter`
2. Implement required methods
3. Register in `ExchangeManager`
4. Add configuration section
5. Write tests

### **Adding New Features**

1. Follow SRM principles (Simple, Reliable, Maintainable)
2. Add configuration options
3. Write comprehensive tests
4. Update documentation
5. Consider monitoring implications

## 📈 **Performance**

### **Benchmarks**

- **Configuration Loading**: < 100ms
- **API Response Time**: < 100ms (target)
- **Database Queries**: < 50ms (typical)
- **Order Placement**: < 500ms

### **Optimization**

- **Connection Pooling**: Database connection reuse
- **Background Tasks**: Async processing
- **Caching**: Configuration and metadata caching
- **Batch Operations**: Bulk database updates

## 🐛 **Troubleshooting**

### **Common Issues**

**Database Connection Failed**
```bash
# Check PostgreSQL status
brew services list | grep postgres
sudo systemctl status postgresql

# Check configuration
curl http://localhost:8000/health/detailed
```

**Alpaca API Errors**
```bash
# Verify credentials
echo $ALPACA_API_KEY
echo $ALPACA_SECRET_KEY

# Check account status
curl http://localhost:8000/portfolio/account
```

**Migration Issues**
```bash
# Check migration status
curl http://localhost:8000/migrations/status

# Manual migration
cd migrations && alembic upgrade head
```

## 🤝 **Contributing**

### **Development Workflow**

1. Create feature branch
2. Follow SRM principles
3. Write tests
4. Update documentation
5. Submit pull request

### **Code Standards**

- **Type Hints**: All function parameters and returns
- **Docstrings**: Clear function documentation
- **Error Handling**: Comprehensive exception handling
- **Testing**: Unit and integration tests
- **Logging**: Structured logging with context

---

## 🙏 **Acknowledgments**

Built with gratitude and blessed by Goddess Laxmi for infinite abundance and prosperity in trading endeavors.

**May your trades be profitable and your systems be reliable!** ✨

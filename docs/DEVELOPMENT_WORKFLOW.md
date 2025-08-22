# 🛠️ Development Workflow Guide

**Blessed by Goddess Laxmi for Infinite Abundance** 🙏

## 🚀 Development Setup

### 1. Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd BrainTransactionsManager

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r mcp-server/requirements.txt
```

### 2. Configuration
```bash
# Copy environment template
cp .env.template .env

# Edit .env with your credentials
# Required: ALPACA_API_KEY, ALPACA_SECRET_KEY
# Optional: Database configuration
```

### 3. Database Setup
```bash
# Start PostgreSQL (if not running)
brew services start postgresql@17

# Run database setup
psql -d braintransactions -f database/ddl/setup_complete.sql
```

## 🔄 Development Workflow

### 1. Start Development Server
```bash
# Start multi-version server
./start-server.sh

# Server will be available at:
# - Main: http://127.0.0.1:8000
# - v1.0.0: http://127.0.0.1:8000/v1.0.0
# - Development: http://127.0.0.1:8000/development
```

### 2. Testing
```bash
# Run unit tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_laxmi_yantra.py -v

# Test live functionality
python examples/test_laxmi_yantra.py
```

### 3. API Testing
```bash
# Test health endpoints
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/v1.0.0/health
curl http://127.0.0.1:8000/development/health

# Test trading endpoints
curl -X POST http://127.0.0.1:8000/development/tools/get_account_status \
  -H 'Content-Type: application/json' -d '{}'
```

## 📦 Release Process

### 1. Create New Release
```bash
# Validate current setup
python release/release_cli.py validate

# Create new minor release
python release/release_cli.py create v1.1.0 --type minor --dry-run

# If dry-run looks good, create actual release
python release/release_cli.py create v1.1.0 --type minor
```

### 2. Update Documentation
```bash
# Generate documentation for new version
python -c "
import sys
sys.path.insert(0, '.')
from release.api_docs_generator import APIDocsGenerator
docs_gen = APIDocsGenerator()
docs = docs_gen.generate_version_docs('v1.1.0')
docs_gen.save_version_docs('v1.1.0', docs)
"
```

### 3. Deploy
```bash
# Commit changes
git add .
git commit -m "Release v1.1.0"

# Push to GitHub
git push origin main
git push origin v1.1.0
```

## 🐛 Debugging

### Common Issues
1. **Port conflicts**: Server auto-selects next available port
2. **Database connection**: Ensure PostgreSQL is running
3. **API credentials**: Verify ALPACA keys in .env
4. **Version conflicts**: Check api_versions.json configuration

### Logs
```bash
# View server logs
tail -f logs/braintransactions.log

# View release logs
tail -f logs/releases.log
```

## 📋 Code Standards

### Python
- Use type hints for all functions
- Follow PEP 8 style guide
- Add docstrings for all public functions
- Use async/await for I/O operations

### API Design
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Maintain backward compatibility
- Provide comprehensive error messages
- Include version in all responses

### Testing
- Write unit tests for all new features
- Test both success and failure scenarios
- Use pytest for test framework
- Maintain >80% code coverage

## 🛡️ Security

### Credentials
- Never commit .env files
- Use environment variables for secrets
- Rotate API keys regularly
- Use paper trading for development

### API Security
- Validate all inputs
- Implement rate limiting
- Use HTTPS in production
- Log security events

## 🙏 Divine Blessing
*May Goddess Laxmi guide your development with wisdom and abundance*

---
**For questions, consult the AI Agent Usage Guide or REST API Usage Guide**

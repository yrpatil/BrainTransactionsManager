# Release Notes - v2.0.1

**Release Date:** 2025-09-25
**Previous Version:** v1.2.0

## Overview

**Major Release** 🚀

This major release introduces significant new capabilities and may include breaking changes.

### Key Highlights
- Enhanced API versioning with backward compatibility
- Improved error handling and validation
- Optimized performance and reliability
- AI-agent focused documentation and examples


## 🚨 Breaking Changes

### API Version v2.0.1

⚠️ **Important:** This major release includes breaking changes.

- **URL Structure**: All endpoints now require version prefix (e.g., `/v2.0.1/tools/buy_stock`)
- **Response Format**: Some field names may have changed for consistency
- **Error Codes**: Enhanced error handling with more specific status codes
- **Authentication**: Updated authentication requirements (if applicable)

**Migration Required:** Please update your client applications to use the new API structure.
See the Migration Guide below for detailed instructions.


## ✨ New Features

- 🔄 **Multi-Version API Support**: Access multiple API versions simultaneously
- 📊 **Enhanced Portfolio Analytics**: Improved PnL calculations and reporting
- 🛡️ **Advanced Error Handling**: More granular error codes and messages
- 🔍 **Health Check Improvements**: Comprehensive system health monitoring
- 📈 **Strategy-Specific Summaries**: Detailed strategy performance analytics
- ⚡ **Performance Optimizations**: Faster response times and reduced latency
- 🤖 **AI-Agent Optimizations**: Streamlined endpoints for AI agent integration

## 🔧 Improvements

- 🚀 **Performance**: Optimized database queries and caching
- 📝 **Logging**: Enhanced logging with structured formats
- 🔧 **Configuration**: Simplified configuration management
- 🛡️ **Security**: Improved input validation and sanitization
- 📚 **Documentation**: Updated AI-agent focused usage guides
- 🔄 **Compatibility**: Better handling of version routing and fallbacks
- ⚡ **Response Times**: Reduced API response latency
- 🧪 **Testing**: Expanded test coverage for reliability

## 🐛 Bug Fixes

- 🔧 Fixed decimal serialization in JSON responses
- 📊 Fixed PnL calculation edge cases with zero cost basis
- 🔄 Fixed background poller error handling
- ⚠️ Fixed error messages for invalid tickers
- 🛡️ Fixed kill switch state persistence
- 📈 Fixed strategy summary aggregation
- 🔍 Fixed health check timeout issues

## 📊 API Changes

### API Endpoints (v2.0.1)

#### New Endpoints
- `GET /v2.0.1/health` - Version-specific health check
- `GET /v2.0.1/versions` - List available API versions
- `GET /v2.0.1/tools/{tool_name}` - Tool execution via GET (convenience)

#### Modified Endpoints
- All endpoints now include version in URL path
- Enhanced error responses with version information
- Improved response headers with deprecation warnings

#### Deprecated Endpoints
- Unversioned endpoints (will redirect to current version)
- Legacy `/mcp/` prefix (maintained for backward compatibility)

#### Response Format Changes
- Added `X-API-Version` header to all responses
- Enhanced error messages with context
- Consistent decimal precision in financial data


## 🔄 Migration Guide

### Migrating from v1.2.0 to v2.0.1

**🚨 Action Required**: This major release requires client updates.

#### URL Updates
```bash
# OLD
curl http://localhost:8000/mcp/tools/buy_stock

# NEW  
curl http://localhost:8000/v2.0.1/tools/buy_stock
```

#### Response Changes
- Some field names have been standardized
- Error format has been enhanced
- Headers now include version information

#### Testing Migration
1. Update your client code to use versioned URLs
2. Test against the new endpoints
3. Verify response parsing still works
4. Update error handling for new status codes

#### Backward Compatibility
- Old endpoints will redirect to current version
- Consider updating to explicit versioning for best performance


## 📋 Full Changelog

- 848fded fix(ordering): ensure unique client_order_id generation (env-strategy-symbol-uuid); docs: update API examples for client_order_id format

---

**🙏 Blessed by Goddess Laxmi for Infinite Abundance**

*This release continues our commitment to reliable, maintainable trading systems with enhanced backward compatibility.*

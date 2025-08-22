# Release Notes - v1.2.0

**Release Date:** 2025-08-23
**Previous Version:** v1.1.1

## Overview

**Minor Release** ✨

This minor release adds new features while maintaining backward compatibility.

### Key Highlights
- Enhanced API versioning with backward compatibility
- Improved error handling and validation
- Optimized performance and reliability
- AI-agent focused documentation and examples


## 🚨 Breaking Changes

✅ No breaking changes in this release. Fully backward compatible.

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

### API Endpoints (v1.2.0)

#### New Endpoints
- `GET /v1.2.0/health` - Version-specific health check
- `GET /v1.2.0/versions` - List available API versions
- `GET /v1.2.0/tools/{tool_name}` - Tool execution via GET (convenience)

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

### Migrating from v1.1.1 to v1.2.0

✅ **Good News**: This release is fully backward compatible!

#### Optional Updates
- Consider using versioned URLs for explicit version control
- Update to take advantage of new features
- Review enhanced error messages

#### No Action Required
- Existing clients will continue to work
- Automatic redirects handle unversioned requests


## 📋 Full Changelog

- Git changelog not available

---

**🙏 Blessed by Goddess Laxmi for Infinite Abundance**

*This release continues our commitment to reliable, maintainable trading systems with enhanced backward compatibility.*


---

# Release Notes - v1.1.1

**Release Date:** 2025-08-22
**Previous Version:** v1.1.0

## Overview

**Patch Release** 🔧

This patch release focuses on bug fixes and improvements.

### Key Highlights
- Enhanced API versioning with backward compatibility
- Improved error handling and validation
- Optimized performance and reliability
- AI-agent focused documentation and examples


## 🚨 Breaking Changes

✅ No breaking changes in this release. Fully backward compatible.

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

### API Endpoints (v1.1.1)

#### New Endpoints
- `GET /v1.1.1/health` - Version-specific health check
- `GET /v1.1.1/versions` - List available API versions
- `GET /v1.1.1/tools/{tool_name}` - Tool execution via GET (convenience)

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

### Migrating from v1.1.0 to v1.1.1

✅ **Good News**: This release is fully backward compatible!

#### Optional Updates
- Consider using versioned URLs for explicit version control
- Update to take advantage of new features
- Review enhanced error messages

#### No Action Required
- Existing clients will continue to work
- Automatic redirects handle unversioned requests


## 📋 Full Changelog

- Git changelog not available

---

**🙏 Blessed by Goddess Laxmi for Infinite Abundance**

*This release continues our commitment to reliable, maintainable trading systems with enhanced backward compatibility.*


---

# Release Notes - v1.1.0

**Release Date:** 2025-08-22
**Previous Version:** v1.0.0

## Overview

**Minor Release** ✨

This minor release adds new features while maintaining backward compatibility.

### Key Highlights
- Enhanced API versioning with backward compatibility
- Improved error handling and validation
- Optimized performance and reliability
- AI-agent focused documentation and examples


## 🚨 Breaking Changes

✅ No breaking changes in this release. Fully backward compatible.

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

### API Endpoints (v1.1.0)

#### New Endpoints
- `GET /v1.1.0/health` - Version-specific health check
- `GET /v1.1.0/versions` - List available API versions
- `GET /v1.1.0/tools/{tool_name}` - Tool execution via GET (convenience)

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

### Migrating from v1.0.0 to v1.1.0

✅ **Good News**: This release is fully backward compatible!

#### Optional Updates
- Consider using versioned URLs for explicit version control
- Update to take advantage of new features
- Review enhanced error messages

#### No Action Required
- Existing clients will continue to work
- Automatic redirects handle unversioned requests


## 📋 Full Changelog

- 908b102 feat: Initial release v1.0.0 - BrainTransactionsManager

---

**🙏 Blessed by Goddess Laxmi for Infinite Abundance**

*This release continues our commitment to reliable, maintainable trading systems with enhanced backward compatibility.*


---

## 1.0.0 - Initial V1 Release

- REST + MCP hybrid server with FastAPI and JSON-RPC bridge
- Laxmi-yantra trading tools (buy, sell, execute_trade)
- Safety: kill switch tools and status
- Resources: account_info, current_positions, portfolio_summary, strategy_summary, system_health
- PnL fields added to summaries (unrealized_pl, unrealized_pl_pct, abs_*, totals)
- Background portfolio event poller (orders/positions) controlled via env
- Start script with defaults (HTTP:8888, MCP SSE:8889) and auto-port selection
- Database schema setup (TimescaleDB hypertable for ohlc_data)
- REST API usage guide with anonymized samples


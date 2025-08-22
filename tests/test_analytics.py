import os
import sys
from datetime import datetime

import pytest
from fastapi.testclient import TestClient


# Ensure project root and src on path
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from server_manager.version_loader import VersionLoader  # noqa: E402


class DummyDB:
    def __init__(self, rows):
        self._rows = rows

    def execute_query(self, query, params=None):
        # Apply simple filtering by strategy if requested
        if params:
            s = params.get('strategy_name') or params.get('s')
            if s is not None:
                return [r for r in self._rows if r.get('strategy_name') == s]
        return self._rows


def build_rows():
    # Fixed timestamps for deterministic annualization
    price_ts = datetime.fromisoformat("2025-01-01T00:00:00")
    created_30d = datetime.fromisoformat("2024-12-02T00:00:00")
    created_10d = datetime.fromisoformat("2024-12-22T00:00:00")
    created_5d = datetime.fromisoformat("2024-12-27T00:00:00")

    return [
        {
            'strategy_name': 'default',
            'ticker': 'AAPL',
            'quantity': 10,
            'avg_entry_price': 100.0,
            'current_price': 110.0,
            'unrealized_pnl_percent': 10.0,
            'unrealized_pnl_amount': 100.0,
            'market_value': 1100.0,
            'last_updated': created_30d,
            'created_at': created_30d,
            'price_ts': price_ts,
        },
        {
            'strategy_name': 'crypto',
            'ticker': 'BTCUSD',
            'quantity': 0.5,
            'avg_entry_price': 20000.0,
            'current_price': 22000.0,
            'unrealized_pnl_percent': 10.0,
            'unrealized_pnl_amount': 1000.0,
            'market_value': 11000.0,
            'last_updated': created_10d,
            'created_at': created_10d,
            'price_ts': price_ts,
        },
        {
            'strategy_name': 'default',
            'ticker': 'TSLA',
            'quantity': 5,
            'avg_entry_price': 200.0,
            'current_price': 195.0,
            'unrealized_pnl_percent': -2.5,
            'unrealized_pnl_amount': -25.0,
            'market_value': 975.0,
            'last_updated': created_5d,
            'created_at': created_5d,
            'price_ts': price_ts,
        },
    ]


def build_app_with_dummy(rows):
    loader = VersionLoader()
    # Monkeypatch the db manager to return dummy rows
    loader._get_db_manager = lambda: DummyDB(rows)
    app = loader.create_basic_version_app("v1.0.0")
    return app


def test_analytics_portfolio_summary_basic():
    rows = build_rows()
    app = build_app_with_dummy(rows)
    client = TestClient(app)
    r = client.get("/analytics/performance/portfolio_summary")
    assert r.status_code == 200
    data = r.json()
    assert 'positions' in data and len(data['positions']) == 3
    assert 'totals' in data
    totals = data['totals']
    # Check net unrealized PnL and pct
    assert pytest.approx(totals['net_unrealized_pnl'], rel=1e-3) == 1075.0
    # 1075 / 13075 * 100 ≈ 8.222
    assert pytest.approx(totals['net_unrealized_pnl_pct'], rel=1e-3) == (1075.0 / 13075.0) * 100.0
    # Annualized metric should exist
    assert 'net_unrealized_anual_pnl_pct' in totals


def test_analytics_strategy_summary_filter():
    rows = build_rows()
    app = build_app_with_dummy(rows)
    client = TestClient(app)
    r = client.get("/analytics/performance/strategy_summary", params={"strategy_name": "default"})
    assert r.status_code == 200
    data = r.json()
    assert len(data['positions']) == 2
    totals = data['totals']
    # default strategy LVL
    assert pytest.approx(totals['total_market_value'], rel=1e-6) == 1100.0 + 975.0
    assert pytest.approx(totals['net_unrealized_pnl'], rel=1e-6) == 100.0 - 25.0


def test_analytics_kpis_endpoint():
    rows = build_rows()
    app = build_app_with_dummy(rows)
    client = TestClient(app)
    r = client.get("/analytics/performance/kpis")
    assert r.status_code == 200
    data = r.json()
    kpis = data['kpis']
    assert kpis['portfolio_market_value'] > 0
    assert 'sharpe_ratio_proxy' in kpis


def test_analytics_top_movers():
    rows = build_rows()
    app = build_app_with_dummy(rows)
    client = TestClient(app)
    r = client.get("/analytics/performance/top_movers", params={"limit": 2})
    assert r.status_code == 200
    movers = r.json()['top_movers']
    assert len(movers) == 2
    # ensure sorting by absolute pnl percent desc
    p0 = abs(float(movers[0]['unrealized_pnl_percent']))
    p1 = abs(float(movers[1]['unrealized_pnl_percent']))
    assert p0 >= p1



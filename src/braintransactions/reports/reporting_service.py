from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.config import BrainConfig
from ..core.logging_config import get_logger
from ..database.connection import DatabaseManager


logger = get_logger("reports")


class ReportingService:
    """
    Lightweight reporting executor for curated SQL files.

    - Uses read-only queries stored under `database/queries/analytics`.
    - Keeps responsibilities narrow: load SQL, execute, return rows.
    - Respects configuration schema search_path handled by DatabaseManager.
    """

    def __init__(self, config: Optional[BrainConfig] = None):
        self.config = config or BrainConfig()
        self.db = DatabaseManager(self.config)
        self.queries_root = (
            Path(__file__).resolve().parents[3]
            / "database"
            / "queries"
            / "analytics"
        )

    def _load_sql(self, filename: str) -> str:
        sql_path = self.queries_root / filename
        if not sql_path.exists():
            raise FileNotFoundError(f"SQL file not found: {sql_path}")
        return sql_path.read_text(encoding="utf-8")

    def run_kpis(self) -> List[Dict[str, Any]]:
        """Return KPI metrics computed in SQL."""
        sql = self._load_sql("kpis.sql")
        return self.db.execute_query(sql)

    def run_strategy_performance(self, strategy_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return strategy performance stats (30d window).

        If strategy_name is provided, we inject a simple filter safely.
        """
        sql = self._load_sql("strategy_performance.sql")
        if strategy_name:
            sql = sql.replace(
                "ORDER BY total_volume DESC;",
                "WHERE strategy_name = %(strategy_name)s\nORDER BY total_volume DESC;",
            )
            return self.db.execute_query(sql, {"strategy_name": strategy_name})
        return self.db.execute_query(sql)

    def run_daily_pnl(self) -> List[Dict[str, Any]]:
        """Return daily P&L performance data for current holdings."""
        sql = self._load_sql("daily_pnl.sql")
        return self.db.execute_query(sql)

    def run_position_performance(self) -> List[Dict[str, Any]]:
        """Return current position performance table data."""
        sql = self._load_sql("position_performance.sql")
        return self.db.execute_query(sql)

    def run_performance_metrics(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return comprehensive performance metrics for dashboard."""
        sql = self._load_sql("performance_metrics.sql")
        
        # Split the multi-query SQL into individual queries
        queries = sql.split(';')[:-1]  # Remove empty last element
        
        # Filter out non-data queries (SET statements, comments, etc.)
        data_queries = []
        for query in queries:
            query_stripped = query.strip()
            if not query_stripped:
                continue
                
            # Get non-comment lines to check actual content
            non_comment_lines = [line.strip() for line in query_stripped.split('\n') 
                               if line.strip() and not line.strip().startswith('--')]
            
            if non_comment_lines:
                first_line = non_comment_lines[0].upper()
                # Include queries that start with WITH or SELECT (actual data queries)
                if first_line.startswith('WITH ') or first_line.startswith('SELECT '):
                    data_queries.append(query)
                    logger.debug(f"Added data query starting with: {first_line[:50]}")
                else:
                    logger.debug(f"Skipped non-data query: {first_line[:50]}")
        
        results = {}
        try:
            # Prepare schema setting for each query
            schema_prefix = "SET search_path TO laxmiyantra, public;\n\n"
            
            # Daily volume trends (first data query)
            if len(data_queries) > 0:
                daily_query = schema_prefix + data_queries[0] + ';'
                logger.info("Executing daily performance query")
                results['daily_performance'] = self.db.execute_query(daily_query)
            
            # Strategy comparison (second data query)  
            if len(data_queries) > 1:
                strategy_query = schema_prefix + data_queries[1] + ';'
                logger.info("Executing strategy comparison query")
                results['strategy_comparison'] = self.db.execute_query(strategy_query)
            
            # Top tickers (third data query)
            if len(data_queries) > 2:
                tickers_query = schema_prefix + data_queries[2] + ';'
                logger.info("Executing top tickers query")
                results['top_tickers'] = self.db.execute_query(tickers_query)
            
            # Hourly patterns (fourth data query)
            if len(data_queries) > 3:
                hourly_query = schema_prefix + data_queries[3] + ';'
                logger.info("Executing hourly patterns query")
                results['hourly_patterns'] = self.db.execute_query(hourly_query)
                
        except Exception as e:
            logger.error(f"Error executing performance metrics: {e}")
            # Return empty results structure
            results = {
                'daily_performance': [],
                'strategy_comparison': [],
                'top_tickers': [],
                'hourly_patterns': []
            }
        
        return results

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Return all dashboard data in single API call.
        
        Aggregates KPIs, strategy performance, and performance metrics
        into a single response for dashboard consumption. Handles errors
        gracefully by returning empty data structures.
        
        Returns:
            Dict containing all dashboard data with status and timestamp
        """
        dashboard_data = {
            "kpis": [],
            "strategy_performance": [],
            "daily_pnl": [],
            "position_performance": [],
            "performance_metrics": {
                "daily_performance": [],
                "strategy_comparison": [],
                "top_tickers": [],
                "hourly_patterns": []
            },
            "generated_at": datetime.now().isoformat(),
            "status": "success",
            "error": None
        }
        
        try:
            # Get KPIs data
            logger.info("Fetching KPIs data for dashboard")
            dashboard_data["kpis"] = self.run_kpis()
            
            # Get strategy performance data
            logger.info("Fetching strategy performance data for dashboard")
            dashboard_data["strategy_performance"] = self.run_strategy_performance()
            
            # Get daily P&L data
            logger.info("Fetching daily P&L data for dashboard")
            dashboard_data["daily_pnl"] = self.run_daily_pnl()
            
            # Get position performance data
            logger.info("Fetching position performance data for dashboard")
            dashboard_data["position_performance"] = self.run_position_performance()
            
            # Get performance metrics (contains multiple result sets)
            logger.info("Fetching performance metrics data for dashboard")
            performance_metrics = self.run_performance_metrics()
            dashboard_data["performance_metrics"] = performance_metrics
            
            logger.info("Dashboard data compiled successfully")
            
        except Exception as e:
            logger.error(f"Error compiling dashboard data: {e}")
            dashboard_data["status"] = "error"
            dashboard_data["error"] = str(e)
            
            # Ensure we have empty structures even on error
            dashboard_data["kpis"] = []
            dashboard_data["strategy_performance"] = []
            dashboard_data["daily_pnl"] = []
            dashboard_data["position_performance"] = []
            dashboard_data["performance_metrics"] = {
                "daily_performance": [],
                "strategy_comparison": [],
                "top_tickers": [],
                "hourly_patterns": []
            }
        
        return dashboard_data



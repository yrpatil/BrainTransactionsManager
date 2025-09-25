"""
Background Monitoring System for BrainTransactionsManager v2.0.0
Blessed by Goddess Laxmi for Infinite Abundance 🙏

Simple, efficient background polling for KPI monitoring and data synchronization.
Focuses on essential monitoring without overengineering.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import time
from .logging_config import get_logger

logger = get_logger("monitoring")


class MonitoringTaskType(Enum):
    """Types of monitoring tasks."""
    PRICE_UPDATE = "price_update"
    PORTFOLIO_SYNC = "portfolio_sync"
    ORDER_RECONCILE = "order_reconcile"
    KPI_CALCULATION = "kpi_calculation"
    HEALTH_CHECK = "health_check"


@dataclass
class MonitoringTask:
    """Monitoring task definition."""
    name: str
    task_type: MonitoringTaskType
    interval_seconds: int
    callback: Callable
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    error_count: int = 0
    success_count: int = 0


class BackgroundMonitor:
    """
    Simple background monitoring system.
    
    Features:
    • Configurable monitoring tasks
    • Automatic task scheduling
    • Error handling and retry logic
    • Performance metrics
    • KPI-focused data updates
    • Simple and reliable
    """
    
    def __init__(self, config, exchange_manager, database_manager):
        """
        Initialize background monitor.
        
        Args:
            config: BrainConfig instance
            exchange_manager: ExchangeManager instance
            database_manager: DatabaseManager instance
        """
        self.config = config
        self.exchange_manager = exchange_manager
        self.database_manager = database_manager
        
        self.tasks: Dict[str, MonitoringTask] = {}
        self.is_running = False
        self.monitor_loop_task: Optional[asyncio.Task] = None
        
        # Performance tracking
        self.total_task_runs = 0
        self.total_errors = 0
        self.start_time: Optional[datetime] = None
        
        # Initialize default tasks
        self._initialize_default_tasks()
    
    def _initialize_default_tasks(self):
        """Initialize default monitoring tasks."""
        # Price update task
        self.register_task(
            "price_updates",
            MonitoringTaskType.PRICE_UPDATE,
            self.config.monitoring.price_poll_interval,
            self._update_prices
        )
        
        # Portfolio synchronization
        self.register_task(
            "portfolio_sync",
            MonitoringTaskType.PORTFOLIO_SYNC,
            self.config.monitoring.portfolio_sync_interval,
            self._sync_portfolio
        )
        
        # Order reconciliation
        self.register_task(
            "order_reconcile",
            MonitoringTaskType.ORDER_RECONCILE,
            self.config.monitoring.order_reconcile_interval,
            self._reconcile_orders
        )
        
        # KPI calculation
        self.register_task(
            "kpi_calculation",
            MonitoringTaskType.KPI_CALCULATION,
            300,  # 5 minutes
            self._calculate_kpis
        )
        
        # System health check
        self.register_task(
            "health_check",
            MonitoringTaskType.HEALTH_CHECK,
            self.config.monitoring.health_check_interval,
            self._system_health_check
        )
        
        logger.info(f"✅ Initialized {len(self.tasks)} monitoring tasks")
    
    def register_task(self, name: str, task_type: MonitoringTaskType, 
                     interval_seconds: int, callback: Callable, enabled: bool = True):
        """
        Register a monitoring task.
        
        Args:
            name: Task identifier
            task_type: Type of monitoring task
            interval_seconds: Task execution interval
            callback: Task callback function
            enabled: Whether task is enabled
        """
        task = MonitoringTask(
            name=name,
            task_type=task_type,
            interval_seconds=interval_seconds,
            callback=callback,
            enabled=enabled,
            next_run=datetime.now() + timedelta(seconds=interval_seconds)
        )
        
        self.tasks[name] = task
        logger.debug(f"📝 Registered monitoring task: {name} (interval: {interval_seconds}s)")
    
    async def start(self):
        """Start background monitoring."""
        if self.is_running:
            logger.warning("Background monitoring already running")
            return
        
        self.is_running = True
        self.start_time = datetime.now()
        
        logger.info("🔄 Starting background monitoring system...")
        
        # Start monitoring loop
        self.monitor_loop_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("✅ Background monitoring started")
    
    async def stop(self):
        """Stop background monitoring."""
        if not self.is_running:
            return
        
        logger.info("⏹️ Stopping background monitoring...")
        
        self.is_running = False
        
        if self.monitor_loop_task:
            self.monitor_loop_task.cancel()
            try:
                await self.monitor_loop_task
            except asyncio.CancelledError:
                pass
        
        logger.info("✅ Background monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        logger.info("🔄 Monitoring loop started")
        
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Check which tasks need to run
                for task in self.tasks.values():
                    if (task.enabled and 
                        task.next_run and 
                        current_time >= task.next_run):
                        
                        # Run task asynchronously
                        asyncio.create_task(self._execute_task(task))
                
                # Sleep for a short interval before next check
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except asyncio.CancelledError:
                logger.info("Monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(10)  # Wait longer on error
        
        logger.info("🔄 Monitoring loop ended")
    
    async def _execute_task(self, task: MonitoringTask):
        """Execute a monitoring task."""
        start_time = time.time()
        
        try:
            logger.debug(f"🔄 Executing task: {task.name}")
            
            # Execute task callback
            await task.callback()
            
            # Update task metrics
            task.last_run = datetime.now()
            task.next_run = task.last_run + timedelta(seconds=task.interval_seconds)
            task.success_count += 1
            self.total_task_runs += 1
            
            execution_time = time.time() - start_time
            logger.debug(f"✅ Task completed: {task.name} ({execution_time:.2f}s)")
            
        except Exception as e:
            logger.error(f"Task error [{task.name}]: {e}")
            
            # Update error metrics
            task.error_count += 1
            self.total_errors += 1
            
            # Schedule retry (with exponential backoff for repeated errors)
            retry_delay = min(task.interval_seconds * (2 ** min(task.error_count, 5)), 3600)  # Max 1 hour
            task.next_run = datetime.now() + timedelta(seconds=retry_delay)
    
    # Task implementations
    
    async def _update_prices(self, price_data: Dict[str, float]):
        """Update prices in database."""
        try:
            for symbol, price in price_data.items():
                query = f"""
                INSERT INTO {self.config.database.schema}.market_data 
                    (ticker, price, volume, timestamp)
                VALUES (%(symbol)s, %(price)s, %(volume)s, CURRENT_TIMESTAMP)
                ON CONFLICT (ticker, timestamp) 
                DO UPDATE SET 
                    price = EXCLUDED.price,
                    volume = EXCLUDED.volume
                """
                
                await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self.database_manager.execute_action(query, price_data)
                )
                
        except Exception as e:
            logger.error(f"Error updating prices: {e}")
    
    async def _sync_portfolio(self):
        """Synchronize portfolio positions with exchange."""
        try:
            # Get positions from exchange
            exchange_positions = await self.exchange_manager.get_positions()
            
            # Get current database positions
            db_positions = await self._get_db_positions()
            
            # Reconcile differences
            reconciled_count = 0
            for exchange_pos in exchange_positions:
                symbol = exchange_pos['symbol']
                quantity = exchange_pos['quantity']
                avg_price = exchange_pos.get('avg_entry_price', 0)
                
                # Find matching DB position
                db_pos = next((p for p in db_positions if p['ticker'] == symbol), None)
                
                if not db_pos or db_pos['quantity'] != quantity:
                    # Update or insert position
                    await self._upsert_position(symbol, quantity, avg_price)
                    reconciled_count += 1
            
            # Remove positions that no longer exist
            exchange_symbols = set(pos['symbol'] for pos in exchange_positions)
            for db_pos in db_positions:
                if db_pos['ticker'] not in exchange_symbols:
                    await self._remove_position(db_pos['ticker'])
                    reconciled_count += 1
            
            if reconciled_count > 0:
                logger.info(f"✅ Portfolio sync: reconciled {reconciled_count} positions")
            
        except Exception as e:
            logger.error(f"Portfolio sync task error: {e}")
            raise
    
    async def _reconcile_orders(self):
        """Reconcile order statuses with exchange."""
        try:
            # Get pending orders from database
            pending_orders = await self._get_pending_orders()
            
            reconciled_count = 0
            for order in pending_orders:
                try:
                    # Get current status from exchange
                    current_status = await self.exchange_manager.get_order_status(order['order_id'])
                    
                    # Update if status changed
                    if current_status['status'] != order['status']:
                        await self._update_order_status(order['order_id'], current_status)
                        reconciled_count += 1
                        
                except Exception as e:
                    logger.warning(f"Failed to reconcile order {order['order_id']}: {e}")
            
            if reconciled_count > 0:
                logger.info(f"✅ Order reconciliation: updated {reconciled_count} orders")
            
        except Exception as e:
            logger.error(f"Order reconciliation task error: {e}")
            raise
    
    async def _calculate_kpis(self):
        """Calculate and update KPIs."""
        try:
            # Get account info
            account_info = await self.exchange_manager.get_account_info()
            
            # Get positions
            positions = await self.exchange_manager.get_positions()
            
            # Calculate KPIs
            kpis = {
                'portfolio_value': account_info.get('portfolio_value', 0),
                'cash_balance': account_info.get('cash', 0),
                'buying_power': account_info.get('buying_power', 0),
                'total_positions': len(positions),
                'total_unrealized_pnl': sum(pos.get('unrealized_pl', 0) for pos in positions),
                'timestamp': datetime.now()
            }
            
            # Store KPIs
            await self._store_kpis(kpis)
            
            logger.debug(f"✅ KPIs calculated: portfolio_value=${kpis['portfolio_value']:.2f}")
            
        except Exception as e:
            logger.error(f"KPI calculation task error: {e}")
            raise
    
    async def _system_health_check(self):
        """Perform system health check."""
        try:
            # Check database health
            db_health = self.database_manager.get_health_status()
            
            # Check exchange health
            exchange_health = await self.exchange_manager.health_check()
            
            # Update system status
            await self._update_system_health({
                'database': db_health,
                'exchanges': exchange_health,
                'monitoring': {
                    'status': 'healthy' if self.is_running else 'stopped',
                    'total_tasks': len(self.tasks),
                    'active_tasks': len([t for t in self.tasks.values() if t.enabled]),
                    'total_runs': self.total_task_runs,
                    'error_rate': self.total_errors / max(1, self.total_task_runs)
                },
                'timestamp': datetime.now()
            })
            
        except Exception as e:
            logger.error(f"Health check task error: {e}")
            raise
    
    # Database helper methods
    
    async def _batch_update_prices(self, price_updates: List[Dict[str, Any]]):
        """Batch update price data."""
        try:
            for price_data in price_updates:
                query = f"""
                INSERT INTO {self.config.database.schema}.ohlc_data 
                    (ticker, timestamp, open, high, low, close, volume)
                VALUES (%(ticker)s, %(timestamp)s, %(open)s, %(high)s, %(low)s, %(close)s, %(volume)s)
                ON CONFLICT (ticker, timestamp, timeframe) 
                DO UPDATE SET 
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    volume = EXCLUDED.volume
                """
                
                await asyncio.get_event_loop().run_in_executor(
                    None, self.database_manager.execute_action, query, price_data
                )
                
        except Exception as e:
            logger.error(f"Error updating prices: {e}")
    
    async def _get_db_positions(self) -> List[Dict[str, Any]]:
        """Get positions from database."""
        query = f"SELECT * FROM {self.config.database.schema}.portfolio_positions"
        return await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.database_manager.execute_query(query)
        )
    
    async def _upsert_position(self, symbol: str, quantity: float, avg_price: float):
        """Insert or update position."""
        query = f"""
        INSERT INTO {self.config.database.schema}.portfolio_positions 
            (strategy_name, ticker, quantity, avg_entry_price, last_updated)
        VALUES ('default', %(symbol)s, %(quantity)s, %(avg_price)s, CURRENT_TIMESTAMP)
        ON CONFLICT (strategy_name, ticker) 
        DO UPDATE SET 
            quantity = EXCLUDED.quantity,
            avg_entry_price = EXCLUDED.avg_entry_price,
            last_updated = EXCLUDED.last_updated
        """
        
        params = {'symbol': symbol, 'quantity': quantity, 'avg_price': avg_price}
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.database_manager.execute_action(query, params)
        )
    
    async def _remove_position(self, symbol: str):
        """Remove position from database."""
        query = f"DELETE FROM {self.config.database.schema}.portfolio_positions WHERE ticker = %(symbol)s"
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.database_manager.execute_action(query, {'symbol': symbol})
        )
    
    async def _get_pending_orders(self) -> List[Dict[str, Any]]:
        """Get pending orders from database."""
        query = f"""
        SELECT * FROM {self.config.database.schema}.order_history 
        WHERE status IN ('submitted', 'pending', 'partially_filled')
        """
        return await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.database_manager.execute_query(query)
        )
    
    async def _update_order_status(self, order_id: str, status_data: Dict[str, Any]):
        """Update order status in database."""
        query = f"""
        UPDATE {self.config.database.schema}.order_history 
        SET status = %(status)s,
            filled_quantity = %(filled_quantity)s,
            filled_avg_price = %(filled_avg_price)s,
            filled_at = %(filled_at)s
        WHERE order_id = %(order_id)s
        """
        
        params = {
            'order_id': order_id,
            'status': status_data.get('status'),
            'filled_quantity': status_data.get('filled_quantity', 0),
            'filled_avg_price': status_data.get('filled_avg_price', 0),
            'filled_at': status_data.get('filled_at')
        }
        
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.database_manager.execute_action(query, params)
        )
    
    async def _store_kpis(self, kpis: Dict[str, Any]):
        """Store KPIs in database."""
        # This could be expanded to store in a dedicated KPIs table
        # For now, we'll update system status
        await self._update_system_status('kpis', True, f"Portfolio: ${kpis['portfolio_value']:.2f}")
    
    async def _update_system_health(self, health_data: Dict[str, Any]):
        """Update system health status."""
        await self._update_system_status('monitoring', True, "Background monitoring active")
    
    async def _update_system_status(self, component: str, is_active: bool, message: str):
        """Update system status table."""
        try:
            query = f"""
            INSERT INTO {self.config.database.schema}.system_status 
                (component_name, is_active, status_message, last_heartbeat, updated_at)
            VALUES (%(component)s, %(is_active)s, %(message)s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT (component_name) 
            DO UPDATE SET 
                is_active = EXCLUDED.is_active,
                status_message = EXCLUDED.status_message,
                last_heartbeat = EXCLUDED.last_heartbeat,
                updated_at = EXCLUDED.updated_at
            """
            
            params = {
                'component': component,
                'is_active': is_active,
                'message': message
            }
            
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.database_manager.execute_action(query, params)
            )
            
        except Exception as e:
            logger.error(f"Error updating system status: {e}")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status."""
        uptime = None
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
        
        task_status = {}
        for name, task in self.tasks.items():
            task_status[name] = {
                'enabled': task.enabled,
                'interval_seconds': task.interval_seconds,
                'last_run': task.last_run.isoformat() if task.last_run else None,
                'next_run': task.next_run.isoformat() if task.next_run else None,
                'success_count': task.success_count,
                'error_count': task.error_count,
                'success_rate': task.success_count / max(1, task.success_count + task.error_count)
            }
        
        return {
            'is_running': self.is_running,
            'uptime_seconds': uptime,
            'total_tasks': len(self.tasks),
            'active_tasks': len([t for t in self.tasks.values() if t.enabled]),
            'total_runs': self.total_task_runs,
            'total_errors': self.total_errors,
            'error_rate': self.total_errors / max(1, self.total_task_runs),
            'tasks': task_status,
            'timestamp': datetime.now().isoformat()
        }

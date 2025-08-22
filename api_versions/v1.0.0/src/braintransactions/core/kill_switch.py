"""
Kill Switch Mixin for BrainTransactionsManager
Blessed by Goddess Laxmi for Infinite Abundance 🙏

Provides emergency shutdown capabilities for all transaction modules.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from .exceptions import KillSwitchActiveError

logger = logging.getLogger(__name__)

class KillSwitchMixin:
    """
    Mixin class that provides kill switch functionality to transaction managers.
    
    Features:
    • Emergency shutdown capabilities
    • Graceful degradation when activated
    • Reason tracking for audit purposes
    • Read-only operations during kill switch
    • Remote activation support for Telegram/API integration
    """
    
    def __init__(self):
        """Initialize kill switch state."""
        self._kill_switch_active = False
        self._kill_switch_reason = None
        self._kill_switch_activated_at = None
        self._kill_switch_activated_by = None
    
    def activate_kill_switch(self, reason: str = "Manual activation", 
                           activated_by: Optional[str] = None) -> bool:
        """
        Activate the kill switch to stop all write operations.
        
        Args:
            reason: Reason for activation
            activated_by: Who/what activated the kill switch
            
        Returns:
            bool: True if successful
        """
        try:
            self._kill_switch_active = True
            self._kill_switch_reason = reason
            self._kill_switch_activated_at = datetime.now()
            self._kill_switch_activated_by = activated_by or "Unknown"
            
            logger.warning(f"🚨 KILL SWITCH ACTIVATED: {reason}")
            logger.warning(f"   Activated by: {self._kill_switch_activated_by}")
            logger.warning(f"   Timestamp: {self._kill_switch_activated_at}")
            logger.warning("   All write operations are now BLOCKED")
            
            return True
            
        except Exception as e:
            logger.error(f"Error activating kill switch: {str(e)}")
            return False
    
    def deactivate_kill_switch(self, reason: str = "Manual deactivation",
                             deactivated_by: Optional[str] = None) -> bool:
        """
        Deactivate the kill switch to resume normal operations.
        
        Args:
            reason: Reason for deactivation
            deactivated_by: Who/what deactivated the kill switch
            
        Returns:
            bool: True if successful
        """
        try:
            if not self._kill_switch_active:
                logger.info("Kill switch is already inactive")
                return True
            
            # Store deactivation info for audit
            previous_reason = self._kill_switch_reason
            previous_activation_time = self._kill_switch_activated_at
            
            self._kill_switch_active = False
            self._kill_switch_reason = None
            self._kill_switch_activated_at = None
            self._kill_switch_activated_by = None
            
            logger.info(f"✅ KILL SWITCH DEACTIVATED: {reason}")
            logger.info(f"   Deactivated by: {deactivated_by or 'Unknown'}")
            logger.info(f"   Previous activation reason: {previous_reason}")
            logger.info(f"   Was active for: {datetime.now() - previous_activation_time if previous_activation_time else 'Unknown'}")
            logger.info("   Normal operations resumed")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating kill switch: {str(e)}")
            return False
    
    def is_kill_switch_active(self) -> bool:
        """Check if kill switch is currently active."""
        return self._kill_switch_active
    
    def get_kill_switch_status(self) -> Dict[str, Any]:
        """
        Get detailed kill switch status information.
        
        Returns:
            Dict with kill switch status details
        """
        return {
            'active': self._kill_switch_active,
            'reason': self._kill_switch_reason,
            'activated_at': self._kill_switch_activated_at.isoformat() if self._kill_switch_activated_at else None,
            'activated_by': self._kill_switch_activated_by,
            'uptime_seconds': (datetime.now() - self._kill_switch_activated_at).total_seconds() 
                             if self._kill_switch_activated_at else None
        }
    
    def check_kill_switch_and_raise(self, operation: str = "operation") -> None:
        """
        Check kill switch status and raise exception if active.
        
        Args:
            operation: Description of the operation being attempted
            
        Raises:
            KillSwitchActiveError: If kill switch is active
        """
        if self._kill_switch_active:
            message = f"{operation.capitalize()} blocked - kill switch active: {self._kill_switch_reason}"
            logger.warning(message)
            raise KillSwitchActiveError(message, operation)
    
    def emergency_stop(self, reason: str = "Emergency stop", 
                      stopped_by: Optional[str] = None) -> bool:
        """
        Emergency stop with immediate kill switch activation.
        
        Args:
            reason: Emergency stop reason
            stopped_by: Who initiated the emergency stop
            
        Returns:
            bool: True if successful
        """
        try:
            logger.critical(f"🚨 EMERGENCY STOP INITIATED: {reason}")
            
            # Activate kill switch
            success = self.activate_kill_switch(f"EMERGENCY: {reason}", stopped_by)
            
            if success:
                logger.critical("🚨 EMERGENCY STOP COMPLETED - System is now in safe mode")
                
                # Call emergency cleanup if implemented by subclass
                if hasattr(self, '_emergency_cleanup'):
                    try:
                        self._emergency_cleanup()
                        logger.info("Emergency cleanup completed")
                    except Exception as e:
                        logger.error(f"Error during emergency cleanup: {str(e)}")
            
            return success
            
        except Exception as e:
            logger.critical(f"CRITICAL ERROR during emergency stop: {str(e)}")
            return False
    
    def with_kill_switch_check(self, operation_name: str):
        """
        Decorator factory for methods that should check kill switch status.
        
        Args:
            operation_name: Name of the operation for logging
            
        Returns:
            Decorator function
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                self.check_kill_switch_and_raise(operation_name)
                return func(*args, **kwargs)
            return wrapper
        return decorator

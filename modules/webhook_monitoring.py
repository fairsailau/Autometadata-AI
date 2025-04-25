"""
Webhook monitoring module for Box webhooks.
This module provides functionality for monitoring Box webhooks.
"""

import os
import json
import logging
import threading
import time
import requests
import streamlit as st
from typing import Dict, Any, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebhookMonitor:
    """
    Monitor for Box webhooks.
    """
    
    def __init__(self, client=None):
        """
        Initialize the webhook monitor.
        
        Args:
            client: Box client instance
        """
        self.client = client
        self.monitoring_thread = None
        self.is_monitoring = False
        self.webhook_status = {}
        self.last_check_time = None
        self.check_interval = 60  # seconds
    
    def start_monitoring(self) -> bool:
        """
        Start monitoring webhooks.
        
        Returns:
            bool: True if monitoring was started successfully, False otherwise
        """
        try:
            if self.is_monitoring:
                logger.warning("Webhook monitoring is already running")
                return True
            
            # Start monitoring in a separate thread
            self.monitoring_thread = threading.Thread(target=self._monitor_webhooks)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            
            self.is_monitoring = True
            logger.info("Webhook monitoring started")
            return True
        
        except Exception as e:
            logger.error(f"Error starting webhook monitoring: {str(e)}", exc_info=True)
            return False
    
    def stop_monitoring(self) -> bool:
        """
        Stop monitoring webhooks.
        
        Returns:
            bool: True if monitoring was stopped successfully, False otherwise
        """
        try:
            if not self.is_monitoring:
                logger.warning("Webhook monitoring is not running")
                return True
            
            self.is_monitoring = False
            
            # Wait for monitoring thread to stop
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5)
            
            logger.info("Webhook monitoring stopped")
            return True
        
        except Exception as e:
            logger.error(f"Error stopping webhook monitoring: {str(e)}", exc_info=True)
            return False
    
    def _monitor_webhooks(self):
        """Monitor webhooks."""
        try:
            while self.is_monitoring:
                # Check webhooks
                self._check_webhooks()
                
                # Sleep for check interval
                time.sleep(self.check_interval)
        
        except Exception as e:
            logger.error(f"Error in webhook monitoring thread: {str(e)}", exc_info=True)
            self.is_monitoring = False
    
    def _check_webhooks(self):
        """Check webhooks."""
        try:
            # Check if client is available
            if not self.client:
                logger.warning("No Box client available")
                return
            
            # Get webhooks
            from modules.webhook_integration import BoxWebhookManager
            webhook_manager = BoxWebhookManager(self.client)
            webhooks = webhook_manager.list_webhooks()
            
            # Update webhook status
            for webhook in webhooks:
                webhook_id = webhook["id"]
                
                # Check webhook status
                status = self._check_webhook_status(webhook)
                
                # Update status
                self.webhook_status[webhook_id] = {
                    "webhook": webhook,
                    "status": status,
                    "last_check_time": time.time()
                }
            
            # Remove old webhooks
            webhook_ids = [webhook["id"] for webhook in webhooks]
            for webhook_id in list(self.webhook_status.keys()):
                if webhook_id not in webhook_ids:
                    self.webhook_status.pop(webhook_id)
            
            # Update last check time
            self.last_check_time = time.time()
            
            logger.info(f"Checked {len(webhooks)} webhooks")
        
        except Exception as e:
            logger.error(f"Error checking webhooks: {str(e)}", exc_info=True)
    
    def _check_webhook_status(self, webhook: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check webhook status.
        
        Args:
            webhook: Webhook information
            
        Returns:
            dict: Webhook status
        """
        try:
            # Get webhook address
            address = webhook["address"]
            
            # Check if address is reachable
            try:
                response = requests.head(address, timeout=5)
                is_reachable = response.status_code < 400
            except:
                is_reachable = False
            
            # Get webhook events
            events = self._get_webhook_events(webhook["id"])
            
            # Return status
            return {
                "is_reachable": is_reachable,
                "events": events,
                "last_event_time": max([event["time"] for event in events]) if events else None
            }
        
        except Exception as e:
            logger.error(f"Error checking webhook status: {str(e)}", exc_info=True)
            return {
                "is_reachable": False,
                "events": [],
                "last_event_time": None,
                "error": str(e)
            }
    
    def _get_webhook_events(self, webhook_id: str) -> List[Dict[str, Any]]:
        """
        Get webhook events.
        
        Args:
            webhook_id: Webhook ID
            
        Returns:
            list: Webhook events
        """
        try:
            # In a real implementation, this would query the Box API for webhook events
            # For now, we'll return an empty list
            return []
        
        except Exception as e:
            logger.error(f"Error getting webhook events: {str(e)}", exc_info=True)
            return []
    
    def get_webhook_status(self, webhook_id: str = None) -> Dict[str, Any]:
        """
        Get webhook status.
        
        Args:
            webhook_id: Webhook ID or None for all webhooks
            
        Returns:
            dict: Webhook status
        """
        if webhook_id:
            return self.webhook_status.get(webhook_id, {})
        else:
            return self.webhook_status
    
    def get_webhook_health(self) -> Dict[str, Any]:
        """
        Get overall webhook health.
        
        Returns:
            dict: Webhook health
        """
        try:
            # Count webhooks
            total_webhooks = len(self.webhook_status)
            
            # Count reachable webhooks
            reachable_webhooks = sum(
                1 for status in self.webhook_status.values()
                if status.get("status", {}).get("is_reachable", False)
            )
            
            # Count webhooks with recent events
            recent_events_threshold = time.time() - (24 * 60 * 60)  # 24 hours
            webhooks_with_recent_events = sum(
                1 for status in self.webhook_status.values()
                if status.get("status", {}).get("last_event_time", 0) > recent_events_threshold
            )
            
            # Calculate health percentage
            health_percentage = (reachable_webhooks / total_webhooks * 100) if total_webhooks > 0 else 0
            
            # Determine health status
            if health_percentage >= 90:
                health_status = "Healthy"
            elif health_percentage >= 70:
                health_status = "Warning"
            else:
                health_status = "Unhealthy"
            
            # Return health
            return {
                "total_webhooks": total_webhooks,
                "reachable_webhooks": reachable_webhooks,
                "webhooks_with_recent_events": webhooks_with_recent_events,
                "health_percentage": health_percentage,
                "health_status": health_status,
                "last_check_time": self.last_check_time
            }
        
        except Exception as e:
            logger.error(f"Error getting webhook health: {str(e)}", exc_info=True)
            return {
                "total_webhooks": 0,
                "reachable_webhooks": 0,
                "webhooks_with_recent_events": 0,
                "health_percentage": 0,
                "health_status": "Unknown",
                "last_check_time": None,
                "error": str(e)
            }


class WebhookMonitoringInterface:
    """
    Interface for monitoring Box webhooks.
    """
    
    def __init__(self, client=None):
        """
        Initialize the webhook monitoring interface.
        
        Args:
            client: Box client instance
        """
        self.client = client
        self.monitor = WebhookMonitor(client)
    
    def render_webhook_monitoring(self):
        """Render the webhook monitoring interface."""
        try:
            st.subheader("Webhook Monitoring")
            st.write("Monitor the status of your Box webhooks.")
            
            # Check if client is available
            if "client" not in st.session_state or not st.session_state.client:
                st.warning("Please authenticate with Box to monitor webhooks.")
                return
            
            # Start/stop monitoring
            col1, col2 = st.columns(2)
            
            with col1:
                if self.monitor.is_monitoring:
                    if st.button("Stop Monitoring", use_container_width=True):
                        if self.monitor.stop_monitoring():
                            st.success("Webhook monitoring stopped successfully")
                            st.rerun()
                        else:
                            st.error("Failed to stop webhook monitoring")
                else:
                    if st.button("Start Monitoring", use_container_width=True):
                        if self.monitor.start_monitoring():
                            st.success("Webhook monitoring started successfully")
                            st.rerun()
                        else:
                            st.error("Failed to start webhook monitoring")
            
            with col2:
                if st.button("Refresh Status", use_container_width=True):
                    self.monitor._check_webhooks()
                    st.rerun()
            
            # Display webhook health
            st.write("---")
            st.write("Webhook Health")
            
            health = self.monitor.get_webhook_health()
            
            # Health status
            if health["health_status"] == "Healthy":
                st.success(f"Webhooks are healthy ({health['health_percentage']:.1f}%)")
            elif health["health_status"] == "Warning":
                st.warning(f"Webhooks need attention ({health['health_percentage']:.1f}%)")
            elif health["health_status"] == "Unhealthy":
                st.error(f"Webhooks are unhealthy ({health['health_percentage']:.1f}%)")
            else:
                st.info("Webhook health is unknown")
            
            # Health details
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Webhooks", health["total_webhooks"])
            
            with col2:
                st.metric("Reachable Webhooks", health["reachable_webhooks"])
            
            with col3:
                st.metric("Webhooks with Recent Events", health["webhooks_with_recent_events"])
            
            # Last check time
            if health["last_check_time"]:
                st.write(f"Last checked: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(health['last_check_time']))}")
            
            # Display webhook status
            st.write("---")
            st.write("Webhook Status")
            
            # Get webhooks
            from modules.webhook_integration import BoxWebhookManager
            webhook_manager = BoxWebhookManager(st.session_state.client)
            webhooks = webhook_manager.list_webhooks()
            
            if webhooks:
                for webhook in webhooks:
                    webhook_id = webhook["id"]
                    status = self.monitor.get_webhook_status(webhook_id)
                    
                    with st.expander(f"Webhook {webhook_id}"):
                        # Webhook details
                        st.write(f"**Target:** {webhook['target']['type']} {webhook['target']['id']}")
                        st.write(f"**Address:** {webhook['address']}")
                        st.write(f"**Triggers:** {', '.join(webhook['triggers'])}")
                        
                        # Status
                        st.write("---")
                        st.write("Status")
                        
                        if status:
                            status_data = status.get("status", {})
                            
                            # Reachability
                            if status_data.get("is_reachable", False):
                                st.success("Webhook endpoint is reachable")
                            else:
                                st.error("Webhook endpoint is not reachable")
                            
                            # Events
                            events = status_data.get("events", [])
                            if events:
                                st.write(f"Recent events: {len(events)}")
                                
                                for event in events:
                                    st.write(f"- {event['type']} at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event['time']))}")
                            else:
                                st.info("No recent events")
                            
                            # Last check time
                            if status.get("last_check_time"):
                                st.write(f"Last checked: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(status['last_check_time']))}")
                        else:
                            st.warning("No status information available")
                        
                        # Actions
                        st.write("---")
                        st.write("Actions")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("Test Webhook", key=f"test_webhook_{webhook_id}", use_container_width=True):
                                st.info("Webhook test not implemented yet")
                        
                        with col2:
                            if st.button("Delete Webhook", key=f"delete_webhook_{webhook_id}", use_container_width=True):
                                if webhook_manager.delete_webhook(webhook_id):
                                    st.success(f"Webhook {webhook_id} deleted successfully")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to delete webhook {webhook_id}")
            else:
                st.info("No webhooks found.")
        
        except Exception as e:
            logger.error(f"Error rendering webhook monitoring: {str(e)}", exc_info=True)
            st.error(f"Error rendering webhook monitoring: {str(e)}")


# Global instance
_webhook_monitor = None

def get_webhook_monitor(client=None) -> WebhookMonitor:
    """
    Get the global webhook monitor instance.
    
    Args:
        client: Box client instance
        
    Returns:
        WebhookMonitor: Global webhook monitor instance
    """
    global _webhook_monitor
    
    if _webhook_monitor is None:
        _webhook_monitor = WebhookMonitor(client)
    elif client is not None:
        _webhook_monitor.client = client
    
    return _webhook_monitor

def render_webhook_monitoring():
    """
    Standalone wrapper for render_webhook_monitoring.
    """
    logger.info("Calling render_webhook_monitoring standalone function")
    interface = WebhookMonitoringInterface()
    
    # Get client from session state
    if "client" in st.session_state:
        interface.client = st.session_state.client
        interface.monitor.client = st.session_state.client
    
    return interface.render_webhook_monitoring()

"""
Integration module for automated workflow.
This module integrates the automated workflow components with the existing application.
"""

import os
import json
import logging
import threading
import streamlit as st
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomatedWorkflowManager:
    """
    Manager for automated workflow integration.
    """
    
    def __init__(self, client=None):
        """
        Initialize the automated workflow manager.
        
        Args:
            client: Box client instance
        """
        self.client = client
        self.event_stream_running = False
        self.lock = threading.RLock()
    
    def set_client(self, client):
        """
        Set the Box client.
        
        Args:
            client: Box client instance
        """
        self.client = client
        
        # Update client in components
        self._update_client_in_components()
    
    def _update_client_in_components(self):
        """Update client in all components."""
        try:
            # Import components
            from modules.event_stream import get_webhook_manager, get_event_processor
            from modules.automated_categorization import get_automated_categorization
            from modules.template_processing import get_automated_processing_service
            from modules.configuration_interface import get_configuration_interface
            
            # Update client in components
            get_webhook_manager(self.client)
            get_event_processor(self.client)
            get_automated_categorization(self.client)
            get_automated_processing_service(self.client)
            get_configuration_interface(self.client)
        
        except Exception as e:
            logger.error(f"Error updating client in components: {str(e)}")
    
    def initialize_automated_workflow(self):
        """Initialize automated workflow components."""
        try:
            # Import configuration
            from modules.configuration_interface import get_automated_workflow_config
            
            # Get configuration
            config = get_automated_workflow_config()
            
            # Check if automated workflow is enabled
            if not config.is_enabled():
                logger.info("Automated workflow is disabled")
                return False
            
            # Initialize components
            self._initialize_event_stream(config)
            self._initialize_event_processors(config)
            self._register_webhooks(config)
            
            logger.info("Automated workflow initialized")
            return True
        
        except Exception as e:
            logger.error(f"Error initializing automated workflow: {str(e)}")
            return False
    
    def _initialize_event_stream(self, config):
        """
        Initialize event stream components.
        
        Args:
            config: Automated workflow configuration
        """
        try:
            # Import event stream module
            from modules.event_stream import start_event_stream
            
            # Get webhook port
            port = config.get_webhook_port()
            
            # Start event stream
            start_event_stream(self.client, port)
            
            self.event_stream_running = True
            logger.info(f"Event stream started on port {port}")
        
        except Exception as e:
            logger.error(f"Error initializing event stream: {str(e)}")
            self.event_stream_running = False
    
    def _initialize_event_processors(self, config):
        """
        Initialize event processors.
        
        Args:
            config: Automated workflow configuration
        """
        try:
            # Import components
            from modules.event_stream import get_event_processor
            from modules.automated_categorization import process_file_upload_event
            
            # Get event processor
            event_processor = get_event_processor(self.client)
            
            # Register processors for event types
            event_processor.register_processor('FILE.UPLOADED', process_file_upload_event)
            event_processor.register_processor('FILE.COPIED', process_file_upload_event)
            event_processor.register_processor('FILE.MOVED', process_file_upload_event)
            
            logger.info("Event processors initialized")
        
        except Exception as e:
            logger.error(f"Error initializing event processors: {str(e)}")
    
    def _register_webhooks(self, config):
        """
        Register webhooks for monitored folders.
        
        Args:
            config: Automated workflow configuration
        """
        try:
            # Import webhook manager
            from modules.event_stream import get_webhook_manager
            
            # Get webhook manager
            webhook_manager = get_webhook_manager(self.client)
            
            # Get monitored folders
            monitored_folders = config.get_monitored_folders()
            
            if not monitored_folders:
                logger.warning("No folders configured for monitoring")
                return
            
            # Get webhook URL
            webhook_port = config.get_webhook_port()
            webhook_url = f"https://your-server-address:{webhook_port}/webhook"
            
            # Register webhooks for each folder
            for folder in monitored_folders:
                folder_id = folder.get('id')
                
                if folder_id:
                    webhook_id = webhook_manager.register_webhook(folder_id, webhook_url)
                    
                    if webhook_id:
                        logger.info(f"Registered webhook for folder {folder_id}: {webhook_id}")
                    else:
                        logger.warning(f"Failed to register webhook for folder {folder_id}")
            
            logger.info("Webhooks registered")
        
        except Exception as e:
            logger.error(f"Error registering webhooks: {str(e)}")
    
    def shutdown_automated_workflow(self):
        """Shutdown automated workflow components."""
        try:
            # Import event stream module
            from modules.event_stream import stop_event_stream
            
            # Stop event stream
            stop_event_stream()
            
            self.event_stream_running = False
            logger.info("Automated workflow shutdown")
            
            return True
        
        except Exception as e:
            logger.error(f"Error shutting down automated workflow: {str(e)}")
            return False
    
    def is_event_stream_running(self):
        """
        Check if event stream is running.
        
        Returns:
            bool: True if running, False otherwise
        """
        return self.event_stream_running


# Global instance
_workflow_manager = None

def get_workflow_manager(client=None) -> AutomatedWorkflowManager:
    """
    Get the global workflow manager instance.
    
    Args:
        client: Box client instance
        
    Returns:
        AutomatedWorkflowManager: Global workflow manager instance
    """
    global _workflow_manager
    
    if _workflow_manager is None:
        _workflow_manager = AutomatedWorkflowManager(client)
    elif client is not None:
        _workflow_manager.set_client(client)
    
    return _workflow_manager

def initialize_automated_workflow(client=None):
    """
    Initialize automated workflow components.
    
    Args:
        client: Box client instance
        
    Returns:
        bool: True if initialized, False otherwise
    """
    # Get workflow manager
    workflow_manager = get_workflow_manager(client)
    
    # Initialize automated workflow
    return workflow_manager.initialize_automated_workflow()

def shutdown_automated_workflow():
    """
    Shutdown automated workflow components.
    
    Returns:
        bool: True if shutdown, False otherwise
    """
    # Get workflow manager
    workflow_manager = get_workflow_manager()
    
    # Shutdown automated workflow
    return workflow_manager.shutdown_automated_workflow()

def is_event_stream_running():
    """
    Check if event stream is running.
    
    Returns:
        bool: True if running, False otherwise
    """
    # Get workflow manager
    workflow_manager = get_workflow_manager()
    
    # Check if event stream is running
    return workflow_manager.is_event_stream_running()

"""
Event stream module for automated workflow.
This module provides webhook handling for Box event stream.
"""

import os
import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Union
from flask import Flask, request, jsonify
import requests
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
webhook_server = None
webhook_thread = None
is_running = False
event_handlers = {}

class WebhookServer:
    """
    Webhook server for Box event stream.
    """
    
    def __init__(self, port=5000, client=None):
        """
        Initialize the webhook server.
        
        Args:
            port: Port to listen on
            client: Box client instance
        """
        self.port = port
        self.client = client
        self.app = Flask(__name__)
        self.setup_routes()
        self.server_thread = None
        self.is_running = False
        
        # Load configuration
        from modules.configuration_interface import get_automated_workflow_config
        self.config = get_automated_workflow_config()
        
        logger.info(f"Webhook server initialized on port {port}")
    
    def setup_routes(self):
        """Set up Flask routes."""
        
        @self.app.route('/webhook', methods=['GET'])
        def webhook_get():
            """Handle GET requests to webhook endpoint."""
            logger.info("Received GET request to webhook endpoint")
            return jsonify({
                "status": "ok",
                "message": "Box webhook endpoint is running",
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/webhook', methods=['POST'])
        def webhook_post():
            """Handle POST requests to webhook endpoint."""
            try:
                # Log request
                logger.info("Received POST request to webhook endpoint")
                
                # Get request data
                data = request.json
                logger.info(f"Webhook data: {json.dumps(data)}")
                
                # Verify webhook signature if available
                if not self.verify_webhook_signature(request):
                    logger.warning("Invalid webhook signature")
                    return jsonify({
                        "status": "error",
                        "message": "Invalid webhook signature"
                    }), 403
                
                # Process webhook event
                self.process_webhook_event(data)
                
                # Return success response
                return jsonify({
                    "status": "ok",
                    "message": "Webhook processed successfully",
                    "timestamp": datetime.now().isoformat()
                })
            
            except Exception as e:
                logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
                return jsonify({
                    "status": "error",
                    "message": f"Error processing webhook: {str(e)}"
                }), 500
    
    def verify_webhook_signature(self, request):
        """
        Verify webhook signature.
        
        Args:
            request: Flask request object
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        # Get signature from headers
        signature = request.headers.get('box-signature-primary')
        
        # If no signature is provided, assume it's valid (for testing)
        if not signature:
            logger.warning("No webhook signature provided, skipping verification")
            return True
        
        # Get webhook primary key from configuration
        webhook_key = self.config.config.get("webhook_primary_key")
        
        # If no key is configured, assume it's valid (for testing)
        if not webhook_key:
            logger.warning("No webhook key configured, skipping verification")
            return True
        
        try:
            # Verify signature
            import hmac
            import hashlib
            
            # Get request body as bytes
            body = request.get_data()
            
            # Calculate expected signature
            expected_signature = hmac.new(
                webhook_key.encode('utf-8'),
                body,
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(signature, expected_signature)
        
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {str(e)}", exc_info=True)
            return False
    
    def process_webhook_event(self, data):
        """
        Process webhook event.
        
        Args:
            data: Webhook event data
        """
        try:
            # Check if data contains trigger field
            if 'trigger' not in data:
                logger.warning("Webhook data does not contain trigger field")
                return
            
            # Get trigger
            trigger = data['trigger']
            
            # Get source
            source = data.get('source', {})
            
            # Get source type
            source_type = source.get('type')
            
            # Get source ID
            source_id = source.get('id')
            
            # Log event
            logger.info(f"Processing webhook event: {trigger} for {source_type} {source_id}")
            
            # Check if we have a handler for this trigger
            if trigger in event_handlers:
                # Call handler
                event_handlers[trigger](data, self.client)
            else:
                logger.warning(f"No handler for trigger: {trigger}")
        
        except Exception as e:
            logger.error(f"Error processing webhook event: {str(e)}", exc_info=True)
    
    def start(self):
        """Start the webhook server."""
        if self.is_running:
            logger.warning("Webhook server is already running")
            return
        
        def run_server():
            """Run the Flask server."""
            try:
                # Run Flask app
                self.app.run(
                    host='0.0.0.0',  # Listen on all interfaces
                    port=self.port,
                    debug=False,
                    use_reloader=False,
                    threaded=True
                )
            except Exception as e:
                logger.error(f"Error running webhook server: {str(e)}", exc_info=True)
        
        # Start server in a separate thread
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Mark as running
        self.is_running = True
        
        logger.info(f"Webhook server started on port {self.port}")
    
    def stop(self):
        """Stop the webhook server."""
        if not self.is_running:
            logger.warning("Webhook server is not running")
            return
        
        try:
            # Shutdown Flask server
            requests.get(f"http://localhost:{self.port}/shutdown")
        except:
            # If shutdown endpoint doesn't work, try to kill the thread
            if self.server_thread and self.server_thread.is_alive():
                # This is not a clean shutdown, but it works
                import ctypes
                ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_long(self.server_thread.ident),
                    ctypes.py_object(SystemExit)
                )
        
        # Mark as not running
        self.is_running = False
        
        logger.info("Webhook server stopped")


def register_event_handler(trigger, handler):
    """
    Register an event handler for a specific trigger.
    
    Args:
        trigger: Event trigger
        handler: Event handler function
    """
    global event_handlers
    
    event_handlers[trigger] = handler
    logger.info(f"Registered handler for trigger: {trigger}")


def start_webhook_server(port=None, client=None):
    """
    Start the webhook server.
    
    Args:
        port: Port to listen on
        client: Box client instance
        
    Returns:
        bool: True if server was started, False otherwise
    """
    global webhook_server, webhook_thread, is_running
    
    # If server is already running, return
    if is_running:
        logger.warning("Webhook server is already running")
        return True
    
    try:
        # Get configuration
        from modules.configuration_interface import get_automated_workflow_config
        config = get_automated_workflow_config()
        
        # Get port from configuration if not provided
        if port is None:
            port = config.get_webhook_port()
        
        # Create webhook server
        webhook_server = WebhookServer(port=port, client=client)
        
        # Start server
        webhook_server.start()
        
        # Mark as running
        is_running = True
        
        # Register default event handlers
        register_default_event_handlers()
        
        logger.info(f"Webhook server started on port {port}")
        return True
    
    except Exception as e:
        logger.error(f"Error starting webhook server: {str(e)}", exc_info=True)
        return False


def stop_webhook_server():
    """
    Stop the webhook server.
    
    Returns:
        bool: True if server was stopped, False otherwise
    """
    global webhook_server, webhook_thread, is_running
    
    # If server is not running, return
    if not is_running:
        logger.warning("Webhook server is not running")
        return True
    
    try:
        # Stop server
        if webhook_server:
            webhook_server.stop()
        
        # Mark as not running
        is_running = False
        
        logger.info("Webhook server stopped")
        return True
    
    except Exception as e:
        logger.error(f"Error stopping webhook server: {str(e)}", exc_info=True)
        return False


def is_webhook_server_running():
    """
    Check if webhook server is running.
    
    Returns:
        bool: True if server is running, False otherwise
    """
    global is_running
    return is_running


def register_default_event_handlers():
    """Register default event handlers."""
    
    # FILE.UPLOADED handler
    def handle_file_uploaded(data, client):
        """
        Handle FILE.UPLOADED event.
        
        Args:
            data: Webhook event data
            client: Box client instance
        """
        try:
            # Get source
            source = data.get('source', {})
            
            # Get source type
            source_type = source.get('type')
            
            # Get source ID
            source_id = source.get('id')
            
            # Log event
            logger.info(f"Handling FILE.UPLOADED event for {source_type} {source_id}")
            
            # Check if source is a file
            if source_type != 'file':
                logger.warning(f"Unexpected source type: {source_type}")
                return
            
            # Get file
            file = client.file(file_id=source_id).get()
            
            # Log file info
            logger.info(f"File uploaded: {file.name} ({file.id})")
            
            # Get parent folder
            parent_folder = file.parent
            
            # Check if parent folder is in monitored folders
            from modules.configuration_interface import get_automated_workflow_config
            config = get_automated_workflow_config()
            
            monitored_folders = config.get_monitored_folders()
            monitored_folder_ids = [folder.get('id') for folder in monitored_folders]
            
            if parent_folder.id not in monitored_folder_ids:
                logger.info(f"Parent folder {parent_folder.id} is not monitored, skipping")
                return
            
            # Process file
            logger.info(f"Processing file {file.id} in monitored folder {parent_folder.id}")
            
            # TODO: Implement file processing logic
            # This would typically involve:
            # 1. Categorizing the document
            # 2. Extracting metadata
            # 3. Applying metadata to the file
            
            logger.info(f"File {file.id} processed successfully")
        
        except Exception as e:
            logger.error(f"Error handling FILE.UPLOADED event: {str(e)}", exc_info=True)
    
    # Register handlers
    register_event_handler('FILE.UPLOADED', handle_file_uploaded)
    register_event_handler('FILE.COPIED', handle_file_uploaded)  # Use same handler for copied files


def test_webhook_connection(url=None):
    """
    Test webhook connection.
    
    Args:
        url: Webhook URL to test
        
    Returns:
        dict: Test result
    """
    try:
        # Get configuration
        from modules.configuration_interface import get_automated_workflow_config
        config = get_automated_workflow_config()
        
        # Get webhook URL
        if url is None:
            # Use streamlit server URL if available
            if "server" in st.config and "baseUrlPath" in st.config.server:
                base_url = st.config.server.baseUrlPath
                port = config.get_webhook_port()
                url = f"{base_url}:{port}/webhook"
            else:
                # Use localhost URL as fallback
                port = config.get_webhook_port()
                url = f"http://localhost:{port}/webhook"
        
        # Make request to webhook URL
        response = requests.get(url, timeout=5)
        
        # Check response
        if response.status_code == 200:
            return {
                "status": "success",
                "message": "Webhook endpoint is accessible",
                "url": url,
                "response": response.json()
            }
        else:
            return {
                "status": "error",
                "message": f"Webhook endpoint returned status code: {response.status_code}",
                "url": url,
                "response": response.text
            }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error testing webhook connection: {str(e)}",
            "url": url
        }


def setup_streamlit_webhook(port=None):
    """
    Set up Streamlit webhook using Streamlit's built-in server.
    
    Args:
        port: Port to expose
        
    Returns:
        dict: Setup result
    """
    try:
        # Get configuration
        from modules.configuration_interface import get_automated_workflow_config
        config = get_automated_workflow_config()
        
        # Get port from configuration if not provided
        if port is None:
            port = config.get_webhook_port()
        
        # Check if Streamlit is running in cloud environment
        is_cloud = os.environ.get('IS_STREAMLIT_CLOUD', 'false').lower() == 'true'
        
        if is_cloud:
            # In Streamlit Cloud, we can use the app URL directly
            app_url = os.environ.get('STREAMLIT_APP_URL', '')
            if not app_url:
                # Try to get from Streamlit config
                if "server" in st.config and "baseUrlPath" in st.config.server:
                    app_url = st.config.server.baseUrlPath
                
                if not app_url:
                    return {
                        "status": "error",
                        "message": "Could not determine Streamlit app URL"
                    }
            
            # Construct webhook URL
            webhook_url = f"{app_url}/webhook"
            
            # Save webhook URL to configuration
            config.config["webhook_url"] = webhook_url
            config._save_config()
            
            return {
                "status": "success",
                "message": "Streamlit webhook URL configured successfully",
                "url": webhook_url
            }
        else:
            # For local development, we need to use a tunnel service
            # Inform the user they need to use a tunnel service
            return {
                "status": "warning",
                "message": "For local development, you need to use a tunnel service like ngrok or localtunnel",
                "port": port,
                "instructions": [
                    "1. Install a tunnel service like ngrok or localtunnel",
                    "2. Run the tunnel service to expose your local port",
                    "3. Configure the webhook URL in Box Developer Console"
                ]
            }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error setting up Streamlit webhook: {str(e)}"
        }


def get_webhook_url():
    """
    Get the webhook URL.
    
    Returns:
        str: Webhook URL or None if not available
    """
    try:
        # Get configuration
        from modules.configuration_interface import get_automated_workflow_config
        config = get_automated_workflow_config()
        
        # Check if webhook URL is configured
        webhook_url = config.config.get("webhook_url")
        if webhook_url:
            return webhook_url
        
        # Check if we're running in Streamlit Cloud
        is_cloud = os.environ.get('IS_STREAMLIT_CLOUD', 'false').lower() == 'true'
        
        if is_cloud:
            # In Streamlit Cloud, we can use the app URL directly
            app_url = os.environ.get('STREAMLIT_APP_URL', '')
            if not app_url:
                # Try to get from Streamlit config
                if "server" in st.config and "baseUrlPath" in st.config.server:
                    app_url = st.config.server.baseUrlPath
                
                if not app_url:
                    return None
            
            # Construct webhook URL
            webhook_url = f"{app_url}/webhook"
            
            # Save webhook URL to configuration
            config.config["webhook_url"] = webhook_url
            config._save_config()
            
            return webhook_url
        
        # For local development, check if ngrok URL is configured
        ngrok_url = config.config.get("ngrok_url")
        if ngrok_url:
            return f"{ngrok_url}/webhook"
        
        # No webhook URL available
        return None
    
    except Exception as e:
        logger.error(f"Error getting webhook URL: {str(e)}", exc_info=True)
        return None


def start_event_stream(client=None, port=None):
    """
    Start the event stream.
    
    Args:
        client: Box client instance
        port: Port to listen on
        
    Returns:
        bool: True if event stream was started, False otherwise
    """
    return start_webhook_server(port=port, client=client)


def stop_event_stream():
    """
    Stop the event stream.
    
    Returns:
        bool: True if event stream was stopped, False otherwise
    """
    return stop_webhook_server()


def is_event_stream_running():
    """
    Check if event stream is running.
    
    Returns:
        bool: True if event stream is running, False otherwise
    """
    return is_webhook_server_running()


# Event processor class
class EventProcessor:
    """
    Event processor for Box events.
    """
    
    def __init__(self, client=None):
        """
        Initialize the event processor.
        
        Args:
            client: Box client instance
        """
        self.client = client
        self.processors = {}
        logger.info("EventProcessor initialized")
    
    def register_processor(self, event_type, processor):
        """
        Register a processor for an event type.
        
        Args:
            event_type: Event type
            processor: Processor function
        """
        self.processors[event_type] = processor
        logger.info(f"Registered processor for event type: {event_type}")
    
    def process_event(self, event):
        """
        Process an event.
        
        Args:
            event: Event data
            
        Returns:
            bool: True if event was processed, False otherwise
        """
        try:
            # Get event type
            event_type = event.get('trigger')
            
            if not event_type:
                logger.warning("Event has no trigger field")
                return False
            
            # Check if we have a processor for this event type
            if event_type not in self.processors:
                logger.warning(f"No processor registered for event type: {event_type}")
                return False
            
            # Process event
            logger.info(f"Processing event of type: {event_type}")
            self.processors[event_type](event, self.client)
            
            return True
        
        except Exception as e:
            logger.error(f"Error processing event: {str(e)}", exc_info=True)
            return False


# Global event processor instance
_event_processor = None

def get_event_processor(client=None):
    """
    Get the global event processor instance.
    
    Args:
        client: Box client instance
        
    Returns:
        EventProcessor: Global event processor instance
    """
    global _event_processor
    
    if _event_processor is None:
        _event_processor = EventProcessor(client)
    elif client is not None:
        _event_processor.client = client
    
    return _event_processor


# Global webhook manager instance
_webhook_manager = None

class WebhookManager:
    """
    Webhook manager for Box webhooks.
    """
    
    def __init__(self, client=None):
        """
        Initialize the webhook manager.
        
        Args:
            client: Box client instance
        """
        self.client = client
        logger.info("WebhookManager initialized")
    
    def register_webhook(self, folder_id, webhook_url):
        """
        Register a webhook for a folder.
        
        Args:
            folder_id: Folder ID
            webhook_url: Webhook URL
            
        Returns:
            str: Webhook ID or None if registration failed
        """
        try:
            # Check if client is available
            if not self.client:
                logger.warning("No client available")
                return None
            
            # Check if folder exists
            try:
                folder = self.client.folder(folder_id=folder_id).get()
            except Exception as e:
                logger.error(f"Error getting folder {folder_id}: {str(e)}")
                return None
            
            # Check if webhook already exists for this folder
            webhooks = self.client.get_webhooks()
            for webhook in webhooks:
                if webhook.target.id == folder_id:
                    logger.info(f"Webhook already exists for folder {folder_id}: {webhook.id}")
                    return webhook.id
            
            # Create webhook
            triggers = ['FILE.UPLOADED', 'FILE.COPIED', 'FILE.MOVED']
            webhook = self.client.create_webhook(folder, webhook_url, triggers)
            
            logger.info(f"Registered webhook for folder {folder_id}: {webhook.id}")
            return webhook.id
        
        except Exception as e:
            logger.error(f"Error registering webhook: {str(e)}", exc_info=True)
            return None
    
    def unregister_webhook(self, webhook_id):
        """
        Unregister a webhook.
        
        Args:
            webhook_id: Webhook ID
            
        Returns:
            bool: True if webhook was unregistered, False otherwise
        """
        try:
            # Check if client is available
            if not self.client:
                logger.warning("No client available")
                return False
            
            # Delete webhook
            self.client.webhook(webhook_id).delete()
            
            logger.info(f"Unregistered webhook: {webhook_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error unregistering webhook: {str(e)}", exc_info=True)
            return False
    
    def get_webhooks(self):
        """
        Get all webhooks.
        
        Returns:
            list: List of webhooks
        """
        try:
            # Check if client is available
            if not self.client:
                logger.warning("No client available")
                return []
            
            # Get webhooks
            webhooks = self.client.get_webhooks()
            
            return webhooks
        
        except Exception as e:
            logger.error(f"Error getting webhooks: {str(e)}", exc_info=True)
            return []


def get_webhook_manager(client=None):
    """
    Get the global webhook manager instance.
    
    Args:
        client: Box client instance
        
    Returns:
        WebhookManager: Global webhook manager instance
    """
    global _webhook_manager
    
    if _webhook_manager is None:
        _webhook_manager = WebhookManager(client)
    elif client is not None:
        _webhook_manager.client = client
    
    return _webhook_manager

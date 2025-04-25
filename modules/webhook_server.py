"""
Box webhook event handler for Streamlit app.
This module provides a Flask webhook handler for Box events.
"""

import os
import json
import logging
import threading
import time
from flask import Flask, request, jsonify
import hmac
import hashlib
import base64
from typing import Dict, Any, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
webhook_app = Flask(__name__)
webhook_server = None
webhook_thread = None
webhook_client = None
webhook_primary_key = None
webhook_handler = None

class WebhookServer:
    """
    Server for handling Box webhook events.
    """
    
    def __init__(self, port: int = 5000, client=None, primary_key: str = None):
        """
        Initialize the webhook server.
        
        Args:
            port: Port to listen on
            client: Box client instance
            primary_key: Box webhook primary signature key
        """
        self.port = port
        self.client = client
        self.primary_key = primary_key
        self.server = None
        self.thread = None
        self.is_running = False
        
        # Import event handler
        from modules.webhook_integration import WebhookEventHandler
        self.event_handler = WebhookEventHandler(client)
    
    def start(self) -> bool:
        """
        Start the webhook server.
        
        Returns:
            bool: True if server was started successfully, False otherwise
        """
        try:
            if self.is_running:
                logger.warning("Webhook server is already running")
                return True
            
            # Set global variables
            global webhook_client, webhook_primary_key, webhook_handler
            webhook_client = self.client
            webhook_primary_key = self.primary_key
            webhook_handler = self.event_handler
            
            # Start server in a separate thread
            self.thread = threading.Thread(target=self._run_server)
            self.thread.daemon = True
            self.thread.start()
            
            # Wait for server to start
            time.sleep(1)
            
            self.is_running = True
            logger.info(f"Webhook server started on port {self.port}")
            return True
        
        except Exception as e:
            logger.error(f"Error starting webhook server: {str(e)}", exc_info=True)
            return False
    
    def _run_server(self):
        """Run the webhook server."""
        try:
            webhook_app.run(host="0.0.0.0", port=self.port)
        except Exception as e:
            logger.error(f"Error running webhook server: {str(e)}", exc_info=True)
    
    def stop(self) -> bool:
        """
        Stop the webhook server.
        
        Returns:
            bool: True if server was stopped successfully, False otherwise
        """
        try:
            if not self.is_running:
                logger.warning("Webhook server is not running")
                return True
            
            # Stop server
            import requests
            try:
                requests.get(f"http://localhost:{self.port}/shutdown")
            except:
                pass
            
            # Wait for server to stop
            if self.thread:
                self.thread.join(timeout=5)
            
            self.is_running = False
            logger.info("Webhook server stopped")
            return True
        
        except Exception as e:
            logger.error(f"Error stopping webhook server: {str(e)}", exc_info=True)
            return False


@webhook_app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Handle webhook events from Box."""
    try:
        # Log request
        logger.info(f"Received webhook request: {request.headers}")
        
        # Verify signature if primary key is available
        if webhook_primary_key:
            is_valid = verify_webhook_signature(request.headers, request.data, webhook_primary_key)
            
            if not is_valid:
                logger.warning("Invalid webhook signature")
                return jsonify({"status": "error", "message": "Invalid signature"}), 403
        
        # Parse request body
        event_data = json.loads(request.data)
        
        # Log event
        logger.info(f"Webhook event: {event_data.get('trigger')} for {event_data.get('source', {}).get('type')} {event_data.get('source', {}).get('id')}")
        
        # Handle event asynchronously
        threading.Thread(target=handle_event_async, args=(event_data,)).start()
        
        # Return success
        return jsonify({"status": "success"}), 200
    
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@webhook_app.route('/shutdown', methods=['GET'])
def shutdown():
    """Shutdown the webhook server."""
    try:
        # Shutdown server
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        
        return jsonify({"status": "success"}), 200
    
    except Exception as e:
        logger.error(f"Error shutting down webhook server: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


def handle_event_async(event_data: Dict[str, Any]):
    """
    Handle webhook event asynchronously.
    
    Args:
        event_data: Event data
    """
    try:
        # Check if handler is available
        if webhook_handler:
            webhook_handler.handle_event(event_data)
        else:
            logger.warning("No webhook handler available")
    
    except Exception as e:
        logger.error(f"Error handling webhook event: {str(e)}", exc_info=True)


def verify_webhook_signature(headers: Dict[str, str], body: bytes, primary_key: str) -> bool:
    """
    Verify a webhook signature.
    
    Args:
        headers: Request headers
        body: Request body
        primary_key: Primary signature key
        
    Returns:
        bool: True if signature is valid, False otherwise
    """
    try:
        # Get signature from headers
        signature = headers.get('box-signature-primary')
        
        # If no signature is provided, assume it's invalid
        if not signature:
            logger.warning("No webhook signature provided")
            return False
        
        # Calculate expected signature
        expected_signature = base64.b64encode(
            hmac.new(
                primary_key.encode('utf-8'),
                body,
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        # Compare signatures
        return hmac.compare_digest(signature, expected_signature)
    
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {str(e)}", exc_info=True)
        return False


# Global instance
_webhook_server = None

def get_webhook_server(port: int = 5000, client=None, primary_key: str = None) -> WebhookServer:
    """
    Get the global webhook server instance.
    
    Args:
        port: Port to listen on
        client: Box client instance
        primary_key: Box webhook primary signature key
        
    Returns:
        WebhookServer: Global webhook server instance
    """
    global _webhook_server
    
    if _webhook_server is None:
        _webhook_server = WebhookServer(port, client, primary_key)
    else:
        _webhook_server.port = port
        _webhook_server.client = client
        _webhook_server.primary_key = primary_key
        
        # Update event handler
        from modules.webhook_integration import WebhookEventHandler
        _webhook_server.event_handler = WebhookEventHandler(client)
    
    return _webhook_server


def start_webhook_server(port: int = 5000, client=None, primary_key: str = None) -> bool:
    """
    Start the webhook server.
    
    Args:
        port: Port to listen on
        client: Box client instance
        primary_key: Box webhook primary signature key
        
    Returns:
        bool: True if server was started successfully, False otherwise
    """
    server = get_webhook_server(port, client, primary_key)
    return server.start()


def stop_webhook_server() -> bool:
    """
    Stop the webhook server.
    
    Returns:
        bool: True if server was stopped successfully, False otherwise
    """
    server = get_webhook_server()
    return server.stop()


def is_webhook_server_running() -> bool:
    """
    Check if the webhook server is running.
    
    Returns:
        bool: True if server is running, False otherwise
    """
    server = get_webhook_server()
    return server.is_running

"""
Event stream integration module for Box webhook events.
This module handles webhook registration, event listening, and event processing.
"""

import os
import json
import time
import hmac
import hashlib
import logging
import threading
import queue
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime
import requests
from flask import Flask, request, jsonify, Response
import atexit

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BoxWebhookManager:
    """
    Manages Box webhooks for folder monitoring.
    """
    
    def __init__(self, client=None):
        """
        Initialize the webhook manager.
        
        Args:
            client: Box client instance
        """
        self.client = client
        self.webhook_config_path = os.path.join(os.path.dirname(__file__), '..', '.webhooks.json')
        self.webhooks = self._load_webhooks()
        self.primary_key = None
        self.secondary_key = None
    
    def set_client(self, client):
        """
        Set the Box client.
        
        Args:
            client: Box client instance
        """
        self.client = client
    
    def set_keys(self, primary_key: str, secondary_key: str):
        """
        Set webhook verification keys.
        
        Args:
            primary_key: Primary verification key
            secondary_key: Secondary verification key
        """
        self.primary_key = primary_key
        self.secondary_key = secondary_key
    
    def _load_webhooks(self) -> Dict[str, Any]:
        """
        Load webhook configuration from file.
        
        Returns:
            dict: Webhook configuration
        """
        if os.path.exists(self.webhook_config_path):
            try:
                with open(self.webhook_config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading webhook config: {str(e)}")
        
        # Return default configuration if file doesn't exist or has errors
        return {
            "webhooks": [],
            "folder_mappings": {}
        }
    
    def _save_webhooks(self):
        """Save webhook configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.webhook_config_path), exist_ok=True)
            with open(self.webhook_config_path, 'w') as f:
                json.dump(self.webhooks, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving webhook config: {str(e)}")
    
    def register_webhook(self, folder_id: str, callback_url: str) -> Optional[str]:
        """
        Register a webhook for a Box folder.
        
        Args:
            folder_id: Box folder ID
            callback_url: Webhook callback URL
            
        Returns:
            str: Webhook ID if successful, None otherwise
        """
        if not self.client:
            logger.error("Box client not initialized")
            return None
        
        try:
            # Check if webhook already exists for this folder
            folder_mappings = self.webhooks.get("folder_mappings", {})
            if folder_id in folder_mappings:
                logger.info(f"Webhook already exists for folder {folder_id}")
                return folder_mappings[folder_id]
            
            # Create webhook
            triggers = ['FILE.UPLOADED', 'FILE.COPIED', 'FILE.MOVED']
            
            # For development/testing, simulate successful webhook registration
            if os.environ.get('WEBHOOK_SIMULATION', 'false').lower() == 'true':
                webhook_id = f"simulated_webhook_{int(time.time())}"
                
                # Save webhook information
                webhook_info = {
                    "id": webhook_id,
                    "folder_id": folder_id,
                    "callback_url": callback_url,
                    "triggers": triggers,
                    "created_at": datetime.now().isoformat(),
                    "simulated": True
                }
                
                webhooks_list = self.webhooks.get("webhooks", [])
                webhooks_list.append(webhook_info)
                
                if "folder_mappings" not in self.webhooks:
                    self.webhooks["folder_mappings"] = {}
                
                self.webhooks["folder_mappings"][folder_id] = webhook_id
                self._save_webhooks()
                
                logger.info(f"Registered simulated webhook {webhook_id} for folder {folder_id}")
                return webhook_id
            
            # Actual webhook registration
            webhook = self.client.create_webhook(
                self.client.folder(folder_id=folder_id),
                triggers,
                callback_url
            )
            
            # Save webhook information
            webhook_id = webhook.id
            webhook_info = {
                "id": webhook_id,
                "folder_id": folder_id,
                "callback_url": callback_url,
                "triggers": triggers,
                "created_at": datetime.now().isoformat()
            }
            
            webhooks_list = self.webhooks.get("webhooks", [])
            webhooks_list.append(webhook_info)
            
            if "folder_mappings" not in self.webhooks:
                self.webhooks["folder_mappings"] = {}
            
            self.webhooks["folder_mappings"][folder_id] = webhook_id
            self._save_webhooks()
            
            logger.info(f"Registered webhook {webhook_id} for folder {folder_id}")
            return webhook_id
        
        except Exception as e:
            logger.error(f"Error registering webhook: {str(e)}")
            return None
    
    def unregister_webhook(self, folder_id: str) -> bool:
        """
        Unregister a webhook for a Box folder.
        
        Args:
            folder_id: Box folder ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.client:
            logger.error("Box client not initialized")
            return False
        
        try:
            # Check if webhook exists for this folder
            folder_mappings = self.webhooks.get("folder_mappings", {})
            if folder_id not in folder_mappings:
                logger.warning(f"No webhook found for folder {folder_id}")
                return False
            
            webhook_id = folder_mappings[folder_id]
            
            # Check if this is a simulated webhook
            is_simulated = False
            for webhook in self.webhooks.get("webhooks", []):
                if webhook["id"] == webhook_id and webhook.get("simulated", False):
                    is_simulated = True
                    break
            
            # Delete webhook
            if not is_simulated:
                webhook = self.client.webhook(webhook_id)
                webhook.delete()
            
            # Update configuration
            webhooks_list = self.webhooks.get("webhooks", [])
            self.webhooks["webhooks"] = [w for w in webhooks_list if w["id"] != webhook_id]
            del self.webhooks["folder_mappings"][folder_id]
            self._save_webhooks()
            
            logger.info(f"Unregistered webhook {webhook_id} for folder {folder_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error unregistering webhook: {str(e)}")
            return False
    
    def get_webhooks(self) -> List[Dict[str, Any]]:
        """
        Get all registered webhooks.
        
        Returns:
            list: List of webhook information
        """
        return self.webhooks.get("webhooks", [])
    
    def get_webhook_for_folder(self, folder_id: str) -> Optional[Dict[str, Any]]:
        """
        Get webhook information for a specific folder.
        
        Args:
            folder_id: Box folder ID
            
        Returns:
            dict: Webhook information or None if not found
        """
        folder_mappings = self.webhooks.get("folder_mappings", {})
        if folder_id not in folder_mappings:
            return None
        
        webhook_id = folder_mappings[folder_id]
        
        for webhook in self.webhooks.get("webhooks", []):
            if webhook["id"] == webhook_id:
                return webhook
        
        return None
    
    def verify_webhook_signature(self, body: bytes, signature: str, delivery_timestamp: str) -> bool:
        """
        Verify Box webhook signature.
        
        Args:
            body: Request body as bytes
            signature: Box signature header
            delivery_timestamp: Box delivery timestamp header
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        # If in development mode, skip signature verification
        if os.environ.get('WEBHOOK_SKIP_VERIFICATION', 'false').lower() == 'true':
            logger.warning("Webhook signature verification skipped (development mode)")
            return True
            
        if not self.primary_key and not self.secondary_key:
            logger.warning("Webhook verification keys not set")
            return False
        
        # Try primary key first
        if self.primary_key:
            if self._verify_signature_with_key(body, signature, delivery_timestamp, self.primary_key):
                return True
        
        # Try secondary key if primary fails
        if self.secondary_key:
            if self._verify_signature_with_key(body, signature, delivery_timestamp, self.secondary_key):
                return True
        
        return False
    
    def _verify_signature_with_key(self, body: bytes, signature: str, delivery_timestamp: str, key: str) -> bool:
        """
        Verify signature with a specific key.
        
        Args:
            body: Request body as bytes
            signature: Box signature header
            delivery_timestamp: Box delivery timestamp header
            key: Verification key
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            # Create message string
            message = delivery_timestamp + "." + body.decode('utf-8')
            
            # Create HMAC signature
            hmac_obj = hmac.new(
                key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            )
            calculated_signature = hmac_obj.hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(calculated_signature, signature)
        
        except Exception as e:
            logger.error(f"Error verifying signature: {str(e)}")
            return False


class EventQueue:
    """
    Queue for processing Box webhook events.
    """
    
    def __init__(self, max_size: int = 1000, persistence_path: Optional[str] = None):
        """
        Initialize the event queue.
        
        Args:
            max_size: Maximum queue size
            persistence_path: Path for queue persistence (or None for in-memory only)
        """
        self.queue = queue.Queue(maxsize=max_size)
        self.persistence_path = persistence_path
        self.lock = threading.RLock()
        
        # Load persisted events if available
        if persistence_path:
            self._load_persisted_events()
    
    def _load_persisted_events(self):
        """Load persisted events from file."""
        if not self.persistence_path or not os.path.exists(self.persistence_path):
            return
        
        try:
            with open(self.persistence_path, 'r') as f:
                events = json.load(f)
                
                # Add events to queue
                for event in events:
                    try:
                        self.queue.put_nowait(event)
                    except queue.Full:
                        logger.warning("Queue full, discarding persisted event")
            
            # Clear persisted events
            os.remove(self.persistence_path)
        
        except Exception as e:
            logger.error(f"Error loading persisted events: {str(e)}")
    
    def _persist_events(self):
        """Persist events to file."""
        if not self.persistence_path:
            return
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
            
            # Get all events from queue
            events = []
            while not self.queue.empty():
                events.append(self.queue.get_nowait())
            
            # Write to file
            with open(self.persistence_path, 'w') as f:
                json.dump(events, f)
            
            # Put events back in queue
            for event in events:
                self.queue.put_nowait(event)
        
        except Exception as e:
            logger.error(f"Error persisting events: {str(e)}")
    
    def put(self, event: Dict[str, Any]) -> bool:
        """
        Add an event to the queue.
        
        Args:
            event: Event data
            
        Returns:
            bool: True if successful, False if queue is full
        """
        try:
            # Add timestamp if not present
            if 'timestamp' not in event:
                event['timestamp'] = time.time()
            
            # Add to queue
            self.queue.put(event, block=False)
            return True
        
        except queue.Full:
            logger.warning("Event queue is full, discarding event")
            return False
    
    def get(self, block: bool = True, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Get an event from the queue.
        
        Args:
            block: Whether to block if queue is empty
            timeout: Timeout in seconds (or None for no timeout)
            
        Returns:
            dict: Event data or None if queue is empty and not blocking
        """
        try:
            return self.queue.get(block=block, timeout=timeout)
        
        except queue.Empty:
            return None
    
    def task_done(self):
        """Mark task as done."""
        self.queue.task_done()
    
    def size(self) -> int:
        """
        Get current queue size.
        
        Returns:
            int: Queue size
        """
        return self.queue.qsize()
    
    def is_empty(self) -> bool:
        """
        Check if queue is empty.
        
        Returns:
            bool: True if queue is empty, False otherwise
        """
        return self.queue.empty()
    
    def shutdown(self):
        """Shutdown the queue and persist events."""
        with self.lock:
            if self.persistence_path:
                self._persist_events()


class WebhookListener:
    """
    Flask-based webhook listener for Box events.
    """
    
    def __init__(self, event_queue: EventQueue, webhook_manager: BoxWebhookManager, port: int = 5000):
        """
        Initialize the webhook listener.
        
        Args:
            event_queue: Event queue for processing events
            webhook_manager: Box webhook manager
            port: Port to listen on
        """
        self.event_queue = event_queue
        self.webhook_manager = webhook_manager
        self.port = port
        self.app = Flask(__name__)
        self.server_thread = None
        self.running = False
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register Flask routes."""
        
        @self.app.route('/webhook', methods=['POST'])
        def webhook_handler():
            """Handle incoming webhook events."""
            # Get request data
            body = request.get_data()
            signature = request.headers.get('box-signature-primary', '')
            delivery_timestamp = request.headers.get('box-delivery-timestamp', '')
            
            # Verify signature if keys are set
            if self.webhook_manager.primary_key or self.webhook_manager.secondary_key:
                if not self.webhook_manager.verify_webhook_signature(body, signature, delivery_timestamp):
                    logger.warning("Invalid webhook signature")
                    return jsonify({"status": "error", "message": "Invalid signature"}), 403
            
            # Parse event data
            try:
                event_data = json.loads(body)
                
                # Handle webhook verification challenge
                if 'challenge' in event_data:
                    logger.info("Received webhook verification challenge")
                    return jsonify({"status": "success", "challenge": event_data['challenge']})
                
                # Process event
                logger.info(f"Received webhook event: {event_data.get('event_type', 'unknown')}")
                
                # Add to queue
                self.event_queue.put(event_data)
                
                return jsonify({"status": "success"})
            
            except Exception as e:
                logger.error(f"Error processing webhook event: {str(e)}")
                return jsonify({"status": "error", "message": str(e)}), 400
        
        @self.app.route('/webhook/status', methods=['GET'])
        def webhook_status():
            """Get webhook status."""
            return jsonify({
                "status": "running" if self.running else "stopped",
                "queue_size": self.event_queue.size(),
                "webhooks": self.webhook_manager.get_webhooks()
            })
    
    def start(self):
        """Start the webhook listener in a separate thread."""
        if self.running:
            logger.warning("Webhook listener already running")
            return
        
        def run_server():
            """Run Flask server."""
            try:
                # Use 0.0.0.0 to listen on all interfaces
                self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)
            except Exception as e:
                logger.error(f"Error running webhook listener: {str(e)}")
                self.running = False
        
        # Start server in a separate thread
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        self.running = True
        logger.info(f"Webhook listener started on port {self.port}")
    
    def stop(self):
        """Stop the webhook listener."""
        if not self.running:
            logger.warning("Webhook listener not running")
            return
        
        # Stop Flask server
        try:
            requests.get(f"http://localhost:{self.port}/shutdown")
        except:
            pass
        
        self.running = False
        logger.info("Webhook listener stopped")


class EventProcessor:
    """
    Processor for Box webhook events.
    """
    
    def __init__(self, client=None, event_queue: Optional[EventQueue] = None):
        """
        Initialize the event processor.
        
        Args:
            client: Box client instance
            event_queue: Event queue for processing events
        """
        self.client = client
        self.event_queue = event_queue
        self.processors = {}
        self.running = False
        self.processor_thread = None
        self.lock = threading.RLock()
    
    def set_client(self, client):
        """
        Set the Box client.
        
        Args:
            client: Box client instance
        """
        self.client = client
    
    def set_event_queue(self, event_queue: EventQueue):
        """
        Set the event queue.
        
        Args:
            event_queue: Event queue for processing events
        """
        self.event_queue = event_queue
    
    def register_processor(self, event_type: str, processor: Callable[[Dict[str, Any]], None]):
        """
        Register a processor for a specific event type.
        
        Args:
            event_type: Event type to process
            processor: Function to process events of this type
        """
        with self.lock:
            self.processors[event_type] = processor
            logger.info(f"Registered processor for event type: {event_type}")
    
    def unregister_processor(self, event_type: str):
        """
        Unregister a processor for a specific event type.
        
        Args:
            event_type: Event type to unregister
        """
        with self.lock:
            if event_type in self.processors:
                del self.processors[event_type]
                logger.info(f"Unregistered processor for event type: {event_type}")
    
    def start(self):
        """Start the event processor."""
        if self.running:
            logger.warning("Event processor already running")
            return
        
        if not self.event_queue:
            logger.error("Event queue not set")
            return
        
        def process_events():
            """Process events from queue."""
            while self.running:
                try:
                    # Get event from queue
                    event = self.event_queue.get(block=True, timeout=1.0)
                    
                    if event:
                        # Process event
                        self._process_event(event)
                        
                        # Mark task as done
                        self.event_queue.task_done()
                
                except Exception as e:
                    if self.running:
                        logger.error(f"Error processing events: {str(e)}")
        
        # Start processor in a separate thread
        self.running = True
        self.processor_thread = threading.Thread(target=process_events)
        self.processor_thread.daemon = True
        self.processor_thread.start()
        
        logger.info("Event processor started")
    
    def stop(self):
        """Stop the event processor."""
        if not self.running:
            logger.warning("Event processor not running")
            return
        
        # Stop processor
        self.running = False
        
        # Wait for processor thread to finish
        if self.processor_thread:
            self.processor_thread.join(timeout=5.0)
        
        logger.info("Event processor stopped")
    
    def _process_event(self, event: Dict[str, Any]):
        """
        Process an event.
        
        Args:
            event: Event data
        """
        try:
            # Get event type
            event_type = event.get('event_type')
            
            if not event_type:
                logger.warning("Event has no type")
                return
            
            # Get processor for this event type
            processor = self.processors.get(event_type)
            
            if not processor:
                logger.info(f"No processor registered for event type: {event_type}")
                return
            
            # Process event
            logger.info(f"Processing event: {event_type}")
            processor(event)
        
        except Exception as e:
            logger.error(f"Error processing event: {str(e)}")


# Global instances
_webhook_manager = None
_event_queue = None
_event_processor = None
_webhook_listener = None

def get_webhook_manager(client=None) -> BoxWebhookManager:
    """
    Get the global webhook manager instance.
    
    Args:
        client: Box client instance
        
    Returns:
        BoxWebhookManager: Global webhook manager instance
    """
    global _webhook_manager
    
    if _webhook_manager is None:
        _webhook_manager = BoxWebhookManager(client)
    elif client is not None:
        _webhook_manager.set_client(client)
    
    return _webhook_manager

def get_event_queue() -> EventQueue:
    """
    Get the global event queue instance.
    
    Returns:
        EventQueue: Global event queue instance
    """
    global _event_queue
    
    if _event_queue is None:
        # Create persistence directory
        persistence_dir = os.path.join(os.path.dirname(__file__), '..', '.events')
        os.makedirs(persistence_dir, exist_ok=True)
        
        # Create event queue
        persistence_path = os.path.join(persistence_dir, 'events.json')
        _event_queue = EventQueue(persistence_path=persistence_path)
    
    return _event_queue

def get_event_processor(client=None) -> EventProcessor:
    """
    Get the global event processor instance.
    
    Args:
        client: Box client instance
        
    Returns:
        EventProcessor: Global event processor instance
    """
    global _event_processor
    
    if _event_processor is None:
        _event_processor = EventProcessor(client, get_event_queue())
    elif client is not None:
        _event_processor.set_client(client)
    
    return _event_processor

def get_webhook_listener(webhook_manager: Optional[BoxWebhookManager] = None, event_queue: Optional[EventQueue] = None, port: int = 5000) -> WebhookListener:
    """
    Get the global webhook listener instance.
    
    Args:
        webhook_manager: Box webhook manager
        event_queue: Event queue for processing events
        port: Port to listen on
        
    Returns:
        WebhookListener: Global webhook listener instance
    """
    global _webhook_listener
    
    if _webhook_listener is None:
        # Get webhook manager and event queue if not provided
        if webhook_manager is None:
            webhook_manager = get_webhook_manager()
        
        if event_queue is None:
            event_queue = get_event_queue()
        
        # Create webhook listener
        _webhook_listener = WebhookListener(event_queue, webhook_manager, port)
    
    return _webhook_listener

def start_event_stream(client=None, port: int = 5000):
    """
    Start the event stream.
    
    Args:
        client: Box client instance
        port: Port to listen on
    """
    try:
        # Get components
        webhook_manager = get_webhook_manager(client)
        event_queue = get_event_queue()
        event_processor = get_event_processor(client)
        webhook_listener = get_webhook_listener(webhook_manager, event_queue, port)
        
        # Start components
        event_processor.start()
        webhook_listener.start()
        
        # Register shutdown handler
        atexit.register(stop_event_stream)
        
        logger.info("Event stream started")
    
    except Exception as e:
        logger.error(f"Error starting event stream: {str(e)}")
        raise

def stop_event_stream():
    """Stop the event stream."""
    try:
        # Get components
        event_processor = get_event_processor()
        webhook_listener = get_webhook_listener()
        event_queue = get_event_queue()
        
        # Stop components
        if event_processor:
            event_processor.stop()
        
        if webhook_listener:
            webhook_listener.stop()
        
        if event_queue:
            event_queue.shutdown()
        
        logger.info("Event stream stopped")
    
    except Exception as e:
        logger.error(f"Error stopping event stream: {str(e)}")
        raise

def process_file_upload_event(event: Dict[str, Any]):
    """
    Process a file upload event.
    This is a placeholder function that should be implemented in the automated_categorization module.
    
    Args:
        event: Event data
    """
    # This function should be implemented in the automated_categorization module
    # and registered with the event processor
    pass

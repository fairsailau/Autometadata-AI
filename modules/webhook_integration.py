"""
Webhook integration module for Box webhooks.
This module provides functionality for integrating with Box webhooks using ngrok.
"""

import os
import json
import logging
import subprocess
import time
import threading
import requests
import hmac
import hashlib
import streamlit as st
from typing import Dict, Any, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NgrokIntegration:
    """
    Integration with ngrok for creating public URLs for webhook endpoints.
    """
    
    def __init__(self):
        """Initialize the ngrok integration."""
        self.ngrok_process = None
        self.public_url = None
        self.ngrok_bin_path = self._get_ngrok_bin_path()
        
    def _get_ngrok_bin_path(self) -> str:
        """
        Get the path to the ngrok binary.
        
        Returns:
            str: Path to the ngrok binary
        """
        # Check if ngrok is in PATH
        try:
            result = subprocess.run(["which", "ngrok"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        # Check common locations
        common_locations = [
            "/usr/local/bin/ngrok",
            "/usr/bin/ngrok",
            os.path.expanduser("~/ngrok"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin", "ngrok")
        ]
        
        for location in common_locations:
            if os.path.exists(location):
                return location
        
        # Not found, will need to download
        return None
    
    def _download_ngrok(self) -> str:
        """
        Download ngrok binary.
        
        Returns:
            str: Path to the downloaded ngrok binary
        """
        try:
            logger.info("Downloading ngrok...")
            
            # Create bin directory if it doesn't exist
            bin_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin")
            os.makedirs(bin_dir, exist_ok=True)
            
            # Determine platform
            import platform
            system = platform.system().lower()
            machine = platform.machine().lower()
            
            # Determine download URL
            if system == "linux":
                if "arm" in machine or "aarch" in machine:
                    url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz"
                else:
                    url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz"
            elif system == "darwin":
                if "arm" in machine or "aarch" in machine:
                    url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-arm64.zip"
                else:
                    url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-amd64.zip"
            elif system == "windows":
                url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
            else:
                raise ValueError(f"Unsupported platform: {system} {machine}")
            
            # Download and extract
            import tempfile
            import shutil
            
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
            
            # Extract based on file type
            if url.endswith(".tgz"):
                import tarfile
                with tarfile.open(temp_file.name, "r:gz") as tar:
                    tar.extractall(bin_dir)
            elif url.endswith(".zip"):
                import zipfile
                with zipfile.ZipFile(temp_file.name, "r") as zip_ref:
                    zip_ref.extractall(bin_dir)
            
            # Clean up
            os.unlink(temp_file.name)
            
            # Set executable permission
            ngrok_path = os.path.join(bin_dir, "ngrok")
            os.chmod(ngrok_path, 0o755)
            
            logger.info(f"ngrok downloaded to {ngrok_path}")
            return ngrok_path
        
        except Exception as e:
            logger.error(f"Error downloading ngrok: {str(e)}", exc_info=True)
            return None
    
    def ensure_ngrok_installed(self) -> bool:
        """
        Ensure ngrok is installed.
        
        Returns:
            bool: True if ngrok is installed, False otherwise
        """
        if self.ngrok_bin_path is None:
            self.ngrok_bin_path = self._download_ngrok()
        
        return self.ngrok_bin_path is not None
    
    def start_ngrok(self, port: int, auth_token: Optional[str] = None, webhook_secret: Optional[str] = None) -> bool:
        """
        Start ngrok and expose the specified port.
        
        Args:
            port: Port to expose
            auth_token: ngrok authentication token
            webhook_secret: Box webhook secret for signature verification
            
        Returns:
            bool: True if ngrok was started successfully, False otherwise
        """
        try:
            # Ensure ngrok is installed
            if not self.ensure_ngrok_installed():
                logger.error("ngrok is not installed and could not be downloaded")
                return False
            
            # Stop existing ngrok process
            self.stop_ngrok()
            
            # Build command
            cmd = [self.ngrok_bin_path, "http", str(port)]
            
            # Add auth token if provided
            if auth_token:
                # Configure ngrok with auth token
                subprocess.run([self.ngrok_bin_path, "config", "add-authtoken", auth_token], 
                              check=True, capture_output=True)
            
            # Add webhook verification if provided
            if webhook_secret:
                cmd.extend(["--verify-webhook", "BOX", "--verify-webhook-secret", webhook_secret])
            
            # Start ngrok
            self.ngrok_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for ngrok to start
            time.sleep(2)
            
            # Get public URL
            self.public_url = self._get_ngrok_url()
            
            if self.public_url:
                logger.info(f"ngrok started successfully, public URL: {self.public_url}")
                return True
            else:
                logger.error("Failed to get ngrok public URL")
                self.stop_ngrok()
                return False
        
        except Exception as e:
            logger.error(f"Error starting ngrok: {str(e)}", exc_info=True)
            self.stop_ngrok()
            return False
    
    def _get_ngrok_url(self) -> Optional[str]:
        """
        Get the public URL provided by ngrok.
        
        Returns:
            str: Public URL or None if not available
        """
        try:
            # Try to get URL from ngrok API
            response = requests.get("http://localhost:4040/api/tunnels")
            data = response.json()
            
            tunnels = data.get("tunnels", [])
            if not tunnels:
                return None
            
            # Get HTTPS tunnel
            https_tunnel = next((t for t in tunnels if t["proto"] == "https"), None)
            if not https_tunnel:
                return None
            
            return https_tunnel["public_url"]
        
        except Exception as e:
            logger.error(f"Error getting ngrok URL: {str(e)}", exc_info=True)
            return None
    
    def stop_ngrok(self) -> bool:
        """
        Stop the ngrok process.
        
        Returns:
            bool: True if ngrok was stopped successfully, False otherwise
        """
        try:
            if self.ngrok_process:
                self.ngrok_process.terminate()
                self.ngrok_process.wait(timeout=5)
                self.ngrok_process = None
                self.public_url = None
                logger.info("ngrok stopped successfully")
                return True
            
            return True
        
        except Exception as e:
            logger.error(f"Error stopping ngrok: {str(e)}", exc_info=True)
            return False
    
    def is_running(self) -> bool:
        """
        Check if ngrok is running.
        
        Returns:
            bool: True if ngrok is running, False otherwise
        """
        if self.ngrok_process is None:
            return False
        
        return self.ngrok_process.poll() is None
    
    def get_public_url(self) -> Optional[str]:
        """
        Get the public URL provided by ngrok.
        
        Returns:
            str: Public URL or None if not available
        """
        if not self.is_running():
            return None
        
        if self.public_url is None:
            self.public_url = self._get_ngrok_url()
        
        return self.public_url


class BoxWebhookManager:
    """
    Manager for Box webhooks.
    """
    
    def __init__(self, client=None):
        """
        Initialize the Box webhook manager.
        
        Args:
            client: Box client instance
        """
        self.client = client
    
    def create_webhook(self, target_type: str, target_id: str, address: str, triggers: List[str]) -> Optional[Dict[str, Any]]:
        """
        Create a webhook in Box.
        
        Args:
            target_type: Target type (file or folder)
            target_id: Target ID
            address: Webhook address
            triggers: Webhook triggers
            
        Returns:
            dict: Webhook information or None if creation failed
        """
        try:
            # Check if client is available
            if not self.client:
                logger.warning("No Box client available")
                return None
            
            # Create webhook
            webhook = self.client.create_webhook({
                "target": {
                    "id": target_id,
                    "type": target_type
                },
                "address": address,
                "triggers": triggers
            })
            
            logger.info(f"Webhook created: {webhook.id}")
            
            # Return webhook info
            return {
                "id": webhook.id,
                "target": {
                    "id": target_id,
                    "type": target_type
                },
                "address": address,
                "triggers": triggers
            }
        
        except Exception as e:
            logger.error(f"Error creating webhook: {str(e)}", exc_info=True)
            return None
    
    def list_webhooks(self) -> List[Dict[str, Any]]:
        """
        List all webhooks for the authenticated user.
        
        Returns:
            list: List of webhooks
        """
        try:
            # Check if client is available
            if not self.client:
                logger.warning("No Box client available")
                return []
            
            # Get webhooks
            webhooks = self.client.get_webhooks()
            
            # Convert to list of dicts
            result = []
            for webhook in webhooks:
                result.append({
                    "id": webhook.id,
                    "target": {
                        "id": webhook.target.id,
                        "type": webhook.target.type
                    },
                    "address": webhook.address,
                    "triggers": webhook.triggers
                })
            
            return result
        
        except Exception as e:
            logger.error(f"Error listing webhooks: {str(e)}", exc_info=True)
            return []
    
    def delete_webhook(self, webhook_id: str) -> bool:
        """
        Delete a webhook.
        
        Args:
            webhook_id: Webhook ID
            
        Returns:
            bool: True if webhook was deleted successfully, False otherwise
        """
        try:
            # Check if client is available
            if not self.client:
                logger.warning("No Box client available")
                return False
            
            # Delete webhook
            self.client.webhook(webhook_id).delete()
            
            logger.info(f"Webhook deleted: {webhook_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting webhook: {str(e)}", exc_info=True)
            return False
    
    def verify_webhook_signature(self, headers: Dict[str, str], body: bytes, primary_key: str) -> bool:
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
            expected_signature = hmac.new(
                primary_key.encode('utf-8'),
                body,
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(signature, expected_signature)
        
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {str(e)}", exc_info=True)
            return False


class WebhookEventHandler:
    """
    Handler for Box webhook events.
    """
    
    def __init__(self, client=None):
        """
        Initialize the webhook event handler.
        
        Args:
            client: Box client instance
        """
        self.client = client
    
    def handle_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Handle a webhook event.
        
        Args:
            event_data: Event data
            
        Returns:
            bool: True if event was handled successfully, False otherwise
        """
        try:
            # Check if client is available
            if not self.client:
                logger.warning("No Box client available")
                return False
            
            # Get trigger
            trigger = event_data.get('trigger')
            
            # Get source
            source = event_data.get('source', {})
            
            # Get source type
            source_type = source.get('type')
            
            # Get source ID
            source_id = source.get('id')
            
            logger.info(f"Handling webhook event: {trigger} for {source_type} {source_id}")
            
            # Handle based on trigger
            if trigger == 'FILE.UPLOADED':
                return self._handle_file_uploaded(source_id)
            elif trigger == 'FILE.COPIED':
                return self._handle_file_copied(source_id)
            elif trigger == 'FILE.MOVED':
                return self._handle_file_moved(source_id)
            else:
                logger.warning(f"Unsupported trigger: {trigger}")
                return False
        
        except Exception as e:
            logger.error(f"Error handling webhook event: {str(e)}", exc_info=True)
            return False
    
    def _handle_file_uploaded(self, file_id: str) -> bool:
        """
        Handle a file uploaded event.
        
        Args:
            file_id: File ID
            
        Returns:
            bool: True if event was handled successfully, False otherwise
        """
        try:
            # Get file
            file = self.client.file(file_id=file_id).get()
            
            logger.info(f"File uploaded: {file.name} ({file.id})")
            
            # TODO: Implement file processing logic
            # This would typically involve:
            # 1. Categorizing the document
            # 2. Extracting metadata
            # 3. Applying metadata to the file
            
            return True
        
        except Exception as e:
            logger.error(f"Error handling file uploaded event: {str(e)}", exc_info=True)
            return False
    
    def _handle_file_copied(self, file_id: str) -> bool:
        """
        Handle a file copied event.
        
        Args:
            file_id: File ID
            
        Returns:
            bool: True if event was handled successfully, False otherwise
        """
        # Use same handler as file uploaded
        return self._handle_file_uploaded(file_id)
    
    def _handle_file_moved(self, file_id: str) -> bool:
        """
        Handle a file moved event.
        
        Args:
            file_id: File ID
            
        Returns:
            bool: True if event was handled successfully, False otherwise
        """
        try:
            # Get file
            file = self.client.file(file_id=file_id).get()
            
            logger.info(f"File moved: {file.name} ({file.id})")
            
            # TODO: Implement file processing logic
            # This would typically involve:
            # 1. Checking if the file is now in a monitored folder
            # 2. If so, process it as if it was uploaded
            
            return True
        
        except Exception as e:
            logger.error(f"Error handling file moved event: {str(e)}", exc_info=True)
            return False


class WebhookConfigurationInterface:
    """
    Interface for configuring Box webhooks.
    """
    
    def __init__(self, client=None):
        """
        Initialize the webhook configuration interface.
        
        Args:
            client: Box client instance
        """
        self.client = client
        self.ngrok = NgrokIntegration()
        self.webhook_manager = BoxWebhookManager(client)
        self.event_handler = WebhookEventHandler(client)
        
        # Load configuration
        from modules.configuration_interface import get_automated_workflow_config
        self.config = get_automated_workflow_config()
    
    def render_webhook_configuration(self):
        """Render the webhook configuration interface."""
        try:
            st.subheader("Webhook Configuration")
            st.write("Configure Box webhooks for automated metadata extraction.")
            
            # Create tabs for different webhook configuration sections
            tabs = st.tabs([
                "Ngrok Setup",
                "Webhook Setup",
                "Webhook Status"
            ])
            
            # Ngrok setup tab
            with tabs[0]:
                self._render_ngrok_setup()
            
            # Webhook setup tab
            with tabs[1]:
                self._render_webhook_setup()
            
            # Webhook status tab
            with tabs[2]:
                self._render_webhook_status()
            
            logger.info("Webhook configuration interface rendered successfully")
        
        except Exception as e:
            logger.error(f"Error rendering webhook configuration interface: {str(e)}", exc_info=True)
            st.error(f"Error rendering webhook configuration interface: {str(e)}")
    
    def _render_ngrok_setup(self):
        """Render the ngrok setup section."""
        try:
            st.subheader("Ngrok Setup")
            st.write("Configure ngrok to expose your local webhook endpoint to the internet.")
            
            # Ngrok status
            is_running = self.ngrok.is_running()
            
            if is_running:
                st.success("Ngrok is running")
                
                # Display public URL
                public_url = self.ngrok.get_public_url()
                if public_url:
                    st.write(f"Public URL: {public_url}")
                    st.write(f"Webhook URL: {public_url}/webhook")
                    
                    # Copy button
                    if st.button("Copy Webhook URL to Clipboard"):
                        st.write(f"Webhook URL copied: {public_url}/webhook")
                        # Note: Actual clipboard copy not possible in Streamlit
                else:
                    st.warning("Ngrok is running but no public URL is available")
            else:
                st.warning("Ngrok is not running")
            
            # Ngrok authentication token
            st.write("---")
            st.write("Ngrok Authentication Token")
            
            # Get token from configuration
            ngrok_token = self.config.config.get("ngrok_token", "")
            
            # Token input
            new_token = st.text_input(
                "Ngrok Authentication Token",
                value=ngrok_token,
                type="password",
                help="Your ngrok authentication token. Get one at https://dashboard.ngrok.com/get-started/your-authtoken"
            )
            
            # Save token if changed
            if new_token != ngrok_token:
                self.config.config["ngrok_token"] = new_token
                self.config._save_config()
            
            # Webhook port
            st.write("---")
            st.write("Webhook Port")
            
            # Get port from configuration
            webhook_port = self.config.get_webhook_port()
            
            # Port input
            new_port = st.number_input(
                "Webhook Port",
                min_value=1000,
                max_value=65535,
                value=webhook_port,
                step=1,
                help="Port to use for webhook server"
            )
            
            # Save port if changed
            if new_port != webhook_port:
                self.config.set_webhook_port(new_port)
            
            # Start/stop ngrok
            st.write("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if is_running:
                    if st.button("Stop Ngrok", use_container_width=True):
                        if self.ngrok.stop_ngrok():
                            st.success("Ngrok stopped successfully")
                            st.rerun()
                        else:
                            st.error("Failed to stop ngrok")
                else:
                    if st.button("Start Ngrok", use_container_width=True):
                        if self.ngrok.start_ngrok(new_port, new_token):
                            st.success("Ngrok started successfully")
                            st.rerun()
                        else:
                            st.error("Failed to start ngrok")
            
            with col2:
                if st.button("Check Ngrok Status", use_container_width=True):
                    st.rerun()
        
        except Exception as e:
            logger.error(f"Error rendering ngrok setup: {str(e)}", exc_info=True)
            st.error(f"Error rendering ngrok setup: {str(e)}")
    
    def _render_webhook_setup(self):
        """Render the webhook setup section."""
        try:
            st.subheader("Webhook Setup")
            st.write("Configure Box webhooks for automated metadata extraction.")
            
            # Check if client is available
            if "client" not in st.session_state or not st.session_state.client:
                st.warning("Please authenticate with Box to configure webhooks.")
                return
            
            # Check if ngrok is running
            if not self.ngrok.is_running():
                st.warning("Please start ngrok to get a public URL for your webhook.")
                return
            
            # Get public URL
            public_url = self.ngrok.get_public_url()
            if not public_url:
                st.warning("No public URL available. Please restart ngrok.")
                return
            
            # Webhook URL
            webhook_url = f"{public_url}/webhook"
            
            # Display webhook URL
            st.write("Webhook URL")
            st.code(webhook_url)
            
            # Box Developer Console instructions
            st.write("---")
            st.write("Box Developer Console Setup")
            
            st.write("""
            To configure a webhook in Box, follow these steps:
            
            1. Go to the [Box Developer Console](https://app.box.com/developers/console)
            2. Select your application
            3. Click on the **Webhooks** tab
            4. Click **Create Webhook**
            5. Select **V2** from the dropdown
            6. Enter the webhook URL shown above
            7. Select the content type (file or folder) to monitor
            8. Select the triggers (events) that will activate the webhook
            9. Click **Create Webhook**
            """)
            
            # Webhook signature verification
            st.write("---")
            st.write("Webhook Signature Verification")
            
            # Get primary key from configuration
            primary_key = self.config.config.get("webhook_primary_key", "")
            
            # Primary key input
            new_primary_key = st.text_input(
                "Primary Signature Key",
                value=primary_key,
                type="password",
                help="Your Box webhook primary signature key. Get this from the Box Developer Console under Webhooks > Manage Signature Keys."
            )
            
            # Save primary key if changed
            if new_primary_key != primary_key:
                self.config.config["webhook_primary_key"] = new_primary_key
                self.config._save_config()
            
            # Restart ngrok with signature verification
            if new_primary_key and st.button("Restart Ngrok with Signature Verification"):
                webhook_port = self.config.get_webhook_port()
                ngrok_token = self.config.config.get("ngrok_token", "")
                
                if self.ngrok.start_ngrok(webhook_port, ngrok_token, new_primary_key):
                    st.success("Ngrok restarted with signature verification")
                    st.rerun()
                else:
                    st.error("Failed to restart ngrok")
        
        except Exception as e:
            logger.error(f"Error rendering webhook setup: {str(e)}", exc_info=True)
            st.error(f"Error rendering webhook setup: {str(e)}")
    
    def _render_webhook_status(self):
        """Render the webhook status section."""
        try:
            st.subheader("Webhook Status")
            st.write("View and manage your Box webhooks.")
            
            # Check if client is available
            if "client" not in st.session_state or not st.session_state.client:
                st.warning("Please authenticate with Box to view webhooks.")
                return
            
            # Refresh button
            if st.button("Refresh Webhooks"):
                st.rerun()
            
            # Get webhooks
            webhooks = self.webhook_manager.list_webhooks()
            
            if webhooks:
                st.write(f"Found {len(webhooks)} webhooks:")
                
                for webhook in webhooks:
                    with st.expander(f"Webhook {webhook['id']}"):
                        st.write(f"**Target:** {webhook['target']['type']} {webhook['target']['id']}")
                        st.write(f"**Address:** {webhook['address']}")
                        st.write(f"**Triggers:** {', '.join(webhook['triggers'])}")
                        
                        if st.button("Delete Webhook", key=f"delete_webhook_{webhook['id']}"):
                            if self.webhook_manager.delete_webhook(webhook['id']):
                                st.success(f"Webhook {webhook['id']} deleted successfully")
                                st.rerun()
                            else:
                                st.error(f"Failed to delete webhook {webhook['id']}")
            else:
                st.info("No webhooks found.")
        
        except Exception as e:
            logger.error(f"Error rendering webhook status: {str(e)}", exc_info=True)
            st.error(f"Error rendering webhook status: {str(e)}")


# Global instance
_webhook_interface = None

def get_webhook_interface(client=None) -> WebhookConfigurationInterface:
    """
    Get the global webhook interface instance.
    
    Args:
        client: Box client instance
        
    Returns:
        WebhookConfigurationInterface: Global webhook interface instance
    """
    global _webhook_interface
    
    if _webhook_interface is None:
        _webhook_interface = WebhookConfigurationInterface(client)
    elif client is not None:
        _webhook_interface.client = client
        _webhook_interface.webhook_manager.client = client
        _webhook_interface.event_handler.client = client
    
    return _webhook_interface

def render_webhook_configuration():
    """
    Standalone wrapper for render_webhook_configuration.
    """
    logger.info("Calling render_webhook_configuration standalone function")
    return get_webhook_interface().render_webhook_configuration()

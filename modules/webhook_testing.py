"""
Integration module for Box webhook integration testing.
This module provides functionality for testing the Box webhook integration.
"""

import os
import json
import logging
import requests
import time
import streamlit as st
from typing import Dict, Any, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebhookTester:
    """
    Tester for Box webhooks.
    """
    
    def __init__(self, client=None):
        """
        Initialize the webhook tester.
        
        Args:
            client: Box client instance
        """
        self.client = client
    
    def test_ngrok_connection(self) -> Dict[str, Any]:
        """
        Test ngrok connection.
        
        Returns:
            dict: Test results
        """
        try:
            # Import ngrok integration
            from modules.webhook_integration import NgrokIntegration
            
            # Create ngrok integration
            ngrok = NgrokIntegration()
            
            # Check if ngrok is running
            is_running = ngrok.is_running()
            
            # Get public URL
            public_url = ngrok.get_public_url() if is_running else None
            
            # Test public URL
            url_reachable = False
            if public_url:
                try:
                    response = requests.head(public_url, timeout=5)
                    url_reachable = response.status_code < 400
                except:
                    url_reachable = False
            
            # Return results
            return {
                "success": is_running and url_reachable,
                "is_running": is_running,
                "public_url": public_url,
                "url_reachable": url_reachable
            }
        
        except Exception as e:
            logger.error(f"Error testing ngrok connection: {str(e)}", exc_info=True)
            return {
                "success": False,
                "is_running": False,
                "public_url": None,
                "url_reachable": False,
                "error": str(e)
            }
    
    def test_webhook_server(self) -> Dict[str, Any]:
        """
        Test webhook server.
        
        Returns:
            dict: Test results
        """
        try:
            # Import webhook server
            from modules.webhook_server import is_webhook_server_running
            
            # Check if webhook server is running
            is_running = is_webhook_server_running()
            
            # Get webhook URL
            webhook_url = None
            if is_running:
                # Import ngrok integration
                from modules.webhook_integration import NgrokIntegration
                
                # Create ngrok integration
                ngrok = NgrokIntegration()
                
                # Get public URL
                public_url = ngrok.get_public_url()
                
                if public_url:
                    webhook_url = f"{public_url}/webhook"
            
            # Test webhook URL
            url_reachable = False
            if webhook_url:
                try:
                    response = requests.head(webhook_url, timeout=5)
                    url_reachable = response.status_code < 400
                except:
                    url_reachable = False
            
            # Return results
            return {
                "success": is_running and url_reachable,
                "is_running": is_running,
                "webhook_url": webhook_url,
                "url_reachable": url_reachable
            }
        
        except Exception as e:
            logger.error(f"Error testing webhook server: {str(e)}", exc_info=True)
            return {
                "success": False,
                "is_running": False,
                "webhook_url": None,
                "url_reachable": False,
                "error": str(e)
            }
    
    def test_webhook_creation(self) -> Dict[str, Any]:
        """
        Test webhook creation.
        
        Returns:
            dict: Test results
        """
        try:
            # Check if client is available
            if not self.client:
                logger.warning("No Box client available")
                return {
                    "success": False,
                    "error": "No Box client available"
                }
            
            # Import webhook integration
            from modules.webhook_integration import BoxWebhookManager
            
            # Create webhook manager
            webhook_manager = BoxWebhookManager(self.client)
            
            # Get webhook URL
            webhook_url = None
            
            # Import ngrok integration
            from modules.webhook_integration import NgrokIntegration
            
            # Create ngrok integration
            ngrok = NgrokIntegration()
            
            # Get public URL
            public_url = ngrok.get_public_url()
            
            if public_url:
                webhook_url = f"{public_url}/webhook"
            else:
                return {
                    "success": False,
                    "error": "No public URL available"
                }
            
            # Get root folder
            root_folder = self.client.folder(folder_id="0").get()
            
            # Create test webhook
            webhook = webhook_manager.create_webhook(
                target_type="folder",
                target_id=root_folder.id,
                address=webhook_url,
                triggers=["FILE.UPLOADED"]
            )
            
            # Check if webhook was created
            if not webhook:
                return {
                    "success": False,
                    "error": "Failed to create webhook"
                }
            
            # Wait for webhook to be available
            time.sleep(2)
            
            # Get webhooks
            webhooks = webhook_manager.list_webhooks()
            
            # Check if webhook is in list
            webhook_found = False
            for w in webhooks:
                if w["id"] == webhook["id"]:
                    webhook_found = True
                    break
            
            # Delete test webhook
            webhook_manager.delete_webhook(webhook["id"])
            
            # Return results
            return {
                "success": webhook_found,
                "webhook": webhook,
                "webhook_found": webhook_found
            }
        
        except Exception as e:
            logger.error(f"Error testing webhook creation: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_webhook_event(self) -> Dict[str, Any]:
        """
        Test webhook event.
        
        Returns:
            dict: Test results
        """
        try:
            # Check if client is available
            if not self.client:
                logger.warning("No Box client available")
                return {
                    "success": False,
                    "error": "No Box client available"
                }
            
            # Import webhook integration
            from modules.webhook_integration import BoxWebhookManager, WebhookEventHandler
            
            # Create webhook manager
            webhook_manager = BoxWebhookManager(self.client)
            
            # Create event handler
            event_handler = WebhookEventHandler(self.client)
            
            # Create test event
            event_data = {
                "type": "webhook_event",
                "id": "eb0c4e06-751f-442c-86f8-fd5bb404dbec",
                "created_at": "2025-04-25T02:10:32-07:00",
                "trigger": "FILE.UPLOADED",
                "webhook": {
                    "id": "53",
                    "type": "webhook"
                },
                "created_by": {
                    "type": "user",
                    "id": "226067247",
                    "name": "Test User",
                    "login": "test@example.com"
                },
                "source": {
                    "id": "73835521473",
                    "type": "file",
                    "file_version": {
                        "type": "file_version",
                        "id": "78096737033",
                        "sha1": "2c61623e86bee78e6ab444af456bccc7a1164095"
                    },
                    "sequence_id": "0",
                    "etag": "0",
                    "sha1": "2c61623e86bee78e6ab444af456bccc7a1164095",
                    "name": "Test-File.txt",
                    "description": "",
                    "size": 26458,
                    "path_collection": {
                        "total_count": 2,
                        "entries": [
                            {
                                "type": "folder",
                                "id": "0",
                                "sequence_id": null,
                                "etag": null,
                                "name": "All Files"
                            },
                            {
                                "type": "folder",
                                "id": "2614853901",
                                "sequence_id": "4",
                                "etag": "4",
                                "name": "Test Folder"
                            }
                        ]
                    },
                    "created_at": "2025-04-25T02:10:32-07:00",
                    "modified_at": "2025-04-25T02:10:32-07:00",
                    "trashed_at": null,
                    "purged_at": null,
                    "content_created_at": "2025-04-25T02:10:32-07:00",
                    "content_modified_at": "2025-04-25T02:10:32-07:00",
                    "created_by": {
                        "type": "user",
                        "id": "226067247",
                        "name": "Test User",
                        "login": "test@example.com"
                    },
                    "modified_by": {
                        "type": "user",
                        "id": "226067247",
                        "name": "Test User",
                        "login": "test@example.com"
                    },
                    "owned_by": {
                        "type": "user",
                        "id": "226067247",
                        "name": "Test User",
                        "login": "test@example.com"
                    },
                    "shared_link": null,
                    "parent": {
                        "type": "folder",
                        "id": "2614853901",
                        "sequence_id": "4",
                        "etag": "4",
                        "name": "Test Folder"
                    },
                    "item_status": "active"
                }
            }
            
            # Handle event
            result = event_handler.handle_event(event_data)
            
            # Return results
            return {
                "success": result,
                "event_handled": result
            }
        
        except Exception as e:
            logger.error(f"Error testing webhook event: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all webhook tests.
        
        Returns:
            dict: Test results
        """
        results = {
            "ngrok_connection": self.test_ngrok_connection(),
            "webhook_server": self.test_webhook_server(),
            "webhook_creation": self.test_webhook_creation(),
            "webhook_event": self.test_webhook_event()
        }
        
        # Calculate overall success
        overall_success = all(test["success"] for test in results.values())
        
        # Add overall success to results
        results["overall_success"] = overall_success
        
        return results


class WebhookTestingInterface:
    """
    Interface for testing Box webhooks.
    """
    
    def __init__(self, client=None):
        """
        Initialize the webhook testing interface.
        
        Args:
            client: Box client instance
        """
        self.client = client
        self.tester = WebhookTester(client)
    
    def render_webhook_testing(self):
        """Render the webhook testing interface."""
        try:
            st.subheader("Webhook Testing")
            st.write("Test your Box webhook integration.")
            
            # Check if client is available
            if "client" not in st.session_state or not st.session_state.client:
                st.warning("Please authenticate with Box to test webhooks.")
                return
            
            # Run tests button
            if st.button("Run All Tests"):
                with st.spinner("Running tests..."):
                    results = self.tester.run_all_tests()
                    
                    # Display overall results
                    if results["overall_success"]:
                        st.success("All tests passed!")
                    else:
                        st.error("Some tests failed. See details below.")
                    
                    # Display test results
                    with st.expander("Test Results", expanded=True):
                        # Ngrok connection test
                        st.write("**Ngrok Connection Test**")
                        ngrok_results = results["ngrok_connection"]
                        
                        if ngrok_results["success"]:
                            st.success("Ngrok connection test passed")
                        else:
                            st.error("Ngrok connection test failed")
                        
                        st.write(f"- Ngrok running: {ngrok_results['is_running']}")
                        st.write(f"- Public URL: {ngrok_results['public_url']}")
                        st.write(f"- URL reachable: {ngrok_results['url_reachable']}")
                        
                        if "error" in ngrok_results:
                            st.write(f"- Error: {ngrok_results['error']}")
                        
                        st.write("---")
                        
                        # Webhook server test
                        st.write("**Webhook Server Test**")
                        server_results = results["webhook_server"]
                        
                        if server_results["success"]:
                            st.success("Webhook server test passed")
                        else:
                            st.error("Webhook server test failed")
                        
                        st.write(f"- Server running: {server_results['is_running']}")
                        st.write(f"- Webhook URL: {server_results['webhook_url']}")
                        st.write(f"- URL reachable: {server_results['url_reachable']}")
                        
                        if "error" in server_results:
                            st.write(f"- Error: {server_results['error']}")
                        
                        st.write("---")
                        
                        # Webhook creation test
                        st.write("**Webhook Creation Test**")
                        creation_results = results["webhook_creation"]
                        
                        if creation_results["success"]:
                            st.success("Webhook creation test passed")
                        else:
                            st.error("Webhook creation test failed")
                        
                        if "webhook" in creation_results:
                            webhook = creation_results["webhook"]
                            st.write(f"- Webhook ID: {webhook['id']}")
                            st.write(f"- Target: {webhook['target']['type']} {webhook['target']['id']}")
                            st.write(f"- Address: {webhook['address']}")
                            st.write(f"- Triggers: {', '.join(webhook['triggers'])}")
                        
                        if "webhook_found" in creation_results:
                            st.write(f"- Webhook found in list: {creation_results['webhook_found']}")
                        
                        if "error" in creation_results:
                            st.write(f"- Error: {creation_results['error']}")
                        
                        st.write("---")
                        
                        # Webhook event test
                        st.write("**Webhook Event Test**")
                        event_results = results["webhook_event"]
                        
                        if event_results["success"]:
                            st.success("Webhook event test passed")
                        else:
                            st.error("Webhook event test failed")
                        
                        if "event_handled" in event_results:
                            st.write(f"- Event handled: {event_results['event_handled']}")
                        
                        if "error" in event_results:
                            st.write(f"- Error: {event_results['error']}")
            
            # Individual test buttons
            st.write("---")
            st.write("Individual Tests")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Test Ngrok Connection", use_container_width=True):
                    with st.spinner("Testing ngrok connection..."):
                        results = self.tester.test_ngrok_connection()
                        
                        if results["success"]:
                            st.success("Ngrok connection test passed")
                        else:
                            st.error("Ngrok connection test failed")
                        
                        st.write(f"- Ngrok running: {results['is_running']}")
                        st.write(f"- Public URL: {results['public_url']}")
                        st.write(f"- URL reachable: {results['url_reachable']}")
                        
                        if "error" in results:
                            st.write(f"- Error: {results['error']}")
            
            with col2:
                if st.button("Test Webhook Server", use_container_width=True):
                    with st.spinner("Testing webhook server..."):
                        results = self.tester.test_webhook_server()
                        
                        if results["success"]:
                            st.success("Webhook server test passed")
                        else:
                            st.error("Webhook server test failed")
                        
                        st.write(f"- Server running: {results['is_running']}")
                        st.write(f"- Webhook URL: {results['webhook_url']}")
                        st.write(f"- URL reachable: {results['url_reachable']}")
                        
                        if "error" in results:
                            st.write(f"- Error: {results['error']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Test Webhook Creation", use_container_width=True):
                    with st.spinner("Testing webhook creation..."):
                        results = self.tester.test_webhook_creation()
                        
                        if results["success"]:
                            st.success("Webhook creation test passed")
                        else:
                            st.error("Webhook creation test failed")
                        
                        if "webhook" in results:
                            webhook = results["webhook"]
                            st.write(f"- Webhook ID: {webhook['id']}")
                            st.write(f"- Target: {webhook['target']['type']} {webhook['target']['id']}")
                            st.write(f"- Address: {webhook['address']}")
                            st.write(f"- Triggers: {', '.join(webhook['triggers'])}")
                        
                        if "webhook_found" in results:
                            st.write(f"- Webhook found in list: {results['webhook_found']}")
                        
                        if "error" in results:
                            st.write(f"- Error: {results['error']}")
            
            with col2:
                if st.button("Test Webhook Event", use_container_width=True):
                    with st.spinner("Testing webhook event..."):
                        results = self.tester.test_webhook_event()
                        
                        if results["success"]:
                            st.success("Webhook event test passed")
                        else:
                            st.error("Webhook event test failed")
                        
                        if "event_handled" in results:
                            st.write(f"- Event handled: {results['event_handled']}")
                        
                        if "error" in results:
                            st.write(f"- Error: {results['error']}")
        
        except Exception as e:
            logger.error(f"Error rendering webhook testing: {str(e)}", exc_info=True)
            st.error(f"Error rendering webhook testing: {str(e)}")


# Global instance
_webhook_tester = None

def get_webhook_tester(client=None) -> WebhookTester:
    """
    Get the global webhook tester instance.
    
    Args:
        client: Box client instance
        
    Returns:
        WebhookTester: Global webhook tester instance
    """
    global _webhook_tester
    
    if _webhook_tester is None:
        _webhook_tester = WebhookTester(client)
    elif client is not None:
        _webhook_tester.client = client
    
    return _webhook_tester

def render_webhook_testing():
    """
    Standalone wrapper for render_webhook_testing.
    """
    logger.info("Calling render_webhook_testing standalone function")
    interface = WebhookTestingInterface()
    
    # Get client from session state
    if "client" in st.session_state:
        interface.client = st.session_state.client
        interface.tester.client = st.session_state.client
    
    return interface.render_webhook_testing()

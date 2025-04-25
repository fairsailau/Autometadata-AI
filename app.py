"""
Main application module for Box metadata extraction.
This module provides the main Streamlit application for Box metadata extraction.
"""

import os
import logging
import streamlit as st
from typing import Dict, Any, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import modules
from modules.authentication import render_authentication, authenticate_with_oauth, authenticate_with_jwt, authenticate_with_developer_token
from modules.session_state_manager import initialize_session_state
from modules.configuration_interface import render_configuration_interface, render_workflow_selection_standalone
from modules.metadata_template_retrieval import get_metadata_templates
from modules.webhook_integration import get_webhook_interface
from modules.webhook_server import start_webhook_server, stop_webhook_server, is_webhook_server_running

# Initialize session state
initialize_session_state()

# Set page config
st.set_page_config(
    page_title="Box Metadata Extraction",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

def render_header():
    """Render the application header."""
    st.title("Box Metadata Extraction")
    st.write("Extract and apply metadata to Box files using AI")

def render_sidebar():
    """Render the application sidebar."""
    with st.sidebar:
        st.header("Box Metadata Extraction")
        st.write("Extract and apply metadata to Box files using AI")
        
        st.divider()
        
        # Workflow mode selection
        st.subheader("Workflow Mode")
        render_workflow_selection_standalone()
        
        st.divider()
        
        # Authentication status
        st.subheader("Box Authentication")
        
        if st.session_state.authenticated:
            st.success(f"You are already authenticated as {st.session_state.user_name}!")
            
            # Refresh metadata templates button
            if st.button("Refresh Metadata Templates"):
                with st.spinner("Refreshing metadata templates..."):
                    templates = get_metadata_templates(st.session_state.client)
                    
                    if templates:
                        st.session_state.metadata_templates = templates
                        st.success(f"Found {len(templates)} metadata templates")
                    else:
                        st.error("Failed to retrieve metadata templates")
        else:
            st.warning("Not authenticated")
            
            # Authentication button
            if st.button("Go to Authentication"):
                st.session_state.current_page = "Authentication"
                st.rerun()
        
        # Webhook status
        if st.session_state.authenticated:
            st.divider()
            st.subheader("Webhook Status")
            
            # Check if webhook server is running
            webhook_running = is_webhook_server_running()
            
            if webhook_running:
                st.success("Webhook server is running")
                
                # Stop webhook server button
                if st.button("Stop Webhook Server"):
                    if stop_webhook_server():
                        st.success("Webhook server stopped successfully")
                        st.rerun()
                    else:
                        st.error("Failed to stop webhook server")
            else:
                st.warning("Webhook server is not running")
                
                # Start webhook server button
                if st.button("Start Webhook Server"):
                    # Get configuration
                    from modules.configuration_interface import get_automated_workflow_config
                    config = get_automated_workflow_config()
                    
                    # Get webhook port and primary key
                    webhook_port = config.get_webhook_port()
                    webhook_primary_key = config.config.get("webhook_primary_key", "")
                    
                    # Start webhook server
                    if start_webhook_server(webhook_port, st.session_state.client, webhook_primary_key):
                        st.success("Webhook server started successfully")
                        st.rerun()
                    else:
                        st.error("Failed to start webhook server")
            
            # Webhook configuration button
            if st.button("Configure Webhooks"):
                st.session_state.current_page = "Webhooks"
                st.rerun()
        
        st.divider()
        
        # Footer
        st.caption("© 2024 Box Metadata Extraction")
        st.caption(f"Version 2.0.0")

def render_home_page():
    """Render the home page."""
    st.header("Home")
    st.write("Configure your automated workflow using the sidebar options.")
    
    # Check if authenticated
    if not st.session_state.authenticated:
        st.warning("Please authenticate with Box to use this application.")
        
        # Authentication button
        if st.button("Go to Authentication"):
            st.session_state.current_page = "Authentication"
            st.rerun()
        
        return
    
    # Check workflow mode
    workflow_mode = st.session_state.workflow_mode
    
    if workflow_mode == "automated":
        # Display automated workflow warning
        st.warning("Automated workflow is not running.")
        
        # Start automated workflow button
        if st.button("Start Automated Workflow"):
            st.success("Automated workflow started successfully")
            st.session_state.automated_workflow_running = True
            st.rerun()
    else:
        # Display manual workflow options
        st.info("Use the sidebar to navigate to different sections of the application.")
        
        # File browser button
        if st.button("Go to File Browser"):
            st.session_state.current_page = "File Browser"
            st.rerun()

def render_authentication_page():
    """Render the authentication page."""
    st.header("Box Authentication")
    
    # Render authentication interface
    client = render_authentication()
    
    # If authenticated, store client in session state
    if client:
        st.session_state.client = client
        st.session_state.authenticated = True
        
        # Get user info
        user = client.user().get()
        st.session_state.user_name = user.name
        
        # Get metadata templates
        with st.spinner("Loading metadata templates..."):
            templates = get_metadata_templates(client)
            
            if templates:
                st.session_state.metadata_templates = templates
                st.success(f"Found {len(templates)} metadata templates")
            else:
                st.warning("No metadata templates found")
        
        # Redirect to home page
        st.session_state.current_page = "Home"
        st.rerun()

def render_file_browser_page():
    """Render the file browser page."""
    st.header("File Browser")
    
    # Check if authenticated
    if not st.session_state.authenticated:
        st.warning("Please authenticate with Box to use this application.")
        
        # Authentication button
        if st.button("Go to Authentication"):
            st.session_state.current_page = "Authentication"
            st.rerun()
        
        return
    
    # Import file browser module
    from modules.file_browser import render_file_browser
    
    # Render file browser
    render_file_browser(st.session_state.client)

def render_configuration_page():
    """Render the configuration page."""
    st.header("Metadata Configuration")
    st.write("Configure your automated workflow using the sidebar options.")
    
    # Check if authenticated
    if not st.session_state.authenticated:
        st.warning("Please authenticate with Box to use this application.")
        
        # Authentication button
        if st.button("Go to Authentication"):
            st.session_state.current_page = "Authentication"
            st.rerun()
        
        return
    
    # Render configuration interface
    render_configuration_interface()

def render_webhooks_page():
    """Render the webhooks page."""
    st.header("Box Webhooks")
    st.write("Configure Box webhooks for automated metadata extraction.")
    
    # Check if authenticated
    if not st.session_state.authenticated:
        st.warning("Please authenticate with Box to use this application.")
        
        # Authentication button
        if st.button("Go to Authentication"):
            st.session_state.current_page = "Authentication"
            st.rerun()
        
        return
    
    # Get webhook interface
    webhook_interface = get_webhook_interface(st.session_state.client)
    
    # Render webhook configuration
    webhook_interface.render_webhook_configuration()

def main():
    """Main application entry point."""
    try:
        # Render sidebar
        render_sidebar()
        
        # Render current page
        current_page = st.session_state.current_page
        
        if current_page == "Home":
            render_home_page()
        elif current_page == "Authentication":
            render_authentication_page()
        elif current_page == "File Browser":
            render_file_browser_page()
        elif current_page == "Configuration":
            render_configuration_page()
        elif current_page == "Webhooks":
            render_webhooks_page()
        else:
            st.error(f"Unknown page: {current_page}")
            st.session_state.current_page = "Home"
            st.rerun()
        
        logger.info(f"Rendered page: {current_page}")
    
    except Exception as e:
        logger.error(f"Error in main application: {str(e)}", exc_info=True)
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()

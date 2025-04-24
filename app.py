"""
Main application module with integrated automated workflow.
"""

import os
import streamlit as st
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import modules
from modules.authentication import authenticate
from modules.file_browser import file_browser
from modules.document_categorization import categorize_document
from modules.metadata_template_retrieval import get_metadata_templates
from modules.metadata_config import metadata_config
from modules.processing import process_files
from modules.results_viewer import display_results
from modules.direct_metadata_application_enhanced_fixed import apply_metadata_to_files
from modules.session_state_manager import initialize_session_state, get_session_state

# Import automated workflow modules
from modules.configuration_interface import (
    render_workflow_selection,
    render_configuration_interface,
    render_monitoring_dashboard,
    get_automated_workflow_config
)
from modules.integration import (
    initialize_automated_workflow,
    shutdown_automated_workflow,
    is_event_stream_running
)

def main():
    """Main application function."""
    # Set page config
    st.set_page_config(
        page_title="Box Metadata Extraction",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Display header
    st.title("Box Metadata Extraction")
    
    # Authenticate
    client = authenticate()
    
    if client:
        # Get session state
        session_state = get_session_state()
        
        # Display sidebar
        display_sidebar(client)
        
        # Render workflow selection
        render_workflow_selection(client)
        
        # Get workflow configuration
        config = get_automated_workflow_config()
        
        # Check if automated workflow is enabled
        if config.is_enabled():
            # Display automated workflow interface
            display_automated_workflow_interface(client)
        else:
            # Display manual workflow interface
            display_manual_workflow_interface(client)
    else:
        st.error("Authentication failed. Please check your credentials.")

def display_sidebar(client):
    """
    Display sidebar with application information and controls.
    
    Args:
        client: Box client instance
    """
    with st.sidebar:
        st.header("Navigation")
        
        # Get workflow configuration
        config = get_automated_workflow_config()
        
        # Create navigation options based on workflow mode
        if config.is_enabled():
            # Automated workflow navigation
            page = st.radio(
                "Select Page",
                ["Dashboard", "Configuration", "Manual Processing"],
                index=0
            )
            
            # Store selected page in session state
            st.session_state.selected_page = page
            
            # Display event stream status
            if is_event_stream_running():
                st.success("Event Stream: Running")
            else:
                st.error("Event Stream: Stopped")
                
                # Start button
                if st.button("Start Event Stream"):
                    if initialize_automated_workflow(client):
                        st.success("Event stream started")
                        st.rerun()
                    else:
                        st.error("Failed to start event stream")
        else:
            # Manual workflow navigation
            page = st.radio(
                "Select Page",
                ["Manual Processing", "Configuration"],
                index=0
            )
            
            # Store selected page in session state
            st.session_state.selected_page = page
            
            # Stop event stream if running
            if is_event_stream_running():
                if st.button("Stop Event Stream"):
                    if shutdown_automated_workflow():
                        st.success("Event stream stopped")
                        st.rerun()
                    else:
                        st.error("Failed to stop event stream")
        
        # Display application information
        st.header("About")
        st.info(
            "Box Metadata Extraction Application\n\n"
            "This application extracts metadata from Box files using Box AI "
            "and applies it to files."
        )
        
        # Display version information
        st.text(f"Version: 2.0.0")
        st.text(f"Last Updated: {datetime.now().strftime('%Y-%m-%d')}")

def display_automated_workflow_interface(client):
    """
    Display automated workflow interface.
    
    Args:
        client: Box client instance
    """
    # Get selected page from session state
    selected_page = st.session_state.get("selected_page", "Dashboard")
    
    if selected_page == "Dashboard":
        # Display monitoring dashboard
        render_monitoring_dashboard(client)
    elif selected_page == "Configuration":
        # Display configuration interface
        render_configuration_interface(client)
    elif selected_page == "Manual Processing":
        # Display manual workflow interface
        display_manual_workflow_interface(client)

def display_manual_workflow_interface(client):
    """
    Display manual workflow interface.
    
    Args:
        client: Box client instance
    """
    # Create tabs for workflow steps
    tabs = st.tabs([
        "1. Select Files",
        "2. Configure Metadata",
        "3. Process Files",
        "4. Review Results",
        "5. Apply Metadata"
    ])
    
    # Tab 1: Select Files
    with tabs[0]:
        display_file_browser(client)
    
    # Tab 2: Configure Metadata
    with tabs[1]:
        display_metadata_config(client)
    
    # Tab 3: Process Files
    with tabs[2]:
        process_files(client)
    
    # Tab 4: Review Results
    with tabs[3]:
        display_results(client)
    
    # Tab 5: Apply Metadata
    with tabs[4]:
        apply_metadata_to_files(client)

if __name__ == "__main__":
    main()

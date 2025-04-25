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

# Set page config - MOVED HERE FROM main() function
st.set_page_config(
    page_title="Box Metadata Extraction",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import modules
from modules.authentication import authenticate
from modules.file_browser import file_browser
from modules.document_categorization import document_categorization
from modules.metadata_template_retrieval import get_metadata_templates, initialize_template_state
from modules.metadata_config import metadata_config
from modules.processing import process_files
from modules.results_viewer import view_results
from modules.direct_metadata_application_enhanced_fixed import apply_metadata_direct
from modules.session_state_manager import initialize_session_state, get_session_state, debug_session_state

# Import automated workflow modules
from modules.configuration_interface import (
    render_workflow_selection,
    render_configuration_interface,
    get_automated_workflow_config
)
from modules.integration import (
    initialize_automated_workflow,
    shutdown_automated_workflow,
    is_event_stream_running
)

def render_home_page(client):
    """Render the home page content."""
    st.write("Welcome to Box Metadata Extraction!")
    st.write("This application helps you extract metadata from Box files using AI and apply it back to the files.")
    st.write("To get started, authenticate with Box using the sidebar and then navigate to the File Browser.")
    
    # Display user journey guide
    from modules.user_journey_guide import user_journey_guide, display_step_help
    user_journey_guide("Home")
    display_step_help("Home")
    
    # Display status
    if client and st.session_state.authenticated:
        st.success("✅ Authentication successful! You can now browse your Box files.")
        st.write("Click on 'File Browser' in the sidebar to continue.")
        
        # Add a direct navigation button to make progression easier
        if st.button("Go to File Browser", type="primary", use_container_width=True):
            st.session_state.current_page = "File Browser"
            st.rerun()
    else:
        st.warning("⚠️ Please authenticate with Box to continue.")

def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Initialize template state
    initialize_template_state()
    
    # Get session state
    session_state = get_session_state()
    
    # Add debugging - dump session state at the beginning of each render
    debug_info = debug_session_state()
    logger.info(f"Session state at start of main(): {debug_info}")
    
    # Display sidebar
    with st.sidebar:
        # Display application title
        st.title("Box Metadata Extraction")
        st.write("Extract and apply metadata to Box files using AI")
        st.write("---")
        
        # Display workflow selection - store the returned workflow mode
        workflow_mode = render_workflow_selection()
        logger.info(f"Workflow mode after render_workflow_selection: {workflow_mode}")
        
        # Display authentication section
        client = authenticate()
        
        # Log authentication status
        logger.info(f"Authentication status: authenticated={st.session_state.authenticated}, client={'present' if client else 'None'}")
        
        # Force navigation to Home page after successful authentication
        if client and st.session_state.authenticated:
            # Store client in session state to ensure it's available throughout the app
            st.session_state.client = client
            logger.info("Client stored in session state")
            
            # Load metadata templates if authenticated
            if "metadata_templates" not in st.session_state or not st.session_state.metadata_templates:
                logger.info("Loading metadata templates after authentication")
                templates = get_metadata_templates(client)
                logger.info(f"Loaded {len(templates)} metadata templates")
            
            # This is a newly authenticated session, trigger a rerun to ensure proper rendering
            if "just_authenticated" not in st.session_state:
                logger.info("Setting just_authenticated flag and triggering rerun")
                st.session_state.just_authenticated = True
                st.rerun()
        
        # Add refresh templates button if authenticated
        if client and st.session_state.authenticated:
            if st.button("Refresh Metadata Templates", key="refresh_templates_button"):
                logger.info("Refreshing metadata templates")
                templates = get_metadata_templates(client, force_refresh=True)
                logger.info(f"Refreshed {len(templates)} metadata templates")
                st.success(f"Refreshed {len(templates)} metadata templates")
        
        # Display automated workflow configuration if selected and authenticated
        if workflow_mode == "automated" and client and st.session_state.authenticated:
            logger.info("Rendering automated workflow configuration")
            render_configuration_interface()
        elif workflow_mode == "automated" and not (client and st.session_state.authenticated):
            st.warning("Please authenticate with Box to configure automated workflow.")
        
        # Display manual workflow navigation if selected
        elif workflow_mode == "manual":
            # Navigation
            st.write("### Navigation")
            
            # Define pages
            pages = {
                "Home": "🏠",
                "File Browser": "📁",
                "Document Categorization": "🏷️",
                "Metadata Configuration": "⚙️",
                "Process Files": "🔄",
                "View Results": "👁️",
                "Apply Metadata": "✅"
            }
            
            # Create navigation buttons
            for page, icon in pages.items():
                if st.button(f"{icon} {page}", key=f"nav_{page}", use_container_width=True):
                    logger.info(f"Navigation button clicked: {page}")
                    st.session_state.current_page = page
                    st.rerun()
        
        # Display footer
        st.write("---")
        st.write("© 2024 Box Metadata Extraction")
        st.write("Version 2.0.0")
    
    # Get current page
    current_page = st.session_state.current_page
    logger.info(f"Current page: {current_page}")
    
    # Display page header
    st.header(f"{current_page}")
    
    # Display main content based on workflow mode and current page
    if workflow_mode == "manual":
        logger.info(f"Rendering manual workflow content for page: {current_page}")
        
        # Home page
        if current_page == "Home":
            render_home_page(client)
        
        # File Browser page
        elif current_page == "File Browser":
            if client and st.session_state.authenticated:
                file_browser()
            else:
                st.warning("⚠️ Please authenticate with Box to browse files.")
                if st.button("Go to Authentication", type="primary"):
                    st.session_state.current_page = "Home"
                    st.rerun()
        
        # Document Categorization page
        elif current_page == "Document Categorization":
            if client and st.session_state.authenticated:
                document_categorization()
            else:
                st.warning("⚠️ Please authenticate with Box to categorize documents.")
                if st.button("Go to Authentication", type="primary"):
                    st.session_state.current_page = "Home"
                    st.rerun()
        
        # Metadata Configuration page
        elif current_page == "Metadata Configuration":
            if client and st.session_state.authenticated:
                metadata_config()
            else:
                st.warning("⚠️ Please authenticate with Box to configure metadata.")
                if st.button("Go to Authentication", type="primary"):
                    st.session_state.current_page = "Home"
                    st.rerun()
        
        # Process Files page
        elif current_page == "Process Files":
            if client and st.session_state.authenticated:
                process_files()
            else:
                st.warning("⚠️ Please authenticate with Box to process files.")
                if st.button("Go to Authentication", type="primary"):
                    st.session_state.current_page = "Home"
                    st.rerun()
        
        # View Results page
        elif current_page == "View Results":
            if client and st.session_state.authenticated:
                view_results()
            else:
                st.warning("⚠️ Please authenticate with Box to view results.")
                if st.button("Go to Authentication", type="primary"):
                    st.session_state.current_page = "Home"
                    st.rerun()
        
        # Apply Metadata page
        elif current_page == "Apply Metadata":
            if client and st.session_state.authenticated:
                apply_metadata_direct(client)
            else:
                st.warning("⚠️ Please authenticate with Box to apply metadata.")
                if st.button("Go to Authentication", type="primary"):
                    st.session_state.current_page = "Home"
                    st.rerun()
    
    # Display content for automated workflow mode
    elif workflow_mode == "automated":
        logger.info("Rendering automated workflow content")
        if client and st.session_state.authenticated:
            st.write("Configure your automated workflow using the sidebar options.")
            
            # Display automated workflow status
            if is_event_stream_running():
                st.info("🔄 Automated workflow is running. New files in monitored folders will be processed automatically.")
                
                # Add stop button
                if st.button("Stop Automated Workflow", type="primary", use_container_width=True):
                    shutdown_automated_workflow()
                    st.rerun()
            else:
                st.warning("⚠️ Automated workflow is not running.")
                
                # Add start button if configuration is valid
                config = get_automated_workflow_config()
                if config and config.get_monitored_folders():
                    if st.button("Start Automated Workflow", type="primary", use_container_width=True):
                        initialize_automated_workflow(client)
                        st.rerun()
                else:
                    st.error("⛔ Please configure monitored folders in the sidebar before starting the automated workflow.")
        else:
            st.warning("⚠️ Please authenticate with Box to configure and start the automated workflow.")
    
    # Add debugging - dump session state at the end of each render
    end_debug_info = debug_session_state()
    logger.info(f"Session state at end of main(): {end_debug_info}")

if __name__ == "__main__":
    main()

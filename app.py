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
from modules.document_categorization import categorize_document
from modules.metadata_template_retrieval import get_metadata_templates
from modules.metadata_config import metadata_config
from modules.processing import process_files
from modules.results_viewer import view_results
from modules.direct_metadata_application_enhanced_fixed import apply_metadata_direct
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
    # Initialize session state
    initialize_session_state()
    
    # Get session state
    session_state = get_session_state()
    
    # Display sidebar
    with st.sidebar:
        # Display application title
        st.title("Box Metadata Extraction")
        st.write("Extract and apply metadata to Box files using AI")
        st.write("---")
        
        # Display workflow selection
        workflow_mode = render_workflow_selection()
        
        # Display authentication section
        client = authenticate()
        
        # Display automated workflow configuration if selected
        if workflow_mode == "automated":
            render_configuration_interface(client)
            
            # Display monitoring dashboard if authenticated
            if client and st.session_state.authenticated:
                render_monitoring_dashboard(client)
        
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
                    st.session_state.current_page = page
                    st.rerun()
        
        # Display footer
        st.write("---")
        st.write("© 2024 Box Metadata Extraction")
        st.write("Version 2.0.0")
    
    # Display main content based on current page
    if workflow_mode == "manual":
        # Get current page
        current_page = st.session_state.current_page
        
        # Display page content
        st.header(f"{current_page}")
        
        # Home page
        if current_page == "Home":
            st.write("Welcome to Box Metadata Extraction!")
            st.write("This application helps you extract metadata from Box files using AI and apply it back to the files.")
            st.write("To get started, authenticate with Box using the sidebar and then navigate to the File Browser.")
            
            # Display user journey guide
            from modules.user_journey_guide import user_journey_guide, display_step_help
            user_journey_guide(current_page)
            display_step_help(current_page)
            
            # Display status
            if client and st.session_state.authenticated:
                st.success("✅ Authentication successful! You can now browse your Box files.")
                st.write("Click on 'File Browser' in the sidebar to continue.")
            else:
                st.warning("⚠️ Please authenticate with Box to continue.")
        
        # File Browser page
        elif current_page == "File Browser":
            file_browser()
        
        # Document Categorization page
        elif current_page == "Document Categorization":
            categorize_document(client)
        
        # Metadata Configuration page
        elif current_page == "Metadata Configuration":
            metadata_config()
        
        # Process Files page
        elif current_page == "Process Files":
            process_files()
        
        # View Results page
        elif current_page == "View Results":
            view_results()
        
        # Apply Metadata page
        elif current_page == "Apply Metadata":
            apply_metadata_direct(client)

if __name__ == "__main__":
    main()

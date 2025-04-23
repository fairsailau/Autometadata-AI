"""
Configuration interface module for automated workflow.
This module provides UI components for configuring the automated workflow.
"""

import os
import json
import logging
import time
import threading
import streamlit as st
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomatedWorkflowConfig:
    """
    Configuration manager for automated workflow.
    """
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.config = {}
        self.config_lock = threading.RLock()
        self.config_path = os.path.join(os.path.dirname(__file__), '..', '.automated_workflow_config.json')
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                logger.error(f"Error loading configuration: {str(e)}")
                self.config = self._get_default_config()
        else:
            self.config = self._get_default_config()
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration.
        
        Returns:
            dict: Default configuration
        """
        return {
            "enabled": False,
            "monitored_folders": [],
            "confidence_threshold": 0.7,
            "ai_model": "default",
            "webhook_port": 5000,
            "updated_at": datetime.now().isoformat()
        }
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration.
        
        Returns:
            dict: Current configuration
        """
        with self.config_lock:
            return self.config.copy()
    
    def update_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update configuration.
        
        Args:
            updates: Configuration updates
            
        Returns:
            dict: Updated configuration
        """
        with self.config_lock:
            self.config.update(updates)
            self.config["updated_at"] = datetime.now().isoformat()
            self._save_config()
            return self.config.copy()
    
    def is_enabled(self) -> bool:
        """
        Check if automated workflow is enabled.
        
        Returns:
            bool: True if enabled, False otherwise
        """
        return self.config.get("enabled", False)
    
    def get_monitored_folders(self) -> List[Dict[str, Any]]:
        """
        Get monitored folders.
        
        Returns:
            list: Monitored folders
        """
        return self.config.get("monitored_folders", [])
    
    def add_monitored_folder(self, folder_id: str, folder_name: str) -> bool:
        """
        Add a folder to monitor.
        
        Args:
            folder_id: Box folder ID
            folder_name: Folder name
            
        Returns:
            bool: True if folder was added, False otherwise
        """
        with self.config_lock:
            # Check if folder already exists
            folders = self.config.get("monitored_folders", [])
            
            for folder in folders:
                if folder.get("id") == folder_id:
                    return False
            
            # Add folder
            folders.append({
                "id": folder_id,
                "name": folder_name,
                "added_at": datetime.now().isoformat()
            })
            
            self.config["monitored_folders"] = folders
            self.config["updated_at"] = datetime.now().isoformat()
            self._save_config()
            
            return True
    
    def remove_monitored_folder(self, folder_id: str) -> bool:
        """
        Remove a monitored folder.
        
        Args:
            folder_id: Box folder ID
            
        Returns:
            bool: True if folder was removed, False otherwise
        """
        with self.config_lock:
            # Check if folder exists
            folders = self.config.get("monitored_folders", [])
            
            for i, folder in enumerate(folders):
                if folder.get("id") == folder_id:
                    # Remove folder
                    folders.pop(i)
                    
                    self.config["monitored_folders"] = folders
                    self.config["updated_at"] = datetime.now().isoformat()
                    self._save_config()
                    
                    return True
            
            return False
    
    def get_confidence_threshold(self) -> float:
        """
        Get confidence threshold.
        
        Returns:
            float: Confidence threshold
        """
        return self.config.get("confidence_threshold", 0.7)
    
    def set_confidence_threshold(self, threshold: float) -> bool:
        """
        Set confidence threshold.
        
        Args:
            threshold: Confidence threshold (0.0-1.0)
            
        Returns:
            bool: True if threshold was set, False otherwise
        """
        if 0.0 <= threshold <= 1.0:
            with self.config_lock:
                self.config["confidence_threshold"] = threshold
                self.config["updated_at"] = datetime.now().isoformat()
                self._save_config()
                return True
        
        return False
    
    def get_ai_model(self) -> str:
        """
        Get AI model.
        
        Returns:
            str: AI model
        """
        return self.config.get("ai_model", "default")
    
    def set_ai_model(self, model: str) -> bool:
        """
        Set AI model.
        
        Args:
            model: AI model
            
        Returns:
            bool: True if model was set, False otherwise
        """
        with self.config_lock:
            self.config["ai_model"] = model
            self.config["updated_at"] = datetime.now().isoformat()
            self._save_config()
            return True
    
    def get_webhook_port(self) -> int:
        """
        Get webhook port.
        
        Returns:
            int: Webhook port
        """
        return self.config.get("webhook_port", 5000)
    
    def set_webhook_port(self, port: int) -> bool:
        """
        Set webhook port.
        
        Args:
            port: Webhook port
            
        Returns:
            bool: True if port was set, False otherwise
        """
        if 1024 <= port <= 65535:
            with self.config_lock:
                self.config["webhook_port"] = port
                self.config["updated_at"] = datetime.now().isoformat()
                self._save_config()
                return True
        
        return False
    
    def enable_automated_workflow(self) -> bool:
        """
        Enable automated workflow.
        
        Returns:
            bool: True if workflow was enabled, False otherwise
        """
        with self.config_lock:
            self.config["enabled"] = True
            self.config["updated_at"] = datetime.now().isoformat()
            self._save_config()
            return True
    
    def disable_automated_workflow(self) -> bool:
        """
        Disable automated workflow.
        
        Returns:
            bool: True if workflow was disabled, False otherwise
        """
        with self.config_lock:
            self.config["enabled"] = False
            self.config["updated_at"] = datetime.now().isoformat()
            self._save_config()
            return True


class ConfigurationInterface:
    """
    Streamlit interface for configuring automated workflow.
    """
    
    def __init__(self, client=None):
        """
        Initialize the configuration interface.
        
        Args:
            client: Box client instance
        """
        self.client = client
        self.config_manager = AutomatedWorkflowConfig()
    
    def set_client(self, client):
        """
        Set the Box client.
        
        Args:
            client: Box client instance
        """
        self.client = client
    
    def render_workflow_selection(self):
        """Render workflow selection interface."""
        st.subheader("Workflow Selection")
        
        # Get current configuration
        config = self.config_manager.get_config()
        enabled = config.get("enabled", False)
        
        # Create columns for layout
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Display workflow options
            workflow_option = st.radio(
                "Select Workflow Mode:",
                ["Manual Processing", "Automated Processing"],
                index=1 if enabled else 0,
                horizontal=True
            )
            
            # Update configuration based on selection
            if workflow_option == "Automated Processing" and not enabled:
                self.config_manager.enable_automated_workflow()
                st.success("Automated workflow enabled")
            elif workflow_option == "Manual Processing" and enabled:
                self.config_manager.disable_automated_workflow()
                st.success("Automated workflow disabled")
        
        with col2:
            # Display status
            status = "Active" if enabled else "Inactive"
            status_color = "green" if enabled else "red"
            
            st.markdown(
                f"<div style='background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>"
                f"<p style='margin-bottom: 5px;'>Automated Workflow</p>"
                f"<p style='color: {status_color}; font-weight: bold; margin: 0;'>{status}</p>"
                f"</div>",
                unsafe_allow_html=True
            )
    
    def render_configuration_interface(self):
        """Render configuration interface."""
        st.header("Automated Workflow Configuration")
        
        # Create tabs for different configuration sections
        tabs = st.tabs([
            "Folder Selection", 
            "AI Model Configuration", 
            "Template Mapping", 
            "Advanced Settings"
        ])
        
        # Folder Selection tab
        with tabs[0]:
            self._render_folder_selection()
        
        # AI Model Configuration tab
        with tabs[1]:
            self._render_ai_model_configuration()
        
        # Template Mapping tab
        with tabs[2]:
            self._render_template_mapping()
        
        # Advanced Settings tab
        with tabs[3]:
            self._render_advanced_settings()
    
    def _render_folder_selection(self):
        """Render folder selection interface."""
        st.subheader("Folder Selection")
        st.write("Select Box folders to monitor for new file uploads:")
        
        # Get current monitored folders
        monitored_folders = self.config_manager.get_monitored_folders()
        
        # Display current monitored folders
        if monitored_folders:
            st.write("Currently monitored folders:")
            
            for i, folder in enumerate(monitored_folders):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"{i+1}. {folder.get('name', 'Unknown')} (ID: {folder.get('id', 'Unknown')})")
                
                with col2:
                    if st.button(f"Remove", key=f"remove_folder_{i}"):
                        if self.config_manager.remove_monitored_folder(folder.get('id')):
                            st.success(f"Removed folder: {folder.get('name', 'Unknown')}")
                            st.rerun()
        else:
            st.info("No folders are currently being monitored.")
        
        # Add new folder
        st.write("Add a new folder to monitor:")
        
        # Create columns for layout
        col1, col2 = st.columns([3, 1])
        
        with col1:
            folder_id = st.text_input("Folder ID", key="new_folder_id")
            folder_name = st.text_input("Folder Name", key="new_folder_name")
        
        with col2:
            st.write("")
            st.write("")
            if st.button("Add Folder", key="add_folder"):
                if folder_id and folder_name:
                    if self.config_manager.add_monitored_folder(folder_id, folder_name):
                        st.success(f"Added folder: {folder_name}")
                        st.rerun()
                    else:
                        st.error("Folder already exists")
                else:
                    st.error("Folder ID and Name are required")
        
        # Browse folders button
        if st.button("Browse Box Folders", key="browse_folders"):
            st.session_state.show_folder_browser = True
        
        # Show folder browser if requested
        if hasattr(st.session_state, 'show_folder_browser') and st.session_state.show_folder_browser:
            self._render_folder_browser()
    
    def _render_folder_browser(self):
        """Render folder browser interface."""
        st.subheader("Box Folder Browser")
        
        if not self.client:
            st.error("Box client not initialized")
            return
        
        try:
            # Get root folder
            root_folder = self.client.folder(folder_id='0').get()
            
            # Display folder contents
            self._display_folder_contents(root_folder)
        
        except Exception as e:
            st.error(f"Error browsing folders: {str(e)}")
    
    def _display_folder_contents(self, folder):
        """
        Display folder contents.
        
        Args:
            folder: Box folder
        """
        try:
            # Get folder items
            items = folder.get_items(limit=100)
            
            # Filter for folders only
            folders = [item for item in items if item.type == 'folder']
            
            # Display folders
            for f in folders:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"📁 {f.name} (ID: {f.id})")
                
                with col2:
                    if st.button(f"Select", key=f"select_folder_{f.id}"):
                        if self.config_manager.add_monitored_folder(f.id, f.name):
                            st.success(f"Added folder: {f.name}")
                            st.session_state.show_folder_browser = False
                            st.rerun()
                        else:
                            st.error("Folder already exists")
                    
                    if st.button(f"Open", key=f"open_folder_{f.id}"):
                        st.session_state.current_folder = f
                        st.rerun()
            
            # Back button if not in root folder
            if hasattr(st.session_state, 'current_folder'):
                if st.button("Back to Parent Folder"):
                    # Get parent folder
                    parent = st.session_state.current_folder.parent()
                    st.session_state.current_folder = parent
                    st.rerun()
        
        except Exception as e:
            st.error(f"Error displaying folder contents: {str(e)}")
    
    def _render_ai_model_configuration(self):
        """Render AI model configuration interface."""
        st.subheader("AI Model Configuration")
        
        # Get current configuration
        config = self.config_manager.get_config()
        current_model = config.get("ai_model", "default")
        confidence_threshold = config.get("confidence_threshold", 0.7)
        
        # AI model selection
        st.write("Select AI model for document categorization:")
        
        model_options = ["default", "enhanced", "specialized"]
        model_descriptions = {
            "default": "Standard Box AI model for general document categorization",
            "enhanced": "Enhanced model with improved accuracy for business documents",
            "specialized": "Specialized model for complex document types"
        }
        
        selected_model = st.selectbox(
            "AI Model",
            model_options,
            index=model_options.index(current_model) if current_model in model_options else 0,
            format_func=lambda x: f"{x.capitalize()} - {model_descriptions[x]}"
        )
        
        if selected_model != current_model:
            if self.config_manager.set_ai_model(selected_model):
                st.success(f"AI model updated to: {selected_model}")
        
        # Confidence threshold
        st.write("Set confidence threshold for automatic processing:")
        
        threshold = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=confidence_threshold,
            step=0.05,
            format="%.2f",
            help="Documents with confidence below this threshold will be flagged for manual review"
        )
        
        if threshold != confidence_threshold:
            if self.config_manager.set_confidence_threshold(threshold):
                st.success(f"Confidence threshold updated to: {threshold:.2f}")
        
        # Display confidence level explanation
        st.info("""
        **Confidence Threshold Explanation:**
        - **High (0.8-1.0):** Very strict, most documents will require manual review
        - **Medium (0.6-0.8):** Balanced, only uncertain categorizations will require review
        - **Low (0.0-0.6):** Permissive, most documents will be processed automatically
        """)
    
    def _render_template_mapping(self):
        """Render template mapping interface."""
        st.subheader("Category-Template Mapping")
        st.write("Define mappings between document categories and metadata templates:")
        
        # Import template mapping service
        from modules.template_processing import get_automated_processing_service
        
        # Get processing service
        processing_service = get_automated_processing_service(self.client)
        
        # Get current mappings
        mappings = processing_service.get_all_template_mappings()
        
        # Display current mappings
        if mappings:
            st.write("Current mappings:")
            
            for category, mapping in mappings.items():
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                
                with col1:
                    st.write(f"**Category:** {category}")
                
                with col2:
                    st.write(f"**Template:** {mapping.get('template_key', 'Unknown')}")
                
                with col3:
                    st.write(f"**Scope:** {mapping.get('template_scope', 'enterprise')}")
                
                with col4:
                    if st.button(f"Remove", key=f"remove_mapping_{category}"):
                        if processing_service.delete_template_mapping(category):
                            st.success(f"Removed mapping for category: {category}")
                            st.rerun()
        else:
            st.info("No mappings defined yet.")
        
        # Add new mapping
        st.write("Add a new mapping:")
        
        # Create columns for layout
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        
        with col1:
            category = st.text_input("Document Category", key="new_mapping_category")
        
        with col2:
            template_key = st.text_input("Template Key", key="new_mapping_template_key")
        
        with col3:
            template_scope = st.selectbox(
                "Scope",
                ["enterprise", "global"],
                index=0,
                key="new_mapping_template_scope"
            )
        
        with col4:
            st.write("")
            st.write("")
            if st.button("Add Mapping", key="add_mapping"):
                if category and template_key:
                    if processing_service.set_template_mapping(category, template_key, template_scope):
                        st.success(f"Added mapping: {category} -> {template_key}")
                        st.rerun()
                    else:
                        st.error("Error adding mapping")
                else:
                    st.error("Category and Template Key are required")
        
        # Template browser button
        if st.button("Browse Templates", key="browse_templates"):
            st.session_state.show_template_browser = True
        
        # Show template browser if requested
        if hasattr(st.session_state, 'show_template_browser') and st.session_state.show_template_browser:
            self._render_template_browser()
    
    def _render_template_browser(self):
        """Render template browser interface."""
        st.subheader("Metadata Template Browser")
        
        if not self.client:
            st.error("Box client not initialized")
            return
        
        try:
            # Import template retrieval module
            from modules.metadata_template_retrieval import get_metadata_templates
            
            # Get templates
            templates = get_metadata_templates(self.client)
            
            # Display templates
            if templates:
                st.write("Available templates:")
                
                for template in templates:
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**Template:** {template.get('templateKey', 'Unknown')}")
                    
                    with col2:
                        st.write(f"**Display Name:** {template.get('displayName', 'Unknown')}")
                    
                    with col3:
                        if st.button(f"Select", key=f"select_template_{template.get('templateKey', '')}"):
                            # Store selected template
                            st.session_state.selected_template = template
                            st.session_state.show_template_browser = False
                            
                            # Pre-fill template key
                            st.session_state.new_mapping_template_key = template.get('templateKey', '')
                            st.session_state.new_mapping_template_scope = template.get('scope', 'enterprise')
                            
                            st.rerun()
            else:
                st.info("No templates available.")
        
        except Exception as e:
            st.error(f"Error browsing templates: {str(e)}")
    
    def _render_advanced_settings(self):
        """Render advanced settings interface."""
        st.subheader("Advanced Settings")
        
        # Get current configuration
        config = self.config_manager.get_config()
        webhook_port = config.get("webhook_port", 5000)
        
        # Webhook port
        st.write("Configure webhook listener port:")
        
        port = st.number_input(
            "Webhook Port",
            min_value=1024,
            max_value=65535,
            value=webhook_port,
            step=1,
            help="Port for the webhook listener service"
        )
        
        if port != webhook_port:
            if self.config_manager.set_webhook_port(port):
                st.success(f"Webhook port updated to: {port}")
        
        # Webhook URL
        st.write("Webhook URL:")
        
        # Get public IP (placeholder)
        public_url = f"https://your-server-address:{port}/webhook"
        
        st.code(public_url)
        st.info("You need to ensure this URL is publicly accessible and properly secured with HTTPS.")
        
        # Advanced options
        st.write("Advanced Options:")
        
        # Create columns for layout
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Reset Configuration", key="reset_config"):
                # Confirm reset
                st.session_state.confirm_reset = True
        
        with col2:
            if st.button("Export Configuration", key="export_config"):
                # Export configuration
                st.session_state.export_config = True
        
        # Confirm reset
        if hasattr(st.session_state, 'confirm_reset') and st.session_state.confirm_reset:
            st.warning("Are you sure you want to reset all configuration?")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Yes, Reset", key="confirm_reset_yes"):
                    # Reset configuration
                    self.config_manager.update_config(self.config_manager._get_default_config())
                    st.success("Configuration reset to defaults")
                    st.session_state.confirm_reset = False
                    st.rerun()
            
            with col2:
                if st.button("Cancel", key="confirm_reset_cancel"):
                    st.session_state.confirm_reset = False
                    st.rerun()
        
        # Export configuration
        if hasattr(st.session_state, 'export_config') and st.session_state.export_config:
            # Get configuration
            config_json = json.dumps(self.config_manager.get_config(), indent=2)
            
            # Display configuration
            st.code(config_json)
            
            # Clear export flag
            st.session_state.export_config = False
    
    def render_monitoring_dashboard(self):
        """Render monitoring dashboard."""
        st.header("Monitoring Dashboard")
        
        # Create tabs for different dashboard sections
        tabs = st.tabs([
            "Processing Status", 
            "Review Queue", 
            "Processing History"
        ])
        
        # Processing Status tab
        with tabs[0]:
            self._render_processing_status()
        
        # Review Queue tab
        with tabs[1]:
            self._render_review_queue()
        
        # Processing History tab
        with tabs[2]:
            self._render_processing_history()
    
    def _render_processing_status(self):
        """Render processing status dashboard."""
        st.subheader("Processing Status")
        
        # Get configuration
        config = self.config_manager.get_config()
        enabled = config.get("enabled", False)
        
        # Display status
        if enabled:
            st.success("Automated workflow is active")
        else:
            st.warning("Automated workflow is inactive")
        
        # Display monitored folders
        monitored_folders = self.config_manager.get_monitored_folders()
        
        if monitored_folders:
            st.write(f"Monitoring {len(monitored_folders)} folders:")
            
            for folder in monitored_folders:
                st.write(f"- {folder.get('name', 'Unknown')} (ID: {folder.get('id', 'Unknown')})")
        else:
            st.info("No folders are being monitored.")
        
        # Display webhook status
        try:
            # Import event stream module
            from modules.event_stream import get_webhook_listener
            
            # Get webhook listener
            webhook_listener = get_webhook_listener()
            
            if webhook_listener.running:
                st.success("Webhook listener is running")
            else:
                st.warning("Webhook listener is not running")
        except Exception as e:
            st.error(f"Error checking webhook status: {str(e)}")
        
        # Display processing metrics (placeholder)
        st.subheader("Processing Metrics")
        
        # Create columns for metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Files Processed", "0")
        
        with col2:
            st.metric("Auto-Processed", "0")
        
        with col3:
            st.metric("Manual Review", "0")
        
        # Display processing rate chart (placeholder)
        st.subheader("Processing Rate")
        st.line_chart({"Processing Rate": [0, 0, 0, 0, 0]})
    
    def _render_review_queue(self):
        """Render review queue dashboard."""
        st.subheader("Manual Review Queue")
        
        # Import automated categorization module
        from modules.automated_categorization import get_automated_categorization
        
        # Get automated categorization instance
        automated_categorization = get_automated_categorization(self.client)
        
        # Get review queue
        review_queue = automated_categorization.get_review_queue()
        
        if review_queue:
            st.write(f"{len(review_queue)} files require manual review:")
            
            for i, item in enumerate(review_queue):
                with st.expander(f"{item.get('file_name', 'Unknown File')} - {item.get('category', 'Unknown')} ({item.get('confidence', 0.0):.2f})"):
                    # Display item details
                    st.write(f"**File ID:** {item.get('file_id', 'Unknown')}")
                    st.write(f"**Category:** {item.get('category', 'Unknown')}")
                    st.write(f"**Confidence:** {item.get('confidence', 0.0):.2f}")
                    st.write(f"**Reasoning:** {item.get('reasoning', 'No reasoning provided')}")
                    st.write(f"**Status:** {item.get('status', 'pending')}")
                    
                    # Create columns for actions
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("Approve", key=f"approve_{i}"):
                            # Update status
                            automated_categorization.update_review_item(
                                item.get('file_id', ''),
                                {"status": "approved"}
                            )
                            st.success("Approved")
                            st.rerun()
                    
                    with col2:
                        if st.button("Reject", key=f"reject_{i}"):
                            # Update status
                            automated_categorization.update_review_item(
                                item.get('file_id', ''),
                                {"status": "rejected"}
                            )
                            st.success("Rejected")
                            st.rerun()
                    
                    with col3:
                        # Category correction
                        new_category = st.text_input(
                            "Correct Category",
                            value=item.get('category', ''),
                            key=f"correct_category_{i}"
                        )
                        
                        if st.button("Update Category", key=f"update_category_{i}"):
                            # Provide feedback
                            automated_categorization.provide_categorization_feedback(
                                item.get('file_id', ''),
                                item.get('category', ''),
                                new_category,
                                item.get('file_name', '')
                            )
                            st.success("Category updated")
                            st.rerun()
        else:
            st.info("No files in review queue.")
    
    def _render_processing_history(self):
        """Render processing history dashboard."""
        st.subheader("Processing History")
        
        # Import template processing module
        from modules.template_processing import get_automated_processing_service
        
        # Get processing service
        processing_service = get_automated_processing_service(self.client)
        
        # Get processing history
        history = processing_service.get_processing_history(limit=50)
        
        if history:
            st.write(f"Recent processing history ({len(history)} entries):")
            
            for i, entry in enumerate(history):
                # Get result
                result = entry.get('result', {})
                status = result.get('status', 'unknown')
                file_id = result.get('file_id', 'unknown')
                category = result.get('category', 'unknown')
                
                # Determine status color
                status_color = "green" if status == "success" else "red"
                
                # Create expander
                with st.expander(f"{i+1}. {category} - {status}"):
                    # Display entry details
                    st.write(f"**File ID:** {file_id}")
                    st.write(f"**Category:** {category}")
                    st.write(f"**Status:** <span style='color: {status_color};'>{status}</span>", unsafe_allow_html=True)
                    
                    # Display template info
                    template_key = result.get('template_key', 'unknown')
                    template_scope = result.get('template_scope', 'enterprise')
                    st.write(f"**Template:** {template_key} ({template_scope})")
                    
                    # Display timestamps
                    timestamp = result.get('timestamp', 'unknown')
                    st.write(f"**Processed:** {timestamp}")
                    
                    # Display error if any
                    if 'error' in result:
                        st.error(f"Error: {result['error']}")
        else:
            st.info("No processing history available.")


# Global instance
_configuration_interface = None

def get_configuration_interface(client=None) -> ConfigurationInterface:
    """
    Get the global configuration interface instance.
    
    Args:
        client: Box client instance
        
    Returns:
        ConfigurationInterface: Global configuration interface instance
    """
    global _configuration_interface
    
    if _configuration_interface is None:
        _configuration_interface = ConfigurationInterface(client)
    elif client is not None:
        _configuration_interface.set_client(client)
    
    return _configuration_interface

def render_workflow_selection(client=None):
    """
    Render workflow selection interface.
    
    Args:
        client: Box client instance
    """
    # Get configuration interface
    interface = get_configuration_interface(client)
    
    # Render workflow selection
    interface.render_workflow_selection()

def render_configuration_interface(client=None):
    """
    Render configuration interface.
    
    Args:
        client: Box client instance
    """
    # Get configuration interface
    interface = get_configuration_interface(client)
    
    # Render configuration interface
    interface.render_configuration_interface()

def render_monitoring_dashboard(client=None):
    """
    Render monitoring dashboard.
    
    Args:
        client: Box client instance
    """
    # Get configuration interface
    interface = get_configuration_interface(client)
    
    # Render monitoring dashboard
    interface.render_monitoring_dashboard()

def get_automated_workflow_config() -> AutomatedWorkflowConfig:
    """
    Get the global automated workflow configuration instance.
    
    Returns:
        AutomatedWorkflowConfig: Global configuration instance
    """
    return AutomatedWorkflowConfig()

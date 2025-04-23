"""
Configuration interface module for automated workflow.
This module provides interfaces for configuring the automated workflow.
"""

import os
import json
import logging
import streamlit as st
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomatedWorkflowConfig:
    """
    Configuration for automated workflow.
    """
    
    def __init__(self):
        """Initialize the configuration."""
        self.config_path = os.path.join(os.path.dirname(__file__), '..', '.config', 'automated_workflow.json')
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            dict: Configuration
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading configuration: {str(e)}")
        
        # Return default configuration if file doesn't exist or has errors
        return {
            "enabled": False,
            "webhook_port": 5000,
            "confidence_threshold": 0.7,
            "monitored_folders": [],
            "category_template_mapping": {},
            "ai_model": "default",
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Update last updated timestamp
            self.config["last_updated"] = datetime.now().isoformat()
            
            # Save configuration
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
    
    def is_enabled(self) -> bool:
        """
        Check if automated workflow is enabled.
        
        Returns:
            bool: True if enabled, False otherwise
        """
        return self.config.get("enabled", False)
    
    def set_enabled(self, enabled: bool):
        """
        Set whether automated workflow is enabled.
        
        Args:
            enabled: Whether automated workflow is enabled
        """
        self.config["enabled"] = enabled
        self._save_config()
    
    def get_webhook_port(self) -> int:
        """
        Get webhook port.
        
        Returns:
            int: Webhook port
        """
        return self.config.get("webhook_port", 5000)
    
    def set_webhook_port(self, port: int):
        """
        Set webhook port.
        
        Args:
            port: Webhook port
        """
        self.config["webhook_port"] = port
        self._save_config()
    
    def get_confidence_threshold(self) -> float:
        """
        Get confidence threshold.
        
        Returns:
            float: Confidence threshold
        """
        return self.config.get("confidence_threshold", 0.7)
    
    def set_confidence_threshold(self, threshold: float):
        """
        Set confidence threshold.
        
        Args:
            threshold: Confidence threshold
        """
        self.config["confidence_threshold"] = threshold
        self._save_config()
    
    def get_monitored_folders(self) -> List[Dict[str, Any]]:
        """
        Get monitored folders.
        
        Returns:
            list: List of monitored folders
        """
        return self.config.get("monitored_folders", [])
    
    def add_monitored_folder(self, folder_id: str, folder_name: str):
        """
        Add a monitored folder.
        
        Args:
            folder_id: Box folder ID
            folder_name: Box folder name
        """
        # Check if folder already exists
        for folder in self.get_monitored_folders():
            if folder.get("id") == folder_id:
                return
        
        # Add folder
        monitored_folders = self.get_monitored_folders()
        monitored_folders.append({
            "id": folder_id,
            "name": folder_name,
            "added_at": datetime.now().isoformat()
        })
        
        self.config["monitored_folders"] = monitored_folders
        self._save_config()
    
    def remove_monitored_folder(self, folder_id: str):
        """
        Remove a monitored folder.
        
        Args:
            folder_id: Box folder ID
        """
        monitored_folders = self.get_monitored_folders()
        self.config["monitored_folders"] = [f for f in monitored_folders if f.get("id") != folder_id]
        self._save_config()
    
    def get_category_template_mapping(self) -> Dict[str, str]:
        """
        Get category to template mapping.
        
        Returns:
            dict: Mapping from category to template ID
        """
        return self.config.get("category_template_mapping", {})
    
    def set_category_template_mapping(self, category: str, template_id: str):
        """
        Set category to template mapping.
        
        Args:
            category: Document category
            template_id: Metadata template ID
        """
        category_template_mapping = self.get_category_template_mapping()
        category_template_mapping[category] = template_id
        
        self.config["category_template_mapping"] = category_template_mapping
        self._save_config()
    
    def remove_category_template_mapping(self, category: str):
        """
        Remove category to template mapping.
        
        Args:
            category: Document category
        """
        category_template_mapping = self.get_category_template_mapping()
        
        if category in category_template_mapping:
            del category_template_mapping[category]
            
            self.config["category_template_mapping"] = category_template_mapping
            self._save_config()
    
    def get_ai_model(self) -> str:
        """
        Get AI model.
        
        Returns:
            str: AI model
        """
        return self.config.get("ai_model", "default")
    
    def set_ai_model(self, model: str):
        """
        Set AI model.
        
        Args:
            model: AI model
        """
        self.config["ai_model"] = model
        self._save_config()
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get full configuration.
        
        Returns:
            dict: Configuration
        """
        return self.config


# Global instance
_config = None

def get_automated_workflow_config() -> AutomatedWorkflowConfig:
    """
    Get the global configuration instance.
    
    Returns:
        AutomatedWorkflowConfig: Global configuration instance
    """
    global _config
    
    if _config is None:
        _config = AutomatedWorkflowConfig()
    
    return _config


class ConfigurationInterface:
    """
    Interface for configuring automated workflow.
    """
    
    def __init__(self, client=None):
        """
        Initialize the configuration interface.
        
        Args:
            client: Box client instance
        """
        self.client = client
        self.config = get_automated_workflow_config()
    
    def set_client(self, client):
        """
        Set the Box client.
        
        Args:
            client: Box client instance
        """
        self.client = client
    
    def render_workflow_selection(self):
        """Render workflow selection interface."""
        st.header("Workflow Mode")
        
        # Get current mode
        is_automated = self.config.is_enabled()
        
        # Create radio button for mode selection
        mode = st.radio(
            "Select Workflow Mode",
            ["Manual", "Automated"],
            index=1 if is_automated else 0
        )
        
        # Update configuration if mode changed
        if (mode == "Automated") != is_automated:
            self.config.set_enabled(mode == "Automated")
            
            # Show success message
            if mode == "Automated":
                st.success("Automated workflow enabled")
            else:
                st.success("Manual workflow enabled")
    
    def render_configuration_interface(self):
        """Render configuration interface."""
        st.header("Automated Workflow Configuration")
        
        # Create tabs for configuration sections
        tabs = st.tabs([
            "Folder Selection",
            "Template Mapping",
            "AI Model",
            "Advanced Settings"
        ])
        
        # Tab 1: Folder Selection
        with tabs[0]:
            self._render_folder_selection()
        
        # Tab 2: Template Mapping
        with tabs[1]:
            self._render_template_mapping()
        
        # Tab 3: AI Model
        with tabs[2]:
            self._render_ai_model_selection()
        
        # Tab 4: Advanced Settings
        with tabs[3]:
            self._render_advanced_settings()
    
    def _render_folder_selection(self):
        """Render folder selection interface."""
        st.subheader("Monitored Folders")
        st.write("Select folders to monitor for new file uploads.")
        
        # Get monitored folders
        monitored_folders = self.config.get_monitored_folders()
        
        # Display current monitored folders
        if monitored_folders:
            st.write("Currently monitored folders:")
            
            for i, folder in enumerate(monitored_folders):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"{folder.get('name')} (ID: {folder.get('id')})")
                
                with col2:
                    if st.button(f"Remove", key=f"remove_folder_{i}"):
                        self.config.remove_monitored_folder(folder.get('id'))
                        st.rerun()
        else:
            st.info("No folders are currently being monitored.")
        
        # Add new folder
        st.write("Add a new folder to monitor:")
        
        # Create columns for input fields
        col1, col2 = st.columns([3, 1])
        
        with col1:
            folder_id = st.text_input("Folder ID", key="new_folder_id")
            folder_name = st.text_input("Folder Name", key="new_folder_name")
        
        with col2:
            st.write("")
            st.write("")
            if st.button("Add Folder"):
                if folder_id and folder_name:
                    self.config.add_monitored_folder(folder_id, folder_name)
                    st.success(f"Added folder: {folder_name}")
                    st.rerun()
                else:
                    st.error("Please enter both folder ID and name.")
        
        # Folder browser
        st.write("Or browse for a folder:")
        
        if self.client:
            # Get root folder
            root_folder = self.client.folder(folder_id='0')
            
            # Display folder browser
            self._render_folder_browser(root_folder)
        else:
            st.warning("Box client not initialized. Please authenticate first.")
    
    def _render_folder_browser(self, folder):
        """
        Render folder browser.
        
        Args:
            folder: Box folder
        """
        try:
            # Get folder items
            items = folder.get_items(limit=100, offset=0)
            
            # Filter folders
            folders = [item for item in items if item.type == 'folder']
            
            # Create selectbox for folders
            if folders:
                folder_names = [".."] + [f"{f.name} (ID: {f.id})" for f in folders]
                selected_folder = st.selectbox("Select Folder", folder_names, key=f"folder_browser_{folder.id}")
                
                if selected_folder == "..":
                    # Go up one level
                    if folder.id != '0':
                        parent = folder.get()['parent']
                        if parent:
                            self._render_folder_browser(self.client.folder(folder_id=parent['id']))
                else:
                    # Extract folder ID
                    selected_id = selected_folder.split("(ID: ")[1].split(")")[0]
                    
                    # Get selected folder
                    selected_folder_obj = self.client.folder(folder_id=selected_id)
                    
                    # Display selected folder
                    st.write(f"Selected: {selected_folder_obj.name} (ID: {selected_folder_obj.id})")
                    
                    # Add button
                    if st.button("Monitor This Folder"):
                        self.config.add_monitored_folder(selected_folder_obj.id, selected_folder_obj.name)
                        st.success(f"Added folder: {selected_folder_obj.name}")
                        st.rerun()
                    
                    # Navigate to selected folder
                    self._render_folder_browser(selected_folder_obj)
            else:
                st.info("No subfolders found.")
                
                # Go up one level
                if folder.id != '0':
                    if st.button("Go Up One Level"):
                        parent = folder.get()['parent']
                        if parent:
                            self._render_folder_browser(self.client.folder(folder_id=parent['id']))
        
        except Exception as e:
            st.error(f"Error browsing folders: {str(e)}")
    
    def _render_template_mapping(self):
        """Render template mapping interface."""
        st.subheader("Category to Template Mapping")
        st.write("Map document categories to metadata templates.")
        
        # Get category template mapping
        category_template_mapping = self.config.get_category_template_mapping()
        
        # Get available templates
        templates = self._get_available_templates()
        
        # Get available categories
        categories = self._get_available_categories()
        
        # Display current mappings
        if category_template_mapping:
            st.write("Current mappings:")
            
            for i, (category, template_id) in enumerate(category_template_mapping.items()):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"Category: {category}")
                
                with col2:
                    template_name = "Unknown"
                    for template in templates:
                        if template.get("id") == template_id:
                            template_name = template.get("templateKey")
                            break
                    
                    st.write(f"Template: {template_name}")
                
                with col3:
                    if st.button(f"Remove", key=f"remove_mapping_{i}"):
                        self.config.remove_category_template_mapping(category)
                        st.rerun()
        else:
            st.info("No category to template mappings defined.")
        
        # Add new mapping
        st.write("Add a new mapping:")
        
        # Create columns for input fields
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            # Create selectbox for categories
            category_options = [""] + categories
            selected_category = st.selectbox("Category", category_options, key="new_mapping_category")
        
        with col2:
            # Create selectbox for templates
            template_options = [""] + [f"{t.get('templateKey')} (ID: {t.get('id')})" for t in templates]
            selected_template = st.selectbox("Template", template_options, key="new_mapping_template")
        
        with col3:
            st.write("")
            st.write("")
            if st.button("Add Mapping"):
                if selected_category and selected_template and selected_category != "" and selected_template != "":
                    # Extract template ID
                    template_id = selected_template.split("(ID: ")[1].split(")")[0]
                    
                    # Add mapping
                    self.config.set_category_template_mapping(selected_category, template_id)
                    st.success(f"Added mapping: {selected_category} -> {selected_template}")
                    st.rerun()
                else:
                    st.error("Please select both category and template.")
    
    def _get_available_templates(self) -> List[Dict[str, Any]]:
        """
        Get available metadata templates.
        
        Returns:
            list: List of metadata templates
        """
        if not self.client:
            return []
        
        try:
            # Import metadata template retrieval module
            from modules.metadata_template_retrieval import get_metadata_templates
            
            # Get enterprise ID
            enterprise_id = self._get_enterprise_id()
            
            if not enterprise_id:
                return []
            
            # Get templates
            templates = get_metadata_templates(self.client, enterprise_id)
            
            return templates
        
        except Exception as e:
            logger.error(f"Error getting available templates: {str(e)}")
            return []
    
    def _get_enterprise_id(self) -> Optional[str]:
        """
        Get Box enterprise ID.
        
        Returns:
            str: Enterprise ID or None if not available
        """
        if not self.client:
            return None
        
        try:
            # Get current user
            user = self.client.user().get()
            
            # Get enterprise
            enterprise = user.enterprise
            
            if enterprise:
                return enterprise.id
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting enterprise ID: {str(e)}")
            return None
    
    def _get_available_categories(self) -> List[str]:
        """
        Get available document categories.
        
        Returns:
            list: List of document categories
        """
        # Import document categorization module
        from modules.document_categorization import get_available_categories
        
        # Get categories
        return get_available_categories()
    
    def _render_ai_model_selection(self):
        """Render AI model selection interface."""
        st.subheader("AI Model Selection")
        st.write("Select the AI model to use for document categorization and metadata extraction.")
        
        # Get current AI model
        current_model = self.config.get_ai_model()
        
        # Create radio button for model selection
        model = st.radio(
            "Select AI Model",
            ["default", "enhanced"],
            index=0 if current_model == "default" else 1
        )
        
        # Update configuration if model changed
        if model != current_model:
            self.config.set_ai_model(model)
            st.success(f"AI model set to: {model}")
        
        # Display model information
        if model == "default":
            st.info(
                "The default model provides standard document categorization and metadata extraction. "
                "It is suitable for most document types and offers good performance."
            )
        else:
            st.info(
                "The enhanced model provides more accurate document categorization and metadata extraction. "
                "It is optimized for complex documents and offers better performance, but may be slower."
            )
    
    def _render_advanced_settings(self):
        """Render advanced settings interface."""
        st.subheader("Advanced Settings")
        
        # Confidence threshold
        st.write("Confidence Threshold")
        st.write(
            "Set the confidence threshold for automatic processing. "
            "Documents with confidence below this threshold will be flagged for manual review."
        )
        
        # Get current confidence threshold
        current_threshold = self.config.get_confidence_threshold()
        
        # Create slider for confidence threshold
        threshold = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=current_threshold,
            step=0.05,
            format="%.2f"
        )
        
        # Update configuration if threshold changed
        if threshold != current_threshold:
            self.config.set_confidence_threshold(threshold)
            st.success(f"Confidence threshold set to: {threshold}")
        
        # Webhook port
        st.write("Webhook Port")
        st.write(
            "Set the port for the webhook listener. "
            "This port must be accessible from the internet for Box webhooks to work."
        )
        
        # Get current webhook port
        current_port = self.config.get_webhook_port()
        
        # Create number input for webhook port
        port = st.number_input(
            "Webhook Port",
            min_value=1024,
            max_value=65535,
            value=current_port,
            step=1
        )
        
        # Update configuration if port changed
        if port != current_port:
            self.config.set_webhook_port(int(port))
            st.success(f"Webhook port set to: {port}")
        
        # Development mode
        st.write("Development Mode")
        st.write(
            "Enable development mode for testing without actual Box webhooks. "
            "This will simulate webhook events and skip signature verification."
        )
        
        # Get current development mode
        current_dev_mode = os.environ.get('WEBHOOK_SIMULATION', 'false').lower() == 'true'
        
        # Create checkbox for development mode
        dev_mode = st.checkbox(
            "Enable Development Mode",
            value=current_dev_mode
        )
        
        # Update environment variable if development mode changed
        if dev_mode != current_dev_mode:
            os.environ['WEBHOOK_SIMULATION'] = 'true' if dev_mode else 'false'
            os.environ['WEBHOOK_SKIP_VERIFICATION'] = 'true' if dev_mode else 'false'
            
            if dev_mode:
                st.success("Development mode enabled")
            else:
                st.success("Development mode disabled")
    
    def render_monitoring_dashboard(self):
        """Render monitoring dashboard."""
        st.header("Automated Workflow Dashboard")
        
        # Create tabs for dashboard sections
        tabs = st.tabs([
            "Overview",
            "Manual Review Queue",
            "Processing History"
        ])
        
        # Tab 1: Overview
        with tabs[0]:
            self._render_dashboard_overview()
        
        # Tab 2: Manual Review Queue
        with tabs[1]:
            self._render_manual_review_queue()
        
        # Tab 3: Processing History
        with tabs[2]:
            self._render_processing_history()
    
    def _render_dashboard_overview(self):
        """Render dashboard overview."""
        st.subheader("System Status")
        
        # Check if event stream is running
        from modules.integration import is_event_stream_running
        
        if is_event_stream_running():
            st.success("Event Stream: Running")
        else:
            st.error("Event Stream: Stopped")
            
            # Start button
            if st.button("Start Event Stream"):
                from modules.integration import initialize_automated_workflow
                
                if initialize_automated_workflow(self.client):
                    st.success("Event stream started")
                    st.rerun()
                else:
                    st.error("Failed to start event stream")
        
        # Display configuration summary
        st.subheader("Configuration Summary")
        
        # Get configuration
        config = self.config.get_config()
        
        # Create columns for configuration summary
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Monitored Folders:")
            st.write(f"{len(config.get('monitored_folders', []))} folders")
            
            st.write("Confidence Threshold:")
            st.write(f"{config.get('confidence_threshold', 0.7)}")
            
            st.write("Last Updated:")
            st.write(f"{config.get('last_updated', 'Never')}")
        
        with col2:
            st.write("Category Mappings:")
            st.write(f"{len(config.get('category_template_mapping', {}))} mappings")
            
            st.write("AI Model:")
            st.write(f"{config.get('ai_model', 'default')}")
            
            st.write("Webhook Port:")
            st.write(f"{config.get('webhook_port', 5000)}")
        
        # Display processing statistics
        st.subheader("Processing Statistics")
        
        # Create columns for processing statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Files Processed", "0")
        
        with col2:
            st.metric("Automatic Processing", "0")
        
        with col3:
            st.metric("Manual Review", "0")
    
    def _render_manual_review_queue(self):
        """Render manual review queue."""
        st.subheader("Files Requiring Manual Review")
        st.write("These files had confidence scores below the threshold and require manual review.")
        
        # Placeholder for manual review queue
        st.info("No files currently in the manual review queue.")
    
    def _render_processing_history(self):
        """Render processing history."""
        st.subheader("Recent Processing History")
        st.write("Recent file processing history and results.")
        
        # Placeholder for processing history
        st.info("No processing history available.")


# Global instance
_interface = None

def get_configuration_interface(client=None) -> ConfigurationInterface:
    """
    Get the global configuration interface instance.
    
    Args:
        client: Box client instance
        
    Returns:
        ConfigurationInterface: Global configuration interface instance
    """
    global _interface
    
    if _interface is None:
        _interface = ConfigurationInterface(client)
    elif client is not None:
        _interface.set_client(client)
    
    return _interface

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

"""
Configuration interface module for the Box Metadata Extraction application.
This module provides the configuration interface for the application.
"""

import streamlit as st
import logging
import json
import os
from typing import Dict, Any, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutomatedWorkflowConfig:
    """
    Configuration for automated workflow.
    """
    
    def __init__(self):
        """Initialize configuration."""
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".config")
        self.config_file = os.path.join(self.config_dir, "automated_workflow.json")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            dict: Configuration
        """
        # Create config directory if it doesn't exist
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        
        # Create config file if it doesn't exist
        if not os.path.exists(self.config_file):
            default_config = {
                "monitored_folders": [],
                "category_template_mapping": {},
                "ai_model": "default",
                "webhook_port": 5000,
                "webhook_enabled": True,
                "advanced_settings": {
                    "confidence_threshold": 0.7,
                    "auto_apply_metadata": False,
                    "notification_enabled": False,
                    "notification_email": ""
                }
            }
            
            with open(self.config_file, "w") as f:
                json.dump(default_config, f, indent=2)
            
            return default_config
        
        # Load config from file
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            return {}
    
    def _save_config(self) -> bool:
        """
        Save configuration to file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create config directory if it doesn't exist
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)
            
            # Save config to file
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")
            return False
    
    def get_monitored_folders(self) -> List[Dict[str, Any]]:
        """
        Get monitored folders.
        
        Returns:
            list: Monitored folders
        """
        return self.config.get("monitored_folders", [])
    
    def add_monitored_folder(self, folder_id: str, folder_name: str) -> bool:
        """
        Add monitored folder.
        
        Args:
            folder_id: Folder ID
            folder_name: Folder name
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if folder already exists
        for folder in self.get_monitored_folders():
            if folder.get("id") == folder_id:
                return False
        
        # Add folder
        self.config.setdefault("monitored_folders", []).append({
            "id": folder_id,
            "name": folder_name
        })
        
        # Save config
        return self._save_config()
    
    def remove_monitored_folder(self, folder_id: str) -> bool:
        """
        Remove monitored folder.
        
        Args:
            folder_id: Folder ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if folder exists
        folders = self.get_monitored_folders()
        for i, folder in enumerate(folders):
            if folder.get("id") == folder_id:
                # Remove folder
                del folders[i]
                self.config["monitored_folders"] = folders
                
                # Save config
                return self._save_config()
        
        return False
    
    def get_category_template_mapping(self) -> Dict[str, str]:
        """
        Get category to template mapping.
        
        Returns:
            dict: Category to template mapping
        """
        return self.config.get("category_template_mapping", {})
    
    def set_category_template_mapping(self, category: str, template_id: str) -> bool:
        """
        Set category to template mapping.
        
        Args:
            category: Document category
            template_id: Template ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Set mapping
        self.config.setdefault("category_template_mapping", {})[category] = template_id
        
        # Save config
        return self._save_config()
    
    def remove_category_template_mapping(self, category: str) -> bool:
        """
        Remove category to template mapping.
        
        Args:
            category: Document category
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if mapping exists
        if category in self.get_category_template_mapping():
            # Remove mapping
            del self.config["category_template_mapping"][category]
            
            # Save config
            return self._save_config()
        
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
            bool: True if successful, False otherwise
        """
        # Set model
        self.config["ai_model"] = model
        
        # Save config
        return self._save_config()
    
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
            bool: True if successful, False otherwise
        """
        # Set port
        self.config["webhook_port"] = port
        
        # Save config
        return self._save_config()
    
    def is_webhook_enabled(self) -> bool:
        """
        Check if webhook is enabled.
        
        Returns:
            bool: True if enabled, False otherwise
        """
        return self.config.get("webhook_enabled", True)
    
    def set_webhook_enabled(self, enabled: bool) -> bool:
        """
        Set webhook enabled.
        
        Args:
            enabled: Webhook enabled
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Set enabled
        self.config["webhook_enabled"] = enabled
        
        # Save config
        return self._save_config()
    
    def get_advanced_settings(self) -> Dict[str, Any]:
        """
        Get advanced settings.
        
        Returns:
            dict: Advanced settings
        """
        return self.config.get("advanced_settings", {})
    
    def set_advanced_setting(self, key: str, value: Any) -> bool:
        """
        Set advanced setting.
        
        Args:
            key: Setting key
            value: Setting value
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Set setting
        self.config.setdefault("advanced_settings", {})[key] = value
        
        # Save config
        return self._save_config()
    
    def is_enabled(self) -> bool:
        """
        Check if automated workflow is enabled.
        
        Returns:
            bool: True if enabled, False otherwise
        """
        return self.config.get("enabled", False)
    
    def set_enabled(self, enabled: bool) -> bool:
        """
        Set automated workflow enabled.
        
        Args:
            enabled: Automated workflow enabled
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Set enabled
        self.config["enabled"] = enabled
        
        # Save config
        return self._save_config()


class ConfigurationInterface:
    """
    Configuration interface for the application.
    """
    
    def __init__(self, client=None):
        """
        Initialize the configuration interface.
        
        Args:
            client: Box client instance
        """
        self.client = client
        self.config = AutomatedWorkflowConfig()
        logger.info("ConfigurationInterface initialized")
    
    def render_workflow_selection(self):
        """Render workflow selection interface."""
        try:
            st.header("Workflow Mode")
            
            # Get current workflow mode
            if "workflow_mode" not in st.session_state:
                st.session_state.workflow_mode = "manual"
            
            # Workflow mode selection
            st.write("Select Workflow Mode")
            workflow_mode = st.radio(
                "Select Workflow Mode",
                options=["Manual", "Automated"],
                index=0 if st.session_state.workflow_mode == "manual" else 1,
                label_visibility="collapsed"
            )
            
            # Update workflow mode
            st.session_state.workflow_mode = workflow_mode.lower()
            
            logger.info("Workflow selection interface rendered successfully")
            
            # Return the workflow mode
            return st.session_state.workflow_mode
        except Exception as e:
            logger.error(f"Error rendering workflow selection: {str(e)}", exc_info=True)
            st.error(f"Error rendering workflow selection: {str(e)}")
            return "manual"  # Default to manual mode on error
    
    def render_configuration_interface(self):
        """Render configuration interface."""
        try:
            # Check if workflow mode is automated
            if st.session_state.workflow_mode != "automated":
                return
            
            st.header("Automated Workflow Configuration")
            
            # Create tabs for different configuration sections
            tabs = st.tabs([
                "Folder Selection",
                "Template Mapping",
                "AI Model",
                "Advanced Settings"
            ])
            
            # Folder selection tab
            with tabs[0]:
                self._render_folder_selection()
            
            # Template mapping tab
            with tabs[1]:
                self._render_template_mapping()
            
            # AI model tab
            with tabs[2]:
                self._render_ai_model_selection()
            
            # Advanced settings tab
            with tabs[3]:
                self._render_advanced_settings()
            
            logger.info("Configuration interface rendered successfully")
        except Exception as e:
            logger.error(f"Error rendering configuration interface: {str(e)}", exc_info=True)
            st.error(f"Error rendering configuration interface: {str(e)}")
    
    def _render_folder_selection(self):
        """Render folder selection interface."""
        try:
            st.subheader("Folder Selection")
            st.write("Select folders to monitor for new files.")
            
            # Get monitored folders
            monitored_folders = self.config.get_monitored_folders()
            
            # Display monitored folders
            if monitored_folders:
                st.write("Currently monitored folders:")
                
                for folder in monitored_folders:
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**{folder.get('name', 'Unknown')}**")
                    
                    with col2:
                        st.write(f"ID: {folder.get('id', 'Unknown')}")
                    
                    with col3:
                        if st.button("Remove", key=f"remove_folder_{folder.get('id', 'Unknown')}"):
                            self.config.remove_monitored_folder(folder.get('id', 'Unknown'))
                            st.rerun()
            else:
                st.info("No folders are currently being monitored.")
            
            # Add new folder section
            st.write("---")
            st.write("Add a new folder to monitor:")
            
            # Client must be available in session state
            if "client" not in st.session_state or not st.session_state.client:
                st.warning("Please authenticate with Box to browse folders.")
                return
            
            # Get root folder
            root_folder = st.session_state.client.folder(folder_id="0")
            
            # Current folder navigation
            if "current_folder_id" not in st.session_state:
                st.session_state.current_folder_id = "0"
                st.session_state.current_folder_name = "All Files"
                st.session_state.folder_path = [{"id": "0", "name": "All Files"}]
            
            # Display current folder path
            path_str = " / ".join([f"{folder['name']}" for folder in st.session_state.folder_path])
            st.write(f"Current location: **{path_str}**")
            
            # Display navigation buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if len(st.session_state.folder_path) > 1:
                    if st.button("⬆️ Up", use_container_width=True):
                        # Remove current folder from path
                        st.session_state.folder_path.pop()
                        
                        # Set current folder to parent
                        parent = st.session_state.folder_path[-1]
                        st.session_state.current_folder_id = parent["id"]
                        st.session_state.current_folder_name = parent["name"]
                        
                        st.rerun()
            
            with col2:
                if st.button("🔄 Refresh", use_container_width=True):
                    st.rerun()
            
            # Get current folder
            current_folder = st.session_state.client.folder(folder_id=st.session_state.current_folder_id)
            
            # Get folder items
            items = current_folder.get_items(limit=100, offset=0)
            
            # Filter folders
            folders = [item for item in items if item.type == "folder"]
            
            # Display folders
            if folders:
                st.write("Folders:")
                
                for folder in folders:
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"📁 {folder.name}")
                    
                    with col2:
                        if st.button("Open", key=f"open_folder_{folder.id}"):
                            # Add folder to path
                            st.session_state.folder_path.append({
                                "id": folder.id,
                                "name": folder.name
                            })
                            
                            # Set current folder
                            st.session_state.current_folder_id = folder.id
                            st.session_state.current_folder_name = folder.name
                            
                            st.rerun()
                        
                        if st.button("Select", key=f"select_folder_{folder.id}"):
                            # Add folder to monitored folders
                            if self.config.add_monitored_folder(folder.id, folder.name):
                                st.success(f"Added folder '{folder.name}' to monitored folders.")
                                st.rerun()
                            else:
                                st.error(f"Folder '{folder.name}' is already being monitored.")
            else:
                st.info("No folders found in the current location.")
        except Exception as e:
            logger.error(f"Error rendering folder selection: {str(e)}", exc_info=True)
            st.error(f"Error rendering folder selection: {str(e)}")
    
    def _render_template_mapping(self):
        """Render template mapping interface."""
        try:
            st.subheader("Template Mapping")
            st.write("Map document categories to metadata templates.")
            
            # Get category template mapping
            mapping = self.config.get_category_template_mapping()
            
            # Display mapping
            if mapping:
                st.write("Current mappings:")
                
                for category, template_id in mapping.items():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**{category}**")
                    
                    with col2:
                        st.write(f"Template ID: {template_id}")
                    
                    with col3:
                        if st.button("Remove", key=f"remove_mapping_{category}"):
                            self.config.remove_category_template_mapping(category)
                            st.rerun()
            else:
                st.info("No category to template mappings defined.")
            
            # Add new mapping section
            st.write("---")
            st.write("Add a new mapping:")
            
            # Get available templates
            if "metadata_templates" not in st.session_state:
                st.warning("Please authenticate with Box to get metadata templates.")
                return
            
            templates = st.session_state.metadata_templates
            
            if not templates:
                st.warning("No metadata templates found. Please create templates in Box.")
                return
            
            # Convert templates dict to list for selectbox
            template_list = list(templates.values())
            
            # Category input
            category = st.text_input("Document Category", key="new_category")
            
            # Template selection
            template_options = [f"{t['displayName']} ({t['id']})" for t in template_list]
            template_index = st.selectbox("Metadata Template", options=range(len(template_options)), format_func=lambda i: template_options[i], key="new_template")
            
            # Add mapping button
            if st.button("Add Mapping", use_container_width=True):
                if not category:
                    st.error("Please enter a document category.")
                    return
                
                template_id = template_list[template_index]["id"]
                
                if self.config.set_category_template_mapping(category, template_id):
                    st.success(f"Added mapping for category '{category}'.")
                    st.rerun()
                else:
                    st.error(f"Error adding mapping for category '{category}'.")
        except Exception as e:
            logger.error(f"Error rendering template mapping: {str(e)}", exc_info=True)
            st.error(f"Error rendering template mapping: {str(e)}")
    
    def _render_ai_model_selection(self):
        """Render AI model selection interface."""
        try:
            st.subheader("AI Model")
            st.write("Select the AI model to use for metadata extraction.")
            
            # Get current AI model
            current_model = self.config.get_ai_model()
            
            # AI model options
            models = {
                "default": "Default (Azure OpenAI GPT-4o mini)",
                "azure__openai__gpt_4o": "Azure OpenAI GPT-4o",
                "azure__openai__gpt_4o_mini": "Azure OpenAI GPT-4o mini",
                "azure__openai__gpt_35_turbo": "Azure OpenAI GPT-3.5 Turbo"
            }
            
            # Model selection
            model_options = list(models.keys())
            model_index = model_options.index(current_model) if current_model in model_options else 0
            
            selected_model = st.radio(
                "Select AI Model",
                options=model_options,
                index=model_index,
                format_func=lambda x: models.get(x, x)
            )
            
            # Update model button
            if selected_model != current_model:
                if st.button("Update AI Model", use_container_width=True):
                    if self.config.set_ai_model(selected_model):
                        st.success(f"Updated AI model to {models.get(selected_model, selected_model)}.")
                        st.rerun()
                    else:
                        st.error(f"Error updating AI model.")
        except Exception as e:
            logger.error(f"Error rendering AI model selection: {str(e)}", exc_info=True)
            st.error(f"Error rendering AI model selection: {str(e)}")
    
    def _render_advanced_settings(self):
        """Render advanced settings interface."""
        try:
            st.subheader("Advanced Settings")
            st.write("Configure advanced settings for the automated workflow.")
            
            # Get advanced settings
            settings = self.config.get_advanced_settings()
            
            # Confidence threshold
            confidence_threshold = st.slider(
                "Confidence Threshold",
                min_value=0.0,
                max_value=1.0,
                value=settings.get("confidence_threshold", 0.7),
                step=0.05,
                format="%.2f",
                help="Minimum confidence score required for document categorization"
            )
            
            # Auto apply metadata
            auto_apply_metadata = st.checkbox(
                "Auto Apply Metadata",
                value=settings.get("auto_apply_metadata", False),
                help="Automatically apply extracted metadata to files"
            )
            
            # Notification settings
            notification_enabled = st.checkbox(
                "Enable Notifications",
                value=settings.get("notification_enabled", False),
                help="Send email notifications for processed files"
            )
            
            # Email input
            notification_email = st.text_input(
                "Notification Email",
                value=settings.get("notification_email", ""),
                disabled=not notification_enabled,
                help="Email address to send notifications to"
            )
            
            # Webhook port
            webhook_port = st.number_input(
                "Webhook Port",
                min_value=1000,
                max_value=65535,
                value=self.config.get_webhook_port(),
                step=1,
                help="Port to use for webhook server"
            )
            
            # Webhook enabled
            webhook_enabled = st.checkbox(
                "Enable Webhook",
                value=self.config.is_webhook_enabled(),
                help="Enable webhook server for Box events"
            )
            
            # Save button
            if st.button("Save Advanced Settings", use_container_width=True):
                # Update settings
                self.config.set_advanced_setting("confidence_threshold", confidence_threshold)
                self.config.set_advanced_setting("auto_apply_metadata", auto_apply_metadata)
                self.config.set_advanced_setting("notification_enabled", notification_enabled)
                self.config.set_advanced_setting("notification_email", notification_email)
                self.config.set_webhook_port(webhook_port)
                self.config.set_webhook_enabled(webhook_enabled)
                
                st.success("Advanced settings saved successfully.")
                st.rerun()
        except Exception as e:
            logger.error(f"Error rendering advanced settings: {str(e)}", exc_info=True)
            st.error(f"Error rendering advanced settings: {str(e)}")


# Global instance
_config_interface = None

def get_configuration_interface(client=None) -> ConfigurationInterface:
    """
    Get the global configuration interface instance.
    
    Args:
        client: Box client instance
        
    Returns:
        ConfigurationInterface: Global configuration interface instance
    """
    global _config_interface
    
    if _config_interface is None:
        _config_interface = ConfigurationInterface(client)
    elif client is not None:
        _config_interface.client = client
    
    return _config_interface

def get_automated_workflow_config() -> AutomatedWorkflowConfig:
    """
    Get the automated workflow configuration.
    
    Returns:
        AutomatedWorkflowConfig: Automated workflow configuration
    """
    return get_configuration_interface().config

# Standalone wrapper functions for use in app.py
def render_workflow_selection():
    """
    Standalone wrapper for render_workflow_selection.
    
    Returns:
        str: Selected workflow mode
    """
    logger.info("Calling render_workflow_selection standalone function")
    return get_configuration_interface().render_workflow_selection()

def render_configuration_interface():
    """
    Standalone wrapper for render_configuration_interface.
    """
    logger.info("Calling render_configuration_interface standalone function")
    get_configuration_interface().render_configuration_interface()

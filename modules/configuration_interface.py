"""
Configuration interface module for Box metadata extraction.
This module provides the configuration interface for the Box metadata extraction application.
"""

import os
import json
import logging
import streamlit as st
from typing import Dict, Any, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomatedWorkflowConfig:
    """
    Configuration for automated workflow.
    """
    
    def __init__(self, config_file: str = None):
        """
        Initialize the automated workflow configuration.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config",
            "automated_workflow.json"
        )
        
        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            dict: Configuration
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    return json.load(f)
            else:
                return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}", exc_info=True)
            return self._get_default_config()
    
    def _save_config(self) -> bool:
        """
        Save configuration to file.
        
        Returns:
            bool: True if configuration was saved successfully, False otherwise
        """
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
            
            logger.info(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}", exc_info=True)
            return False
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration.
        
        Returns:
            dict: Default configuration
        """
        return {
            "confidence_threshold": 0.7,
            "auto_apply_metadata": False,
            "enable_notifications": False,
            "notification_email": "",
            "webhook_port": 5000,
            "enable_webhook": False,
            "ngrok_token": "",
            "webhook_primary_key": "",
            "monitored_folders": []
        }
    
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
            threshold: Confidence threshold
            
        Returns:
            bool: True if threshold was set successfully, False otherwise
        """
        try:
            self.config["confidence_threshold"] = threshold
            return self._save_config()
        except Exception as e:
            logger.error(f"Error setting confidence threshold: {str(e)}", exc_info=True)
            return False
    
    def get_auto_apply_metadata(self) -> bool:
        """
        Get auto apply metadata flag.
        
        Returns:
            bool: Auto apply metadata flag
        """
        return self.config.get("auto_apply_metadata", False)
    
    def set_auto_apply_metadata(self, auto_apply: bool) -> bool:
        """
        Set auto apply metadata flag.
        
        Args:
            auto_apply: Auto apply metadata flag
            
        Returns:
            bool: True if flag was set successfully, False otherwise
        """
        try:
            self.config["auto_apply_metadata"] = auto_apply
            return self._save_config()
        except Exception as e:
            logger.error(f"Error setting auto apply metadata flag: {str(e)}", exc_info=True)
            return False
    
    def get_enable_notifications(self) -> bool:
        """
        Get enable notifications flag.
        
        Returns:
            bool: Enable notifications flag
        """
        return self.config.get("enable_notifications", False)
    
    def set_enable_notifications(self, enable: bool) -> bool:
        """
        Set enable notifications flag.
        
        Args:
            enable: Enable notifications flag
            
        Returns:
            bool: True if flag was set successfully, False otherwise
        """
        try:
            self.config["enable_notifications"] = enable
            return self._save_config()
        except Exception as e:
            logger.error(f"Error setting enable notifications flag: {str(e)}", exc_info=True)
            return False
    
    def get_notification_email(self) -> str:
        """
        Get notification email.
        
        Returns:
            str: Notification email
        """
        return self.config.get("notification_email", "")
    
    def set_notification_email(self, email: str) -> bool:
        """
        Set notification email.
        
        Args:
            email: Notification email
            
        Returns:
            bool: True if email was set successfully, False otherwise
        """
        try:
            self.config["notification_email"] = email
            return self._save_config()
        except Exception as e:
            logger.error(f"Error setting notification email: {str(e)}", exc_info=True)
            return False
    
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
            bool: True if port was set successfully, False otherwise
        """
        try:
            self.config["webhook_port"] = port
            return self._save_config()
        except Exception as e:
            logger.error(f"Error setting webhook port: {str(e)}", exc_info=True)
            return False
    
    def get_enable_webhook(self) -> bool:
        """
        Get enable webhook flag.
        
        Returns:
            bool: Enable webhook flag
        """
        return self.config.get("enable_webhook", False)
    
    def set_enable_webhook(self, enable: bool) -> bool:
        """
        Set enable webhook flag.
        
        Args:
            enable: Enable webhook flag
            
        Returns:
            bool: True if flag was set successfully, False otherwise
        """
        try:
            self.config["enable_webhook"] = enable
            return self._save_config()
        except Exception as e:
            logger.error(f"Error setting enable webhook flag: {str(e)}", exc_info=True)
            return False
    
    def get_monitored_folders(self) -> List[str]:
        """
        Get monitored folders.
        
        Returns:
            list: Monitored folders
        """
        return self.config.get("monitored_folders", [])
    
    def set_monitored_folders(self, folders: List[str]) -> bool:
        """
        Set monitored folders.
        
        Args:
            folders: Monitored folders
            
        Returns:
            bool: True if folders were set successfully, False otherwise
        """
        try:
            self.config["monitored_folders"] = folders
            return self._save_config()
        except Exception as e:
            logger.error(f"Error setting monitored folders: {str(e)}", exc_info=True)
            return False
    
    def add_monitored_folder(self, folder: str) -> bool:
        """
        Add monitored folder.
        
        Args:
            folder: Monitored folder
            
        Returns:
            bool: True if folder was added successfully, False otherwise
        """
        try:
            folders = self.get_monitored_folders()
            
            if folder not in folders:
                folders.append(folder)
                self.config["monitored_folders"] = folders
                return self._save_config()
            
            return True
        except Exception as e:
            logger.error(f"Error adding monitored folder: {str(e)}", exc_info=True)
            return False
    
    def remove_monitored_folder(self, folder: str) -> bool:
        """
        Remove monitored folder.
        
        Args:
            folder: Monitored folder
            
        Returns:
            bool: True if folder was removed successfully, False otherwise
        """
        try:
            folders = self.get_monitored_folders()
            
            if folder in folders:
                folders.remove(folder)
                self.config["monitored_folders"] = folders
                return self._save_config()
            
            return True
        except Exception as e:
            logger.error(f"Error removing monitored folder: {str(e)}", exc_info=True)
            return False


class ConfigurationInterface:
    """
    Interface for configuring the application.
    """
    
    def __init__(self, client=None):
        """
        Initialize the configuration interface.
        
        Args:
            client: Box client instance
        """
        self.client = client
        self.config = AutomatedWorkflowConfig()
    
    def render_configuration_interface(self):
        """Render the configuration interface."""
        try:
            st.subheader("Configuration Interface")
            
            # Create tabs for different configuration sections
            tabs = st.tabs([
                "Folder Selection",
                "Template Mapping",
                "AI Model",
                "Advanced Settings"
            ])
            
            # Folder selection tab
            with tabs[0]:
                self.render_folder_selection()
            
            # Template mapping tab
            with tabs[1]:
                self.render_template_mapping()
            
            # AI model tab
            with tabs[2]:
                self.render_ai_model_selection()
            
            # Advanced settings tab
            with tabs[3]:
                self.render_advanced_settings()
            
            logger.info("Configuration interface rendered successfully")
        
        except Exception as e:
            logger.error(f"Error rendering configuration interface: {str(e)}", exc_info=True)
            st.error(f"Error rendering configuration interface: {str(e)}")
    
    def render_folder_selection(self):
        """Render the folder selection interface."""
        try:
            st.subheader("Folder Selection")
            st.write("Select folders to monitor for automated metadata extraction.")
            
            # Check if client is available
            if "client" not in st.session_state or not st.session_state.client:
                st.warning("Please authenticate with Box to select folders.")
                return
            
            # Get monitored folders
            monitored_folders = self.config.get_monitored_folders()
            
            # Display monitored folders
            if monitored_folders:
                st.write("Monitored folders:")
                
                for folder_id in monitored_folders:
                    try:
                        folder = self.client.folder(folder_id=folder_id).get()
                        
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**{folder.name}** ({folder_id})")
                        
                        with col2:
                            if st.button("Remove", key=f"remove_folder_{folder_id}"):
                                if self.config.remove_monitored_folder(folder_id):
                                    st.success(f"Folder {folder.name} removed successfully")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to remove folder {folder.name}")
                    except Exception as e:
                        st.warning(f"Error loading folder {folder_id}: {str(e)}")
                        
                        if st.button("Remove Invalid Folder", key=f"remove_invalid_folder_{folder_id}"):
                            if self.config.remove_monitored_folder(folder_id):
                                st.success(f"Invalid folder {folder_id} removed successfully")
                                st.rerun()
                            else:
                                st.error(f"Failed to remove invalid folder {folder_id}")
            else:
                st.info("No folders are currently being monitored.")
            
            # Add new folder
            st.write("---")
            st.write("Add new folder")
            
            # Get root folder
            root_folder = self.client.folder(folder_id="0").get()
            
            # Get folder items
            items = self.client.folder(folder_id="0").get_items()
            
            # Filter folders
            folders = [item for item in items if item.type == "folder"]
            
            # Create folder options
            folder_options = [{"id": folder.id, "name": folder.name} for folder in folders]
            
            # Add root folder
            folder_options.insert(0, {"id": root_folder.id, "name": "All Files"})
            
            # Create folder names for selectbox
            folder_names = [f"{folder['name']} ({folder['id']})" for folder in folder_options]
            
            # Folder selection
            selected_folder_index = st.selectbox(
                "Select folder",
                range(len(folder_names)),
                format_func=lambda i: folder_names[i]
            )
            
            selected_folder = folder_options[selected_folder_index]
            
            # Add button
            if st.button("Add Folder"):
                if selected_folder["id"] in monitored_folders:
                    st.warning(f"Folder {selected_folder['name']} is already being monitored.")
                else:
                    if self.config.add_monitored_folder(selected_folder["id"]):
                        st.success(f"Folder {selected_folder['name']} added successfully")
                        st.rerun()
                    else:
                        st.error(f"Failed to add folder {selected_folder['name']}")
        
        except Exception as e:
            logger.error(f"Error rendering folder selection: {str(e)}", exc_info=True)
            st.error(f"Error rendering folder selection: {str(e)}")
    
    def render_template_mapping(self):
        """Render the template mapping interface."""
        try:
            st.subheader("Template Mapping")
            st.write("Map document categories to metadata templates.")
            
            # Check if client is available
            if "client" not in st.session_state or not st.session_state.client:
                st.warning("Please authenticate with Box to configure template mapping.")
                return
            
            # Check if templates are available
            if "metadata_templates" not in st.session_state or not st.session_state.metadata_templates:
                st.warning("No metadata templates found. Please refresh metadata templates.")
                
                if st.button("Refresh Metadata Templates"):
                    # Import metadata template retrieval module
                    from modules.metadata_template_retrieval import get_metadata_templates
                    
                    # Get templates
                    templates = get_metadata_templates(st.session_state.client)
                    
                    if templates:
                        st.session_state.metadata_templates = templates
                        st.success(f"Found {len(templates)} metadata templates")
                        st.rerun()
                    else:
                        st.error("Failed to retrieve metadata templates")
                
                return
            
            # Get templates
            templates = st.session_state.metadata_templates
            
            # Convert templates to list for selectbox
            template_list = []
            for template_key, template in templates.items():
                template_list.append({
                    "key": template_key,
                    "display_name": template.get("displayName", template_key),
                    "template": template
                })
            
            # Sort templates by display name
            template_list.sort(key=lambda x: x["display_name"])
            
            # Get template mappings
            template_mappings = self.config.config.get("template_mappings", {})
            
            # Display existing mappings
            if template_mappings:
                st.write("Existing mappings:")
                
                for category, template_key in template_mappings.items():
                    # Find template display name
                    template_display_name = template_key
                    for template in template_list:
                        if template["key"] == template_key:
                            template_display_name = template["display_name"]
                            break
                    
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**{category}**")
                    
                    with col2:
                        st.write(f"{template_display_name}")
                    
                    with col3:
                        if st.button("Remove", key=f"remove_mapping_{category}"):
                            template_mappings.pop(category)
                            self.config.config["template_mappings"] = template_mappings
                            self.config._save_config()
                            st.success(f"Mapping for {category} removed successfully")
                            st.rerun()
            else:
                st.info("No category to template mappings defined.")
            
            # Add new mapping
            st.write("---")
            st.write("Add new mapping")
            
            # Category input
            category = st.text_input("Document Category")
            
            # Template selection
            template_options = [template["display_name"] for template in template_list]
            selected_template_index = st.selectbox(
                "Select template",
                range(len(template_options)),
                format_func=lambda i: template_options[i]
            )
            
            selected_template = template_list[selected_template_index]
            
            # Add button
            if st.button("Add Mapping"):
                if not category:
                    st.warning("Please enter a document category.")
                elif category in template_mappings:
                    st.warning(f"Mapping for {category} already exists.")
                else:
                    template_mappings[category] = selected_template["key"]
                    self.config.config["template_mappings"] = template_mappings
                    self.config._save_config()
                    st.success(f"Mapping for {category} added successfully")
                    st.rerun()
        
        except Exception as e:
            logger.error(f"Error rendering template mapping: {str(e)}", exc_info=True)
            st.error(f"Error rendering template mapping: {str(e)}")
    
    def render_ai_model_selection(self):
        """Render the AI model selection interface."""
        try:
            st.subheader("AI Model Selection")
            st.write("Select the AI model to use for metadata extraction.")
            
            # Get current model
            current_model = self.config.config.get("ai_model", "gpt-4")
            
            # Model options
            model_options = [
                "gpt-4",
                "gpt-4-turbo",
                "gpt-3.5-turbo",
                "claude-3-opus",
                "claude-3-sonnet",
                "claude-3-haiku"
            ]
            
            # Model selection
            selected_model = st.selectbox(
                "Select AI model",
                model_options,
                index=model_options.index(current_model) if current_model in model_options else 0
            )
            
            # Save button
            if st.button("Save Model Selection"):
                self.config.config["ai_model"] = selected_model
                self.config._save_config()
                st.success(f"AI model set to {selected_model}")
        
        except Exception as e:
            logger.error(f"Error rendering AI model selection: {str(e)}", exc_info=True)
            st.error(f"Error rendering AI model selection: {str(e)}")
    
    def render_advanced_settings(self):
        """Render the advanced settings interface."""
        try:
            st.subheader("Advanced Settings")
            st.write("Configure advanced settings for the automated workflow.")
            
            # Confidence threshold
            confidence_threshold = self.config.get_confidence_threshold()
            
            new_threshold = st.slider(
                "Confidence Threshold",
                min_value=0.0,
                max_value=1.0,
                value=confidence_threshold,
                step=0.01,
                help="Minimum confidence level required for metadata extraction"
            )
            
            if new_threshold != confidence_threshold:
                self.config.set_confidence_threshold(new_threshold)
            
            # Auto apply metadata
            auto_apply = self.config.get_auto_apply_metadata()
            
            new_auto_apply = st.checkbox(
                "Auto Apply Metadata",
                value=auto_apply,
                help="Automatically apply extracted metadata to files"
            )
            
            if new_auto_apply != auto_apply:
                self.config.set_auto_apply_metadata(new_auto_apply)
            
            # Enable notifications
            enable_notifications = self.config.get_enable_notifications()
            
            new_enable_notifications = st.checkbox(
                "Enable Notifications",
                value=enable_notifications,
                help="Send email notifications for metadata extraction events"
            )
            
            if new_enable_notifications != enable_notifications:
                self.config.set_enable_notifications(new_enable_notifications)
            
            # Notification email
            if new_enable_notifications:
                notification_email = self.config.get_notification_email()
                
                new_notification_email = st.text_input(
                    "Notification Email",
                    value=notification_email,
                    help="Email address to send notifications to"
                )
                
                if new_notification_email != notification_email:
                    self.config.set_notification_email(new_notification_email)
            
            # Webhook configuration
            st.write("---")
            st.subheader("Webhook Configuration")
            
            # Import webhook integration module
            from modules.webhook_integration import render_webhook_configuration
            
            # Render webhook configuration
            render_webhook_configuration()
        
        except Exception as e:
            logger.error(f"Error rendering advanced settings: {str(e)}", exc_info=True)
            st.error(f"Error rendering advanced settings: {str(e)}")


def render_workflow_selection_standalone():
    """
    Standalone wrapper for render_workflow_selection.
    """
    logger.info("Calling render_workflow_selection_standalone function")
    interface = ConfigurationInterface()
    return interface.render_workflow_selection()

def render_configuration_interface_standalone():
    """
    Standalone wrapper for render_configuration_interface.
    """
    logger.info("Calling render_configuration_interface_standalone function")
    interface = ConfigurationInterface()
    
    # Get client from session state
    if "client" in st.session_state:
        interface.client = st.session_state.client
    
    return interface.render_configuration_interface()

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
    Get the global automated workflow configuration instance.
    
    Returns:
        AutomatedWorkflowConfig: Global automated workflow configuration instance
    """
    return get_configuration_interface().config

def render_workflow_selection():
    """
    Standalone wrapper for render_workflow_selection.
    """
    logger.info("Calling render_workflow_selection standalone function")
    return get_configuration_interface().render_workflow_selection()

def render_configuration_interface():
    """
    Standalone wrapper for render_configuration_interface.
    """
    logger.info("Calling render_configuration_interface standalone function")
    return get_configuration_interface().render_configuration_interface()

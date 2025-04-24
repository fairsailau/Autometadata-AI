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
                
        # Return the selected mode to allow app.py to respond to it
        return mode
    
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
    
    # Other methods of ConfigurationInterface...
    # (rest of the class implementation)


# Add standalone functions that create an instance of ConfigurationInterface and call its methods
def render_workflow_selection(client=None):
    """
    Standalone function to render workflow selection interface.
    
    Args:
        client: Box client instance
    
    Returns:
        str: Selected workflow mode
    """
    config_interface = ConfigurationInterface(client)
    return config_interface.render_workflow_selection()

def render_configuration_interface(client=None):
    """
    Standalone function to render configuration interface.
    
    Args:
        client: Box client instance
    """
    config_interface = ConfigurationInterface(client)
    config_interface.render_configuration_interface()

def render_monitoring_dashboard(client=None):
    """
    Standalone function to render monitoring dashboard.
    
    Args:
        client: Box client instance
    """
    # Implementation would call the corresponding method on ConfigurationInterface
    # For now, just display a placeholder
    st.header("Monitoring Dashboard")
    st.write("This dashboard shows the status of the automated workflow.")
    
    if client:
        st.success("Connected to Box as: " + client.user().get().name)
    else:
        st.warning("Not connected to Box. Please authenticate first.")

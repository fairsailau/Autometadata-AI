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
        logger.info("ConfigurationInterface initialized")
    
    def set_client(self, client):
        """
        Set the Box client.
        
        Args:
            client: Box client instance
        """
        self.client = client
        logger.info("Client set in ConfigurationInterface")
    
    def render_workflow_selection(self):
        """Render workflow selection interface."""
        st.header("Workflow Mode")
        logger.info("Rendering workflow selection interface")
        
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
        return mode.lower()
    
    def render_configuration_interface(self):
        """Render configuration interface."""
        try:
            st.header("Automated Workflow Configuration")
            logger.info("Rendering configuration interface")
            
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
                
            logger.info("Configuration interface rendered successfully")
        except Exception as e:
            logger.error(f"Error rendering configuration interface: {str(e)}", exc_info=True)
            st.error(f"Error rendering configuration interface: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
    
    def _render_folder_selection(self):
        """Render folder selection interface."""
        try:
            st.subheader("Monitored Folders")
            st.write("Select folders to monitor for automated metadata extraction.")
            
            # Display current monitored folders
            monitored_folders = self.config.get_monitored_folders()
            
            if monitored_folders:
                st.write("Currently monitored folders:")
                for folder in monitored_folders:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"📁 {folder.get('name', 'Unknown')} ({folder.get('id', 'Unknown')})")
                    with col2:
                        if st.button("Remove", key=f"remove_folder_{folder.get('id')}"):
                            self.config.remove_monitored_folder(folder.get('id'))
                            st.rerun()
            else:
                st.info("No folders are currently being monitored.")
            
            # Add new folder section
            st.write("---")
            st.write("Add a new folder to monitor:")
            
            if self.client:
                # Enhanced folder selection with folder browser
                use_browser = st.checkbox("Use folder browser", value=True, 
                                         help="Browse your Box folders instead of entering folder ID manually")
                
                if use_browser:
                    # Implement folder browser
                    st.write("#### Browse Box Folders")
                    
                    # Initialize folder navigation state if not exists
                    if "folder_nav" not in st.session_state:
                        st.session_state.folder_nav = {
                            "current_folder_id": "0",  # Root folder
                            "current_folder_name": "All Files",
                            "folder_path": [{"id": "0", "name": "All Files"}],
                            "selected_folder_id": None,
                            "selected_folder_name": None
                        }
                    
                    # Display current path
                    path_html = " / ".join([f"<a href='#' id='{folder['id']}'>{folder['name']}</a>" 
                                          for folder in st.session_state.folder_nav["folder_path"]])
                    st.markdown(f"**Path:** {path_html}", unsafe_allow_html=True)
                    
                    # Get current folder contents
                    try:
                        current_folder_id = st.session_state.folder_nav["current_folder_id"]
                        folder_items = self.client.folder(folder_id=current_folder_id).get_items(limit=100)
                        
                        # Filter to only show folders
                        folders = [item for item in folder_items if item.type == "folder"]
                        
                        if folders:
                            # Display folders
                            st.write("**Select a folder:**")
                            
                            # Create a grid layout for folders
                            cols = st.columns(3)
                            for i, folder in enumerate(folders):
                                col_idx = i % 3
                                with cols[col_idx]:
                                    if st.button(f"📁 {folder.name}", key=f"folder_{folder.id}"):
                                        # Navigate to this folder
                                        st.session_state.folder_nav["current_folder_id"] = folder.id
                                        st.session_state.folder_nav["current_folder_name"] = folder.name
                                        st.session_state.folder_nav["folder_path"].append({
                                            "id": folder.id,
                                            "name": folder.name
                                        })
                                        st.rerun()
                        else:
                            st.info("No subfolders found in this location.")
                        
                        # Option to go back
                        if len(st.session_state.folder_nav["folder_path"]) > 1:
                            if st.button("⬅️ Go Back", key="go_back_folder"):
                                # Remove current folder from path
                                st.session_state.folder_nav["folder_path"].pop()
                                # Set current folder to the last one in the path
                                last_folder = st.session_state.folder_nav["folder_path"][-1]
                                st.session_state.folder_nav["current_folder_id"] = last_folder["id"]
                                st.session_state.folder_nav["current_folder_name"] = last_folder["name"]
                                st.rerun()
                        
                        # Select current folder button
                        current_folder_name = st.session_state.folder_nav["current_folder_name"]
                        current_folder_id = st.session_state.folder_nav["current_folder_id"]
                        
                        if st.button(f"Select Current Folder: {current_folder_name}", key="select_current_folder"):
                            # Add this folder to monitored folders
                            self.config.add_monitored_folder(current_folder_id, current_folder_name)
                            st.success(f"Added folder: {current_folder_name}")
                            
                            # Reset folder navigation
                            st.session_state.folder_nav = {
                                "current_folder_id": "0",
                                "current_folder_name": "All Files",
                                "folder_path": [{"id": "0", "name": "All Files"}],
                                "selected_folder_id": None,
                                "selected_folder_name": None
                            }
                            st.rerun()
                    
                    except Exception as e:
                        st.error(f"Error browsing folders: {str(e)}")
                        logger.error(f"Error browsing folders: {str(e)}", exc_info=True)
                
                else:
                    # Manual folder ID input
                    folder_id = st.text_input("Folder ID")
                    folder_name = st.text_input("Folder Name (optional)")
                    
                    if st.button("Add Folder"):
                        if folder_id:
                            if not folder_name:
                                # Try to get folder name from Box
                                try:
                                    folder = self.client.folder(folder_id).get()
                                    folder_name = folder.name
                                except Exception as e:
                                    st.error(f"Error retrieving folder name: {str(e)}")
                                    folder_name = f"Folder {folder_id}"
                            
                            self.config.add_monitored_folder(folder_id, folder_name)
                            st.success(f"Added folder: {folder_name}")
                            st.rerun()
                        else:
                            st.error("Please enter a folder ID")
            else:
                st.warning("Please authenticate with Box to add folders")
            
            # Event stream integration section
            st.write("---")
            st.subheader("Event Stream Integration")
            st.write("Configure Box event stream to automatically process new files.")
            
            # Webhook setup instructions
            with st.expander("Webhook Setup Instructions", expanded=False):
                st.write("""
                ### Setting up Box Webhooks
                
                1. Go to the [Box Developer Console](https://app.box.com/developers/console)
                2. Create a new app or select your existing app
                3. Navigate to the 'Webhooks' section
                4. Create a new webhook with the following settings:
                   - Target URL: Use the webhook URL shown below
                   - Triggers: Select 'FILE.UPLOADED' and 'FILE.COPIED'
                   - Address: Select the folders you want to monitor
                5. Save the webhook configuration
                """)
            
            # Get webhook URL
            webhook_port = self.config.get_webhook_port()
            base_url = os.environ.get('WEBHOOK_BASE_URL', 'http://localhost')
            webhook_url = f"{base_url}:{webhook_port}/webhook"
            
            st.code(webhook_url, language="text")
            st.info("Use this URL when configuring webhooks in the Box Developer Console.")
            
            # Test webhook connection
            if st.button("Test Webhook Connection"):
                try:
                    # Simulate a webhook test
                    import requests
                    response = requests.get(webhook_url, timeout=5)
                    if response.status_code == 200:
                        st.success("Webhook endpoint is accessible!")
                    else:
                        st.warning(f"Webhook endpoint returned status code: {response.status_code}")
                except Exception as e:
                    st.error(f"Error testing webhook connection: {str(e)}")
            
            logger.info("Folder selection interface rendered successfully")
        except Exception as e:
            logger.error(f"Error rendering folder selection: {str(e)}", exc_info=True)
            st.error(f"Error rendering folder selection: {str(e)}")
    
    def _render_template_mapping(self):
        """Render template mapping interface."""
        try:
            st.subheader("Template Mapping")
            st.write("Map document categories to metadata templates.")
            
            # Get metadata templates
            templates = []
            if self.client:
                try:
                    from modules.metadata_template_retrieval import get_metadata_templates
                    templates = get_metadata_templates(self.client)
                    
                    # Store templates in session state for reuse
                    if "metadata_templates" not in st.session_state or not st.session_state.metadata_templates:
                        st.session_state.metadata_templates = templates
                    
                    if not templates:
                        st.warning("No metadata templates found. Please create templates in Box.")
                except Exception as e:
                    st.error(f"Error retrieving metadata templates: {str(e)}")
                    logger.error(f"Error retrieving metadata templates: {str(e)}", exc_info=True)
            else:
                st.warning("Please authenticate with Box to retrieve metadata templates.")
            
            # Get document categories
            # In a real implementation, this would come from the document categorization module
            # For now, we'll use a placeholder list
            categories = [
                "Invoice", 
                "Contract", 
                "Resume", 
                "Report", 
                "Letter", 
                "Form", 
                "Receipt", 
                "Other"
            ]
            
            # Get current mappings
            mappings = self.config.get_category_template_mapping()
            
            # Display current mappings
            st.write("Current category to template mappings:")
            
            if mappings:
                for category, template_id in mappings.items():
                    col1, col2, col3 = st.columns([2, 3, 1])
                    
                    with col1:
                        st.write(f"**{category}**")
                    
                    with col2:
                        # Find template name
                        template_name = "Unknown Template"
                        for template in templates:
                            if template.get("id") == template_id:
                                template_name = template.get("templateKey", "Unknown Template")
                                break
                        
                        st.write(template_name)
                    
                    with col3:
                        if st.button("Remove", key=f"remove_mapping_{category}"):
                            self.config.remove_category_template_mapping(category)
                            st.rerun()
            else:
                st.info("No category to template mappings configured.")
            
            # Add new mapping section
            st.write("---")
            st.write("Add a new category to template mapping:")
            
            # Category selection
            selected_category = st.selectbox("Document Category", categories)
            
            # Template selection
            template_options = [{"id": "", "name": "Select a template..."}]
            for template in templates:
                template_options.append({
                    "id": template.get("id", ""),
                    "name": template.get("templateKey", "Unknown Template")
                })
            
            selected_template = st.selectbox(
                "Metadata Template",
                options=[t["id"] for t in template_options],
                format_func=lambda x: next((t["name"] for t in template_options if t["id"] == x), "Unknown")
            )
            
            # Add mapping button
            if st.button("Add Mapping"):
                if selected_category and selected_template:
                    self.config.set_category_template_mapping(selected_category, selected_template)
                    st.success(f"Added mapping: {selected_category} -> {selected_template}")
                    st.rerun()
                else:
                    st.error("Please select both a category and a template")
                    
            logger.info("Template mapping interface rendered successfully")
        except Exception as e:
            logger.error(f"Error rendering template mapping: {str(e)}", exc_info=True)
            st.error(f"Error rendering template mapping: {str(e)}")
    
    def _render_ai_model_selection(self):
        """Render AI model selection interface."""
        try:
            st.subheader("AI Model Selection")
            st.write("Select the AI model to use for metadata extraction.")
            
            # Get current AI model
            current_model = self.config.get_ai_model()
            
            # Define available models based on Box AI documentation
            # Source: https://developer.box.com/guides/box-ai/ai-models/
            models = [
                {"id": "default", "name": "Default (Box AI)"},
                {"id": "azure__openai__gpt_4o", "name": "GPT-4o (Azure OpenAI)"},
                {"id": "azure__openai__gpt_4o_mini", "name": "GPT-4o Mini (Azure OpenAI)"},
                {"id": "azure__openai__gpt_35_turbo", "name": "GPT-3.5 Turbo (Azure OpenAI)"},
                {"id": "google__gemini_2_0_flash_001", "name": "Gemini 2.0 Flash (Google)"},
                {"id": "google__gemini_2_0_flash_lite_preview", "name": "Gemini 2.0 Flash Lite (Google)"},
                {"id": "google__gemini_1_5_flash_001", "name": "Gemini 1.5 Flash (Google)"},
                {"id": "google__gemini_1_5_pro_001", "name": "Gemini 1.5 Pro (Google)"},
                {"id": "aws__claude_3_haiku", "name": "Claude 3 Haiku (AWS)"},
                {"id": "aws__claude_3_sonnet", "name": "Claude 3 Sonnet (AWS)"},
                {"id": "aws__claude_3_5_sonnet", "name": "Claude 3.5 Sonnet (AWS)"},
                {"id": "aws__claude_3_7_sonnet", "name": "Claude 3.7 Sonnet (AWS)"},
                {"id": "aws__titan_text_lite", "name": "Titan Text Lite (AWS)"}
            ]
            
            # Model selection
            selected_model = st.selectbox(
                "AI Model",
                options=[m["id"] for m in models],
                index=next((i for i, m in enumerate(models) if m["id"] == current_model), 0),
                format_func=lambda x: next((m["name"] for m in models if m["id"] == x), "Unknown")
            )
            
            # Model description
            model_descriptions = {
                "default": "Uses Box's built-in AI capabilities for metadata extraction.",
                "azure__openai__gpt_4o": "Most capable model for complex metadata extraction tasks. Higher cost but better accuracy.",
                "azure__openai__gpt_4o_mini": "Balanced model with good performance and reasonable cost.",
                "azure__openai__gpt_35_turbo": "Fast and cost-effective model. Good for simple metadata extraction tasks.",
                "google__gemini_2_0_flash_001": "Google's fast and efficient model for quick metadata extraction.",
                "google__gemini_2_0_flash_lite_preview": "Lightweight version of Gemini 2.0 Flash, optimized for speed.",
                "google__gemini_1_5_flash_001": "Efficient model for routine metadata extraction tasks.",
                "google__gemini_1_5_pro_001": "More powerful Google model for complex document understanding.",
                "aws__claude_3_haiku": "Fast and efficient Claude model for routine metadata extraction.",
                "aws__claude_3_sonnet": "Balanced Claude model with good performance for most tasks.",
                "aws__claude_3_5_sonnet": "Enhanced Claude model with improved accuracy.",
                "aws__claude_3_7_sonnet": "Latest Claude model with advanced capabilities.",
                "aws__titan_text_lite": "Amazon's lightweight model for basic metadata extraction."
            }
            
            if selected_model in model_descriptions:
                st.info(model_descriptions[selected_model])
            
            # Model comparison
            with st.expander("Model Comparison", expanded=False):
                st.write("""
                ### Model Comparison
                
                | Model | Speed | Cost | Accuracy | Best For |
                | ----- | ----- | ---- | -------- | -------- |
                | GPT-4o | Medium | High | Highest | Complex documents, legal contracts |
                | GPT-4o Mini | Fast | Medium | High | Most business documents |
                | GPT-3.5 Turbo | Very Fast | Low | Good | Simple documents, high volume |
                | Gemini 2.0 Flash | Fast | Medium | High | General purpose extraction |
                | Claude 3 Sonnet | Medium | Medium | High | Detailed analysis, compliance |
                | Claude 3 Haiku | Fast | Low | Good | Quick extraction, high volume |
                | Titan Text Lite | Very Fast | Low | Good | Basic metadata, high volume |
                """)
            
            # Save button
            if st.button("Save Model Selection"):
                self.config.set_ai_model(selected_model)
                st.success(f"AI model set to: {selected_model}")
                
            logger.info("AI model selection interface rendered successfully")
        except Exception as e:
            logger.error(f"Error rendering AI model selection: {str(e)}", exc_info=True)
            st.error(f"Error rendering AI model selection: {str(e)}")
    
    def _render_advanced_settings(self):
        """Render advanced settings interface."""
        try:
            st.subheader("Advanced Settings")
            st.write("Configure advanced settings for the automated workflow.")
            
            # Webhook port
            current_port = self.config.get_webhook_port()
            new_port = st.number_input(
                "Webhook Port",
                min_value=1024,
                max_value=65535,
                value=current_port,
                help="Port to use for the webhook server. Must be between 1024 and 65535."
            )
            
            # Confidence threshold
            current_threshold = self.config.get_confidence_threshold()
            new_threshold = st.slider(
                "Confidence Threshold",
                min_value=0.0,
                max_value=1.0,
                value=current_threshold,
                step=0.05,
                help="Minimum confidence level required for automated categorization."
            )
            
            # Save button
            if st.button("Save Advanced Settings"):
                # Update webhook port
                if new_port != current_port:
                    self.config.set_webhook_port(new_port)
                
                # Update confidence threshold
                if new_threshold != current_threshold:
                    self.config.set_confidence_threshold(new_threshold)
                
                st.success("Advanced settings saved")
                
            # Webhook URL information
            st.write("---")
            st.subheader("Webhook Information")
            
            # Get webhook URL - Use dynamic URL generation based on Streamlit's server info
            webhook_port = self.config.get_webhook_port()
            
            # For local development, use localhost
            base_url = os.environ.get('WEBHOOK_BASE_URL', 'http://localhost')
            webhook_url = f"{base_url}:{webhook_port}/webhook"
            
            st.code(webhook_url)
            st.info("Use this URL when configuring webhooks in the Box Developer Console.")
            
            # Reset configuration button
            st.write("---")
            st.subheader("Reset Configuration")
            st.warning("This will reset all automated workflow configuration to default values.")
            
            if st.button("Reset Configuration", key="reset_config"):
                # Create a new configuration instance
                global _config
                _config = AutomatedWorkflowConfig()
                self.config = _config
                
                st.success("Configuration reset to default values")
                st.rerun()
                
            logger.info("Advanced settings interface rendered successfully")
        except Exception as e:
            logger.error(f"Error rendering advanced settings: {str(e)}", exc_info=True)
            st.error(f"Error rendering advanced settings: {str(e)}")
    
    def render_monitoring_dashboard(self):
        """Render monitoring dashboard."""
        try:
            st.header("Monitoring Dashboard")
            st.write("This dashboard shows the status of the automated workflow.")
            
            # Check if event stream is running
            from modules.integration import is_event_stream_running
            event_stream_status = is_event_stream_running()
            
            # Display status
            st.subheader("System Status")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    label="Event Stream",
                    value="Running" if event_stream_status else "Stopped"
                )
            
            with col2:
                st.metric(
                    label="Monitored Folders",
                    value=len(self.config.get_monitored_folders())
                )
            
            # Display recent activity
            st.subheader("Recent Activity")
            
            # In a real implementation, this would come from a database or log file
            # For now, we'll use placeholder data
            if self.client:
                st.write("Connected to Box as: " + self.client.user().get().name)
                
                # Placeholder activity data
                st.write("No recent activity to display.")
            else:
                st.warning("Not connected to Box. Please authenticate first.")
                
            logger.info("Monitoring dashboard rendered successfully")
        except Exception as e:
            logger.error(f"Error rendering monitoring dashboard: {str(e)}", exc_info=True)
            st.error(f"Error rendering monitoring dashboard: {str(e)}")


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


# Add standalone functions that create an instance of ConfigurationInterface and call its methods
def render_workflow_selection(client=None):
    """
    Standalone function to render workflow selection interface.
    
    Args:
        client: Box client instance
    
    Returns:
        str: Selected workflow mode
    """
    logger.info("Calling render_workflow_selection standalone function")
    config_interface = get_configuration_interface(client)
    return config_interface.render_workflow_selection()

def render_configuration_interface(client=None):
    """
    Standalone function to render configuration interface.
    
    Args:
        client: Box client instance
    """
    logger.info("Calling render_configuration_interface standalone function")
    config_interface = get_configuration_interface(client)
    config_interface.render_configuration_interface()

def render_monitoring_dashboard(client=None):
    """
    Standalone function to render monitoring dashboard.
    
    Args:
        client: Box client instance
    """
    logger.info("Calling render_monitoring_dashboard standalone function")
    config_interface = get_configuration_interface(client)
    config_interface.render_monitoring_dashboard()

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
    
    def get_webhook_enabled(self) -> bool:
        """
        Get webhook enabled.
        
        Returns:
            bool: Webhook enabled
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


class ConfigurationInterface:
    """
    Configuration interface for the Box Metadata Extraction application.
    """
    
    def __init__(self):
        """Initialize configuration interface."""
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
        except Exception as e:
            logger.error(f"Error rendering workflow selection: {str(e)}", exc_info=True)
            st.error(f"Error rendering workflow selection: {str(e)}")
    
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
            
            # Folder browser
            if st.session_state.authenticated and st.session_state.client:
                # Get root folder
                root_folder = st.session_state.client.folder(folder_id="0").get()
                
                # Initialize folder navigation state
                if "folder_navigation" not in st.session_state:
                    st.session_state.folder_navigation = {
                        "current_folder_id": "0",
                        "current_folder_name": "All Files",
                        "folder_path": [{"id": "0", "name": "All Files"}]
                    }
                
                # Display current folder path
                path_str = " / ".join([f"{folder['name']}" for folder in st.session_state.folder_navigation["folder_path"]])
                st.write(f"Current location: {path_str}")
                
                # Get current folder
                current_folder_id = st.session_state.folder_navigation["current_folder_id"]
                current_folder = st.session_state.client.folder(folder_id=current_folder_id).get()
                
                # Display folder contents
                folder_items = current_folder.get_items(limit=100)
                
                # Filter only folders
                folders = [item for item in folder_items if item.type == "folder"]
                
                # Display folders
                if folders:
                    st.write("Select a folder:")
                    
                    # Create columns for folder display
                    cols = st.columns(3)
                    
                    # Display folders in columns
                    for i, folder in enumerate(folders):
                        col_idx = i % 3
                        with cols[col_idx]:
                            if st.button(f"📁 {folder.name}", key=f"folder_{folder.id}"):
                                # Navigate to folder
                                st.session_state.folder_navigation["current_folder_id"] = folder.id
                                st.session_state.folder_navigation["current_folder_name"] = folder.name
                                st.session_state.folder_navigation["folder_path"].append({
                                    "id": folder.id,
                                    "name": folder.name
                                })
                                st.rerun()
                else:
                    st.info("No folders found in the current location.")
                
                # Back button
                if len(st.session_state.folder_navigation["folder_path"]) > 1:
                    if st.button("⬅️ Back to parent folder"):
                        # Remove current folder from path
                        st.session_state.folder_navigation["folder_path"].pop()
                        
                        # Set current folder to parent
                        parent = st.session_state.folder_navigation["folder_path"][-1]
                        st.session_state.folder_navigation["current_folder_id"] = parent["id"]
                        st.session_state.folder_navigation["current_folder_name"] = parent["name"]
                        
                        st.rerun()
                
                # Add current folder button
                if current_folder_id != "0":  # Don't allow adding the root folder
                    if st.button("➕ Add current folder for monitoring"):
                        # Add folder to monitored folders
                        self.config.add_monitored_folder(
                            current_folder_id,
                            st.session_state.folder_navigation["current_folder_name"]
                        )
                        st.success(f"Added folder '{st.session_state.folder_navigation['current_folder_name']}' to monitored folders.")
                        st.rerun()
            else:
                st.warning("Please authenticate with Box to browse folders.")
                return
            
            # Manual folder entry
            st.write("---")
            st.write("Or enter folder details manually:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                folder_id = st.text_input("Folder ID")
            
            with col2:
                folder_name = st.text_input("Folder Name")
            
            if st.button("Add Folder", key="add_folder_manual"):
                if folder_id and folder_name:
                    # Add folder to monitored folders
                    self.config.add_monitored_folder(folder_id, folder_name)
                    st.success(f"Added folder '{folder_name}' to monitored folders.")
                    st.rerun()
                else:
                    st.error("Please enter both folder ID and name.")
            
            # Webhook configuration
            st.write("---")
            st.subheader("Webhook Configuration")
            
            # Webhook enabled checkbox
            webhook_enabled = st.checkbox(
                "Enable webhook for automatic processing",
                value=self.config.get_webhook_enabled()
            )
            
            if webhook_enabled != self.config.get_webhook_enabled():
                self.config.set_webhook_enabled(webhook_enabled)
            
            # Webhook port
            webhook_port = st.number_input(
                "Webhook port",
                min_value=1000,
                max_value=65535,
                value=self.config.get_webhook_port(),
                help="Port to listen for webhook events"
            )
            
            if webhook_port != self.config.get_webhook_port():
                self.config.set_webhook_port(webhook_port)
            
            # Webhook setup instructions
            with st.expander("Webhook Setup Instructions", expanded=False):
                st.markdown("""
                ### Setting up Box Webhooks
                
                Box webhooks allow automatic processing of files when they are uploaded or modified.
                
                #### Step 1: Start the webhook server
                
                The webhook server is automatically started when you run this application.
                
                #### Step 2: Start ngrok tunnel
                
                Run this command in a terminal to create a tunnel to your webhook port:
                ```
                ngrok http 5000
                ```
                
                #### Step 3: Configure Box webhook
                
                1. Go to the [Box Developer Console](https://app.box.com/developers/console)
                2. Create a new app or select your existing app
                3. Navigate to the 'Webhooks' section
                4. Create a new webhook with the following settings:
                   - Target URL: Use the ngrok URL (e.g., https://a1b2-c3d4-e5f6.ngrok.io/webhook)
                   - Triggers: Select 'FILE.UPLOADED' and 'FILE.COPIED'
                   - Address: Select the folders you want to monitor
                5. Save the webhook configuration
                
                #### Step 4: Start your webhook server
                
                The webhook server will automatically start when you run this application.
                """)
            
            # Get webhook URL
            webhook_port = self.config.get_webhook_port()
            
            # Display ngrok instructions
            st.subheader("Webhook URL")
            st.info("""
            Box webhooks require a public URL. You need to use ngrok to expose your local webhook server.
            
            After starting ngrok with `ngrok http 5000`, enter the ngrok URL below:
            """)
            
            # Input for ngrok URL
            ngrok_url = st.text_input("ngrok URL (e.g., https://a1b2-c3d4-e5f6.ngrok.io)")
            
            if ngrok_url:
                webhook_url = f"{ngrok_url}/webhook"
                st.code(webhook_url, language="text")
                st.success("Use this URL when configuring webhooks in the Box Developer Console.")
                
                # Save ngrok URL to config
                if "ngrok_url" not in self.config.config or self.config.config["ngrok_url"] != ngrok_url:
                    self.config.config["ngrok_url"] = ngrok_url
                    self.config._save_config()
                    st.success("ngrok URL saved to configuration")
            
            logger.info("Folder selection interface rendered successfully")
        except Exception as e:
            logger.error(f"Error rendering folder selection: {str(e)}", exc_info=True)
            st.error(f"Error rendering folder selection: {str(e)}")
    
    def _render_template_mapping(self):
        """Render template mapping interface."""
        try:
            st.subheader("Template Mapping")
            st.write("Map document categories to metadata templates.")
            
            # Check if authenticated
            if not st.session_state.authenticated:
                st.warning("Please authenticate with Box to retrieve metadata templates.")
                return
            
            # Get metadata templates
            templates = []
            try:
                from modules.metadata_template_retrieval import get_metadata_templates
                # Force refresh templates to ensure we have the latest data
                templates = get_metadata_templates(st.session_state.client, force_refresh=True)
                
                # Store templates in session state for reuse
                if templates:
                    st.session_state.metadata_templates = templates
                    st.success(f"Successfully retrieved {len(templates)} metadata templates from Box.")
                else:
                    st.warning("No metadata templates found. Please create templates in Box.")
            except Exception as e:
                st.error(f"Error retrieving metadata templates: {str(e)}")
                logger.error(f"Error retrieving metadata templates: {str(e)}", exc_info=True)
                
                # Try to use cached templates if available
                if "metadata_templates" in st.session_state and st.session_state.metadata_templates:
                    templates = st.session_state.metadata_templates
                    st.info(f"Using {len(templates)} cached metadata templates.")
            
            # Get document categories from document_categorization.py
            try:
                # These are the document types defined in document_categorization.py
                categories = [
                    "Sales Contract",
                    "Invoices",
                    "Tax",
                    "Financial Report",
                    "Employment Contract",
                    "PII",
                    "Other"
                ]
            except Exception as e:
                # Fallback categories if there's an error
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
                logger.error(f"Error retrieving document categories: {str(e)}", exc_info=True)
            
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
                        if isinstance(templates, dict):
                            # If templates is a dictionary (key-value pairs)
                            if template_id in templates:
                                template_obj = templates[template_id]
                                if isinstance(template_obj, dict):
                                    template_name = template_obj.get("templateKey", "Unknown Template")
                        elif isinstance(templates, list):
                            # If templates is a list of dictionaries
                            for template in templates:
                                if isinstance(template, dict) and template.get("id") == template_id:
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
            
            if isinstance(templates, dict):
                # If templates is a dictionary (key-value pairs)
                for template_id, template in templates.items():
                    if isinstance(template, dict):
                        template_options.append({
                            "id": template_id,
                            "name": template.get("templateKey", "Unknown Template")
                        })
            elif isinstance(templates, list):
                # If templates is a list of dictionaries
                for template in templates:
                    if isinstance(template, dict):
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
            
            # Save model selection
            if selected_model != current_model:
                self.config.set_ai_model(selected_model)
                st.success(f"AI model updated to {selected_model}")
            
            # Display model information
            with st.expander("Model Information", expanded=False):
                st.markdown("""
                ### Box AI Models
                
                Box AI supports various models from different providers:
                
                #### Azure OpenAI Models
                - **GPT-4o**: Latest and most capable model, best for complex tasks
                - **GPT-4o Mini**: Smaller, faster version of GPT-4o
                - **GPT-3.5 Turbo**: Good balance of performance and speed
                
                #### Google Models
                - **Gemini 2.0 Flash**: Fast, efficient model for quick responses
                - **Gemini 2.0 Flash Lite**: Lightweight version of Gemini 2.0 Flash
                - **Gemini 1.5 Flash**: Fast model with good performance
                - **Gemini 1.5 Pro**: More capable model for complex tasks
                
                #### AWS Models
                - **Claude 3 Haiku**: Fast, efficient model for quick responses
                - **Claude 3 Sonnet**: Good balance of performance and speed
                - **Claude 3.5 Sonnet**: Improved version of Claude 3 Sonnet
                - **Claude 3.7 Sonnet**: Latest Claude model with enhanced capabilities
                - **Titan Text Lite**: Lightweight model for basic tasks
                
                For more information, see the [Box AI documentation](https://developer.box.com/guides/box-ai/ai-models/).
                """)
            
            # Model comparison
            with st.expander("Model Comparison", expanded=False):
                st.markdown("""
                ### Model Comparison
                
                | Model | Speed | Quality | Use Case |
                | ----- | ----- | ------- | -------- |
                | GPT-4o | Medium | Excellent | Complex document analysis |
                | GPT-4o Mini | Fast | Very Good | Balanced performance |
                | GPT-3.5 Turbo | Very Fast | Good | High-volume processing |
                | Gemini 2.0 Flash | Fast | Very Good | Quick analysis |
                | Gemini 1.5 Pro | Medium | Excellent | Detailed extraction |
                | Claude 3 Haiku | Very Fast | Good | Simple documents |
                | Claude 3.5 Sonnet | Medium | Excellent | Complex documents |
                | Titan Text Lite | Very Fast | Basic | Simple metadata |
                """)
            
            logger.info("AI model selection interface rendered successfully")
        except Exception as e:
            logger.error(f"Error rendering AI model selection: {str(e)}", exc_info=True)
            st.error(f"Error rendering AI model selection: {str(e)}")
    
    def _render_advanced_settings(self):
        """Render advanced settings interface."""
        try:
            st.subheader("Advanced Settings")
            st.write("Configure advanced settings for automated workflow.")
            
            # Get current settings
            settings = self.config.get_advanced_settings()
            
            # Confidence threshold
            confidence_threshold = st.slider(
                "Confidence threshold",
                min_value=0.0,
                max_value=1.0,
                value=settings.get("confidence_threshold", 0.7),
                step=0.05,
                help="Minimum confidence level required for automatic metadata application"
            )
            
            if confidence_threshold != settings.get("confidence_threshold"):
                self.config.set_advanced_setting("confidence_threshold", confidence_threshold)
            
            # Auto-apply metadata
            auto_apply = st.checkbox(
                "Automatically apply metadata",
                value=settings.get("auto_apply_metadata", False),
                help="When enabled, metadata will be applied automatically if confidence is above threshold"
            )
            
            if auto_apply != settings.get("auto_apply_metadata"):
                self.config.set_advanced_setting("auto_apply_metadata", auto_apply)
            
            # Notification settings
            st.write("---")
            st.write("Notification Settings")
            
            # Enable notifications
            notifications_enabled = st.checkbox(
                "Enable email notifications",
                value=settings.get("notification_enabled", False),
                help="Send email notifications when files are processed"
            )
            
            if notifications_enabled != settings.get("notification_enabled"):
                self.config.set_advanced_setting("notification_enabled", notifications_enabled)
            
            # Email address
            email = st.text_input(
                "Notification email",
                value=settings.get("notification_email", ""),
                disabled=not notifications_enabled
            )
            
            if email != settings.get("notification_email") and notifications_enabled:
                self.config.set_advanced_setting("notification_email", email)
            
            # Processing settings
            st.write("---")
            st.write("Processing Settings")
            
            # Max concurrent processes
            max_processes = st.number_input(
                "Maximum concurrent processes",
                min_value=1,
                max_value=10,
                value=settings.get("max_processes", 2),
                help="Maximum number of files to process concurrently"
            )
            
            if max_processes != settings.get("max_processes"):
                self.config.set_advanced_setting("max_processes", max_processes)
            
            # Processing timeout
            timeout = st.number_input(
                "Processing timeout (seconds)",
                min_value=30,
                max_value=600,
                value=settings.get("processing_timeout", 120),
                help="Maximum time to spend processing a single file"
            )
            
            if timeout != settings.get("processing_timeout"):
                self.config.set_advanced_setting("processing_timeout", timeout)
            
            # Debug mode
            debug_mode = st.checkbox(
                "Enable debug mode",
                value=settings.get("debug_mode", False),
                help="Enable additional logging and debugging information"
            )
            
            if debug_mode != settings.get("debug_mode"):
                self.config.set_advanced_setting("debug_mode", debug_mode)
            
            logger.info("Advanced settings interface rendered successfully")
        except Exception as e:
            logger.error(f"Error rendering advanced settings: {str(e)}", exc_info=True)
            st.error(f"Error rendering advanced settings: {str(e)}")
    
    def render_monitoring_dashboard(self):
        """Render monitoring dashboard."""
        try:
            st.header("Monitoring Dashboard")
            st.write("Monitor automated workflow processing.")
            
            # Placeholder for monitoring dashboard
            st.info("Monitoring dashboard is under development.")
            
            logger.info("Monitoring dashboard rendered successfully")
        except Exception as e:
            logger.error(f"Error rendering monitoring dashboard: {str(e)}", exc_info=True)
            st.error(f"Error rendering monitoring dashboard: {str(e)}")


def get_automated_workflow_config():
    """
    Get automated workflow configuration.
    
    Returns:
        AutomatedWorkflowConfig: Configuration
    """
    return AutomatedWorkflowConfig()


def get_configuration_interface():
    """
    Get configuration interface.
    
    Returns:
        ConfigurationInterface: Configuration interface
    """
    return ConfigurationInterface()


def render_workflow_selection():
    """
    Render workflow selection interface.
    
    This is a standalone function that can be called from the main app.
    """
    logger.info("Calling render_workflow_selection standalone function")
    interface = ConfigurationInterface()
    interface.render_workflow_selection()


def render_configuration_interface():
    """
    Render configuration interface.
    
    This is a standalone function that can be called from the main app.
    """
    logger.info("Calling render_configuration_interface standalone function")
    interface = ConfigurationInterface()
    interface.render_configuration_interface()

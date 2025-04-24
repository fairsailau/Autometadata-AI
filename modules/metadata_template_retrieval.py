import streamlit as st
import logging
import requests
import time
import json
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_metadata_templates(client, force_refresh=False):
    """
    Retrieve metadata templates from Box
    
    Args:
        client: Box client
        force_refresh: Force refresh of templates
        
    Returns:
        dict: Metadata templates
    """
    # Check if templates are already cached and not forcing refresh
    if not force_refresh and hasattr(st.session_state, "metadata_templates") and st.session_state.metadata_templates:
        logger.info(f"Using cached metadata templates: {len(st.session_state.metadata_templates)} templates")
        return st.session_state.metadata_templates
    
    # If client is not provided or not authenticated, return empty dict
    if not client or not hasattr(st.session_state, "authenticated") or not st.session_state.authenticated:
        logger.warning("Client not provided or not authenticated")
        return {}
    
    try:
        # Get access token from client
        access_token = None
        if hasattr(client, '_oauth'):
            access_token = client._oauth.access_token
        elif hasattr(client, 'auth') and hasattr(client.auth, 'access_token'):
            access_token = client.auth.access_token
        
        if not access_token:
            raise ValueError("Could not retrieve access token from client")
        
        logger.info("Retrieved access token, fetching metadata templates")
        
        # Get metadata templates using direct API calls
        templates = {}
        
        # Retrieve enterprise templates
        enterprise_templates = retrieve_templates_by_scope(access_token, "enterprise")
        logger.info(f"Retrieved {len(enterprise_templates)} enterprise templates")
        
        # Process enterprise templates
        for template in enterprise_templates:
            if "templateKey" in template and "scope" in template:
                template_key = template["templateKey"]
                scope = template["scope"]
                template_id = f"{scope}_{template_key}"
                
                # Store template
                templates[template_id] = {
                    "id": template_id,
                    "key": template_key,
                    "displayName": template.get("displayName", template_key),
                    "scope": scope,
                    "templateKey": template_key,
                    "fields": template.get("fields", []),
                    "hidden": template.get("hidden", False)
                }
                
                # Fetch template fields if not included in the response
                if not template.get("fields") and "id" in template:
                    try:
                        fields = retrieve_template_fields(access_token, scope, template_key)
                        templates[template_id]["fields"] = fields
                    except Exception as e:
                        logger.error(f"Error retrieving fields for template {template_key}: {str(e)}")
        
        # Retrieve global templates
        global_templates = retrieve_templates_by_scope(access_token, "global")
        logger.info(f"Retrieved {len(global_templates)} global templates")
        
        # Process global templates
        for template in global_templates:
            if "templateKey" in template and "scope" in template:
                template_key = template["templateKey"]
                scope = template["scope"]
                template_id = f"{scope}_{template_key}"
                
                # Store template
                templates[template_id] = {
                    "id": template_id,
                    "key": template_key,
                    "displayName": template.get("displayName", template_key),
                    "scope": scope,
                    "templateKey": template_key,
                    "fields": template.get("fields", []),
                    "hidden": template.get("hidden", False)
                }
                
                # Fetch template fields if not included in the response
                if not template.get("fields") and "id" in template:
                    try:
                        fields = retrieve_template_fields(access_token, scope, template_key)
                        templates[template_id]["fields"] = fields
                    except Exception as e:
                        logger.error(f"Error retrieving fields for template {template_key}: {str(e)}")
        
        # Cache templates
        st.session_state.metadata_templates = templates
        st.session_state.template_cache_timestamp = time.time()
        
        logger.info(f"Retrieved and cached {len(templates)} metadata templates")
        
        # Debug output
        if not templates:
            logger.warning("No templates were retrieved from Box API")
            
        return templates
    
    except Exception as e:
        logger.error(f"Error retrieving metadata templates: {str(e)}", exc_info=True)
        # Don't clear existing templates on error
        if not hasattr(st.session_state, "metadata_templates"):
            st.session_state.metadata_templates = {}
        return st.session_state.metadata_templates

def retrieve_templates_by_scope(access_token, scope):
    """
    Retrieve metadata templates for a specific scope using direct API call
    
    Args:
        access_token: Box API access token
        scope: Template scope (enterprise or global)
        
    Returns:
        list: List of metadata templates for the specified scope
    """
    templates = []
    next_marker = None
    
    try:
        # Make API calls until all templates are retrieved
        while True:
            # Construct API URL
            api_url = f"https://api.box.com/2.0/metadata_templates/{scope}"
            if next_marker:
                api_url += f"?marker={next_marker}"
            
            # Set headers
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Make API call
            logger.info(f"Making API call to {api_url}")
            response = requests.get(api_url, headers=headers)
            
            # Check for errors
            if response.status_code != 200:
                logger.error(f"API error: {response.status_code} - {response.text}")
                response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            # Add templates to list
            if 'entries' in data:
                templates.extend(data['entries'])
                logger.info(f"Retrieved {len(data['entries'])} templates from {scope} scope")
            else:
                logger.warning(f"No entries found in response from {scope} scope")
                logger.debug(f"Response: {json.dumps(data)}")
            
            # Check for next marker
            if 'next_marker' in data and data['next_marker']:
                next_marker = data['next_marker']
            else:
                break
        
        return templates
    
    except Exception as e:
        logger.error(f"Error retrieving {scope} templates: {str(e)}", exc_info=True)
        return []

def retrieve_template_fields(access_token, scope, template_key):
    """
    Retrieve fields for a specific metadata template
    
    Args:
        access_token: Box API access token
        scope: Template scope (enterprise or global)
        template_key: Template key
        
    Returns:
        list: List of template fields
    """
    try:
        # Construct API URL
        api_url = f"https://api.box.com/2.0/metadata_templates/{scope}/{template_key}/schema"
        
        # Set headers
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Make API call
        logger.info(f"Making API call to {api_url}")
        response = requests.get(api_url, headers=headers)
        
        # Check for errors
        if response.status_code != 200:
            logger.error(f"API error: {response.status_code} - {response.text}")
            response.raise_for_status()
        
        # Parse response
        data = response.json()
        
        # Return fields
        if 'fields' in data:
            return data['fields']
        else:
            logger.warning(f"No fields found in template {template_key}")
            return []
    
    except Exception as e:
        logger.error(f"Error retrieving fields for template {template_key}: {str(e)}", exc_info=True)
        return []

def initialize_template_state():
    """
    Initialize template-related session state variables
    """
    # Template cache
    if not hasattr(st.session_state, "metadata_templates"):
        st.session_state.metadata_templates = {}
        logger.info("Initialized metadata_templates in session state")
    
    # Template cache timestamp
    if not hasattr(st.session_state, "template_cache_timestamp"):
        st.session_state.template_cache_timestamp = None
        logger.info("Initialized template_cache_timestamp in session state")
    
    # Document type to template mapping
    if not hasattr(st.session_state, "document_type_to_template"):
        st.session_state.document_type_to_template = {
            "Sales Contract": None,
            "Invoices": None,
            "Tax": None,
            "Financial Report": None,
            "Employment Contract": None,
            "PII": None,
            "Other": None
        }
        logger.info("Initialized document_type_to_template in session state")

def get_template_by_id(template_id):
    """
    Get template by ID
    
    Args:
        template_id: Template ID
        
    Returns:
        dict: Template or None if not found
    """
    if not template_id:
        return None
    
    if not hasattr(st.session_state, "metadata_templates") or not st.session_state.metadata_templates:
        return None
    
    return st.session_state.metadata_templates.get(template_id)

def get_template_by_document_type(document_type):
    """
    Get template by document type
    
    Args:
        document_type: Document type
        
    Returns:
        dict: Template or None if not found
    """
    if not document_type:
        return None
    
    if not hasattr(st.session_state, "document_type_to_template"):
        return None
    
    template_id = st.session_state.document_type_to_template.get(document_type)
    if not template_id:
        return None
    
    return get_template_by_id(template_id)

def map_document_type_to_template(document_type, template_id):
    """
    Map document type to template
    
    Args:
        document_type: Document type
        template_id: Template ID
    """
    if not hasattr(st.session_state, "document_type_to_template"):
        st.session_state.document_type_to_template = {}
    
    st.session_state.document_type_to_template[document_type] = template_id
    logger.info(f"Mapped document type '{document_type}' to template '{template_id}'")

def display_template_info(template_id):
    """
    Display template information
    
    Args:
        template_id: Template ID
    """
    template = get_template_by_id(template_id)
    if not template:
        st.warning(f"Template {template_id} not found")
        return
    
    st.write(f"**Template:** {template.get('displayName', template.get('key', 'Unknown'))}")
    st.write(f"**Scope:** {template.get('scope', 'Unknown')}")
    
    # Display fields
    fields = template.get('fields', [])
    if fields:
        st.write("**Fields:**")
        for field in fields:
            field_type = field.get('type', 'Unknown')
            field_key = field.get('key', 'Unknown')
            field_display_name = field.get('displayName', field_key)
            
            st.write(f"- {field_display_name} ({field_type})")
    else:
        st.write("No fields found in this template")

def refresh_templates(client):
    """
    Force refresh of metadata templates
    
    Args:
        client: Box client
        
    Returns:
        dict: Refreshed metadata templates
    """
    return get_metadata_templates(client, force_refresh=True)

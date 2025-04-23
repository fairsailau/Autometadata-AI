"""
Template selection and processing module for automated metadata extraction.
This module handles mapping document categories to metadata templates and processing files.
"""

import os
import json
import logging
import time
import threading
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TemplateMappingService:
    """
    Maps document categories to metadata templates.
    """
    
    def __init__(self):
        """Initialize the template mapping service."""
        self.mappings = {}
        self.mapping_lock = threading.RLock()
        self.mapping_path = os.path.join(os.path.dirname(__file__), '..', '.template_mappings.json')
        self._load_mappings()
    
    def _load_mappings(self):
        """Load template mappings from file."""
        if os.path.exists(self.mapping_path):
            try:
                with open(self.mapping_path, 'r') as f:
                    self.mappings = json.load(f)
            except Exception as e:
                logger.error(f"Error loading template mappings: {str(e)}")
                self.mappings = {}
    
    def _save_mappings(self):
        """Save template mappings to file."""
        try:
            with open(self.mapping_path, 'w') as f:
                json.dump(self.mappings, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving template mappings: {str(e)}")
    
    def set_mapping(self, category: str, template_key: str, template_scope: str = "enterprise") -> bool:
        """
        Set a mapping from document category to metadata template.
        
        Args:
            category: Document category
            template_key: Metadata template key
            template_scope: Metadata template scope
            
        Returns:
            bool: True if mapping was set, False otherwise
        """
        with self.mapping_lock:
            self.mappings[category] = {
                "template_key": template_key,
                "template_scope": template_scope,
                "updated_at": datetime.now().isoformat()
            }
            
            self._save_mappings()
            logger.info(f"Set mapping: {category} -> {template_key} ({template_scope})")
            return True
    
    def get_mapping(self, category: str) -> Optional[Dict[str, str]]:
        """
        Get the metadata template mapping for a document category.
        
        Args:
            category: Document category
            
        Returns:
            dict: Template mapping or None if not found
        """
        return self.mappings.get(category)
    
    def get_all_mappings(self) -> Dict[str, Dict[str, str]]:
        """
        Get all template mappings.
        
        Returns:
            dict: All template mappings
        """
        return self.mappings.copy()
    
    def delete_mapping(self, category: str) -> bool:
        """
        Delete a template mapping.
        
        Args:
            category: Document category
            
        Returns:
            bool: True if mapping was deleted, False otherwise
        """
        with self.mapping_lock:
            if category in self.mappings:
                del self.mappings[category]
                self._save_mappings()
                logger.info(f"Deleted mapping for category: {category}")
                return True
            
            return False


class MetadataProcessor:
    """
    Processes files for metadata extraction and application.
    """
    
    def __init__(self, client=None):
        """
        Initialize the metadata processor.
        
        Args:
            client: Box client instance
        """
        self.client = client
        self.template_mapping_service = TemplateMappingService()
        self.processing_history = {}
        self.history_lock = threading.RLock()
        self.history_path = os.path.join(os.path.dirname(__file__), '..', '.processing_history.json')
        self._load_history()
    
    def set_client(self, client):
        """
        Set the Box client.
        
        Args:
            client: Box client instance
        """
        self.client = client
    
    def _load_history(self):
        """Load processing history from file."""
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, 'r') as f:
                    self.processing_history = json.load(f)
            except Exception as e:
                logger.error(f"Error loading processing history: {str(e)}")
                self.processing_history = {}
    
    def _save_history(self):
        """Save processing history to file."""
        try:
            with open(self.history_path, 'w') as f:
                json.dump(self.processing_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving processing history: {str(e)}")
    
    def _update_history(self, file_id: str, result: Dict[str, Any]):
        """
        Update processing history.
        
        Args:
            file_id: Box file ID
            result: Processing result
        """
        with self.history_lock:
            self.processing_history[file_id] = {
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            
            # Limit history size
            if len(self.processing_history) > 1000:
                # Remove oldest entries
                sorted_keys = sorted(
                    self.processing_history.keys(),
                    key=lambda k: self.processing_history[k]["timestamp"]
                )
                
                # Remove oldest 100 entries
                for key in sorted_keys[:100]:
                    del self.processing_history[key]
            
            self._save_history()
    
    def process_file(self, file_id: str, category: str) -> Dict[str, Any]:
        """
        Process a file for metadata extraction and application.
        
        Args:
            file_id: Box file ID
            category: Document category
            
        Returns:
            dict: Processing result
        """
        if not self.client:
            logger.error("Box client not initialized")
            return {
                "status": "error",
                "error": "Box client not initialized",
                "file_id": file_id,
                "category": category
            }
        
        try:
            # Get template mapping
            mapping = self.template_mapping_service.get_mapping(category)
            
            if not mapping:
                logger.warning(f"No template mapping found for category: {category}")
                return {
                    "status": "error",
                    "error": f"No template mapping found for category: {category}",
                    "file_id": file_id,
                    "category": category
                }
            
            # Extract template information
            template_key = mapping["template_key"]
            template_scope = mapping["template_scope"]
            
            # Extract metadata
            extraction_result = self._extract_metadata(file_id, category, template_key)
            
            if "error" in extraction_result:
                logger.error(f"Error extracting metadata: {extraction_result['error']}")
                return {
                    "status": "error",
                    "error": extraction_result["error"],
                    "file_id": file_id,
                    "category": category,
                    "template_key": template_key,
                    "template_scope": template_scope
                }
            
            # Apply metadata
            application_result = self._apply_metadata(
                file_id, template_key, template_scope, extraction_result["metadata"]
            )
            
            # Prepare result
            result = {
                "status": application_result.get("status", "error"),
                "file_id": file_id,
                "category": category,
                "template_key": template_key,
                "template_scope": template_scope,
                "extraction": extraction_result,
                "application": application_result,
                "timestamp": datetime.now().isoformat()
            }
            
            # Update history
            self._update_history(file_id, result)
            
            return result
        
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "file_id": file_id,
                "category": category,
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_metadata(self, file_id: str, category: str, template_key: str) -> Dict[str, Any]:
        """
        Extract metadata from a file.
        
        Args:
            file_id: Box file ID
            category: Document category
            template_key: Metadata template key
            
        Returns:
            dict: Extraction result
        """
        try:
            # Import here to avoid circular imports
            from modules.metadata_extraction import extract_metadata_for_template
            
            # Get template fields
            template_fields = self._get_template_fields(template_key)
            
            if not template_fields:
                return {
                    "error": f"Could not retrieve fields for template: {template_key}"
                }
            
            # Extract metadata
            metadata = extract_metadata_for_template(self.client, file_id, template_key, template_fields)
            
            return {
                "status": "success",
                "metadata": metadata,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_template_fields(self, template_key: str) -> List[str]:
        """
        Get fields for a metadata template.
        
        Args:
            template_key: Metadata template key
            
        Returns:
            list: Template fields
        """
        try:
            # Import here to avoid circular imports
            from modules.metadata_template_retrieval import get_metadata_template_fields
            
            # Get template fields
            fields = get_metadata_template_fields(self.client, template_key)
            
            return fields
        
        except Exception as e:
            logger.error(f"Error getting template fields: {str(e)}")
            return []
    
    def _apply_metadata(self, file_id: str, template_key: str, template_scope: str, 
                       metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply metadata to a file.
        
        Args:
            file_id: Box file ID
            template_key: Metadata template key
            template_scope: Metadata template scope
            metadata: Metadata to apply
            
        Returns:
            dict: Application result
        """
        try:
            # Import here to avoid circular imports
            from modules.direct_metadata_application_enhanced_fixed import apply_metadata
            
            # Apply metadata
            result = apply_metadata(self.client, file_id, template_key, template_scope, metadata)
            
            return {
                "status": "success",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error applying metadata: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_processing_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get processing history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            list: Processing history
        """
        with self.history_lock:
            # Sort by timestamp (newest first)
            sorted_history = sorted(
                self.processing_history.items(),
                key=lambda item: item[1]["timestamp"],
                reverse=True
            )
            
            # Convert to list and limit
            history_list = [
                {"file_id": file_id, **entry}
                for file_id, entry in sorted_history[:limit]
            ]
            
            return history_list


class AutomatedProcessingService:
    """
    Service for automated metadata processing.
    """
    
    def __init__(self, client=None):
        """
        Initialize the automated processing service.
        
        Args:
            client: Box client instance
        """
        self.client = client
        self.metadata_processor = MetadataProcessor(client)
        self.template_mapping_service = self.metadata_processor.template_mapping_service
    
    def set_client(self, client):
        """
        Set the Box client.
        
        Args:
            client: Box client instance
        """
        self.client = client
        self.metadata_processor.set_client(client)
    
    def process_categorization_result(self, categorization_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a categorization result.
        
        Args:
            categorization_result: Categorization result
            
        Returns:
            dict: Processing result
        """
        try:
            # Extract file ID and category
            file_id = categorization_result.get("file_id", "")
            category = categorization_result.get("category", "")
            
            if not file_id:
                logger.warning("Categorization result has no file ID")
                return {
                    "status": "error",
                    "error": "Categorization result has no file ID",
                    "categorization": categorization_result
                }
            
            if not category:
                logger.warning("Categorization result has no category")
                return {
                    "status": "error",
                    "error": "Categorization result has no category",
                    "file_id": file_id
                }
            
            # Process file
            return self.metadata_processor.process_file(file_id, category)
        
        except Exception as e:
            logger.error(f"Error processing categorization result: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "categorization": categorization_result,
                "timestamp": datetime.now().isoformat()
            }
    
    def set_template_mapping(self, category: str, template_key: str, template_scope: str = "enterprise") -> bool:
        """
        Set a mapping from document category to metadata template.
        
        Args:
            category: Document category
            template_key: Metadata template key
            template_scope: Metadata template scope
            
        Returns:
            bool: True if mapping was set, False otherwise
        """
        return self.template_mapping_service.set_mapping(category, template_key, template_scope)
    
    def get_template_mapping(self, category: str) -> Optional[Dict[str, str]]:
        """
        Get the metadata template mapping for a document category.
        
        Args:
            category: Document category
            
        Returns:
            dict: Template mapping or None if not found
        """
        return self.template_mapping_service.get_mapping(category)
    
    def get_all_template_mappings(self) -> Dict[str, Dict[str, str]]:
        """
        Get all template mappings.
        
        Returns:
            dict: All template mappings
        """
        return self.template_mapping_service.get_all_mappings()
    
    def delete_template_mapping(self, category: str) -> bool:
        """
        Delete a template mapping.
        
        Args:
            category: Document category
            
        Returns:
            bool: True if mapping was deleted, False otherwise
        """
        return self.template_mapping_service.delete_mapping(category)
    
    def get_processing_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get processing history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            list: Processing history
        """
        return self.metadata_processor.get_processing_history(limit)


# Global instance
_automated_processing_service = None

def get_automated_processing_service(client=None) -> AutomatedProcessingService:
    """
    Get the global automated processing service instance.
    
    Args:
        client: Box client instance
        
    Returns:
        AutomatedProcessingService: Global automated processing service instance
    """
    global _automated_processing_service
    
    if _automated_processing_service is None:
        _automated_processing_service = AutomatedProcessingService(client)
    elif client is not None:
        _automated_processing_service.set_client(client)
    
    return _automated_processing_service

def process_categorization_result(categorization_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a categorization result.
    
    Args:
        categorization_result: Categorization result
        
    Returns:
        dict: Processing result
    """
    # Get automated processing service instance
    processing_service = get_automated_processing_service()
    
    # Process categorization result
    return processing_service.process_categorization_result(categorization_result)

"""
Test script for automated workflow components.
This script tests the functionality of the automated workflow components.
"""

import os
import sys
import json
import logging
import time
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
from modules.event_stream import (
    WebhookManager, 
    EventProcessor, 
    WebhookListener,
    process_webhook_event
)
from modules.automated_categorization import (
    AutomatedCategorization,
    WorkflowRouter,
    process_file_upload_event
)
from modules.template_processing import (
    TemplateMappingService,
    MetadataProcessor,
    AutomatedProcessingService
)
from modules.configuration_interface import AutomatedWorkflowConfig
from modules.integration import AutomatedWorkflowManager

class TestEventStream(unittest.TestCase):
    """Test event stream components."""
    
    def setUp(self):
        """Set up test environment."""
        # Create mock client
        self.mock_client = MagicMock()
        
        # Create webhook manager
        self.webhook_manager = WebhookManager(self.mock_client)
        
        # Create event processor
        self.event_processor = EventProcessor(self.mock_client)
        
        # Create webhook listener
        self.webhook_listener = WebhookListener(5000, self.event_processor)
    
    def test_webhook_manager_register(self):
        """Test webhook registration."""
        # Mock client response
        self.mock_client.create_webhook.return_value = MagicMock(id='webhook123')
        
        # Register webhook
        webhook_id = self.webhook_manager.register_webhook('folder123', 'https://example.com/webhook')
        
        # Check result
        self.assertEqual(webhook_id, 'webhook123')
        self.mock_client.create_webhook.assert_called_once()
    
    def test_event_processor_register(self):
        """Test event processor registration."""
        # Create mock processor
        mock_processor = MagicMock()
        
        # Register processor
        self.event_processor.register_processor('FILE.UPLOADED', mock_processor)
        
        # Check registration
        self.assertIn('FILE.UPLOADED', self.event_processor.processors)
        self.assertEqual(self.event_processor.processors['FILE.UPLOADED'], mock_processor)
    
    def test_event_processor_process(self):
        """Test event processing."""
        # Create mock processor
        mock_processor = MagicMock()
        
        # Register processor
        self.event_processor.register_processor('FILE.UPLOADED', mock_processor)
        
        # Create event
        event = {
            'type': 'FILE.UPLOADED',
            'source': {
                'id': 'file123',
                'type': 'file'
            }
        }
        
        # Process event
        self.event_processor.process_event(event)
        
        # Check processor called
        mock_processor.assert_called_once_with(event, self.mock_client)
    
    def test_process_webhook_event(self):
        """Test webhook event processing."""
        # Create mock event processor
        mock_processor = MagicMock()
        
        # Create event
        event = {
            'type': 'FILE.UPLOADED',
            'source': {
                'id': 'file123',
                'type': 'file'
            }
        }
        
        # Process event
        with patch('modules.event_stream.get_event_processor', return_value=mock_processor):
            process_webhook_event(event)
            
            # Check processor called
            mock_processor.process_event.assert_called_once_with(event)


class TestAutomatedCategorization(unittest.TestCase):
    """Test automated categorization components."""
    
    def setUp(self):
        """Set up test environment."""
        # Create mock client
        self.mock_client = MagicMock()
        
        # Create automated categorization
        self.automated_categorization = AutomatedCategorization(self.mock_client)
        
        # Create workflow router
        self.workflow_router = WorkflowRouter()
    
    def test_categorize_file(self):
        """Test file categorization."""
        # Mock client response
        self.mock_client.file.return_value.get.return_value = MagicMock(
            id='file123',
            name='test.pdf'
        )
        
        # Mock categorization response
        with patch('modules.automated_categorization.categorize_document', return_value={
            'category': 'Invoice',
            'confidence': 0.8,
            'reasoning': 'Test reasoning'
        }):
            # Categorize file
            result = self.automated_categorization.categorize_file('file123')
            
            # Check result
            self.assertEqual(result['category'], 'Invoice')
            self.assertEqual(result['confidence'], 0.8)
            self.assertEqual(result['file_id'], 'file123')
    
    def test_workflow_router_high_confidence(self):
        """Test workflow router with high confidence."""
        # Create categorization result
        result = {
            'file_id': 'file123',
            'category': 'Invoice',
            'confidence': 0.8,
            'reasoning': 'Test reasoning'
        }
        
        # Route result
        route = self.workflow_router.route_categorization(result, 0.7)
        
        # Check route
        self.assertEqual(route, 'automated')
    
    def test_workflow_router_low_confidence(self):
        """Test workflow router with low confidence."""
        # Create categorization result
        result = {
            'file_id': 'file123',
            'category': 'Invoice',
            'confidence': 0.6,
            'reasoning': 'Test reasoning'
        }
        
        # Route result
        route = self.workflow_router.route_categorization(result, 0.7)
        
        # Check route
        self.assertEqual(route, 'manual_review')
    
    def test_process_file_upload_event(self):
        """Test file upload event processing."""
        # Create mock automated categorization
        mock_categorization = MagicMock()
        mock_categorization.categorize_file.return_value = {
            'file_id': 'file123',
            'category': 'Invoice',
            'confidence': 0.8,
            'reasoning': 'Test reasoning'
        }
        
        # Create event
        event = {
            'type': 'FILE.UPLOADED',
            'source': {
                'id': 'file123',
                'type': 'file'
            }
        }
        
        # Process event
        with patch('modules.automated_categorization.get_automated_categorization', return_value=mock_categorization):
            process_file_upload_event(event, self.mock_client)
            
            # Check categorization called
            mock_categorization.categorize_file.assert_called_once_with('file123')
            mock_categorization.process_categorization_result.assert_called_once()


class TestTemplateProcessing(unittest.TestCase):
    """Test template processing components."""
    
    def setUp(self):
        """Set up test environment."""
        # Create mock client
        self.mock_client = MagicMock()
        
        # Create template mapping service
        self.template_mapping_service = TemplateMappingService()
        
        # Create metadata processor
        self.metadata_processor = MetadataProcessor(self.mock_client)
        
        # Create automated processing service
        self.processing_service = AutomatedProcessingService(self.mock_client)
    
    def test_template_mapping(self):
        """Test template mapping."""
        # Set mapping
        result = self.template_mapping_service.set_mapping('Invoice', 'invoice', 'enterprise')
        
        # Check result
        self.assertTrue(result)
        
        # Get mapping
        mapping = self.template_mapping_service.get_mapping('Invoice')
        
        # Check mapping
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping['template_key'], 'invoice')
        self.assertEqual(mapping['template_scope'], 'enterprise')
    
    def test_process_categorization_result(self):
        """Test processing categorization result."""
        # Mock metadata extraction and application
        with patch('modules.template_processing.MetadataProcessor.process_file', return_value={
            'status': 'success',
            'file_id': 'file123',
            'category': 'Invoice'
        }):
            # Process categorization result
            result = self.processing_service.process_categorization_result({
                'file_id': 'file123',
                'category': 'Invoice',
                'confidence': 0.8
            })
            
            # Check result
            self.assertEqual(result['status'], 'success')
            self.assertEqual(result['file_id'], 'file123')
            self.assertEqual(result['category'], 'Invoice')


class TestConfiguration(unittest.TestCase):
    """Test configuration components."""
    
    def setUp(self):
        """Set up test environment."""
        # Create configuration
        self.config = AutomatedWorkflowConfig()
        
        # Reset configuration to defaults
        self.config.update_config(self.config._get_default_config())
    
    def test_enable_disable(self):
        """Test enabling and disabling automated workflow."""
        # Enable
        self.config.enable_automated_workflow()
        
        # Check enabled
        self.assertTrue(self.config.is_enabled())
        
        # Disable
        self.config.disable_automated_workflow()
        
        # Check disabled
        self.assertFalse(self.config.is_enabled())
    
    def test_monitored_folders(self):
        """Test monitored folders configuration."""
        # Add folder
        result = self.config.add_monitored_folder('folder123', 'Test Folder')
        
        # Check result
        self.assertTrue(result)
        
        # Get folders
        folders = self.config.get_monitored_folders()
        
        # Check folders
        self.assertEqual(len(folders), 1)
        self.assertEqual(folders[0]['id'], 'folder123')
        self.assertEqual(folders[0]['name'], 'Test Folder')
        
        # Remove folder
        result = self.config.remove_monitored_folder('folder123')
        
        # Check result
        self.assertTrue(result)
        
        # Get folders
        folders = self.config.get_monitored_folders()
        
        # Check folders
        self.assertEqual(len(folders), 0)
    
    def test_confidence_threshold(self):
        """Test confidence threshold configuration."""
        # Set threshold
        result = self.config.set_confidence_threshold(0.8)
        
        # Check result
        self.assertTrue(result)
        
        # Get threshold
        threshold = self.config.get_confidence_threshold()
        
        # Check threshold
        self.assertEqual(threshold, 0.8)


class TestIntegration(unittest.TestCase):
    """Test integration components."""
    
    def setUp(self):
        """Set up test environment."""
        # Create mock client
        self.mock_client = MagicMock()
        
        # Create workflow manager
        self.workflow_manager = AutomatedWorkflowManager(self.mock_client)
    
    def test_initialize_workflow(self):
        """Test initializing automated workflow."""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.is_enabled.return_value = True
        mock_config.get_webhook_port.return_value = 5000
        mock_config.get_monitored_folders.return_value = [
            {'id': 'folder123', 'name': 'Test Folder'}
        ]
        
        # Mock event stream
        with patch('modules.integration.get_automated_workflow_config', return_value=mock_config):
            with patch('modules.event_stream.start_event_stream') as mock_start:
                with patch('modules.event_stream.get_event_processor') as mock_processor:
                    with patch('modules.event_stream.get_webhook_manager') as mock_webhook:
                        # Initialize workflow
                        result = self.workflow_manager.initialize_automated_workflow()
                        
                        # Check result
                        self.assertTrue(result)
                        
                        # Check event stream started
                        mock_start.assert_called_once()
                        
                        # Check event processor initialized
                        mock_processor.assert_called()
                        
                        # Check webhooks registered
                        mock_webhook.assert_called()


if __name__ == '__main__':
    unittest.main()

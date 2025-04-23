# Box Metadata Extraction Application - Automated Workflow

This README provides an overview of the enhanced Box Metadata Extraction application with automated workflow capabilities.

## Overview

The Box Metadata Extraction application now supports two workflow modes:

1. **Manual Processing** - The original workflow where users manually select files, configure metadata, process files, review results, and apply metadata.
2. **Automated Processing** - A new event-driven workflow that automatically processes files uploaded to monitored Box folders.

## Automated Workflow Features

- **Event-Driven Processing**: Automatically processes files as they are uploaded to monitored Box folders
- **Confidence-Based Routing**: Routes documents with high confidence scores to automated processing and flags low-confidence documents for manual review
- **Configurable Mapping**: Allows users to define mappings between document categories and metadata templates
- **Monitoring Dashboard**: Provides visibility into processing status, review queue, and processing history
- **Flexible Configuration**: Supports customization of monitored folders, AI models, confidence thresholds, and more

## Components

The automated workflow consists of the following components:

- **Event Stream Integration**: Handles Box webhooks and event processing
- **Automated Categorization**: Categorizes documents and routes them based on confidence
- **Template Processing**: Maps categories to templates and applies metadata
- **Configuration Interface**: Provides UI for configuring the automated workflow
- **Integration Layer**: Connects automated workflow components with the existing application

## Getting Started

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   streamlit run app.py
   ```

3. Authenticate with Box and select the workflow mode (Manual or Automated)

4. For automated workflow:
   - Configure monitored folders
   - Set up category-to-template mappings
   - Adjust confidence threshold and other settings
   - Monitor processing through the dashboard

## Configuration

The automated workflow can be configured through the Configuration interface, which includes:

- **Folder Selection**: Select Box folders to monitor for new file uploads
- **AI Model Configuration**: Choose AI model and set confidence threshold
- **Template Mapping**: Define mappings between document categories and metadata templates
- **Advanced Settings**: Configure webhook settings and other advanced options

## Monitoring

The monitoring dashboard provides visibility into the automated workflow:

- **Processing Status**: View overall status and metrics
- **Review Queue**: Review and approve/reject low-confidence documents
- **Processing History**: View history of processed documents

## Testing

Run the automated workflow tests:
```
python -m unittest tests.test_automated_workflow
```

## Requirements

- Python 3.7+
- Streamlit 1.22.0+
- Box SDK 3.9.0+
- Other dependencies listed in requirements.txt

## Notes

- For webhook functionality, your server needs to be publicly accessible
- Configure proper security for webhook endpoints in production environments
- Consider using a reverse proxy for HTTPS support

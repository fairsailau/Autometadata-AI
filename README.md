# Box Metadata Extraction Application - README

## Overview

The Box Metadata Extraction application is a Streamlit-based tool that allows users to extract metadata from Box files using AI and apply it back to the files. The application supports both manual and automated workflows, with comprehensive webhook integration for real-time processing of new files.

## Features

- **Authentication**: Multiple authentication methods (OAuth 2.0, JWT, Developer Token)
- **Workflow Modes**: Choose between manual and automated workflows
- **Metadata Template Management**: View and select metadata templates from Box
- **Template Mapping**: Map document categories to metadata templates
- **AI Model Integration**: Configure AI models for metadata extraction
- **Advanced Settings**: Customize confidence thresholds and other settings
- **Webhook Integration**: Comprehensive Box webhook support for automated processing
- **Monitoring Tools**: Monitor webhook health and status
- **Testing Tools**: Test webhook functionality

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/fairsailau/Autometadata-AI.git
   cd Autometadata-AI
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   streamlit run app.py
   ```

## Configuration

### Box Authentication

The application supports three authentication methods:
- **OAuth 2.0**: Authenticate with a Box account using OAuth 2.0
- **JWT**: Authenticate with a Box service account using JWT
- **Developer Token**: Authenticate with a Box developer token

### Webhook Configuration

For automated workflows with webhook integration:
1. Install and configure ngrok (required for local development)
2. Configure webhook settings in the application
3. Create webhooks for Box folders
4. Start the webhook server

See the [Webhook Integration Guide](docs/webhook_integration_guide.md) for detailed instructions.

## Usage

1. **Authentication**:
   - Select your preferred authentication method
   - Authenticate with Box

2. **Workflow Selection**:
   - Choose between Manual and Automated workflow modes

3. **Manual Workflow**:
   - Browse Box files
   - Select files for metadata extraction
   - Review and apply extracted metadata

4. **Automated Workflow**:
   - Configure webhook settings
   - Set up template mappings
   - Configure AI model settings
   - Start the automated workflow

5. **Webhook Management**:
   - Monitor webhook health and status
   - Test webhook functionality
   - View webhook event history

## Documentation

- [Webhook Integration Guide](docs/webhook_integration_guide.md)
- [Event Stream Integration Design](docs/Box%20Event%20Stream%20Integration%20Design.md)
- [Automated Categorization Workflow Design](docs/Automated%20Categorization%20Workflow%20Design.md)
- [Template Selection and Processing Design](docs/Template%20Selection%20and%20Processing%20Design.md)
- [Configuration Interface Design](docs/Configuration%20Interface%20Design.md)

## Requirements

- Python 3.7+
- Streamlit 1.10+
- Box SDK 3.0+
- Flask 2.0+
- ngrok (for local webhook development)

## License

© 2024 Box Metadata Extraction

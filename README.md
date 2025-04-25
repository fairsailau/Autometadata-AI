# Box Metadata Extraction with AI

This application helps you extract metadata from Box files using AI and apply it back to the files.

## Features

- **Authentication**: Connect to Box using OAuth 2.0, JWT, or Developer Token
- **Manual Workflow**: Browse files, categorize documents, configure metadata, process files, view results, and apply metadata
- **Automated Workflow**: Configure monitored folders, template mapping, AI model, and advanced settings for automated processing
- **AI-Powered Extraction**: Extract metadata from documents using AI models
- **Metadata Application**: Apply extracted metadata back to Box files

## Installation

1. Clone the repository:
```bash
git clone https://github.com/fairsailau/Autometadata-AI.git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. **Authentication**: Connect to Box using OAuth 2.0, JWT, or Developer Token
2. **Select Workflow Mode**: Choose between Manual and Automated workflow
3. **Manual Workflow**:
   - Browse files
   - Categorize documents
   - Configure metadata
   - Process files
   - View results
   - Apply metadata
4. **Automated Workflow**:
   - Configure monitored folders
   - Set up template mapping
   - Select AI model
   - Configure advanced settings
   - Start automated workflow

## Recent Updates

- Fixed authentication flow to ensure proper navigation after successful login
- Improved page transition logic for both manual and automated workflows
- Enhanced user experience with direct navigation buttons and clear status messages
- Added comprehensive error handling and user feedback throughout the application

## License

© 2024 Box Metadata Extraction

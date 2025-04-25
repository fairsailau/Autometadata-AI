# Streamlit Cloud Deployment Guide for Autometadata-AI

This document provides guidance for deploying the Autometadata-AI application to Streamlit Cloud, with special attention to avoiding common deployment issues.

## Authentication Module Compatibility

The authentication module has been updated to ensure compatibility with Streamlit Cloud. The following changes were made:

1. Function names in `authentication.py` now match exactly what's being imported in `app.py`
2. Separate functions for each authentication method are properly exported
3. Error handling has been improved for session state access

## Deployment Steps

1. **Upload the Fixed Code**
   - Use the provided zip file containing the fixed code
   - Extract and push to your GitHub repository connected to Streamlit Cloud

2. **Configure Streamlit Cloud Settings**
   - Set the main file path to `app.py`
   - Configure any required environment variables
   - Set Python version to 3.10 or higher

3. **Deploy the Application**
   - Deploy the application through the Streamlit Cloud dashboard
   - Monitor the deployment logs for any issues

## Common Issues and Solutions

### Import Errors
If you encounter import errors:
- Check that all module names match exactly what's being imported
- Ensure all required packages are listed in `requirements.txt`
- Verify that function names match between import statements and function definitions

### Authentication Issues
If authentication doesn't work properly:
- Verify that your Box application credentials are correctly configured
- Check that redirect URIs are properly set in your Box Developer Console
- Ensure your Box application has the necessary permissions

### Session State Issues
If session state variables are not persisting:
- Use the session state manager functions for accessing session state
- Avoid direct access to session state variables without checking if they exist
- Initialize all required session state variables at application startup

## Testing After Deployment

After deploying to Streamlit Cloud:

1. Test the authentication flow with all authentication methods
2. Verify that you can progress past the authentication step
3. Test metadata template retrieval and mapping
4. Test webhook configuration if using automated workflows

## Troubleshooting

If issues persist after deployment:

1. Check the Streamlit Cloud logs for specific error messages
2. Verify that all dependencies are correctly installed
3. Test locally with the same code to identify environment-specific issues
4. Check for any Streamlit Cloud-specific limitations that might affect your application

## Contact and Support

If you encounter any issues with the deployment, please provide:
1. Screenshots of any error messages
2. Streamlit Cloud logs
3. Steps to reproduce the issue

This will help in quickly diagnosing and resolving any remaining problems.

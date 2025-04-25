# Box Metadata Extraction with Webhook Integration

This document provides an overview of the updated Box Metadata Extraction application with proper webhook integration.

## Overview

The Box Metadata Extraction application has been updated to include comprehensive webhook integration, allowing for automated metadata extraction when files are uploaded to Box. The application now includes:

1. **Webhook Configuration Interface**: A user-friendly interface for configuring Box webhooks
2. **Ngrok Integration**: Automatic integration with ngrok for exposing local webhook endpoints
3. **Webhook Server**: A Flask-based server for receiving and processing webhook events
4. **Webhook Monitoring**: Tools for monitoring the health and status of registered webhooks
5. **Webhook Testing**: Comprehensive testing tools for validating the webhook integration

## Key Components

### 1. Webhook Configuration Interface

The webhook configuration interface allows users to:
- Configure webhook settings (port, triggers, etc.)
- View and manage registered webhooks
- Start and stop the webhook server
- Monitor webhook health and status

### 2. Ngrok Integration

The application integrates with ngrok to expose local webhook endpoints to the internet, allowing Box to send webhook events to the application. The ngrok integration:
- Automatically starts and manages ngrok
- Provides a public URL for the webhook endpoint
- Handles ngrok authentication and configuration

### 3. Webhook Server

The webhook server is responsible for receiving and processing webhook events from Box. It:
- Listens for incoming webhook events
- Verifies webhook signatures for security
- Processes events asynchronously
- Triggers metadata extraction for new files

### 4. Webhook Monitoring

The webhook monitoring tools allow users to:
- Monitor the health and status of registered webhooks
- View webhook event history
- Identify and troubleshoot webhook issues
- Receive notifications for webhook failures

### 5. Webhook Testing

The webhook testing tools allow users to:
- Test the ngrok connection
- Test the webhook server
- Test webhook creation and registration
- Test webhook event processing

## Setup Instructions

1. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```

2. **Configure Ngrok**:
   - Sign up for a free ngrok account at https://ngrok.com/
   - Download and install ngrok
   - Authenticate ngrok with your authtoken: `ngrok authtoken YOUR_AUTH_TOKEN`

3. **Configure Box Developer Account**:
   - Create a Box Developer account at https://developer.box.com/
   - Create a new Box application
   - Configure OAuth 2.0 authentication
   - Add the webhook scope to your application

4. **Run the Application**:
   ```
   streamlit run app.py
   ```

5. **Configure Webhooks**:
   - Authenticate with Box
   - Navigate to the Webhooks page
   - Configure webhook settings
   - Create webhooks for your Box folders

## Usage

1. **Authentication**:
   - Select your preferred authentication method (OAuth 2.0, JWT, Developer Token)
   - Authenticate with Box

2. **Workflow Selection**:
   - Choose between Manual and Automated workflow modes

3. **Webhook Configuration**:
   - Navigate to the Webhooks page
   - Configure webhook settings
   - Create webhooks for your Box folders

4. **Webhook Monitoring**:
   - Monitor webhook health and status
   - View webhook event history
   - Troubleshoot webhook issues

5. **Metadata Extraction**:
   - Upload files to your Box folders
   - Webhook events will trigger metadata extraction
   - View and manage extracted metadata

## Troubleshooting

If you encounter issues with the webhook integration, try the following:

1. **Check Ngrok Connection**:
   - Ensure ngrok is installed and configured
   - Verify that ngrok is running and accessible
   - Check the ngrok public URL

2. **Check Webhook Server**:
   - Ensure the webhook server is running
   - Verify that the webhook endpoint is accessible
   - Check the webhook server logs for errors

3. **Check Box Configuration**:
   - Verify that your Box application has the webhook scope
   - Ensure webhooks are properly configured in Box
   - Check the Box developer console for webhook status

4. **Run Webhook Tests**:
   - Navigate to the Webhook Testing page
   - Run the comprehensive webhook tests
   - Address any issues identified by the tests

## Additional Resources

- [Box Developer Documentation](https://developer.box.com/guides/webhooks/v2/)
- [Ngrok Documentation](https://ngrok.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)

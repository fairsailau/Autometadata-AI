"""
Event Stream Integration Documentation

This document provides information about the Box event stream integration in the Autometadata-AI application.

## Overview

The Box event stream integration allows the application to receive real-time notifications when files are uploaded, copied, or moved in monitored Box folders. This enables automated processing of files without requiring manual intervention.

## How It Works

The integration uses Box webhooks to receive event notifications. When a file is uploaded to a monitored folder, Box sends a webhook notification to the application, which then processes the file automatically.

## Streamlit Integration

Streamlit does not natively support webhook endpoints, but we've implemented a solution that works in both Streamlit Cloud and local development environments:

### Streamlit Cloud

When running in Streamlit Cloud, the application can use the Streamlit app URL directly as the webhook endpoint. The application automatically detects if it's running in Streamlit Cloud and configures the webhook URL accordingly.

### Local Development

For local development, you need to use a tunnel service to expose your local webhook endpoint to the internet. The application provides instructions for setting up a tunnel service like ngrok or localtunnel.

## Configuration

The webhook integration can be configured in the "Advanced Settings" tab of the "Automated Workflow Configuration" section:

1. **Webhook Port**: The port on which the webhook server listens for incoming notifications.
2. **Enable Webhook**: Toggle to enable or disable the webhook server.

## Webhook URL

The webhook URL is automatically generated based on the environment:

- In Streamlit Cloud: `{app_url}/webhook`
- In local development with a tunnel service: `{tunnel_url}/webhook`

## Monitored Folders

You can configure which Box folders to monitor in the "Folder Selection" tab of the "Automated Workflow Configuration" section. When a file is uploaded to a monitored folder, the application will automatically process it.

## Event Types

The following event types are supported:

- `FILE.UPLOADED`: Triggered when a file is uploaded to a monitored folder.
- `FILE.COPIED`: Triggered when a file is copied to a monitored folder.
- `FILE.MOVED`: Triggered when a file is moved to a monitored folder.

## Troubleshooting

If you're experiencing issues with the webhook integration, check the following:

1. **Webhook Server**: Make sure the webhook server is running. You can check this in the "Automated Workflow Configuration" section.
2. **Webhook URL**: Make sure the webhook URL is accessible from the internet. You can test this by visiting the webhook URL in a browser.
3. **Box Developer Console**: Make sure the webhook is properly configured in the Box Developer Console.
4. **Logs**: Check the application logs for any errors related to the webhook integration.

## Local Development with Tunnel Services

For local development, you need to use a tunnel service to expose your local webhook endpoint to the internet. Here are instructions for setting up common tunnel services:

### ngrok

1. Install ngrok: https://ngrok.com/download
2. Run ngrok to expose your webhook port: `ngrok http {webhook_port}`
3. Copy the HTTPS URL provided by ngrok (e.g., `https://abcd1234.ngrok.io`)
4. Configure this URL as your webhook URL in the Box Developer Console

### localtunnel

1. Install localtunnel: `npm install -g localtunnel`
2. Run localtunnel to expose your webhook port: `lt --port {webhook_port}`
3. Copy the URL provided by localtunnel (e.g., `https://abcd1234.loca.lt`)
4. Configure this URL as your webhook URL in the Box Developer Console
"""

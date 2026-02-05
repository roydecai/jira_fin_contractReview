# Jira Contract Review Assistant

An automated contract review system that integrates with Jira to process contract attachments using AI, providing legal, tax, and financial risk assessments.

## Overview

This project automates the contract review process by monitoring Jira tickets for specific triggers, downloading attached contracts, processing them through an AI-powered contract analysis system, and posting the results back to the original ticket as comments. The system uses ByteDance's Doubao AI to provide professional legal and financial review of contracts.

## Features

- Monitors Jira tickets for specific trigger conditions
- Automatically downloads and processes PDF and DOCX contract attachments
- Performs comprehensive contract review covering:
  - Legal compliance
  - Completeness checks
  - Legal risk identification
  - Tax risk assessment
  - Financial risk analysis
- Posts AI-generated review comments back to Jira
- Runs scheduled checks during business hours (9 AM - 7 PM)

## Prerequisites

Before running this application, you need:

1. **Jira Access**
   - Jira server URL
   - Username and API token with appropriate permissions
   - Project key and issue type specifications

2. **ByteDance Doubao API Access**
   - ARK API URL
   - API Key
   - Model identifier

3. **System Dependencies**
   - Python 3.7+
   - Required Python packages (listed in installation section)

## Installation

1. Clone or download the project files

2. Install required Python dependencies:

```bash
pip install requests python-dotenv pdfplumber python-docx schedule volcengine-sdk-arkruntime
```

3. Set up your configuration (see Configuration section below)

## Configuration

Create or update the `.env` file in the project root with the following variables:

```env
# JIRA Configuration
JIRA_SERVER="https://your-company.atlassian.net"
JIRA_USERNAME="your-email@example.com"
JIRA_API_TOKEN="your-jira-api-token"
JIRA_PROJECT_KEY="YOUR-PROJECT-KEY"
JIRA_ISSUE_TYPE="IssueTypeName"
JIRA_TRIGGER_KEYWORD="@trigger-keyword"

# Doubao AI API Configuration
ARK_API_URL="https://ark.example.com/api/v3"
ARK_API_KEY="your-ark-api-key"
DOUBAO_MODEL="doubao-model-name"

# Attachment Processing Configuration
attachment_save_path="./downloads"
```

### Configuration Details

- **JIRA_SERVER**: Your Atlassian Jira server URL (e.g., https://company.atlassian.net)
- **JIRA_USERNAME**: Email address associated with your Jira account
- **JIRA_API_TOKEN**: API token generated in your Jira account settings
- **JIRA_PROJECT_KEY**: The key of the project to monitor (e.g., "FIN-CHN")
- **JIRA_ISSUE_TYPE**: The issue type to monitor (e.g., "Accounting-Expense")
- **JIRA_TRIGGER_KEYWORD**: The keyword in comments that triggers contract processing (default: "@FIN-ContractHelper")
- **ARK_API_URL**: URL for the ARK API service
- **ARK_API_KEY**: API key for ARK/Doubao service
- **DOUBAO_MODEL**: Name of the AI model to use for contract analysis
- **attachment_save_path**: Local path to save downloaded attachments (optional)

## Usage

Run the main application:

```bash
python main.py
```

The application will:
1. Connect to your Jira instance
2. Search for tickets matching your configured project and issue type
3. Check for the trigger keyword in ticket comments
4. Download the latest attachment from matching tickets
5. Process the attachment through the Doubao AI for contract review
6. Post the AI-generated review back to the ticket as a comment
7. Repeat at configured intervals during business hours (9 AM - 7 PM)

### Triggering Contract Review

To initiate a contract review:
1. Upload the contract file (PDF or DOCX) to a Jira ticket
2. Add a comment containing the trigger keyword (default: `@FIN-ContractHelper`)
3. The system will process the contract during the next scan cycle

## System Architecture

The application consists of several modules:

- **main.py**: Main application loop that orchestrates the entire workflow
- **jira_client.py**: Handles Jira API interactions (authentication, ticket retrieval, comments, attachments)
- **doubao_client.py**: Interfaces with the Doubao AI API for contract analysis
- **attachment_processor.py**: Converts Jira attachments to text for AI processing
- **trigger_checker.py**: Checks if tickets meet processing conditions
- **config.py**: Centralized configuration management
- **schedule**: Library for periodic execution

## Supported File Types

- PDF documents
- Microsoft Word documents (.docx)

## Business Hours

The application runs scheduled scans during business hours only:
- Monday to Friday, 9:00 AM to 7:00 PM
- Scans occur at 5-minute intervals within the business hours window

## Error Handling

- Network connection issues are logged and retried in subsequent cycles
- Unsupported file formats generate error messages posted to Jira
- Authentication failures are reported with troubleshooting suggestions
- API rate limits are respected according to service guidelines

## Security Considerations

- API credentials are stored in environment variables and not committed to version control
- Sensitive contract information is processed through secure API connections
- Jira API uses standard OAuth/Basic Authentication as per Atlassian guidelines

## Maintenance and Monitoring

Monitor the console output for:
- Connection status to Jira and Doubao services
- Number of tickets processed
- AI token consumption
- Error messages requiring attention

## License

This project is for internal use and follows company-specific licensing terms.
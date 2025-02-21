# Purrf

## Overview

**Purrf** is a web application designed to provide a comprehensive summary of CircleCat organization members' activity across various platforms. It aggregates data from JIRA, Google Meet, Google Chat, Microsoft Teams, and Gerrit to offer insights into individual contributions, such as the number of messages sent, code changes (CLs) submitted, and more.  Purrf helps team members track progress, assess contributions.

## Features

* **JIRA Ticket Tracking:**  Displays JIRA ticket counts and related status for each member.
* **Google Meet Session Summary:**  Shows attendance records for Google Meet sessions.
* **Google Chat Participation:**  Visualizes participation in Google Chat.
* **Microsoft Teams Activity:**  Visualizes participation in Microsoft Teams Chat.
* **Gerrit Statistics:**  Provides summaries of Gerrit contributions.
* **Interactive Dashboard:**  A web-based dashboard for viewing aggregated reports.
* **User Authentication:**  Secure access to the application.

## Getting Started

This project uses Bazel for build and dependency management.

### Prerequisites

- Bazel 8.1.0
- Python 3.12.3

### Building

Python dependencies are managed within the Bazel workspace.

To build all targets in the project:

```bash
bazel build //...
```

To build specific target in the submodule in the project:

```bash
bazel build //path/to/submodule:specific_target
```

### Running the project
After building the target, run it using:

```bash
bazel run //path/to/submodule:specific_target
```

### Before push the code
Remember to check if code format is up to standard.

To check code format, run:

```bash
bazel clean
bash lint.sh all_files
```
**Note:** If `lint.sh` fails with checksum verification errors (e.g., "sha256sum: command not found"), ensure you have the necessary **jq** installed.

To format the code, run:

```bash
bazel build //:format
bazel run //:format
```

## Accessing Google Cloud External APIs
This project integrates with Google Cloud external APIs, such as Google Chat API. To authenticate and authorize access, you need to use OAuth 2.0 client IDs.

### Obtaining OAuth 2.0 Client IDs
- Create a Google Cloud Project: If you don't have one, create a project in the Google Cloud Console.
- Enable APIs: In your project, enable the APIs you need (e.g., Google Chat API).
- Create Credentials:
  - In the Google Cloud Console, go to "APIs & Services" > "Credentials".
  - Click "Create Credentials" > "OAuth client ID".
  - Select "Desktop app" as the application type.
  - Download the generated client_secrets.json file.

### Authenticating with OAuth 2.0 Client IDs
You can use the gcloud command-line tool for authentication.

Install gcloud: If not installed, follow the Google Cloud documentation.
<https://cloud.google.com/sdk/docs/install>

Run the Authentication Command:

```bash

gcloud auth application-default login --client-id-file=/path/to/client_secrets.json --scopes=[https://www.googleapis.com/auth/chat.spaces.readonly,https://www.googleapis.com/auth/cloud-platform]

```
Replace /path/to/client_secrets.json with the path to your client_secrets.json file.

Adjust the --scopes parameter to include the necessary API scopes.

**Important Notes**
- Securely store your client_secrets.json file.
- Use appropriate scopes based on the APIs you need to access.
- Alternatively, service account key files can be used for authentication.
# Azure Event Function: Event Hub Trigger with Input and Output Bindings

This Azure Function processes events from a **source Event Hub** (e.g., `Private Jaxi Event Hub`) and forwards them to a **destination Event Hub** (e.g., `NOC/Centralized Event Hub` ). The function leverages an input Event Hub trigger to retrieve events and an output Event Hub binding to publish processed events to the destination Event Hub.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Setup and Configuration](#setup-and-configuration)
  - [Environment Variables](#environment-variables)
  - [Local Development](#local-development)
  - [Connection Variables](#connection-variables)
- [Usage](#usage)
- [Deployment](#deployment)

## Overview

This function is designed to facilitate seamless data flow between two Event Hubs:
- **Source Event Hub (Jaxi)**: Internal Event Hub for capturing events.
- **Destination Event Hub (NOC)**: Centralized Event Hub for monitoring and aggregating events.

### Requirements

- Azure Function App
- Event Hubs for both input (source) and output (destination)
- Python 3.8 or later
- Azure Functions Core Tools (for local development)

## Architecture

1. The function triggers when a message is published to the **source Event Hub**.
2. The message is processed by the function (any transformations or logging can be applied here).
3. The function publishes the message to the **destination Event Hub** for centralized monitoring.

## Setup and Configuration

### Environment Variables

The following environment variables are required for the function to connect to the Event Hubs and to store state information in Azure Storage:

| Variable Name                  | Description                                          |
|--------------------------------|------------------------------------------------------|
| `AzureWebJobsStorage`          | Azure Storage connection string for function storage |
| `SourceEventHubName`          | Name of the source (input) Event Hub                 |
| `DestinationEventHubName`     | Name of the destination (output) Event Hub           |

### Connection Variables

In addition to the environment variables, you also need to define connection variables to establish connections to the Event Hubs:

| Variable Name                      | Description                                         |
|------------------------------------|-----------------------------------------------------|
| `SourceEventHubConnectionString`         | Connection string for the source Event Hub          |
| `DestinationEventHubConnectionString`    | Connection string for the destination Event Hub     |

#### Configuring Locally
Define these variables in `local.settings.json` for local development:

```json
{
    "IsEncrypted": false,
    "Values": {
        "AzureWebJobsStorage": "<your-storage-connection-string>",
        "FUNCTIONS_WORKER_RUNTIME": "python",
        "AzureWebJobsFeatureFlags":"EnableWorkerIndexing",
        "SourceEventHubName": "kafka-default-topic",
        "DestinationEventHubName": "noc-event-hub"
    },
    "ConnectionStrings": {
        "SourceEventHubConnectionString": "<source-connection-string>",
        "DestinationEventHubConnectionString": "<destination-connection-string>"
    }
}

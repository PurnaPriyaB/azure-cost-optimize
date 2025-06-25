# Azure Billing Records Cost Optimization

This project implements a cost-efficient archival solution for billing records stored in Azure Cosmos DB by automatically moving old records to Azure Blob Storage using Terraform and Azure Functions.

---

## Problem

- Cosmos DB stores over 2 million billing records.
- Records older than 90 days are rarely accessed.
- Growing data size increases storage and request costs.

## Goal

- Reduce costs by archiving records older than 90 days.
- Keep archived data accessible with low latency.
- Maintain existing APIs without downtime or changes.

---

## Solution Overview

- Use Cosmos DB TTL (90 days) to expire old records.
- Azure Function runs daily to:
  - Archive expired records to Blob Storage (compressed).
  - Delete archived records from Cosmos DB.
- Billing API reads from Cosmos DB and falls back to Blob Storage if record is missing.

---

## Architecture Diagram



                       +--------------------+
                       |     API Clients    |
                       +---------+----------+
                                 |
                                 v
                        +--------+--------+
                        |    Billing API   |
                        +--------+--------+
                                 |
              +-----------------+------------------+
              |                                    |
              v                                    v
   +--------------------+             +---------------------------+
   |   Azure Cosmos DB  |             |    Azure Blob Storage     |
   |  (≤ 90 days data)  |<---+        |  (Archived .gz records)   |
   +---------+----------+    |        +---------------------------+
             |               |
             |   Not Found   |
             |               |
             v               |
   +-------------------------+         
   |    Azure Function App   |   <-- scheduled daily job
   | (archive + fallback API)|   
   +-------------------------+

   


---

## Components

| Component           | Description                                    |
|---------------------|------------------------------------------------|
| Terraform           | Deploys Cosmos DB, Blob Storage, Azure Function|
| Cosmos DB           | Stores recent billing records (≤90 days)        |
| Azure Blob Storage  | Stores archived records as compressed blobs     |
| Azure Function      | Archives old records daily and serves fallback   |
| Billing API         | Reads from Cosmos DB, fallback to Blob Storage  |

---

## Deployment Instructions

### Prerequisites

- Azure CLI installed and logged in (`az login`)
- Terraform installed
- Python 3.9+ (for Azure Function dependencies)
- Azure Functions Core Tools (optional)

### Steps
1. Clone the repo:

   ```bash
   git clone <your-repo-url>
   cd azure-cost-optimize
   
2. Initialize Terraform:
Initialize Terraform in your project directory. This downloads the required provider plugins and sets up the backend.

   ```bash
   terraform init

3. Preview Infrastructure Deployment
Generate and review the Terraform execution plan to see what resources will be created or modified.

   ```bash
   terraform plan
4.  Apply Terraform Configuration
Deploy the infrastructure by applying the Terraform configuration.
     ```bash
     terraform apply
     
   Type yes when prompted to confirm the deployment.

5. Deploy the Azure Function
Package and deploy the Azure Function responsible for archiving old billing records.
     ```bash
     cd archive-function
     pip install -r requirements.txt -t .
     zip -r ../archive-function.zip .
     cd ..
     az functionapp deployment source config-zip \
    --resource-group billing-archiver-rg \
    --name billing-archiver-func \
    --src archive-function.zip


* Ensure Python and Azure CLI are installed and you're logged in (az login).

* This zips the function and deploys it to your Azure Function App.

* Once deployed, the function runs on a schedule and begins archiving records older than 90 days.


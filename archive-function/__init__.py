import os, json, gzip, datetime
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient
import azure.functions as func

cosmos_client = CosmosClient.from_connection_string(os.environ["COSMOS_DB_CONNECTION_STRING"])
container = cosmos_client.get_database_client("billingdb").get_container_client("billingRecords")

blob_service = BlobServiceClient.from_connection_string(os.environ["AzureWebJobsStorage"])
archive_container = blob_service.get_container_client("archived-records")

def main(mytimer: func.TimerRequest) -> None:
    cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=90)).isoformat()
    query = f"SELECT * FROM c WHERE c.createdAt < '{cutoff}'"
    for record in container.query_items(query, enable_cross_partition_query=True):
        blob_name = f"{record['id']}.json.gz"
        content = gzip.compress(json.dumps(record).encode())
        archive_container.upload_blob(blob_name, content, overwrite=True)
        container.delete_item(record['id'], partition_key=record['partitionKey'])

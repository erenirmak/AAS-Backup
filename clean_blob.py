from azure.storage.blob import BlobServiceClient

import datetime
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

logging.basicConfig(
    filename=os.getenv('CLEANUP_LOG_FILE_PATH', "C:/path/to/your/logs/Logs/cleanup_backups.log"),
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Starting blob cleanup process.")
logging.info("Loading environment variables.")
# Azure Storage credentials
STORAGE_ACCOUNT_NAME = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
STORAGE_ACCOUNT_KEY = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
STORAGE_CONTAINER_NAME = os.getenv('AZURE_STORAGE_CONTAINER_NAME')
ENDPOINT_SUFFIX = os.getenv('AZURE_STORAGE_ENDPOINT_SUFFIX', 'core.windows.net')

retention_period = 5
logging.info(f"------------------------------------------------------------------")
logging.info("Connecting to Azure Blob Storage.")
blob_service_client = BlobServiceClient(account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.{ENDPOINT_SUFFIX}", credential=STORAGE_ACCOUNT_KEY)
container_client = blob_service_client.get_container_client(STORAGE_CONTAINER_NAME)
blobs = container_client.list_blobs()
logging.info("Connected to Azure Blob Storage. Getting list of blobs in the container.")
logging.info("Starting blob deletion process.")
logging.info(f"------------------------------------------------------------------")
for blob in blobs:
    logging.info(f"Processing blob: {blob.name}")
    try:
    # Extract the date from the blob name
        blob_date_str = blob.name.split('_')[-1].replace('.abf', '')
        blob_date = datetime.datetime.strptime(blob_date_str, '%d-%m-%Y').date()
    except Exception as e:
        logging.warning(f"Skipping blob {blob.name} due to date parsing error: {e}")
        logging.info(f"------------------------------------------------------------------")
        continue
    
    logging.info(f"Blob creation date is being checked.")
    if (datetime.datetime.now().date() - blob_date).days > retention_period:
        logging.info(f"Blob {blob.name} is older than retention period of {retention_period} days, deleting.")
        try:
            blob_client = container_client.get_blob_client(blob)
            blob_client.delete_blob()
            logging.info(f"Deleted old backup: {blob.name}")
        except Exception as e:
            logging.error(f"Error deleting blob {blob.name}: {e}")
        
    else:
        logging.info(f"Backup {blob.name} is within retention period, skipping deletion.")
    
    logging.info(f"------------------------------------------------------------------")
    
logging.info("Blob cleanup process completed.")
logging.info(f"------------------------------------------------------------------")
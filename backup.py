import win32com.client

import datetime
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Date Settings
date_format = "%d-%m-%Y"
today = datetime.datetime.today().date()
today_format = today.strftime(date_format)

# Logging Settings
logging.basicConfig(
    filename=os.getenv('BACKUP_LOG_FILE_PATH', "C:/path/to/your/logs/Logs/backup.log"),
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')


logging.info("Starting backup process.")
logging.info(f"Backup date: {today_format}")
logging.info("Loading environment variables.")
# Azure AD App credentials
TENANT_ID = os.getenv('AZURE_TENANT_ID')
CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')
SCOPE = os.getenv('AZURE_SCOPE')

# AAS connection
SERVER = os.getenv('AAS_SERVER')
DATABASE = os.getenv('AAS_MODELS', '').split(",")

logging.info(f"------------------------------------------------------------------")
logging.info("Connecting to Azure Analysis Services.")
# Use ADODB via pywin32
conn = win32com.client.Dispatch("ADODB.Connection")
conn.Provider = "MSOLAP"
conn.Properties("Data Source").Value = SERVER
conn.Properties("Persist Security Info").Value = "True"
conn.Properties("User ID").Value = f"app:{CLIENT_ID}@{TENANT_ID}"
conn.Properties("Password").Value = CLIENT_SECRET
conn.Open()
logging.info("Connected to Azure Analysis Services.")

cmd = win32com.client.Dispatch("ADODB.Command")
cmd.ActiveConnection = conn

logging.info("Starting backup process.")
logging.info(f"------------------------------------------------------------------")
for db in DATABASE:
    
    backup_name = db.replace(db, "IsoGenel") if "IsoGenel" in db else db
    
    logging.info(f"Backing up database: {db}")
    logging.info(f"Backup name: {backup_name}")

    # XMLA Backup Command
    xmla_backup = f"""
    <Backup xmlns="http://schemas.microsoft.com/analysisservices/2003/engine">
    <Object>
        <DatabaseID>{db}</DatabaseID>
    </Object>
    <File>{backup_name}_{today_format}.abf</File>
    <AllowOverwrite>true</AllowOverwrite>
    <ApplyCompression>true</ApplyCompression>
    </Backup>
    """
    logging.info(f"Executing backup command for database: {db}")
    logging.info(f"Backup command generated successfully.")
    logging.info(f"Executing backup command for database: {db}")
    try:
        cmd.CommandText = xmla_backup
        cmd.Execute()
        logging.info(f"Backup command executed successfully for database: {db}")
        logging.info(f"------------------------------------------------------------------")
    except Exception as e:
        logging.error(f"Error executing backup command for database {db}: {e}")
        logging.info(f"Backup command failed for database: {db}")
        logging.info(f"------------------------------------------------------------------")
        continue
    
logging.info(f"Backup process completed for all databases.")
logging.info(f"------------------------------------------------------------------")
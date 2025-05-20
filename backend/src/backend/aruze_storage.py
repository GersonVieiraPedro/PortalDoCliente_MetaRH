from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContentSettings
import os
from dotenv import load_dotenv
load_dotenv()

AZURE_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
AZURE_STORAGE_ACCOUNT_KEY = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
SAS_TOKEN = os.getenv("SAS_TOKEN")

connection_string = (
    f"DefaultEndpointsProtocol=https;"
    f"AccountName={AZURE_STORAGE_ACCOUNT_NAME};"
    f"AccountKey={AZURE_STORAGE_ACCOUNT_KEY};"
    f"EndpointSuffix=core.windows.net"
)
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

from PIL import Image
from io import BytesIO

def convert_to_png(data: bytes) -> bytes:
    image = Image.open(BytesIO(data)).convert("RGBA")
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()



def upload_image(filename: str, data: bytes):
    print("file_name:", filename)
    print("data type:", type(data))
    print("data size:", len(data) if hasattr(data, '__len__') else 'stream')
    content_type = "image/jpeg" if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg") else "image/png"
        
    blob_client = container_client.get_blob_client(filename)
    blob_client.upload_blob(
        data,
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type)
    )
    return get_image_url(filename)


def get_image_url(filename: str):
    return f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{CONTAINER_NAME}/{filename}"

def delete_image(filename: str):    
    blob_client = container_client.get_blob_client(f"fotos/usuarios/{filename}")
    blob_client.delete_blob()

def list_images():
    return [blob.name for blob in container_client.list_blobs()]

def image_exists(filename: str):
    blob_client = container_client.get_blob_client(f"fotos/usuarios/{filename}")
    return blob_client.exists()

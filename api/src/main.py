from webdav3.client import Client

import os
from dotenv import load_dotenv
from extract_metadata  import extract_data



def _get_webdab3_client(cloud_url="minube.uh.cu"):
    cloud_id = os.environ.get("UH_CLOUD_ID")
    cloud_password = os.environ.get("UH_CLOUD_PASSWORD")

    options = {
        "webdav_hostname": f"http://{cloud_url}/remote.php/{cloud_id}",
        "webdav_login": cloud_id,
        "webdav_password": cloud_password,
    }

    return Client(options)
    # client.verify = False  # omitir verificación de certificado SSL si es necesario



def _sync_folders(remote_directory_path:str,local_directory_path:str,cloud_url:str="minube.uh.cu"):
    client=_get_webdab3_client(cloud_url)
    client.sync(remote_directory_path,local_directory_path)
    
    




def main():
    
    load_dotenv()
    
    local_folder="/shared"
    
    _sync_folders("/shared",local_folder,"localhost:8080")
    
    extract_data()
    
        
    
    
    
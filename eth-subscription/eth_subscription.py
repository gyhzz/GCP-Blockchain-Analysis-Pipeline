import asyncio
import json
from websockets import connect
import configparser
from google.cloud import storage
from datetime import datetime


# Function to load configuration
def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['DEFAULT']['InfuraWsUrl'], config['DEFAULT']['GcsBucketName']


# Function to upload a file to Google Cloud Storage
def upload_to_gcs(bucket_name, json_data, destination_blob_name):

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    # Convert the JSON data to a string and upload it
    blob.upload_from_string(json.dumps(json_data), content_type='application/json')

    print(f"Data uploaded to {destination_blob_name}.")


async def get_event():
    infura_ws_url, gcs_bucket_name = load_config()

    async with connect(infura_ws_url) as ws:
        await ws.send(json.dumps({"id": 1, "method": "eth_subscribe", "params": ["newHeads"]}))
        subscription_response = await ws.recv()
        print(subscription_response)

        # Now subscribed to the event; keep listening for new events
        while True:

            try:
                message = await asyncio.wait_for(ws.recv(), timeout=60)
                data = json.loads(message)['params']['result']

                # Generate unique file name
                block_number = int(data['number'], 16)
                date = datetime.today().strftime('%Y%m%d')
                file_name = f'ethereum_blocks/{date}/block{block_number}'

                # Upload JSON data to GCS bucket
                upload_to_gcs(gcs_bucket_name, data, file_name)

            except asyncio.TimeoutError:
                print("Timeout waiting for a message")

            except Exception as e:
                print(f"An error occurred: {e}")
                break  # Exiting the loop in case of an error


if __name__ == "__main__":
    asyncio.run(get_event())
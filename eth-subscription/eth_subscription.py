import asyncio
import json
from websockets import connect
import configparser


def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['DEFAULT']['InfuraWsUrl']


async def get_event():
    infura_ws_url = load_config()
    async with connect(infura_ws_url) as ws:
        await ws.send(json.dumps({"id": 1, "method": "eth_subscribe", "params": ["newHeads"]}))
        subscription_response = await ws.recv()
        print(subscription_response)
        # Now subscribed to the event; keep listening for new events
        while True:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=60)
                print(json.loads(message))
            except asyncio.TimeoutError:
                print("Timeout waiting for a message")
            except Exception as e:
                print(f"An error occurred: {e}")
                break  # Exiting the loop in case of an error


if __name__ == "__main__":
    asyncio.run(get_event())
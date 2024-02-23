### Ethereum Subscription Service

#### Description
This service acts as a streaming data source for Ethereum blockchain data by connecting to an Infura Ethereum mainnet websocket API and listens for new blocks posted on the Ethereum blockchain.It reads block header data for each new block posted in a JSON string format, converts it into a parquet file and store into a data lake (Google Cloud Storage bucket).

##### V1 
- Set up connection to Infura wss API endpoint
- Create separate config.ini file to store endpoint URL (might change this to an environment variable later to secure URL)
- Create asynchro function to listen to endpoint for new messages
- Prints each new JSON message to stdout
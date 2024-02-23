### Ethereum Subscription Service

#### Description
This service acts as a streaming data source for Ethereum blockchain data by connecting to an Infura Ethereum mainnet websocket API and listens for new blocks posted on the Ethereum blockchain.It reads block header data for each new block posted in a JSON string format, converts it into a parquet file and store into a data lake (Google Cloud Storage bucket).

##### V1 
- Set up connection to Infura wss API endpoint
- Create separate config.ini file to store endpoint URL (might change this to an environment variable later to secure URL)
- Create asynchro function to listen to endpoint for new messages
- Prints each new JSON message to stdout
- Application contains Dockerfile and deployment configuration

##### V2
- Instead of sending block details to stdout, block details will be uploaded to a Google Cloud Storage bucket which acts as a data lake for raw Ethereum block header JSON
- Each block will create a new unique file Ethereum_blocks/YYYYMMDD/block<block_number>
- GKE deployment YAML file added Kubernetes service account gcs-writer-sa to allow writing to Google Cloud Storage (Remember to create a IAM service account that has the following roles: Storage Object Admin, Service Account Token Creator. Also, make sure to allow KSA to impersonate this IAM SA by adding policy binding and kubectl annotation)
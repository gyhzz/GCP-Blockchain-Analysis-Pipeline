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


### Kafka Service on GKE

#### Description
This will be the main message broadcasting service for stream processing pipelines. It contains a kafka topic called eth-block-details which collects Ethereum block header details such as block number, block hash, and gas fee details and broadcasts to its subscribers. The service populating this kafka topic is a Cloud Functions instance running Pubsub which monitors the data lake of Ethereum Subscription Service and pushes new files to the GKE kafka cluster. Using Cloud Functions instead of having the kafka cluster use Pubsub to listen to bucket events effectively decouples and isolates the data source from data consumers. The intermediate data storage can always be changed without having to make much changes to this kafka service.

##### V1 
- Deployed a kafka cluster to GKE using strimzi with 3 replicas
- Each replica is a node that can run this kafka cluster. If a single node fails, there are 2 other nodes that can run kafka jobs increasing availability
- Currently there's 1 kafka topic deployed with 3 partitions and 3 replicas
- This means that the data log of the kafka topic is split into 3 partitions, each having part of the full log. This allows each partition to be processed by a different node, allowing distributed processing
- Each partition is also replicated 3 times across different nodes to increase data redundancy to reduce probability of data loss

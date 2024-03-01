# Data Pipeline for Blockchain Analytics

![alt text](https://github.com/gyhzz/GCP-Blockchain-Analysis-Pipeline/blob/main/images/data_architecture_2.png?raw=true)

![alt text](https://github.com/gyhzz/GCP-Blockchain-Analysis-Pipeline/blob/main/images/data_architecture_flow.png?raw=true)

## Data Architecture and Design Choice
The primary purpose of this project is to design and develop a portable and lightweight big data platform and is meant to serve a diverse group of users. The design of this platform focuses on key software design principles of portability, modularity, scalability, and maintainability, as well as data governance and data democratization principles such as data traceability and accessibility. Data engineers are able to develop and deploy scalable and fault-tolerant data ingestion and data processing pipelines in a consistent manner, while data analysts and business users are able to access and visualize clean and relevant data which can be be used to make business decisions.

- Portability, Where Possible
The platform is developed with portability as a core design principle, where each service is containerized and packaged together with their own depedency requirements and run on isolated environments. Each service is packaged into docker containers and deployable on Kubernetes, meaning they can be deployed and run anywhere kubernetes is supported such as on-prem systems or cloud platforms. 

- Data Traceability
In order to promote data governance and the responsible use of data, all data ingested into the data platform should be traceable and available for auditing or data recovery purposes.

- Data Democratization
All raw data and transformed data should be made easily accessible to anyone, business users or analysts, who require access as long as they have the necessary rights to access the data.
 
___

### Ethereum Subscription Service (Data Source)

#### Description
This service acts as a streaming data source for Ethereum blockchain data by connecting to an Infura Ethereum mainnet websocket API and listens for new blocks posted on the Ethereum blockchain. It reads block header data for each new block posted in a JSON string format and stores it into a data lake (Google Cloud Storage bucket).

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

___

### Kafka Service on GKE (Event Streaming)

#### Description
This will be the main message broadcasting service for stream processing pipelines. It contains a kafka topic called eth-block-details which collects Ethereum block numbers and broadcasts to its subscribers. The service populating this kafka topic is a Cloud Functions instance running Pubsub which monitors the data lake of Ethereum Subscription Service and pushes data of new files uploaded to the GKE kafka cluster. Using Cloud Functions instead of having the kafka cluster use Pubsub to listen to bucket events effectively decouples and isolates the data source from data consumers. The intermediate data storage can always be changed without having to make much changes to this kafka service.

- When deploying a kafka cluster in GKE in free trial period using strimzi, some services such as zookeeper and entity operator may have issues starting up due to limited quota if using GKE autopilot
- In free trial, quota for CPU, memory, storage cannot be increased (sending in a request could be possible)
- Will face GKE scaling issue even if replica set to 1
- Kafka cluster may not run properly without zookeeper and entity operator do not start successfully
- To overcome this, configure your own cluster instead of using autopilot
- Use 3 nodes per pool with e2-standard-2 machine and don't enable node scaling
- The kafka cluster should be able to run comfortably in this set up
- To check current resource utilization, go to IAM and Admin > Quotas and System Limits > Search for global_in_use_addresses > Compute Engine API

##### V1 
- Deployed a kafka cluster to GKE using strimzi with 3 replicas
- Each replica is a node that can run this kafka cluster. If a single node fails, there are 2 other nodes that can run kafka jobs increasing availability
- Currently there's 1 kafka topic deployed with 3 partitions and 3 replicas
- This means that the data log of the kafka topic is split into 3 partitions, each having part of the full log. This allows each partition to be processed by a different node, allowing distributed processing
- Each partition is also replicated 3 times across different nodes to increase data redundancy to reduce probability of data loss

##### V2
- Changed kafka cluster replica to 1 and kafka topic replica and partition to 1 to reduce resource allocation (due to GCP resource quota)
- Added new listener with port 9094 to the kafka cluster to allow external communication

___

### GCS Notification Service Using Cloud Function and Pubsub

#### Description
This service monitors the blockchain-data-lake bucket for new file uploads. Each new file uploaded to this bucket will be pushed to a Pubsub topic which automatically triggers the cloud function. This cloud function collects the bucket name and file name from the event details, accesses the file and pulls the block number data. This block number is then sent to the kafka topic on GKE.

##### To upgrade in the future
- Currently, Python 3.12 has issues with the kafka python module giving an error of kafka.vendor.six.moves module not found
- A temporary fix is to replace this module installation with this: pip install git+https://github.com/dpkp/kafka-python.git
- Once the kafka module for Python 3.12 has been fixed, use the proper kafka module instead

##### V1 
- Created Pubsub service that monitors the GCS bucket for new file uploads
- Each new file uploaded sends a notification to this Pubsub topic which triggers the cloud function
- Cloud function collects the bucket name and file name from event details
- Sample structure of the pubsub event message is included in gcs-notifications/pubsub_notifications_sample.json
- The file is accessed and the block number is collected from the file
- Block number is pushed to the kafka topic on GKE
- Use the kafka_test_consumer_app.py to check for messages coming in in real-time

___

### Spark Streaming Job on GKE

#### Description
This Spark streaming job deployed on GKE is developed in pyspark and uses the spark-sql-kafka-0-10_2.12 kafka integration library for Spark from Maven Repositories. This library is a kafka connector for Spark and allow Spark to read and publish messages to kafka topics and is installed at runtime as defined in the docker image configuration. In this application, Spark reads messages from a kafka topic that serves raw data, performs some transformation, and publishes the transformed data to another kafka topic.

- **Spark Version**: 3.5.1, **Scala Version**: 2.12.18, **Kafka Version**: 0.10
- Kafka Integration Library Link: https://mvnrepository.com/artifact/org.apache.spark/spark-sql-kafka-0-10_2.12/3.5.1

##### V1 
- The Spark application is compiled into a docker image that uses Spark 3.5.1 as its base image. This Spark base image contains Spark, Python3, Pip3, but no kafka connector.
- At runtime, the docker image is instructed to install the kafka integration library before starting the pyspark script
- In the pyspark script, spark connects to the kafka topic via the kafka boostrap server's external IP, kafka topic name, and group ID
- The message receieved from the kafka topic is in key-value structure, where the key acts as a message identifier which can be used for partitioning or grouping of data, and value stores the actual published data.
- Abstract the value and convert it from binary format to string and perform some transformations
- Finally, the transformed data is then pushed to another kafka topic
- This streaming job runs continuously unless instructed to halt

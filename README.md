# RE-Miner-Hub

RE-Miner-Hub is a web-service system designed to empower researchers with the capability to conduct feature extraction and emotion classification tasks using a common API syntax. RE-Miner-Hub serves as a centralized orchestration service of heterogeneous software components (both from a logic and physical point of view), each of them deployed as decoupled, decentralized software resources. This architecture facilitates re-usability of third-party methods, which can extend RE-Miner set of tasks by either replicating and embedding these techniques as a new RE-Miner software module or simply by using available services from the web.

### Services Provided
RE-Miner-Hub offers two main services, which are materialized as differentiated services in the codebase:

1. Emotion Extraction Service: This service specializes in extracting emotional content from text data. Researchers can utilize this service to analyze and classify emotions expressed within textual content.

2. Feature Extraction Service: The feature extraction service focuses on extracting relevant features from input data. These features can be used for various tasks such as sentiment analysis, text categorization, or any other text-based analysis requiring feature representation.

## Requeriments

  - Python 3.x

## How to Install

1.  Clone the repository
```console
  git clone git@github.com:gessi-chatbots/RE-Miner-Hub.git
  cd RE-Miner-Hub
```
2. Navigate to the project directory
```console
  cd RE-Miner-Hub
```
3. Install the required dependencies
```console
  pip install -r requirements.txt
```

## How to deploy (old)
1. 
    `docker build -t re_miner_hub:latest .`
2. 
    `docker run -d --name RE_Miner_HUB -p 3002:3002 re_miner_hub:latest`

## How to deploy (new)

### Step 1: Pull image
`docker pull mtiessler/kg_repository:latest`
### Step 2: Build image
`docker build -t mtiessler/kg_repository:latest .`
### Step 3: Create kg_repository.env file
Here go the credentials to access the SPARQL Database. 
The .env file has to be in the directory where the commands are being run. 

```
DB_USERNAME=username
DB_PASSWORD=password 
```

### Step 4: Run container
`docker run -d --env-file kg_repository.env -p 3003:3003 mtiessler/kg_repository:latest`

## How to Use

1. Run the main script to start the RE-Miner-Hub server
```console
  python api.py
```
This will start the web service, and you'll see output indicating that the server is running.

## License

Free use of this software is granted under the terms of the GNU General Public License v3.0: https://www.gnu.org/licenses/gpl.html

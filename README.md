# Airspace Sectorization via Voronoi Diagrams for CSCI 716 - Computational Geometry 
By Audrey Fuller (alf9310@rit.edu), Ricky Gupta (rg4825@rit.edu) and Lauren Kaestle (lk2958@rit.edu)

TODO high level description

## Background Information
* TODO

### Algorithm Inputs and Outputs
(Include visualization)

### Problem Domain
* TODO

## Existing Research
* TODO
* Include the main paper 

## Algorithm Description
* TODO: Ricky

### Complexity Analysis 
* Running time for different inputs

## How to Run Locally
### Prerequisites
The following must be installed in order for the system to run locally:
- Docker with Docker Compose
- A free tier account on [OpenSky](https://opensky-network.org/)

All further instructions will assume that the above has been satisfied.

### Setting up the Environment
1. Obtain the API credentials for your OpenSky account by visiting the [account page](https://opensky-network.org/my-opensky/account). On the left hand side, under 'API Client' create your own API client credentials.
2. In root of the project, create a file called `.env.local` formatted as follows:
```env
OPENSKY_CLIENT_ID=<client-id>
OPENSKY_CLIENT_SECRET=<client-secret>
```
Replace the items in tags with the credentials received from the account page.

### Running the Application
1. In the root of the project, run `docker compose up --build -d`. This will start the docker build process for the backend and frontend containers.
2. Once the containers are running, open up Docker Desktop to confirm they are working. There should be a compose project called `csci-716-final-project` with two containers running: `frontend` and `backend`.
3. Click on the container named `frontend` and confirm it's done running. This is indicated by the text `✓ Ready in Xms` where `X` is replaced by the number of milliseconds the app took to launch.
4. Navigate to `localhost:3030` on within your local browser. The application should be hosted there.

## How to Use
- TODO

### Example Results
* TODO

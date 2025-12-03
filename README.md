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
To generate the 2D Voronoi diagrams, the program starts by using the Bowyer-Watson algorithm to generate the Delaunay triangulation of the points. This algorithm starts by generating a "super-triangle" that contains all of the points. Next, each point is incrementally added to the current triangulation. After each point is added, any "bad" triangles with this point within its circumcircle are removed and the gap left behind is re-triangulated. At the end, any triangles formed by edges of the original supertriangle are removed from the triangulation. The algorithm has a worst-case time complexity of O(n^2). To generate the Voronoi diagram, the program iterates through the triangles, connecting circumcenters of triangles that share edges. If an edge is on the border of the triangulation, the Voronoi edge is made by extending a line out from the circumcenter of the triangle to the bounding box perpendicular to the triangle's edge. Iterating through the triangles should also take O(n^2) time, maintaining O(n^2) time complexity overall.

One project we referenced in the initial week 6 presentation was the [World Airports Voronoi Map](https://www.jasondavies.com/maps/voronoi/airports/). The creator of this project also had a [similar project](https://www.jasondavies.com/maps/voronoi/). According to this project, the 3D convex hull of the spherical points is equivalent to the spherical Delaunay triangulation of these points. Based on this information, our program uses the incremental algorithm to construct the convex hull. The program stores information about the triangulation in a doubly-connected edge list (DCEL) to facilitate the "clean-up" step after each vertex is added and the Voronoi generation step. The DCEL consists of vertices (seed points), half-edges (a directed edge with a "twin", or the same edge in the opposite direction), and faces. To create the convex hull, the program starts by creating the initial tetrahedron from the first four points in the list of seeds. Next, the program iterates through the remaining points. For each point, the program iterates through all of the current faces of the hull and checks which faces are visible from this point (based on the explanation from [this lecture](https://tildesites.bowdoin.edu/~ltoma/teaching/cs3250-CompGeom/spring17/Lectures/cg-hull3d.pdf)). If the vertex isn't visible from any of the current faces, it isn't added to the hull (this means it should fall within the current hull). If it is visible from any of the current faces, these faces need to be replaced. The program iterates through the half-edges of these faces. If the half-edge is in the border set, a new face is made connecting the half-edge to the new vertex. If the half-edge isn't part of the border, it is within the hull and gets discarded. Each old face also gets discarded. This algorithm requires iterating through each point, and adding a point requires iterating through each face, for an overall time complexity of O(n^2). Converting the hull to the Voronoi diagram requires iterating through each face of the DCEL. For each face, the circumcenter is calculated, then it is connected to the circumcenters of all adjacent faces, which are found by iterating through the face's half-edges and getting the circumcenter of the face stored by the half-edge's twin. Overall, by using the DCEL to efficiently perform twin updates and generate the Voronoi diagram, overall expected time complexity for the algorithm is O(n^2).

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

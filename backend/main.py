# file:         main.py
# description:  the main script file

from fastapi import FastAPI

from voronoi import *

app = FastAPI()

@app.get("/")
def test():
    return {"output": "hello world"}


# Get the 2D Voronoi diagram for a set of example seeds
@app.get("/voronoi/2dexample")
def voronoi_endpoint():
    # Example seeds
    seeds = [(10, 10), (20, 20), (30, 10), (20, 5), (25, 15)]
    triangles = bowyer_watson(seeds)
    polygons = voronoi_from_triangulation(triangles, 0, 0, 40, 40)
    return {"voronoi_polygons": polygons}

# Get the 2d Voronoi diagram for a set of given seeds
@app.get("/voronoi/2d")
def voronoi_2d_endpoint(seeds: str):
    # Parse the seeds from the query parameter
    seed_list = []
    for pair in seeds.split(";"):
        x, y = map(float, pair.split(","))
        seed_list.append((x, y))
    triangles = bowyer_watson(seed_list)
    polygons = voronoi_from_triangulation(triangles, 0, 0, 400, 400)
    return {"voronoi_polygons": polygons}
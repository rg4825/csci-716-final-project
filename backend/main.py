# file:         main.py
# description:  the main script file

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from voronoi import *

app = FastAPI()

@app.get("/")
def test():
    return {"output": "hello world"}


app = FastAPI()

class VoronoiRequest(BaseModel):
    seeds: List[List[float]]  # List of [x, y] coordinates
    min_x: float = 0
    min_y: float = 0
    max_x: float = 100
    max_y: float = 100

@app.post("/voronoi/2dexample")
def voronoi_endpoint(request: VoronoiRequest):
    # Convert list of lists to list of tuples
    seeds = [tuple(seed) for seed in request.seeds]
    
    # Generate Voronoi diagram
    triangles = bowyer_watson(seeds)
    polygons = voronoi_from_triangulation(
        triangles, 
        request.min_x, 
        request.min_y, 
        request.max_x, 
        request.max_y
    )
    
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
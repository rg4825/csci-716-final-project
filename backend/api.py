# file:         main.py
# description:  FastAPI backend for generating 2D Voronoi diagrams using the Bowyer-Watson algorithm.

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
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


class VoronoiUserInputRequest(BaseModel):
    airport_code: str
    radius: float
    timestamp: str  # UTC timestamp
    num_seeds: int

    num_generations: int
    generation_size: int
    crossover: float
    patience: int


# Generate Voronoi diagram from POST request with seeds and bounding box
# (frontend -> backend -> frontend)
@app.post("/voronoi/2d")
def voronoi_endpoint(request: VoronoiRequest):
    # Convert list of lists to list of tuples
    seeds = [tuple(seed) for seed in request.seeds]

    # Generate Voronoi diagram
    polygons = compute_voronoi(
        seeds, request.min_x, request.min_y, request.max_x, request.max_y
    )

    return {"voronoi_polygons": polygons}


# Generate Voronoi diagram from GET request (backend -> frontend)
@app.get("/voronoi/2dstatic")
def voronoi_2d_endpoint(seeds: str):
    # Parse the seeds from the query parameter
    seed_list = []
    for pair in seeds.split(";"):
        x, y = map(float, pair.split(","))
        seed_list.append((x, y))
    polygons = compute_voronoi(seed_list, 0, 0, 400, 400)
    return {"voronoi_polygons": polygons}


# Send the user input to the backend and get the Voronoi diagram
# Voronoi user input parameters:
# - Airport Code
# - Radius (in km)
# - Start date (TODO: format?)
# - End date
# - Number of seeds
#
# Genetic algorithm parameters:
# - Number of generations
# - Generation size
# - Crossover
# - Patience
@app.post("/voronoi/userinput")
def voronoi_user_input(request: VoronoiUserInputRequest):
    # Extract user input parameters
    airport_code = request.airport_code
    radius = request.radius
    timestamp = request.timestamp
    num_seeds = request.num_seeds

    num_generations = request.num_generations
    generation_size = request.generation_size
    crossover = request.crossover
    patience = request.patience

    # TODO: Implement genetic algorithm for Voronoi diagram generation

    return {"message": "Voronoi diagram generation started"}


# Stream Voronoi diagrams over time using StreamingResponse
async def generate_voronoi():
    # Example: Stream Voronoi diagrams over time
    import asyncio
    import json
    import random

    for i in range(10):  # Simulate 10 steps of generation
        # Generate random seeds for demonstration
        seeds = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(10)]
        polygons = compute_voronoi(seeds, 0, 0, 100, 100)

        yield json.dumps({"step": i, "voronoi_polygons": polygons})
        await asyncio.sleep(1)  # Simulate time delay


# Stream the genetic algorithm output to the frontend
@app.get("/voronoi/stream")
async def voronoi_stream():
    async def event_generator():
        async for chunk in generate_voronoi():
            yield f"data: {chunk}\n\n"  # SSE format requires 'data:' prefix and double newline

    return StreamingResponse(event_generator(), media_type="text/event-stream")

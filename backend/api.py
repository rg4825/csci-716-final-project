# file:         main.py
# description:  FastAPI backend for generating 2D Voronoi diagrams using the Bowyer-Watson algorithm.

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import asyncio

from voronoi import *

app = FastAPI()

# For real-time data streaming (not supported by default in next.is API routes)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up CORS for development purposes (sending data to frontend not through a proxy)
'''
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development)
    allow_credentials=False,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)'''

@app.get("/")
def test():
    return {"output": "hello world"}


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

from genetic_algorithm import Population, Organism
import numpy as np


# --------------- Genetic Algorithm Test Endpoint ---------------

@app.get("/test/ga")
def test_ga():
    import string
    from genetic_algorithm import Population

    target = list("Hello, Computational Geometry!")

    genome = (
        list(string.ascii_letters)
        + list(string.digits)
        + list(string.punctuation)
        + [" "]
    )
    chromosome_len = len(target)

    def fitness_func(chromosomes):
        char_correct = 0
        for target_gene, chromosome_gene in zip(target, chromosomes):
            if target_gene == chromosome_gene:
                char_correct += 1

        fitness = char_correct / chromosome_len
        return fitness

    def to_string(organism):
        return f"\n\tchromosomes: {''.join(organism.chromosomes)}\n\tfitness score = {organism.fitness}"

    def reproduce_func(o1, o2, crossover=0.80):
        child_chromosome = []
        rng = np.random.default_rng()

        for gene1, gene2 in zip(o1.chromosomes, o2.chromosomes):
            p = rng.random()

            if p < crossover / 2:
                child_chromosome.append(gene1)
                continue

            elif p < crossover:
                child_chromosome.append(gene2)
                continue

            child_chromosome.append(np.random.choice(genome))

        return Organism(child_chromosome, o1.fitness_func, to_string=o1.to_string)

    def create_random_organism():
        chromosomes = []
        rng = np.random.default_rng()

        for i in range(chromosome_len):
            chromosomes.append(rng.choice(genome))

        return Organism(
            chromosomes,
            fitness_func,
            to_string=to_string,
        )

    population = Population(
        chromosome_len,
        fitness_func,
        reproduce_func,
        create_random_organism,
        threshold=0.999,
        generation_size=100,
        num_generations=5,
        organism_to_string=to_string,
        patience=0,
    )

    # Yield each generation's fittest organism as JSON
    fittest = population.fully_evolve_population()
    return fittest.to_json()


async def generate_ga_async(airport, lat, lon, generations, cells, radius):
    import string
    from genetic_algorithm import Population

    print(f"Generating GA async with airport={airport}, lat={lat}, lon={lon}, generations={generations}, cells={cells}, radius={radius}")
    target = list("Hello, Computational Geometry!")

    genome = (
        list(string.ascii_letters)
        + list(string.digits)
        + list(string.punctuation)
        + [" "]
    )
    chromosome_len = len(target)

    def fitness_func(chromosomes):
        char_correct = 0
        for target_gene, chromosome_gene in zip(target, chromosomes):
            if target_gene == chromosome_gene:
                char_correct += 1

        fitness = char_correct / chromosome_len
        return fitness

    def to_string(organism):
        return f"\n\tchromosomes: {''.join(organism.chromosomes)}\n\tfitness score = {organism.fitness}"

    def reproduce_func(o1, o2, crossover=0.80):
        child_chromosome = []
        rng = np.random.default_rng()

        for gene1, gene2 in zip(o1.chromosomes, o2.chromosomes):
            p = rng.random()

            if p < crossover / 2:
                child_chromosome.append(gene1)
                continue

            elif p < crossover:
                child_chromosome.append(gene2)
                continue

            child_chromosome.append(np.random.choice(genome))

        return Organism(child_chromosome, o1.fitness_func, to_string=o1.to_string)

    def create_random_organism():
        chromosomes = []
        rng = np.random.default_rng()

        for i in range(chromosome_len):
            chromosomes.append(rng.choice(genome))

        return Organism(
            chromosomes,
            fitness_func,
            to_string=to_string,
        )

    population = Population(
        chromosome_len,
        fitness_func,
        reproduce_func,
        create_random_organism,
        threshold=0.999,
        generation_size=2000,
        num_generations=generations,
        organism_to_string=to_string,
        patience=0,
    )

    # Yield each generation's fittest organism as JSON
    for organism, generation in population.fully_evolve_population_generator():
        await asyncio.sleep(0.0)  # Simulate async behavior
        yield {
            "generation": generation,
            "organism": organism.to_json()
        }

    # End of generator
    yield {"event": "end"}
    return


@app.get("/test/ga_async")
async def test_ga_async(
    airport: str = "Frederick Douglass Greater Rochester International Airport",
    lat: float = 43.1189, lon: float = -77.672401,
    generations: int = 10, cells: int = 20,
    radius: int = 50
):
    async def event_generator():
        async for chunk in generate_ga_async(airport, lat, lon, generations, cells, radius):
            json_data = json.dumps(chunk) # Convert from dict
            yield f"data: {json_data}\n\n"  # Proper SSE message format

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# --------------- FLIGHT Genetic Algorithm Test Endpoint ---------------

from open_sky import get_flights_lat_lng, get_flight_trajectories
MAX_32 = 2**32 - 1

@app.get("/flight/ga")
def flight_ga(
    # Rochester Airport (KROC) coordinates
    airport: str = "Frederick Douglass Greater Rochester International Airport",
    lat: float = 43.1189, lon: float = -77.672401,
    generations: int = 10, cells: int = 20,
    radius: int = 50,
):
    flights, bbox = get_flights_lat_lng(lat, lon, radius)
    trajectories = get_flight_trajectories(flights)

    y_min, x_min, y_max, x_max = bbox[0], bbox[1], bbox[2], bbox[3]
    x_diff = x_max - x_min
    y_diff = y_max - y_min

    def _encode_chromosome(x, y):
        norm_x, norm_y = (x - x_min) / x_diff, (
            y - y_min
        ) / y_diff  # normalizes to [0, 1]
        enc_x, enc_y = np.round(np.multiply(norm_x, MAX_32)).astype(
            np.uint32
        ), np.round(np.multiply(norm_y, MAX_32)).astype(
            np.uint32
        )  # uniformly maps to uint32, a small amount of precision loss
        x_bin, y_bin = np.binary_repr(enc_x, width=32), np.binary_repr(
            enc_y, width=32
        )  # 32 bit binary representation of uint32
        return x_bin, y_bin

    def _decode_chromosome(chromosome):
        enc_x, enc_y = np.uint32(int(chromosome[0], 2)), np.uint32(
            int(chromosome[1], 2)
        )
        norm_x, norm_y = np.divide(enc_x, MAX_32), np.divide(enc_y, MAX_32)
        x, y = x_min + norm_x * x_diff, y_min + norm_y * y_diff
        return float(x), float(y)

    def organism_to_voronoi(organism):
        """
        :param organism:    organism for the voronoi flight task
        :return:            seed_tree, voronoi_edges from compute_voronoi_tree
        """
        seeds = [_decode_chromosome(c) for c in organism.chromosomes]
        seed_tree, voronoi_edges = compute_voronoi_tree(
            seeds, x_min, y_min, x_max, y_max
        )
        return seed_tree, voronoi_edges

    def fitness_func(chromosomes):
        seeds = [_decode_chromosome(c) for c in chromosomes]
        cell_duration_dict = dict.fromkeys(seeds, 0)
        total_flights_in_cell = dict.fromkeys(seeds, 0)

        seed_tree, voronoi_edges = compute_voronoi_tree(
            seeds, x_min, y_min, x_max, y_max
        )
        for t in trajectories:
            cell_counter = dict.fromkeys(seeds, 0)
            prev_cell = None
            prev_waypoint = None

            for waypoint in t.itertuples():
                if waypoint.latitude < x_min or waypoint.latitude > x_max or waypoint.longitude < y_min or waypoint.longitude > y_max:
                    continue
                cell = find_closest_cell(seed_tree, seeds, (waypoint.latitude, waypoint.longitude))

                if cell_counter[cell] == 0:
                    cell_counter[cell] += 1

                if cell == prev_cell:
                    cell_duration_dict[cell] += (waypoint.timestamp - prev_waypoint.timestamp).seconds
                    prev_cell = cell
                    prev_waypoint = waypoint
                    continue

                prev_cell = cell
                prev_waypoint = waypoint

            for seed in seeds:
                total_flights_in_cell[seed] += cell_counter[seed]

        min_avg_flight_time = float('inf')
        for seed in seeds:
            duration = cell_duration_dict[seed]
            if duration == 0:
                continue  # I am assuming that we skip if it's 0, but we could theoretically say it's 0 and then break

            num_flights = total_flights_in_cell[seed]
            avg_flight_time = duration/num_flights

            if avg_flight_time < min_avg_flight_time:
                min_avg_flight_time = avg_flight_time

        return -min_avg_flight_time

    def to_string(organism):
        s = "\n\tchromosomes:"
        for chromosome in organism.chromosomes:
            s += f"\n\t\t{_decode_chromosome(chromosome)}"
        s += f"\n\tfitness: {organism.fitness}"

        return s
    
    def to_json(organism):
        return {
            "chromosomes": [ _decode_chromosome(c) for c in organism.chromosomes],
            "fitness": organism.fitness,
        }

    def _crossover_mutate_chromosomes(chromosome1, chromosome2, mutation=0.20):
        child_chromosome = np.zeros(2, dtype=np.dtypes.StringDType)
        rng = np.random.default_rng()

        for i in range(len(chromosome1[0])):
            x1, y1 = chromosome1[0][i], chromosome1[1][i]
            x2, y2 = chromosome2[0][i], chromosome2[1][i]

            px = rng.random()
            py = rng.random()
            px_mutate = rng.random()
            py_mutate = rng.random()

            if px < 0.50:
                child_chromosome[0] += x1
            else:
                child_chromosome[0] += x2

            if py < 0.50:
                child_chromosome[1] += y1
            else:
                child_chromosome[1] += y2

            if px_mutate < mutation:
                mutate_val = (int(child_chromosome[0][i]) + 1) % 2
                child_chromosome[0] = child_chromosome[0][:-1] + str(mutate_val)

            if py_mutate < mutation:
                mutate_val = (int(child_chromosome[1][i]) + 1) % 2
                child_chromosome[1] = child_chromosome[1][:-1] + str(mutate_val)

        return child_chromosome

    def reproduce_func(o1, o2, mutation=0.20):
        child_chromosomes = np.array(
            [
                _crossover_mutate_chromosomes(chrom1, chrom2, mutation)
                for chrom1, chrom2 in zip(o1.chromosomes, o2.chromosomes)
            ],
            dtype=np.dtypes.StringDType,
        )
        child_chromosomes = np.array(
            [_decode_chromosome(row) for row in child_chromosomes]
        )
        child_chromosomes = child_chromosomes[child_chromosomes[:, 0].argsort()]
        child_chromosomes = np.array(
            [_encode_chromosome(row[0], row[1]) for row in child_chromosomes],
            dtype=np.dtypes.StringDType,
        )

        return Organism(child_chromosomes, o1.fitness_func, to_string=o1.to_string)

    def create_random_organism():
        chromosomes = np.zeros((cells, 2))
        rng = np.random.default_rng()

        for i in range(cells):
            x, y = rng.uniform(x_min, x_max), rng.uniform(y_min, y_max)
            chromosomes[i] = x, y

        chromosomes = chromosomes[chromosomes[:, 0].argsort()]
        chromosomes = np.array(
            [_encode_chromosome(row[0], row[1]) for row in chromosomes],
            dtype=np.dtypes.StringDType,
        )

        return Organism(
            chromosomes,
            fitness_func,
            to_string=to_string,
        )

    population = Population(
        32,
        fitness_func,
        reproduce_func,
        create_random_organism,
        num_generations=generations,
        organism_to_string=to_string,
    )

    fittest = population.fully_evolve_population()
    print(f"{fittest}")

    # Return each generation's fittest organism as JSON
    return to_json(fittest)

# Async version of flight GA
async def generate_flight_ga_async(   
    # Rochester Airport (KROC) coordinates
    airport: str = "Frederick Douglass Greater Rochester International Airport",
    lat: float = 43.1189, lon: float = -77.672401,
    generations: int = 10, cells: int = 20,
    radius: int = 50
):  
    print(f"Generating Flight GA async with airport={airport}, lat={lat}, lon={lon}, generations={generations}, cells={cells}, radius={radius}")

    flights, bbox = get_flights_lat_lng(lat, lon, radius)
    trajectories = get_flight_trajectories(flights)

    y_min, x_min, y_max, x_max = bbox[0], bbox[1], bbox[2], bbox[3]
    x_diff = x_max - x_min
    y_diff = y_max - y_min

    def _encode_chromosome(x, y):
        norm_x, norm_y = (x - x_min) / x_diff, (
            y - y_min
        ) / y_diff  # normalizes to [0, 1]
        enc_x, enc_y = np.round(np.multiply(norm_x, MAX_32)).astype(
            np.uint32
        ), np.round(np.multiply(norm_y, MAX_32)).astype(
            np.uint32
        )  # uniformly maps to uint32, a small amount of precision loss
        x_bin, y_bin = np.binary_repr(enc_x, width=32), np.binary_repr(
            enc_y, width=32
        )  # 32 bit binary representation of uint32
        return x_bin, y_bin

    def _decode_chromosome(chromosome):
        enc_x, enc_y = np.uint32(int(chromosome[0], 2)), np.uint32(
            int(chromosome[1], 2)
        )
        norm_x, norm_y = np.divide(enc_x, MAX_32), np.divide(enc_y, MAX_32)
        x, y = x_min + norm_x * x_diff, y_min + norm_y * y_diff
        return float(x), float(y)

    def organism_to_voronoi(organism):
        """
        :param organism:    organism for the voronoi flight task
        :return:            seed_tree, voronoi_edges from compute_voronoi_tree
        """
        seeds = [_decode_chromosome(c) for c in organism.chromosomes]
        seed_tree, voronoi_edges = compute_voronoi_tree(
            seeds, x_min, y_min, x_max, y_max
        )
        return seed_tree, voronoi_edges

    def fitness_func(chromosomes):
        seeds = [_decode_chromosome(c) for c in chromosomes]
        cell_duration_dict = dict.fromkeys(seeds, 0)
        total_flights_in_cell = dict.fromkeys(seeds, 0)

        seed_tree, voronoi_edges = compute_voronoi_tree(
            seeds, x_min, y_min, x_max, y_max
        )
        for t in trajectories:
            cell_counter = dict.fromkeys(seeds, 0)
            prev_cell = None
            prev_waypoint = None

            for waypoint in t.itertuples():
                if waypoint.latitude < x_min or waypoint.latitude > x_max or waypoint.longitude < y_min or waypoint.longitude > y_max:
                    continue
                cell = find_closest_cell(seed_tree, seeds, (waypoint.latitude, waypoint.longitude))

                if cell_counter[cell] == 0:
                    cell_counter[cell] += 1

                if cell == prev_cell:
                    cell_duration_dict[cell] += (waypoint.timestamp - prev_waypoint.timestamp).seconds
                    prev_cell = cell
                    prev_waypoint = waypoint
                    continue

                prev_cell = cell
                prev_waypoint = waypoint

            for seed in seeds:
                total_flights_in_cell[seed] += cell_counter[seed]

        min_avg_flight_time = float('inf')
        for seed in seeds:
            duration = cell_duration_dict[seed]
            if duration == 0:
                continue  # I am assuming that we skip if it's 0, but we could theoretically say it's 0 and then break

            num_flights = total_flights_in_cell[seed]
            avg_flight_time = duration/num_flights

            if avg_flight_time < min_avg_flight_time:
                min_avg_flight_time = avg_flight_time

        return -min_avg_flight_time

    def to_string(organism):
        s = "\n\tchromosomes:"
        for chromosome in organism.chromosomes:
            s += f"\n\t\t{_decode_chromosome(chromosome)}"
        s += f"\n\tfitness: {organism.fitness}"

        return s
    
    # Special decode to JSON function for flight GA organism
    def to_json(organism):
        return {
            "chromosomes": [ _decode_chromosome(c) for c in organism.chromosomes],
            "fitness": organism.fitness,
        }
    
    # Special method to convert KDTree to JSON-serializable format
    def KDTree_to_json(kd_tree):
        return {
            "data": kd_tree.data.tolist(),
        }
    
    # Special method to convert Voronoi edges to JSON-serializable format
    def voronoi_edges_to_geojson(voronoi_edges):
        seed_info = [
            min(seeds, key=lambda p: p[0])[0],
            min(seeds, key=lambda p: p[1])[1],
            max(seeds, key=lambda p: p[0])[0],
            max(seeds, key=lambda p: p[1])[1]
        ]

        geojson_dict = {"type": "FeatureCollection", "polygons": [], "seeds": []}
        for cell in voronoi_edges.values():
            cell.cell_to_geojson(x_min, y_min, x_max, y_max, seed_info, geojson_dict)
        return geojson_dict

    def _crossover_mutate_chromosomes(chromosome1, chromosome2, mutation=0.20):
        child_chromosome = np.zeros(2, dtype=np.dtypes.StringDType)
        rng = np.random.default_rng()

        for i in range(len(chromosome1[0])):
            x1, y1 = chromosome1[0][i], chromosome1[1][i]
            x2, y2 = chromosome2[0][i], chromosome2[1][i]

            px = rng.random()
            py = rng.random()
            px_mutate = rng.random()
            py_mutate = rng.random()

            if px < 0.50:
                child_chromosome[0] += x1
            else:
                child_chromosome[0] += x2

            if py < 0.50:
                child_chromosome[1] += y1
            else:
                child_chromosome[1] += y2

            if px_mutate < mutation:
                mutate_val = (int(child_chromosome[0][i]) + 1) % 2
                child_chromosome[0] = child_chromosome[0][:-1] + str(mutate_val)

            if py_mutate < mutation:
                mutate_val = (int(child_chromosome[1][i]) + 1) % 2
                child_chromosome[1] = child_chromosome[1][:-1] + str(mutate_val)

        return child_chromosome

    def reproduce_func(o1, o2, mutation=0.20):
        child_chromosomes = np.array(
            [
                _crossover_mutate_chromosomes(chrom1, chrom2, mutation)
                for chrom1, chrom2 in zip(o1.chromosomes, o2.chromosomes)
            ],
            dtype=np.dtypes.StringDType,
        )
        child_chromosomes = np.array(
            [_decode_chromosome(row) for row in child_chromosomes]
        )
        child_chromosomes = child_chromosomes[child_chromosomes[:, 0].argsort()]
        child_chromosomes = np.array(
            [_encode_chromosome(row[0], row[1]) for row in child_chromosomes],
            dtype=np.dtypes.StringDType,
        )

        return Organism(child_chromosomes, o1.fitness_func, to_string=o1.to_string)

    def create_random_organism():
        chromosomes = np.zeros((cells, 2))
        rng = np.random.default_rng()

        for i in range(cells):
            x, y = rng.uniform(x_min, x_max), rng.uniform(y_min, y_max)
            chromosomes[i] = x, y

        chromosomes = chromosomes[chromosomes[:, 0].argsort()]
        chromosomes = np.array(
            [_encode_chromosome(row[0], row[1]) for row in chromosomes],
            dtype=np.dtypes.StringDType,
        )

        return Organism(
            chromosomes,
            fitness_func,
            to_string=to_string,
        )

    population = Population(
        32,
        fitness_func,
        reproduce_func,
        create_random_organism,
        num_generations=generations,
        organism_to_string=to_string,
    )

    # Yield each generation's fittest organism as JSON
    for organism, generation in population.fully_evolve_population_generator():
        await asyncio.sleep(0.0)  # Simulate async behavior

        # Convert organism to Voronoi 
        seed_tree, voronoi_edges = organism_to_voronoi(organism)
        
        # Convert voronoi edges to JSON-serializable format
        voronoi_edges_json = voronoi_edges_to_geojson(voronoi_edges)


        print(f"Generation {generation}, Organism: {organism}")
        print(f"Voronoi Edges: {voronoi_edges_json}")

        # Yield voronoi diagram data
        # TODO: Yield flights as well!
        yield {
            "generation": generation,
            "organism": to_json(organism),
            "seed_tree": KDTree_to_json(seed_tree), # KD Tree
            "voronoi_edges": voronoi_edges_json, # dictionary of seed points and Voronoi cells
        }

    # End of generator
    yield {"event": "end"}
    return

@app.get("/flight/ga_async")
async def flight_ga_async(   
    airport: str,
    lat: float, lon: float,
    generations: int, cells: int,
    radius: int
):  
    async def event_generator():
        async for chunk in generate_flight_ga_async(airport, lat, lon, generations, cells, radius):
            json_data = json.dumps(chunk) # Convert from dict
            yield f"data: {json_data}\n\n"  # Proper SSE message format

    return StreamingResponse(event_generator(), media_type="text/event-stream",)
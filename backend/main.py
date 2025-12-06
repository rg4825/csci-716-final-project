# file:         main.py
# description:  the main script file

import numpy as np

from collections import Counter

from pyarrow import int32

from open_sky import get_flights_airport, get_flight_trajectories
from genetic_algorithm import Organism, Population
from voronoi import compute_voronoi_tree, find_closest_cell

MAX_32 = 2**32 - 1


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
        generation_size=2000,
        num_generations=0,
        organism_to_string=to_string,
        patience=0,
    )
    fittest = population.fully_evolve_population()
    print(f"{fittest}")


def test_open_sky():
    data = get_flights_airport(airport="Akron Canton Regional Airport", radius=10)
    for flight in data.itertuples():
        print(flight)
    print()
    trajectories = get_flight_trajectories(data)
    for traj in trajectories:
        for i in traj.itertuples():
            print(i)
        print()


def flight_ga():
    airport = "Akron Canton Regional Airport"
    radius = 50
    cells = 20

    flights, bbox = get_flights_airport(airport, radius)
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
        organism_to_string=to_string,
    )
    fittest = population.fully_evolve_population()
    print(f"{fittest}")


def main():
    pass
    #flight_ga()


if __name__ == "__main__":
    main()

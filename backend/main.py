# file:         main.py
# description:  the main script file

import numpy as np

from open_sky import get_flights_airport, get_flight_trajectories
from genetic_algorithm import Organism, Population


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


def main():
    test_ga()


if __name__ == "__main__":
    main()

# file:         genetic_algorithm.py
# description:  contains the classes and structure for a generic GA

import numpy as np


class Organism:
    """
    Represents a single organism as a part of the population.
    """

    def __init__(self, chromosomes, fitness_func, genome):
        """
        :param chromosomes:     a list of tokens that can be considered this organism's "gene sequence"
        :param fitness_func:    the function used to evaluate how "fit" this organism is
        :param genome:          a list of all valid genetic bases
        """
        self.chromosomes = chromosomes
        self.fitness_func = fitness_func
        self.genome = genome

        self.fitness = self.fitness_func(self.chromosomes)

    def reproduce(self, other):
        child_chromosome = []
        rng = np.random.default_rng()

        for gene1, gene2 in zip(self.chromosomes, other.chromosomes):
            p = rng.random()

            if p < 0.45:
                child_chromosome.append(gene1)
                continue

            elif p < 0.90:
                child_chromosome.append(gene2)
                continue

            child_chromosome.append(np.random.choice(self.genome))

        return Organism(child_chromosome, self.fitness_func, self.genome)


class Population:
    """
    Represents a group of individuals, on which to simulate evolution on.
    """

    def __init__(
        self,
        genome,
        chromosome_len,
        fitness_func,
        generation_size=50,
        num_generations=100,
        threshold=0.90,
    ):
        """
        :param generation_size:     number of organisms per generation
        :param genome:              a list of all valid genetic bases
        :param fitness_func:        the function used to evaluate how "fit" this organism is
        :param num_generations:     the maximum number of generations
        :param threshold:           if the fitness is beyond this threshold for an organism, stop evolution
        """
        self.genome = genome
        self.chromosome_len = chromosome_len
        self.generation_size = generation_size
        self.fitness_func = fitness_func
        self.num_generations = num_generations
        self.threshold = threshold

        self.current_generation_index = 0
        self.current_generation = []

    def fully_evolve_population(self):
        """
        Given the current generation, evolve the population until either the threshold is hit or the maximum number
        of generations is hit.
        :return:
        """

    def advance_one_generation(self):
        """
        Advances the population by one generation. Changes the state of this Population object.
        :return:
        """
        pass

    def initialize_generation(self):
        """
        Updates self.current_generation if it's currently empty with self.generation_size number of organisms.
        """
        if self.current_generation:
            return

        for _ in range(self.generation_size):
            o = self.create_random_organism()
            self.current_generation.append(o)

    def create_random_organism(self):
        """
        :return:    An Organism with a random set of chromosomes.
        """
        chromosomes = []
        rng = np.random.default_rng()

        for i in range(self.chromosome_len):
            chromosomes.append(rng.choice(self.genome))

        return Organism(chromosomes, self.fitness_func, self.genome)

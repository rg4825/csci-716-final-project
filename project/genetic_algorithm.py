# file:         genetic_algorithm.py
# description:  contains the classes and structure for a generic GA


class Organism:
    """
    Represents a single organism as a part of the population.
    """

    def __init__(self, chromosomes, fitness_func):
        self.chromosomes = chromosomes
        self.fitness_score = fitness_func(self.chromosomes)

    def reproduce(self, other):
        pass


class Population:
    """
    Represents a group of individuals, on which to simulate evolution on.
    """

    def __init__(
        self,
        population_size,
        valid_genes,
        fitness_func,
        num_generations=100,
        threshold=0.01,
    ):
        self.population_size = population_size
        self.valid_genes = valid_genes
        self.fitness_func = fitness_func
        self.num_generations = num_generations
        self.threshold = threshold

        self.current_generation_index = 0
        self.current_generation = []

    def fully_evolve_population(self):
        pass

    def advance_one_generation(self):
        pass

    def create_random_organism(self):
        pass

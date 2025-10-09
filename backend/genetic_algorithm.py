# file:         genetic_algorithm.py
# description:  contains the classes and structure for a generic GA

import numpy as np

from tqdm import tqdm

class Organism:
    """
    Represents a single organism as a part of the population.
    """

    def __init__(self, chromosomes, fitness_func, genome, to_string=None):
        """
        :param chromosomes:     a list of tokens that can be considered this organism's "gene sequence"
        :param fitness_func:    the function used to evaluate how "fit" this organism is
        :param genome:          a list of all valid genetic bases
        """
        self.chromosomes = chromosomes
        self.fitness_func = fitness_func
        self.genome = genome
        self.to_string = to_string

        self.fitness = self.fitness_func(self.chromosomes)

    def reproduce(self, other, crossover=.80):
        """
        Creates a new organism using the chromosomes of each parent, with a chance of mutation equal to
        1-crossover.
        :param other:       the other organism for genes to passed on
        :param crossover:   the chance of a gene to be taken from a parent
        :return:            a new organism inheriting traits from both parents
        """
        child_chromosome = []
        rng = np.random.default_rng()

        for gene1, gene2 in zip(self.chromosomes, other.chromosomes):
            p = rng.random()

            if p < crossover/2:
                child_chromosome.append(gene1)
                continue

            elif p < crossover:
                child_chromosome.append(gene2)
                continue

            child_chromosome.append(np.random.choice(self.genome))

        return Organism(child_chromosome, self.fitness_func, self.genome, to_string=self.to_string)

    def __str__(self):
        if self.to_string is None:
            return f"{''.join(self.chromosomes)}, fitness = {self.fitness}"
        return self.to_string(self)

    def __eq__(self, other):
        return self.chromosomes == other.chromosomes


class Population:
    """
    Represents a group of individuals, on which to simulate evolution on.
    """

    def __init__(
        self,
        genome,
        chromosome_len,
        fitness_func,
        generation_size=500,
        num_generations=200,
        threshold=0.999,
        patience=0,
        organism_to_string=None
    ):
        """
        :param genome:              a list of all valid genetic bases
        :param chromosome_len:      the length of the target chromosome
        :param fitness_func:        the function used to evaluate how "fit" this organism is, the greater the fitness
                                    the better
        :param generation_size:     (opt.) number of organisms per generation, default 500
        :param num_generations:     (opt.) the maximum number of generations, beyond initialization, default 200
        :param threshold:           (opt.) if the fitness is beyond this threshold for an organism, stop evolution
        :param patience:            (opt.) the number of generations that need to pass w/o improvement for the
                                    algorithm to stop
        :param organism_to_string:  (opt.) function that should be used by the Organism object as its __str__() method,
                                    default None
        """
        self.genome = genome
        self.chromosome_len = chromosome_len
        self.generation_size = generation_size
        self.fitness_func = fitness_func
        self.num_generations = num_generations
        self.threshold = threshold
        self.patience = patience
        self.organism_to_string = organism_to_string

        self.current_generation_index = 0
        self.current_generation = []

    def fully_evolve_population(self):
        """
        Given the current generation, evolve the population until either the threshold is hit or the maximum number
        of generations is hit.
        :return:
        """
        self.initialize_generation()  # this is considered generation 0
        fittest_organism = self.current_generation[0]

        prev_fittest_organism = self.current_generation[0]
        patience_counter = 0

        if self.num_generations == 0:
            while True:
                self.current_generation_index += 1
                fittest_organism = self.advance_one_generation()
                print(f"fittest organism: {fittest_organism}")

                if fittest_organism == prev_fittest_organism:
                    patience_counter += 1
                else:
                    patience_counter = 0
                    prev_fittest_organism = fittest_organism

                if patience_counter >= self.patience != 0:
                    print(f"fitness has not improved in {self.patience} iterations, stopping early...")
                    return fittest_organism

                if fittest_organism.fitness >= self.threshold:
                    print(f"fitness >= threshold {self.threshold}, stopping...")
                    return fittest_organism

        for _ in range(self.num_generations):
            self.current_generation_index += 1
            fittest_organism = self.advance_one_generation()
            print(f"fittest organism: {fittest_organism}")

            if fittest_organism == prev_fittest_organism:
                patience_counter += 1
            else:
                patience_counter = 0
                prev_fittest_organism = fittest_organism

            if patience_counter >= self.patience != 0:
                print(f"fitness has not improved in {self.patience} iterations, stopping early...")
                break

            if fittest_organism.fitness >= self.threshold:
                print(f"fitness >= threshold {self.threshold}, stopping...")
                return fittest_organism

        return fittest_organism

    def advance_one_generation(self):
        """
        Advances the population by one generation using the roulette wheel method. Changes the state of this
        Population object. Assumes that the current generation is already sorted by fitness.
        :return:    the fittest Organism from this generation
        """
        new_generation = []
        rng = np.random.default_rng()

        total_fitness = sum([o.fitness for o in self.current_generation])
        probs = [o.fitness/total_fitness for o in self.current_generation]

        for _ in tqdm(range(self.generation_size), desc=f"Generation {self.current_generation_index}"):
            p1 = self.current_generation[rng.choice(self.generation_size, p=probs)]
            p2 = self.current_generation[rng.choice(self.generation_size, p=probs)]
            child = p1.reproduce(p2)
            new_generation.append(child)

        self.current_generation = sorted(new_generation, key = lambda o:o.fitness, reverse=True)  # sort the new generation by fitness
        return self.current_generation[0]

    def initialize_generation(self):
        """
        Updates self.current_generation if it's currently empty with self.generation_size number of organisms.
        """
        if self.current_generation:
            return

        for _ in range(self.generation_size):
            organism = self.create_random_organism()
            self.current_generation.append(organism)

        self.current_generation = sorted(self.current_generation, key = lambda o:o.fitness, reverse=True)

    def create_random_organism(self):
        """
        :return:    An Organism with a random set of chromosomes.
        """
        chromosomes = []
        rng = np.random.default_rng()

        for i in range(self.chromosome_len):
            chromosomes.append(rng.choice(self.genome))

        return Organism(chromosomes, self.fitness_func, self.genome, to_string=self.organism_to_string)

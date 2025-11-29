# file:         genetic_algorithm.py
# description:  contains the classes and structure for a generic GA

import numpy as np

from tqdm import tqdm


class Organism:
    """
    Represents a single organism as a part of the population. Meant to used with the roulette wheel method
    for selecting the next generation.
    """

    def __init__(self, chromosomes, fitness_func, to_string=None):
        """
        :param chromosomes:     a list of tokens that can be considered this organism's "gene sequence"
        :param fitness_func:    the function used to evaluate how "fit" this organism is
        """
        self.chromosomes = chromosomes
        self.fitness_func = fitness_func
        self.to_string = to_string

        self.fitness = self.fitness_func(self.chromosomes)

    def __str__(self):
        if self.to_string is None:
            return f"{''.join(self.chromosomes)}, fitness = {self.fitness}"
        return self.to_string(self)

    def __eq__(self, other):
        return self.chromosomes == other.chromosomes
    
    def to_json(self):
        return {
            "chromosomes": "".join(self.chromosomes),
            "fitness": self.fitness
        }


class Population:
    """
    Represents a group of individuals, on which to simulate evolution on. Uses the roulette wheel method for
    creating the next generation.
    """

    def __init__(
        self,
        chromosome_len,
        fitness_func,
        reproduce_func,
        generator_func,
        crossover=0.80,
        generation_size=500,
        num_generations=200,
        threshold=0.999,
        patience=0,
        organism_to_string=None,
    ):
        """
        :param chromosome_len:      the length of the target chromosome
        :param fitness_func:        the function used to evaluate how "fit" this organism is, the greater the fitness
                                    the better
        :param reproduce_func       the function used by all organisms to reproduce
        :param generator_func       the function used to create a new organism
        :param crossover            (opt.) the probability that crossover will occur, default 0.80
        :param generation_size:     (opt.) number of organisms per generation, default 500
        :param num_generations:     (opt.) the maximum number of generations, beyond initialization, default 200
        :param threshold:           (opt.) if the fitness is beyond this threshold for an organism, stop evolution,
                                    default .999 (in essence meaning that the algo will not stop based on threshold
                                    until near perfect)
        :param patience:            (opt.) the number of generations that need to pass w/o improvement for the
                                    algorithm to stop, default is sentinel value 0 corresponding to patience being
                                    turned off
        :param organism_to_string:  (opt.) function that should be used by the Organism object as its __str__() method,
                                    default None
        """
        self.chromosome_len = chromosome_len
        self.generation_size = generation_size
        self.fitness_func = fitness_func
        self.reproduce_func = reproduce_func
        self.generator_func = generator_func
        self.crossover = crossover
        self.num_generations = num_generations
        self.threshold = threshold
        self.patience = patience
        self.organism_to_string = organism_to_string

        self.current_generation_index = 0
        self.current_generation = []

    def fully_evolve_population(self, prog_bar=True):
        """
        Given the current generation, evolve the population until either the threshold is hit or the maximum number
        of generations is hit.
        :param prog_bar:    boolean for if progress bar should be shown per generation
        """
        self.initialize_generation()  # this is considered generation 0
        fittest_organism = self.current_generation[0]

        prev_fittest_organism = self.current_generation[0]
        print(f"fittest organism: {fittest_organism}")
        patience_counter = 0

        if self.num_generations == 0:
            while True:
                self.current_generation_index += 1
                fittest_organism = self.advance_one_generation(prog_bar=prog_bar)
                print(f"fittest organism: {fittest_organism}")

                if (fittest_organism.chromosomes == prev_fittest_organism.chromosomes):
                    patience_counter += 1
                else:
                    patience_counter = 0
                    prev_fittest_organism = fittest_organism

                if patience_counter >= self.patience != 0:
                    print(
                        f"fitness has not improved in {self.patience} iterations, stopping early..."
                    )
                    return fittest_organism

                if fittest_organism.fitness >= self.threshold:
                    print(f"fitness >= threshold {self.threshold}, stopping...")
                    return fittest_organism

        for _ in range(self.num_generations):
            self.current_generation_index += 1
            fittest_organism = self.advance_one_generation(prog_bar=prog_bar)
            print(f"fittest organism: {fittest_organism}")

            if (fittest_organism.chromosomes == prev_fittest_organism.chromosomes):
                patience_counter += 1
            else:
                patience_counter = 0
                prev_fittest_organism = fittest_organism

            if patience_counter >= self.patience != 0:
                print(
                    f"fitness has not improved in {self.patience} iterations, stopping early..."
                )
                break

            if fittest_organism.fitness >= self.threshold:
                print(f"fitness >= threshold {self.threshold}, stopping...")
                break

        return fittest_organism

    def fully_evolve_population_generator(self, prog_bar=False):
        """
        Given the current generation, evolve the population until either the threshold is hit or the maximum number
        of generations is hit. Yields the fittest organism of each generation and the fittest overall at the end.
        :param prog_bar:    boolean for if progress bar should be shown per generation
        """

        self.initialize_generation()  # this is considered generation 0
        fittest_organism = self.current_generation[0]
        yield fittest_organism, self.current_generation_index

        prev_fittest_organism = self.current_generation[0]
        patience_counter = 0

        if self.num_generations == 0:
            while True:
                self.current_generation_index += 1
                fittest_organism = self.advance_one_generation(prog_bar=prog_bar)
                print(f"fittest organism: {fittest_organism}")
                yield fittest_organism, self.current_generation_index

                if (fittest_organism.chromosomes == prev_fittest_organism.chromosomes):
                    patience_counter += 1
                else:
                    patience_counter = 0
                    prev_fittest_organism = fittest_organism

                if patience_counter >= self.patience != 0:
                    print(
                        f"fitness has not improved in {self.patience} iterations, stopping early..."
                    )
                    yield fittest_organism, self.current_generation_index

                if fittest_organism.fitness >= self.threshold:
                    print(f"fitness >= threshold {self.threshold}, stopping...")
                    yield fittest_organism, self.current_generation_index

        for _ in range(self.num_generations):
            self.current_generation_index += 1
            fittest_organism = self.advance_one_generation(prog_bar=prog_bar)
            print(f"fittest organism: {fittest_organism}")
            yield fittest_organism, self.current_generation_index

            if (fittest_organism.chromosomes == prev_fittest_organism.chromosomes):
                patience_counter += 1
            else:
                patience_counter = 0
                prev_fittest_organism = fittest_organism

            if patience_counter >= self.patience != 0:
                print(
                    f"fitness has not improved in {self.patience} iterations, stopping early..."
                )
                break

            if fittest_organism.fitness >= self.threshold:
                print(f"fitness >= threshold {self.threshold}, stopping...")
                break

        return

    def advance_one_generation(self, prog_bar=True):
        """
        Advances the population by one generation using the roulette wheel method. Changes the state of this
        Population object. Assumes that the current generation is already sorted by fitness.
        :param prog_bar:    boolean for if progress bar should be shown
        :return:            the fittest Organism from this generation
        """
        new_generation = []
        rng = np.random.default_rng()

        total_fitness = sum([o.fitness for o in self.current_generation])
        probs = [o.fitness / total_fitness for o in self.current_generation]

        if prog_bar:
            for _ in tqdm(
                range(self.generation_size),
                desc=f"Generation {self.current_generation_index}",
            ):
                p1 = self.current_generation[rng.choice(self.generation_size, p=probs)]
                p2 = self.current_generation[rng.choice(self.generation_size, p=probs)]
                child = self.reproduce_func(p1, p2)
                new_generation.append(child)
        else:
            for _ in range(self.generation_size):
                rng = np.random.default_rng()
                p = rng.random()
                p1 = self.current_generation[rng.choice(self.generation_size, p=probs)]

                if p > self.crossover:
                    new_generation.append(p1)
                    continue

                p2 = self.current_generation[rng.choice(self.generation_size, p=probs)]
                child = self.reproduce_func(p1, p2)
                new_generation.append(child)

        self.current_generation = sorted(
            new_generation, key=lambda o: o.fitness, reverse=True
        )  # sort the new generation by fitness
        return self.current_generation[0]

    def initialize_generation(self, prog_bar=True):
        """
        Updates self.current_generation if it's currently empty with self.generation_size number of organisms.
        :return:    None
        """
        if self.current_generation:
            return
        if prog_bar:
            for _ in tqdm(range(self.generation_size), desc="initializing generation"):
                organism = self.generator_func()
                self.current_generation.append(organism)

        else:
            for _ in range(self.generation_size):
                organism = self.generator_func()
                self.current_generation.append(organism)

        self.current_generation = sorted(
            self.current_generation, key=lambda o: o.fitness, reverse=True
        )

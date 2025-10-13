# file:         main.py
# description:  the main script file


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

    population = Population(
        genome,
        chromosome_len,
        fitness_func,
        threshold=0.999,
        generation_size=2000,
        num_generations=0,
        organism_to_string=to_string,
        patience=0,
    )
    fittest = population.fully_evolve_population()
    print(f"{fittest}")


def main():
    test_ga()


if __name__ == "__main__":
    main()

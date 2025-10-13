# file: main.py
# description: the main script file

def test_ga():
    import string
    from genetic_algorithm import Population

    target = list("Hello, Computational Geometry!")

    genome = list(string.ascii_letters) + list(string.digits) + list(string.punctuation) + [" "]
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

    population = Population(genome, chromosome_len, fitness_func, threshold=.999, generation_size=2000,
                            num_generations=0, organism_to_string=to_string, patience=0)
    fittest = population.fully_evolve_population()
    print(f"{fittest}")


def test_voronoi():
    import json
    from voronoi import bowyer_watson, voronoi_from_triangulation, Triangle
    import matplotlib.pyplot as plt
    triangulation = bowyer_watson([
        (2, 2), (4, 5), (6, 6), (3, 8), (9, 4), (5, 8)
    ])
    for t in triangulation:
        plt.plot([t.p1[0], t.p2[0]], [t.p1[1], t.p2[1]], c='b')
        plt.plot([t.p2[0], t.p3[0]], [t.p2[1], t.p3[1]], c='b')
        plt.plot([t.p1[0], t.p3[0]], [t.p1[1], t.p3[1]], c='b')
    obj = voronoi_from_triangulation(triangulation, 0, 0, 12, 12)
    edges = json.loads(obj)['edges']
    for e in edges:
        plt.plot([e['x1'], e['x2']], [e['y1'], e['y2']])
    plt.xlim(0, 12)
    plt.ylim(0, 12)
    plt.savefig('test.png')


def main():
    #test_ga()
    test_voronoi()


if __name__ == "__main__":
    main()

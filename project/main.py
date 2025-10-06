# file: main.py
# description: the main script file
from voronoi import *
import numpy as np

def main():
    #print("hello computational geometry!")
    random_arr = []
    for i in range(10):
        random_arr.append(
            (np.random.randint(low=1, high=100), 
             np.random.randint(low=1, high=100))
        )
    triangulation = bowyer_watson(random_arr)
    voronoi_from_triangulation(triangulation)


if __name__ == "__main__":
    main()

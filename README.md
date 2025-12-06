# Airspace Resectorization with Voronoi Diagrams
By Audrey Fuller (alf9310@rit.edu), Ricky Gupta (rg4825@rit.edu) and Lauren Kaestle (lk2958@rit.edu)

We aim to optimize airspace “sectors” by generating Voronoi diagrams whose seed points are evolved using a genetic algorithm. The goal is to reduce air-traffic controller workload by creating sector boundaries that better balance aircraft density, crossover frequency, and dwell time.

## Background Information
Airspace is divided into sectors that determine which air-traffic controller tracks each aircraft. Poorly designed sectors can overload controllers or produce excessive handoffs between sectors. Prior research proposes optimization-based approaches, but practical tools that allow interactive exploration of airspace designs—especially using real flight data—are limited.

## Algorithm Inputs and Outputs
### Inputs:
* Airport and radius (defining the geographic bounding box)
* Number of Voronoi cells
* Number of GA generations
* Real-time flight positions from an API

### Outputs:
* A Voronoi diagram representing proposed airspace sectors
* GA-optimized seed locations for the Voronoi cells
* A web-based interactive visualization (bounding box, polygons, and seed points)

## Problem Domain
Optimality matters because imbalanced sectors increase controller workload, jeopardizing safety and efficiency. However, perfect optimization is not required. A “good enough” solution that reduces worst-case workloads is sufficient because airspace constraints are noisy, dynamic, and dependent on real-time flight patterns.

## Existing Research
The main paper we referenced for the creation of this aplication was a NASA Paper on [Three Dimensional Sector Design with Optimal Number of Sectors](https://ntrs.nasa.gov/api/citations/20100039174/downloads/20100039174.pdf). This uses the same idea of optomizing the voronoi diagrams using a genetic algorithm with three different optomization functions:
* Average Sector Dwell Time
* Intersection Proximity
* Dominant Flow Proximity
For our own research, we use only average sector dwell time. 

One of the other websites we referenced was this [Spherical Voronoi Diagram Website](https://www.jasondavies.com/maps/voronoi/) by Jason Davies. This uses a very clean looking spherical vornoi map representation with the D3 library, which we referenced for our front-end framework. 

So while some FAA and academic projects explore automated resectorization, but they generally do not combine real-time data, GA optimization, and interactive visualizations in a single tool.

## Algorithm Description
1. Compute an initial Voronoi diagram centered on a selected airport and bounding box.
2. Encode Voronoi seed points as binary chromosomes using 32-bit normalized coordinates.
3. Evaluate fitness using average aircraft dwell time per sector.
4. Genetic algorithm loop: Selection,
* Crossover and mutation (bit-level)
* Regeneration of Voronoi diagrams from offspring
* Fitness reevaluation
* Return best-performing Voronoi seed configuration, sent to the frontend for rendering.
5. A KD-tree accelerates point-to-cell lookup during fitness evaluation, reducing traversal cost from linear to O(logn).

## Example Results

TODO

## Complexity Analysis 
Let n be the number of Voronoi cells (seed points) and m the number of aircraft.

### Voronoi generation:
2D Bowyer–Watson: O(nlog⁡n)
3D incremental convex hull: O(n^2) worst case

### Fitness evaluation:
KD-tree lookup per aircraft: O(log⁡n)
Total per generation: O(mlog⁡n)

### GA per generation:
Chromosome operations: O(n)
Full cost per generation: O(nlogn + mlogn)
  

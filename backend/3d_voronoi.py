# file: 3d_voronoi.py
# description: file of functions for creating spherical voronoi diagram

from dcel import *
import json
from scipy.spatial import KDTree 

class Cell:
    """
    Class representing a cell of the Voronoi diagram, which stores the seed
    point and set of edges that form the cell.
    """
    def __init__(self, seed):
        self.seed = seed # should be a vertex
        self.edges = set()

    def __eq__(self, other):
        if not isinstance(other, Cell):
            return False
        return self.seed == other.seed
    
    def __hash__(self):
        return hash(self.seed)

def build_initial_tetrahedron(points, dcel):
    """
    Uses the first four points to build the initial tetrahedron
    Arguments:
        points: the list of points to create the tetrahedron with
        dcel: the DCEL object to add to
    """
    vertices = []
    half_edges = []
    for p in points:
        v = dcel.create_vertex(p[0], p[1], p[2])
        vertices.append(v)
    dcel.find_inner_point(points)
    for i in range(len(vertices)):
        tmp = vertices[:i] + vertices[i+1:]
        f, he1, he2, he3 = dcel.create_face(tmp[0], tmp[1], tmp[2])
        half_edges.append(he1)
        half_edges.append(he2)
        half_edges.append(he3)
    dcel.find_twins(half_edges)


def convex_hull_3d(points):
    """
    Finds the 3d convex hull of a set of 3d coordinates, which is
    used to find Delaunay triangulation/Voronoi diagram, using the
    incremental algorithm
    Arguments:
        points: list of tuples representing (x, y, z) coordinates
    Returns:
        the DCEL that stores information about the triangulation
    """
    dcel = DCEL()
    # build tetrahedron from first four points
    build_initial_tetrahedron(points[:4], dcel)
    for p in points[4:]:
        # iterate t
        dcel.add_point(p[0], p[1], p[2])
    return dcel


def voronoi_3d(dcel, radius, center):
    """
    Iterates through the edges, connecting circumcenters of adjacent edges
    Arguments:
        dcel: the DCEL object containing faces of the Delaunay triangulation
        radius: the radius of the sphere
        center: a list representing the center point of the sphere
    Returns:
        JSON object representing the edges of the Voronoi diagram
    """
    center = Vertex(center[0], center[1], center[2])
    voronoi_edges = set()
    for face in dcel.faces:
        face.calc_circumcenter(radius, center)
    for face in dcel.faces:
        edges = face.get_edges()
        for edge in edges:
            c1 = face.circumcenter
            c2 = edge.twin.face.circumcenter
            if c1 is None or c2 is None:
                continue
            voronoi_edges.add(
                tuple(
                    sorted([c1, c2], key=lambda c: (c.x, c.y, c.z))
                )
            )
    edge_dicts = []
    for edge in voronoi_edges:
        edge_dicts.append(
            {
                "x1": edge[0].x,
                "y1": edge[0].y,
                "z1": edge[0].z,
                "x2": edge[1].x,
                "y2": edge[1].y,
                "z2": edge[1].z
            }
        )
    voronoi_obj = json.dumps({"edges": edge_dicts})
    return voronoi_obj


def _build_voronoi_tree(seeds, dcel, radius, center):
    """
    Alternative to voronoi_3d that uses the triangulation
    and bounding box to create a KD tree storing Voronoi edges for each
    seed point.

    Arguments:
        seeds: the seed points of the Voronoi diagram
        dcel: the DCEL representing the convex hull/Delaunay triangulation
        radius: the radius of the sphere these points are on
        center: the x, y, z coordinate representing the center of the sphere
    Returns:
        KD Tree of seed points
        dictionary of seed points and Voronoi edges
    """
    center = Vertex(center[0], center[1], center[2])
    voronoi_edges = {}
    for face in dcel.faces:
        face.calc_circumcenter(radius, center)
    for edge in dcel.half_edges:
        if edge.org not in voronoi_edges:
            voronoi_edges[edge.org] = Cell(edge.org)
    for face in dcel.faces:
        edges = face.get_edges()
        for edge in edges:
            c1 = face.circumcenter
            c2 = edge.twin.face.circumcenter
            if c1 is None or c2 is None:
                continue
            new_edge = tuple(
                    sorted([c1, c2], key=lambda c: (c.x, c.y, c.z))
                )
            voronoi_edges[edge.org].edges.add(
                new_edge
            )
            voronoi_edges[edge.twin.org].edges.add(
                new_edge
            )
    seed_tree = KDTree(seeds)
    return seed_tree, voronoi_edges


def find_closest_cell(voronoi_tree, points, point):
    """
    Uses the KD tree of Voronoi diagram information to look up the
    nearest Voronoi cell to the given point.

    Arguments:
        voronoi_tree: a KD tree of seed points
        points: the list of seed points
        point: a point somewhere on the map
    Returns:
        the seed of the Voronoi cell this point is in
    """
    _, index = voronoi_tree.query(point)
    return points[index]


def test_kd_tree(seeds, radius, center):
    hull_dcel = convex_hull_3d(seeds)
    tree, edges = _build_voronoi_tree(seeds, hull_dcel, radius, center)
    closest = find_closest_cell(tree, seeds, (0.0000,  0.0000, -1.0000))
    print(closest)

'''points = [
    (0.0000,  0.0000,  1.0000),
    (0.5257,  0.0000,  0.8507),
    (-0.5209, -0.3478,  0.7793),
    (0.4253, -0.6204,  0.6593),
    (0.7827,  0.4268,  0.4540),
    (-0.2656,  0.8649,  0.4253),
    (-0.8944, -0.0528,  0.4440),
    (-0.2318, -0.9110,  0.3416),
    (0.6235, -0.7190,  0.3061),
    (0.9441,  0.3265,  0.0451),
    (-0.0711,  0.9963,  0.0487),
    (-0.9487,  0.2833,  0.1413),
    (-0.4819, -0.8413, -0.2450),
    (0.4830, -0.7347, -0.4771),
    (0.8641,  0.4784, -0.1564),
    (-0.1145,  0.8668, -0.4853),
    (-0.7365, -0.2534, -0.6269),
    (0.2594, -0.4004, -0.8788),
    (-0.1681,  0.5009,  0.8492)
]
test_kd_tree(points, 1, (0, 0, 0))'''
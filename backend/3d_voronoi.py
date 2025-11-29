# file: 3d_voronoi.py
# description: file of functions for creating spherical voronoi diagram

from dcel import *
import json
from scipy.spatial import KDTree 
import numpy as np

class Cell:
    """
    Class representing a cell of the Voronoi diagram, which stores the seed
    point and set of edges that form the cell.
    """
    def __init__(self, seed):
        self.seed = seed # should be a vertex
        self.sort_point = None
        self.edges = set()

    def cell_to_geojson(self, center, radius, voronoi_dict):
        """
        Adds the seed point and bounding polygon for this region to the
        geoJSON-formatted dict provided.

        Args:
            center: center of the sphere these points are located on
            radius: radius of the sphere these points are located on
            voronoi_dict: geoJSON dict to add info about this Voronoi cell
        """
        sums = [0, 0, 0]
        points = set()
        for edge in self.edges:
            points.add(edge[0])
            points.add(edge[1])
        if len(points) == 0:
            return

        # convert seed and points into unit vectors
        seed_vector = (
            (self.seed.x - center[0]) / radius,
            (self.seed.y - center[1]) / radius,
            (self.seed.z - center[2]) / radius
        )

        point_dict = {}
        for point in points:
            point_vector = (
                (point.x - center[0]) / radius,
                (point.y - center[1]) / radius,
                (point.z - center[2]) / radius
            )
            # map point vector to original point
            point_dict[point_vector] = point

        # pick random vector (not parallel to seed), estimate w/ cross product
        if np.linalg.norm(np.cross(seed_vector, [1, 0, 0])) <= 1e-10:
            tmp_vector = [0, 1, 0]
        else:
            tmp_vector = [1, 0, 0]

        v1 = np.cross(tmp_vector, seed_vector)
        v1 /= np.linalg.norm(v1)
        v2 = np.cross(center, v1)

        angle_dict = {}
        for point in point_dict.keys():
            # get angles to compare
            to_project = np.dot(point, seed_vector) * np.array(seed_vector, dtype=float)
            new_vals = (
                point[0] - to_project,
                point[1] - to_project,
                point[2] - to_project
            )
            new_vals /= np.linalg.norm(new_vals)
            angle = tuple(np.arctan2(
                np.dot(new_vals, v2),
                np.dot(new_vals, v1)
            ))
            # map angle to point vector
            angle_dict[angle] = point
        
        sorted_angles = sorted(angle_dict.keys())

        sorted_points = []
        for angle in sorted_angles:
            point = point_dict.get(angle_dict[angle])
            if point:
                sorted_points.append(point)

        coord_list = []
        for point in sorted_points:
            coord_list.append([point.x, point.y, point.z])
        coord_list.append(
            [sorted_points[0].x, sorted_points[0].y, sorted_points[0].z]
        )

        voronoi_dict["polygons"].append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon", 
                    "coordinates": coord_list,
                },
                "properties": {},
            }
        )
        voronoi_dict["seeds"].append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [self.seed.x, self.seed.y, self.seed.z],
                },
                "properties": {"is_seed": True},
            }
        )
        

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
    tree, cells = _build_voronoi_tree(seeds, hull_dcel, radius, center)
    '''for seed, cell in cells.items():
        pass
    closest = find_closest_cell(tree, seeds, (0.0000,  0.0000, -1.0000))
    print(closest)'''
    geojson_dict = {"type": "FeatureCollection", "polygons": [], "seeds": []}
    for cell in cells.values():
        cell.cell_to_geojson(center, radius, geojson_dict)
    voronoi_geojson = json.dumps(geojson_dict)
    print(voronoi_geojson)


points = [
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
test_kd_tree(points, 1, (0, 0, 0))
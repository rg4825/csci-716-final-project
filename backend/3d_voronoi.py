# file: 3d_voronoi.py
# description: file of functions for creating spherical voronoi diagram

from dcel import *


def build_initial_tetrahedron(points, dcel):
    """
    Uses the first four points to build the initial tetrahedron
    """
    vertices = []
    half_edges = []
    for p in points:
        v = dcel.create_vertex(p[0], p[1], p[2])
        vertices.append(v)
    # dcel.find_inner_point()
    dcel.find_inner_point(points)
    for i in range(len(vertices)):
        tmp = vertices[:i] + vertices[i + 1 :]
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
    hull = build_initial_tetrahedron(points[:4], dcel)
    for p in points[4:]:
        dcel.add_point(p[0], p[1], p[2])
    return dcel


def voronoi_3d(triangulation):
    """
    Iterates through the edges, connecting circumcenters of adjacent edges
    """
    # triangulation will be the DCEL representing the triangulation
    pass

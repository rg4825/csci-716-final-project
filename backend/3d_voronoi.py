# file: 3d_voronoi.py
# description: file of functions for creating spherical voronoi diagram

from dcel import *
import json

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
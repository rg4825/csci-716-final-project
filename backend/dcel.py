# file: 3d_voronoi.py
# description: Doubly-connected edge list implementation for removing hull edges

import math

class Vertex:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        return (abs(self.x - other.x) < math.pow(10, -10)
                and abs(self.y - other.y) < math.pow(10, -10)
                and abs(self.z - other.z) < math.pow(10, -10))

    def __hash__(self):
        return hash((round(self.x, 10), round(self.y, 10), round(self.z, 10)))

    def __repr__(self):
        return f"Vertex({self.x}, {self.y}, {self.z})"


class HalfEdge:
    """
    Class representing a directed edge (1/2 of an undirected edge)
    """
    def __init__(self, v1):
        self.org = v1 # access dst vertex as twin.org
        self.twin = None
        self.face = None # access other face as twin.face
        self.next = None
        self.prev = None

    def __eq__(self, other):
        return (self.org == other.org
                and self.next.org == other.next.org)

    def __hash__(self):
        return hash((self.org, self.next.org))

    def __repr__(self):
      return f"HalfEdge({self.org}, {self.next.org})"
        

class Face:
    def __init__(self, edge):
        self.inc_edge = edge

    def calc_circumcenter(self):
        """
        Calculates the circumcenter of a triangular face
        """
        pass

    def get_edges(self):
        edges = set()
        edges.add(self.inc_edge)
        he = self.inc_edge.next
        while he not in edges:
            edges.add(he)
            he = he.next
        return edges

    def is_visible(self, point):
        a = self.inc_edge.org
        b = self.inc_edge.next.org
        c = self.inc_edge.next.next.org
        m = [
            [a.x, a.y, a.z, 1],
            [b.x, b.y, b.z, 1],
            [c.x, c.y, c.z, 1],
            [point.x, point.y, point.z, 1]
        ]
        det = self.calc_determinant(m)
        if det > 0: # point behind face, face not visible
            return False
        else: # point in front of face, face visible
            return True

    def calc_determinant(self, m):
        if len(m) == 2:
            return (m[0][0] * m[1][1]) - (m[0][1] * m[1][0])
        elif len(m) == 3:
            m1 = [[m[1][1], m[1][2]], [m[2][1], m[2][2]]]
            m2 = [[m[1][0], m[1][2]], [m[2][0], m[2][2]]]
            m3 = [[m[1][0], m[1][1]], [m[2][0], m[2][1]]]
            return (
                (m[0][0] * self.calc_determinant(m1))
                - (m[0][1] * self.calc_determinant(m2))
                + (m[0][2] * self.calc_determinant(m3))
            )
        elif len(m) == 4:
            m1 = [
                [m[1][1], m[1][2], m[1][3]],
                [m[2][1], m[2][2], m[2][3]],
                [m[3][1], m[3][2], m[3][3]]
            ]
            m2 = [
                [m[1][0], m[1][2], m[1][3]],
                [m[2][0], m[2][2], m[2][3]],
                [m[3][0], m[3][2], m[3][3]]
            ]
            m3 = [
                [m[1][0], m[1][1], m[1][3]],
                [m[2][0], m[2][1], m[2][3]],
                [m[3][0], m[3][1], m[3][3]]
            ]
            m4 = [
                [m[1][0], m[1][1], m[1][2]],
                [m[2][0], m[2][1], m[2][2]],
                [m[3][0], m[3][1], m[3][2]]
            ]
            return (
                (m[0][0] * self.calc_determinant(m1))
                - (m[0][1] * self.calc_determinant(m2))
                + (m[0][2] * self.calc_determinant(m3))
                - (m[0][3] * self.calc_determinant(m4))
            )


class DCEL:
    def __init__(self):
        self.vertices = set()
        self.half_edges = set()
        self.faces = set()
        self.inner_point = None

    def create_vertex(self, x, y, z):
        v = Vertex(x, y, z)
        self.vertices.add(v)
        return v

    def find_inner_point(self, points):
      x_sum = 0
      y_sum = 0
      z_sum = 0
      for p in points:
        x_sum += p[0]
        y_sum += p[1]
        z_sum += p[2]
      length = float(len(points))
      self.inner_point = Vertex(
          x_sum / length, y_sum / length, z_sum / length
      )

    def is_ccw(self, a, b, c):
        """
        Given three vertices a, b, and c of a face, determine
        if they are clockwise or counterclockwise, as determined
        by the right hand rule pointing outside of the hull.
        """
        ab = [b.x - a.x, b.y - a.y, b.z - a.z]
        ac = [c.x - a.x, c.y - a.y, c.z - a.z]
        # find the normal vector with cross product
        cross_prod = [
            (ab[1] * ac[2]) - (ab[2] * ac[1]),
            (ab[2] * ac[0]) - (ab[0] * ac[2]),
            (ab[0] * ac[1]) - (ab[1] * ac[0])
        ]
        ap = [
            self.inner_point.x - a.x,
            self.inner_point.y - a.y,
            self.inner_point.z - a.z
        ]
        dot_prod = (
            (cross_prod[0] * ap[0])
            + (cross_prod[1] * ap[1])
            + (cross_prod[2] * ap[2])
        )
        if dot_prod < 0:
            # normal vector points away from inner point
            return True
        else:
            # normal vector points towards inner point
            return False

    def create_face(self, v1, v2, v3):
        # order v1, v2, v3 so that they are CCW
        if self.inner_point:
            if not self.is_ccw(v1, v2, v3):
                tmp = v2
                v2 = v3
                v3 = tmp
        # create half edges
        he1 = HalfEdge(v1)
        he2 = HalfEdge(v2)
        he3 = HalfEdge(v3)
        # link half edges to other ones in same triangle
        he1.prev = he3
        he1.next = he2
        he2.prev = he1
        he2.next = he3
        he3.prev = he2
        he3.next = he1
        # create face, set face for each of these half edges to face
        f = Face(he1)
        he1.face = f
        he2.face = f
        he3.face = f
        # add half edges and face to DCEL
        self.half_edges.add(he1)
        self.half_edges.add(he2)
        self.half_edges.add(he3)
        self.faces.add(f)
        return f, he1, he2, he3

    def find_twins(self, new_half_edges):
        for he1 in self.half_edges:
            for he2 in new_half_edges:
                if (
                    (he1.org == he2.next.org) and
                    (he2.org == he1.next.org)
                ):
                    he1.twin = he2
                    he2.twin = he1
                    break

    def add_point(self, x, y, z):
        v = self.create_vertex(x, y, z)
        visible_faces = set()
        for face in self.faces:
            if face.is_visible(v):
                visible_faces.add(face)
        if len(visible_faces) == 0:
            self.vertices.discard(v)
        else:
            border = set()
            half_edges = []
            for face in visible_faces:
                # find which edges form the border
                edges = face.get_edges()
                for he in edges:
                    if he.twin and he.twin.face not in visible_faces:
                        border.add(he)
            for face in visible_faces:
                # remove unnecessary faces and edges
                edges = face.get_edges()
                for he in edges:
                    if he not in border:
                        if he.twin:
                            he.twin = None
                        self.half_edges.discard(he)
                self.faces.discard(face)
            for he in border:
                # replace border edges
                v1 = he.org
                v2 = he.twin.org
                he.twin = None
                self.half_edges.discard(he)
                f, he1, he2, he3 = self.create_face(v1, v2, v)
                half_edges.append(he1)
                half_edges.append(he2)
                half_edges.append(he3)
            self.find_twins(half_edges)
# file: 3d_voronoi.py
# description: Doubly-connected edge list implementation for removing hull edges

import math

class Vertex:
    """
    Class representing DCEL vertices, which store (x, y, z) coordinates
    """
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
        self.circumcenter = None

    def calc_circumcenter(self, radius, center):
        """
        Calculates the circumcenter of a triangular face
        Args:
            radius: radius of the sphere the points fall on
            center: the center of the sphere
        """
        edges = self.get_edges()
        a = edges[0].org
        b = edges[1].org
        c = edges[2].org
        ab = Vertex(b.x - a.x, b.y - a.y, b.z - a.z)
        len_ab_sq = (ab.x * ab.x) + (ab.y * ab.y) + (ab.z * ab.z)
        ac = Vertex(c.x - a.x, c.y - a.y, c.z - a.z)
        len_ac_sq = (ac.x * ac.x) + (ac.y * ac.y) + (ac.z * ac.z)
        # cross product of the vectors ab and ac
        cross_prod1 = Vertex(
            (ab.y * ac.z) - (ab.z * ac.y),
            (ab.z * ac.x) - (ab.x * ac.z),
            (ab.x * ac.y) - (ab.y * ac.x)
        )
        len_cross_prod1_sq = (
            (cross_prod1.x * cross_prod1.x)
            + (cross_prod1.y * cross_prod1.y)
            + (cross_prod1.z * cross_prod1.z)
        )
        if len_cross_prod1_sq == 0:
            # division by 0
            return
        # cross product of cross_product1 and ab
        cross_prod2 = Vertex(
            (cross_prod1.y * ab.z) - (cross_prod1.z * ab.y),
            (cross_prod1.z * ab.x) - (cross_prod1.x * ab.z),
            (cross_prod1.x * ab.y) - (cross_prod1.y * ab.x)
        )
        # cross product of cross_product1 and ac
        cross_prod3 = Vertex(
            (ac.y * cross_prod1.z) - (ac.z * cross_prod1.y),
            (ac.z * cross_prod1.x) - (ac.x * cross_prod1.z),
            (ac.x * cross_prod1.y) - (ac.y * cross_prod1.x)
        )
        # circumcenter represented as a vertex
        cc = Vertex(
            a.x + (((len_ac_sq * cross_prod2.x) + (len_ab_sq * cross_prod3.x))
                    / (2 * len_cross_prod1_sq)),
            a.y + (((len_ac_sq * cross_prod2.y) + (len_ab_sq * cross_prod3.y))
                    / (2 * len_cross_prod1_sq)),
            a.z + (((len_ac_sq * cross_prod2.z) + (len_ab_sq * cross_prod3.z))
                    / (2 * len_cross_prod1_sq))
        )
        # vector from center to circumcenter as a vertex
        center_to_cc = Vertex(
            cc.x - center.x,
            cc.y - center.y,
            cc.z - center.z
        )
        len_center_to_cc = math.sqrt(
            (center_to_cc.x * center_to_cc.x)
            + (center_to_cc.y * center_to_cc.y)
            + (center_to_cc.z * center_to_cc.z)
        )
        # unit vector from center toward circumcenter times radius and adjusted based on center
        self.circumcenter = Vertex(
            ((center_to_cc.x / len_center_to_cc) * radius) + center.x,
            ((center_to_cc.y / len_center_to_cc) * radius) + center.y,
            ((center_to_cc.z / len_center_to_cc) * radius) + center.z
        )

    def get_edges(self):
        """
        Iterates through the edges of the face, starting at the
        inc_edge, to find all edges
        Returns:
            a list of the face's edges
        """
        edges = [self.inc_edge]
        he = self.inc_edge.next
        while he != self.inc_edge:
            edges.append(he)
            he = he.next
        return edges

    def is_visible(self, point):
        """
        Determines if this face is visible from a given point
        Args:
            point: the point to check visibility for
        Returns:
            True if the face is visible from the point,
            False otherwise
        """
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
        """
        Recursively calculates the determinant of the given nxn matrix
        (where n=2, 3, or 4)
        Args:
            m: the matrix to find the determinant of
        Returns:
            the determinant of the matrix
        """
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
        return None  # should never get here


class DCEL:
    """
    Class representing the doubly-connected edge list
    """
    def __init__(self):
        self.vertices = set()
        self.half_edges = set()
        self.edge_dict = {} # to help match up neighbors more efficiently
        self.faces = set()
        self.inner_point = None

    def create_vertex(self, x, y, z):
        """
        Creates a vertex from the given x, y, and z values and
        adds it to the DCEL vertex set
        Args:
            x: the x-coordinate of the new vertex
            y: the y-coordinate of the new vertex
            z: the z-coordinate of the new vertex
        Returns:
            the new vertex that was created
        """
        v = Vertex(x, y, z)
        self.vertices.add(v)
        return v

    def find_inner_point(self, points):
        """
        Finds a point within the convex hull for properly orienting edges
        Args:
            points: the list of points used to form the hull
        """
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
        Args:
            a: the first vertex
            b: the second vertex
            c: the third vertex
        Returns:
            True if the points are counterclockwise, False otherwise
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
        """
        Creates half-edges and faces from the given vertices,
        adding them to the DCEL half-edge and face sets
        Args:
            v1: the first vertex of the face
            v2: the second vertex of the face
            v3: the third vertex of the face
        """
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
        # add twin relationships if they exist:
        twin1 = self.edge_dict.get((he1.next.org, he1.org))
        if twin1:
            he1.twin = twin1
            twin1.twin = he1
            self.edge_dict.pop((he1.next.org, he1.org))
        else:
            self.edge_dict[(he1.org, he1.next.org)] = he1
        twin2 = self.edge_dict.get((he2.next.org, he2.org))
        if twin2:
            he2.twin = twin2
            twin2.twin = he2
            self.edge_dict.pop((he2.next.org, he2.org))
        else:
            self.edge_dict[(he2.org, he2.next.org)] = he2
        twin3 = self.edge_dict.get((he3.next.org, he3.org))
        if twin3:
            he3.twin = twin3
            twin3.twin = he3
            self.edge_dict.pop((he3.next.org, he3.org))
        else:
            self.edge_dict[(he3.org, he3.next.org)] = he3


    def add_point(self, x, y, z):
        """
        If a point isn't already within the existing hull, add the
        edges/faces needed to add it to the hull and remove any faces
        that are no longer visible
        Args:
            x: the x-coordinate of the point to add
            y: the y-coordinate of the point to add
            z: the z-coordinate of the point to add
        """
        v = self.create_vertex(x, y, z)
        visible_faces = set()
        for face in self.faces:
            if face.is_visible(v):
                visible_faces.add(face)
        if len(visible_faces) == 0:
            self.vertices.discard(v)
        else:
            border = set()
            for face in visible_faces:
                # find which edges form the border
                edges = face.get_edges()
                for he in edges:
                    if he.twin and he.twin.face not in visible_faces:
                        border.add(he)
            visible_face_list = list(visible_faces)
            #for face in visible_faces:
            while len(visible_face_list) > 0:
                # remove unnecessary faces and edges
                face = visible_face_list[0]
                edges = face.get_edges()
                #for he in edges:
                while len(edges) > 0:
                    he = edges[0]
                    if he in border:
                        v1 = he.org
                        v2 = he.twin.org
                        self.edge_dict[(v2, v1)] = he.twin
                        self.create_face(v1, v2, v)
                    edges.remove(he)
                    self.half_edges.discard(he)
                visible_face_list.remove(face)
                self.faces.discard(face)
# file: 3d_voronoi.py
# description: Doubly-connected edge list implementation for removing hull edges
# based on https://www.cs.umd.edu/class/spring2020/cmsc754/Lects/lect10-dcel.pdf

class Vertex:
    def __init__(self, x, y, z):
        # coordinates
        self.p = (x, y, z)


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
        

class Face:
    def __init__(self, edge):
        self.inc_edge = edge


class DCEL:
    def __init__(self):
        self.vertices = []
        self.half_edges = []
        self.faces = []

    def create_vertex(self, x, y, z):
        v = Vertex(x, y, z)
        self.vertices.append(v)
        return v
    
    def create_face(self, v1, v2, v3):

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
        self.half_edges.append(he1)
        self.half_edges.append(he2)
        self.half_edges.append(he3)
        self.faces.append(f)
        return f, he1, he2, he3
    

    def set_twin(self, he1, he2):
        he1.twin = he2
        he2.twin = he1
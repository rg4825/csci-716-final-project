"""
File:   voronoi.py
Description:    implementation of the Bowyer-Watson algorithm to create a
                Delaunay triangulation and use the circumcenters to find
                edges of the Voronoi diagram
"""

import math

class Edge:
    def __init__(self, p1, p2):
        if p1[0] < p2[0] or (p1[0] == p2[0] and p1[1] <= p2[1]):
            self.p1 = p1
            self.p2 = p2
        else:
            self.p1 = p2
            self.p2 = p1
        self.midpoint = ((self.p1[0] + self.p2[0]) / 2.0,
                         (self.p1[1] + self.p2[1]) / 2.0)
        if self.p1[0] - self.p2[0] == 0:
            self.slope = None
        else:
            self.slope = (self.p1[1] - self.p2[1]) / (self.p1[0] - self.p2[0])
        if self.slope is None:
            self.perp_slope = 0
        elif self.slope == 0:
            self.perp_slope = None
        else:
            self.perp_slope = -1.0 / self.slope
    
    def __eq__(self, other_edge):
        if not isinstance(other_edge, Edge):
            return False
        return self.p1 == other_edge.p1 and self.p2 == other_edge.p2
    
    def __hash__(self):
        return hash((self.p1, self.p2))


class Triangle:
    def __init__(self, p1, p2, p3):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.edges = [Edge(self.p1, self.p2),
                      Edge(self.p1, self.p3),
                      Edge(self.p2, self.p3)]
        self.circumcenter = None

    def __eq__(self, other_triangle):
        if not isinstance(other_triangle, Triangle):
            return False
        for edge in self.edges:
            if edge not in other_triangle.edges:
                return False
        return True
    
    def __hash__(self):
        return hash((self.p1, self.p2, self.p3))

    def find_circumcenter(self):
        """
        Find the circumcenter of the triangle, which are used to find the
        circumcircle for Delaunay triangulation and are the vertices of the
        Voronoi diagram
        Returns:
            the circumcenter of this triangle
        """
        #find midpoints of two lines:
        if self.circumcenter != None:
            return self.circumcenter
        midpoint1 = self.edges[0].midpoint
        midpoint2 = self.edges[1].midpoint
        #find slopes of same two lines and perpendicular lines
        perp_slope1 = self.edges[0].perp_slope
        perp_slope2 = self.edges[1].perp_slope
        #calculate x, y where the perpendicular bisectors intersect:
        if perp_slope1 is None:
            x = midpoint1[0]
            b = midpoint2[1] - (perp_slope2 * midpoint2[0])
            y = (perp_slope2 * x) + b
        elif perp_slope2 is None:
            x = midpoint2[0]
            b = midpoint1[1] - (perp_slope1 * midpoint1[0])
            y = (perp_slope1 * x) + b
        elif perp_slope1 == 0:
            y = midpoint1[1]
            b = midpoint2[1] - (midpoint2[0] * perp_slope2)
            x = (y - b) / perp_slope2
        elif perp_slope2 == 0:
            y = midpoint2[1]
            b = midpoint1[1] - (midpoint1[0] * perp_slope1)
            x = (y - b) / perp_slope1
        else:
            if perp_slope1 - perp_slope2 == 0:
                #TODO: figure out how to handle this error
                print("Error: perpendicular bisectors are parallel, can't find circumcenter")
                exit(1)
            x = ((perp_slope1 * midpoint1[0]) - midpoint1[1] - (perp_slope2 * midpoint2[0]) + midpoint2[1]) / (perp_slope1 - perp_slope2)
            y = (perp_slope1 * (x - midpoint1[0])) + midpoint1[1]
        self.circumcenter = (x, y)
        return self.circumcenter
        
    def find_circumcircle(self):
        """
        Find the circumcircle of the triangle, which is used to determine
        which triangles belong in a Delaunay triangulation
        Returns:
            the circumcircle of this triangle
        """
        center = self.find_circumcenter()
        dist = math.sqrt(
            math.pow(center[0] - self.p1[0], 2) + 
            math.pow(center[1] - self.p1[1], 2)
        )
        return Circle(center, dist)


class Circle:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
    

def find_supertriangle(points):
    """
    Finds a supertriangle that surrounds the set of points provided
    Arguments:
        points: list of tuples representing x, y coordinates
    Returns:
        a triangle object representing the supertriangle
    """
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    mid_x = (min_x + max_x) / 2.0
    mid_y = (min_y + max_y) / 2.0
    dx = max_x - min_x
    dy = max_y - min_y
    d = max(dx, dy) * 5.0 #added scaling factor to make large enough triangle
    return Triangle(
        (mid_x - d, mid_y - d),
        (mid_x, mid_y + d),
        (mid_x + d, mid_y - d)
    )


def bowyer_watson(points):
    """
    Finds the Delaunay triangulation for a given set of points using the
    Bowyer-Watson algorithm
    Arguments:
        points: a list of tuples representing x, y coordinates
    Returns:
        triangulation: a list of triangles that form the 
                       Delaunay triangulation
    """
    supertriangle = find_supertriangle(points)
    triangulation = [supertriangle]
    for point in points:
        bad_triangles = []
        for triangle in triangulation:
            circumcircle = triangle.find_circumcircle()
            center = circumcircle.center
            dist = math.sqrt(
                math.pow(center[0] - point[0], 2) + 
                math.pow(center[1] - point[1], 2)
            )
            if dist < circumcircle.radius: # <= ?
                bad_triangles.append(triangle)
        
        polygon = []
        to_remove = []
        for triangle in bad_triangles:
            for edge in triangle.edges:
                if edge in polygon:
                    to_remove.append(edge)
                else:
                    polygon.append(edge)
        
        for edge in to_remove:
            if edge in polygon:
                polygon.remove(edge)

        for triangle in bad_triangles:
            triangulation.remove(triangle)
        for edge in polygon:
            triangulation.append(Triangle(point, edge.p1, edge.p2))

    triangulation = [
        t for t in triangulation 
        if t.p1 not in [supertriangle.p1, supertriangle.p2, supertriangle.p3]
        and t.p2 not in [supertriangle.p1, supertriangle.p2, supertriangle.p3]
        and t.p3 not in [supertriangle.p1, supertriangle.p2, supertriangle.p3]
    ]
    
    return triangulation


def voronoi_from_triangulation(triangulation, min_x, min_y, max_x, max_y):
    """
    Given the Delaunay triangulation of a set of points,
    Arguments:
        triangulation: a list of triangles that form the 
                       Delaunay triangulation
        min_x: minimum x coordinate the "infinite edges" can extend out to
        min_y: minimum y coordinate the "infinite edges" can extend out to
        max_x: maximum x coordinate the "infinite edges" can extend out to
        max_y: maximum y coordinate the "infinite edges" can extend out to
    Returns:
        JSON object representing a Voronoi diagram
    """

    pass
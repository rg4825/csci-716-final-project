# file: voronoi.py
# description: testing implementation of creating Voronoi diagrams

import math
import matplotlib.pyplot as plt # for testing

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
    # circumcenter is a site of the Voronoi diagram
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
                #find better way to handle this error?
                #might also need to handle collinear points...?
                print("Error: perpendicular bisectors are parallel, can't find circumcenter")
                exit(1)
            x = ((perp_slope1 * midpoint1[0]) - midpoint1[1] - (perp_slope2 * midpoint2[0]) + midpoint2[1]) / (perp_slope1 - perp_slope2)
            y = (perp_slope1 * (x - midpoint1[0])) + midpoint1[1]
        self.circumcenter = (x, y)
        return self.circumcenter
        
    def find_circumcircle(self):
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


def voronoi_from_triangulation(triangulation):
    pass
    #for triangle in triangulation
        #for edge in triangle
            #if edge in another triangle
                #create an edge from circumcenters of the triangles
            #else
                #edge extends toward infinity in the direction perpendicular from the edge
    #make edge class that can also hold slope to handle extending out to infinity??
    #could also add custom comparator
    figure, axes = plt.subplots()
    plt.title('Delaunay Triangles & Voronoi Diagram')
    circumcenters_x = []
    circumcenters_y = []
    for t in triangulation:
        plt.plot([t.p1[0], t.p2[0]], [t.p1[1], t.p2[1]], c='b')
        plt.plot([t.p1[0], t.p3[0]], [t.p1[1], t.p3[1]], c='b')
        plt.plot([t.p2[0], t.p3[0]], [t.p2[1], t.p3[1]], c='b')
        '''circumcircle = t.find_circumcircle()
        circumcenters_x.append(circumcircle.center[0])
        circumcenters_y.append(circumcircle.center[1])
        axes.add_artist(
            plt.Circle((circumcircle.center[0], circumcircle.center[1]), 
                       circumcircle.radius, 
                       fill=False)
        )'''
        circumcenters_x.append(t.find_circumcenter()[0])
        circumcenters_y.append(t.find_circumcenter()[1])
    plt.scatter(circumcenters_x, circumcenters_y, c='r')

    current_xlim = plt.xlim()
    current_ylim = plt.ylim()

    for t1 in triangulation:
        c1 = t1.find_circumcenter()
        for edge in t1.edges:
            edge_found = False
            for t2 in triangulation:
                if t1 == t2:
                    continue
                if edge in t2.edges:
                    c2 = t2.find_circumcenter()
                    plt.plot([c1[0], c2[0]], 
                             [c1[1], c2[1]], 
                             c='r', ls='--')
                    edge_found = True
                    
            if not edge_found:
                #TODO: 
                perp_slope = edge.perp_slope
                midpt = edge.midpoint
                #find direction to edge from midpt, steps:
                #treat find unit vector to find direction?
                #find distance from midpt to c1
                #extend to boundary using line formula

    plt.xlim((0, current_xlim[1]))
    plt.ylim((0, current_ylim[1]))

    plt.savefig('test.png')
    #plt.show()
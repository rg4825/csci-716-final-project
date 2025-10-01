# file: voronoi.py
# description: testing implementation of creating Voronoi diagrams

import sys
import math
#import matplotlib.pyplot as plt

class Triangle:
    # circumcenter is a site of the Voronoi diagram
    def __init__(self, p1, p2, p3):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.circumcenter = None

    def __eq__(self, other):
        assert isinstance(other, Triangle)

    def get_edges(self):
        edges = [sorted((self.p1, self.p2), key=lambda e: (e[0], e[1])), 
                sorted((self.p2, self.p3), key=lambda e: (e[0], e[1])), 
                sorted((self.p1, self.p3), key=lambda e: (e[0], e[1]))]
        return edges

    def find_circumcenter(self):
        #find midpoints of two lines:
        if self.circumcenter != None:
            return self.circumcenter
        midpoint1 = ((self.p1[0] + self.p2[0]) / 2.0,
                     (self.p1[1] + self.p2[1]) / 2.0)
        midpoint2 = ((self.p1[0] + self.p3[0]) / 2.0,
                     (self.p1[1] + self.p3[1]) / 2.0)
        #find slopes of same two lines
        if self.p1[0] - self.p2[0] == 0:
            slope1 = 'undefined'
        else:
            slope1 = (self.p1[1] - self.p2[1]) / (self.p1[0] - self.p2[0])
        if self.p1[0] - self.p3[0] == 0:
            slope2 = 'undefined'
        else:
            slope2 = (self.p1[1] - self.p3[1]) / (self.p1[0] - self.p3[0])
        #find slope of perpendicular lines:
        if slope1 == 'undefined':
            perp_slope1 = 0
        elif slope1 == 0:
            perp_slope1 = 'undefined'
        else:
            perp_slope1 = -1.0 / slope1
        if slope2 == 'undefined':
            perp_slope2 = 0
        elif slope2 == 0:
            perp_slope2 = 'undefined'
        else:
            perp_slope2 = -1.0 / slope2
        #calculate x, y where the perpendicular bisectors intersect:
        if perp_slope1 == 'undefined':
            x = midpoint1[0]
            b = midpoint2[1] - (perp_slope2 * midpoint2[0])
            y = (perp_slope2 * x) + b
        elif perp_slope2 == 'undefined':
            x = midpoint2[0]
            b = midpoint1[1] - (perp_slope1 * midpoint1[0])
            y = (perp_slope1 * x) + b
        else:
            #TODO: need to double-check my work on this one...
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
    #check if this needs to be edited at all
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    diff_x = max_x - min_x
    diff_y = max_y - min_y
    #TODO: edit supertriangle creation to NOT TOUCH ANY OF THE POLYGON'S SIDES
    '''return Triangle(
        (min_x - diff_x * 0.1, max_y - diff_y), 
        (min_x - diff_x * 0.1, max_y + diff_y * 2), 
        (min_x + diff_x * 1.7, max_y + diff_y * 0.5)
    )'''
    return Triangle((-5, -5), (6, -5), (1, 10)) #hard-coded in for testing


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
            for edge in triangle.get_edges():
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
            triangulation.append(Triangle(point, edge[0], edge[1]))

    triangulation = [
        t for t in triangulation 
        if t.p1 not in [supertriangle.p1, supertriangle.p2, supertriangle.p3]
        and t.p2 not in [supertriangle.p1, supertriangle.p2, supertriangle.p3]
        and t.p3 not in [supertriangle.p1, supertriangle.p2, supertriangle.p3]
    ]
    
    return triangulation


def voronoi_from_triangulation(triangulation):
    #for triangle in triangulation
        #for edge in triangle
            #if edge in another triangle
                #create an edge from circumcenters of the triangles
            #else
                #edge extends toward infinity in the direction perpendicular from the edge
    #make edge class that can also hold slope to handle extending out to infinity??
    #could also add custom comparator
    for t in triangulation:
        print(f'({t.p1}, {t.p2}, {t.p3})')
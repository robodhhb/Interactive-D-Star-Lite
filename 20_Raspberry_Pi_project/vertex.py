#!/usr/bin/python3
############################################################
# Class Vertex
# The class Vertex represents a single vertex in the path-
# planning algorithm D*Lite. A vertex is a field in the
# matrix of the area where the robot drives.
#
# File: vertex.py
# Author: Detlef Heinze 
# Version: 1.0    Date: 22.07.2020       
###########################################################

import math as math

class Vertex(object):

    def __init__(self,x=0, y=0):
        self.x=x    #x-ccordinate in the vertexGrid (not canvas)
        self.y=y    #y-coordinate in the vertexGrid (not canvas)
        self.g= float('inf')     #Estimated cost to goal
        self.rsh= float('inf')   #Sum of costs to goal so far
                                 #if g !=rsh then vertex is inconsistent
        self.isGoal= False
        self.isObstacle= False
        self.key=0 
    
    #If vertex is a goal then set rsh value to 0 otherwise to infinite
    def setIsGoal(self, aBool):
        self.isGoal = aBool
        if aBool:
            self.rsh= 0
        else:
            self.rsh= float('inf')
    
    #If vertex is an obstacle set rsh to infinite
    def setIsObstacle(self,aBool):
        self.isObstacle = aBool
        if aBool:
            self.rsh= float('inf') 
    
    #CalculateKey function of the D*Lite algorithm
    #Return the calculated key for sorting.
    def calculateKey(self, startNode, k, hIsZero, directNeighbors):
        if self.g < self.rsh:
            min1= self.g
        else: 
            min1= self.rsh 
        self.key= (min1 + self.h(startNode, hIsZero, directNeighbors) + k, min1)
        return self.key


    #Calculate the heuristic-value of the vertex
    def h(self, startNode, hIsZero=True, directNeighbors=False):
        if hIsZero:
            #Do not use a heuristic. Then more planning steps are needed
            return 0
        elif directNeighbors:
            #max. 4 neighbors, use exact distance without considering obstacles
            return abs(self.x - startNode.x) + abs(self.y -startNode.y)
        else:
            #max. eight neighbors: use euklidic distance
            return math.sqrt(math.pow(self.x - startNode.x,2) + math.pow(self.y -startNode.y,2))

    #Define a "<"  operator for comparision of two vertices
    def __lt__(self, anotherVertex):
        return self.key < anotherVertex.key
    

    def print(self):
        print('x:', self.x, 'y:', self.y, 'g:', self.g, 
              'rsh:', self.rsh, 'IsGoal:', self.isGoal, 
              'IsObstacle:', self.isObstacle)

if __name__ == "__main__":
    s=Vertex()
    s.print()
    s.setIsGoal(True)
    s.print()
    s2=Vertex()
    print(s<s2)

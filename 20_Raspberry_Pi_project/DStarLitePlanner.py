#!/usr/bin/python3
############################################################
# Class DStarLitePlanner
# This class implements the planning algorithm D* Lite 
# (see Sven Koenig, Maxim Likhachev, 2002) on a 
# two-dimensional grid of vertices (Class Vertex) with
# additional support for an interactive view.
#
# File: DStarLitePlanner.py
# Author: Detlef Heinze 
# Version: 1.1    Date: 05.06.2020       
###########################################################

import time
import platform as pf #Used for check if program runs on 
                      #Windows or on Raspbian (Linux)
import vertex as vertex
import priorityQueue as pq
import screenExecuter as se
import ev3_executer as ev3e

class DStarLitePlanner(object):

    #Create a new initialized DStarLitePlanner with a vertexgrid
    def __init__(self, myView, gridWidth=5, gridHeight= 4, hIsZero= True, directNeighbors=False):
        self.view= myView
        self.width= gridWidth
        self.height= gridHeight
        self.directNeighbors= directNeighbors # false=8, true=4
        self.vertexGrid = [[vertex.Vertex(x,y) for y in range(gridHeight)] for x in range(gridWidth)]
        print("Creating vertex grid with height:", gridHeight, "and width:", gridWidth, "\n")
        self.startCoordinates= [float('inf'),float('inf')]
        self.goalCoordinates= [float('inf'),float('inf')]
        self.obstacles= set()
        self.startNode= None
        self.goalNode= None
        self.lastNode= None
        self.hIsZero= hIsZero
        self.priorityQueue= pq.PriorityQueue()   #The priority queue U
        self.planReady = False #True if a plan (= a path) is present
        self.actualPath = [] #Sequence of vertices from start to goal
        self.executer= None #Planexecuter
    
    #### Functions for interactive view ########################################################

    def setStartCoordinates(self, x=0, y=0):
        self.startCoordinates= [int(x),int(y)]
        print("  New start coordinates:",self.startCoordinates)
    
    def getStartCoordinates(self):
        return self.startCoordinates

    def setGoalCoordinates(self, x=0, y=0):
        if self.goalCoordinates[0] != float('inf'):
            #Old goal-node
            vertex=self.vertexGrid[self.goalCoordinates[0]][self.goalCoordinates[1]]
            vertex.setIsGoal(False)
        self.goalCoordinates= [int(x),int(y)]
        self.vertexGrid[self.goalCoordinates[0]][self.goalCoordinates[1]].setIsGoal(True)
        print("  New goal coordinates:",self.goalCoordinates)

    def getGoalCoordinates(self):
        return self.goalCoordinates 

    def areStartAndGoalSet(self):
        return (self.getStartCoordinates() != [float('inf'),float('inf')]) and \
                self.getGoalCoordinates() != [float('inf'),float('inf')]
    
    #Execute the created plan. 
    def executePlan(self, execModeStr):
        if execModeStr == 'Screen Simulation':
            self.executer= se.ScreenExecuter(self.view, self)
            result= self.executer.executePlan()
            return result
        elif execModeStr == 'Lego EV3 Control':
            if pf.system() == 'Windows':
                return False, 'Lego EV3 Control is not supported on Windows: Use Raspbian (Raspberry Pi)'
            elif pf.system() == 'Linux':
                self.executer= ev3e.EV3_Executer(self.view, self)
                result= self.executer.executePlan()
                return result[0], result[1]
            return False, "Not yet implemented"

    ##### D* Lite Algorithm #############################################################

    #Initialize the planning process. Function implements the "Initialize" procedure
    #of the D*Lite algorithm. 
    def initializePlanning(self):
        print('Initialize planning:')
        self.goalNode= self.vertexGrid[self.goalCoordinates[0]][self.goalCoordinates[1]]
        self.k = 0.0  
        #All vertices have been already initialized with inf-value in vertex.py.
        #Also the goal node's rsh value is already initialized with 0 in the interactive view
        #Add now the inconsistent goal node into the priority queue.
        key= self.goalNode.calculateKey(self.startNode, self.k, self.hIsZero, self.directNeighbors)
        self.priorityQueue.insert(self.goalNode, key)
        print('Start- and goal-node:')
        self.startNode.print()
        self.goalNode.print()
  
    #Function implements the ComputeShortestPath function of the D*Lite algorithm
    def computeShortestPath(self):
        print("\nComputing shortest path")
        self.planSteps=0  #counts loops of while-statement
        while (self.priorityQueue.top_key() < self.startNode.calculateKey(self.startNode,self.k, self.hIsZero, \
                                                                          self.directNeighbors)) or \
                (self.startNode.rsh != self.startNode.g):
            k_old= self.priorityQueue.top_key()
            u= self.priorityQueue.pop()
            if not u in self.obstacles:
                self.updateVertexColor(u, "white")
            k= u.calculateKey(self.startNode, self.k, self.hIsZero, self.directNeighbors)
            if k_old < k:
                self.priorityQueue.insert(u, k)
                self.updateVertexColor(u, "yellow")
            elif u.g > u.rsh:
                u.g= u.rsh
                self.view.update_g(u.x, u.y) 
                for pred in self.neighbors(u):
                    self.updateVertex(pred)
            else:
                u.g= float('inf')
                self.view.update_g(u.x, u.y)
                predPlus_u = self.neighbors(u)
                predPlus_u.append(u)
                for i in predPlus_u:
                    self.updateVertex(i)
            self.planSteps+=1
            #Interactive behavior:
            if self.stepDelay > 0:
                time.sleep(self.stepDelay)
                self.view.master.update()
            elif self.stepDelay < 0:
                self.view.show('Press ok for next step')

    #Main planning function of the D* Lite algorithm
    def mainPlanning(self, planningMode="Run to result"):
        print('\nStart planning using mode:', planningMode)
        if planningMode == 'Slow step':
            self.stepDelay = 2  #2s delay
        elif planningMode == 'Manual step':
            self.stepDelay = -1  #User presses button to go forward
        else:
            self.stepDelay= 0 #0 ms delay
        self.planReady = False
        startTime= time.time()
        #Start the planning algorithm
        self.startNode= self.vertexGrid[self.startCoordinates[0]][self.startCoordinates[1]]
        self.lastNode= self.startNode
        self.initializePlanning()
        self.computeShortestPath()
        print('End ComputeShortestPath')
        print('Time to plan:', time.time() - startTime, 's\n')

        #A path exists if g(startNode) != float('inf')
        #Mark the path on screen in light blue
        self.planReady= self.startNode.g != float('inf')
        self.actualPath=[]
        self.showAndRemberPath()

    # Utilities for planning #########################################################

    #Calculate the cost of moving to a neighbor vertex
    def neighborCost(self, fromVertex, toVertex):
        if toVertex.isObstacle or fromVertex.isObstacle:
            return float('inf') #Do not move in or from an obstacle
        elif ((abs(fromVertex.x - toVertex.x) == 0) and \
            (abs(fromVertex.y - toVertex.y) == 1))  or \
            ((abs(fromVertex.x - toVertex.x) == 1) and \
            (abs(fromVertex.y - toVertex.y) == 0)):
            return 1  #straight move
        elif (abs(fromVertex.x - toVertex.x) == 1 and \
            abs(fromVertex.y - toVertex.y) == 1):
            return 1.4 #diagonal move
        else: 
            raise Exception("NeighborCost: Vertex is not a neighbor")

    #Calculate neighbors of a vertex depending on the
    #maximum count (4 or 8). Return neighbor vertices.
    def neighbors(self, aVertex):
        result= []
        if not self.view.directNeigbors.get(): #8 neighbors
            for x in range(aVertex.x -1, aVertex.x +2):
                for y in range(aVertex.y -1, aVertex.y +2): 
                    if x in range(self.width) and \
                       y in range(self.height) and \
                       not(x == aVertex.x and y == aVertex.y):
                        result.append(self.vertexGrid[x][y])
        else: #4 neighbors
            if aVertex.x -1 >= 0:
                result.append(self.vertexGrid[aVertex.x -1][aVertex.y])
            if aVertex.x +1 < self.width:
                result.append(self.vertexGrid[aVertex.x+1][aVertex.y])
            if aVertex.y-1 >= 0:
                result.append(self.vertexGrid[aVertex.x][aVertex.y-1])
            if aVertex.y+1 <self.height:
                result.append(self.vertexGrid[aVertex.x][aVertex.y+1])
        return result

    #Calculate the neighbor with the smallest sum of g and rsh-value.
    #Used after planning for finding the cheapest path.
    def calcCheapestNeighbor(self, aVertex):
        neighbors= self.neighbors(aVertex)
        cheapest= neighbors[0]
        for i in range(1,len(neighbors)):
            if (cheapest.g + cheapest.rsh) > (neighbors[i].g + neighbors[i].rsh):
                cheapest = neighbors[i]
        return cheapest

    #Function implements the UpdateVertex procedure of the D*Lite algorithm
    #Only calls for update on screen are added
    def updateVertex(self, aVertex):
        print('Update vertex', aVertex.x, aVertex.y)
        if aVertex != self.goalNode:
            #Calculate new rsh(aVertex)
            allNeighbors= self.neighbors(aVertex)
            values=[]
            for s in allNeighbors:
                value= self.neighborCost(aVertex,s) + s.g
                values.append(value)
            sortedValues=sorted(values) 
            aVertex.rsh= sortedValues[0]
            #Update rsh-value on screen
            self.view.update_rsh(aVertex.x, aVertex.y)
        if aVertex in self.priorityQueue:
            self.priorityQueue.remove(aVertex)
            print('Removed', aVertex.x, aVertex.y)
        if aVertex.g != aVertex.rsh:
            key= aVertex.calculateKey(self.startNode, self.k, self.hIsZero, self.directNeighbors)
            self.priorityQueue.insert(aVertex, key )
            print(aVertex.x, aVertex.y, 'added to priorityQueue')
            self.updateVertexColor(aVertex, "yellow")

    # Show the planned path on the view and remember the path
    # for execution.
    def showAndRemberPath(self):
        node= self.lastNode #from here to goal
        self.actualPath= []
        while (node != self.goalNode) and self.planReady:
            self.actualPath.append(node)
            node=self.calcCheapestNeighbor(node)
            if node != self.goalNode and not node.isObstacle:
                self.view.updateColor(node,'light blue')
            self.planReady= node.g != float('inf')
        if self.planReady:
            self.actualPath.append(self.goalNode)

    def clearOldPath(self, startStep):
        #Replanning occured. Remove old path#
        i= startStep
        node= self.actualPath[i]
        while (node != self.goalNode):
            if node not in self.obstacles:
                self.view.updateColor(node,'white')
            i+=1
            node= self.actualPath[i]

    def updateVertexColor(self, aVertex, aColor):
        if not aVertex== self.startNode and not aVertex == self.goalNode:
            self.view.updateColor(aVertex,aColor)

    # New obstacle on planned path during plan execution has been found. 
    # Replan the path to goal
    # Return if a plan exists.
    def replanning(self, aVertex):
        self.k= self.k + self.lastNode.h(self.startNode, self.hIsZero, self.directNeighbors)
        self.lastNode= self.startNode
        self.updateVertex(aVertex)
        neighbors= self.neighbors(aVertex)
        for n in neighbors:
            self.updateVertex(n)
        self.computeShortestPath()
        self.planReady= self.startNode.g != float('inf')
        return self.planReady   

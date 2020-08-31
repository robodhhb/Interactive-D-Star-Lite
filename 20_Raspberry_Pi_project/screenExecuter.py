#!/usr/bin/python3
############################################################
# Class ScreenExecuter
# The class ScreenExecuter simulates the execution of the
# path by a robot. The simulated robot is shown on screen 
# and drives from vertex to vertex of the path. Also
# changes in the direction are simulated (N, E, S, W) and
# (SW, SE, NW, NE).
# 
# File: screenExecuter.py
# Author: Detlef Heinze 
# Version: 1.1    Date: 22.07.2020       
###########################################################

import time

class ScreenExecuter(object):

    def __init__(self, myView, myPlanner):
        print('\nCreating ScreenExecuter')
        self.view= myView
        self.planner= myPlanner
        self.robotIconsIDs = {} #Dictionary for canvas icon ids
        self.actualOrientation= "" #North, East, South, West,  
                                   #NorthWest, NorthEast, SouthWest or SouthEast
        self.stepDelay= 0.4 #second(s) delay between execution steps
        
        self.createRobotIcons() #Icons used during execution of plan
 
    # Has to be overwritten in subclasses controlling real robots
    # Check business rules regarding the plan execution.
    # Return True or False
    def executionAllowed(self):
        #This class has no restrictions.
        return True

    # Execute the actual plan. Let the robot drive from startNode to goalNode.
    # Replan if an obstacle suddenly appears on the path.
    # Return True if execution was successfull, False otherwise.
    # Return also a string describing the result
    def executePlan(self):
        if not self.executionAllowed():
            return False, "Plan incompatible with executer. Check direct neighbors setting (Tab: Planning)" 
        result= self.connectRealRobot()
        if not result[0]: #no connection possible
            return result[0], result[1]
        else:
            print('Starting plan execution')
            result, reply= self.putRobotAtInitPos()
            abort=False
            #Now execute the plan including orientation of the robot
            while self.planner.startNode != self.planner.goalNode  \
                  and not abort and result:
                step= 1
                replanned= False
                while step < len(self.planner.actualPath) \
                      and not replanned and result:
                    nextVertex= self.planner.actualPath[step]
                    result, reply= self.orientRobotTo(nextVertex)
                    self.view.master.update()
                    self.delay()
                    if nextVertex.isObstacle or self.robotReportsObstacle():
                        # New obstacle occupies nextVertex on path!!! Replanning!!!
                        # New obstacles besides the path are not considered
                        # because the robot does not see them.
                        print('\nNew obstacle at', nextVertex.x, nextVertex.y)
                        if self.robotReportsObstacle() and not nextVertex.isObstacle:
                            nextVertex.isObstacle= True
                            self.planner.obstacles.add(nextVertex)
                            self.view.updateColor(nextVertex, 'brown')
                        print('Replanning!')
                        self.planner.clearOldPath(step)
                        abort= not self.planner.replanning(nextVertex)
                        self.planner.showAndRemberPath()
                        replanned=True
                        print('Replanning done\n')
                    else:
                        if result:
                            result, reply= self.moveRobot(self.planner.startNode, nextVertex, self.actualOrientation)
                        self.view.master.update()
                        self.delay()
                        step+=1
            self.view.canvGrid.itemconfig(self.robotIconsIDs[self.actualOrientation], \
                                          state= 'hidden')
            if not abort and result:
                result, reply= self.actionAtEnd()
                if result:
                    print('Goal reached.')
                    return True, 'Goal reached.'
                else:
                    return False, 'Robot error at goal'
            elif abort:
                print('No path to goal exists')
                result, reply= self.actionAtEnd()
                return False, 'No path to goal exists'
            elif not result:
                print('Abort with robot connection error')
                return result, 'Abort with robot connection error'

    # Calculate the orietation to the next vertex in the plan
    # which has to be a neighbor.
    # Return new orientation
    def calcOrientation(self, actualVertex, nextVertex):
        if actualVertex.x == nextVertex.x:
            if actualVertex.y -1 == nextVertex.y:
                newOrientation= "South"
            else:
                newOrientation= "North"
        elif actualVertex.y == nextVertex.y:
            if actualVertex.x -1 == nextVertex.x:
                newOrientation= "West"
            else:
                newOrientation='East'
        elif actualVertex.x +1 == nextVertex.x:
            if actualVertex.y +1 == nextVertex.y:
                newOrientation= "NorthEast"
            else:
                newOrientation= "SouthEast"
        elif actualVertex.x -1 == nextVertex.x:
            if actualVertex.y -1 == nextVertex.y:
                newOrientation= "SouthWest"
            else:
                newOrientation= "NorthWest"
        print('Orientation: ', newOrientation)
        return newOrientation
   
    # Orient the robot to the next vertex.
    # Return True if action was successfull.
    # Return also a string describing the situation.
    def orientRobotTo(self, nextVertex):
        print('\nOrient robot to next vertex', nextVertex.x, nextVertex.y)
        newOrientation= self.calcOrientation(self.planner.startNode, nextVertex)
        result= True
        reply= ''
        if self.actualOrientation != newOrientation:
            result, reply= self.moveRobot(self.planner.startNode,self.planner.startNode, newOrientation)
            self.actualOrientation= newOrientation
        return result, reply


    # Calculate the rectangle on screen at the given vertex  
    def vertexToRect(self, aVertex):
        tag= str(aVertex.x) + '-' + str(aVertex.y)
        rectHandle=self.view.canvGrid.find_withtag(tag)
        return self.view.canvGrid.coords(rectHandle)

    # Put robot icon at start of path with inital orientation then
    # orient robot to next vertex.
    # Return True if action was successfull.
    # Return also a string describing the situation.
    def putRobotAtInitPos(self):
        self.createRobotIcons()
        self.planner.startNode= self.planner.actualPath[0]
        self.actualOrientation= self.view.cbRoboOrientation.get()
        result, reply= self.moveRobot(self.planner.vertexGrid[0][0], self.planner.startNode, \
            self.actualOrientation, commandRobot=False)
        self.view.master.update()
        self.delay()
        self.putRealRobotAtInitPos()
        nextOrientation= self.calcOrientation(self.planner.startNode, self.planner.actualPath[1])
        if nextOrientation != self.actualOrientation:
            #Orient robot to first vertex of path
            result, reply= self.moveRobot(self.planner.startNode, self.planner.startNode, \
                                          nextOrientation)
        else:
            #Is there an unplanned obstacle on the first vertex?
            result, reply= self.obstacleStartCheck()
        self.view.master.update()
        self.delay()
        return result, reply

    # Has to be overwritten in subclasses controlling real robots
    # Establish a connection to the robot.
    # Return False with error message if connection
    # cannot be  established.
    # Return also a string describing the situation
    def connectRealRobot(self):
        # The screenExecuter allways has a connection
        return True, ''
   
    # Has to be overwritten in subclasses controlling real
    # robots. Ask user if robot is put at initial vertex
    # with initial orientation. 
    def putRealRobotAtInitPos(self):
        pass


    # Move robot to aVertex with an orienetation
    # Move all polygons to aVertex, only that with given orientation
    # shall be visible. Then command real robot, if any.
    def moveRobot(self, fromVertex, toVertex, orientation, commandRobot=True):
        print('\nMove robot to', toVertex.x, toVertex.y, orientation)
        result= True
        reply=''
        rectFromVertex= self.vertexToRect(fromVertex)
        rectToVertex= self.vertexToRect(toVertex)
        deltaX= rectToVertex[0] - rectFromVertex[0]
        deltaY= rectToVertex[1] - rectFromVertex[1]
        for key in self.robotIconsIDs:
            self.view.canvGrid.move(self.robotIconsIDs[key], deltaX,deltaY) #Moves a delta
        self.view.canvGrid.itemconfig(self.robotIconsIDs[self.actualOrientation], state= 'hidden')
        self.view.canvGrid.itemconfig(self.robotIconsIDs[orientation], state= 'normal')
        if commandRobot:
            #To be overwritten in subclasses for real robots
            result, reply= self.commandRobot(orientation) 
        self.planner.startNode= toVertex
        self.actualOrientation= orientation
        return result, reply
    
    # To be overwritten in subclasses with real robots (no simulation)
    # Command a real robot.
    # Return True if action was successfull.
    # Return also a string describing the situation.
    def commandRobot(self, orientation):
        #Do nothing here because this is a screen simulator
        return True, ''
    
    # To be overwritten in subclasses with real robots (no simulation)
    # Return if a real robot reports an obstacle ahead in driving direction
    # in the telemetry.
    def robotReportsObstacle(self):
        # No real robot here
        return False
    
    # To be overwritten in subclasses with real robots (no simulation)
    # Check for obstacle at start location before robot starts to drive
    # Is there an unplanned obstacle on the next vertex
    def obstacleStartCheck(self):
        #Do nothing here because this is a screen simulator
        return True, ''

    
    # To be overwritten in subclasses with real robots (no simulation)
    # Add action when path has been executed or robot has to stop when
    # replanning must be done because of a new obstacle
    # Return True if action was successfull.
    # Return also a string describing the situation.
    def actionAtEnd(self):
        #Do nothing here because this is a screen simulator
        return True, ''

    # To be overwritten in subclasses.
    # Add some delay between steps of plan execution for screen simulation 
    def delay(self):
        time.sleep(self.stepDelay)
        

    # Graphical elements #####################################################################
    # Create robot icons for simulation of moves from start to goal.
    # Initial position of all icons is 0,0 of actual vertexGrid
    def createRobotIcons(self):
        polygon_north = self.view.canvGrid.create_polygon(10, 0, 20, 35, 0,35, fill='blue', state='hidden')
        self.robotIconsIDs['North']= polygon_north
        polygon_south = self.view.canvGrid.create_polygon(0, 0, 20, 0, 10,35, fill='blue', state='hidden')
        self.robotIconsIDs['South']= polygon_south
        polygon_east = self.view.canvGrid.create_polygon(0, 0, 0, 20, 35, 10, fill='blue', state='hidden')
        self.robotIconsIDs['East']= polygon_east
        polygon_west = self.view.canvGrid.create_polygon(0, 10, 35, 0, 35, 20, fill='blue', state='hidden')
        self.robotIconsIDs['West']= polygon_west

        polygon_northEast= self.view.canvGrid.create_polygon(30, 0, 0,24, 18, 33, fill='blue', state='hidden')
        self.robotIconsIDs['NorthEast']= polygon_northEast
        polygon_northWest= self.view.canvGrid.create_polygon(0, 0, 30,24, 14, 33, fill='blue', state='hidden')
        self.robotIconsIDs['NorthWest']= polygon_northWest
        polygon_southWest= self.view.canvGrid.create_polygon(0, 30, 18,0, 30, 16, fill='blue', state='hidden')
        self.robotIconsIDs['SouthWest']= polygon_southWest
        polygon_southEast= self.view.canvGrid.create_polygon(30, 30, 12,0, 0, 16, fill='blue', state='hidden')
        self.robotIconsIDs['SouthEast']= polygon_southEast

        #Move all polygon to vertex in lower left corner of vertexGrid
        #From that location we can move all polygons to the actual position
        rect= self.vertexToRect(self.planner.vertexGrid[0][0])
        xOffset= (rect[0] + rect[2]) // 2
        yOffset= (rect[1] + rect[3]) // 2
        for key in self.robotIconsIDs:
            if key == "West" or key == "East":
                posX= xOffset-17
                posY= yOffset-10
            else:
                posX= xOffset-10
                posY= yOffset-17
            self.view.canvGrid.move(self.robotIconsIDs[key], posX, posY) 
            
        
#!/usr/bin/python3
############################################################
# Class EV3_Executer
# The class EV3_Executer executes a pathplan by commamding
# a Lego EV3 robot connected via a serial 
# bluetooth connection. An EV3 robot is shown on screen 
# and drives from vertex to vertex of the path. 
# The robot can move forward and change direction to
# north, east, south and west. 
#
# This class inherits from ScreenExecuter. 
# 
# File: ev3_executer.py
# Author: Detlef Heinze 
# Version: 1.1    Date: 22.07.2020       
###########################################################

import time
from screenExecuter import ScreenExecuter
import TMTCpi2EV3 as tmtcCom #Telemetety and Telecommand IF

class EV3_Executer(ScreenExecuter):

    def __init__(self, myView, myPlanner):
        print('\nCreating EV3_Executer')
        # Call base class initialisation
        ScreenExecuter.__init__(self,myView,myPlanner)
        self.serialPort='/dev/rfcomm0'  #Port to EV3
        self.mailboxName='abc'  #EV3 default mailbox name
        self.detectRealObstacle = False #True, if a new obstacle appeared
                                        #during plan execution
        self.lastCommand= '' #last command send to the robot
        self.initCommandDict()
        
        
    # Initialize the dictionaries for the robot commands depending
    # on the current orientation North, East, South or West
    def initCommandDict(self):
        northDict= {'East': 'TurnR90', 'South': 'Turn180', 'West': 'TurnL90', 'North': 'Drive'}
        eastDict=  {'North': 'TurnL90', 'South': 'TurnR90', 'West': 'Turn180', 'East': 'Drive'}
        southDict= {'North': 'Turn180', 'East': 'TurnL90', 'West': 'TurnR90', 'South': 'Drive'}
        westDict= {'North': 'TurnR90', 'East': 'Turn180', 'South': 'TurnL90', 'West': 'Drive'}
        
        self.directionDict = {'North': northDict,
                              'East': eastDict,
                              'South': southDict,
                              'West': westDict}      

    # Overwritten method of superclass.
    def executionAllowed(self):
        # Check business rules regarding the plan execution.
        # The EV3 robot control can only move robots to direct 
        # neighbors: Vertices in direction north, east, 
        # south and west.
        return self.planner.directNeighbors

    # Overwritten method of superclass.
    # Establish a connection to the robot.
    # Return False with error message if connection
    # cannot be  established
    def connectRealRobot(self):
        try:
            print('Connecting EV3 robot')
            self.ev3 = tmtcCom.TMTCpi2EV3(self.serialPort, self.mailboxName)
            print('Bluetooth device is present: ' + self.serialPort)
            ack, result= self.ev3.sendTC('Heartbeat', False)
            print(ack, result)
            if not ack:
                print('Heartbeat was not acknowledged. Start program on EV3!')
                return False,'Heartbeat was not acknowledged. Start program on EV3!'
            else:
                print("Heartbeat acknowledged")
                return True,"Heartbeat acknowledged"
        except:
            print('\nConnection error during EV3 communication')
            print('No device: ', self.serialPort)
            return False, 'Robot connection error: No device: ' + self.serialPort

    # Overwritten method of superclass.
    # Ask user if robot is put at initial vertex
    # with initial orientation. 
    def putRealRobotAtInitPos(self):
        self.view.show('Click OK if robot is located at vertex ' + str(self.planner.startNode.x) +\
                        '-' + str(self.planner.startNode.y) + ' with orientation ' + \
                        self.actualOrientation + '?')

    # Overwritten method of superclass 
    # Return if a real robot reports an obstacle ahead in driving direction
    # in the telemetry. 
    def robotReportsObstacle(self):
        # Return True if the last telecommand has been reported an obstacle
        # on the next vertex in view direction. If robot is driving then
        # stop it.
        if self.detectRealObstacle and self.lastCommand == 'Drive':
            self.actionAtEnd() # Stop robot: do not crash
        return self.detectRealObstacle

    # Overwritten method of superclass
    # Command robot with the next move action. This can be a turn or a 
    # forward drive.
    # Return True, if command was executed without error
    # Return additionally the telemetry from the robot
    def commandRobot(self, orientation):
        command= self.directionDict[self.actualOrientation][orientation]
        print('Commanding EV3:', command)
        #Send a telecommand, await telemetry and wait for max. 12 seconds
        ack, reply= self.ev3.sendTC(command, True, 12)
        self.lastCommand= command
        #If telemetry contains a ! at end then an obstacle is ahead.
        self.detectRealObstacle= reply[len(reply)-1] == '!'
        return ack, reply
    
    # Overwritten method of superclass
    # Check for obstacle at start location before robot starts to drive
    # Is there an unplanned obstacle on the next vertex
    # Return True, if command was executed without error
    # Return additionally the telemetry from the robot
    def obstacleStartCheck(self):
        print('Commanding EV3: CheckDistance')
        ack, reply= self.ev3.sendTC('CheckDistance', True, 12)
        print(ack,reply)
        self.lastCommand= 'CheckDistance'
        #If telemetry contains a ! at end then an obstacle is ahead.
        self.detectRealObstacle= reply[len(reply)-1] == '!'  
        return ack, reply    

    
    # Overwritten method of superclass
    # Robot drives to the goal and must be stopped when
    # it is totally on the goal vertex or a new obstacle appeared.
    # Return True, if command was executed without error
    # Return additionally the telemetry from the robot
    def actionAtEnd(self):
        print('Commanding EV3: Stop')
        ack, reply= self.ev3.sendTC('Stop', True, 12)
        self.lastCommand= 'Stop'
        return ack, reply    
    
    # Overwritten method of superclass
    # No delay needed here
    def delay(self):
        pass
        
            
            
            
            
        
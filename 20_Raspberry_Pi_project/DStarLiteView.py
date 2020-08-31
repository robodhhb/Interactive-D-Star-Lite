#!/usr/bin/python3
############################################################
# Class DStarLiteView
# The class DStarLiteView implements an interactive view
# for the vertexGrid of the D*Lite algorithm. It implements
# the interactive design of the terrain with start-, goalnode
# and obstacles and the pathplanning and path execution. 
#
# File: DStarLiteView.py
# Author: Detlef Heinze 
# Version: 1.1    Date: 22.07.2020       
###########################################################

from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from DStarLitePlanner import *
import enum

# Possible states of the application
class AppState(enum.Enum): 
    inDesign = 0
    inPlanning = 1
    planPresent = 2
    inExecution = 3
    afterExecution= 4

class DStarLiteView(object):

    #Initialize a new DStarLiteView
    def __init__(self, master):
        self.master = master
        self.master.geometry('700x600')
        self.master.resizable(0, 0)
        master.title("Interactive D* Lite 1.0")
        self.appState= AppState.inDesign

        #Default planning grid size
        self.gridHeight= 4
        self.gridWidth= 5
        
        #tab control: designTab, row=0
        self.tab_control = ttk.Notebook(master)
        self.designTab = ttk.Frame(self.tab_control)
        self.planTab = ttk.Frame(self.tab_control)
        self.execTab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.designTab, text='Design')
        self.tab_control.add(self.planTab, text='Planning')
        self.tab_control.add(self.execTab, text='Execution')

        self.lblGridWith = Label(self.designTab, text="Grid width:")
        self.lblGridWith.grid(column=0, row=0, pady= 5, sticky= W)
        self.gridWidthVal= IntVar()
        self.gridWidthVal.set(self.gridWidth)     
        self.spinGridWidth= Spinbox(self.designTab, from_=4, to=11, width=5, state='readonly',textvariable=self.gridWidthVal)
        self.spinGridWidth.grid(column=1, row=0, pady=5, sticky= W)
        self.lblGridHeight = Label(self.designTab, text="Grid height:")
        self.lblGridHeight.grid(column=2, row=0, pady= 5, sticky= W)
        self.gridHeightVal= IntVar()  
        self.gridHeightVal.set(self.gridHeight)   
        self.spinGridHeight= Spinbox(self.designTab, from_=4, to=11, width=5, state='readonly',textvariable=self.gridHeightVal)
        self.spinGridHeight.grid(column=3, row=0, pady=5, sticky= W)
        self.btnRecreate= Button(self.designTab, text="Recreate grid", command=self.btnRecreate_clicked)
        self.btnRecreate.grid(column=4, row=0, pady=5, padx= 5, sticky=W)
        self.tab_control.grid(column=0, row=0)

        #tab control: designTab, row=1
        self.lblClickMode= Label(self.designTab, text="Click mode:")
        self.lblClickMode.grid(column=0, row=1, pady= 5, sticky= W)
        self.clickModeVal= IntVar()  
        self.clickModeVal.set(1)
        self.rad1 = Radiobutton(self.designTab,text='Start', value=1, variable=self.clickModeVal)
        self.rad2 = Radiobutton(self.designTab,text='Goal', value=2, variable=self.clickModeVal)
        self.rad3 = Radiobutton(self.designTab,text='Obstacle', value=3, variable=self.clickModeVal)
        self.rad1.grid(column=1, row=1)
        self.rad2.grid(column=2, row=1)
        self.rad3.grid(column=3, row=1)
        
        #tab control: planningTab
        self.lblMode= Label(self.planTab, text="Planning mode:")
        self.lblMode.grid(column=0, row=0, sticky= W)
        self.cbPlanningMode= ttk.Combobox(self.planTab, state="readonly", values=('Fast','Slow step', 'Manual step'),
                                          width=12)
        self.cbPlanningMode.current(0)
        self.cbPlanningMode.grid(column=1, row=0, pady= 5, padx=0, sticky= W)
        self.h0_check = BooleanVar()
        self.h0_check.set(FALSE) #set check state
        self.h0Check = Checkbutton(self.planTab, text='h = 0', state=NORMAL, var=self.h0_check)
        self.h0Check.grid(column=2, row=0, padx=10)
        self.directNeigbors = BooleanVar()
        self.directNeigbors.set(True) #False= 8 neighbors, True= 4 neighbors
        self.neighbors = Checkbutton(self.planTab, text='Only direct neighbors(4)', var=self.directNeigbors)
        self.neighbors.grid(column=3, row=0, padx=10)
        self.btnPlan= Button(self.planTab, text="Start planning", command=self.btnPlan_clicked)
        self.btnPlan.grid(column=4, row=0, pady=5, padx= 20,sticky=W)

        self.lblPlanHint=Label(self.planTab, text="Planning hint:")
        self.lblPlanHint.grid(column=0, row=1, pady= 5, sticky= W)
        self.planHint=StringVar()
        self.planHint.set('-')
        self.lblPlanHintText= Label(self.planTab, text="", textvariable= self.planHint)
        self.lblPlanHintText.grid(column=1, row=1, pady= 5, columnspan=2, sticky= W)

        #tab control: execTab
        self.lblExecMode= Label(self.execTab, text="Execution mode:")
        self.lblExecMode.grid(column=0, row=0, sticky= W)
        self.cbExecMode= ttk.Combobox(self.execTab, state="readonly", values=('Screen Simulation', 'Lego EV3 Control'),
                                          width=18)
        self.cbExecMode.current(0)
        self.cbExecMode.grid(column=1, row=0, pady= 5, padx=0, sticky= W)
        self.lblRoboOrientation= Label(self.execTab, text="Robot start orientation:")
        self.lblRoboOrientation.grid(column=2, row=0, padx=8, sticky= W)
        self.cbRoboOrientation= ttk.Combobox(self.execTab, state="readonly", values=('North', 'East', 'South', 'West'),
                                          width=8)
        self.cbRoboOrientation.current(0)
        self.cbRoboOrientation.grid(column=3, row=0, pady= 5, padx=0, sticky= W)                                 
        self.btnExec= Button(self.execTab, text="Execute plan", command=self.btnExec_clicked)
        self.btnExec.grid(column=4, row=0, pady=5, padx= 20,sticky=W)
        self.lblExecHint=Label(self.execTab, text="Execution hint:")
        self.lblExecHint.grid(column=0, row=1, pady= 5, sticky= W)
        self.execHint= StringVar()
        self.execHint.set('-')
        self.lblExecHintText= Label(self.execTab, text="", textvariable= self.execHint)
        self.lblExecHintText.grid(column=1, row=1, pady= 5, columnspan=2, sticky= W)

        #Row = 2 the grid
        self.createGrid()
        

    #### Eventhandler ####################################################################

    # Button "Recreate" has been clicked. 
    def btnRecreate_clicked(self):
        #Recreate the planning grid including all variables
        self.planHint.set('-')
        self.master.update()
        self.createGrid()
        self.h0Check.config(state="normal")
        self.neighbors.config(state="normal")
        self.appState= AppState.inDesign
    
    #Button "Start Planning" has been clicked. Execute planning
    def btnPlan_clicked(self):
        if self.appState != AppState.inDesign:
            messagebox.showinfo('Hint', 'Plan already created')
            return
        self.tab_control.tab(0, state="disabled")
        self.tab_control.tab(2, state="disabled")
        #Check business rules
        if self.planner.areStartAndGoalSet():
            self.planner.hIsZero= self.h0_check.get()
            self.planner.directNeighbors= self.directNeigbors.get()
            self.planHint.set('Planning in progress.......')
            self.appState= AppState.inPlanning
            self.master.update()
            self.planner.mainPlanning(self.cbPlanningMode.get())
            if self.planner.planReady:
                self.appState= AppState.planPresent
                self.h0Check.config(state="disabled")
                self.neighbors.config(state="disabled")
                self.planHint.set('Planning successful within ' + str(self.planner.planSteps) + ' steps')
                messagebox.showinfo('Hint', 'Plan is ready')
            else:
                self.appState= AppState.inDesign
                self.planHint.set('Planning unsuccessful !!!')
                messagebox.showinfo('Hint', 'No plan exists')
                messagebox.showinfo('Hint', 'Recreating grid')
                self.btnRecreate_clicked()
            
        else:
            messagebox.showinfo('Hint', 'Start- and/or Goalvertex is not definied')
            self.appState= AppState.inDesign
        self.tab_control.tab(0, state="normal")
        self.tab_control.tab(2, state="normal")
        
    # Button "Execute" has been clicked
    def btnExec_clicked(self):
        #Check business rules
        if not self.planner.planReady:
            messagebox.showinfo('Hint', 'No plan present. Goto design and planning tab.')
        else:
            self.appState= AppState.inExecution
            self.tab_control.tab(0, state="disabled")
            self.tab_control.tab(1, state="disabled")
            self.clickModeVal.set(3) #Obstacle Mode
            self.execHint.set('Click to add obstacles during plan execution')
            result= self.planner.executePlan(self.cbExecMode.get())  
            if result[0]:
                messagebox.showinfo('Hint', 'Plan has been executed!')
                self.appState= AppState.afterExecution
            else:
                messagebox.showinfo('Hint', result[1])
                self.appState= AppState.planPresent
            self.planHint.set('-')
            self.tab_control.tab(0, state="normal")
            self.tab_control.tab(1, state="normal")
            

    # Calculate the x and y coordinate of vertexGrid which the user has clicked.
    # If a g- or rsh- value was clickes find the rectangle below it. 
    # Return 4 values: True, if click was within a rectangle,
    #                  the x anf y coord of the rectangle in vertexGrid
    #                  and the rectangle clicked
    def getClickInRectangle(self, current):
        if self.canvGrid.gettags(current)[0] == 'rect':
            return True, self.canvGrid.gettags(current)[1],\
                        self.canvGrid.gettags(current)[2],\
                        current
        if self.canvGrid.gettags(current)[0] == 'gtext':
            below= self.canvGrid.find_below(current)
            if self.canvGrid.gettags(below)[0] == 'rect':
                return True, self.canvGrid.gettags(below)[1],\
                       self.canvGrid.gettags(below)[2],\
                       below
        if self.canvGrid.gettags(current)[0] == 'rshtext':
            below= self.canvGrid.find_below(current)
            below1= self.canvGrid.find_below(below)
            if self.canvGrid.gettags(below1)[0] == 'rect':
                return True, self.canvGrid.gettags(below1)[1],\
                       self.canvGrid.gettags(below1)[2],\
                       below1
        else: #no rectangle clicked
            return False, 0, 0, current

    #Handle the click-event in the canvas if appState is inDesing or inExecution
    def canv_clicked(self, event):
        print("clicked at", event.x, event.y)
        if (self.appState == AppState.inDesign or self.appState == AppState.inExecution) and \
            self.canvGrid.find_withtag(CURRENT):
            print(self.canvGrid.gettags(CURRENT))
            print(self.getClickInRectangle(CURRENT))
            result= self.getClickInRectangle(CURRENT)
            if result[0]: #Click within a rectangle of the grid
                x= result[1] #x coordinate in grid
                y= result[2] #y coordiante in grid
                clickMode= self.clickModeVal.get()
                if not self.isNodeOccupied(x,y,clickMode):     
                    if clickMode == 1:
                        #Set start node
                        if self.planner.getStartCoordinates()[0] != float('inf'):
                            tag= str(self.planner.getStartCoordinates()[0]) + '-' + str(self.planner.getStartCoordinates()[1])
                            handle=self.canvGrid.find_withtag(tag)
                            self.canvGrid.itemconfig(handle, fill= "white")
                        self.canvGrid.itemconfig(result[3], fill="green")
                        self.planner.setStartCoordinates(x,y)
                    elif clickMode == 2:
                        #Set goal node
                        oldGoal= self.planner.getGoalCoordinates()[0] != float('inf')
                        if oldGoal:
                            oldGoalCoord= self.planner.getGoalCoordinates()
                            tag= str(oldGoalCoord[0]) + '-' + str(oldGoalCoord[1])
                            handle=self.canvGrid.find_withtag(tag)
                            self.canvGrid.itemconfig(handle, fill= "white")
                        self.canvGrid.itemconfig(result[3], fill="red")
                        self.planner.setGoalCoordinates(x,y)
                        self.update_rsh(x,y)
                        if oldGoal:
                            self.update_rsh(oldGoalCoord[0], oldGoalCoord[1])
                    elif clickMode == 3:
                        #Set or reset obstacale node
                        node= self.planner.vertexGrid[int(x)][int(y)]
                        if not node.isObstacle:
                            node.isObstacle= True
                            self.canvGrid.itemconfig(result[3], fill="brown")
                            self.planner.obstacles.add(node)
                        elif not self.appState == AppState.inExecution:
                            #Obstacles can only be removed in Design
                            node.isObstacle= False
                            self.canvGrid.itemconfig(result[3], fill="white")
                            self.planner.obstacles.remove(node)
                        self.update_rsh(x,y)
        else: 
            self.show('Action not possible in this state of planning. Recreate grid.')
            
    def show(self, aMessage):
        messagebox.showinfo('Hint', aMessage)

    #### Functions ############################################################
    
    #Create a new planner and draw the grid
    def createGrid(self):
        #Create a planner and initialize it
        print('Creating planner')
        self.planner= DStarLitePlanner(self, 
                               gridWidth=self.gridWidthVal.get(),
                               gridHeight= self.gridHeightVal.get(),
                               hIsZero= self.h0_check.get(),
                               directNeighbors= self.directNeigbors.get()) 
        horizShift= 30
        self.canvGrid = Canvas(self.master, height=800,width= 600 + horizShift)
        self.canvGrid.bind("<Button-1>", self.canv_clicked)
        self.canvGrid.grid(column=0, row=2, pady=10, padx= 10, columnspan=6, sticky= W)                      
        self.drawPlanningGrid(horizShift)
        
   
    #Draw the actual status of the planning grid
    def drawPlanningGrid(self, horizShift):
        #Draw planning grid
        self.canvGrid.create_rectangle(0,0, 680, 430, outline="white", fill="white")
        self.stepX= 600//self.gridWidthVal.get()
        self.stepY= 400//self.gridHeightVal.get()
        rowCount= self.gridHeightVal.get()-1
        columnCount=0
        #Add rectangles with g and rsh values
        for i in range(0,600-self.stepX+1, self.stepX):
            for j in range(0,400-self.stepY+1, self.stepY):
                self.canvGrid.create_rectangle(i+horizShift,j+2, i+horizShift+self.stepX, 
                                               j+self.stepY+2, fill="white", 
                                               tags=('rect', columnCount, rowCount, str(columnCount)+ '-' + str(rowCount)))
                self.canvGrid.create_text(i+horizShift+self.stepX//2, j+2+self.stepY//3, 
                                          text='g:' + str(self.planner.vertexGrid[columnCount][rowCount].g),
                                          tags= ('gtext','g-' + str(columnCount)+ '-' + str(rowCount)))
                self.canvGrid.create_text(i+horizShift+self.stepX//2-5, j+2+self.stepY//3+15, 
                                          text='rsh:' + str(self.planner.vertexGrid[columnCount][rowCount].rsh),
                                          tags= ('rshtext', 'rsh-' + str(columnCount)+ '-' + str(rowCount)))
                rowCount-=1
            columnCount+=1
            rowCount=self.gridHeightVal.get()-1
        #Add row and column numbers                                       
        rowCount= self.gridHeightVal.get()-1
        for i in range(0,400-self.stepY+1,self.stepY):
            self.canvGrid.create_text(15, i+self.stepY/2,text=str(rowCount))
            rowCount-=1
        columnCount= 0
        for i in range(0,600, self.stepX ):
            self.canvGrid.create_text(i+horizShift+self.stepX/2, 400+ 15, text=str(columnCount))
            columnCount+=1
    
    #Update rsh-value on screen
    def update_rsh(self, x,y):
        tag= 'rsh-'+ str(x) + '-' + str(y)
        #print('rsh-tag:' + tag)
        handle=self.canvGrid.find_withtag(tag)
        value= round(self.planner.vertexGrid[int(x)][int(y)].rsh,2)
        self.canvGrid.itemconfig(handle, text='rsh:' + str(value))
        #print(value)
        
    #Update g-value on screen
    def update_g(self,x,y):
        tag= 'g-'+ str(x) + '-' + str(y)
        #print('g:' + tag)
        handle=self.canvGrid.find_withtag(tag)
        value= round(self.planner.vertexGrid[int(x)][int(y)].g,2)
        self.canvGrid.itemconfig(handle, text='g:' + str(value))

    # Update-color of vertex on screen if it is not the start- or goal-node
    def updateColor(self, aVertex, aColor):
        tag= str(aVertex.x) + '-' + str(aVertex.y)
        handle=self.canvGrid.find_withtag(tag)
        self.canvGrid.itemconfig(handle, fill= aColor)

    #Check if the clicked rectangle is occupied by other or the same
    #type of node regarding the clickMode 
    def isNodeOccupied(self,x,y,clickMode):
        start= self.planner.getStartCoordinates()
        if [int(x),int(y)] != start:
            goal= self.planner.getGoalCoordinates()
            if [int(x),int(y)] != goal:
                ob= self.planner.vertexGrid[int(x)][int(y)].isObstacle
                if ob and clickMode <= 2:
                    messagebox.showwarning('Vertex occupied', 'The vertex is occupied by an obstacle')
                    return True
                else:
                    return False
            else:
                messagebox.showwarning('Vertex occupied', 'The vertex is occupied by a goal')
                return True
        else:
            messagebox.showwarning('Vertex occupied', 'The vertex is occupied by a start node')
            return True

    #Print function for test purpose
    def dumpVertices(self):
        [[self.planner.vertexGrid[x][y].print() for x in range(self.gridWidth)] for y in range(self.gridHeight)]

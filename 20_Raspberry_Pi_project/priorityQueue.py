#!/usr/bin/python3
############################################################
# Class PriorityQueue
# This class implements a priority queue for the 
# planning algorithm D*Lite. If the queue is not
# empty then the first element (index=0) has the
# smallest key-value of all elements.
#
# File: priorityQueue.py
# Author: Detlef Heinze 
# Version: 1.0    Date: 22.07.2020       
###########################################################
import heapq
import vertex as vertex



class PriorityQueue:

    #Initialize a new instance
    def __init__(self):
        self.elements = []

    #Return True, if the queue is empty
    def empty(self):
        return len(self.elements) == 0

    #Return the number of elements    
    def count(self):
        return len(self.elements)

    #Insert a new item with the calculated key into the queue
    def insert(self, item, calculatedKey):
        heapq.heappush(self.elements, (calculatedKey, item))

    #Pop and return the smallest item in the queue
    def pop(self):
        element = heapq.heappop(self.elements)
        return element[1]
        
    #Return the key of the first element in the queue
    #If the priority queue is empty return key with inf-values.
    #This terminates the while loop of the ComputeShortestPath procedure of
    #the D*light algorithm
    def top_key(self):
        if self.empty():
            return (float('inf'),float('inf'))
        else:
           #print('Elements:', self.elements)
           return heapq.nsmallest(1, self.elements)[0][0]
    
    #Remove an element from the queue
    def remove(self, node):
        self.elements = [e for e in self.elements if e[1] != node]
        heapq.heapify(self.elements)
        
    #Iterator
    def __iter__(self):
       for key, node in self.elements:
            yield node

if __name__ == "__main__":
    pq= PriorityQueue()
    a=vertex.Vertex()
    a.rsh=0
    b=vertex.Vertex()
    b.rsh=1
    pq.insert(b,1)
    pq.insert(a,0)
    print('Elements:',pq.count())
    print('TopKey:', pq.top_key())
    aPop= pq.pop()
    print(aPop.rsh)
    bPop= pq.pop()
    print(bPop.rsh)
    print(pq.empty())
    

#Required Imports
try:
    import pygame
    import sys
    import math
    from tkinter import *
    from tkinter import ttk
    from tkinter import messagebox
    import os
except:
    import install_requirements  # install packages

    import pygame
    import sys
    import math
    from tkinter import *
    from tkinter import ttk
    from tkinter import messagebox
    import os


#Constants
SCREEN_HEIGHT = 800
SCREEN_WIDTH = SCREEN_HEIGHT #Lets keep things simple with regular hexagons
NUM_COLS = 50
NUM_ROWS = NUM_COLS
GRID = [0 for i in range(NUM_COLS)]

#Colors
VISITED = (255,0,0)
NEIGHBORING = (0,255,0)
IN_OPT = (0,0,255)
OOB = (220,220,220)
START_FINISH = (255,8,127)
NOT_VISITED = (255,255,255)
OBSTACLE = (0,0,0)
BACKGROUND = (104,107,112)

#Global Variables
w = SCREEN_WIDTH / NUM_COLS
h = SCREEN_HEIGHT / NUM_ROWS
open = []
closed = []

class Node:
    def __init__(self, i, j):
        #Screen index
        self.i = i
        self.j = j
        
        #physical location of the center of the hexagon
        self.x = w*(i+1/2)
        self.y = h*(j+1/2+1/2*(j%2==0)) #even columns are shifted down by 1/2 unit
        
        #Member variables for the A-star algorithm
        self.f = 0
        self.g = 0
        self.h = 0
        
        #List to hold Node's neighbors, to possibly add them to open list
        self.neighbors = []
        
        #Previously visited Node
        self.previous = None
        
        #Is this node an obstacle?
        self.obstacle = False
        
        #Has this node been traversed?
        self.closed = False
        
        #Contribution to cost
        self.cost = 1
    
    #Create Neighborhood
    def neighborhood(self, board):
        i, j = self.i, self.j
        
        #above
        n_i, n_j = i, j - 1
        if i > 0 and not board[n_i][n_j].obstacle:
            self.neighbors.append(board[n_i][n_j])
        
        #below
        n_i, n_j = i, j + 1
        if i < NUM_COLS - 1 and not board[n_i][n_j].obstacle:
            self.neighbors.append(board[n_i][n_j])
        
        #top right
        n_i = i + 1
        n_j = j if j % 2 == 0 else j - 1
        if i < NUM_COLS - 1 and j > 0 and not board[n_i][n_j].obstacle:
            self.neighbors.append(board[n_i][n_j])
        
        #bottom right
        n_i = i + 1
        n_j = j + 1 if j % 2 == 0 else j
        if i < NUM_COLS - 1 and j < NUM_ROWS - 1 and not board[n_i][n_j].obstacle:
            self.neighbors.append(board[n_i][n_j])
        
        #bottom left
        n_i = i - 1
        n_j = j + 1 if j % 2 == 0 else j
        if i > 0 and j < NUM_ROWS - 1 and not board[n_i][n_j].obstacle:
            self.neighbors.append(board[n_i][n_j])
        
        #top left
        n_i = i - 1
        n_j = j if j % 2 == 0 else j - 1
        if i > 0 and j > 0 and not board[n_i][n_j].obstacle:
            self.neighbors.append(board[n_i][n_j])
    
    #Draw the hexagon according to the color input
    def draw(self, color, lineWidth):
        if not self.closed:
            x_offset = w/(2*math.cos(math.pi/6))
            y_offset = h/(2*math.cos(math.pi/6))
            small_x_offset = (w/2)*math.tan(math.pi/6)
            pygame.draw.polygon(screen, color, ([self.x+x_offset, self.y], [self.x+small_x_offset, self.y-y_offset], [self.x-small_x_offset, self.y-y-y_offset], [self.x-x_offset, self.y], [self.x-small_x_offset, self.y+y_offset], [self.x+small_x_offset, self.y+y_offset]), lineWidth)
            pygame.display.update()
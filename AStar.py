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
        self.y = h*(j+1/2+1/2*(i%2==0)) #even columns are shifted down by 1/2 unit
        
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
        if j > 0 and not board[n_i][n_j].obstacle:
            self.neighbors.append(board[n_i][n_j])
        
        #below
        n_i, n_j = i, j + 1
        if j < NUM_ROWS - 1 and not board[n_i][n_j].obstacle:
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
            p1 = [self.x+x_offset, self.y]
            p2 = [self.x+small_x_offset, self.y-y_offset]
            p3 = [self.x-small_x_offset, self.y-y_offset]
            p4 = [self.x-x_offset, self.y]
            p5 = [self.x-small_x_offset, self.y+y_offset]
            p6 = [self.x+small_x_offset, self.y+y_offset]
            pygame.draw.polygon(screen, color, (p1, p2, p3, p4, p5, p6), lineWidth)
            pygame.display.update()

# Initialize board
GRID = [0 for i in range(NUM_COLS)]
for i in range(NUM_COLS):
    GRID[i] = [0 for j in range(NUM_ROWS)]
    
for i in range(NUM_COLS):
    for j in range(NUM_ROWS):
        GRID[i][j] = Node(i,j)

# Function for setting start and finish points
def onsubmit():
    global start
    global end
    st = startBox.get().split(' ')
    ed = endBox.get().split(' ')
    start = GRID[int(st[0])][int(st[1])]
    end = GRID[int(ed[0])][int(ed[1])]
    window.quit()
    window.destroy()

# Function for creating obstacle points by dragging mouse
def createObstacle(x):
    obstacle = GRID[x[0] // (SCREEN_WIDTH // NUM_COLS)][x[1] // (SCREEN_HEIGHT // NUM_ROWS)]
    if not (obstacle == start or obstacle == end or obstacle.obstacle):
        obstacle.obstacle = True
        obstacle.draw(OBSTACLE, 0)
        
# Define heuristic for A*
def heuristic(p1, p2):
    return math.sqrt((p1.x-p2.x)**2+(p1.y-p2.y)**2)
    
def main():
    start.draw(START_FINISH, 0)
    end.draw(START_FINISH, 0)
    
    if open:
        lowestIndex = 0
        for i in range(len(open)):
            if open[i].f < open[lowestIndex].f:
                lowestIndex = i
                
        current = open[lowestIndex]
        if current == end:
            print('done', current.f)
            start.draw(START_FINISH, 0)
            temp = current.f
            for i in range(round(current.f)):
                current.closed = False
                current.draw(IN_OPT,0)
                current = current.previous
            end.draw(START_FINISH, 0)
            
            Tk().wm_withdraw()
            result = messagebox.askokcancel('Goal Found!', ('The solution was found.\nThe total distance travelled was ' + str(temp) + '\nRun the program again?'))
            if result:
                os.execl(sys.executable, sys.executable, *sys.argv)
            else:
                game_over = True
                while game_over:
                    ev = pygame.event.get()
                    for event in ev:
                        if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                            game_over = False
                            break
            pygame.quit()
            
        open.pop(lowestIndex)
        closed.append(current)
        
        neighbors = current.neighbors
        for neighbor in neighbors:
            if neighbor not in closed:  
                tempG = current.g + current.cost
                if neighbor in open:
                    if neighbor.g > tempG:
                        neighbor.g = tempG
                else:
                    neighbor.g = tempG
                    open.append(neighbor)
                    
            neighbor.h = heuristic(neighbor, end)
            neighbor.f = neighbor.g + neighbor.h
            
            if neighbor.previous is None:
                neighbor.previous = current
    
    if var.get():
        for i in range(len(open)):
            open[i].draw(NEIGHBORING, 0)
            
        for i in range(len(closed)):
            if closed[i] != start:
                closed[i].draw(VISITED, 0)
    current.closed = True
    
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.fill(BACKGROUND)

for i in range(NUM_COLS):
    for j in range(NUM_ROWS):
        GRID[i][j].draw(NOT_VISITED, 1)
        
for i in range(NUM_ROWS):
    GRID[0][i].draw(OOB, 0)
    GRID[0][i].obstacle = True
    GRID[NUM_COLS-1][i].obstacle = True
    GRID[NUM_COLS-1][i].draw(OOB, 0)
    GRID[i][NUM_ROWS-1].draw(OOB, 0)
    GRID[i][0].draw(OOB, 0)
    GRID[i][0].obstacle = True
    GRID[i][NUM_ROWS-1].obstacle = True

window = Tk()
label = Label(window, text = 'Starting point: x1 y1')
startBox = Entry(window)
label1 = Label(window, text = 'Ending point: x2 y2')
endBox = Entry(window)
var = IntVar()
drawPath = ttk.Checkbutton(window, text="Display steps?", onvalue=1, offvalue=0, variable=var)

submit = Button(window, text="Submit", command=onsubmit)

drawPath.grid(columnspan=2, row=2)
submit.grid(columnspan=2, row=3)
label1.grid(row=1, pady=3)
endBox.grid(row=1, column=1, pady=3)
startBox.grid(row=0, column=1, pady=3)
label.grid(row=0, pady=3)

window.update()
mainloop()

pygame.init()
open.append(start)

start.draw(START_FINISH, 0)
end.draw(START_FINISH, 0)

loop = True
while loop:
    ev = pygame.event.get()
    for event in ev:
        if event.type == pygame.QUIT:
            pygame.quit()
        if pygame.mouse.get_pressed()[0]:
            try:
                pos = pygame.mouse.get_pos()
                createObstacle(pos)
            except AttributeError:
                pass
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                loop = False
                break
                
for i in range(NUM_COLS):
    for j in range(NUM_ROWS):
        GRID[i][j].neighborhood(GRID)

while True:
    ev = pygame.event.poll()
    if ev.type == pygame.QUIT:
        pygame.quit()
    pygame.display.update()
    main()
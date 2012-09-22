# AI Term Project
# Group 18 (Shreya Inamdar, Deepika Bablani, Ajith Ranka)
# Version: 25-April-2012/3

import math	# for sqrt, log
import random	# for random, randint
import os	# for clear screen
import time	# for delay

SIZE = 9
COLORDICT = {'EMPTY': '.', 'BLACK': 'B', 'WHITE': 'W'}
C = 0.44	# UCT exploration constant (< 1)
MAXMOVES = SIZE * SIZE

# Attributes: point.x, point.y and point.color
class Point:
    def __init__(self):
        self.used = False

    def setXY(self, x, y):
        if (0 <= x < SIZE) and (0 <= y < SIZE): 
            self.x, self.y = x, y
        else: raise AttributeError
    
    def setColor(self, color):
        if(color in COLORDICT):
            self.color = color
        else: raise AttributeError
 
    def getXY(self):
        return self.x, self.y
    
    def getColor(self):
        return self.color

# Attributes: board.size, board.point[][], board.koPoint
class Board(Point):
    def __init__(self):
        self.size = SIZE
        self.nextPlayer = 'BLACK' 	# Black plays first
        self.koPoint = []
        self.point = [[Point() for i in range(SIZE)] for j in range(SIZE)]
        self.emptyPoints = []
        self.history = []		# List of moves played
        self.blackDead = 0		# Dead black stones
        self.whiteDead = 0              # Dead white stones
        for i in range(SIZE):
            for j in range(SIZE):
                self.point[i][j].setXY(i, j)
                self.point[i][j].setColor('EMPTY')
                self.emptyPoints.append((i, j))
    
    def cloneBoard(self):
        copy = Board()
        for i in range(SIZE):
             for j in range(SIZE):
                copy.point[i][j].x = self.point[i][j].x
                copy.point[i][j].y = self.point[i][j].y
                copy.point[i][j].color = self.point[i][j].color
        return copy

    def reset(self):
        self.__init__()

    def move(self, point):
        # Is the move a pass? 
        if (point == 'PASS'):
            if (self.nextPlayer == 'WHITE'):
                self.nextPlayer = 'BLACK'
            else:
                self.nextPlayer = 'WHITE'
            return 

        capturedStones = []	# Coordinates of captured stones
        # Is the point empty?
        if (point.color != 'EMPTY'):
#            print 'Sorry. The point is not empty.'
            return None

        # Is the point leading to repetition?
        if ((point.x, point.y) in self.koPoint):
#            print 'Sorry. Repetition is not allowed.'
            return None

        # Is the move suicide?
        neighbours = getNeighbours(point, self)
        isSuicide = True
        myColor = self.nextPlayer 
        enemyColor = 'WHITE' if point.color == 'BLACK' else 'BLACK'
        for pt in neighbours:

            # If the neighbour is empty, isSuicide = false
            if (pt.color == 'EMPTY'):
                isSuicide = False

            # If the neighbour is an ally not in atari, isSuicide = false
            elif (pt.color == myColor) and (inAtari(pt, self) == False):
                isSuicide = False

            # If the neighbour is an enemy in atari, isSuicide = false
            # This move is a capture
            elif (pt.color == enemyColor) and (inAtari(pt, self) == True):
                isSuicide = False

                # Remove enemy stones from the board
                x, y = pt.x, pt.y
                for (i, j) in getChainPoints(x, y, self):
                    self.point[i][j].setColor('EMPTY')
                    capturedStones.append((i,j))
                    if (enemyColor == 'WHITE'): self.whiteDead += 1
                    else: self.blackDead += 1
                        

        # If suicide, return none
        if (isSuicide):
#            print 'Sorry. Suicide is not allowed.' 
            return None 

        # The point is not empty
        # And the move is not suicidal or repetitive
        # Therefore, a legal move
        point.setColor(self.nextPlayer)
        point.used = True
        self.history.append((point.x, point.y))
        self.emptyPoints.remove((point.x, point.y))
        if (self.nextPlayer == 'WHITE'):
            self.nextPlayer = 'BLACK'
        else:
            self.nextPlayer = 'WHITE'  

        # Update board.koPoint
        # If only one stone is captured update to board.koPoint
        if (len(capturedStones) == 1):
            self.koPoint = capturedStones
        else:
            self.koPoint = []                 

    def replay(self):
        newboard = Board()
        os.system("clear")
        for (i, j) in self.history:
            newboard.move(newboard.point[i][j])
            newboard.printBoard()
            time.sleep(0.1)	# 1 second delay
            os.system("clear")	# Clear the screen

    def isLegal(self, point):
        capturedStones = []	# Coordinates of captured stones

        # Is the point empty?
        if (point.color != 'EMPTY'):
            return False

        # Is the point leading to repetition?
        if ((point.x, point.y) in self.koPoint):
            return False

        # Is the move suicide?
        neighbours = getNeighbours(point, self)
        isSuicide = True
        myColor = self.nextPlayer 
        enemyColor = 'WHITE' if point.color == 'BLACK' else 'BLACK'
        for pt in neighbours:

            # If the neighbour is empty, isSuicide = false
            if (pt.color == 'EMPTY'):
                isSuicide = False

            # If the neighbour is an ally not in atari, isSuicide = false
            elif (pt.color == myColor) and (inAtari(pt, self) == False):
                isSuicide = False

            # If the neighbour is an enemy in atari, isSuicide = false
            elif (pt.color == enemyColor) and (inAtari(pt, self) == True):
                isSuicide = False

        # If suicide, return false
        if (isSuicide):
            return False
        else:
            return True

    def printBoard(self):
        columnheader = '  '
        for i in range(SIZE):
            columnheader = columnheader + str(i+1) + ' '
        print columnheader
        for i in range(SIZE):
            rowstring = ''
            for j in range(SIZE):
                rowstring = rowstring + COLORDICT[self.point[i][j].color] + ' '
            print str(i+1) + ' ' + rowstring

    def usefulMoves(self):
        usefulmoves = []
        if len(self.history) == 0:
            usefulmoves = [(SIZE/2,SIZE/2),(SIZE/2,SIZE/2 + 1)]
        else:
            [x1, y1] = self.history[len(self.history) - 1] # Last move
            [x2, y2] = self.history[len(self.history) - 2] # Second last move
            libs = getLiberties(x1, y1, self) + getLiberties(x2, y2, self)
            for (i, j) in libs:
                if (i, j) not in usefulmoves:
                    usefulmoves.append((i, j))
        return usefulmoves

    def score(self, color):
        if color == 'WHITE':
            count = self.blackDead
        else:
            count = self.whiteDead
        for x in range(SIZE):
            for y in range(SIZE):   
                pointcolor = self.point[x][y].color
                if pointcolor == color:
                    count += 1
                elif pointcolor == 'EMPTY':
                    surround = 0
                    for neighbour in getNeighbours(self.point[x][y], self):
                        if neighbour.color == color:
                            surround += 1
                    if surround == len(getNeighbours(self.point[x][y], self)): 
                        count += 1
        return count

    # Return false if no legal empty points are left
    def isGameOver(self):
        gameover = True
        for (x, y) in self.emptyPoints:
            if (self.isLegal(self.point[x][y])):
                return False
        return True

    # Returns random empty point
    def randomEmptyPoint(self):
        # Reset board.emptyPoints
        self.emptyPoints = []
        for x in range(SIZE):
            for y in range(SIZE):
                if self.point[x][y].color == 'EMPTY':
                    self.emptyPoints.append((x,y))
        # Return random empty point
        length = len(self.emptyPoints)
        if (length != 0):
            randomindex = random.randint(0, length - 1)
            return self.emptyPoints[randomindex]
 
# Returns a list of neighbours
def getNeighbours(point, board):
    x, y = point.getXY()
    neighbours = []
    for dx, dy in [(0, 1),(1, 0),(0, -1),(-1, 0)]:
        nx, ny =  x + dx, y + dy
        if (0 <= nx < SIZE) and (0 <= ny < SIZE):
            neighbours.append(board.point[nx][ny])
    return neighbours

# Returns a list of empty points (liberties) surrounding a point or group
def getLiberties(x, y, board):
    # Make a clone of the board
    copy = board.cloneBoard()
    liberties = []

    # And call calLiberties with clone
    return calLiberties(x, y, copy, liberties)

def calLiberties(x, y, copy, liberties):
    # Switch color of the point
    oldColor = copy.point[x][y].getColor()
    newColor = 'WHITE' if (oldColor == 'BLACK') else 'BLACK'
    copy.point[x][y].setColor(newColor)

    # And get its neighbours
    neighbours = getNeighbours(copy.point[x][y], copy)

    for pt in neighbours:
        x, y = pt.getXY()
        # If a neighbour is of the same color
        if (pt.color == oldColor):
            # calculate its liberties (call calLiberties)
            # and append them to list 
            for (i,j) in calLiberties(x, y, copy, liberties):
                if (i,j) not in liberties: 
                    liberties.append((i,j))

        # If a neighbour is empty, append to list  
        elif (pt.getColor() == 'EMPTY' and (x,y) not in liberties):
            liberties.append((x, y))

    return liberties

# Returns true if group is in danger of capture (Atari)
# Capture is possible if group has only one liberty (empty point)
def inAtari(point, board):
    liberties = getLiberties(point.x, point.y, board)
    if len(liberties) == 1: 
        return True
    else: 
        return False

# Returns a list of connected points of the same color
def getChainPoints(x, y, board):
    # Make a clone of the board
    copy = board.cloneBoard()

    # Append (x,y) to list
    chain = [(x,y)]

    # Call calChainPoints with clone
    return calChainPoints(x, y, copy, chain)

def calChainPoints(x, y, copy, chain):
    # Switch color of point
    myColor = copy.point[x][y].getColor()
    enemyColor = 'WHITE' if (myColor == 'BLACK') else 'BLACK'
    copy.point[x][y].setColor(enemyColor)

    # And get its neighbours
    neighbours = getNeighbours(copy.point[x][y], copy)

    for pt in neighbours:
        x, y = pt.getXY()
        # If a neighbour is of the same color
        if (pt.getColor() == myColor):
            # Append its coordinate to chain
            chain.append((x,y))
            # And search for its chain points
            # Append new points found to chain
            for (i,j) in calChainPoints(x, y, copy, chain):
                if (i,j) not in chain:
                    chain.append((i,j))

    return chain

class Node():
    def __init__(self, board):
        self.wins = 0
        self.visits = 0
        if (board.history == []):
            self.x, self.y = -1, -1
        else:
            self.x, self.y = board.history.pop()
        self.childNodes = []
        self.siblingNodes = []
    
    def update(self, value):
        self.visits += 1
        self.wins += value
   
    def getWinRate(self):
        if (self.visits > 0):
            return self.wins/self.visits
        else:
            return 0

class UCTTree():
    # Returns child with most visits
    def getBestChild(self, node):
        maxvisits = -1
        for child in node.childNodes:
            if (child.visits > maxvisits):
                bestchild = child
                maxvisits = child.visits
        return bestchild 
    
    # Returns child with best uctvalue
    def UCTSelect(self, node):
        maxuct = -1
        for child in node.childNodes:
            if(child.visits > 0):
                winrate = child.getWinRate()
                uct = C * math.sqrt(math.log(node.visits)/ child.visits)
                uctvalue = winrate + uct
            else:
                # Assign large random uctvalue to unexplored childs           
                uctvalue = 10000 + 1000 * random.random()
            if (uctvalue > maxuct):
                bestchild = child
                maxuct = uctvalue
        return bestchild

    # Plays random moves
    # Returns 1 if black wins, else 0
    def playRandomGame(self, node, board):
        moves = 0
        while moves < MAXMOVES:
            [x, y] = board.randomEmptyPoint()
            board.move(board.point[x][y])
            moves += 1
        if board.score('BLACK') >= board.score('WHITE'):
            return 1
        else:
            return 0
    
    def playSimulation(self, node, board):
        result = 0
        if (node.childNodes == [] and node.visits < 10):
            result = self.playRandomGame(node, board)
        else:
            # If childNodes is empty, fill it
            if (node.childNodes == []):
                self.createChildren(node, board)
            # Select move (next node)
            next = self.UCTSelect(node)
            board.move(board.point[next.x][next.y])
            # Recursive call to playSimulation
            res = self.playSimulation(next, board)
            # Update node
            result = 1 - res
        node.update(1 - result)
        return result

    # Generate child nodes from a parent
    def createChildren(self, parentnode, board):
        # Reset board.emptyPoints
        board.emptyPoints = []
        for x in range(SIZE):
            for y in range(SIZE):
                if board.point[x][y].color == 'EMPTY':
                    board.emptyPoints.append((x,y))
        # Add childNodes
        for (i, j) in board.emptyPoints:
            clone = board.cloneBoard()
            clone.move(clone.point[i][j])
            node = Node(clone)
            node.x, node.y = i, j
            parentnode.childNodes.append(node) 

    # Monte Carlo Tree Search
    def UCTSearch(self, numSim, board):
        root = Node(board)
        if (board.history == []):
            root.x, root.y = SIZE/2, SIZE/2
        else:
            root.x, root.y = board.history.pop()
        self.createChildren(root, board)
       
        copy = board.cloneBoard()
        t = 0
        while t < numSim:
            self.playSimulation(root, copy)
            copy.reset()
            copy = board.cloneBoard()
            t = t + 1
        
        node = self.getBestChild(root)
        return node.x, node.y

def userMove(board):
    while True:
        print '\n'
        text = raw_input('?: ').strip()
        if text == 'p':
            return 'PASS'
        if text == 'q':
            raise EOFError
        try:
            x, y = [int(i) for i in text.split()]
        except ValueError:
            continue
        if not (0 <= x < SIZE and 0 <= y < SIZE):
            continue
        return x,y

def play():
    b = Board()
    n = Node(b)
    t = UCTTree()
    turns = 0
    while turns < 10:

        [x, y] = userMove(b)
        b.move(b.point[x][y])
        os.system('clear')
        b.printBoard()

        [x, y] = t.UCTSearch(15, b)
        b.move(b.point[x][y])
        os.system('clear')
        b.printBoard()

        turns += 1

    print 'WHITE score:', b.score('WHITE')
    print 'BLACK score:', b.score('BLACK')

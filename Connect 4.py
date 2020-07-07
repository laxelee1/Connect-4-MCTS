import numpy as np
import matplotlib.pyplot as plt

#ERROR: IN THE ENDGAME, BECAUSE IT CAN LOOK SO MANY MOVES AHEAD,
#DUE TO MOST NODES BEING TERMINAL OR INVALID,
#THE MATRICES IT CREATES FOR THE TREE ARE TOO MASSIVE.
#NEED A MORE ELEGANT WAY OF EXPANIDNG NODES THAT DOESN'T CREATE HUGE MATRICES
width = 7
height = 6
inarow = 4


class Player():
    def __init__(self, marker):
        self.marker = marker

white = Player(1)
black = Player(-1)

def getWinner(x):
    if x[0] == 0:
        return False
    for i in range(len(x)-1):
        if not x[i+1] == x[0]:
            return False
    return x[0]

class Board():
    def __init__(self, setup = [], a = width, b = height, c = inarow):
        self.width = a
        self.height = b
        self.inarow = c

        self.cells = np.zeros((self.height, self.width))

        self.Turn = white

        self.choices = np.arange(0,self.width)

        self.lastMove = (0,0)

        self.moveHistory = []

        self.gameover = False

        for i in range(len(setup)):
            self.doTurn(setup[i])
            self.switchTurn()

    def switchTurn(self):
        if self.Turn == white:
            self.Turn = black
        else:
            self.Turn = white
    
    def doTurn(self, move):
        for i in range(self.height):
            if not self.cells[0][move] == 0:
                print('Invalid Move')
                print('Move History:')
                print(self.moveHistory + [move])
                print('\n')
                print('self.choices')
                print(self.choices)
                print('\n\n\n')
                raise Exception('InvalidMove')
            if i+1 == self.height:
                self.cells[i][move] = self.Turn.marker
                self.lastMove = (i,move)
                self.moveHistory.append(move)
                return True
            if not self.cells[i+1][move] == 0:
                self.cells[i][move] = self.Turn.marker
                self.lastMove = (i,move)
                self.moveHistory.append(move)
                if i == 0:
                    choices = []
                    for j in range(len(self.choices)):
                        if not self.choices[j] == move:
                            choices.append(self.choices[j])
                    self.choices = np.array(choices)
                return True

    def display(self):
        plt.imshow(self.cells)
        plt.show()

    def hasWon(self):
        y = self.lastMove[0]
        x = self.lastMove[1]
        L = self.inarow
        right = self.width - 1
        bottom = self.height - 1
        #diagonaldownwards
        for i in range(L):
            for j in range(L):
                if not 0<=y-i+j<=bottom:
                    break
                if not 0<=x-i+j<=right:
                    break
            else:
                cells = [self.cells[y-i+j][x-i+j] for j in range(L)]
                winner = getWinner(cells)
                if not winner:
                    continue
                return winner
        #diagonalupwards
        for i in range(L):
            for j in range(L):
                if not 0<=y+i-j<=bottom:
                    break
                if not 0<=x-i+j<=right:
                    break
            else:
                cells = [self.cells[y+i-j][x-i+j] for j in range(L)]
                winner = getWinner(cells)
                if not winner:
                    continue
                return winner
        #horizontal
        for i in range(L):
            for j in range(L):
                if not 0<=x-i+j<=right:
                    break
            else:
                cells = [self.cells[y][x-i+j] for j in range(L)]
                winner = getWinner(cells)
                if not winner:
                    continue
                return winner
        #vertical
        for i in range(L):
            for j in range(L):
                if not 0<=y-i+j<=bottom:
                    break
            else:
                cells = [self.cells[y-i+j][x] for j in range(L)]
                winner = getWinner(cells)
                if not winner:
                    continue
                return winner
        return False

    def isFull(self):
        for i in range(self.width):
            if self.cells[0][i] == 0:
                return False
        return True
        
    def playout(self):
        winner = self.hasWon()
        if winner:
            #self.display()
            return winner, True
        if len(self.choices) == 0:
            #self.display()
            return winner, True
        while True:
            n = np.random.choice(self.choices)
            #print('move =',n)
            turn = self.doTurn(n)
            self.switchTurn()
            winner = self.hasWon()
            if winner:
                #self.display()
                return winner, False
            if len(self.choices) == 0:
                #self.display()
                return 0, False

def getIndexMax(x):
    maximum = x[0]
    index = 0
    for i in range(len(x)-1):
        if x[i+1] > maximum:
            maximum = x[i+1]
            index = i+1
    return index

class Tree():
    '''Each Tree is a list of Trees'''
    def __init__(self, move=[], parents=[], children=[], setup=[], wins=0, sims=0, term=False):
        self.setup = setup
        self.move = move
        self.path = parents + move
        self.wins = wins
        self.sims = sims
        self.term = term
        self.parents = parents
        self.children = []
        for i in children:
            self.add_valid_child(i)
    def __repr__(self):
        return 'Move ' + str(self.move)
    
    def add_valid_child(self, child):
        '''Assert that child is a valid move'''
        assert isinstance(child, Tree)
        if not child.parents == self.parents + self.move:
            print('child.parents =',child.parents)
            print('self.parents =',self.parents)
            print('self.move =',self.move)
            raise Exception('InheritanceError')
        assert self.term == False
        self.children.append(child)

    def getKids(self):
        t = self
        kids = []
        for child in t.children:
            kids.append(child.move[0])
        return kids

    def getInfo(self, path):
        '''Get wins, sims, term and children'''
        t = self
        for move in path:
            kids = t.getKids()
            if not move in kids:
                raise Exception('MissingChildren')
            index = kids.index(move)
            t = t.children[index]
        no_kids = len(t.children)
        kids = [t.children[i].move[0] for i in range(no_kids)]
        return t.wins, t.sims, t.term, kids
    
    def setInfoRecur(self, path, wins=False, sims=False, term=False, newmoves=[]):
        #return updated tree
        #updated tree = old tree, but with updated affected branches
        t = self
        if len(path) == 0:
            if sims:
                t.sims += 1
            if wins:
                t.wins += 1
            if term:
                t.term = term
            for move in newmoves:
                t.add_valid_child(Tree([move], t.path, setup=t.setup))
            return t
        kids = t.getKids()
        index = kids.index(path[0])
        updated_path = path[1:]
        update = t.children[index].setInfoRecur(updated_path, wins, sims, term, newmoves)
        t.children[index] = update
        return t
    def setInfo(self, path, wins=False, sims=False, term=False, newmoves=[]):
        self = self.setInfoRecur(path, wins, sims, term, newmoves)

    def backpropagateRecur(self, path, result, term):
        #return updated tree
        #updated tree = old tree, but with updated
        def update(flip = False):
            t.sims += 1
            if not len(t.parents + t.move)%2 == 0:
                if result == 1:
                    t.wins += 1
                elif result == 0:
                    t.wins += 0.5
            else:
                if result == -1:
                    t.wins += 1
                elif result == 0:
                    t.wins += 0.5
        t = self
        if len(path) == 0:
            t.term = term
            update()
            return t
        update()
        kids = t.getKids()
        index = kids.index(path[0])
        updated_path = path[1:]
        update = t.children[index].backpropagateRecur(updated_path, result, term)
        t.children[index] = update
        return t
    def backpropagate(self, path, result, term):
        self = self.backpropagateRecur(path, result, term)

    def selection(self, path):
        #if leaf
            #no playout
                #do a playout
                #get result
                #backpropagate, including terminality
                ##return root node, new tree
            #else
                #if terminal
                    #backpropagate
                    ##return root node, new tree
                #else
                    #expand nodes below
                    #mark as not leaf
                    ##return first valid child node, new tree
        #else
            ##return valid child node with highest UCB1, new tree
        flip = False
        if not len(self.setup)%2 == 0:
            flip = True
        b = Board(self.setup + path)
        wins, sims, term, children = self.getInfo(path)
        if len(children) == 0:
            if sims == 0:
                result, term = b.playout()
                if flip:
                    result = -result
                #print('result =',result)
                t.backpropagate(path, result, term)#fix what's backpropagating
                return []
            else:
                if term:
                    result, term = b.playout()
                    if flip:
                        result = -result
                    #print('result =',result)
                    t.backpropagate(path, result, term)
                    return []
                else:
                    for i in range(width):
                        next_move = b.choices[0]
                        if i in b.choices:
                            self.setInfo(path, newmoves=[i])
                    return path + [next_move]
        else:
            #print('sims =',sims)
            #print('options are:')
            #for i in children:
                #w,n,te,c = self.getInfo(path + [i])
                #if n is not 0:
                #    calc = 'UCB1 = '+str(w/n + np.sqrt(2)*np.sqrt(np.log(sims)/n))+'\n'
                #else:
                #    calc = 'UCB1 = infinite\n'
                #print((w,n,te,c), end=calc)
            no_moves = len(children)
            w = np.zeros(no_moves)
            n = np.zeros(no_moves)
            c = np.sqrt(2)
            N = sims

            for index, e in enumerate(children):
                iwins, isims = self.getInfo(path + [e])[0:2]
                if isims == 0:
                    return path + [e]
                w[index] = iwins
                n[index] = isims

            UCB1 = w/n + c*np.sqrt(np.log(N)/n)
            next_move = getIndexMax(UCB1)
            return path + [children[next_move]]

            #return path + children[]
            #find which index of w that has highest UCB1, then index children 

    def getMove(self, no_sims=1000):
        next_node = []
        while True:
            next_node = self.selection(next_node)
            sims = self.getInfo([])[1]
            if sims == no_sims+1:
                break
        children = self.getKids()
        n = np.zeros((width))
        for i in children:
            n[i] = self.getInfo([i])[1]
        move = getIndexMax(n)
        print(n)
        return move


def do():
    global next_node
    next_node = t.selection(next_node)
    print('next_node =',next_node)

def nice(path):
    w,n,te,c = t.getInfo(path)
    if n is not 0:
        calc = 'UCB1 = '+str(w/n + np.sqrt(2)*np.sqrt(np.log(t.getInfo(path[:-1])[1])/n))+'\n'
    else:
        calc = 'UCB1 = infinite\n'
    print((w,n,te,c), end=calc)

def deepnice(path):
    for i in range(width):
        nice(path+[width])

while True:
    try:        
        difficulty = input('What difficulty? (default = 1000)    ')
        if difficulty == '':
            difficulty = 1000
            break
        difficulty = int(difficulty)
        break
    except:
        print('InvalidInput')
while True:
    goFirst = input('Do you want to go first?    ')
    if goFirst == 'yes':
        break
    if goFirst == 'no':
        break 
z = []
if goFirst == 'no':
    t = Tree(setup=z)
    MCTSmove = t.getMove(difficulty)
    print('MCTS move is', MCTSmove)
    z += [MCTSmove]
    b = Board(z)
    b.display()
while True:
    while True:
        try:
            playerMove = int(input("What's your move?    "))
            assert 0<=playerMove<width
            testboard = Board(z)
            assert playerMove in testboard.choices
            break
        except:
            print('InalidInput')
    z += [playerMove]
    b = Board(z)
    tempboard = b
    if tempboard.playout()[1]:
        winner = b.hasWon()
        if winner:
            print('YOU WIN')
        else:
            print('DRAW')
        break
    t = Tree(setup=z)
    MCTSmove = t.getMove(difficulty)
    print('MCTS move is', MCTSmove)
    z += [MCTSmove]
    b = Board(z)
    b.display()
    tempboard = b
    if tempboard.playout()[1]:
        winner = b.hasWon()
        if winner:
            print('YOU LOSE')
        else:
            print('DRAW')
        break

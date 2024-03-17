import math
import matplotlib.pyplot as plt
import random

class MiniSpecies:
    def __init__(self, timeSeedToAdult, percentSeedToAdult, averageAdultTime, percentAdultAlive, numberSeeds):
        self.t1 = timeSeedToAdult
        self.p1 = percentSeedToAdult
        self.pp1 = math.e ** (math.log(self.p1) / self.t1)
        self.p2 = averageAdultTime
        self.ll = percentAdultAlive
        self.pp2 = math.e ** (math.log(self.ll) / self.p2)
        self.n = numberSeeds
        
class MiniSeed:
    def __init__(self, species):
        self.age = 0
        self.t1 = species.t1
        self.p = species.pp1
        self.species = species
        
    def update(self):
        sp = random.random()
        if (sp > self.p):
            return "yoo"
        else:
            self.age += 1
            if (self.age > self.t1):
                return MiniAdult(self.species, self.age)
            return self
        
class MiniSeedArray:
    def __init__(self):
        self.store = []
        
    def update(self):
        for i in range(len(self.store)):
            new = self.store[i].update()
            if (type(new) == MiniAdult):
                return new
            else:
                self.store[i] = new
        self.store = [item for item in self.store if item != "yoo"]
        return self
    
    def addSeed(self, seed):
        self.store.append(seed)
        
    def removeSeed(self, index):
        temp = self.store.pop(index)
        
    def getStore(self):
        return self.store
    
class MiniAdult:
    def __init__(self, species, age):
        self.age = age
        self.species = species
        self.n = species.n
        self.p = species.pp2
        
    def update(self):
        sp = random.random()
        if (sp > self.p):
            return "yas" # dead
        else:
            self.age += 1
            seeds = MiniSeedArray()
            for _ in range(self.n):
                seeds.addSeed(MiniSeed(self.species))
            return seeds
    
class MiniBoard:
    def __init__(self, size, maxtime, startspawn, species):
        self.size = size
        self.board = [[MiniSeedArray() for _ in range(size)] for _ in range(size)]
        self.ctime = 0
        self.mtime = maxtime
        self.species = species
        for _ in range(startspawn):
            newx = random.randint(0, size - 1)
            newy = random.randint(0, size - 1)
            self.board[newx][newy].addSeed(MiniSeed(self.species))
            
    def step(self):
        for i in range(self.size):
            for j in range(self.size):
                new = self.board[i][j].update()
                if (new == "yas"):
                    self.board[i][j] = MiniSeedArray()
                elif (type(new) == MiniAdult):
                    self.board[i][j] = new
                elif (type(new) == MiniSeedArray):
                    if (type(self.board[i][j] == MiniAdult)):
                        ran = [-2, -1, 0, 1, 2]
                        for seed in new.store:
                            newx = i + random.choice(ran)
                            newy = j + random.choice(ran)
                            if (newx < self.size and newy < self.size and newx >= 0 and newy >= 0):
                                if (type(self.board[newx][newy]) == MiniSeedArray):
                                    self.board[newx][newy].addSeed(seed)
                    else:
                        self.board[i][j] = new
                        
    def run(self):
        while (self.ctime < self.mtime):
            self.ctime += 1
            self.step()
        return self.board
    
    def visboard(self):
        printedBoard = [[0 for _ in range(self.size)] for _ in range(self.size)]
        for i in range(self.size):
            for j in range(self.size):
                if (type(self.board[i][j]) == MiniAdult):
                    printedBoard[i][j] = 1
        plt.imshow(printedBoard, cmap='hot', interpolation='nearest')
        plt.colorbar()
        plt.show()
        return "Visualization with the \"hot\" heatmap."
    
    def checkseeds(self):
        printedBoard = [[0 for _ in range(self.size)] for _ in range(self.size)]
        for i in range(self.size):
            for j in range(self.size):
                if (type(self.board[i][j]) == MiniSeedArray):
                    printedBoard[i][j] = len(self.board[i][j].store)
        plt.imshow(printedBoard, cmap='hot', interpolation='nearest')
        plt.colorbar()
        plt.show()
        return "Visualization with the \"hot\" heatmap."
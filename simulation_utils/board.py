"""This module defines the Tile and Board classes."""
import random
import numpy as np
import dill as pickle
import matplotlib.pyplot as plt

from species import SpeciesList
from plants import Juvenile
from plants import Adult
from plants import PlantArray

class Tile:
    """
    Tile class. Represents a Tile on the Board.

    Attributes:
        neighbourData (dict): Dictionary containing {speciesID: count} of the neighboring tiles.
        plantArray (PlantArray): A PlantArray object storing the Plant objects on the current tile.

    Methods:
        updateData() -> 'Tile'
        update(neighborData: dict) -> tuple
    """
    def __init__(self, storageLimit : int):
        self.neighbourData = {}
        self.plantArray = PlantArray(storageLimit)

    def updateData(self) -> 'Tile':
        """
        Updates the dictionary containing the number of Adult trees on the Tile.
        """
        self.neighbourData = self.plantArray.dictionaryFormat
        return self

    def update(self, neighborData: dict,
              boomerModel : bool) -> tuple: # TODO
        """
        Updates the Plant objects stored on this tile, using the neighbor data.

        Args:
            neighborData (dict): A dictionary containing the list of adult neighbors.
            boomerModel (bool): If True, this is the boomer model. If False, it is the
                age-structured model.

        Returns:
            tuple: The first element is a 'Tile' object and the second element is a
                PlantArray containing the Juvenile objects produced.
        """
        newPlantArray = self.plantArray.update(neighborData)
        self.plantArray = newPlantArray
        self.updateData()
        newSeeds = self.plantArray.produceSeeds(boomerModel)
        return self, newSeeds

class Board:
    """
    Board class. A Board is comprised of many Tile objects, and can be updated.

    Attributes:
        speciesList (SpeciesList): SpeciesList containing the Species present on the Board.
        boardLength (int): Length of the Board.
        board (list): Nested list containing the Tile objects.

    Methods:
        loadBoard(filepath: str) -> 'Board'
        saveBoard(filepath: str) -> None
        loadSpecies(filepath: str) -> None
        printBoard() -> None
        printSpecies(speciesID: int) -> None
        makeNeighborDicts() -> list
        update() -> 'Board'
        clearBoard() -> 'Board'
    """
    def __init__(self, speciesList: SpeciesList, boardLength: int, 
                storageLimit : int, startNumber : int,
                boomerModel : bool,
                stdev : int, 
                printFreq : int):
        self.speciesList = speciesList
        self.boardLength = boardLength
        self.boardTime = 0
        self.storageLimit = storageLimit
        self.boomerModel = boomerModel
        self.board = [[Tile(self.storageLimit) for _ in range(self.boardLength)] for _ in range(self.boardLength)]
        self.seedBoard = [[PlantArray(storageLimit) for _ in range(self.boardLength)]
                          for _ in range(self.boardLength)]
        
        self.startNumber = startNumber
        self.printFreq = printFreq
        for i in range(len(self.speciesList.species)):
            if (self.boomerModel): # generate unique coordinates to populate the board
                coords = set()
                while len(coords) < self.startNumber:
                    coords.add((np.random.randint(0, self.boardLength - 1), 
                                np.random.randint(0, self.boardLength - 1)))
                for coord in coords:
                    x, y = coord
                    self.seedBoard[x][y].addAdult(Adult(self.speciesList.species[i], 0))
            else:
                for j in range(self.startNumber):
                    startX = random.randint(0, self.boardLength - 1)
                    startY = random.randint(0, self.boardLength - 1)
                    self.seedBoard[startX][startY].addPlant(Juvenile(self.speciesList.species[i], 0))

        self.stdev = stdev
        self.mean = [0, 0]
        self.cov = [[self.stdev**2, 0], [0, self.stdev**2]]

    def loadBoard(self, filepath: str) -> 'Board':
        """
        Loads a Board object from a file. Uses the Dill module in Python.

        Args:
            filepath (str): The filepath the Board is loaded from.

        Returns:
            self. The Board stored inside the given filepath.
        """
        returnBoard = None
        with open(filepath, 'rb') as file:
            returnBoard = pickle.load(file)
        return returnBoard

    def saveBoard(self, filepath: str) -> None:
        """
        Saves a Board object to a file. Uses the Dill module in Python.

        Args:
            filepath (str): The filepath to store the Board at.
        """
        with open(filepath, 'wb') as file:
            pickle.dump(self, file)

    def loadSpecies(self, filepath: str) -> 'Board':
        """"
        Loads a dictionary of Species from a file.
        """
        self.speciesList = self.speciesList.loadSpeciesData(filepath)
        return self

    def printBoard(self, boardTime: int) -> None:
        """
        Prints a Board object as a heatmap. The colours on the heatmap represent the Species of the
        Adult trees on the Board.
        """
        printedBoard = [[-1 for _ in range(self.boardLength)] for _ in range(self.boardLength)]
        for i in range(self.boardLength):
            for j in range(self.boardLength):
                if self.board[i][j].plantArray.hasAdult:
                    printedBoard[i][j] = self.board[i][j].plantArray.currentAdult.species.speciesID
        plt.imshow(printedBoard, cmap=plt.get_cmap("tab20c", len(self.speciesList.species) + 2),
                   interpolation='nearest', vmin = -1, vmax = len(self.speciesList.species) + 1)
        if boardTime == 1:
            plt.colorbar()
#         plt.show()
        outputName = str(boardTime) + ".png"
        plt.savefig(outputName)

    def printSpecies(self, speciesID: int) -> None:
        """
        Displays the positions of a single Species on the Board.

        Args:
            speciesID (int): Only Adult trees of the given Species are displayed.
        """
        printedBoard = [[0 for _ in range(self.boardLength)] for _ in range(self.boardLength)]
        for i in range(self.boardLength):
            for j in range(self.boardLength):
                if ((self.board[i][j].plantArray.hasAdult) and
                    (self.board[i][j].plantArray.currentAdult.species == speciesID)):
                    printedBoard[i][j] = 1
        plt.imshow(printedBoard, cmap='hot', interpolation='nearest')
        plt.colorbar()
        plt.show()

    def makeNeighborDicts(self) -> list:
        """
        Generates a nested list storing the neighbor dictionaries for each Tile on the Board.
        Uses recursive mergeDict() function from PlantArray
        
        Future optimisation can involve Search and cumulative algorithms involving demergeDict()
        """
        returnList = [[0 for _ in range(self.boardLength)] for _ in range(self.boardLength)]
        for i in range (self.boardLength):
            for j in range(self.boardLength):
                newDict = {}
                positions = [[i - 1, j - 1], [i- 1, j], [i - 1, j + 1],
                             [i, j - 1], [i, j], [i, j + 1],
                             [i + 1, j - 1], [i + 1, j], [i + 1, j + 1]]
                for position in positions:
                    # check within boundary
                    if ((position[0] > -1) and (position[0] < self.boardLength) and
                        (position[1] > -1) and (position[1] < self.boardLength)):
                        newDict = (self.board[position[0]][position[1]].plantArray.
                                             mergeDict(newDict, self.boomerModel))
                returnList[i][j] = newDict
        return returnList

    def saveNeighborDicts(self, boardTime : int, boomerModel : bool) -> list:
        """
        Same as makeNeighborDicts, but this time we need to include saving the counts as well
        """
        exportData = self.speciesList.storage.copy(deep = True)
        exportData['Adult'] = 0
        exportData['Juvenile'] = 0
        returnList = [[0 for _ in range(self.boardLength)] for _ in range(self.boardLength)]
        for i in range (self.boardLength):
            for j in range(self.boardLength):
                exportDict = self.board[i][j].plantArray.neighborDict
                for speciesID, countList in exportDict.items():
                    exportData.loc[exportData['speciesID'] == speciesID, 'Adult'] += countList[0]
                    exportData.loc[exportData['speciesID'] == speciesID, 'Juvenile'] += countList[1]

                newDict = {}
                positions = [[i - 1, j - 1], [i- 1, j], [i - 1, j + 1],
                             [i, j - 1], [i, j], [i, j + 1],
                             [i + 1, j - 1], [i + 1, j], [i + 1, j + 1]]
                for position in positions:
                    if ((position[0] > -1) and (position[0] < self.boardLength) and
                        (position[1] > -1) and (position[1] < self.boardLength)): # check within boundary
                        newDict = (self.board[position[0]][position[1]].plantArray.
                                   mergeDict(newDict, self.boomerModel))
                returnList[i][j] = newDict
        saveName = str(boardTime) + ".csv"                                                  
        exportData.to_csv(saveName, index=False)
        return returnList


    def update(self) -> 'Board':
        """
        Updates the Board object. Neighbor dictionaries are first created for each Tile on the
        Board. Following that, each Tile is updated using the neighbor dictionary associated
        with it. New seeds are then distributed to the PlantArray objects in self.seedBoard.
        Once all Tile objects have been updated, the new seeds from self.seedBoard are added
        to the Tile object.
        
        Return:
            self.
        """
        
        if (((self.boardTime - 1) % self.printFreq) == 0): # steal state every 100 timesteps
            newNeighborDicts = self.saveNeighborDicts(self.boardTime, self.boomerModel)
            self.printBoard(self.boardTime)
        else:
            newNeighborDicts = self.makeNeighborDicts()
            
        self.boardTime += 1
        
        for i in range(self.boardLength):
            for j in range(self.boardLength):
                tileUpdate = self.board[i][j].update(newNeighborDicts[i][j],
                                                    self.boomerModel)       # (Tile, PlantArray)
                self.board[i][j] = tileUpdate[0]                                   # update Tile
                newSeeds = tileUpdate[1]                                           # PlantArray of interest

                for k in range(len(newSeeds.storage)):                             # list of Plants
#                     newX = random.choice([-1, 0, 1])
#                     newY = random.choice([-1, 0, 1])
                    newX, newY = np.round(np.random.multivariate_normal(self.mean, self.cov, 1))[0] # binomial normal distribution
                    newX = int(newX)
                    newY = int(newY)
                    if ((i + newX > -1) and (i + newX < self.boardLength) and
                        (j + newY > -1) and (j + newY < self.boardLength)):
                        self.seedBoard[i + newX][j + newY].addPlant(newSeeds.storage[k]) # This line ensures
                                                                                         # boomerModel with 
                                                                                         # PlantArray of Adult
                                                                                         # will not overflow
                        
        for i in range(self.boardLength):
            for j in range(self.boardLength):
                self.board[i][j].plantArray.mergeArray(self.seedBoard[i][j]) # mergeArray allows addition of an Adult
                                                                             # if the board itself does not have an Adult yet
                self.seedBoard[i][j] = self.seedBoard[i][j].clear()
        return self

    def clearBoard(self) -> 'Board':
        """
        Clears all Tile objects on the Board (effectively making a new Board).

        Return:
            'Board': An empty Board object.
        """
        return Board(self.speciesList, self.boardLength, self.storageLimit, self.startNumber)

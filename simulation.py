#!/usr/bin/env python
# coding: utf-8
# %%

# %%


"""Module containing all simulation tools."""


# %%


import math
import random
import dill as pickle
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# Current Issues

# 1. I think that there will be some funky business with the SpeciesID if we're making new Species
# instances to test out stuff, because loading a Species dictionary into SpeciesList does not
# actually update the speciesID of Species. One potential fix is to make sure that Species.speciesID
# gets updated as well every time we load a new dict of Species.
# 
#     - Maybe to handle this we can let speciesID be a property of SpeciesList rather than Species, so the creation of any Species will have to refer back to SpeciesList to obtain the property

# 2. The neighborData dictionary currently used by the PlantArray and Tile classes is currently
# configured to store SpeciesID as keys, and the number of Adult trees of that species as the value.
# We might want to consider updating this in the future so the values in the dictionary are a list
# storing the number of seeds, juveniles, and adults of that species.

# 3. I am currently using the dill module to save and load the Board, and I am not sure how exactly
# it works. It might be good to eventually move away from the dill module.
# (Note: I haven't tested the dill module as of 10/03/2024)

# 4. Speciation has not been added yet.

# %%


class Species:
    """
    Species class.
    Meant to act as a storage for all data of a Species.

    Attributes: all other attributes are described in the constructor of this class.
        speciesID (int): A class variable that numbers the different Species generated.
        seedPerTick (float): The probability of surviving one tick as a Seed of this Species.
        adultPerTick (float): The probability of surviving one tick as an Adult of this Species.

    Methods:
        getDataAsDict() -> dict
    """
    speciesID = 1

    def __init__(self, parentID: int, p1: float, p2: float, t1: int, t2: int,
                 t3: int, ns: int, conNDD: float, hetNDD: float):
        """
        Initialize a new instance of Species.

        This constructor initializes a new instance of Species with the provided parameters.

        Args:
            parentID (int): Species ID of the parent Species. To be used for speciation events.
            p1 (float): The probability that a Seed of this Species makes it to an adult.
            p2 (float): The probability that an Adult of this Species is alive, given that
                t2 timesteps have passed.
            t1 (int): The number of timesteps required for a Seed to become an Adult.
            t2 (int): The number of timesteps used for calculations with
                p2. Set arbitrarily by the user.
            t3 (int): The number of timesteps required for an Adult of this Species to start
                producing Seed objects.
            ns (int): The number of Seed objects produced by an Adult of this Species every tick.
            CNDD (float): The magnitude of CNDD effects on this Species.
            HNDD (float): The magnitude of HNDD effects on this Species.
        """
        self.speciesID = Species.speciesID
        self.parentID = parentID
        self.t1 = t1
        self.p1 = p1
        self.seedPerTick = math.e ** (math.log(self.p1) / self.t1)          # or self.pi ** (1/self.ti)
        self.t2 = t2
        self.p2 = p2
        self.adultPerTick = math.e ** (math.log(self.p2) / self.t2)         # or self.p2 ** (1/self.t2)
        self.ns = ns
        self.conNDD = conNDD
        self.hetNDD = hetNDD
        Species.speciesID += 1

    def getDataAsDict(self) -> dict:
        """
        Stores a Species object in dictionary format.

        Returns:
            dict: Species data stored as a dictionary.
        """
        returnDict = {"speciesID": self.speciesID, "parentID": self.parentID, "t1": self.t1,
                      "p1": self.p1, "seedPerTick": self.seedPerTick, "t2": self.t2, "p2": self.p2,
                      "adultPerTick": self.adultPerTick, "ns": self.ns, "CNDD": self.conNDD,
                      "HNDD": self.hetNDD}
        return returnDict


# %%


class SpeciesList:
    """
    SpeciesList class.
    Meant to act as a master storage list for all Species objects and their associated data.

    Attributes:
        columnNames (list): class-level attribute containing the column names for saving the data
            to a file.
        storage (pandas.DataFrame): A Pandas DataFrame storing each Species as a column. 
        species (list): Python list storing every added Species object to an instance of SpeciesList

    Methods:
        addSpecies(species: Species) -> SpeciesList
        mergeSpeciesList(newList: SpeciesList) -> SpeciesList
        loadSpeciesData(filepath: str) -> None
        saveSpeciesData(filepath: str) -> None
    """
    columnNames: list = ["speciesID", "parentID", "t1", "p1", "seedPerTick", "t2", "p2",
                         "adultPerTick", "ns", "CNDD", "HNDD"]

    def __init__(self):
        self.storage = pd.DataFrame(columns=SpeciesList.columnNames)
        self.species = []

    def addSpecies(self, species: Species) -> 'SpeciesList':                 
        """
        Adds a Species object to the SpeciesList storage. Converts the new Species object
        into a Pandas DataFrame and merges it into the SpeciesList storage DataFrame.

        Args:
            species (Species): A new Species object.

        Returns:
            self.
        """
        try:
            newSpecies = pd.DataFrame(species.getDataAsDict(), index=[0])
            self.storage = pd.concat([self.storage, newSpecies], ignore_index=True)
            self.species.append(species)
            print("Species " + str(species.speciesID) + " added.")
            return self
        except ValueError:
            print("Error adding Species.")
            return self

    def mergeSpeciesList(self, newList: 'SpeciesList') -> 'SpeciesList':
        """
        Merges a new SpeciesList into an existing SpeciesList. This merges the Pandas DataFrame
        of both SpeciesList objects, and discards duplicate rows.

        Args:
            newList (SpeciesList): Another SpeciesList object.
        
        Returns:
            self.
        """
        newStorage = pd.concat([self.storage, newList.storage], ignore_index=True)
        self.species.extend([sp for sp in newList.species if sp not in self.species])
        self.storage = newStorage.drop_duplicates()
        return self

    def loadSpeciesData(self, filepath: str) -> None:
        """
        Loads the Species data from a file.

        Args:
            filepath (str): Filepath, including the file extension. For example, "test.csv".
        """
        try:
            self.storage = pd.read_csv(filepath)
            print("Species data loaded successfully.")
        except FileNotFoundError:
            print("File not found! Please check that you have" +
                   "provided the full filepath e.g., \"test.csv\" ")

    def saveSpeciesData(self, filepath: str) -> None:
        """
        Saves the Species data to a file.

        Args:
            filepath (str): Filepath, including the file extension. For example, "test.csv".
        """
        try:
            self.storage.to_csv(filepath, index=False)
            print("File saved successfully.")
        except FileNotFoundError:
            print("File not found! Please check that you have" +
                   "provided the full filepath e.g., \"test.csv\" ")


# %%


class Plant:
    """
    Parent class for all Plant objects. Contains several generic methods to be overridden.

    Attributes:
        species (Species): the Species of this Plant.
        age (int): the current age of the Plant, i.e, the number of timesteps it has survived for.

    Methods:
        calculateNDD(cNeighbors: int, hNeighbors: int) -> float
        updateTick(cNeighbors: int, hNeighbors: int) -> bool
        update() -> 'Plant'
    """
    def __init__(self, species: Species, age: int=0): # pass the Species object into the constructor
        """
        Initialize a new instance of Plant.

        This constructor initializes a new instance of Plant with the provided parameters.

        Args:
            species (Species): The Species of the Plant.
            age (int): The current age of the Plant.
        """
        self.species = species
        self.age = age

    def calculateNDD(self, cNeighbors: int, hNeighbors: int) -> float:
        """
        Calculates the NDD effect exerted by the neighbors of a Plant.

        Args:
            cNeighbors (int): Number of neighboring Adult conspecifics.
            hNeighbors (int): Number of neighboring Adult heterospecifics.

        Returns:
            float: Decrease in probability of survival for a single tick.
        """
        return (0 * cNeighbors) + (0 * hNeighbors)

    def updateTick(self, cNeighbors, hNeighbors) -> bool:
        """
        Checks if the Plant survives the current tick.

        Args:
            cNeighbors (int): Number of neighboring Adult conspecifics.
            hNeighbors (int): Number of neighboring Adult heterospecifics.

        Returns:
            bool: True if the Plant survives this tick, False otherwise.
        """
        return random.random() <= 1 - self.calculateNDD(cNeighbors, hNeighbors)

    def update(self, cNeighbors, hNeighbors) -> 'Plant':
        """
        Checks if the Plant grows to the next stage of life or remains at the current stage.

        Returns:
            Plant: Returns self if it remains at the same stage of life, or a new
                Plant object if it grows.
        """
        if self.updateTick(cNeighbors, hNeighbors):
            self.age += 1
            return self
        return None


# %%


class Juvenile(Plant):
    """
    Juvenile class that inherits from the Plant class. All three methods are overriden.
    Further method descriptions are available in the Plant class above.

    Methods:
        calculateNDD(cNeighbors: int, hNeighbors: int) -> float
        updateTick(cNeighbors: int, hNeighbors: int) -> bool
        update() -> 'Plant'
    """
    def __init__(self, species: Species, age: int):
        super().__init__(species, age)

    def calculateNDD(self, cNeighbors, hNeighbors) -> float:
        """
        The multipliers used are currently arbitrary.
        """
        return (2 * cNeighbors * self.species.conNDD) + (2 * hNeighbors * self.species.hetNDD)

    def updateTick(self, cNeighbors, hNeighbors) -> bool:
        return (random.random() <=
                self.species.seedPerTick - self.calculateNDD(cNeighbors, hNeighbors))

    def update(self, cNeighbors, hNeighbors) -> Plant:
        if self.updateTick(cNeighbors, hNeighbors):
            self.age += 1
            if self.age >= self.species.t1:
                return Adult(self.species, self.age) # Grows to an Adult
            return self # Remains a Juvenile
        return DeadPlant(self.species, self.age) # Dies


# %%


class Adult(Plant):
    """
    Adult class that inherits from the Plant class. All three methods are overriden.
    Further method descriptions are available in the Plant class above.

    Methods:
        calculateNDD(cNeighbors: int, hNeighbors: int) -> float
        updateTick(cNeighbors: int, hNeighbors: int) -> bool
        update(cNeighbors: int, hNeighbors: int) -> 'Plant'
    """
    def __init__(self, species: Species, age: int):
        super().__init__(species, age)

    def calculateNDD(self, cNeighbors: int, hNeighbors: int) -> float:
        """
        The multipliers used are currently arbitrary.
        """
        return (1 * cNeighbors * self.species.conNDD) + (1 * hNeighbors * self.species.hetNDD)

    def updateTick(self, cNeighbors: int, hNeighbors: int) -> bool:
        return (random.random() <=
                self.species.adultPerTick - self.calculateNDD(cNeighbors, hNeighbors))

    def update(self, cNeighbors, hNeighbors) -> Plant:
        if self.updateTick(cNeighbors, hNeighbors):
            self.age += 1
            return self # Remains an Adult
        return DeadPlant(self.species, self.age) # Dies


# %%


class DeadPlant(Plant):
    """
    DeadPlant class that inherits from the Plant class. This is meant to be a filler class,
    with all DeadPlant class objects deleted as soon as possible. Hence, it has no methods.
    """
    def __init__(self, species: Species, age: int):
        super().__init__(species, age)


# %%


class PlantArray:
    """
    PlantArray class. Contains a list of Plant objects.

    Attributes:
        hasAdult (bool): True if the PlantArray contains an Adult object, False otherwise.
        currentAdult (Adult): Stores the current Adult of the PlantArray. There can only
            be one Adult at a time.
        storage (list): List of Plant objects. Soft capped at 50.

    Methods:
        addPlant(plant: Plant) -> 'PlantArray'
        mergeArray(newArray: 'PlantArray') -> 'PlantArray'
        produceSeeds() -> list
        update(neighborDict: dict) -> 'PlantArray'
        toDict() -> dict
    """
    def __init__(self):
        self.hasAdult = False
        self.currentAdult = None
        self.storage = []

    def addPlant(self, plant: Plant) -> 'PlantArray':
        """
        Adds a Plant object to the PlantArray. If the new Plant object is an Adult and
        the PlantArray already has an Adult, the new Plant is not added.

        Args:
            plant (Plant): New Plant object.

        Returns:
            self.
        """
        if (isinstance(plant, Adult) and self.hasAdult):              # if we already have an adult, do not add
            return self
        if (len(self.storage) >= 50):                                 # if we are full on capacity
            if (isinstance(plant, Adult)):                            # but you want to add an adult
                self.storage[random.randint(0, len(self.storage)-1)] = plant     # randomly replace one with an adult
                self.hasAdult = True
                self.currentAdult = plant
            return self                                               # otherwise, you don't get added
        if isinstance(plant, Adult):                                  # if not full capacity and it's an adult
            self.hasAdult = True
            self.currentAdult = plant
        self.storage.append(plant)
        return self

    def mergeArray(self, newArray: 'PlantArray') -> 'PlantArray':
        """
        Merges two PlantArray objects together. If both the old and new PlantArray objects have
        an Adult, then the new PlantArray is not added and the original PlantArray is returned.

        Args:
            newArray (PlantArray): New PlantArray object.

        Returns:
            self.
        """

        if (self.hasAdult and newArray.hasAdult):
            return self
        selfCopy = self
        for otherPlant in newArray.storage:
            selfCopy = selfCopy.addPlant(otherPlant)
        return selfCopy

    def produceSeeds(self) -> 'PlantArray':
        """
        Produces a list of Juvenile objects that the PlantArray produces in one tick.

        Returns:
            PlantArray: Juvenile objects.
        """
        seedArray = PlantArray()
        if self.hasAdult:
            for _ in range (self.currentAdult.species.ns):
                seedArray.addPlant(Juvenile(self.currentAdult.species, 0))
        return seedArray

    def update(self, neighborDict: dict) -> 'PlantArray':
        """
        Takes in a dictionary of neighbors to update a cell. Each individual Plant in the
        PlantArray will get updated. If the PlantArray has an Adult present and it survives
        the update, all other potential Adults (i.e., Juvenile trees which are old enough)
        will remain at Juvenile stage. If there is no Adult present in the PlantArray, one
        of the potential Adults is randomly selected to be the new Adult of the PlantArray.

        Args:
            neighborDict (dict): Dictionary containing the number of neighboring Adult trees.
                Keys are species ID, and values are number of Adults of that Species.
        
        Returns:
            self.
        """
        newStorage = []
        pickNewAdult = True
        if self.hasAdult:
            pickNewAdult = False
        for plant in self.storage:
            plantSpecies = plant.species.speciesID
            conspecificCount, heterospecificCount = 0, 0
            if plantSpecies in neighborDict:
                conspecificCount = neighborDict[plantSpecies]
                heterospecificCount = sum(neighborDict.values()) - conspecificCount
            else:
                heterospecificCount = sum(neighborDict.values())
            newPlant = plant.update(conspecificCount, heterospecificCount)
            if not isinstance(newPlant, DeadPlant):
                newStorage.append(newPlant)
            if plant == self.currentAdult:
                if isinstance(newPlant, DeadPlant):
                    self.currentAdult = None
                    self.hasAdult = False
                    pickNewAdult = True
        if pickNewAdult:
            adultList = [plant for plant in newStorage if isinstance(plant, Adult)]
            if len(adultList) > 0:
                self.hasAdult = True
                self.currentAdult = adultList[random.randint(0, len(adultList) - 1)]
        newStorage = list(filter(lambda x: not isinstance(x, Adult), newStorage))[0:50]
        if self.hasAdult:
            if len(newStorage) > 0:
                newStorage[random.randint(0, len(newStorage) - 1)] = self.currentAdult     
            else:
                newStorage.append(self.currentAdult)
        self.storage = newStorage
        return self

    def toDict(self) -> dict:
        """
        Returns as a dictionary. Key is SpeciesID, value is number of Adults.
        """
        returnDict = {}
        if self.hasAdult:
            returnDict[self.currentAdult.species.speciesID] = 1
        return returnDict


#    def toDict(self) -> dict:
#        """
#        Stores the Plant objects in the PlantArray as a dictionary, with SpeciesID as keys.
#        This method assumes that the PlantArray has at most one Adult object inside it.
# 
#        Return:
#            dict: Keys are SpeciesID, values are a list containing the number of Adults and
#                Juveniles in the format [adultCount, juvenileCount].
#        """
#        returnDict = {}
#        if self.hasAdult:
#            returnDict[self.currentAdult.species.speciesID] = [1, 0]
#        for plant in self.storage:
#            speciesID = plant.species.speciesID
#            if speciesID in returnDict:
#                returnDict[speciesID][1] += 1
#            else:
#                returnDict[speciesID] = [0, 1]
#        return returnDict

# %%


class Tile:
    """
    Tile class. Represents a Tile on the Board.

    Attributes:
        plantData (dict): A summarized dictionary form of the PlantArray.
        plantArray (PlantArray): A PlantArray object storing the Plant objects on the current tile.

    Methods:
        updateData() -> 'Tile'
        update(neighborData: dict) -> tuple
    """
    def __init__(self):
        self.plantData = {}
        self.plantArray = PlantArray()

    def updateData(self) -> 'Tile':
        """
        Updates the dictionary containing the number of Adult trees on the Tile.
        """
        self.plantData = self.plantArray.toDict()
        return self

    def update(self, neighborData: dict) -> tuple:
        """
        Updates the Plant objects stored on this tile, using the neighbor data.

        Args:
            neighborData (dict): A dictionary containing the list of adult neighbors.

        Returns:
            tuple: The first element is a 'Tile' object and the second element is a
                PlantArray containing the Juvenile objects produced.
        """
        newPlantArray = self.plantArray.update(neighborData)
        self.plantArray = newPlantArray
        self.updateData()
        newSeeds = self.plantArray.produceSeeds()
        return self, newSeeds


# %%


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
    def __init__(self, speciesList: SpeciesList, boardLength: int):
        self.speciesList = speciesList
        self.boardLength = boardLength
        self.boardTime = 0
        self.board = [[Tile() for _ in range(self.boardLength)] for _ in range(self.boardLength)]
        self.seedBoard = [[PlantArray() for _ in range(self.boardLength)]
                          for _ in range(self.boardLength)]
        for i in range(len(self.speciesList.species)):
            for j in range(5):
                start_x = random.randint(0, self.boardLength - 1)
                start_y = random.randint(0, self.boardLength - 1)
                self.seedBoard[start_x][start_y].addPlant(Juvenile(self.speciesList.species[i], 0))

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

    def printBoard(self) -> None:
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
        plt.colorbar()
        plt.show()

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
        """
        returnList = [[0 for _ in range(self.boardLength)] for _ in range(self.boardLength)]
        for i in range (self.boardLength):
            for j in range(self.boardLength):
                newDict = {}
                positions = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
                for position in positions:
                    if ((i + position[0] > -1) and (i + position[0] < self.boardLength) and
                        (j + position[1] > -1) and (j + position[1] < self.boardLength)):
                        neighborDict = (self.board[i + position[0]][j + position[1]]
                                        .plantArray.toDict())
                        for speciesID, count in neighborDict.items():
                            if speciesID in newDict:
                                newDict[speciesID] = newDict[speciesID] + count
                            else:
                                newDict[speciesID] = count
                returnList[i][j] = newDict
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
        self.boardTime += 1
        newNeighborDicts = self.makeNeighborDicts()
        for i in range(self.boardLength):
            for j in range(self.boardLength):
                tileUpdate = self.board[i][j].update(newNeighborDicts[i][j])       # (Tile, PlantArray)
                self.board[i][j] = tileUpdate[0]                                   # update Tile
                newSeeds = tileUpdate[1]                                           # PlantArray of interest
                for k in range(len(newSeeds.storage)):                             # list of Plants
                    newX = random.choice([-1, 0, 1])
                    newY = random.choice([-1, 0, 1])
                    if ((i + newX > -1) and (i + newX < self.boardLength) and
                        (j + newY > -1) and (j + newY < self.boardLength)):
                        self.seedBoard[i + newX][j + newY].addPlant(newSeeds.storage[k])
        for i in range(self.boardLength):
            for j in range(self.boardLength):
                self.board[i][j].plantArray.mergeArray(self.seedBoard[i][j])
        return self

    def clearBoard(self) -> 'Board':
        """
        Clears all Tile objects on the Board (effectively making a new Board).

        Return:
            'Board': An empty Board object.
        """
        return Board(self.speciesList, self.boardLength)


# %%


class Simulation:
    """
    Main Simulation class where the program will be run.

    Attributes:
        board (Board): A Board object to run the simulation on.
        params (list): Not in use at the moment.
        simulationTime (int): Total number of ticks the Simulation has run.

    Methods:
        loadParams(filepath: str) -> 'Simulation'
        saveParams(filepath: str) -> None
        loadBoard(filepath: str) -> 'Simulation'
        useBoard(newBoard: Board) -> 'Simulation'
        clearBoard() -> 'Simulation'
        saveBoard(filepath: str) -> None
        loadSpecies(filepath: str) -> 'Simulation'
        saveSpecies(filepath: str) -> None
        run(iterations: int) -> 'Simulation'
    """
    def __init__(self, speciesList: SpeciesList, boardLength: int):
        self.board = Board(speciesList, boardLength)
        self.params = None
        self.simulationTime = 0

    def loadParams(self, filepath: str) -> 'Simulation':
        """
        Loads a set of parameters from a file. Not used at the moment.

        Args:
            filepath (str): Filepath of saved parameters.

        Return:
            self.
        """
        returnParams = None
        with open(filepath, 'rb') as file:
            returnParams = pickle.load(file)
        self.params = returnParams
        return self

    def saveParams(self, filepath: str) -> None:
        """
        Saves a set of parameters to a file. Not used at the moment.

        Args:
            filepath (str): Filepath to save parameters to.
        """
        with open(filepath, 'wb') as file:
            pickle.dump(self, file)

    def loadBoard(self, filepath: str) -> 'Simulation':
        """
        Loads a Board from a file.

        Args:
            filepath (str): Filepath of saved board.
        """
        self.board = self.board.loadBoard(filepath)
        return self

    def useBoard(self, newBoard: Board) -> 'Simulation':
        """
        Replaces the Board with an existing Board object.

        Args:
            newBoard (Board): The new Board to be used.
        """
        self.board = newBoard
        return self

    def clearBoard(self) -> 'Simulation':
        """
        Clears the Board. The Board will retain its size and SpeciesList.
        """
        self.board = self.board.clearBoard()
        return self

    def saveBoard(self, filepath: str) -> None:
        """
        Saves the current Board to a file.

        Args:
            filepath (str): Filepath to save the Board to.
        """
        self.board.saveBoard(filepath)

    def loadSpecies(self, filepath: str) -> 'Simulation':
        """
        Loads a set of Species from a file.

        Args:
            filepath (str): Filepath to load the SpeciesList from.

        Return:
            self.
        """
        self.board.loadSpecies(filepath)
        return self

    def saveSpecies(self, filepath: str) -> None:
        """
        Saves the current Species to a file.

        Args:
            filepath (str): Filepath to save the SpeciesList to.
        """
        self.board.speciesList.saveSpeciesData(filepath)

    def run(self, iterations: int, printFreq: int) -> 'Simulation':
        """
        Updates the Board, i.e., runs the Simulation for a fixed number of iterations.
        Prints the Board every 100 timesteps.

        Args:
            iterations (int): Number of ticks to run the Simulation for.
            printFreq (int): How frequently to printBoard()

        Return:
            self.
        """
        for i in range(iterations):
            self.simulationTime += 1
            self.board.update()
            if not (i % printFreq) and i > 0:
                print(f'Board at {self.simulationTime}')
                self.board.printBoard()
        return self


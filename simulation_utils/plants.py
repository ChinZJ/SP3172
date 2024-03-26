"""This module defines the Plant, Juvenile, Adult, DeadPlant, and PlantArray classes."""
import random
from species import Species

class Plant:
    """
    Parent class for all Plant objects. Contains several generic methods to be overridden.
    The methods to be overwritten are stated here as an example of how it will be used

    Attributes:
        species (Species): the Species of this Plant.
        age (int): the current age of the Plant, i.e, the number of timesteps it has survived for.

    Methods:
        calculateNDD(cNeighbors: int, hNeighbors: int) -> float
        updateTick(cNeighbors: int, hNeighbors: int) -> bool
        update() -> 'Plant'
    """
    def __init__(self, species: Species, age: int = 0):
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

class DeadPlant(Plant):
    """
    DeadPlant class that inherits from the Plant class. This is meant to be a filler class,
    with all DeadPlant class objects deleted as soon as possible. Hence, it has no methods.
    """
    def __init__(self, species: Species, age: int):
        super().__init__(species, age)

class PlantArray:
    """
    PlantArray class. The primary purpose of the PlantArray object is to store a list of
    Plant objects that will be present within the same Tile location. Hence, the PlantArray
    should obey the two assumptions below.
    1. There is a maximum of one Adult in the PlantArray
    2. There is a maximum number of Plant objects in the PlantArray.

    Attributes:
        hasAdult (bool): True if the PlantArray contains an Adult object, False otherwise.
        currentAdult (Adult): Stores the current Adult of the PlantArray. There can only
            be one Adult at a time. If there is no Adult within the PlantArray, currentAdult is
            set to None.
        storageLimit (int): Maximum number of Plant objects in the PlantArray. This should be
            capped at 50 for computational reasons.
        storage (list): List of Plant objects. The maximum size of the list is determined by
            storageLimit.
        dictionaryFormat (dict): Dictionary containing the number of Adult and Juvenile Plant
            objects the PlantArray has. It is stored in {speciesID: [adultCount, juvenileCount]}
            format.

    Methods:
        addPlant(plant: Plant) -> 'PlantArray'
        mergeArray(newArray: 'PlantArray') -> 'PlantArray'
        produceSeeds() -> list
        update(neighborDict: dict) -> 'PlantArray'
        toDict() -> dict
    """
    def __init__(self, storageLimit : int) -> None:
        self.hasAdult = False
        self.currentAdult = None
        self.storage = []
        self.storageLimit = storageLimit
        self.dictionaryFormat = {}

    def addPlant(self, plant: Plant) -> 'PlantArray':
        """
        Adds a Plant object to the PlantArray. There are several cases to fit the
        requirement that a PlantArray has at most one Adult object.
        
        If the new Plant object is an Adult and
        the PlantArray already has an Adult, the new Plant is not added.
        
        Updates self.neighborTuple afterwards
        
        Case 1: Add Adult
            1.1 Already have adult -> New plant is not added.
            1.2 No adult
                1.2.1 Storage full capacity -> Random replace
                1.2.2 Storage has capacity -> Add
        Case 2: Add juvenile
            2.1 Storage full capacity -> None
            2.2 Storage no capacity -> add

        Args:
            plant (Plant): New Plant object.

        Returns:
            self.
        """
        if ((isinstance(plant, Adult) and self.hasAdult) or
            (isinstance(plant, Juvenile) and len(self.storage) >= self.storageLimit)):
            return self

        if isinstance(plant, Adult):
            if len(self.storage) >= self.storageLimit: # Storage is full of Juveniles
                replacedJuvenileIndex = random.randint(0, len(self.storage) - 1)
                self.dictionaryFormat[replacedJuvenileIndex][1] -= 1
                self.storage[replacedJuvenileIndex] = plant
            else: # Storage has space
                self.storage.append(plant)
            self.hasAdult = True
            self.currentAdult = plant
            speciesID = plant.species.speciesID
            if speciesID in self.dictionaryFormat: # Species already in Tile
                self.dictionaryFormat[speciesID] = [1, self.dictionaryFormat[speciesID][1]]
            else: # Species not already in Tile
                self.dictionaryFormat[speciesID] = [1, 0]
        elif len(self.storage) < self.storageLimit:
            self.storage.append(plant)
            speciesID = plant.species.speciesID
            if speciesID in self.dictionaryFormat: # Species already in Tile
                self.dictionaryFormat[speciesID] = [0, self.dictionaryFormat[speciesID][1] + 1]
            else: # Species not already in Tile
                self.dictionaryFormat[speciesID] = [0, 1]
        return self

    def addAdult(self, plant: Adult) -> 'PlantArray':
        """
        Used exclusively in the boomerModel.
        Allows of addition of multiple Adults into storage, 
        for them to be scattered upon merge.
        
        Method does not break anything as addPlant is still called after,
        ie. only one Adult per grid is preserved regardless
        """
        if len(self.storage) < self.storageLimit: # ensure no overflow
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
        selfCopy = self # note selfCopy and self point to the same object
        for otherPlant in newArray.storage:
            selfCopy = selfCopy.addPlant(otherPlant) # addPlant() updates neighborList
        return selfCopy

    def produceSeeds(self, boomerModel : bool) -> 'PlantArray':
        """
        Produces a list of Juvenile objects that the PlantArray produces in one tick.

        Returns:
            PlantArray: Juvenile objects.
        """
        seedArray = PlantArray(self.storageLimit)
        if self.hasAdult:
            if boomerModel:
                for _ in range (self.currentAdult.species.ns):
                    seedArray.addAdult(Adult(self.currentAdult.species, 0))
            else:
                for _ in range (self.currentAdult.species.ns):
                    seedArray.addPlant(Juvenile(self.currentAdult.species, 0))
        return seedArray

    def mergeDict(self, neighborDict: dict, boomerModel: bool) -> dict:
        """
        This creates another dictionary to be used during update()
        Calls either boomerMergeDict() or zoomerMergeDict() depending on model variant
        
        Recursive method, where all Plant must call mergeDict to produce a standardised dict      
        
        Args:
            neighborDict (dict): dict of neighbor Plants
            boomerModel (boolean): boolean if boomer model is being run

        Returns:
            mergedDict (dict): dict of all Plant
        """
        if boomerModel:
            return self.boomerMergeDict(neighborDict)
        return self.zoomerMergeDict(neighborDict)

    def boomerMergeDict(self, neighborDict: dict) -> dict:
        """
        Return a dictionary of Adult count only.
        Key is speciesID
        Value is number of Adult
        
        Args:
            neighborDict (dict): dict of neighbor Plants
            
        Returns:
            mergedDict (dict): dict of all Adult Plant
        """
        if self.hasAdult:
            speciesID = self.currentAdult.species.speciesID
            if speciesID in neighborDict:
                neighborDict[speciesID] += 1
            else:
                neighborDict[speciesID] = 1
        return neighborDict

    def zoomerMergeDict(self, neighborDict: dict) -> dict:
        """
        Return a dictionary of all Plant count.
        Key is speciesID
        Value is number of Adult and Juvenile (not distinguished)
        
        Args:
            neighborDict (dict): dict of neighbor Plants
            
        Returns:
            mergedDict (dict): dict of all Plant
        """
        for speciesID, countLst in self.dictionaryFormat.items():
            count = sum(countLst)
            if speciesID in neighborDict:
                neighborDict[speciesID] += count # sum of both Adult and Juvenile
            else:
                neighborDict[speciesID] = count
        return neighborDict

    def toDict(self) -> dict: # TODO
        """
        Returns as a dict
        Key is speciesID, 
        value is a list containing number of (Adult, Juvenile)
        
        Since every PlantArray has a maximum of one Adult, 
        there is no point in checking every iteration. We will check at the end
        
        Avoid repeatedly calling this method as it seems to be potentially expensive
        Can be used during instatiation
        """
        returnDict = {}
        for plant in self.storage:
            speciesID = plant.species.speciesID
            if speciesID in returnDict:
                returnDict[speciesID][1] += 1
            else:
                returnDict[speciesID] = [0, 1]
        if self.hasAdult: # Now check if Adult exists
            speciesID = self.currentAdult.species.speciesID
            if speciesID in returnDict: # The Adult was counted as a "Juvenile"
                returnDict[speciesID][0] += 1
                returnDict[speciesID][1] -= 1
            else: # New species
                returnDict[speciesID] = [1, 0]
        self.dictionaryFormat = returnDict # Update self
        return returnDict

    def updatedToDict(self) -> dict:
        """
        Gets everything as a dict.

        Returns:
            dict: A dictionary of Plant objects stored in the PlantArray in
                {speciesID: [adultCount, juvenileCount]} format.
        """
        return self.dictionaryFormat

    def update(self, neighborDict: dict) -> 'PlantArray': # TODO
        """
        Takes in neighborDict (currently set as a 3 x 3 Moore neighborhood)
        
        NOTE: We assume that the neighborDict already contains itself.
        ie. mergeDict() was called on the Tile itself (refer to Board)
        
        This neighborDict is either created by boomerMergeDict() or zoomerMergeDict()
        Thus the implementation in update() is generalised
        
        Each individual Plant in the PlantArray will get updated first.
        Juvenile and Adult will be added into separate lists.
        If there is an Adult present after the update, purge all other Adult
            ie. There can only be one Adult and the Adult that has survived the longest
                is taken to be the "most dominant"
        Else select an Adult at random
    
        Create a new dict to replace self.neighborDict.
        Further optimisation will require changing self.neighborDict instead of creating new

        Args:
            neighborDict (dict): Dictionary containing the number of neighboring Adult trees.
                Keys are species ID, and values are number of Adults of that Species.
        
        Returns:
            self.
        """
        newStorage = []
        adultStorage = []
        newNeighborDict = {}
        for plant in self.storage:
            speciesID = plant.species.speciesID
            conCount = neighborDict[speciesID] - 1 # note -1 to subtract itself
            hetCount = sum(neighborDict.values()) - conCount

            newPlant = plant.update(conCount, hetCount)
            if isinstance(newPlant, DeadPlant): # plant died
                if plant == self.currentAdult: # Adult that died
                    self.hasAdult = False
                    self.currentAdult = None
            else: # plant survived
                if isinstance(newPlant, Adult): # Grew into Adult
                    adultStorage.append(newPlant)
                    if plant == self.currentAdult: # Update the currentAdult
                        self.currentAdult = newPlant
                else: # Still Juvenile
                    newStorage.append(newPlant)
                    if speciesID in newNeighborDict:
                        newNeighborDict[speciesID][1] += 1
                    else:
                        newNeighborDict[speciesID] = [0, 1]

        speciesID = -1 # error check if no new adult
        if self.hasAdult: # Adult survived to next timepoint
            speciesID = self.currentAdult.species.speciesID
        else: # Need a replacement
            if len(adultStorage) > 0: # There are adults to pick from
                self.hasAdult = True
                self.currentAdult = adultStorage[random.randint(0, len(adultStorage) -1)]
        if speciesID != -1: # Adult exists
            newStorage.append(self.currentAdult) # add Adult into the new list
            if speciesID in newNeighborDict:
                newNeighborDict[speciesID][0] += 1
            else:
                newNeighborDict[speciesID] = [1, 0]

        self.storage = newStorage
        self.dictionaryFormat = newNeighborDict
        return self

    def clear(self) -> 'PlantArray':
        """
        Use for seedBoard in 'Board' class
        Called upon addition of seedBoard to board
        """
        return PlantArray(self.storageLimit)

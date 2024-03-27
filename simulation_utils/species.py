"""This module defines the Species and SpeciesList classes."""
import math
import pandas as pd

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

    def __init__(self, parentID: int,
                 p1: float, p2: float,
                 t1: int, t2: int,
                 ns: int,
                 conNDD: float, hetNDD: float):
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
            ns (int): The number of Seed objects produced by an Adult of this Species every tick.
            conNDD (float): The magnitude of CNDD effects on this Species.
            hetNDD (float): The magnitude of HNDD effects on this Species.
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
        returnDict = {"speciesID": self.speciesID, "parentID": self.parentID,
                      "t1": self.t1, "p1": self.p1, "seedPerTick": self.seedPerTick,
                      "t2": self.t2, "p2": self.p2, "adultPerTick": self.adultPerTick,
                      "ns": self.ns,
                      "CNDD": self.conNDD, "HNDD": self.hetNDD}
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
            newSpecies = pd.DataFrame(species.getDataAsDict(), index = [0])
            self.storage = pd.concat([self.storage, newSpecies], ignore_index = True)
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
        self.storage = newStorage.drop_duplicates(["speciesID"])
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

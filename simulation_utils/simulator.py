"""This module contains the Simulation class."""
import numpy as np
import dill as pickle

from species import Species
from species import SpeciesList
from board import Board

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
    def __init__(self, speciesList: SpeciesList, boardLength: int,
                storageLimit : int = 50, startNumber : int = 5, 
                boomerModel: bool = False, stdev : int = 5, 
                printFreq : int = 100):
        self.board = Board(speciesList, boardLength, storageLimit, startNumber, boomerModel, stdev, printFreq)
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

    def run(self, iterations: int) -> 'Simulation':
        """
        Updates the Board, i.e., runs the Simulation for a fixed number of iterations.
        Prints the Board every 100 timesteps.

        Args:
            iterations (int): Number of ticks to run the Simulation for.
            printFreq (int): How frequently to printBoard()

        Return:
            self.
        """
        for i in range(iterations + 2):
            self.board.update()
        return self
    
# %%

def generateSpeciesList(numOfSpecies : int, stdevLog : float,
                        t1: int, t2: int, 
                        ns : int, 
                        conNDD : float, hetNDD : float) -> 'SpeciesList':
    """
    Creates a SpeciesList with numOfSpecies number of species.
    The following attributes of species are currently fixed but can be subjected to variation in future:
        t1 (time taken for Juvenile to germinate to Adult, 
        t2 (time taken for Adult to reach mortaility on average),
        ns (number of seeds produced by each adult), 
        conNDD (magnitude of conspecifc negative density dependence), 
        hetNDD (magnitude of heterospecific negative density dependence)
    
    The following are drawn from a lognormal distribution:
        p1 (probability that juvenile survives to adult on average)
        p2 (probabiltiy that adult survives after t2 time steps)
    """
    
    speciesList = SpeciesList()
    for i in range(numOfSpecies):
        # Generate p1 and p2
        p1, p2 = np.random.lognormal(mean = 0.0, sigma = stdevLog, size = 2)
        while (p1 > 1.0):
            p1 = np.random.lognormal(mean = 0.0, sigma = stdevLog, size = None)
        while (p2 > 1.0):
            p2 = np.random.lognormal(mean = 0.0, sigma = stdevLog, size = None)
        speciesList.addSpecies(Species(-1, p1, p2, t1, t2, ns, conNDD, hetNDD))
    return speciesList

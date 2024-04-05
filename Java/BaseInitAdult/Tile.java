import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.*;

public class Tile {
    List<Plant> oldPlantArray; // for READ operations
    List<Plant> newPlantArray; // for self WRITE operations
    int oldAdultSpeciesId;
    int newAdultSpeciesId;
    Plant oldAdult;
    Plant newAdult;
    List<Tile> nNDD; // can implement same as below if extending past Moore nbhd
    Map<Species, Pair<Integer, Integer>> oldNeighMap;   // for READ operations
                                                        // key is Species
                                                        // pair is juvCount and adultCount
    Map<Species, Pair<Integer, Integer>> newNeighMap;   // for self WRITE operations
    Map<Integer, List<Tile>> nSeeds; // key: distance, value: list of tiles at that distance
    List<Double> distProbs;
    SpeciesList speciesList;
    Pair<Integer, Integer> coords;
    public static final Species DUMMY = new Species(-1, -1, -1, -1, -1, -1, -1, -1, -1);

    public Tile(SpeciesList speciesList, List<Double> distProbs, int i, int j) {
        this.oldPlantArray = new ArrayList<>(); 
        this.newPlantArray = new ArrayList<>(); 
        this.oldAdultSpeciesId = -1;
        this.newAdultSpeciesId = -1;
        this.oldAdult = null;
        this.newAdult = null;
        this.nNDD = new ArrayList<Tile>(); // note this can only be created after instantiating all Tiles
        this.nSeeds = new HashMap<>(); 
        this.oldNeighMap = new HashMap<>(); 
        this.newNeighMap = new HashMap<>(); 
        this.speciesList = speciesList;
        this.distProbs = distProbs;
        this.coords = new Pair<Integer, Integer>(i, j);
    }

    public String toString() {
        return String.format("Tile %s", this.coords.toString());
    }

    
    public HashMap<Species, Integer> countNeighborsNDD() { 
        // special key DUMMY included for total count and must be excluded in future uses
        // Note that individuals on the same Tile are also NEIGHBORS of itself
        // key: species, value: number of neighbors of that species     
        HashMap<Species, Integer> neighborMap = new HashMap<>();
        int count = 0;
        // Note that nNDD accounts for self by implementation
        for (int i = 0; i < this.nNDD.size(); i++) {
            Tile neighb = this.nNDD.get(i);
            for (Species key : neighb.oldNeighMap.keySet()) {
                int sum = neighb.oldNeighMap.get(key).first + neighb.oldNeighMap.get(key).second;
                count += sum;
                if (neighborMap.containsKey(key)) {
                        neighborMap.replace(key, neighborMap.get(key) + sum);
                } else {
                    neighborMap.put(key, sum);
                }
            }
        }
        neighborMap.put(Tile.DUMMY, count);
        return neighborMap;
    }

    public HashMap<Integer, Pair<Pair<Integer, List<Integer>>, Integer>> mergeNeighborMap(HashMap<Integer, Pair<Pair<Integer, List<Integer>>, Integer>> neighborMap) {
        // Note use speciesId as key to faciliate exportation in class Board
        // key: Species, value: Pair<adultCount, list of ages>, juvenileCount
        for (Species key : this.oldNeighMap.keySet()) {
            Pair<Integer, Integer> thisPair = this.oldNeighMap.get(key);
            if (neighborMap.containsKey(key.speciesId)) {
                Pair<Pair<Integer, List<Integer>>, Integer> pair = neighborMap.get(key.speciesId);
                // Check if adult present
                if (thisPair.first != 0) { //adult exists
                    ++pair.first.first;
                    pair.first.second.add(this.oldAdult.age);
                } // else no need to update since no adult
                pair.second += thisPair.second;

                neighborMap.replace(key.speciesId, pair);
            } else {
                List<Integer> adultAge = new ArrayList<>();
                Pair<Integer, List<Integer>> pairFirst = new Pair<>(0, adultAge); //initialize
                if (thisPair.first != 0) { //adult exists
                    ++pairFirst.first;
                    pairFirst.second.add(this.oldAdult.age);
                } // else do nothing because no adults
                Pair<Pair<Integer, List<Integer>>, Integer> pair = new Pair<>(pairFirst, thisPair.second);
                neighborMap.put(key.speciesId, pair);
            }
        }
        return neighborMap;
    }

    public HashMap<Species, Double> countNeighborsSeeds() {
        // special key DUMMY included for total count and must be excluded in future uses
        // Note that individuals on the same Tile can also disperse seeds to itself and are thus included
        // key: Species, value: probabilities
        HashMap<Species, Double> seedNeighbors = new HashMap<>();
        double count = 0.0;
        for (Map.Entry<Integer, List<Tile>> tiles : nSeeds.entrySet()) {
            int distance = tiles.getKey();
            List<Tile> lst = tiles.getValue();
            for (Tile t : lst) {
                if (t.oldAdult != null) { // there exists an adult
                    Species neighborAdultSpecies = t.oldAdult.species;
                    count += this.distProbs.get(distance);
                    if (seedNeighbors.containsKey(neighborAdultSpecies)) {
                        seedNeighbors.put(neighborAdultSpecies, seedNeighbors.get(neighborAdultSpecies) + this.distProbs.get(distance));
                    } else {
                        seedNeighbors.put(neighborAdultSpecies, this.distProbs.get(distance));
                    }
                }
            }
        }
        seedNeighbors.put(Tile.DUMMY, count);
        return seedNeighbors;
    }

    public void updateExistingPlants() {
        // get neighbor counts
        // Remember that neighborMap has DUMMY key
        HashMap<Species, Integer> neighborMap = this.countNeighborsNDD();
        int totalNeighborAdults = neighborMap.get(Tile.DUMMY);
        boolean existingAdult = false;

        // update each plant
        // Check during iteration if existingAdult survives
        List<Plant> potentialAdults = new ArrayList<>();
        for (int i = 0; i < oldPlantArray.size(); i++) {
            Plant oldPlant = oldPlantArray.get(i);
            int conNeighbors = neighborMap.get(oldPlant.species) - 1; // note that we have to SUBTRACT itself
            int hetNeighbors = totalNeighborAdults - conNeighbors - 1; // again, subtract ITSELF
            Plant newPlant = oldPlant.update(conNeighbors, hetNeighbors);
            if (newPlant == null) { // dead
                continue;
            }
            if (newPlant instanceof Adult) { // adult
                // implementation of Plant.update() makes Plant mutable unless the Plant is dead (null)
                if (!existingAdult) { // no current Adult, thus need to maintain potentialAdults
                    potentialAdults.add(newPlant);
                }
                if (newPlant == this.oldAdult) { // trivially true, previous adult alive
                    
                    existingAdult = true;
                    this.newAdultSpeciesId = newPlant.species.speciesId;
                    this.newAdult = newPlant;
                }
            } else { //juvenile
                this.newPlantArray.add(newPlant);
                if (this.newNeighMap.containsKey(newPlant.species)) {
                    Pair<Integer, Integer> pair = this.newNeighMap.get(newPlant.species);
                    ++pair.second;
                    this.newNeighMap.replace(newPlant.species, pair);
                } else {
                    Pair<Integer, Integer> pair = new Pair<Integer, Integer>(0, 1);
                    this.newNeighMap.put(newPlant.species, pair);
                }
            }
        }

        if (!existingAdult) { // Pick a new adult
            int len = potentialAdults.size();
            if (len != 0) { // ensure there are adults to choose from
                Random random = new Random();
                int ind = random.nextInt(len);
                this.newAdult = potentialAdults.get(ind);
                this.newAdultSpeciesId = this.newAdult.species.speciesId;
            }
        } 
        // Since there is an adult dominating the board, we assume that all new Adults die
        // Thus, we only update adult in newNeighMap
        if (this.newAdult != null) {
            this.newPlantArray.add(this.newAdult);
            if (this.newNeighMap.containsKey(this.newAdult.species)) {
                Pair<Integer, Integer> pair = this.newNeighMap.get(this.newAdult.species);
                pair.first = 1;
                this.newNeighMap.replace(this.newAdult.species, pair);
            } else {
                Pair<Integer, Integer> pair = new Pair<Integer, Integer>(1, 0);
                this.newNeighMap.put(this.newAdult.species, pair);
            }
        }
    }

    public void addNewSeeds() { 
        int newSeedCount = 50 - newPlantArray.size();

        // key: Species, value: "probability"
        // Remember that neighborSeedProbabilities has DUMMY key
        HashMap<Species, Double> neighborSeedProbabilities = this.countNeighborsSeeds();
        double totalProb = neighborSeedProbabilities.get(Tile.DUMMY);
        if (totalProb == 0.0) {
            return;
        }
       
        // Create cumulative probability
        // key: probability, value: index to speciesList
        TreeMap<Double, Integer> cumProbability = new TreeMap<>();
        List<Species> speciesList = new ArrayList<>();
        double cumProb = 0;
        int idx = 0;

        for (Map.Entry<Species, Double> prob : neighborSeedProbabilities.entrySet()) {
            Species species = prob.getKey();
            double speciesProb = prob.getValue();
            if (species == Tile.DUMMY) { // DUMMY key must be EXCLUDED from calculations
                continue;
            }
            cumProb += speciesProb;
            cumProbability.put((cumProb / totalProb), idx);
            idx++;
            speciesList.add(species); // index is now mappable to speciesList
        }
        
        while (newSeedCount-- > 0) { 
            // here, we assume that seeds are infinite
            // thus, we will keep dispersing seeds until the array is filled
            double prob = Math.random();
            double key = cumProbability.ceilingKey(prob);
            int index = cumProbability.get(key);

            Species species = speciesList.get(index);
            newPlantArray.add(new Juvenile(species, 0));
            if (this.newNeighMap.containsKey(species)) {
                Pair<Integer, Integer> pair = this.newNeighMap.get(species);
                ++pair.second;
                this.newNeighMap.replace(species, pair);
            } else {
                Pair<Integer, Integer> pair = new Pair<Integer, Integer>(0, 1);
                this.newNeighMap.put(species, pair);
            }
        }
    }

    public void updateSelf() {
        // REMINDER: THIS MUST BE DONE IN A SEPERATE PARALLEL STREAM
        this.oldPlantArray = this.newPlantArray;
        this.newPlantArray = new ArrayList<>();

        this.oldAdult = this.newAdult;
        this.newAdult = null;


        this.oldAdultSpeciesId = this.newAdultSpeciesId;
        this.newAdultSpeciesId = -1;

        this.oldNeighMap = this.newNeighMap;
        this.newNeighMap = new HashMap<>();;
    }


}

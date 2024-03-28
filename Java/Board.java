import java.sql.Array;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.stream.Collectors;
import java.util.*;
import java.io.*;

public class Board {
    List<Tile> board = new ArrayList<>();
    SpeciesList speciesList;
    int bivStdev;
    BivariateDist bivDist;
    public List<Double> distanceProbs;
    int boardLength;
    int nNDD;
    int nSeeds;

    public Board(SpeciesList sl, int bivStdev, BivariateDist bivDist, 
                int boardLength, int nNDD, int numJuvenile) {
        this.speciesList = sl;
        this.bivStdev = bivStdev;
        this.bivDist = bivDist;
        this.distanceProbs = bivDist.distData.get(bivStdev);
        this.boardLength = boardLength;
        this.nNDD = nNDD;   // Note that nNDD should be the distance EXCLUDING SELF
                            // ie. an nNDD of 0 would reference only itself
                            // an nNDD of 1 would be a moore neighborhood
        
        this.nSeeds = distanceProbs.size() - 1; // note that this is also the radius EXCLUDING SELF
        
        for (int i = 0; i < boardLength; i++) {
            for (int j = 0; j < boardLength; j++) {
                this.board.add(new Tile(this.speciesList, this.distanceProbs, i, j)); // note i, j are coordinates for debugging
            }
        }

        List<Integer> shiftsNDD = new ArrayList<>();
        List<Integer> shiftsSeeds = new ArrayList<>();
        for (int s = -nNDD; s <= nNDD; s++) { // Inclusive 
            shiftsNDD.add(s);
        }
        for (int s = -nSeeds; s <= nSeeds; s++) { // Inclusive 
            shiftsSeeds.add(s);
        }

        for (int ind = 0; ind < this.board.size(); ind++) {
            Tile targetTile = this.board.get(ind);
            int j = ind % this.boardLength; // column
            int i = (ind - j) / this.boardLength; // row
            for (int dx: shiftsNDD) { // NDD
                for (int dy: shiftsNDD) {
                    if (j + dy >= 0 && j + dy < this.boardLength && i + dx >= 0 && i + dx < this.boardLength) {
                        int neighborIndex = ((i + dx) * this.boardLength) + (j + dy);
                        targetTile.nNDD.add(this.board.get(neighborIndex));
                    }
                }
            }
            for (int dx: shiftsSeeds) { // seeds
                for (int dy: shiftsSeeds) {
                    if (j + dy >= 0 && j + dy < this.boardLength && i + dx >= 0 && i + dx < this.boardLength) {
                        int neighborIndex = ((i + dx) * this.boardLength) + (j + dy);
                        int dist = Math.max(Math.abs(dx), Math.abs(dy));
                        // Check if dist present first
                        List<Tile> t;
                        if (targetTile.nSeeds.containsKey(dist)) {
                            t = targetTile.nSeeds.get(dist);
                        } else {
                            t = new ArrayList<Tile>();
                        }
                        t.add(this.board.get(neighborIndex));
                        targetTile.nSeeds.put(dist, t); // this replaces the current existing value
                    }
                }
            }
        }
        
        for (Integer key : this.speciesList.speciesList.keySet()) {
            Species species = this.speciesList.speciesList.get(key);
            Random random = new Random();
            int len = this.board.size();
            for (int i = 0; i < numJuvenile; i++) {
                while (true) {
                    // Only when a new Juvenile has been planted then we can proceed
                    int ind = random.nextInt(len);
                    if (this.board.get(ind).oldPlantArray.size() < 50) {
                        this.board.get(ind).oldPlantArray.add(new Juvenile(species, 0));
                        if (this.board.get(ind).oldNeighMap.containsKey(species)) {
                            Pair<Integer, Integer> pair = this.board.get(ind).oldNeighMap.get(species);
                            ++pair.second;
                            this.board.get(ind).oldNeighMap.replace(species, pair);
                        } else {
                            Pair<Integer, Integer> pair = new Pair<Integer, Integer>(0, 1);
                            this.board.get(ind).oldNeighMap.put(species, pair);
                        }
                        break;
                    }
                }
            }
        }
    }

    public void update() {
        // parallelization input here
        ExecutorService executor = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());

        this.board.parallelStream().forEach(tile -> executor.execute(() -> {
            tile.updateExistingPlants();

            tile.addNewSeeds();
        }));

        executor.shutdown();


        while (!executor.isTerminated()); // wait
        
        ExecutorService executorTwo = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());

        this.board.parallelStream().forEach(tile -> executorTwo.execute(() -> {
            tile.updateSelf();
        }));

        executorTwo.shutdown();

        while (!executorTwo.isTerminated()); // wait
    }

    public void run(int steps) throws IOException {
        for (int i = 0; i <= steps; i++) {
            this.update();
            if ((i + 1) % 100 == 0) {
                this.exportData(i + 1);
            }
            if ((i + 1) % 1000 == 0) {
                this.exportState(i + 1);
            }
        }
        
    }

    public void exportData(Integer iter) throws IOException {
        // This looks at all the tiles, calculate the total number of Juvs and Adults for each species
        // and exports it onto a csv labelled "iter.csv"
        List<String> csvFormat = this.speciesList.csvFormat;
        String fileName = iter.toString() + ".csv";
        BufferedWriter bw = new BufferedWriter(new FileWriter(fileName));

        // Iterate through all tiles and get the mergeDict
        HashMap<Integer, Pair<Pair<Integer, List<Integer>>, Integer>> neighborMap = new HashMap<>();
        for (Tile tile : this.board) {
            neighborMap = tile.mergeNeighborMap(neighborMap);
        }
        bw.write(csvFormat.get(0)); //Headers
        bw.newLine();
        for (int i = 1; i < csvFormat.size(); i++) {
            // Start from 1 because 0 is a header
            // Note that csvFormat is in ascending order of speciesId
            // Since the 0th index is the column headers, we can directly index it
            List<String> editLine = Arrays.asList(csvFormat.get(i).split(","));
            if (editLine.size() == 0) {
                continue;
            }
            // Reconstruct the csv
            if (neighborMap.containsKey(i)) {
                Pair<Pair<Integer, List<Integer>>, Integer> pair = neighborMap.get(i);
                // Filter out the adults
                Pair<Integer, List<Integer>> adultPair = pair.first;
                System.out.println(adultPair);
                // check for Adults
                if (adultPair.first != 0) {
                    String ages = String.join("#", adultPair.second.stream().map(Object::toString).collect(Collectors.toList()));
                    editLine.set(10, adultPair.first.toString()); // 10 is adults
                    editLine.set(12, ages);
                } else {
                    editLine.set(10, "0");
                    editLine.set(12, "");
                }
                editLine.set(11, pair.second.toString()); // 11 is juveniles
            } else {
                editLine.set(10, "0");
                editLine.set(11, "0");
                editLine.set(12, "");
            }
            bw.write(String.join(",", editLine));
            bw.newLine();
        }
        bw.flush();
        bw.close();
    }
    

    public void exportState(Integer iter) throws IOException {
        String fileName = iter.toString() + "finalState.csv";
        List<String> line = new ArrayList<>();
        BufferedWriter bw = new BufferedWriter(new FileWriter(fileName));

        //Iterate through all tiles
        int col = 0;
        for (Tile tile : this.board) {
            line.add(Integer.toString(tile.oldAdultSpeciesId));
            col++;
            if (col % this.boardLength == 0) {
                String convert = String.join(",", line);
                bw.write(String.join(",", line));
                bw.newLine();
                line = new ArrayList<>();
            }
        }
        bw.flush();
        bw.close();
    }
}

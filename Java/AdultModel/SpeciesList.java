// package TeTrees.t;

import java.util.*;
import java.io.*;

public class SpeciesList {
    HashMap<Integer, Species> speciesList = new HashMap<>();
    List<String> csvFormat;

    public SpeciesList(String fileName) throws IOException {
        this.speciesList = this.convert(fileName);
    }

    public HashMap<Integer, Species> convert(String fileName) throws IOException {
        // This is meant to create the speciesList for the code
        // However, it will secretly create the csvFormat used for exporting data in class Board
        BufferedReader br = new BufferedReader(new FileReader(fileName));
        HashMap<Integer, Species> speciesList = new HashMap<>();
        List<String> csvFormat = new ArrayList<>();

        csvFormat.add(br.readLine()); // Drop header, but save for csvFormat
        // Column header as follows: 
        // speciesID, parentID, t1, p1, seedPerTick, t2, p2, adultPerTick, CNDD, HNDD, Adult, Juvenile
        // p1, seedPerTick, p2, adultPerTick, CNDD, HNDD are double
        // Rest are int
        String line = br.readLine();
        while(line != null) {
            csvFormat.add(line); 
            List<String> lineData = Arrays.asList(line.split(","));
            if (lineData.size() != 0) { 
                // Creation of Species
                int speciesId = Integer.parseInt(lineData.get(0));
                int parentId = Integer.parseInt(lineData.get(1));
                int t1 = Integer.parseInt(lineData.get(2));
                double p1 = Double.parseDouble(lineData.get(3));
                double seedPerTick = Double.parseDouble(lineData.get(4));
                int t2 = Integer.parseInt(lineData.get(5));
                double p2 = Double.parseDouble(lineData.get(6));
                double adultPerTick = Double.parseDouble(lineData.get(7));
                double conNDD = Double.parseDouble(lineData.get(8));
                double hetNDD = Double.parseDouble(lineData.get(9));

                Species species = new Species(speciesId, 
                                                p1, p2, 
                                                t1, t2, 
                                                seedPerTick, adultPerTick,
                                                conNDD, hetNDD);
                speciesList.put(speciesId, species);
            }
            line = br.readLine();
        }
        this.csvFormat = csvFormat;
        return speciesList;
    }

    public SpeciesList addSpecies(Species s) {
        this.speciesList.put(s.speciesId, s);
        return this;
    }

}

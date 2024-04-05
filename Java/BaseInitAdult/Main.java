import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.*;
import java.io.*;

<<<<<<< Updated upstream:Java/Main.java
=======

>>>>>>> Stashed changes:Java/BaseInitAdult/Main.java
public class Main {
    public static void main(String[] args) throws FileNotFoundException, Exception, IOException{
        // Capture the start time
        long startTime = System.nanoTime();

        // Pre processing
        // arg0: String speciesList directory
        // arg1: String bivariate normal distribution directory
        String slFile = args[0];
        SpeciesList speciesList = new SpeciesList(slFile);
        
        String bvFile = args[1];
        BivariateDist bivDist = new BivariateDist(bvFile);
        
        // Main Program
        // arg2: int bivStdev
        // arg3: int boardLength
        // arg4: int nNDD
        // arg5: int numJuvenile
        // arg6: int time

        Board board = new Board(speciesList, Integer.parseInt(args[2]), bivDist, Integer.parseInt(args[3]), Integer.parseInt(args[4]), Integer.parseInt(args[5]));
        System.out.println("Board created! Starting iterations...");
        
        int end = Integer.parseInt(args[6]);
        board.run(end);
        System.out.println("All iterations completed! Creating final board state...");


        // Capture the end time
        long endTime = System.nanoTime();

        // Calculate the runtime
        long runtime = endTime - startTime;

        // Print the start and end times
        System.out.println("Start Time: " + startTime);
        System.out.println("End Time: " + endTime);

        // Print the runtime in milliseconds
        System.out.println("Runtime: " + runtime / 1000000 + " milliseconds");
    }
}

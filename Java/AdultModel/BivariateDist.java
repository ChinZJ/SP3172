// package TeTrees.t;

import java.util.*;
import java.io.*;

public class BivariateDist{
	HashMap<Integer, List<Double>> distData = new HashMap<Integer, List<Double>>();

	public BivariateDist(String fileName) throws IOException {
		this.distData = BivariateDist.convert(fileName);
	}

	public static HashMap<Integer, List<Double>> convert(String fileName) throws IOException {
        BufferedReader br = new BufferedReader(new FileReader(fileName));
		
		HashMap<Integer, List<Double>> distData = new HashMap<Integer, List<Double>>(); //stdev as key, long[] as value

		br.readLine(); // Drop header
		String line = br.readLine();
		while(line != null) {
			List<String> lineData = Arrays.asList(line.split(","));
			if (lineData.size() != 0) {
				List<Double> data = new ArrayList<Double>();
				for (int i = 2; i < lineData.size(); i++) { // Discard mean and stdev
					data.add(Double.parseDouble(lineData.get(i))); // Convert to long for storing
				}
				distData.put(Integer.parseInt(lineData.get(1)), data);
			}
			line = br.readLine();
		}
		return distData;
    }
}
// package TeTrees.t;

public class Plant {
    Species species;
    int age;

    public Plant(Species s, int age) {
        this.species = s;
        this.age = age;
    }

    public String toString() {
        return "Generic Plant that should not exist";
    }

    public double calculateNDD(double cNeighbors, double hNeighbors) {
        return cNeighbors + hNeighbors;
    }

    public boolean updateTick(double cNeighbors, double hNeighbors) {
        return Math.random() <= 1 - calculateNDD(cNeighbors, hNeighbors);
    }

    public Plant update(double cNeighbors, double hNeighbors) {
        if (this.updateTick(cNeighbors, hNeighbors)) {
            ++this.age;
            return this;
        }
        return null;
    }

}

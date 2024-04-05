public class Adult extends Plant {
    public Adult(Species s, int age) {
        super(s, age);
    }

    @Override
    public String toString() {
        return "Adult of species index " + this.species.speciesId + " of age " + this.age;
    }

    @Override
    public double calculateNDD(double cNeighbors, double hNeighbors) {
        return (cNeighbors * this.species.conNDD) +
                (hNeighbors * this.species.hetNDD);
    }

    @Override
    public boolean updateTick(double cNeighbors, double hNeighbors) {
        return Math.random() <= this.species.p2 - calculateNDD(cNeighbors, hNeighbors);
    }

    @Override
    public Plant update(double cNeighbors, double hNeighbors) {
        if (this.updateTick(cNeighbors, hNeighbors)) {
            ++this.age;
            return this;
        }
        return null;
    }
}

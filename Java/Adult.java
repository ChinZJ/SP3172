public class Adult extends Plant {
    public Adult(Species s, int age) {
        super(s, age);
    }

    @Override
    public String toString() {
        return "Adult of species index " + this.species.speciesId + " of age " + this.age;
    }

    @Override
    public double calculateNDD(int cNeighbors, int hNeighbors) {
        return (cNeighbors * this.species.conNDD) +
                (hNeighbors * this.species.hetNDD);
    }

    @Override
    public boolean updateTick(int cNeighbors, int hNeighbors) {
        return Math.random() <= 1 - calculateNDD(cNeighbors, hNeighbors);
    }

    @Override
    public Plant update(int cNeighbors, int hNeighbors) {
        if (this.updateTick(cNeighbors, hNeighbors)) {
            ++this.age;
            return this;
        }
        return null;
    }
}

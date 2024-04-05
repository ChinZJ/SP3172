public class Juvenile extends Plant {
    public Juvenile(Species s, int age) {
        super(s, age);
    }

    @Override
    public String toString() {
        return "Juvenile of species index " + this.species.speciesId + " of age " + this.age;
    }

    @Override
    public double calculateNDD(int cNeighbors, int hNeighbors) {
        // Currently set to exert twice as strong
        return (2 * cNeighbors * this.species.conNDD) +
                (2 * hNeighbors * this.species.hetNDD);
    }

    @Override
    public boolean updateTick(int cNeighbors, int hNeighbors) {
        return Math.random() <= this.species.seedPerTick - calculateNDD(cNeighbors, hNeighbors);
    }

    @Override
    public Plant update(int cNeighbors, int hNeighbors) {
        if (this.updateTick(cNeighbors, hNeighbors)) {
            ++this.age;
            if (this.age >= this.species.t1) {
                return new Adult(this.species, this.age);
            }
            return this;
        }
        return null;
    }
}

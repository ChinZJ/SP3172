public class Species {
    int speciesId;
    int t1;
    double p1;
    double seedPerTick;
    int t2;
    double p2;
    double adultPerTick;
    double conNDD;
    double hetNDD;

    public Species(int speciesId,
                   double p1, double p2,
                   int t1, int t2,
                   double seedPerTick, double adultPerTick,
                   double conNDD, double hetNDD) {
        this.speciesId = speciesId;
        this.t1 = t1;
        this.p1 = p1;
        this.seedPerTick = seedPerTick;
        this.t2 = t2;
        this.p2 = p2;
        this.adultPerTick = adultPerTick;
        this.conNDD = conNDD;
        this.hetNDD = hetNDD;
    }

    public String toString() {
        return "sIdx " + this.speciesId;
    }

    @Override
    public boolean equals(Object obj) {
        if (obj == null) {
            return false;
        } else if (this == obj) {
            return true;
        }

        if (obj instanceof Species species) {
            return this.speciesId == species.speciesId;
        }

        return false;
    }

    @Override
    // I dont know how to fix the warning that hashCode needs to be updated as well along with equals()
    public int hashCode() {
        return super.hashCode();
    }
}

// package TeTrees.t;

class Pair <T, V> {
	T first;
	V second;

	public Pair(T first, V second) {
		this.first = first;
		this.second = second;
	}

	public String toString() { 
		return "(" + this.first.toString() + ", " + this.second.toString() + ")";
	}
}
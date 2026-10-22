"""Counters for one algorithm run."""


class Metrics:
    """Store comparisons, moves, seconds, extra list slots, and DNF status."""
    def __init__(self):
        self.comparisons = 0
        self.moves = 0
        self.elapsed_time = 0.0
        self.peak_extra_memory = 0
        self.dnf = False

    def reset(self):
        self.comparisons = 0
        self.moves = 0
        self.elapsed_time = 0.0
        self.peak_extra_memory = 0
        self.dnf = False

    def to_dict(self):
        return {
            "comparisons": self.comparisons,
            "moves": self.moves,
            "elapsed_time": self.elapsed_time,
            "peak_extra_memory": self.peak_extra_memory,
            "dnf": self.dnf
        }

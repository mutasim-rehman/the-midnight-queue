"""
Metrics tracking for sorting algorithms.
Uses simple, standard Python with no external libraries.
"""


class Metrics:
    """
    Tracks operation counts and performance for a run.
    
    Attributes:
        comparisons: Number of key comparisons performed.
        moves: Number of element writes/moves performed.
        elapsed_time: Execution time in seconds.
        peak_extra_memory: Maximum auxiliary array elements allocated.
        dnf: True if the run exceeded the 5-minute limit.
    """
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

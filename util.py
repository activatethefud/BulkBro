"""Utility functions for BulkBro."""

import pickle


def load_sol(filename):
    """Load a solution from pickle file."""
    with open(filename, 'rb') as f:
        return pickle.load(f)


class statlist:
    def __init__(self):
        self.data = []
        self.len = 0
        self.sum = 0
        self.var = 0
        self.std = 0
        self.avg = 0
        self.max = None
        self.min = None
        self.max_abs = 0

    def append(self, val):
        self.data.append(val)
        self.len += 1
        self.sum += val
        if self.max is None or val > self.max:
            self.max = val
        if self.min is None or val < self.min:
            self.min = val
        self.avg = self.sum / self.len
        delta = val - self.avg
        self.var += delta * delta
        if self.len > 2:
            self.std = (self.var / (self.len - 1)) ** 0.5
        self.max_abs = max(self.max_abs, abs(self.max) if self.max is not None else 0, abs(self.min) if self.min is not None else 0)

    def normalize(self, other):
        return other / (self.max_abs + 0.01)

    def remove_outliers(self):
        pass

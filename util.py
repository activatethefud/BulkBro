"""Utility functions for BulkBro."""

import pickle


def load_sol(filename):
    """Load a solution from pickle file."""
    with open(filename, 'rb') as f:
        return pickle.load(f)

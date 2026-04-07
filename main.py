"""
Entry point for the MariaDB vector-search tuning MVP.

This script connects to MariaDB, runs a small sweep over vector-search
parameters, and stores results in the report table.

The actual benchmark logic lives in `vector_tuner.py`.
"""

from vector_tuner import run_benchmark


if __name__ == "__main__":
    run_benchmark()
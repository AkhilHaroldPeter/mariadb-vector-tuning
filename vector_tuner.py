"""
Vector search tuning MVP for MariaDB.

This module:
- connects to MariaDB
- computes exact ground truth results
- builds a VECTOR index for each M value
- runs approximate searches for each ef_search value
- computes recall and QPS
- stores results in a report table

The goal is to provide a small but real benchmark harness for testing
vector-search tradeoffs in MariaDB.
"""

from __future__ import annotations

import time
from typing import List, Tuple

import pymysql


DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "root",
    "database": "vector_test",
    "port": 3307,
}

QUERY_VECTOR = "[0.1,0.2,0.3,0.4]"


# Number of nearest neighbors to retrieve
K = 1


CONFIGS: List[Tuple[int, int]] = [
    (4, 10),
    (4, 20),
    (8, 20),
    (8, 40),
    (16, 40),
    (16, 80),
]


def connect_db():
    """Create and return a MariaDB connection and cursor."""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    return conn, cursor


def get_ground_truth(cursor) -> List[int]:
    """Return the exact top-K nearest neighbors using exact vector distance."""
    sql = f"""
    SELECT id
    FROM data
    ORDER BY VEC_DISTANCE_COSINE(v, VEC_FromText('{QUERY_VECTOR}'))
    LIMIT {K}
    """
    cursor.execute(sql)
    return [row[0] for row in cursor.fetchall()]


def build_index(cursor, conn, M: int) -> float:
    """Drop and rebuild the VECTOR index for the given M value.

    Returns:
        Build time in seconds.
    """
    try:
        cursor.execute("DROP INDEX idx_vec ON data")
        conn.commit()
    except Exception:
        pass

    start = time.time()

    cursor.execute(
        f"""
        CREATE VECTOR INDEX idx_vec
        ON data(v)
        M={M}
        """
    )
    conn.commit()

    return time.time() - start


def run_query(cursor, ef: int) -> tuple[list[int], float]:
    """Run one approximate vector search with the given ef_search value.

    Returns:
        A tuple of (result_ids, query_duration_seconds).
    """
    cursor.execute(f"SET SESSION mhnsw_ef_search = {ef}")

    start = time.time()

    cursor.execute(
        f"""
        SELECT id
        FROM data
        ORDER BY VEC_DISTANCE_COSINE(v, VEC_FromText('{QUERY_VECTOR}'))
        LIMIT {K}
        """
    )

    results = [row[0] for row in cursor.fetchall()]
    duration = time.time() - start

    return results, duration


def compute_recall(ground_truth: list[int], approx: list[int]) -> float:
    """Compute recall as overlap / ground_truth_size."""
    if not ground_truth:
        return 0.0
    return len(set(ground_truth) & set(approx)) / len(ground_truth)


def run_benchmark() -> None:
    """Run the full benchmark sweep and store results in the report table."""
    conn, cursor = connect_db()

    try:
        ground_truth = get_ground_truth(cursor)
        print("Ground Truth:", ground_truth)

        print(f"{'M':<5}{'ef':<5}{'Recall':<10}{'QPS':<10}{'Build Time'}")
        print("-" * 50)

        for M, ef in CONFIGS:
            build_time = build_index(cursor, conn, M)
            results, query_time = run_query(cursor, ef)

            recall = compute_recall(ground_truth, results)
            qps = 1 / query_time if query_time > 0 else 0.0

            cursor.execute(
                """
                INSERT INTO report (M, ef_search, recall, build_time, qps)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (M, ef, recall, build_time, qps),
            )
            conn.commit()

            print(f"{M:<5}{ef:<5}{recall:<10.2f}{qps:<10.2f}{build_time:.4f}")

    finally:
        cursor.close()
        conn.close()
# MariaDB Vector Search Tuning MVP

This repository contains a small benchmark tool for evaluating vector-search tuning in MariaDB using the HNSW index. The goal is to compare different index configurations and measure the trade-off between recall, query speed, and index build time.

## What this project does

The script:
- connects to MariaDB
- reads vectors from a local table
- computes exact ground-truth nearest neighbors
- builds a VECTOR index for different `M` values
- runs approximate search for different `ef_search` values
- computes recall
- measures query speed (QPS)
- stores benchmark results in a `report` table

## Requirements

- Python 3.9+
- MariaDB Server with VECTOR support
- `pymysql` Python package

### Install Python dependency

```bash
pip install pymysql
```

## MariaDB setup

### 1) Start MariaDB

Make sure MariaDB is running on the expected port.

This project uses:
- host: `127.0.0.1`
- port: `3307`
- user: `root`
- password: `root`
- database: `vector_test`


⚠️ Note:  
The `user` and `password` values are placeholders. Replace them with your actual MariaDB credentials based on your local setup.

Make sure to update them in:
- `README.md` (if you copy commands)
- `vector_tuner.py` → `DB_CONFIG`

If your MariaDB runs on a different port or with different credentials, update `DB_CONFIG` in `vector_tuner.py`.

### 2) Create the database and tables

Run the SQL setup script:

```sql
CREATE DATABASE vector_test;
USE vector_test;
```

Then create:
- a `data` table for vectors
- a `report` table for benchmark results

The `data` table uses `VECTOR(4)` in this MVP.

### 3) Load sample vectors

The sample setup inserts a few fixed vectors plus additional randomly generated vectors. This gives the benchmark enough data to test multiple configurations.

## How to run

### 1) Prepare the database

Run the SQL setup file first.

### 2) Run the benchmark

```bash
python main.py
```

### 3) Check results

The benchmark prints a summary in the terminal and inserts rows into the `report` table.

To inspect the report:

```sql
SELECT * FROM report;
```

## File structure

```text
.
├── main.py
├── vector_tuner.py
├── sql/
│   └── setup.sql
├── README.md
└── .gitignore
```

## What the key parameters mean

### `K`

`K` is the number of nearest neighbors returned for each query.

Example:
- `K = 10` means return the top 10 closest vectors
- `K = 200` means return the top 200 closest vectors

Why it matters:
- Smaller `K` makes evaluation stricter
- Larger `K` makes recall easier to achieve

In this MVP, `K` is intentionally large enough to evaluate a meaningful slice of the result set.

### `M`

`M` controls the graph connectivity of the HNSW index.

Intuition:
- lower `M` = fewer links, faster build, lower memory, possibly lower recall
- higher `M` = more links, slower build, more memory, usually better recall

This is one of the main tuning knobs for index quality.

### `ef_search`

`ef_search` controls how much of the graph MariaDB explores during search.

Intuition:
- lower `ef_search` = faster queries, lower recall
- higher `ef_search` = slower queries, better recall

This is the main tuning knob for query-time accuracy vs speed.

### `QPS`

QPS stands for queries per second.

It is a simple way to measure how fast the search runs.
Higher QPS means faster query execution.

### `build_time`

This is the time required to build the VECTOR index for a given `M` value.

Higher `M` usually increases build time because the graph becomes denser.

## How the benchmark works

1. Compute exact nearest neighbors using `VEC_DISTANCE_COSINE`
2. Build a VECTOR index with a chosen `M`
3. Set `mhnsw_ef_search`
4. Run approximate search
5. Compare approximate results with ground truth
6. Compute recall
7. Measure query speed and build time
8. Store the result in `report`

## Output example

```text
M    ef   Recall    QPS       Build Time
--------------------------------------------------
4    10   0.85      520.26    0.1145
8    40   0.95      495.96    0.1265
16   80   1.00      331.12    0.1712
```

## Notes

- This is an MVP and is intentionally small.
- The benchmark is designed to be easy to extend with more data, more queries, and additional metrics.
- If your MariaDB setup uses a different host, port, user, or password, update the connection settings in the Python code.

## Next improvements

Possible future additions:
- multiple query vectors instead of a single query
- CSV export
- HTML report
- plotting recall vs QPS
- support for larger datasets
- sampling from an existing user table




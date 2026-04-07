-- CREATE DATABASE vector_test;

-- Select the working database for the MVP.
USE vector_test;

-- Start fresh for repeatable experiments.
DROP TABLE IF EXISTS report1;
DROP TABLE IF EXISTS data1;

-- Main vector data table.
-- VECTOR(4) matches the four-dimensional sample vectors used in the MVP.
CREATE TABLE data1 (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  v VECTOR(4) NOT NULL
);

-- Small seed dataset for local testing.
INSERT INTO data1 (v) VALUES
(VEC_FromText('[0.1,0.2,0.3,0.4]')),
(VEC_FromText('[0.2,0.1,0.4,0.3]')),
(VEC_FromText('[0.9,0.8,0.7,0.6]')),
(VEC_FromText('[0.11,0.21,0.31,0.41]')),
(VEC_FromText('[0.5,0.5,0.5,0.5]'));

-- Generate additional random vectors for a slightly more realistic test set.
SET max_recursive_iterations = 1000;

INSERT INTO data1 (v)
SELECT VEC_FromText(
  CONCAT(
    '[',
    ROUND(RAND(), 2), ',',
    ROUND(RAND(), 2), ',',
    ROUND(RAND(), 2), ',',
    ROUND(RAND(), 2),
    ']'
  )
)
FROM (
  WITH RECURSIVE seq AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq WHERE n < 200
  )
  SELECT * FROM seq
) AS t;

-- Optional checks while debugging.
-- SELECT * FROM data;
-- SELECT id, VEC_ToText(v) FROM data;

-- Report table for benchmark results.
CREATE TABLE report1 (
  M INT,
  ef_search INT,
  recall DOUBLE,
  build_time DOUBLE,
  qps DOUBLE
);

-- SELECT * FROM report1;
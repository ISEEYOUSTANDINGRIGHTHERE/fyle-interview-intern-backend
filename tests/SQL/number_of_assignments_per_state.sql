-- Write query to get number of graded assignments for each student:
-- tests/SQL/number_of_assignments_per_state.sql
SELECT state, COUNT(id) AS assignment_count
FROM assignments
WHERE state IN ('DRAFT', 'GRADED', 'SUBMITTED')
GROUP BY state;


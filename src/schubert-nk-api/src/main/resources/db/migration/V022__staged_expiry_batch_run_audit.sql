-- NK-DAT-001/NK-OPS-001; RD OPS-009/MQ-009; UI251 §8/11;
-- SS331 §8.2/341 §9; SSC-078/BUG-238/YKT-189; PT-DB-018.
-- V021 and earlier remain byte-identical. PostgreSQL transactional constraint replacement.
SET ROLE nk_owner;

ALTER TABLE schubert.batch_runs
    DROP CONSTRAINT ck_batch_runs_expiry_audit;

ALTER TABLE schubert.batch_runs
    ADD CONSTRAINT ck_batch_runs_expiry_audit CHECK (
        CASE
            WHEN step <> 'CLEAN_EXPIRY' THEN
                expiry_cutoff_at IS NULL
                AND expiry_before_count IS NULL
                AND expiry_after_count IS NULL
            WHEN expiry_cutoff_at IS NULL
                 AND expiry_before_count IS NULL
                 AND expiry_after_count IS NULL THEN
                status <> 'SUCCESS'
            WHEN expiry_cutoff_at IS NOT NULL
                 AND expiry_before_count IS NOT NULL THEN
                pg_catalog.isfinite(expiry_cutoff_at)
                AND expiry_before_count >= 0
                AND target_count <= expiry_before_count
                AND (
                    (expiry_after_count IS NULL
                     AND status <> 'SUCCESS'
                     AND success_count = 0)
                    OR
                    (expiry_after_count IS NOT NULL
                     AND expiry_after_count >= 0
                     AND expiry_after_count <= expiry_before_count
                     AND (status <> 'SUCCESS'
                          OR (expiry_before_count - expiry_after_count = success_count
                              AND target_count = success_count
                              AND failure_count = 0)))
                )
            ELSE false
        END);

RESET ROLE;

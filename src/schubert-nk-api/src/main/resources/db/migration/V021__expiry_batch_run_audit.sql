-- NK-DAT-001/NK-OPS-001; RD OPS-009/MQ-009; UI251 §8/11;
-- SS331 §8.2/341 §9; SSC-077/BUG-237/YKT-188; PT-DB-016/PT-BAT-284.
-- Append-only migration. V001..020 and existing non-Expiry rows remain unchanged.
SET ROLE nk_owner;

DO $guard$
BEGIN
    IF EXISTS (SELECT 1 FROM schubert.batch_runs
               WHERE step = 'CLEAN_EXPIRY' AND status = 'SUCCESS') THEN
        RAISE EXCEPTION USING ERRCODE='55000',
            MESSAGE='legacy successful Expiry audit requires controlled reconciliation';
    END IF;
END
$guard$;

ALTER TABLE schubert.batch_runs
    ADD COLUMN expiry_cutoff_at timestamptz,
    ADD COLUMN expiry_before_count bigint,
    ADD COLUMN expiry_after_count bigint;

ALTER TABLE schubert.batch_runs
    ADD CONSTRAINT ck_batch_runs_expiry_audit CHECK (
        (step <> 'CLEAN_EXPIRY'
         AND expiry_cutoff_at IS NULL
         AND expiry_before_count IS NULL
         AND expiry_after_count IS NULL)
        OR
        (step = 'CLEAN_EXPIRY'
         AND (
             (expiry_cutoff_at IS NULL
              AND expiry_before_count IS NULL
              AND expiry_after_count IS NULL
              AND status <> 'SUCCESS')
             OR
             (expiry_cutoff_at IS NOT NULL
              AND expiry_before_count IS NOT NULL
              AND expiry_after_count IS NOT NULL
              AND pg_catalog.isfinite(expiry_cutoff_at)
              AND expiry_before_count >= 0
              AND expiry_after_count >= 0
              AND expiry_after_count <= expiry_before_count
              AND (status <> 'SUCCESS'
                   OR (expiry_before_count - expiry_after_count = success_count
                       AND target_count = success_count
                       AND failure_count = 0))))));

RESET ROLE;

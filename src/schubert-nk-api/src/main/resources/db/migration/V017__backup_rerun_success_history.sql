-- NK-DAT-001; DAT-009/OPS-009/BAK; UI251 section11; SS331 section8.2/341 section11.
-- SSC-054/BUG-138/YKT-108/PG-D-145; PT-DB-INBOX-233..240.
-- V001..016 immutable. Preserve successful backup history; no table/grant/retention changes.
SET ROLE nk_owner;

DROP INDEX schubert.uq_batch_runs_business_step_success;
CREATE UNIQUE INDEX uq_batch_runs_business_step_success ON schubert.batch_runs (business_date, step)
    WHERE status = 'SUCCESS' AND step NOT IN ('BACKUP_DB', 'BACKUP_CONFIG');

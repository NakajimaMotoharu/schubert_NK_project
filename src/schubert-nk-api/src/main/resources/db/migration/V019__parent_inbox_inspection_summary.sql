-- NK-DAT-001; DAT-009/OPS-009/MQ-008/UI212/241/251; SS331 3.13/332/341 7.3.
-- SSC049/PG-D-162; PT-DB-INBOX-251..258. V001..018 immutable.
SET ROLE nk_owner;

CREATE FUNCTION schubert.maintenance_read_inbox_summary(p_run_id uuid,p_cutoff timestamptz)
RETURNS TABLE(inspected_count bigint,deleted_count bigint,protected_count bigint,complete boolean)
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, schubert
SET timezone = 'UTC'
AS $function$
DECLARE progress schubert.inbox_inspection_progress;
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR NOT pg_catalog.isfinite(p_cutoff)
       OR p_cutoff < timestamptz '0001-01-01 00:00:00+00'
       OR p_cutoff >= timestamptz '10000-01-01 00:00:00+00' THEN
        RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='invalid inspection summary argument';
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_catalog.pg_locks
         WHERE locktype='advisory' AND pid=pg_catalog.pg_backend_pid()
           AND database=(SELECT oid FROM pg_catalog.pg_database
                          WHERE datname=pg_catalog.current_database())
           AND classid=0 AND objid=71419602 AND objsubid=1
           AND mode='ExclusiveLock' AND granted) THEN
        RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='inspection summary lock required';
    END IF;
    -- One PK observation, no row lock/DML/cache or private projection to the caller.
    SELECT p.* INTO progress FROM schubert.inbox_inspection_progress p WHERE p.run_id=p_run_id;
    IF NOT FOUND THEN RETURN; END IF;
    IF progress.cutoff<>p_cutoff THEN
        RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='inspection summary identity mismatch';
    END IF;
    RETURN QUERY SELECT progress.inspected_count,progress.deleted_count,
                        progress.protected_count,progress.completed_at IS NOT NULL;
END
$function$;

REVOKE ALL ON FUNCTION schubert.maintenance_read_inbox_summary(uuid,timestamptz) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION schubert.maintenance_read_inbox_summary(uuid,timestamptz) TO schubert_batch;
RESET ROLE;

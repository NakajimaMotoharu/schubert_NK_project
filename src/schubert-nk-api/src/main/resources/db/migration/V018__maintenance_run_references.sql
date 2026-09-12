-- NK-DAT-001; DAT-009/OPS-009; UI251; SS331 3.12/332/343 6.15.
-- SSC-055/PG-D-159; PT-DB-INBOX-241..248; V001..017 remain immutable.
-- Observation only: caller retains OS/DB exclusion through the related file operation.
SET ROLE nk_owner;

CREATE FUNCTION schubert.maintenance_read_run_references(p_run_id uuid,p_cutoff timestamptz)
RETURNS TABLE(has_batch_history boolean,has_inbox_progress boolean,
              has_log_progress boolean,identity_consistent boolean)
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, schubert
SET timezone = 'UTC'
AS $function$
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR NOT pg_catalog.isfinite(p_cutoff)
       OR p_cutoff < timestamptz '0001-01-01 00:00:00+00'
       OR p_cutoff >= timestamptz '10000-01-01 00:00:00+00' THEN
        RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='invalid run reference argument';
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_catalog.pg_locks
         WHERE locktype='advisory' AND pid=pg_catalog.pg_backend_pid()
           AND database=(SELECT oid FROM pg_catalog.pg_database
                          WHERE datname=pg_catalog.current_database())
           AND classid=0 AND objid=71419602 AND objsubid=1
           AND mode='ExclusiveLock' AND granted) THEN
        RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='run reference lock required';
    END IF;
    -- All four values share one statement snapshot. Never filter by age/status or backfill.
    RETURN QUERY SELECT
        EXISTS(SELECT 1 FROM schubert.batch_runs b WHERE b.run_id=p_run_id),
        EXISTS(SELECT 1 FROM schubert.inbox_inspection_progress i WHERE i.run_id=p_run_id),
        EXISTS(SELECT 1 FROM schubert.log_cleanup_progress l WHERE l.run_id=p_run_id),
        NOT EXISTS(SELECT 1 FROM schubert.batch_runs b WHERE b.run_id=p_run_id
                    AND b.business_date<>(p_cutoff AT TIME ZONE 'Asia/Tokyo')::date)
        AND NOT EXISTS(SELECT 1 FROM schubert.inbox_inspection_progress i
                        WHERE i.run_id=p_run_id AND i.cutoff<>p_cutoff)
        AND NOT EXISTS(SELECT 1 FROM schubert.log_cleanup_progress l
                        WHERE l.run_id=p_run_id AND l.cutoff<>p_cutoff);
END
$function$;

REVOKE ALL ON FUNCTION schubert.maintenance_read_run_references(uuid,timestamptz) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION schubert.maintenance_read_run_references(uuid,timestamptz) TO schubert_batch;
RESET ROLE;

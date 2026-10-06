-- NK-DAT-001/OPS009/DAT009/UI251/SS331341343; SSC200201/BUG788/YKT562; REF200001.
-- Readonly complete progress seal. No raw cursor, baseline grant or old migration changes.
SET ROLE nk_owner;
CREATE FUNCTION schubert.maintenance_read_success_progress(
    p_run_id uuid,p_cutoff timestamptz,p_step text,p_ended timestamptz)
RETURNS TABLE(proof_sha256 text)
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, schubert
SET timezone = 'UTC'
AS $function$
DECLARE
    log_progress schubert.log_cleanup_progress;
    inbox_progress schubert.inbox_inspection_progress;
    canonical text;
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR p_ended IS NULL OR p_step IS NULL
       OR p_step NOT IN ('CLEAN_LOG','CLEAN_INBOX_OUTBOX')
       OR NOT pg_catalog.isfinite(p_cutoff) OR NOT pg_catalog.isfinite(p_ended)
       OR p_cutoff < timestamptz '0001-01-01 00:00:00+00'
       OR p_ended >= timestamptz '10000-01-01 00:00:00+00' OR p_ended<p_cutoff THEN
        RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='invalid success progress argument';
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_catalog.pg_locks
        WHERE locktype='advisory' AND pid=pg_catalog.pg_backend_pid()
          AND database=(SELECT oid FROM pg_catalog.pg_database WHERE datname=pg_catalog.current_database())
          AND classid=0 AND objid=71419602 AND objsubid=1 AND mode='ExclusiveLock' AND granted) THEN
        RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='success progress lock required';
    END IF;
    IF p_step='CLEAN_LOG' THEN
        SELECT p.* INTO log_progress FROM schubert.log_cleanup_progress p WHERE p.run_id=p_run_id;
        IF NOT FOUND THEN RETURN; END IF;
        IF log_progress.cutoff<>p_cutoff OR log_progress.completed_at IS NULL
           OR NOT pg_catalog.isfinite(log_progress.completed_at)
           OR log_progress.completed_at<p_cutoff OR log_progress.completed_at>p_ended
           OR log_progress.target_count<0 OR log_progress.deleted_count<0
           OR log_progress.deleted_count>log_progress.target_count
           OR log_progress.skipped_count<>log_progress.target_count-log_progress.deleted_count
           OR (log_progress.after_logged_at IS NULL)<>(log_progress.after_id IS NULL)
           OR (log_progress.target_count=0)<>(log_progress.after_id IS NULL)
           OR (log_progress.after_id IS NOT NULL AND
             (log_progress.after_id NOT BETWEEN 1 AND 999999999999
              OR NOT pg_catalog.isfinite(log_progress.after_logged_at)
              OR log_progress.after_logged_at>=p_cutoff-interval '2160 hours')) THEN
            RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='success log progress incomplete';
        END IF;
        canonical:=pg_catalog.row_to_json(log_progress)::text;
    ELSE
        SELECT p.* INTO inbox_progress FROM schubert.inbox_inspection_progress p WHERE p.run_id=p_run_id;
        IF NOT FOUND THEN RETURN; END IF;
        IF inbox_progress.cutoff<>p_cutoff OR inbox_progress.completed_at IS NULL
           OR NOT pg_catalog.isfinite(inbox_progress.completed_at)
           OR inbox_progress.completed_at<p_cutoff OR inbox_progress.completed_at>p_ended
           OR inbox_progress.inspected_count<0 OR inbox_progress.deleted_count<0
           OR inbox_progress.deleted_count>inbox_progress.inspected_count
           OR inbox_progress.protected_count<>inbox_progress.inspected_count-inbox_progress.deleted_count
           OR (inbox_progress.inspected_count=0)<>(inbox_progress.after_message_id IS NULL) THEN
            RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='success inbox progress incomplete';
        END IF;
        canonical:=pg_catalog.row_to_json(inbox_progress)::text;
    END IF;
    RETURN QUERY SELECT pg_catalog.encode(pg_catalog.sha256(pg_catalog.convert_to(canonical,'UTF8')),'hex');
END
$function$;
REVOKE ALL ON FUNCTION schubert.maintenance_read_success_progress(uuid,timestamptz,text,timestamptz) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION schubert.maintenance_read_success_progress(uuid,timestamptz,text,timestamptz) TO schubert_batch;
RESET ROLE;

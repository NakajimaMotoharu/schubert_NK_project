-- NK-DAT-001; DAT-009/MQ-008/OPS-009; UI212/241/251; SS331 3.8/341 7.3/343.
-- QA-046/UIC-006/SSC-049/PG-D-127; BUG-014/YKT-012; PT-DB-INBOX-073..080.
-- Progress and inspected deletion MUST commit in the same private Java-owned transaction.
SET ROLE nk_owner;

CREATE TABLE schubert.inbox_inspection_progress (
    run_id uuid NOT NULL,
    cutoff timestamptz NOT NULL,
    after_message_id uuid,
    inspected_count bigint NOT NULL DEFAULT 0,
    deleted_count bigint NOT NULL DEFAULT 0,
    protected_count bigint NOT NULL DEFAULT 0,
    completed_at timestamptz,
    CONSTRAINT pk_inbox_inspection_progress PRIMARY KEY (run_id),
    CONSTRAINT ck_inbox_inspection_progress_cutoff CHECK (pg_catalog.isfinite(cutoff)),
    CONSTRAINT ck_inbox_inspection_progress_counts CHECK (
        inspected_count >= 0 AND deleted_count >= 0 AND deleted_count <= inspected_count
        AND protected_count >= 0 AND protected_count = inspected_count - deleted_count),
    CONSTRAINT ck_inbox_inspection_progress_cursor CHECK (
        (inspected_count = 0) = (after_message_id IS NULL)),
    CONSTRAINT ck_inbox_inspection_progress_completed CHECK (
        completed_at IS NULL OR pg_catalog.isfinite(completed_at))
);
CREATE INDEX ix_inbox_inspection_progress_completed
    ON schubert.inbox_inspection_progress(completed_at,run_id) WHERE completed_at IS NOT NULL;
-- V005 default privileges are too broad for this private control table.
REVOKE ALL ON schubert.inbox_inspection_progress FROM PUBLIC,schubert_app;
GRANT SELECT ON schubert.inbox_inspection_progress TO schubert_backup;

CREATE FUNCTION schubert.maintenance_open_inbox_inspection(p_run_id uuid,p_cutoff timestamptz)
RETURNS SETOF schubert.inbox_inspection_progress
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, schubert
SET timezone = 'UTC'
AS $function$
DECLARE progress schubert.inbox_inspection_progress;
BEGIN
    PERFORM schubert.maintenance_lock_inbox_backup(p_run_id,p_cutoff);
    INSERT INTO schubert.inbox_inspection_progress(run_id,cutoff) VALUES(p_run_id,p_cutoff)
        ON CONFLICT(run_id) DO NOTHING;
    SELECT p.run_id,p.cutoff,p.after_message_id,p.inspected_count,p.deleted_count,
           p.protected_count,p.completed_at INTO progress
      FROM schubert.inbox_inspection_progress p WHERE p.run_id=p_run_id FOR UPDATE;
    IF progress.cutoff <> p_cutoff THEN
        RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='inspection cutoff mismatch';
    END IF;
    RETURN NEXT progress;
END
$function$;

CREATE FUNCTION schubert.maintenance_record_inbox_inspection(
    p_run_id uuid,p_cutoff timestamptz,p_expected_after uuid,p_expected_count bigint,
    p_message_id uuid,p_outcome text,p_expected_xact text)
RETURNS SETOF schubert.inbox_inspection_progress
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, schubert
SET timezone = 'UTC'
AS $function$
DECLARE progress schubert.inbox_inspection_progress;
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR NOT pg_catalog.isfinite(p_cutoff)
       OR p_expected_count IS NULL OR p_expected_count < 0
       OR p_outcome IS NULL OR p_outcome NOT IN ('DELETED','PROTECTED','END')
       OR ((p_outcome='END') <> (p_message_id IS NULL))
       OR p_expected_xact IS NULL OR p_expected_xact !~ '^[0-9]{1,20}$' THEN
        RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='invalid inspection checkpoint argument';
    END IF;
    IF p_expected_xact <> pg_catalog.pg_current_xact_id()::text THEN
        RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='inspection transaction mismatch';
    END IF;
    PERFORM schubert.maintenance_lock_inbox_backup(p_run_id,p_cutoff);
    SELECT p.run_id,p.cutoff,p.after_message_id,p.inspected_count,p.deleted_count,
           p.protected_count,p.completed_at INTO progress
      FROM schubert.inbox_inspection_progress p WHERE p.run_id=p_run_id FOR UPDATE;
    IF NOT FOUND OR progress.cutoff <> p_cutoff OR progress.completed_at IS NOT NULL
       OR progress.after_message_id IS DISTINCT FROM p_expected_after
       OR progress.inspected_count <> p_expected_count THEN
        RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='inspection checkpoint is stale';
    END IF;
    IF p_outcome='END' THEN
        IF EXISTS(SELECT 1 FROM schubert.request_inbox i
                   WHERE i.processing_state IN ('COMPLETED','ERROR') AND i.expires_at<p_cutoff
                     AND (p_expected_after IS NULL OR i.message_id>p_expected_after)) THEN
            RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='inspection candidates remain';
        END IF;
        UPDATE schubert.inbox_inspection_progress p SET completed_at=pg_catalog.clock_timestamp()
         WHERE p.run_id=p_run_id;
    ELSE
        IF p_expected_after IS NOT NULL AND p_message_id<=p_expected_after THEN
            RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='inspection cursor did not advance';
        END IF;
        IF p_outcome='DELETED' THEN
            IF EXISTS(SELECT 1 FROM schubert.request_inbox i WHERE i.message_id=p_message_id) THEN
                RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='inspection deletion is not applied';
            END IF;
        ELSE
            PERFORM i.message_id FROM schubert.request_inbox i
             WHERE i.message_id=p_message_id AND i.processing_state IN ('COMPLETED','ERROR')
               AND i.expires_at<p_cutoff FOR UPDATE;
            IF NOT FOUND THEN
                RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='protected inspection candidate is missing';
            END IF;
        END IF;
        UPDATE schubert.inbox_inspection_progress p
           SET after_message_id=p_message_id,inspected_count=p.inspected_count+1,
               deleted_count=p.deleted_count+CASE WHEN p_outcome='DELETED' THEN 1 ELSE 0 END,
               protected_count=p.protected_count+CASE WHEN p_outcome='PROTECTED' THEN 1 ELSE 0 END
         WHERE p.run_id=p_run_id;
    END IF;
    RETURN QUERY SELECT p.run_id,p.cutoff,p.after_message_id,p.inspected_count,p.deleted_count,
                        p.protected_count,p.completed_at
                   FROM schubert.inbox_inspection_progress p WHERE p.run_id=p_run_id;
END
$function$;

CREATE FUNCTION schubert.maintenance_cleanup_inbox_progress(
    p_run_id uuid,p_cutoff timestamptz,p_limit integer)
RETURNS TABLE(target_count bigint,deleted_count bigint,skipped_count bigint,reason_code varchar(32))
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, schubert, schubert_web_session
SET timezone = 'UTC'
AS $function$
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR NOT pg_catalog.isfinite(p_cutoff)
       OR p_limit IS NULL OR p_limit NOT BETWEEN 1 AND 1000 THEN
        RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='invalid cleanup argument';
    END IF;
    BEGIN
        PERFORM schubert.maintenance_lock_inbox_backup(p_run_id,p_cutoff);
    EXCEPTION
        WHEN lock_not_available THEN
            RETURN QUERY SELECT 0::bigint,0::bigint,0::bigint,'LOCK_BUSY'::varchar(32);
            RETURN;
        WHEN object_not_in_prerequisite_state THEN
            RETURN QUERY SELECT 0::bigint,0::bigint,0::bigint,'BACKUP_GATE'::varchar(32);
            RETURN;
    END;
    RETURN QUERY WITH candidate AS (
        SELECT p.run_id FROM schubert.inbox_inspection_progress p
         WHERE p.completed_at<p_cutoff-interval '9600 hours' AND p.run_id<>p_run_id
           AND NOT EXISTS(SELECT 1 FROM schubert.batch_runs b
                           WHERE b.run_id=p.run_id AND b.status IN ('RUNNING','FAILED'))
         ORDER BY p.completed_at,p.run_id FOR UPDATE SKIP LOCKED LIMIT p_limit
    ), removed AS (
        DELETE FROM schubert.inbox_inspection_progress p USING candidate c
         WHERE p.run_id=c.run_id RETURNING p.run_id
    )
    SELECT (SELECT count(*) FROM candidate),(SELECT count(*) FROM removed),0::bigint,'OK'::varchar(32);
END
$function$;

REVOKE ALL ON FUNCTION schubert.maintenance_open_inbox_inspection(uuid,timestamptz) FROM PUBLIC;
REVOKE ALL ON FUNCTION schubert.maintenance_record_inbox_inspection(uuid,timestamptz,uuid,bigint,uuid,text,text) FROM PUBLIC;
REVOKE ALL ON FUNCTION schubert.maintenance_cleanup_inbox_progress(uuid,timestamptz,integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION schubert.maintenance_open_inbox_inspection(uuid,timestamptz),
    schubert.maintenance_record_inbox_inspection(uuid,timestamptz,uuid,bigint,uuid,text,text)
    TO schubert_inbox_inspector;
GRANT EXECUTE ON FUNCTION schubert.maintenance_cleanup_inbox_progress(uuid,timestamptz,integer) TO schubert_batch;
RESET ROLE;

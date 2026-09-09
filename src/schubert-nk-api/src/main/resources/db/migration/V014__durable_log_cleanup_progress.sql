-- NK-DAT-001; DAT-009/OPS-009; UI251; SS331 3.9/332 11.4/341 7.2.
-- SSC-051/PG-D-136; BUG-104/YKT-092/012; PT-DB-INBOX-153..160.
-- Hold rows advance a durable cursor without deletion; all state changes share the caller TX.
SET ROLE nk_owner;

CREATE TABLE schubert.log_cleanup_progress (
    run_id uuid NOT NULL,
    cutoff timestamptz NOT NULL,
    after_logged_at timestamptz,
    after_id bigint,
    target_count bigint NOT NULL DEFAULT 0,
    deleted_count bigint NOT NULL DEFAULT 0,
    skipped_count bigint NOT NULL DEFAULT 0,
    completed_at timestamptz,
    CONSTRAINT pk_log_cleanup_progress PRIMARY KEY (run_id),
    CONSTRAINT ck_log_cleanup_progress_cutoff CHECK (pg_catalog.isfinite(cutoff)),
    CONSTRAINT ck_log_cleanup_progress_counts CHECK (
        target_count >= 0 AND deleted_count >= 0 AND deleted_count <= target_count
        AND skipped_count >= 0 AND skipped_count = target_count - deleted_count),
    CONSTRAINT ck_log_cleanup_progress_cursor CHECK (
        (after_logged_at IS NULL) = (after_id IS NULL)
        AND (target_count = 0) = (after_id IS NULL)),
    CONSTRAINT ck_log_cleanup_progress_position CHECK (
        after_id IS NULL OR (after_id BETWEEN 1 AND 999999999999
        AND pg_catalog.isfinite(after_logged_at)
        AND after_logged_at < cutoff - interval '2160 hours')),
    CONSTRAINT ck_log_cleanup_progress_completed CHECK (
        completed_at IS NULL OR pg_catalog.isfinite(completed_at))
);
CREATE INDEX ix_log_cleanup_progress_completed
    ON schubert.log_cleanup_progress(completed_at,run_id) WHERE completed_at IS NOT NULL;
REVOKE ALL ON schubert.log_cleanup_progress FROM PUBLIC,schubert_app;
GRANT SELECT ON schubert.log_cleanup_progress TO schubert_backup;

CREATE OR REPLACE FUNCTION schubert.maintenance_cleanup_logs(
    p_run_id uuid,p_cutoff timestamptz,p_limit integer)
RETURNS TABLE(target_count bigint,deleted_count bigint,skipped_count bigint,reason_code varchar(32))
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, schubert, schubert_web_session
SET timezone = 'UTC'
AS $function$
DECLARE
    progress schubert.log_cleanup_progress;
    log_cutoff timestamptz;
    selected_count bigint;
    removed_count bigint;
    held_count bigint;
    last_time timestamptz;
    last_id bigint;
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR NOT pg_catalog.isfinite(p_cutoff)
       OR p_limit IS NULL OR p_limit NOT BETWEEN 1 AND 10000 THEN
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
    -- NOWAIT failure rolls back this entire block, including the first progress INSERT.
    BEGIN
        INSERT INTO schubert.log_cleanup_progress(run_id,cutoff) VALUES(p_run_id,p_cutoff)
            ON CONFLICT(run_id) DO NOTHING;
        SELECT p.run_id,p.cutoff,p.after_logged_at,p.after_id,p.target_count,p.deleted_count,
               p.skipped_count,p.completed_at INTO progress
          FROM schubert.log_cleanup_progress p WHERE p.run_id=p_run_id FOR UPDATE NOWAIT;
        IF progress.cutoff <> p_cutoff THEN
            RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='log cleanup cutoff mismatch';
        END IF;
        IF progress.completed_at IS NOT NULL THEN
            RETURN QUERY SELECT 0::bigint,0::bigint,0::bigint,'OK'::varchar(32);
            RETURN;
        END IF;
        log_cutoff := p_cutoff - interval '2160 hours';
        WITH candidate AS MATERIALIZED (
            SELECT l.id,l.logged_at,l.security_hold_until FROM schubert.app_logs l
             WHERE l.logged_at < log_cutoff
               AND (progress.after_id IS NULL
                    OR (l.logged_at,l.id) > (progress.after_logged_at,progress.after_id))
             ORDER BY l.logged_at,l.id LIMIT p_limit FOR UPDATE NOWAIT
        ), removed AS (
            DELETE FROM schubert.app_logs l USING candidate c
             WHERE l.id=c.id
               AND (c.security_hold_until IS NULL OR c.security_hold_until<=log_cutoff)
            RETURNING l.id
        )
        SELECT (SELECT count(*) FROM candidate),(SELECT count(*) FROM removed),
               (SELECT count(*) FROM candidate c WHERE c.security_hold_until>log_cutoff),
               (SELECT c.logged_at FROM candidate c ORDER BY c.logged_at DESC,c.id DESC LIMIT 1),
               (SELECT c.id FROM candidate c ORDER BY c.logged_at DESC,c.id DESC LIMIT 1)
          INTO selected_count,removed_count,held_count,last_time,last_id;
        IF selected_count=0 THEN
            UPDATE schubert.log_cleanup_progress p SET completed_at=pg_catalog.clock_timestamp()
             WHERE p.run_id=p_run_id;
        ELSE
            UPDATE schubert.log_cleanup_progress p
               SET after_logged_at=last_time,after_id=last_id,
                   target_count=p.target_count+selected_count,
                   deleted_count=p.deleted_count+removed_count,
                   skipped_count=p.skipped_count+held_count
             WHERE p.run_id=p_run_id;
        END IF;
        RETURN QUERY SELECT selected_count,removed_count,held_count,'OK'::varchar(32);
    EXCEPTION
        WHEN lock_not_available THEN
            RETURN QUERY SELECT 0::bigint,0::bigint,0::bigint,'LOCK_BUSY'::varchar(32);
    END;
END
$function$;

CREATE FUNCTION schubert.maintenance_read_log_cleanup_progress(p_run_id uuid,p_cutoff timestamptz)
RETURNS TABLE(target_count bigint,deleted_count bigint,skipped_count bigint,complete boolean)
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, schubert, schubert_web_session
SET timezone = 'UTC'
AS $function$
DECLARE progress schubert.log_cleanup_progress;
BEGIN
    PERFORM schubert.maintenance_lock_inbox_backup(p_run_id,p_cutoff);
    SELECT p.run_id,p.cutoff,p.after_logged_at,p.after_id,p.target_count,p.deleted_count,
           p.skipped_count,p.completed_at INTO progress
      FROM schubert.log_cleanup_progress p WHERE p.run_id=p_run_id FOR SHARE NOWAIT;
    IF NOT FOUND THEN
        RETURN QUERY SELECT 0::bigint,0::bigint,0::bigint,false;
    ELSE
        IF progress.cutoff<>p_cutoff THEN
            RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='log cleanup cutoff mismatch';
        END IF;
        RETURN QUERY SELECT progress.target_count,progress.deleted_count,progress.skipped_count,
                            progress.completed_at IS NOT NULL;
    END IF;
END
$function$;

CREATE FUNCTION schubert.maintenance_cleanup_log_progress(
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
        SELECT p.run_id FROM schubert.log_cleanup_progress p
         WHERE p.completed_at<p_cutoff-interval '9600 hours' AND p.run_id<>p_run_id
           AND NOT EXISTS(SELECT 1 FROM schubert.batch_runs b
                           WHERE b.run_id=p.run_id AND b.status IN ('RUNNING','FAILED'))
         ORDER BY p.completed_at,p.run_id FOR UPDATE SKIP LOCKED LIMIT p_limit
    ), removed AS (
        DELETE FROM schubert.log_cleanup_progress p USING candidate c
         WHERE p.run_id=c.run_id RETURNING p.run_id
    )
    SELECT (SELECT count(*) FROM candidate),(SELECT count(*) FROM removed),0::bigint,'OK'::varchar(32);
END
$function$;

REVOKE ALL ON FUNCTION schubert.maintenance_cleanup_logs(uuid,timestamptz,integer) FROM PUBLIC;
REVOKE ALL ON FUNCTION schubert.maintenance_read_log_cleanup_progress(uuid,timestamptz) FROM PUBLIC;
REVOKE ALL ON FUNCTION schubert.maintenance_cleanup_log_progress(uuid,timestamptz,integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION schubert.maintenance_cleanup_logs(uuid,timestamptz,integer),
    schubert.maintenance_read_log_cleanup_progress(uuid,timestamptz),
    schubert.maintenance_cleanup_log_progress(uuid,timestamptz,integer) TO schubert_batch;
RESET ROLE;

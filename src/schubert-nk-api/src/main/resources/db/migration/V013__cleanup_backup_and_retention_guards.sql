-- NK-DAT-001; RD DAT-009/OPS-009; UI251 section6; SS331 section3.3.1/332 section11/341 section7.
-- SSC-050/PG-D-129; BUG-092/093/YKT-083/084; PT-DB-INBOX-089..096.
-- All cutoffs are fixed run-start anchors. No caller-supplied retention override.
-- V001..012 immutable. Existing ACLs retained; PUBLIC remains revoked.
SET ROLE nk_owner;

CREATE OR REPLACE FUNCTION schubert.maintenance_cleanup_notifications(
    p_run_id uuid, p_cutoff timestamptz, p_limit integer)
RETURNS TABLE(target_count bigint, deleted_count bigint, skipped_count bigint, reason_code varchar(32))
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, schubert, schubert_web_session
SET timezone = 'UTC'
AS $function$
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR NOT pg_catalog.isfinite(p_cutoff) OR p_limit IS NULL OR p_limit NOT BETWEEN 1 AND 1000 THEN
        RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'invalid cleanup argument';
    END IF;
    BEGIN
        PERFORM schubert.maintenance_lock_inbox_backup(p_run_id, p_cutoff);
    EXCEPTION
        WHEN SQLSTATE '55P03' THEN
            RETURN QUERY SELECT 0::bigint, 0::bigint, 0::bigint, 'LOCK_BUSY'::varchar(32);
            RETURN;
        WHEN SQLSTATE '55000' THEN
            RETURN QUERY SELECT 0::bigint, 0::bigint, 0::bigint, 'BACKUP_GATE'::varchar(32);
            RETURN;
    END;
    RETURN QUERY
    WITH candidate AS (
        SELECT n.id FROM schubert.notifications n
         WHERE (n.state = 'CANCELLED' AND n.state_changed_at < p_cutoff)
            OR (n.state IN ('COMPLETED', 'ERROR') AND n.state_changed_at <= p_cutoff - interval '24 hours')
         ORDER BY n.id FOR UPDATE SKIP LOCKED LIMIT p_limit
    ), removed AS (
        DELETE FROM schubert.notifications n USING candidate c WHERE n.id = c.id RETURNING n.id
    )
    SELECT (SELECT count(*) FROM candidate), (SELECT count(*) FROM removed), 0::bigint, 'OK'::varchar(32);
END
$function$;

CREATE OR REPLACE FUNCTION schubert.maintenance_cleanup_questions(
    p_run_id uuid, p_cutoff timestamptz, p_limit integer)
RETURNS TABLE(target_count bigint, deleted_count bigint, skipped_count bigint, reason_code varchar(32))
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, schubert, schubert_web_session
SET timezone = 'UTC'
AS $function$
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR NOT pg_catalog.isfinite(p_cutoff) OR p_limit IS NULL OR p_limit NOT BETWEEN 1 AND 1000 THEN
        RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'invalid cleanup argument';
    END IF;
    BEGIN
        PERFORM schubert.maintenance_lock_inbox_backup(p_run_id, p_cutoff);
    EXCEPTION
        WHEN SQLSTATE '55P03' THEN
            RETURN QUERY SELECT 0::bigint, 0::bigint, 0::bigint, 'LOCK_BUSY'::varchar(32);
            RETURN;
        WHEN SQLSTATE '55000' THEN
            RETURN QUERY SELECT 0::bigint, 0::bigint, 0::bigint, 'BACKUP_GATE'::varchar(32);
            RETURN;
    END;
    RETURN QUERY
    WITH candidate AS (
        SELECT q.id FROM schubert.questions q
         WHERE q.is_deleted = true AND q.deleted_at < p_cutoff
           AND NOT EXISTS (SELECT 1 FROM schubert.notifications n WHERE n.question_id = q.id)
         ORDER BY q.id FOR UPDATE SKIP LOCKED LIMIT p_limit
    ), removed AS (
        DELETE FROM schubert.questions q USING candidate c WHERE q.id = c.id RETURNING q.id
    )
    SELECT (SELECT count(*) FROM candidate), (SELECT count(*) FROM removed), 0::bigint, 'OK'::varchar(32);
END
$function$;

CREATE OR REPLACE FUNCTION schubert.maintenance_cleanup_sessions(
    p_run_id uuid, p_cutoff timestamptz, p_limit integer)
RETURNS TABLE(target_count bigint, deleted_count bigint, skipped_count bigint, reason_code varchar(32))
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, schubert, schubert_web_session
SET timezone = 'UTC'
AS $function$
DECLARE
    api_deleted bigint;
    ip_deleted bigint;
    web_deleted bigint;
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR NOT pg_catalog.isfinite(p_cutoff) OR p_limit IS NULL OR p_limit NOT BETWEEN 1 AND 1000 THEN
        RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'invalid cleanup argument';
    END IF;
    BEGIN
        PERFORM schubert.maintenance_lock_inbox_backup(p_run_id, p_cutoff);
    EXCEPTION
        WHEN SQLSTATE '55P03' THEN
            RETURN QUERY SELECT 0::bigint, 0::bigint, 0::bigint, 'LOCK_BUSY'::varchar(32);
            RETURN;
        WHEN SQLSTATE '55000' THEN
            RETURN QUERY SELECT 0::bigint, 0::bigint, 0::bigint, 'BACKUP_GATE'::varchar(32);
            RETURN;
    END;
    WITH candidate AS (
        SELECT s.id FROM schubert.auth_sessions s
         WHERE s.expires_at <= p_cutoff - interval '24 hours'
            OR (s.revoked AND s.revoked_at <= p_cutoff - interval '24 hours')
         ORDER BY s.expires_at, s.id FOR UPDATE SKIP LOCKED LIMIT p_limit
    )
    DELETE FROM schubert.auth_sessions s USING candidate c WHERE s.id = c.id;
    GET DIAGNOSTICS api_deleted = ROW_COUNT;
    WITH candidate AS (
        SELECT a.client_address FROM schubert.login_ip_attempts a
         WHERE greatest(a.window_started_at + interval '15 minutes',
                        coalesce(a.locked_until, '-infinity'::timestamptz))
                   <= p_cutoff - interval '24 hours'
         ORDER BY a.updated_at, a.client_address
         FOR UPDATE SKIP LOCKED LIMIT greatest(p_limit - api_deleted, 0)
    )
    DELETE FROM schubert.login_ip_attempts a USING candidate c
     WHERE a.client_address = c.client_address;
    GET DIAGNOSTICS ip_deleted = ROW_COUNT;
    WITH candidate AS (
        SELECT s.id FROM schubert_web_session.web_http_sessions s
         WHERE s.expires_at <= p_cutoff
         ORDER BY s.expires_at, s.id FOR UPDATE SKIP LOCKED
         LIMIT greatest(p_limit - api_deleted - ip_deleted, 0)
    )
    DELETE FROM schubert_web_session.web_http_sessions s USING candidate c WHERE s.id = c.id;
    GET DIAGNOSTICS web_deleted = ROW_COUNT;
    RETURN QUERY SELECT api_deleted + ip_deleted + web_deleted,
                        api_deleted + ip_deleted + web_deleted,
                        0::bigint, 'OK'::varchar(32);
END
$function$;

CREATE OR REPLACE FUNCTION schubert.maintenance_cleanup_logs(
    p_run_id uuid, p_cutoff timestamptz, p_limit integer)
RETURNS TABLE(target_count bigint, deleted_count bigint, skipped_count bigint, reason_code varchar(32))
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, schubert, schubert_web_session
SET timezone = 'UTC'
AS $function$
DECLARE
    log_cutoff timestamptz;
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR NOT pg_catalog.isfinite(p_cutoff) OR p_limit IS NULL OR p_limit NOT BETWEEN 1 AND 10000 THEN
        RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'invalid cleanup argument';
    END IF;
    BEGIN
        PERFORM schubert.maintenance_lock_inbox_backup(p_run_id, p_cutoff);
    EXCEPTION
        WHEN SQLSTATE '55P03' THEN
            RETURN QUERY SELECT 0::bigint, 0::bigint, 0::bigint, 'LOCK_BUSY'::varchar(32);
            RETURN;
        WHEN SQLSTATE '55000' THEN
            RETURN QUERY SELECT 0::bigint, 0::bigint, 0::bigint, 'BACKUP_GATE'::varchar(32);
            RETURN;
    END;
    log_cutoff := p_cutoff - interval '2160 hours';
    RETURN QUERY
    WITH candidate AS (
        SELECT l.id, l.security_hold_until FROM schubert.app_logs l
         WHERE l.logged_at < log_cutoff
         ORDER BY l.logged_at, l.id FOR UPDATE SKIP LOCKED LIMIT p_limit
    ), removed AS (
        DELETE FROM schubert.app_logs l USING candidate c
         WHERE l.id = c.id
           AND (c.security_hold_until IS NULL OR c.security_hold_until <= log_cutoff)
        RETURNING l.id
    )
    SELECT (SELECT count(*) FROM candidate),
           (SELECT count(*) FROM removed),
           (SELECT count(*) FROM candidate c WHERE c.security_hold_until > log_cutoff),
           'OK'::varchar(32);
END
$function$;

CREATE OR REPLACE FUNCTION schubert.maintenance_cleanup_batch_runs(
    p_run_id uuid, p_cutoff timestamptz, p_limit integer)
RETURNS TABLE(target_count bigint, deleted_count bigint, skipped_count bigint, reason_code varchar(32))
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, schubert, schubert_web_session
SET timezone = 'UTC'
AS $function$
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR NOT pg_catalog.isfinite(p_cutoff) OR p_limit IS NULL OR p_limit NOT BETWEEN 1 AND 1000 THEN
        RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'invalid cleanup argument';
    END IF;
    BEGIN
        PERFORM schubert.maintenance_lock_inbox_backup(p_run_id, p_cutoff);
    EXCEPTION
        WHEN SQLSTATE '55P03' THEN
            RETURN QUERY SELECT 0::bigint, 0::bigint, 0::bigint, 'LOCK_BUSY'::varchar(32);
            RETURN;
        WHEN SQLSTATE '55000' THEN
            RETURN QUERY SELECT 0::bigint, 0::bigint, 0::bigint, 'BACKUP_GATE'::varchar(32);
            RETURN;
    END;
    RETURN QUERY
    WITH candidate AS (
        SELECT b.id FROM schubert.batch_runs b
         WHERE b.ended_at < p_cutoff - interval '9600 hours' AND b.status IN ('SUCCESS', 'WARNING', 'SKIPPED')
           AND b.run_id <> p_run_id
           AND NOT EXISTS (SELECT 1 FROM schubert.batch_runs investigation
                            WHERE investigation.run_id = b.run_id
                              AND investigation.status IN ('RUNNING', 'FAILED'))
         ORDER BY b.ended_at, b.id FOR UPDATE SKIP LOCKED LIMIT p_limit
    ), removed AS (
        DELETE FROM schubert.batch_runs b USING candidate c WHERE b.id = c.id RETURNING b.id
    )
    SELECT (SELECT count(*) FROM candidate), (SELECT count(*) FROM removed), 0::bigint, 'OK'::varchar(32);
END
$function$;

RESET ROLE;

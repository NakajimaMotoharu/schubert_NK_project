-- NK-DAT-001/NK-MSG-002; RD DAT-009/OPS-009; UI241/242/251; SS324 section12/332 section11/341 section7.
-- PT-DB-001/011, PT-IDEM-013; BUG-014 (outbox portion)/BUG-015; YKT-012.
-- Append-only correction: V001..V005 checksums remain unchanged. CREATE OR REPLACE retains ACLs.
-- p_cutoff for message stores is the fixed run anchor, NOT an already age-subtracted threshold.
-- Inbox decrypt/reference protection remains tracked under BUG-014; this migration does not close it.
SET ROLE nk_owner;

CREATE OR REPLACE FUNCTION schubert.maintenance_cleanup_notifications(
    p_run_id uuid, p_cutoff timestamptz, p_limit integer)
RETURNS TABLE(target_count bigint, deleted_count bigint, skipped_count bigint, reason_code varchar(32))
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, schubert, schubert_web_session
AS $function$
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR p_limit IS NULL OR p_limit NOT BETWEEN 1 AND 1000 THEN
        RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'invalid cleanup argument';
    END IF;
    IF NOT pg_catalog.pg_try_advisory_xact_lock(71419602) THEN
        RETURN QUERY SELECT 0::bigint, 0::bigint, 0::bigint, 'LOCK_BUSY'::varchar(32);
        RETURN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM schubert.batch_runs b WHERE b.run_id = p_run_id AND b.step = 'BACKUP_DB' AND b.status = 'SUCCESS')
       OR NOT EXISTS (SELECT 1 FROM schubert.batch_runs b WHERE b.run_id = p_run_id AND b.step = 'BACKUP_CONFIG' AND b.status = 'SUCCESS') THEN
        RETURN QUERY SELECT 0::bigint, 0::bigint, 0::bigint, 'BACKUP_GATE'::varchar(32);
        RETURN;
    END IF;
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
AS $function$
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR p_limit IS NULL OR p_limit NOT BETWEEN 1 AND 1000 THEN
        RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'invalid cleanup argument';
    END IF;
    IF NOT pg_catalog.pg_try_advisory_xact_lock(71419602) THEN
        RETURN QUERY SELECT 0::bigint, 0::bigint, 0::bigint, 'LOCK_BUSY'::varchar(32);
        RETURN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM schubert.batch_runs b WHERE b.run_id = p_run_id AND b.step = 'BACKUP_DB' AND b.status = 'SUCCESS')
       OR NOT EXISTS (SELECT 1 FROM schubert.batch_runs b WHERE b.run_id = p_run_id AND b.step = 'BACKUP_CONFIG' AND b.status = 'SUCCESS') THEN
        RETURN QUERY SELECT 0::bigint, 0::bigint, 0::bigint, 'BACKUP_GATE'::varchar(32);
        RETURN;
    END IF;
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
AS $function$
DECLARE
    api_deleted bigint;
    ip_deleted bigint;
    web_deleted bigint;
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR p_limit IS NULL OR p_limit NOT BETWEEN 1 AND 1000 THEN
        RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'invalid cleanup argument';
    END IF;
    IF NOT pg_catalog.pg_try_advisory_xact_lock(71419602) THEN
        RETURN QUERY SELECT 0::bigint, 0::bigint, 0::bigint, 'LOCK_BUSY'::varchar(32);
        RETURN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM schubert.batch_runs b WHERE b.run_id = p_run_id AND b.step = 'BACKUP_DB' AND b.status = 'SUCCESS')
       OR NOT EXISTS (SELECT 1 FROM schubert.batch_runs b WHERE b.run_id = p_run_id AND b.step = 'BACKUP_CONFIG' AND b.status = 'SUCCESS') THEN
        RETURN QUERY SELECT 0::bigint, 0::bigint, 0::bigint, 'BACKUP_GATE'::varchar(32);
        RETURN;
    END IF;
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

CREATE OR REPLACE FUNCTION schubert.maintenance_cleanup_message_stores(
    p_run_id uuid, p_cutoff timestamptz, p_limit integer)
RETURNS TABLE(target_count bigint, deleted_count bigint, skipped_count bigint, reason_code varchar(32))
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, schubert, schubert_web_session
AS $function$
DECLARE
    inbox_deleted bigint;
    api_outbox_deleted bigint;
    web_outbox_deleted bigint;
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR p_limit IS NULL OR p_limit NOT BETWEEN 1 AND 1000 THEN
        RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'invalid cleanup argument';
    END IF;
    IF NOT pg_catalog.pg_try_advisory_xact_lock(71419602) THEN
        RETURN QUERY SELECT 0::bigint, 0::bigint, 0::bigint, 'LOCK_BUSY'::varchar(32);
        RETURN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM schubert.batch_runs b WHERE b.run_id = p_run_id AND b.step = 'BACKUP_DB' AND b.status = 'SUCCESS')
       OR NOT EXISTS (SELECT 1 FROM schubert.batch_runs b WHERE b.run_id = p_run_id AND b.step = 'BACKUP_CONFIG' AND b.status = 'SUCCESS') THEN
        RETURN QUERY SELECT 0::bigint, 0::bigint, 0::bigint, 'BACKUP_GATE'::varchar(32);
        RETURN;
    END IF;
    WITH candidate AS (
        SELECT i.message_id FROM schubert.request_inbox i
         WHERE i.processing_state <> 'PROCESSING' AND i.expires_at < p_cutoff
         ORDER BY i.expires_at, i.message_id FOR UPDATE SKIP LOCKED LIMIT p_limit
    )
    DELETE FROM schubert.request_inbox i USING candidate c WHERE i.message_id = c.message_id;
    GET DIAGNOSTICS inbox_deleted = ROW_COUNT;
    WITH candidate AS (
        SELECT o.id FROM schubert.mq_outbox o
         WHERE o.status = 'SENT' AND o.sent_at < p_cutoff - interval '168 hours'
           AND (o.lease_until IS NULL OR o.lease_until < p_cutoff)
         ORDER BY o.id FOR UPDATE SKIP LOCKED LIMIT greatest(p_limit - inbox_deleted, 0)
    )
    DELETE FROM schubert.mq_outbox o USING candidate c WHERE o.id = c.id;
    GET DIAGNOSTICS api_outbox_deleted = ROW_COUNT;
    WITH candidate AS (
        SELECT o.id FROM schubert_web_session.web_log_outbox o
         WHERE o.status = 'SENT' AND o.sent_at < p_cutoff - interval '168 hours'
           AND (o.lease_until IS NULL OR o.lease_until < p_cutoff)
         ORDER BY o.id FOR UPDATE SKIP LOCKED LIMIT greatest(p_limit - inbox_deleted - api_outbox_deleted, 0)
    )
    DELETE FROM schubert_web_session.web_log_outbox o USING candidate c WHERE o.id = c.id;
    GET DIAGNOSTICS web_outbox_deleted = ROW_COUNT;
    RETURN QUERY SELECT inbox_deleted + api_outbox_deleted + web_outbox_deleted,
                        inbox_deleted + api_outbox_deleted + web_outbox_deleted,
                        0::bigint, 'OK'::varchar(32);
END
$function$;

CREATE OR REPLACE FUNCTION schubert.maintenance_cleanup_logs(
    p_run_id uuid, p_cutoff timestamptz, p_limit integer)
RETURNS TABLE(target_count bigint, deleted_count bigint, skipped_count bigint, reason_code varchar(32))
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, schubert, schubert_web_session
AS $function$
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR p_limit IS NULL OR p_limit NOT BETWEEN 1 AND 10000 THEN
        RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'invalid cleanup argument';
    END IF;
    IF NOT pg_catalog.pg_try_advisory_xact_lock(71419602) THEN
        RETURN QUERY SELECT 0::bigint, 0::bigint, 0::bigint, 'LOCK_BUSY'::varchar(32);
        RETURN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM schubert.batch_runs b WHERE b.run_id = p_run_id AND b.step = 'BACKUP_DB' AND b.status = 'SUCCESS')
       OR NOT EXISTS (SELECT 1 FROM schubert.batch_runs b WHERE b.run_id = p_run_id AND b.step = 'BACKUP_CONFIG' AND b.status = 'SUCCESS') THEN
        RETURN QUERY SELECT 0::bigint, 0::bigint, 0::bigint, 'BACKUP_GATE'::varchar(32);
        RETURN;
    END IF;
    RETURN QUERY
    WITH candidate AS (
        SELECT l.id, l.security_hold_until FROM schubert.app_logs l
         WHERE l.logged_at < p_cutoff
         ORDER BY l.logged_at, l.id FOR UPDATE SKIP LOCKED LIMIT p_limit
    ), removed AS (
        DELETE FROM schubert.app_logs l USING candidate c
         WHERE l.id = c.id
           AND (c.security_hold_until IS NULL OR c.security_hold_until <= p_cutoff)
        RETURNING l.id
    )
    SELECT (SELECT count(*) FROM candidate),
           (SELECT count(*) FROM removed),
           (SELECT count(*) FROM candidate c WHERE c.security_hold_until > p_cutoff),
           'OK'::varchar(32);
END
$function$;

CREATE OR REPLACE FUNCTION schubert.maintenance_cleanup_batch_runs(
    p_run_id uuid, p_cutoff timestamptz, p_limit integer)
RETURNS TABLE(target_count bigint, deleted_count bigint, skipped_count bigint, reason_code varchar(32))
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, schubert, schubert_web_session
AS $function$
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR p_limit IS NULL OR p_limit NOT BETWEEN 1 AND 1000 THEN
        RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'invalid cleanup argument';
    END IF;
    IF NOT pg_catalog.pg_try_advisory_xact_lock(71419602) THEN
        RETURN QUERY SELECT 0::bigint, 0::bigint, 0::bigint, 'LOCK_BUSY'::varchar(32);
        RETURN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM schubert.batch_runs b WHERE b.run_id = p_run_id AND b.step = 'BACKUP_DB' AND b.status = 'SUCCESS')
       OR NOT EXISTS (SELECT 1 FROM schubert.batch_runs b WHERE b.run_id = p_run_id AND b.step = 'BACKUP_CONFIG' AND b.status = 'SUCCESS') THEN
        RETURN QUERY SELECT 0::bigint, 0::bigint, 0::bigint, 'BACKUP_GATE'::varchar(32);
        RETURN;
    END IF;
    RETURN QUERY
    WITH candidate AS (
        SELECT b.id FROM schubert.batch_runs b
         WHERE b.started_at < p_cutoff AND b.status IN ('SUCCESS', 'WARNING', 'SKIPPED')
           AND b.run_id <> p_run_id
         ORDER BY b.started_at, b.id FOR UPDATE SKIP LOCKED LIMIT p_limit
    ), removed AS (
        DELETE FROM schubert.batch_runs b USING candidate c WHERE b.id = c.id RETURNING b.id
    )
    SELECT (SELECT count(*) FROM candidate), (SELECT count(*) FROM removed), 0::bigint, 'OK'::varchar(32);
END
$function$;

RESET ROLE;

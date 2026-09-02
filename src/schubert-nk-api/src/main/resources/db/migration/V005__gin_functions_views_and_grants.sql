-- NK-DAT-001 / PT-DB-005,011,012 / UI 212, 241, 242 / SS 331 sections 3 and 11, 343 section 9.2
SET ROLE nk_owner;

CREATE INDEX ix_script_files_chapter_title_trgm ON schubert.script_files
    USING gin ((coalesce(chapter_title, '') || ' ' || display_path) public.gin_trgm_ops);
CREATE INDEX ix_speakers_name_trgm ON schubert.speakers USING gin (name public.gin_trgm_ops);
CREATE INDEX ix_script_entries_body_search_trgm ON schubert.script_entries USING gin (body_search public.gin_trgm_ops);
CREATE INDEX ix_questions_body_trgm ON schubert.questions USING gin (body public.gin_trgm_ops) WHERE is_deleted = false;
CREATE INDEX ix_app_logs_message_trgm ON schubert.app_logs USING gin (message public.gin_trgm_ops);

CREATE VIEW schubert.v_ops_component_counts WITH (security_barrier = true) AS
SELECT 'auth_sessions'::text AS component, count(*)::bigint AS total_count,
       count(*) FILTER (WHERE NOT revoked AND expires_at > CURRENT_TIMESTAMP)::bigint AS active_count
  FROM schubert.auth_sessions
UNION ALL
SELECT 'async_jobs', count(*)::bigint,
       count(*) FILTER (WHERE state IN ('RECEIVED', 'PROCESSING'))::bigint
  FROM schubert.async_jobs
UNION ALL
SELECT 'mq_outbox', count(*)::bigint,
       count(*) FILTER (WHERE status IN ('PENDING', 'ERROR'))::bigint
  FROM schubert.mq_outbox
UNION ALL
SELECT 'web_log_outbox', count(*)::bigint,
       count(*) FILTER (WHERE status IN ('PENDING', 'ERROR'))::bigint
  FROM schubert_web_session.web_log_outbox;

CREATE VIEW schubert.v_ops_recent_events WITH (security_barrier = true) AS
SELECT logged_at AS event_at, service::text AS component, category::text AS category,
       action::text AS event_code, level::text AS severity
  FROM schubert.app_logs
 WHERE level IN ('WARN', 'ERROR')
UNION ALL
SELECT started_at AS event_at, 'BATCH'::text AS component, 'BATCH'::text AS category,
       step::text AS event_code, status::text AS severity
  FROM schubert.batch_runs
 WHERE status IN ('WARNING', 'FAILED');

CREATE FUNCTION schubert.maintenance_cleanup_notifications(
    p_run_id uuid, p_cutoff timestamptz, p_limit integer)
RETURNS TABLE(target_count bigint, deleted_count bigint, skipped_count bigint, reason_code varchar(32))
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, schubert, schubert_web_session
AS $function$
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR p_limit NOT BETWEEN 1 AND 1000 THEN
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

CREATE FUNCTION schubert.maintenance_cleanup_questions(
    p_run_id uuid, p_cutoff timestamptz, p_limit integer)
RETURNS TABLE(target_count bigint, deleted_count bigint, skipped_count bigint, reason_code varchar(32))
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, schubert, schubert_web_session
AS $function$
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR p_limit NOT BETWEEN 1 AND 1000 THEN
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

CREATE FUNCTION schubert.maintenance_cleanup_sessions(
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
    IF p_run_id IS NULL OR p_cutoff IS NULL OR p_limit NOT BETWEEN 1 AND 1000 THEN
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

CREATE FUNCTION schubert.maintenance_cleanup_message_stores(
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
    IF p_run_id IS NULL OR p_cutoff IS NULL OR p_limit NOT BETWEEN 1 AND 10000 THEN
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
         WHERE o.status = 'SENT' AND o.sent_at < p_cutoff
         ORDER BY o.sent_at, o.id FOR UPDATE SKIP LOCKED LIMIT p_limit
    )
    DELETE FROM schubert.mq_outbox o USING candidate c WHERE o.id = c.id;
    GET DIAGNOSTICS api_outbox_deleted = ROW_COUNT;
    WITH candidate AS (
        SELECT o.id FROM schubert_web_session.web_log_outbox o
         WHERE o.status = 'SENT' AND o.sent_at < p_cutoff
         ORDER BY o.sent_at, o.id FOR UPDATE SKIP LOCKED LIMIT p_limit
    )
    DELETE FROM schubert_web_session.web_log_outbox o USING candidate c WHERE o.id = c.id;
    GET DIAGNOSTICS web_outbox_deleted = ROW_COUNT;
    RETURN QUERY SELECT inbox_deleted + api_outbox_deleted + web_outbox_deleted,
                        inbox_deleted + api_outbox_deleted + web_outbox_deleted,
                        0::bigint, 'OK'::varchar(32);
END
$function$;

CREATE FUNCTION schubert.maintenance_cleanup_logs(
    p_run_id uuid, p_cutoff timestamptz, p_limit integer)
RETURNS TABLE(target_count bigint, deleted_count bigint, skipped_count bigint, reason_code varchar(32))
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, schubert, schubert_web_session
AS $function$
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR p_limit NOT BETWEEN 1 AND 10000 THEN
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

CREATE FUNCTION schubert.maintenance_cleanup_batch_runs(
    p_run_id uuid, p_cutoff timestamptz, p_limit integer)
RETURNS TABLE(target_count bigint, deleted_count bigint, skipped_count bigint, reason_code varchar(32))
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, schubert, schubert_web_session
AS $function$
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR p_limit NOT BETWEEN 1 AND 1000 THEN
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

REVOKE ALL ON SCHEMA schubert, schubert_web_session, schubert_meta FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA schubert, schubert_web_session, schubert_meta FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA schubert, schubert_web_session FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA schubert, schubert_web_session FROM PUBLIC;

GRANT USAGE ON SCHEMA schubert TO schubert_app, schubert_batch, schubert_backup, schubert_ops_ro;
GRANT USAGE ON SCHEMA schubert_web_session TO schubert_web_session, schubert_backup;
GRANT USAGE ON SCHEMA schubert_meta TO schubert_backup;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA schubert TO schubert_app;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA schubert TO schubert_app;

GRANT SELECT, INSERT, UPDATE, DELETE ON schubert.batch_runs TO schubert_batch;
GRANT USAGE, SELECT ON SEQUENCE schubert.batch_runs_id_seq TO schubert_batch;
GRANT EXECUTE ON FUNCTION schubert.maintenance_cleanup_notifications(uuid, timestamptz, integer) TO schubert_batch;
GRANT EXECUTE ON FUNCTION schubert.maintenance_cleanup_questions(uuid, timestamptz, integer) TO schubert_batch;
GRANT EXECUTE ON FUNCTION schubert.maintenance_cleanup_sessions(uuid, timestamptz, integer) TO schubert_batch;
GRANT EXECUTE ON FUNCTION schubert.maintenance_cleanup_message_stores(uuid, timestamptz, integer) TO schubert_batch;
GRANT EXECUTE ON FUNCTION schubert.maintenance_cleanup_logs(uuid, timestamptz, integer) TO schubert_batch;
GRANT EXECUTE ON FUNCTION schubert.maintenance_cleanup_batch_runs(uuid, timestamptz, integer) TO schubert_batch;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA schubert_web_session TO schubert_web_session;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA schubert_web_session TO schubert_web_session;

GRANT SELECT ON ALL TABLES IN SCHEMA schubert, schubert_web_session, schubert_meta TO schubert_backup;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA schubert, schubert_web_session TO schubert_backup;

GRANT SELECT ON schubert.v_ops_component_counts, schubert.v_ops_recent_events TO schubert_ops_ro;

ALTER DEFAULT PRIVILEGES FOR ROLE nk_owner IN SCHEMA schubert
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO schubert_app;
ALTER DEFAULT PRIVILEGES FOR ROLE nk_owner IN SCHEMA schubert
    GRANT USAGE ON SEQUENCES TO schubert_app;
ALTER DEFAULT PRIVILEGES FOR ROLE nk_owner IN SCHEMA schubert
    GRANT SELECT ON TABLES TO schubert_backup;
ALTER DEFAULT PRIVILEGES FOR ROLE nk_owner IN SCHEMA schubert_web_session
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO schubert_web_session;
ALTER DEFAULT PRIVILEGES FOR ROLE nk_owner IN SCHEMA schubert_web_session
    GRANT USAGE ON SEQUENCES TO schubert_web_session;
ALTER DEFAULT PRIVILEGES FOR ROLE nk_owner IN SCHEMA schubert_web_session
    GRANT SELECT ON TABLES TO schubert_backup;

RESET ROLE;

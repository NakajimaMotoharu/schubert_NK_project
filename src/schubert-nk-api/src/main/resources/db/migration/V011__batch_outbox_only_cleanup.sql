-- NK-DAT-001/NK-MSG-002; DAT-009/MQ-008/OPS-009; UI212/241/251; SS331 3.7/332 11.4.
-- QA-046/SSC-049/PG-D-126; BUG-014/YKT-012; PT-DB-INBOX-065..072.
-- V001..010 immutable. Only the private inspector may perform Inbox deletion.
SET ROLE nk_owner;

CREATE OR REPLACE FUNCTION schubert.maintenance_cleanup_message_stores(
    p_run_id uuid, p_cutoff timestamptz, p_limit integer)
RETURNS TABLE(target_count bigint, deleted_count bigint, skipped_count bigint, reason_code varchar(32))
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, schubert, schubert_web_session
SET timezone = 'UTC'
AS $function$
DECLARE
    api_deleted bigint;
    web_deleted bigint;
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR NOT pg_catalog.isfinite(p_cutoff)
       OR p_limit IS NULL OR p_limit NOT BETWEEN 1 AND 1000 THEN
        RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'invalid cleanup argument';
    END IF;
    BEGIN
        PERFORM schubert.maintenance_lock_inbox_backup(p_run_id, p_cutoff);
    EXCEPTION
        WHEN lock_not_available THEN
            RETURN QUERY SELECT 0::bigint,0::bigint,0::bigint,'LOCK_BUSY'::varchar(32);
            RETURN;
        WHEN object_not_in_prerequisite_state THEN
            RETURN QUERY SELECT 0::bigint,0::bigint,0::bigint,'BACKUP_GATE'::varchar(32);
            RETURN;
    END;
    WITH candidate AS (
        SELECT o.id FROM schubert.mq_outbox o
         WHERE o.status = 'SENT' AND o.sent_at < p_cutoff - interval '168 hours'
           AND (o.lease_until IS NULL OR o.lease_until < p_cutoff)
         ORDER BY o.id FOR UPDATE SKIP LOCKED LIMIT p_limit
    )
    DELETE FROM schubert.mq_outbox o USING candidate c WHERE o.id = c.id;
    GET DIAGNOSTICS api_deleted = ROW_COUNT;
    WITH candidate AS (
        SELECT o.id FROM schubert_web_session.web_log_outbox o
         WHERE o.status = 'SENT' AND o.sent_at < p_cutoff - interval '168 hours'
           AND (o.lease_until IS NULL OR o.lease_until < p_cutoff)
         ORDER BY o.id FOR UPDATE SKIP LOCKED LIMIT greatest(p_limit - api_deleted,0)
    )
    DELETE FROM schubert_web_session.web_log_outbox o USING candidate c WHERE o.id = c.id;
    GET DIAGNOSTICS web_deleted = ROW_COUNT;
    -- OK certifies this Outbox chunk only; the parent must require the separate Inbox step.
    RETURN QUERY SELECT api_deleted + web_deleted,api_deleted + web_deleted,
                        0::bigint,'OK'::varchar(32);
END
$function$;

REVOKE ALL ON FUNCTION schubert.maintenance_cleanup_message_stores(uuid,timestamptz,integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION schubert.maintenance_cleanup_message_stores(uuid,timestamptz,integer) TO schubert_batch;
RESET ROLE;

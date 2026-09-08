-- NK-DAT-001; OPS-009/DAT-009/MQ-008; UI212/241/251; SS331 section3.4/324 section12.
-- QA-046/UIC-006/SSC-049; PG-D-121; PT-DB-INBOX-017..024; BUG-014/YKT-012 remain open.
-- This READ/LOCK boundary does not decrypt, authorize deletion, or fix the V006 Inbox DELETE.
-- Provision dedicated role with provisioning/001_roles.sql before migration. V001..007 unchanged.
SET ROLE nk_owner;

CREATE FUNCTION schubert.maintenance_next_auth_inbox(
    p_run_id uuid, p_cutoff timestamptz, p_after_message_id uuid)
RETURNS SETOF schubert.request_inbox
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, schubert
SET timezone = 'UTC'
AS $function$
DECLARE
    inbox_row schubert.request_inbox;
    verified_backup_steps text[];
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR NOT pg_catalog.isfinite(p_cutoff) THEN
        RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'invalid inspection argument';
    END IF;
    IF NOT pg_catalog.pg_try_advisory_xact_lock(71419602) THEN
        RAISE EXCEPTION USING ERRCODE = '55P03', MESSAGE = 'inspection lock busy';
    END IF;
    -- BUG-080/YKT-071: decide only from the locked query snapshot, not a later EXISTS.
    SELECT pg_catalog.array_agg(verified.step) INTO verified_backup_steps
      FROM (
        SELECT b.step::text AS step FROM schubert.batch_runs b
         WHERE b.run_id = p_run_id
           AND b.business_date = (p_cutoff AT TIME ZONE 'Asia/Tokyo')::date
           AND b.step IN ('BACKUP_DB', 'BACKUP_CONFIG') AND b.status = 'SUCCESS'
           AND b.ended_at IS NOT NULL
         ORDER BY b.id FOR SHARE
      ) AS verified;
    IF verified_backup_steps IS NULL
       OR NOT verified_backup_steps @> ARRAY['BACKUP_DB', 'BACKUP_CONFIG'] THEN
        RAISE EXCEPTION USING ERRCODE = '55000', MESSAGE = 'inspection backup gate failed';
    END IF;
    SELECT i.message_id, i.correlation_id, i.request_layout_id, i.request_version,
           i.owner_user_id, i.operation_token, i.request_fingerprint_hmac, i.fingerprint_key_version,
           i.processing_state, i.result_ref_type, i.result_ref_id, i.result_ref_uuid,
           i.response_layout_id, i.response_version, i.response_body_encrypted, i.response_key_version,
           i.created_at, i.completed_at, i.expires_at
      INTO inbox_row FROM schubert.request_inbox i
     WHERE i.processing_state IN ('COMPLETED', 'ERROR')
       AND i.response_layout_id IN ('LGNRSP01', 'LOGRSP01')
       AND i.expires_at < p_cutoff
       AND (p_after_message_id IS NULL OR i.message_id > p_after_message_id)
     ORDER BY i.message_id LIMIT 1 FOR UPDATE;
    IF NOT FOUND THEN
        RETURN;
    END IF;
    IF inbox_row.result_ref_type = 'AUTH_SESSION' THEN
        PERFORM s.id FROM schubert.auth_sessions s WHERE s.id = inbox_row.result_ref_uuid FOR SHARE;
    END IF;
    RETURN NEXT inbox_row;
END
$function$;

REVOKE ALL ON FUNCTION schubert.maintenance_next_auth_inbox(uuid,timestamptz,uuid) FROM PUBLIC;
GRANT USAGE ON SCHEMA schubert TO schubert_inbox_inspector;
GRANT EXECUTE ON FUNCTION schubert.maintenance_next_auth_inbox(uuid,timestamptz,uuid) TO schubert_inbox_inspector;
GRANT SELECT (id,user_id,created_message_id,context_hash,context_ciphertext,key_version,issued_at,revoked,revoked_at)
    ON schubert.auth_sessions TO schubert_inbox_inspector;

RESET ROLE;

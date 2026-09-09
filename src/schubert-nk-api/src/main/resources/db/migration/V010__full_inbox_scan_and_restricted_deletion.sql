-- NK-DAT-001; OPS-009/DAT-009/MQ-008; UI212/241/251; SS331 section3.6/324 section12.
-- QA-046/UIC-006/SSC-049/PG-D-124; PT-DB-INBOX-049..056; BUG-014 remains open.
-- V001..009 immutable. SQL capability is NOT an AES/reference validation certificate.
SET ROLE nk_owner;

CREATE FUNCTION schubert.maintenance_lock_inbox_backup(p_run_id uuid, p_cutoff timestamptz)
RETURNS void
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = pg_catalog, schubert
SET timezone = 'UTC'
AS $function$
DECLARE
    verified_backup_steps text[];
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR NOT pg_catalog.isfinite(p_cutoff) THEN
        RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'invalid inspection argument';
    END IF;
    IF NOT pg_catalog.pg_try_advisory_xact_lock(71419602) THEN
        RAISE EXCEPTION USING ERRCODE = '55P03', MESSAGE = 'inspection lock busy';
    END IF;
    -- BUG-080/YKT-071: decide only from this locked snapshot, never a subsequent EXISTS.
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
END
$function$;

CREATE FUNCTION schubert.maintenance_next_inbox(
    p_run_id uuid, p_cutoff timestamptz, p_after_message_id uuid)
RETURNS SETOF schubert.request_inbox
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, schubert
SET timezone = 'UTC'
AS $function$
DECLARE
    inbox_row schubert.request_inbox;
BEGIN
    PERFORM schubert.maintenance_lock_inbox_backup(p_run_id, p_cutoff);
    SELECT i.message_id, i.correlation_id, i.request_layout_id, i.request_version,
           i.owner_user_id, i.operation_token, i.request_fingerprint_hmac, i.fingerprint_key_version,
           i.processing_state, i.result_ref_type, i.result_ref_id, i.result_ref_uuid,
           i.response_layout_id, i.response_version, i.response_body_encrypted, i.response_key_version,
           i.created_at, i.completed_at, i.expires_at
      INTO inbox_row FROM schubert.request_inbox i
     WHERE i.processing_state IN ('COMPLETED', 'ERROR') AND i.expires_at < p_cutoff
       AND (p_after_message_id IS NULL OR i.message_id > p_after_message_id)
     ORDER BY i.message_id LIMIT 1 FOR UPDATE;
    IF NOT FOUND THEN
        RETURN;
    END IF;
    -- Unsupported response/reference kinds remain candidates for a protected-row WARNING.
    IF inbox_row.result_ref_type = 'AUTH_SESSION' THEN
        PERFORM s.id FROM schubert.auth_sessions s WHERE s.id = inbox_row.result_ref_uuid FOR SHARE;
    ELSIF inbox_row.result_ref_type = 'USER' THEN
        PERFORM u.id FROM schubert.app_users u WHERE u.id = inbox_row.result_ref_id FOR SHARE;
    ELSIF inbox_row.result_ref_type = 'SCENARIO_FILE' THEN
        PERFORM f.id FROM schubert.script_files f WHERE f.id = inbox_row.result_ref_id FOR SHARE;
    END IF;
    RETURN NEXT inbox_row;
END
$function$;

CREATE FUNCTION schubert.maintenance_delete_inbox(
    p_run_id uuid, p_cutoff timestamptz, p_message_id uuid,
    p_expected_xact text, p_expected_response_sha256 bytea)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, schubert
SET timezone = 'UTC'
AS $function$
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR NOT pg_catalog.isfinite(p_cutoff)
       OR p_message_id IS NULL OR p_expected_xact IS NULL
       OR p_expected_xact !~ '^[0-9]{1,20}$'
       OR p_expected_response_sha256 IS NULL
       OR pg_catalog.octet_length(p_expected_response_sha256) <> 32 THEN
        RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'invalid inspection deletion argument';
    END IF;
    IF p_expected_xact <> pg_catalog.pg_current_xact_id()::text THEN
        RETURN false;
    END IF;
    PERFORM schubert.maintenance_lock_inbox_backup(p_run_id, p_cutoff);
    DELETE FROM schubert.request_inbox i
     WHERE i.message_id = p_message_id
       AND pg_catalog.sha256(i.response_body_encrypted) = p_expected_response_sha256
       AND i.processing_state IN ('COMPLETED', 'ERROR')
       AND i.request_layout_id IN (
         'LGNREQ01','LOGREQ01','GAMREQ01','SPKREQ01','RTEREQ01','SCFREQ01','SRCREQ01','SCNREQ01',
         'AUDREQ01','ANMREQ01','ANLREQ01','VIDREQ01','MCTREQ01','MCSREQ01','MTRREQ01','MEDREQ01',
         'USRREQ01','UDTREQ01','LGSREQ01','UCRREQ01','USTREQ01','URLREQ01','UPWREQ01','ULKREQ01')
       AND i.response_layout_id::text = pg_catalog.left(i.request_layout_id::text,3) || 'RSP01'
       AND ((i.request_layout_id = 'LGNREQ01' AND i.owner_user_id IS NULL)
         OR (i.request_layout_id <> 'LGNREQ01' AND i.owner_user_id IS NOT NULL))
       AND i.request_version = '001' AND i.response_version = '001'
       AND ((i.request_layout_id IN ('UCRREQ01','USTREQ01','URLREQ01','UPWREQ01','ULKREQ01')
             AND i.operation_token IS NOT NULL)
         OR (i.request_layout_id NOT IN ('UCRREQ01','USTREQ01','URLREQ01','UPWREQ01','ULKREQ01')
             AND i.operation_token IS NULL))
       AND ((i.result_ref_type = 'NONE' AND i.result_ref_id IS NULL AND i.result_ref_uuid IS NULL)
         OR (i.request_layout_id IN ('LGNREQ01','LOGREQ01') AND i.result_ref_type = 'AUTH_SESSION'
             AND i.result_ref_id IS NULL AND i.result_ref_uuid IS NOT NULL)
         OR (i.request_layout_id IN ('UCRREQ01','USTREQ01','URLREQ01','UPWREQ01','ULKREQ01')
             AND i.result_ref_type = 'USER' AND i.result_ref_id BETWEEN 1 AND 999999999999
             AND i.result_ref_uuid IS NULL)
         OR (i.request_layout_id = 'SCNREQ01' AND i.result_ref_type = 'SCENARIO_FILE'
             AND i.result_ref_id BETWEEN 1 AND 999999999999 AND i.result_ref_uuid IS NULL))
       AND pg_catalog.isfinite(i.created_at) AND pg_catalog.isfinite(i.completed_at)
       AND pg_catalog.isfinite(i.expires_at) AND i.created_at <= i.completed_at
       AND i.expires_at >= i.completed_at + CASE
         WHEN i.request_layout_id IN ('LGNREQ01','LOGREQ01','UCRREQ01','USTREQ01','URLREQ01','UPWREQ01','ULKREQ01')
           THEN interval '168 hours' ELSE interval '24 hours' END
       AND i.expires_at < p_cutoff;
    RETURN FOUND;
END
$function$;

REVOKE ALL ON FUNCTION schubert.maintenance_lock_inbox_backup(uuid,timestamptz) FROM PUBLIC;
REVOKE ALL ON FUNCTION schubert.maintenance_next_inbox(uuid,timestamptz,uuid) FROM PUBLIC;
REVOKE ALL ON FUNCTION schubert.maintenance_delete_inbox(uuid,timestamptz,uuid,text,bytea) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION schubert.maintenance_next_inbox(uuid,timestamptz,uuid),
    schubert.maintenance_delete_inbox(uuid,timestamptz,uuid,text,bytea) TO schubert_inbox_inspector;
GRANT SELECT (id,version) ON schubert.app_users TO schubert_inbox_inspector;
GRANT SELECT (id,game_id) ON schubert.script_files TO schubert_inbox_inspector;

RESET ROLE;

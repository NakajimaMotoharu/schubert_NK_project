-- NK-DAT-001; OPS-009/DAT-009/MQ-008; UI212/241/251; SS324 12.3/331 3.5/341/343.
-- QA-046/UIC-006/SSC-049; PG-D-122; PT-DB-INBOX-025..032.
-- Trusted inspection process ONLY: SQL does not validate AES or saved business references.
-- Caller owns a fresh private transaction, continuous candidate/reference locks, and key lifetime.
-- No SAVEPOINT, callback, intermediate commit, or transfer of validation to another connection.
SET ROLE nk_owner;

CREATE FUNCTION schubert.maintenance_delete_auth_inbox(
    p_run_id uuid, p_cutoff timestamptz, p_message_id uuid,
    p_expected_xact text, p_expected_response_sha256 bytea)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, schubert
SET timezone = 'UTC'
AS $function$
DECLARE
    verified_backup_steps text[];
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
    IF NOT pg_catalog.pg_try_advisory_xact_lock(71419602) THEN
        RAISE EXCEPTION USING ERRCODE = '55P03', MESSAGE = 'inspection lock busy';
    END IF;
    -- BUG-080/YKT-071: decide only from the locked query result, never a later snapshot.
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
    DELETE FROM schubert.request_inbox i
     WHERE i.message_id = p_message_id
       AND pg_catalog.sha256(i.response_body_encrypted) = p_expected_response_sha256
       AND i.processing_state IN ('COMPLETED', 'ERROR')
       AND ((i.request_layout_id = 'LGNREQ01' AND i.response_layout_id = 'LGNRSP01'
             AND i.owner_user_id IS NULL)
         OR (i.request_layout_id = 'LOGREQ01' AND i.response_layout_id = 'LOGRSP01'
             AND i.owner_user_id IS NOT NULL))
       AND i.request_version = '001' AND i.response_version = '001'
       AND i.operation_token IS NULL
       AND ((i.result_ref_type = 'NONE' AND i.result_ref_id IS NULL AND i.result_ref_uuid IS NULL)
         OR (i.result_ref_type = 'AUTH_SESSION' AND i.result_ref_id IS NULL AND i.result_ref_uuid IS NOT NULL))
       AND pg_catalog.isfinite(i.created_at) AND pg_catalog.isfinite(i.completed_at)
       AND pg_catalog.isfinite(i.expires_at) AND i.created_at <= i.completed_at
       AND i.expires_at >= i.completed_at + interval '168 hours'
       AND i.expires_at < p_cutoff;
    RETURN FOUND;
END
$function$;

REVOKE ALL ON FUNCTION schubert.maintenance_delete_auth_inbox(uuid,timestamptz,uuid,text,bytea) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION schubert.maintenance_delete_auth_inbox(uuid,timestamptz,uuid,text,bytea)
    TO schubert_inbox_inspector;

RESET ROLE;

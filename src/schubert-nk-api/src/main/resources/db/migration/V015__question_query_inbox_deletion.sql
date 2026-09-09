-- NK-DAT-001; DAT-009/MQ-008/OPS-009; UI236/241/251; SS324 12.8/331 3.10.
-- QA-046/SSC-049/PG-D-139; PT-DB-INBOX-161..168. V001..014 remain immutable.
-- Only four frozen query routes are added; no business-reference or role expansion.
SET ROLE nk_owner;

CREATE OR REPLACE FUNCTION schubert.maintenance_delete_inbox(
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
         'NTSREQ01','NTDREQ01','QSSREQ01','QSDREQ01',
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

REVOKE ALL ON FUNCTION schubert.maintenance_delete_inbox(uuid,timestamptz,uuid,text,bytea) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION schubert.maintenance_delete_inbox(uuid,timestamptz,uuid,text,bytea) TO schubert_inbox_inspector;
RESET ROLE;

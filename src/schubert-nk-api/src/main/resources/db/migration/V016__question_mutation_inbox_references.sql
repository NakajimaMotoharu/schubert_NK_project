-- NK-DAT-001; DAT-009/OPS-009/QST/NTF/MQ-008; UI232/236/241/251.
-- SS324 12.9/331 3.11/332; QA-046/SSC-049/052/PG-D-141; PT-DB-INBOX-177..192.
-- V001..015 immutable. SQL does not certify snapshot authentication.
SET ROLE nk_owner;

CREATE UNIQUE INDEX uq_mq_outbox_question_work ON schubert.mq_outbox(correlation_id)
    WHERE destination='nk.async.work' AND layout_id='QWKREQ01';

CREATE OR REPLACE FUNCTION schubert.maintenance_next_inbox(
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
    ELSIF inbox_row.result_ref_type = 'QUESTION' THEN
        -- Strong parent lock also blocks insertion of an absent Answer/Job through its FK.
        PERFORM q.id FROM schubert.questions q WHERE q.id = inbox_row.result_ref_id FOR UPDATE;
        PERFORM a.id FROM schubert.answers a WHERE a.question_id = inbox_row.result_ref_id ORDER BY a.id FOR SHARE;
        PERFORM j.id FROM schubert.async_jobs j WHERE j.question_id = inbox_row.result_ref_id ORDER BY j.id FOR SHARE;
    ELSIF inbox_row.result_ref_type = 'JOB' THEN
        -- Existing or absent notification remains stable until the owned transaction ends.
        PERFORM j.id FROM schubert.async_jobs j WHERE j.id = inbox_row.result_ref_id FOR UPDATE;
        PERFORM n.id FROM schubert.notifications n WHERE n.job_id = inbox_row.result_ref_id ORDER BY n.id FOR SHARE;
    END IF;
    RETURN NEXT inbox_row;
END
$function$;

CREATE FUNCTION schubert.maintenance_read_question_work(p_source uuid)
RETURNS TABLE(message_id uuid, correlation_id uuid, body bytea, status varchar,
              sent_at timestamptz, leased boolean)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, schubert
SET timezone = 'UTC'
AS $function$
BEGIN
    IF p_source IS NULL THEN
        RAISE EXCEPTION USING ERRCODE = '22023', MESSAGE = 'invalid work reference argument';
    END IF;
    RETURN QUERY
        SELECT o.message_id, o.correlation_id, o.body, o.status, o.sent_at,
               (o.lease_owner IS NOT NULL OR o.lease_until IS NOT NULL)
          FROM schubert.mq_outbox o
         WHERE o.correlation_id=p_source AND o.destination='nk.async.work'
           AND o.layout_id='QWKREQ01' AND o.layout_version='001'
           AND pg_catalog.octet_length(o.body)=320
         ORDER BY o.id FOR SHARE;
END
$function$;

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
         'NTSREQ01','NTDREQ01','QSSREQ01','QSDREQ01','QSBREQ01','NTCREQ01','QDLREQ01',
         'USRREQ01','UDTREQ01','LGSREQ01','UCRREQ01','USTREQ01','URLREQ01','UPWREQ01','ULKREQ01')
       AND i.response_layout_id::text = pg_catalog.left(i.request_layout_id::text,3) || 'RSP01'
       AND ((i.request_layout_id = 'LGNREQ01' AND i.owner_user_id IS NULL)
         OR (i.request_layout_id <> 'LGNREQ01' AND i.owner_user_id IS NOT NULL))
       AND i.request_version = '001' AND i.response_version = '001'
       AND ((i.request_layout_id IN ('UCRREQ01','USTREQ01','URLREQ01','UPWREQ01','ULKREQ01','QSBREQ01','NTCREQ01','QDLREQ01')
             AND i.operation_token IS NOT NULL)
         OR (i.request_layout_id NOT IN ('UCRREQ01','USTREQ01','URLREQ01','UPWREQ01','ULKREQ01','QSBREQ01','NTCREQ01','QDLREQ01')
             AND i.operation_token IS NULL))
       AND ((i.result_ref_type = 'NONE' AND i.result_ref_id IS NULL AND i.result_ref_uuid IS NULL
             AND (i.request_layout_id NOT IN ('QSBREQ01','NTCREQ01','QDLREQ01')
                  OR i.processing_state = 'ERROR'))
         OR (i.request_layout_id IN ('LGNREQ01','LOGREQ01') AND i.result_ref_type = 'AUTH_SESSION'
             AND i.result_ref_id IS NULL AND i.result_ref_uuid IS NOT NULL)
         OR (i.request_layout_id IN ('UCRREQ01','USTREQ01','URLREQ01','UPWREQ01','ULKREQ01')
             AND i.result_ref_type = 'USER' AND i.result_ref_id BETWEEN 1 AND 999999999999
             AND i.result_ref_uuid IS NULL)
         OR (i.request_layout_id = 'SCNREQ01' AND i.result_ref_type = 'SCENARIO_FILE'
             AND i.result_ref_id BETWEEN 1 AND 999999999999 AND i.result_ref_uuid IS NULL)
         OR (i.request_layout_id IN ('QSBREQ01','QDLREQ01') AND i.result_ref_type = 'QUESTION'
             AND i.result_ref_id BETWEEN 1 AND 999999999999 AND i.result_ref_uuid IS NULL)
         OR (i.request_layout_id = 'NTCREQ01' AND i.result_ref_type = 'JOB'
             AND i.result_ref_id BETWEEN 1 AND 999999999999 AND i.result_ref_uuid IS NULL))
       AND (i.request_layout_id NOT IN ('QSBREQ01','NTCREQ01','QDLREQ01')
         OR (i.processing_state = 'ERROR' AND i.result_ref_type = 'NONE')
         OR (i.processing_state = 'COMPLETED' AND i.result_ref_id BETWEEN 1 AND 999999999999
             AND i.result_ref_uuid IS NULL AND
             ((i.request_layout_id IN ('QSBREQ01','QDLREQ01') AND i.result_ref_type = 'QUESTION')
              OR (i.request_layout_id = 'NTCREQ01' AND i.result_ref_type = 'JOB'))))
       AND pg_catalog.isfinite(i.created_at) AND pg_catalog.isfinite(i.completed_at)
       AND pg_catalog.isfinite(i.expires_at) AND i.created_at <= i.completed_at
       AND i.expires_at >= i.completed_at + CASE
         WHEN i.request_layout_id IN ('LGNREQ01','LOGREQ01','UCRREQ01','USTREQ01','URLREQ01','UPWREQ01','ULKREQ01','QSBREQ01','NTCREQ01','QDLREQ01')
           THEN interval '168 hours' ELSE interval '24 hours' END
       AND i.expires_at < p_cutoff;
    RETURN FOUND;
END
$function$;

GRANT SELECT (id,owner_user_id,operation_token,receipt_id,submitted_at,is_deleted,deleted_at,deleted_by,version)
    ON schubert.questions TO schubert_inbox_inspector;
GRANT SELECT (id,question_id,owner_user_id,message_id,correlation_id,received_at,state,state_changed_at,cancelled_at,version)
    ON schubert.async_jobs TO schubert_inbox_inspector;
GRANT SELECT (question_id,is_deleted,deleted_at,deleted_by) ON schubert.answers TO schubert_inbox_inspector;
GRANT SELECT (job_id,question_id,owner_user_id,state,state_changed_at) ON schubert.notifications TO schubert_inbox_inspector;
REVOKE ALL ON FUNCTION schubert.maintenance_read_question_work(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION schubert.maintenance_read_question_work(uuid) TO schubert_inbox_inspector;
RESET ROLE;


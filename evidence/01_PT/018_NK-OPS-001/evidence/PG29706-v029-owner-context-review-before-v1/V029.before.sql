-- NK-DAT-001; RD DAT-001..011/AUT-001..004; UI241/242/243; SS331/354 SSC340.
-- BUG2846/YKT2405; PT-DB-NULL340-001..015.
-- Flyway's PostgreSQL migration transaction validates all existing rows. A failure
-- rolls back every replacement; no inferred repair, NOT VALID, or legacy rewrite.

ALTER TABLE schubert.auth_sessions
    DROP CONSTRAINT ck_auth_sessions_revocation,
    ADD CONSTRAINT ck_auth_sessions_revocation CHECK ((
        (NOT revoked AND revoked_at IS NULL AND revoke_reason IS NULL)
        OR (revoked AND revoked_at IS NOT NULL AND revoke_reason IN
            ('LOGOUT', 'DISABLED', 'PASSWORD_RESET', 'ADMIN', 'EXPIRED', 'REPLACED'))
    ) IS TRUE);

ALTER TABLE schubert.media_assets
    DROP CONSTRAINT ck_media_assets_pair,
    ADD CONSTRAINT ck_media_assets_pair CHECK ((
        (media_type = 'VIDEO' AND pair_key IS NULL AND pair_role IS NULL)
        OR (media_type = 'MUSIC' AND (
            (pair_role IN ('M', 'I') AND octet_length(pair_key) BETWEEN 1 AND 256)
            OR (pair_role = 'N' AND pair_key IS NULL)))
    ) IS TRUE);

ALTER TABLE schubert.notifications
    DROP CONSTRAINT ck_notifications_error,
    ADD CONSTRAINT ck_notifications_error CHECK ((
        (state = 'ERROR'
            AND error_code IN ('PROCESS_FAILED', 'SYSTEM_UNAVAIL', 'RESOURCE_LIMIT', 'DATA_INTEGRITY', 'PROTOCOL_ERROR')
            AND error_message IS NOT NULL)
        OR (state <> 'ERROR' AND error_code IS NULL AND error_message IS NULL)
    ) IS TRUE);

ALTER TABLE schubert.request_inbox
    DROP CONSTRAINT ck_request_inbox_response_snapshot_pair,
    ADD CONSTRAINT ck_request_inbox_response_snapshot_pair CHECK ((
        (response_body_encrypted IS NULL AND response_key_version IS NULL)
        OR (response_body_encrypted IS NOT NULL
            AND octet_length(response_body_encrypted) BETWEEN 29 AND 1050000
            AND response_key_version ~ '^[A-Za-z0-9][A-Za-z0-9._-]{0,15}$')
    ) IS TRUE),
    DROP CONSTRAINT ck_request_inbox_result_reference,
    ADD CONSTRAINT ck_request_inbox_result_reference CHECK ((
        (result_ref_type IS NULL AND result_ref_id IS NULL AND result_ref_uuid IS NULL)
        OR (result_ref_type = 'NONE' AND result_ref_id IS NULL AND result_ref_uuid IS NULL)
        OR (result_ref_type = 'AUTH_SESSION' AND result_ref_id IS NULL AND result_ref_uuid IS NOT NULL)
        OR (result_ref_type IN ('USER', 'QUESTION', 'JOB', 'SCENARIO_FILE')
            AND result_ref_id BETWEEN 1 AND 999999999999 AND result_ref_uuid IS NULL)
    ) IS TRUE);

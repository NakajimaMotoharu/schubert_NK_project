-- NK-DAT-001/NK-QST-001; UI213/224/242; SS312/331; SSC152/BUG422/YKT333.
-- PT-QST-STATE. Append-only: V003 bytes and all prior Flyway checksums remain unchanged.
SET ROLE nk_owner;

LOCK TABLE schubert.async_jobs IN SHARE ROW EXCLUSIVE MODE;
LOCK TABLE schubert.notifications IN ACCESS EXCLUSIVE MODE;

DO $legacy$
BEGIN
    IF EXISTS (
        SELECT 1 FROM schubert.notifications n
        JOIN schubert.async_jobs j ON j.id = n.job_id
        WHERE n.state = 'ACCEPTED' AND j.state <> 'RECEIVED'
    ) THEN
        RAISE EXCEPTION USING ERRCODE = '22000', MESSAGE = 'LEGACY_NOTIFICATION_STATE';
    END IF;
END
$legacy$;

ALTER TABLE schubert.notifications DROP CONSTRAINT ck_notifications_state;
UPDATE schubert.notifications SET state = 'RECEIVED' WHERE state = 'ACCEPTED';
ALTER TABLE schubert.notifications ADD CONSTRAINT ck_notifications_state
    CHECK (state IN ('RECEIVED', 'PROCESSING', 'COMPLETED', 'ERROR', 'CANCELLED'));

RESET ROLE;

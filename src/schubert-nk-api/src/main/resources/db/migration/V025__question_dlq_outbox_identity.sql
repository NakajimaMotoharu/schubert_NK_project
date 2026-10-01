-- NK-DAT-001/NK-MSG-002/QST-001; ASY001/MQ008; UI242;
-- SS312/321/324/331/332/SSC155; PT-QST-DLQ-DB. V001..024 immutable.
SET ROLE nk_owner;
LOCK TABLE schubert.mq_outbox IN ACCESS EXCLUSIVE MODE;
DO $migration$
BEGIN
    IF EXISTS (SELECT 1 FROM schubert.mq_outbox WHERE destination='nk.dead.letter') THEN
        RAISE EXCEPTION USING ERRCODE='22000', MESSAGE='LEGACY_DLQ_METADATA_REQUIRED';
    END IF;
END
$migration$;

ALTER TABLE schubert.mq_outbox
    ADD COLUMN dlq_original_message_id uuid,
    ADD COLUMN dlq_original_transport_id varchar(128),
    ADD COLUMN dlq_delivery_count integer,
    ADD COLUMN dlq_error_code varchar(32),
    ADD COLUMN dlq_detected_at timestamptz,
    ADD CONSTRAINT ck_mq_outbox_dlq_profile CHECK (
        (destination='nk.async.work' AND dlq_original_message_id IS NULL
         AND dlq_original_transport_id IS NULL AND dlq_delivery_count IS NULL
         AND dlq_error_code IS NULL AND dlq_detected_at IS NULL)
        OR
        (destination='nk.dead.letter' AND dlq_original_message_id IS NOT NULL
         AND dlq_original_message_id<>message_id AND dlq_original_transport_id IS NOT NULL
         AND dlq_original_transport_id COLLATE "C" ~ '^[ -~]{1,128}$'
         AND btrim(dlq_original_transport_id)<>'' AND dlq_delivery_count IS NOT NULL
         AND dlq_delivery_count>=1 AND dlq_error_code IS NOT NULL
         AND dlq_error_code='QUESTION_RETRY_EXHAUSTED' AND dlq_detected_at IS NOT NULL
         AND pg_catalog.isfinite(dlq_detected_at)
         AND dlq_detected_at BETWEEN timestamptz '0001-01-01 00:00:00+00'
                                 AND timestamptz '9999-12-31 23:59:59.999999+00'
         AND layout_id='QWKREQ01' AND layout_version='001'
         AND pg_catalog.octet_length(body)=320));

CREATE UNIQUE INDEX uq_mq_outbox_dlq_original ON schubert.mq_outbox(dlq_original_message_id)
    WHERE destination='nk.dead.letter';

CREATE FUNCTION schubert.guard_dlq_outbox_identity() RETURNS trigger
LANGUAGE plpgsql
SET search_path=pg_catalog,schubert
AS $function$
BEGIN
    IF (NEW.destination='nk.dead.letter' AND OLD.destination<>NEW.destination) OR
       (OLD.destination='nk.dead.letter' AND
       ROW(NEW.message_id,NEW.correlation_id,NEW.destination,NEW.layout_id,NEW.layout_version,
           NEW.body,NEW.created_at,NEW.dlq_original_message_id,NEW.dlq_original_transport_id,
           NEW.dlq_delivery_count,NEW.dlq_error_code,NEW.dlq_detected_at)
       IS DISTINCT FROM
       ROW(OLD.message_id,OLD.correlation_id,OLD.destination,OLD.layout_id,OLD.layout_version,
           OLD.body,OLD.created_at,OLD.dlq_original_message_id,OLD.dlq_original_transport_id,
           OLD.dlq_delivery_count,OLD.dlq_error_code,OLD.dlq_detected_at)) THEN
        RAISE EXCEPTION USING ERRCODE='23514', MESSAGE='IMMUTABLE_DLQ_IDENTITY';
    END IF;
    RETURN NEW;
END
$function$;
REVOKE ALL ON FUNCTION schubert.guard_dlq_outbox_identity() FROM PUBLIC;
CREATE TRIGGER guard_dlq_outbox_identity BEFORE UPDATE ON schubert.mq_outbox
    FOR EACH ROW EXECUTE FUNCTION schubert.guard_dlq_outbox_identity();
RESET ROLE;

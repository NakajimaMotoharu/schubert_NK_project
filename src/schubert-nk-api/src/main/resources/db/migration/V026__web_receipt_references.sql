-- NK-DAT-001/NK-WEB-002/NK-BAT-001; DAT009/OPS009/FUN001/AUT004; UI241/242/251.
-- QA048/SSC169/175; SS313/331 9.4/332/341/343; PG-D357; RCPT001..006.
-- V001..025 immutable. Technical locator only; no owner, token, body, or business FK.
SET ROLE nk_owner;

CREATE TABLE schubert_web_session.web_receipt_references (
    receipt_id char(26) NOT NULL,
    question_id bigint NOT NULL,
    submitted_at timestamptz NOT NULL,
    CONSTRAINT pk_web_receipt_references PRIMARY KEY (receipt_id),
    CONSTRAINT ck_web_receipt_references_receipt CHECK (receipt_id::text ~ '^[0-9A-HJKMNP-TV-Z]{26}$'),
    CONSTRAINT ck_web_receipt_references_question CHECK (question_id BETWEEN 1 AND 999999999999),
    CONSTRAINT ck_web_receipt_references_submitted CHECK (
        pg_catalog.isfinite(submitted_at)
        AND submitted_at=pg_catalog.date_trunc('milliseconds',submitted_at))
);
CREATE INDEX ix_web_receipt_references_question_id
    ON schubert_web_session.web_receipt_references(question_id);
REVOKE ALL ON schubert_web_session.web_receipt_references
    FROM PUBLIC,schubert_app,schubert_batch,schubert_web_session;
GRANT SELECT,INSERT,DELETE ON schubert_web_session.web_receipt_references TO schubert_web_session;
GRANT SELECT ON schubert_web_session.web_receipt_references TO schubert_backup;

CREATE FUNCTION schubert.maintenance_cleanup_web_receipt_references(
    p_run_id uuid,p_cutoff timestamptz,p_limit integer)
RETURNS TABLE(target_count bigint,deleted_count bigint,skipped_count bigint,reason_code varchar(32))
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, schubert, schubert_web_session
SET timezone = 'UTC'
AS $function$
DECLARE
    v_identity boolean;
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR NOT pg_catalog.isfinite(p_cutoff)
       OR p_cutoff < timestamptz '0001-01-01 00:00:00+00'
       OR p_cutoff >= timestamptz '10000-01-01 00:00:00+00'
       OR p_limit IS NULL OR p_limit NOT BETWEEN 1 AND 1000 THEN
        RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='invalid cleanup argument';
    END IF;
    BEGIN
        PERFORM schubert.maintenance_lock_inbox_backup(p_run_id,p_cutoff);
    EXCEPTION
        WHEN lock_not_available THEN
            RETURN QUERY SELECT 0::bigint,0::bigint,0::bigint,'LOCK_BUSY'::varchar(32);
            RETURN;
        WHEN object_not_in_prerequisite_state THEN
            RETURN QUERY SELECT 0::bigint,0::bigint,0::bigint,'BACKUP_GATE'::varchar(32);
            RETURN;
    END;
    SELECT r.identity_consistent INTO STRICT v_identity
      FROM schubert.maintenance_read_run_references(p_run_id,p_cutoff) r;
    IF v_identity IS DISTINCT FROM true THEN
        RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='cleanup identity mismatch';
    END IF;
    RETURN QUERY WITH candidate AS (
        SELECT w.receipt_id FROM schubert_web_session.web_receipt_references w
         WHERE NOT EXISTS(SELECT 1 FROM schubert.questions q WHERE q.id=w.question_id)
         ORDER BY w.receipt_id FOR UPDATE SKIP LOCKED LIMIT p_limit
    ), removed AS (
        DELETE FROM schubert_web_session.web_receipt_references w USING candidate c
         WHERE w.receipt_id=c.receipt_id RETURNING w.receipt_id
    )
    SELECT (SELECT count(*) FROM candidate),(SELECT count(*) FROM removed),0::bigint,'OK'::varchar(32);
END
$function$;
REVOKE ALL ON FUNCTION schubert.maintenance_cleanup_web_receipt_references(uuid,timestamptz,integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION schubert.maintenance_cleanup_web_receipt_references(uuid,timestamptz,integer) TO schubert_batch;

CREATE OR REPLACE FUNCTION schubert.maintenance_execute_cleanup_step(
    p_run_id uuid,p_cutoff timestamptz,p_step_id bigint,p_attempt integer,
    p_started timestamptz,p_kind text,p_limit integer)
RETURNS TABLE(target_count bigint,deleted_count bigint,skipped_count bigint,
              step_target_count bigint,step_success_count bigint,complete boolean,reason_code text)
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, schubert, schubert_web_session
SET timezone = 'UTC'
AS $function$
DECLARE
    v_name text;
    v_identity boolean;
    v_step record;
    v_chunk record;
    v_remaining boolean;
    v_total bigint;
    v_changed bigint;
BEGIN
    IF p_run_id IS NULL OR p_cutoff IS NULL OR p_step_id IS NULL OR p_attempt IS NULL
       OR p_started IS NULL OR p_kind IS NULL OR p_limit IS NULL
       OR NOT pg_catalog.isfinite(p_cutoff) OR NOT pg_catalog.isfinite(p_started)
       OR p_cutoff < timestamptz '0001-01-01 00:00:00+00'
       OR p_started >= timestamptz '10000-01-01 00:00:00+00' OR p_started < p_cutoff
       OR p_step_id NOT BETWEEN 1 AND 999999999999 OR p_attempt NOT BETWEEN 1 AND 99
       OR p_limit NOT BETWEEN 1 AND 1000
       OR p_kind NOT IN ('NOTIFICATIONS','QUESTIONS','SESSIONS','OUTBOX',
                         'BATCH_RUNS','INBOX_PROGRESS','LOG_PROGRESS','WEB_RECEIPTS') THEN
        RAISE EXCEPTION USING ERRCODE='22023',MESSAGE='invalid step cleanup argument';
    END IF;
    v_name := CASE p_kind
        WHEN 'NOTIFICATIONS' THEN 'CLEAN_NOTIFICATION'
        WHEN 'QUESTIONS' THEN 'CLEAN_QUESTION'
        WHEN 'SESSIONS' THEN 'CLEAN_SESSION'
        WHEN 'OUTBOX' THEN 'CLEAN_INBOX_OUTBOX'
        ELSE 'CLEAN_BATCH_RUN' END;
    -- Lock order is backup -> parent step -> candidates. A rejected observation has unknown totals.
    BEGIN
        PERFORM schubert.maintenance_lock_inbox_backup(p_run_id,p_cutoff);
    EXCEPTION
        WHEN lock_not_available THEN
            RETURN QUERY SELECT 0::bigint,0::bigint,0::bigint,NULL::bigint,NULL::bigint,false,'LOCK_BUSY'::text;
            RETURN;
        WHEN object_not_in_prerequisite_state THEN
            RETURN QUERY SELECT 0::bigint,0::bigint,0::bigint,NULL::bigint,NULL::bigint,false,'BACKUP_GATE'::text;
            RETURN;
    END;
    SELECT r.identity_consistent INTO STRICT v_identity
      FROM schubert.maintenance_read_run_references(p_run_id,p_cutoff) r;
    IF v_identity IS DISTINCT FROM true THEN
        RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='step cleanup identity mismatch';
    END IF;
    BEGIN
        SELECT b.target_count,b.success_count,b.failure_count,b.byte_count,b.status,b.ended_at
          INTO v_step FROM schubert.batch_runs b
         WHERE b.id=p_step_id AND b.run_id=p_run_id
           AND b.business_date=(p_cutoff AT TIME ZONE 'Asia/Tokyo')::date
           AND b.step=v_name AND b.attempt=p_attempt AND b.started_at=p_started
         FOR UPDATE NOWAIT;
        IF NOT FOUND THEN
            RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='step cleanup handle missing';
        END IF;
    EXCEPTION WHEN lock_not_available THEN
        RETURN QUERY SELECT 0::bigint,0::bigint,0::bigint,NULL::bigint,NULL::bigint,false,'LOCK_BUSY'::text;
        RETURN;
    END;
    IF v_step.status IS DISTINCT FROM 'RUNNING' OR v_step.ended_at IS NOT NULL
       OR v_step.target_count IS NULL OR v_step.target_count<0
       OR v_step.success_count IS DISTINCT FROM v_step.target_count
       OR v_step.failure_count IS DISTINCT FROM 0::bigint OR v_step.byte_count IS DISTINCT FROM 0::bigint THEN
        RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='step cleanup state mismatch';
    END IF;
    BEGIN
        CASE p_kind
            WHEN 'WEB_RECEIPTS' THEN
                SELECT r.target_count,r.deleted_count,r.skipped_count,r.reason_code INTO STRICT v_chunk
                  FROM schubert.maintenance_cleanup_web_receipt_references(p_run_id,p_cutoff,p_limit) r;
            WHEN 'NOTIFICATIONS' THEN
                SELECT r.target_count,r.deleted_count,r.skipped_count,r.reason_code INTO STRICT v_chunk
                  FROM schubert.maintenance_cleanup_notifications(p_run_id,p_cutoff,p_limit) r;
            WHEN 'QUESTIONS' THEN
                SELECT r.target_count,r.deleted_count,r.skipped_count,r.reason_code INTO STRICT v_chunk
                  FROM schubert.maintenance_cleanup_questions(p_run_id,p_cutoff,p_limit) r;
            WHEN 'SESSIONS' THEN
                SELECT r.target_count,r.deleted_count,r.skipped_count,r.reason_code INTO STRICT v_chunk
                  FROM schubert.maintenance_cleanup_sessions(p_run_id,p_cutoff,p_limit) r;
            WHEN 'OUTBOX' THEN
                SELECT r.target_count,r.deleted_count,r.skipped_count,r.reason_code INTO STRICT v_chunk
                  FROM schubert.maintenance_cleanup_message_stores(p_run_id,p_cutoff,p_limit) r;
            WHEN 'BATCH_RUNS' THEN
                SELECT r.target_count,r.deleted_count,r.skipped_count,r.reason_code INTO STRICT v_chunk
                  FROM schubert.maintenance_cleanup_batch_runs(p_run_id,p_cutoff,p_limit) r;
            WHEN 'INBOX_PROGRESS' THEN
                SELECT r.target_count,r.deleted_count,r.skipped_count,r.reason_code INTO STRICT v_chunk
                  FROM schubert.maintenance_cleanup_inbox_progress(p_run_id,p_cutoff,p_limit) r;
            WHEN 'LOG_PROGRESS' THEN
                SELECT r.target_count,r.deleted_count,r.skipped_count,r.reason_code INTO STRICT v_chunk
                  FROM schubert.maintenance_cleanup_log_progress(p_run_id,p_cutoff,p_limit) r;
        END CASE;
    EXCEPTION WHEN foreign_key_violation THEN
        IF p_kind <> 'QUESTIONS' THEN RAISE; END IF;
        RETURN QUERY SELECT 0::bigint,0::bigint,0::bigint,v_step.target_count,v_step.success_count,
                            false,'FOREIGN_KEY_CONFLICT'::text;
        RETURN;
    END;
    IF v_chunk.target_count IS NULL OR v_chunk.target_count NOT BETWEEN 0 AND p_limit
       OR v_chunk.deleted_count IS DISTINCT FROM v_chunk.target_count
       OR v_chunk.skipped_count IS DISTINCT FROM 0::bigint OR v_chunk.reason_code IS NULL
       OR v_chunk.reason_code NOT IN ('OK','LOCK_BUSY','BACKUP_GATE')
       OR (v_chunk.reason_code<>'OK' AND v_chunk.target_count<>0) THEN
        RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='step cleanup chunk mismatch';
    END IF;
    IF v_chunk.reason_code<>'OK' THEN
        RETURN QUERY SELECT 0::bigint,0::bigint,0::bigint,NULL::bigint,NULL::bigint,
                            false,v_chunk.reason_code::text;
        RETURN;
    END IF;
    IF v_chunk.target_count=0 THEN
        -- Do not mistake SKIP LOCKED's empty chunk for an empty eligible set.
        CASE p_kind
            WHEN 'WEB_RECEIPTS' THEN
                SELECT EXISTS(SELECT 1 FROM schubert_web_session.web_receipt_references w
                    WHERE NOT EXISTS(SELECT 1 FROM schubert.questions q WHERE q.id=w.question_id))
                  INTO v_remaining;
            WHEN 'NOTIFICATIONS' THEN
                SELECT EXISTS(SELECT 1 FROM schubert.notifications n
                   WHERE (n.state='CANCELLED' AND n.state_changed_at<p_cutoff)
                      OR (n.state IN ('COMPLETED','ERROR') AND n.state_changed_at<=p_cutoff-interval '24 hours'))
                  INTO v_remaining;
            WHEN 'QUESTIONS' THEN
                SELECT EXISTS(SELECT 1 FROM schubert.questions q
                   WHERE q.is_deleted=true AND q.deleted_at<p_cutoff
                     AND NOT EXISTS(SELECT 1 FROM schubert.notifications n WHERE n.question_id=q.id))
                  INTO v_remaining;
            WHEN 'SESSIONS' THEN
                SELECT EXISTS(SELECT 1 FROM schubert.auth_sessions s
                   WHERE s.expires_at<=p_cutoff-interval '24 hours'
                      OR (s.revoked AND s.revoked_at<=p_cutoff-interval '24 hours'))
                    OR EXISTS(SELECT 1 FROM schubert.login_ip_attempts a
                       WHERE greatest(a.window_started_at+interval '15 minutes',
                             coalesce(a.locked_until,'-infinity'::timestamptz))<=p_cutoff-interval '24 hours')
                    OR EXISTS(SELECT 1 FROM schubert_web_session.web_http_sessions s WHERE s.expires_at<=p_cutoff)
                  INTO v_remaining;
            WHEN 'OUTBOX' THEN
                SELECT EXISTS(SELECT 1 FROM schubert.mq_outbox o
                   WHERE o.status='SENT' AND o.sent_at<p_cutoff-interval '168 hours'
                     AND (o.lease_until IS NULL OR o.lease_until<p_cutoff))
                    OR EXISTS(SELECT 1 FROM schubert_web_session.web_log_outbox o
                       WHERE o.status='SENT' AND o.sent_at<p_cutoff-interval '168 hours'
                         AND (o.lease_until IS NULL OR o.lease_until<p_cutoff))
                  INTO v_remaining;
            WHEN 'BATCH_RUNS' THEN
                SELECT EXISTS(SELECT 1 FROM schubert.batch_runs b
                   WHERE b.ended_at<p_cutoff-interval '9600 hours' AND b.status IN ('SUCCESS','WARNING','SKIPPED')
                     AND b.run_id<>p_run_id
                     AND NOT EXISTS(SELECT 1 FROM schubert.batch_runs i WHERE i.run_id=b.run_id AND i.status IN ('RUNNING','FAILED')))
                  INTO v_remaining;
            WHEN 'INBOX_PROGRESS' THEN
                SELECT EXISTS(SELECT 1 FROM schubert.inbox_inspection_progress p
                   WHERE p.completed_at<p_cutoff-interval '9600 hours' AND p.run_id<>p_run_id
                     AND NOT EXISTS(SELECT 1 FROM schubert.batch_runs b WHERE b.run_id=p.run_id AND b.status IN ('RUNNING','FAILED')))
                  INTO v_remaining;
            WHEN 'LOG_PROGRESS' THEN
                SELECT EXISTS(SELECT 1 FROM schubert.log_cleanup_progress p
                   WHERE p.completed_at<p_cutoff-interval '9600 hours' AND p.run_id<>p_run_id
                     AND NOT EXISTS(SELECT 1 FROM schubert.batch_runs b WHERE b.run_id=p.run_id AND b.status IN ('RUNNING','FAILED')))
                  INTO v_remaining;
        END CASE;
        IF v_remaining THEN
            RETURN QUERY SELECT 0::bigint,0::bigint,0::bigint,NULL::bigint,NULL::bigint,false,'LOCK_BUSY'::text;
            RETURN;
        END IF;
        RETURN QUERY SELECT 0::bigint,0::bigint,0::bigint,v_step.target_count,v_step.success_count,true,'OK'::text;
        RETURN;
    END IF;
    v_total := v_step.target_count+v_chunk.deleted_count; -- native bigint overflow rolls back DELETE too
    UPDATE schubert.batch_runs b SET target_count=v_total,success_count=v_total
     WHERE b.id=p_step_id AND b.run_id=p_run_id
       AND b.business_date=(p_cutoff AT TIME ZONE 'Asia/Tokyo')::date AND b.step=v_name
       AND b.attempt=p_attempt AND b.started_at=p_started AND b.status='RUNNING' AND b.ended_at IS NULL
       AND b.target_count=v_step.target_count AND b.success_count=v_step.success_count
       AND b.failure_count=0 AND b.byte_count=0;
    GET DIAGNOSTICS v_changed=ROW_COUNT;
    IF v_changed<>1 THEN
        RAISE EXCEPTION USING ERRCODE='55000',MESSAGE='step cleanup count update mismatch';
    END IF;
    RETURN QUERY SELECT v_chunk.target_count,v_chunk.deleted_count,v_chunk.skipped_count,v_total,v_total,false,'OK'::text;
END
$function$;
REVOKE ALL ON FUNCTION schubert.maintenance_execute_cleanup_step(uuid,timestamptz,bigint,integer,timestamptz,text,integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION schubert.maintenance_execute_cleanup_step(uuid,timestamptz,bigint,integer,timestamptz,text,integer) TO schubert_batch;
RESET ROLE;

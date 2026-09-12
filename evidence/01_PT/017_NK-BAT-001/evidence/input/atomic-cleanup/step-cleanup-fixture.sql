-- Independent public PG164 fixture, not a deployed DB dump. DB259..266/BAT162..177.
-- Explicit UTC literals. Expected eligible rows: notification1/question1/session3/outbox2/history1/progress1+1.
DELETE FROM schubert.notifications;
DELETE FROM schubert.questions;
DELETE FROM schubert.auth_sessions;
DELETE FROM schubert.login_ip_attempts;
DELETE FROM schubert.request_inbox;
DELETE FROM schubert.mq_outbox;
DELETE FROM schubert.inbox_inspection_progress;
DELETE FROM schubert.log_cleanup_progress;
DELETE FROM schubert.batch_runs;
DELETE FROM schubert_web_session.web_http_sessions;
DELETE FROM schubert_web_session.web_log_outbox;
INSERT INTO schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at)
VALUES(7,'Learner','learner','synthetic-unused','USER','ACTIVE','2026-09-01T00:00:00Z','2026-09-01T00:00:00Z','2026-09-01T00:00:00Z')
ON CONFLICT(id) DO NOTHING;
INSERT INTO schubert.batch_runs(id,run_id,business_date,step,attempt,started_at,ended_at,status) VALUES
(90000,'12345678-9abc-def0-8123-456789abcdef','2026-09-13','BACKUP_DB',1,'2026-09-12T15:00:00Z','2026-09-12T15:01:00Z','SUCCESS'),
(90001,'12345678-9abc-def0-8123-456789abcdef','2026-09-13','BACKUP_CONFIG',1,'2026-09-12T15:00:00Z','2026-09-12T15:01:00Z','SUCCESS'),
(90010,'12345678-9abc-def0-8123-456789abcdef','2026-09-13','CLEAN_NOTIFICATION',1,'2026-09-13T02:00:00Z',NULL,'RUNNING'),
(90011,'12345678-9abc-def0-8123-456789abcdef','2026-09-13','CLEAN_QUESTION',1,'2026-09-13T02:00:00Z',NULL,'RUNNING'),
(90012,'12345678-9abc-def0-8123-456789abcdef','2026-09-13','CLEAN_SESSION',1,'2026-09-13T02:00:00Z',NULL,'RUNNING'),
(90013,'12345678-9abc-def0-8123-456789abcdef','2026-09-13','CLEAN_INBOX_OUTBOX',1,'2026-09-13T02:00:00Z',NULL,'RUNNING'),
(90014,'12345678-9abc-def0-8123-456789abcdef','2026-09-13','CLEAN_BATCH_RUN',1,'2026-09-13T02:00:00Z',NULL,'RUNNING'),
(1,'00000000-0000-0000-0000-000000000001','2024-01-01','PUBLIC_OLD',1,'2024-01-01T00:00:00Z','2024-01-01T00:01:00Z','SUCCESS');
INSERT INTO schubert.questions(id,receipt_id,owner_user_id,body,operation_token,submitted_at,is_deleted,deleted_at,deleted_by) VALUES
(1,'00000000000000000000000001',7,'public retained question','00000000-0000-0000-0000-000000000001','2026-09-01T00:00:00Z',false,NULL,NULL),
(2,'00000000000000000000000002',7,'public removed question','00000000-0000-0000-0000-000000000002','2026-09-01T00:00:00Z',true,'2026-09-01T00:00:00Z',7);
INSERT INTO schubert.async_jobs(id,question_id,owner_user_id,state,message_id,correlation_id,received_at,state_changed_at)
VALUES(1,1,7,'RECEIVED','00000000-0000-0001-0000-000000000001','00000000-0000-0002-0000-000000000001','2026-09-01T00:00:00Z','2026-09-01T00:00:00Z');
INSERT INTO schubert.notifications(id,job_id,question_id,owner_user_id,notification_type,state,accepted_at,state_changed_at,created_at,updated_at)
VALUES(1,1,1,7,'COMPLETED','COMPLETED','2026-09-01T00:00:00Z','2026-09-01T00:00:00Z','2026-09-01T00:00:00Z','2026-09-01T00:00:00Z');
INSERT INTO schubert.auth_sessions(id,user_id,context_hash,context_ciphertext,key_version,issued_at,last_accessed_at,expires_at,client_address,created_message_id)
VALUES('00000000-0000-0000-0000-000000000001',7,repeat('0',64),decode(repeat('00',30),'hex'),'v1','2026-09-01T00:00:00Z','2026-09-01T00:00:00Z','2026-09-01T00:01:00Z','127.0.0.1','00000000-0000-0001-0000-000000000001');
INSERT INTO schubert.login_ip_attempts VALUES('127.0.0.1',1,'2026-09-01T00:00:00Z',NULL,'2026-09-01T00:00:00Z');
INSERT INTO schubert_web_session.web_http_sessions VALUES
('00000000-0000-0000-0000-000000000001',repeat('0',64),decode(repeat('00',30),'hex'),'v1','2026-09-01T00:00:00Z','2026-09-01T00:00:00Z','2026-09-01T00:01:00Z',28800,0);
INSERT INTO schubert.mq_outbox(id,message_id,correlation_id,destination,layout_id,layout_version,body,status,next_attempt_at,created_at,sent_at)
VALUES(1,'00000000-0000-0000-0000-000000000001','00000000-0000-0001-0000-000000000001','nk.async.work','QSBREQ01','001',decode('00','hex'),'SENT','2026-09-01T00:00:00Z','2026-09-01T00:00:00Z','2026-09-01T00:00:00Z');
INSERT INTO schubert_web_session.web_log_outbox(id,message_id,correlation_id,layout_id,layout_version,payload_ciphertext,key_version,status,next_attempt_at,created_at,sent_at)
VALUES(1,'00000000-0000-0000-0000-000000000001','00000000-0000-0001-0000-000000000001','WLGEVT01','001',decode(repeat('00',30),'hex'),'v1','SENT','2026-09-01T00:00:00Z','2026-09-01T00:00:00Z','2026-09-01T00:00:00Z');
INSERT INTO schubert.inbox_inspection_progress(run_id,cutoff,completed_at)
VALUES('00000000-0000-0000-0000-000000000002','2024-01-01T00:00:00Z','2024-01-01T00:01:00Z');
INSERT INTO schubert.log_cleanup_progress(run_id,cutoff,completed_at)
VALUES('00000000-0000-0000-0000-000000000003','2024-01-01T00:00:00Z','2024-01-01T00:01:00Z');

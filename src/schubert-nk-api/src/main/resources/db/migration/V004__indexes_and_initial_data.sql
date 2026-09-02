-- NK-DAT-001 / PT-DB-005,011 / UI 223, 242 / SS 331 sections 4 through 9, 343 section 8
SET ROLE nk_owner;

CREATE INDEX ix_app_users_role_status ON schubert.app_users (role, status, id);
CREATE INDEX ix_app_users_locked_until ON schubert.app_users (locked_until) WHERE locked_until IS NOT NULL;
CREATE INDEX ix_auth_sessions_user_active ON schubert.auth_sessions (user_id, last_accessed_at DESC, id) WHERE revoked = false;
CREATE INDEX ix_auth_sessions_expires_at ON schubert.auth_sessions (expires_at);
CREATE INDEX ix_login_ip_attempts_updated_at ON schubert.login_ip_attempts (updated_at);
CREATE INDEX ix_script_entries_speaker_order ON schubert.script_entries (game_id, speaker_id, display_order, id);
CREATE INDEX ix_audio_files_basename ON schubert.audio_files (game_id, basename, id);
CREATE INDEX ix_entry_audio_links_audio_id ON schubert.entry_audio_links (audio_file_id, game_id, entry_id);
CREATE INDEX ix_media_assets_listing ON schubert.media_assets (media_type, category, section, display_order, id);
CREATE INDEX ix_questions_owner_active ON schubert.questions (owner_user_id, submitted_at DESC, id DESC) WHERE is_deleted = false;
CREATE INDEX ix_questions_admin_active ON schubert.questions (submitted_at DESC, id DESC) WHERE is_deleted = false;
CREATE INDEX ix_questions_deleted ON schubert.questions (deleted_at, id) WHERE is_deleted = true;
CREATE INDEX ix_async_jobs_fifo ON schubert.async_jobs (state, received_at, id);
CREATE INDEX ix_async_jobs_state_changed ON schubert.async_jobs (state, state_changed_at, id);
CREATE INDEX ix_async_jobs_owner ON schubert.async_jobs (owner_user_id, state_changed_at DESC, id DESC);
CREATE INDEX ix_notifications_owner ON schubert.notifications (owner_user_id, state_changed_at DESC, id DESC);
CREATE INDEX ix_notifications_cleanup ON schubert.notifications (state, state_changed_at, id);
CREATE UNIQUE INDEX uq_request_inbox_operation ON schubert.request_inbox (owner_user_id, operation_token)
    WHERE operation_token IS NOT NULL;
CREATE INDEX ix_request_inbox_expires ON schubert.request_inbox (expires_at);
CREATE INDEX ix_request_inbox_correlation ON schubert.request_inbox (correlation_id);
CREATE INDEX ix_mq_outbox_dispatch ON schubert.mq_outbox (status, next_attempt_at, id);
CREATE INDEX ix_mq_outbox_lease ON schubert.mq_outbox (lease_until) WHERE status = 'PENDING';
CREATE INDEX ix_app_logs_logged_at ON schubert.app_logs (logged_at DESC);
CREATE INDEX ix_app_logs_category_time ON schubert.app_logs (category, logged_at DESC);
CREATE INDEX ix_app_logs_correlation_id ON schubert.app_logs (correlation_id);
CREATE INDEX ix_app_logs_message_id ON schubert.app_logs (message_id);
CREATE UNIQUE INDEX uq_batch_runs_business_step_success ON schubert.batch_runs (business_date, step)
    WHERE status = 'SUCCESS';
CREATE INDEX ix_batch_runs_run_step ON schubert.batch_runs (run_id, step);
CREATE INDEX ix_batch_runs_status_started ON schubert.batch_runs (status, started_at DESC);
CREATE INDEX ix_web_http_sessions_expires_at ON schubert_web_session.web_http_sessions (expires_at);
CREATE INDEX ix_pending_context_revocations_due
    ON schubert_web_session.pending_context_revocations (next_attempt_at, requested_at);
CREATE INDEX ix_pending_context_revocations_expires
    ON schubert_web_session.pending_context_revocations (expires_at);
CREATE INDEX ix_web_log_outbox_dispatch
    ON schubert_web_session.web_log_outbox (status, next_attempt_at, id);
CREATE INDEX ix_web_log_outbox_sent_cleanup
    ON schubert_web_session.web_log_outbox (sent_at) WHERE status = 'SENT';

INSERT INTO schubert.games (id, code, title, display_order, created_at) VALUES
    (1, 'NUKITASHI1', 'NUKITASHI', 1, TIMESTAMPTZ '2026-09-01 00:00:00+00'),
    (2, 'NUKITASHI2', 'NUKITASHI2', 2, TIMESTAMPTZ '2026-09-01 00:00:00+00');

RESET ROLE;

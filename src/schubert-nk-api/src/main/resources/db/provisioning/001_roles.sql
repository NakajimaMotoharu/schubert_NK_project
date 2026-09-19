-- NK-DAT-001 / RD DAT-001..011, BAK-001..008 / UI 212, 241 / SS 331 section 3, 343 section 9
-- Run as the database administration role while connected to the target database.
-- Passwords are assigned out of band through the approved credential procedure.
DO $roles$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'nk_owner') THEN
        CREATE ROLE nk_owner NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'schubert_migration') THEN
        CREATE ROLE schubert_migration LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'schubert_app') THEN
        CREATE ROLE schubert_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'schubert_batch') THEN
        CREATE ROLE schubert_batch LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'schubert_backup') THEN
        CREATE ROLE schubert_backup LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'schubert_web_session') THEN
        CREATE ROLE schubert_web_session LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'schubert_ops_ro') THEN
        CREATE ROLE schubert_ops_ro LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
    END IF;
    -- QA-046/SSC-049, PG-D-121, PT-DB-INBOX-017/022: no owner membership or broad data role.
    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'schubert_inbox_inspector') THEN
        CREATE ROLE schubert_inbox_inspector LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
    END IF;
END
$roles$;

GRANT nk_owner TO schubert_migration WITH ADMIN FALSE, INHERIT FALSE, SET TRUE;

ALTER ROLE schubert_migration SET search_path = schubert_meta, pg_catalog;
ALTER ROLE schubert_app SET search_path = schubert, pg_catalog;
ALTER ROLE schubert_batch SET search_path = schubert, pg_catalog;
ALTER ROLE schubert_backup SET search_path = schubert, schubert_web_session, schubert_meta, pg_catalog;
ALTER ROLE schubert_web_session SET search_path = schubert_web_session, pg_catalog;
ALTER ROLE schubert_ops_ro SET search_path = schubert, pg_catalog;
ALTER ROLE schubert_inbox_inspector SET search_path = schubert, pg_catalog;
ALTER ROLE schubert_inbox_inspector SET lock_timeout = '5s';
ALTER ROLE schubert_inbox_inspector SET statement_timeout = '30s';

-- BUG208/YKT164; RD PER, UI212/253, SS342 section6.2; PT-OPS-PGCFG005.
ALTER ROLE schubert_app SET statement_timeout = '1500ms';
ALTER ROLE schubert_app SET lock_timeout = '500ms';
ALTER ROLE schubert_app SET idle_in_transaction_session_timeout = '15s';
ALTER ROLE schubert_web_session SET statement_timeout = '1500ms';
ALTER ROLE schubert_web_session SET lock_timeout = '500ms';
ALTER ROLE schubert_web_session SET idle_in_transaction_session_timeout = '15s';
ALTER ROLE schubert_batch SET statement_timeout = '30min';
ALTER ROLE schubert_batch SET lock_timeout = '5s';
ALTER ROLE schubert_batch SET idle_in_transaction_session_timeout = '60s';
ALTER ROLE schubert_backup SET statement_timeout = '30min';
ALTER ROLE schubert_backup SET lock_timeout = '5s';
ALTER ROLE schubert_backup SET idle_in_transaction_session_timeout = '60s';
ALTER ROLE schubert_migration SET statement_timeout = '30min';
ALTER ROLE schubert_migration SET lock_timeout = '5s';
ALTER ROLE schubert_migration SET idle_in_transaction_session_timeout = '60s';
ALTER ROLE schubert_ops_ro SET statement_timeout = '10s';
ALTER ROLE schubert_ops_ro SET lock_timeout = '1s';
ALTER ROLE schubert_ops_ro SET idle_in_transaction_session_timeout = '15s';

DO $database_grants$
DECLARE
    database_name text := pg_catalog.current_database();
BEGIN
    EXECUTE pg_catalog.format('REVOKE CREATE ON DATABASE %I FROM PUBLIC', database_name);
    EXECUTE pg_catalog.format('GRANT CREATE, CONNECT ON DATABASE %I TO nk_owner', database_name);
    EXECUTE pg_catalog.format(
        'GRANT CONNECT ON DATABASE %I TO schubert_migration, schubert_app, schubert_batch, schubert_backup, schubert_web_session, schubert_ops_ro, schubert_inbox_inspector',
        database_name);
    EXECUTE pg_catalog.format('ALTER DATABASE %I SET timezone TO %L', database_name, 'UTC');
END
$database_grants$;

REVOKE CREATE ON SCHEMA public FROM PUBLIC;

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
END
$roles$;

GRANT nk_owner TO schubert_migration WITH ADMIN FALSE, INHERIT FALSE, SET TRUE;

ALTER ROLE schubert_migration SET search_path = schubert_meta, pg_catalog;
ALTER ROLE schubert_app SET search_path = schubert, pg_catalog;
ALTER ROLE schubert_batch SET search_path = schubert, pg_catalog;
ALTER ROLE schubert_backup SET search_path = schubert, schubert_web_session, schubert_meta, pg_catalog;
ALTER ROLE schubert_web_session SET search_path = schubert_web_session, pg_catalog;
ALTER ROLE schubert_ops_ro SET search_path = schubert, pg_catalog;

DO $database_grants$
DECLARE
    database_name text := pg_catalog.current_database();
BEGIN
    EXECUTE pg_catalog.format('REVOKE CREATE ON DATABASE %I FROM PUBLIC', database_name);
    EXECUTE pg_catalog.format('GRANT CREATE, CONNECT ON DATABASE %I TO nk_owner', database_name);
    EXECUTE pg_catalog.format(
        'GRANT CONNECT ON DATABASE %I TO schubert_migration, schubert_app, schubert_batch, schubert_backup, schubert_web_session, schubert_ops_ro',
        database_name);
    EXECUTE pg_catalog.format('ALTER DATABASE %I SET timezone TO %L', database_name, 'UTC');
END
$database_grants$;

REVOKE CREATE ON SCHEMA public FROM PUBLIC;

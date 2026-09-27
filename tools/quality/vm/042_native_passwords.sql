-- Disposable PGPT VM only. Server-side read avoids secret SQL/argv/log output.
-- SS331 role names, native SCRAM authentication; no deployed role/data accessed.
SET password_encryption='scram-sha-256';
DO $fixture$
BEGIN
  EXECUTE format('ALTER ROLE schubert_app PASSWORD %L',
    trim(trailing E'\n' from pg_read_file('/var/lib/postgresql/pgpt-passwords/db-api')));
  EXECUTE format('ALTER ROLE schubert_web_session PASSWORD %L',
    trim(trailing E'\n' from pg_read_file('/var/lib/postgresql/pgpt-passwords/db-web')));
END
$fixture$;

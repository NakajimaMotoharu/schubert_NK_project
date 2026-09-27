-- Private disposable VM only, no credential in SQL statement/argv.
SET password_encryption='scram-sha-256';
DO $fixture$
BEGIN
 EXECUTE format('ALTER ROLE schubert_migration PASSWORD %L',
   trim(trailing E'\n' from pg_read_file('/var/lib/postgresql/pgpt-passwords/db-migration')));
END
$fixture$;

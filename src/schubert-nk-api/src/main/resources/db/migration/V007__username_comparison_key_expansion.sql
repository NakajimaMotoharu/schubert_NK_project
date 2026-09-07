-- NK-DAT-001 / NK-AUT-001; FUN-001/009, AUT-001; UI226/242; SS331/314.
-- SSC-014 / BUG-028 / YKT-025; PT-AUT-NAME-004, PT-DB-001.
-- Display username and audit/wire bounds remain 64 UTF-8 bytes. Locale.ROOT lowercase may expand
-- 64 display bytes to 96 comparison-key bytes. Preserve existing values, uniqueness and grants.
ALTER TABLE schubert.app_users DROP CONSTRAINT ck_app_users_username_key_bytes;
ALTER TABLE schubert.app_users ADD CONSTRAINT ck_app_users_username_key_bytes
    CHECK (octet_length(username_key) BETWEEN 1 AND 96);

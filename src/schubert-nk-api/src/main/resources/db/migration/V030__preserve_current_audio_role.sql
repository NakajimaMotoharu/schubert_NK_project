-- NK-DDL-001 / MIG003005006 / DAT004 / TST / UI223242254 / SS331343 SSC396
-- BUG2943 / YKT2472 / PT-DB-AUDIOROLE030-STATIC; actual DB acceptance remains HOLD.
-- Forward-only extension. V001..V029 stay byte-identical; Flyway owns the transaction.
ALTER TABLE schubert.audio_files ALTER COLUMN audio_role TYPE varchar(11);
ALTER TABLE schubert.audio_files DROP CONSTRAINT ck_audio_files_audio_role_bytes;
ALTER TABLE schubert.audio_files ADD CONSTRAINT ck_audio_files_audio_role_bytes
    CHECK (octet_length(audio_role) BETWEEN 1 AND 11);

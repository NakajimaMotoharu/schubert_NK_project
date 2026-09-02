package dev.codex.schubert.nk.api.database;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Savepoint;
import java.sql.Statement;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeSet;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.stream.Collectors;
import org.flywaydb.core.Flyway;
import org.flywaydb.core.api.MigrationInfo;
import org.flywaydb.core.api.output.MigrateResult;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.postgresql.util.PSQLException;

/**
 * PostgreSQL 18 component PT for NK-DAT-001.
 *
 * <p>Trace: RD DAT-001..011; UI 212/241/242; SS 331/343/354; PT-DB-001..015.
 * Expected catalog sets in this class are independent from the migration implementation.
 */
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
final class DatabaseMigrationTest {
    private static final String DATABASE = "schubert_nk";
    private static final String ADMIN = "pgpt_admin";
    private static final String MIGRATION = "schubert_migration";
    private static final String FIXED_TIME = "2026-09-02 00:00:00+00";
    private static final String HASH = "a".repeat(64);
    private static final String CIPHER = "decode('" + "00".repeat(29) + "','hex')";
    private static final String UUID_1 = "00000000-0000-0000-0000-000000000001";
    private static final String UUID_2 = "00000000-0000-0000-0000-000000000002";
    private static final Map<String, Integer> CLEANUP_FUNCTION_LIMITS = Map.of(
            "maintenance_cleanup_notifications", 1000,
            "maintenance_cleanup_questions", 1000,
            "maintenance_cleanup_sessions", 1000,
            "maintenance_cleanup_message_stores", 10000,
            "maintenance_cleanup_logs", 10000,
            "maintenance_cleanup_batch_runs", 1000);
    private static final Path MODULE = Path.of("").toAbsolutePath().normalize();

    private static Path pgRoot;
    private static Path clusterRoot;
    private static Path dataDirectory;
    private static int port;
    private static String jdbcUrl;
    private static Flyway flyway;
    private static MigrateResult firstMigration;

    @BeforeAll
    static void startPostgreSqlAndMigrate() throws Exception {
        pgRoot = locatePostgreSqlRoot();
        Path target = MODULE.resolve("target");
        Files.createDirectories(target);
        clusterRoot = Files.createTempDirectory(target, "postgresql-18-");
        dataDirectory = clusterRoot.resolve("data");
        port = availablePort();

        run(pgBinary("initdb"), "-D", dataDirectory.toString(), "-L",
                pgRoot.resolve("share/postgresql/18").toString(), "--no-locale", "--encoding=UTF8",
                "--auth=trust", "--username=" + ADMIN);
        run(pgBinary("pg_ctl"), "-D", dataDirectory.toString(), "-l",
                clusterRoot.resolve("postgresql.log").toString(), "-o", serverOptions(), "start");

        run(pgBinary("createdb"), "-h", "127.0.0.1", "-p", Integer.toString(port), "-U", ADMIN, DATABASE);
        jdbcUrl = "jdbc:postgresql://127.0.0.1:" + port + "/" + DATABASE;
        executeResourceAsAdmin("db/provisioning/001_roles.sql");
        flyway = configuredFlyway(jdbcUrl, true, "classpath:db/migration");
        firstMigration = flyway.migrate();
    }

    @AfterAll
    static void stopPostgreSql() throws Exception {
        if (dataDirectory != null && Files.exists(dataDirectory.resolve("postmaster.pid"))) {
            run(pgBinary("pg_ctl"), "-D", dataDirectory.toString(), "stop", "-m", "fast");
        }
    }

    @Test
    @Order(1)
    @DisplayName("PT-DB-001 V001-V005 migrate, validate and idempotent rerun")
    void migrationsAreVersionedValidatedAndIdempotent() throws SQLException {
        assertEquals(5, firstMigration.migrationsExecuted);
        assertTrue(flyway.validateWithResult().validationSuccessful);
        assertEquals(0, flyway.migrate().migrationsExecuted);
        List<String> applied = Arrays.stream(flyway.info().applied())
                .map(MigrationInfo::getVersion)
                .filter(Objects::nonNull)
                .map(version -> version.getVersion())
                .toList();
        assertEquals(List.of("001", "002", "003", "004", "005"), applied);
        assertEquals(0L, queryLong(ADMIN,
                "select count(*) from schubert_meta.flyway_schema_history where success = false"));
        assertEquals("nk_owner", queryString(ADMIN,
                "select pg_get_userbyid(relowner) from pg_class where oid='schubert_meta.flyway_schema_history'::regclass"));
    }

    @Test
    @Order(2)
    @DisplayName("PT-DB-002 schemas, pg_trgm and 21 tables")
    void schemasExtensionAndTablesMatchTheIndependentCatalog() throws SQLException {
        assertEquals(Set.of("schubert", "schubert_meta", "schubert_web_session"), querySet(ADMIN,
                "select schema_name from information_schema.schemata "
                        + "where schema_name in ('schubert','schubert_meta','schubert_web_session')"));
        assertEquals(Set.of("pg_trgm"), querySet(ADMIN,
                "select extname from pg_extension where extname='pg_trgm'"));
        assertEquals(expectedTables(), querySet(ADMIN,
                "select table_schema||'.'||table_name from information_schema.tables "
                        + "where table_type='BASE TABLE' and table_schema in ('schubert','schubert_web_session')"));
    }

    @Test
    @Order(3)
    @DisplayName("PT-DB-003 all table columns and required identity columns")
    void tableColumnsAndIdentityColumnsMatchTheIndependentMatrix() throws SQLException {
        Map<String, Set<String>> actual = queryGroupedSet(
                "select c.table_schema||'.'||c.table_name, c.column_name from information_schema.columns c "
                        + "join information_schema.tables t on t.table_schema=c.table_schema and t.table_name=c.table_name "
                        + "where t.table_type='BASE TABLE' and c.table_schema in ('schubert','schubert_web_session') "
                        + "order by c.ordinal_position");
        assertEquals(expectedColumns(), actual);

        Set<String> identity = querySet(ADMIN,
                "select table_schema||'.'||table_name||'.'||column_name from information_schema.columns "
                        + "where is_identity='YES' and table_schema in ('schubert','schubert_web_session')");
        assertEquals(expectedIdentityColumns(), identity);
        assertEquals("NEVER", queryString(ADMIN,
                "select is_generated from information_schema.columns "
                        + "where table_schema='schubert' and table_name='script_entries' and column_name='id'"));
        assertEquals("ALWAYS", queryString(ADMIN,
                "select is_generated from information_schema.columns "
                        + "where table_schema='schubert' and table_name='script_entries' and column_name='body_search'"));
    }

    @Test
    @Order(4)
    @DisplayName("PT-DB-004 named constraints, FK delete actions and deferred trigger")
    void constraintsForeignKeysAndDeferredTriggerAreComplete() throws SQLException {
        assertEquals("145|23|30|21|1", queryString(ADMIN,
                "select count(*) filter(where contype='c')||'|'||count(*) filter(where contype='f')||'|'||"
                        + "count(*) filter(where contype='u')||'|'||count(*) filter(where contype='p')||'|'||"
                        + "count(*) filter(where contype='t') from pg_constraint c join pg_namespace n "
                        + "on n.oid=c.connamespace where n.nspname in ('schubert','schubert_web_session')"));
        assertEquals(0L, queryLong(ADMIN,
                "select count(*) from pg_constraint c join pg_namespace n on n.oid=c.connamespace "
                        + "where n.nspname in ('schubert','schubert_web_session') and not c.convalidated"));
        long unnamed = queryLong(ADMIN,
                "select count(*) from pg_constraint c join pg_namespace n on n.oid=c.connamespace "
                        + "where n.nspname in ('schubert','schubert_web_session') "
                        + "and c.contype in ('p','f','u','c') "
                        + "and c.conname !~ '^(pk|fk|uq|ck)_' ");
        assertEquals(0L, unnamed);

        Set<String> foreignKeys = querySet(ADMIN,
                "select c.conname||':'||c.confdeltype::text from pg_constraint c "
                        + "join pg_namespace n on n.oid=c.connamespace where n.nspname='schubert' and c.contype='f'");
        assertTrue(foreignKeys.contains("fk_script_entries_script_files_file_game:c"));
        assertTrue(foreignKeys.contains("fk_entry_audio_links_script_entries_entry_game:c"));
        assertTrue(foreignKeys.contains("fk_answers_questions_question_id:c"));
        assertTrue(foreignKeys.contains("fk_async_jobs_questions_question_id:c"));
        assertTrue(foreignKeys.contains("fk_notifications_questions_question_id:r"));
        assertTrue(foreignKeys.contains("fk_notifications_async_jobs_job_id:r"));
        assertTrue(foreignKeys.contains("fk_audio_files_games_game_id:r"));

        assertEquals("true:true", queryString(ADMIN,
                "select tgdeferrable||':'||tginitdeferred from pg_trigger "
                        + "where tgname='ck_entry_audio_links_entry_type_limit'"));
    }

    @Test
    @Order(5)
    @DisplayName("PT-DB-005 explicit btree, partial and GIN indexes")
    void explicitIndexesMatchTheIndependentSet() throws SQLException {
        Set<String> actual = querySet(ADMIN,
                "select indexname from pg_indexes where schemaname in ('schubert','schubert_web_session') "
                        + "and (indexname like 'ix\\_%' escape '\\' "
                        + "or indexname in ('uq_request_inbox_operation','uq_batch_runs_business_step_success'))");
        assertEquals(expectedExplicitIndexes(), actual);
        assertEquals(5L, queryLong(ADMIN,
                "select count(*) from pg_index i join pg_class c on c.oid=i.indexrelid "
                        + "join pg_am a on a.oid=c.relam join pg_namespace n on n.oid=c.relnamespace "
                        + "where n.nspname='schubert' and a.amname='gin'"));
        assertTrue(queryString(ADMIN,
                "select indexdef from pg_indexes where schemaname='schubert' "
                        + "and indexname='uq_request_inbox_operation'").contains("WHERE (operation_token IS NOT NULL)"));
    }

    @Test
    @Order(6)
    @DisplayName("PT-DB-006 N12 identity sequence bounds")
    void identitySequencesHaveTheN12LimitAndDoNotCycle() throws SQLException {
        Set<String> sequences = querySet(ADMIN,
                "select schemaname||'.'||sequencename from pg_sequences "
                        + "where schemaname in ('schubert','schubert_web_session')");
        assertEquals(expectedSequences(), sequences);
        assertEquals(expectedSequences().size(), queryLong(ADMIN,
                "select count(*) from pg_sequences where schemaname in ('schubert','schubert_web_session') "
                        + "and min_value=1 and max_value=999999999999 and increment_by=1 and cycle=false"));
    }

    @Test
    @Order(7)
    @DisplayName("PT-DB-007 N12/N9, UTF-8 bytes, hash, enum and path boundaries")
    void scalarAndPathBoundariesRejectInvalidRows() throws SQLException {
        try (Connection connection = connection(ADMIN)) {
            connection.setAutoCommit(false);
            execute(connection, userInsert(1, "u".repeat(64), 999999999));
            assertRejects(connection, "23514", userInsert(2, "u".repeat(65), 0));
            assertRejects(connection, "23514", userInsert(3, "user", 1000000000));
            assertRejects(connection, "23514", userInsertWithRole(4, "OTHER"));
            assertRejects(connection, "23514",
                    "insert into schubert.script_files(game_id,display_order,storage_relative_path,display_path,file_name,sha256,byte_size,created_at) "
                            + "values(1,1,'../escape','shown','file.ks','" + HASH + "',0,'" + FIXED_TIME + "')");
            assertRejects(connection, "23514",
                    "insert into schubert.script_files(game_id,display_order,storage_relative_path,display_path,file_name,sha256,byte_size,created_at) "
                            + "values(1,1,'ok/file','shown','file.ks','INVALID',0,'" + FIXED_TIME + "')");
            connection.rollback();
        }
    }

    @Test
    @Order(8)
    @DisplayName("PT-DB-008 state/time/null and Security hold correlations")
    void stateTimeAndNullCorrelationsAreEnforced() throws SQLException {
        try (Connection connection = connection(ADMIN)) {
            connection.setAutoCommit(false);
            execute(connection, userInsert(10, "owner", 0));
            assertRejects(connection, "23514",
                    "insert into schubert.auth_sessions values('" + UUID_1 + "',10,'" + HASH + "'," + CIPHER
                            + ",'key-1','" + FIXED_TIME + "','" + FIXED_TIME + "','2026-09-03 00:00:00+00',false,'"
                            + FIXED_TIME + "',null,'127.0.0.1','" + UUID_2 + "')");
            assertRejects(connection, "23514",
                    questionInsert(10, true, "null", "null"));
            execute(connection, questionInsert(10, false, "null", "null"));
            assertRejects(connection, "23514",
                    jobInsert("RECEIVED", "'" + FIXED_TIME + "'", "null", "null", "null", "null"));
            execute(connection, jobInsert("RECEIVED", "null", "null", "null", "null", "null"));
            assertRejects(connection, "23514",
                    "insert into schubert.notifications(job_id,question_id,owner_user_id,notification_type,state,accepted_at,state_changed_at,created_at,updated_at) "
                            + "values(1,1,10,'ERROR','ERROR','" + FIXED_TIME + "','" + FIXED_TIME + "','"
                            + FIXED_TIME + "','" + FIXED_TIME + "')");
            assertRejects(connection, "23514",
                    "insert into schubert.request_inbox(message_id,correlation_id,request_layout_id,request_version,"
                            + "request_fingerprint_hmac,fingerprint_key_version,processing_state,created_at,completed_at,expires_at) values('"
                            + UUID_1 + "','" + UUID_2 + "','LGNREQ01','001','" + HASH + "','key-1','PROCESSING','"
                            + FIXED_TIME + "','" + FIXED_TIME + "','2026-09-03 00:00:00+00')");
            assertRejects(connection, "23514",
                    "insert into schubert.mq_outbox(message_id,correlation_id,destination,layout_id,layout_version,body,status,"
                            + "next_attempt_at,lease_owner,created_at) values('" + UUID_1 + "','" + UUID_2
                            + "','nk.async.work','QWKREQ01','001',decode('00','hex'),'PENDING','" + FIXED_TIME
                            + "','worker','" + FIXED_TIME + "')");
            assertRejects(connection, "23514",
                    "insert into schubert_web_session.web_http_sessions values('" + UUID_1 + "','" + HASH + "',"
                            + CIPHER + ",'key-1','" + FIXED_TIME + "','" + FIXED_TIME
                            + "','2026-09-03 00:00:00+00',28801,0)");
            assertRejects(connection, "23514",
                    "insert into schubert.app_logs(id,logged_at,service,category,level,action,message,"
                            + "security_hold_until) values(600,'2026-01-01 00:00:00+00','API','ACTION','INFO',"
                            + "'TEST_ACTION','public test log','2026-09-03 00:00:00+00')");
            connection.rollback();
        }
    }

    @Test
    @Order(9)
    @DisplayName("PT-DB-009 composite game FKs and delete actions")
    void compositeGameForeignKeysAndDeleteActionsAreEnforced() throws SQLException {
        try (Connection connection = connection(ADMIN)) {
            connection.setAutoCommit(false);
            execute(connection, userInsert(20, "owner20", 0));
            execute(connection, scriptFileInsert(101, 1, 1));
            execute(connection, scriptFileInsert(102, 2, 1));
            execute(connection, speakerInsert(201, 1));
            execute(connection, speakerInsert(202, 2));
            assertRejects(connection, "23503", scriptEntryInsert(301, 1, 101, 202));
            execute(connection, scriptEntryInsert(301, 1, 101, 201));
            execute(connection, audioInsert(401, 2));
            assertRejects(connection, "23503",
                    "insert into schubert.entry_audio_links values(301,401,1,'voice',1,'" + FIXED_TIME + "')");
            assertRejects(connection, "23001", "delete from schubert.games where id=1");

            execute(connection, audioInsert(402, 1));
            execute(connection, "insert into schubert.entry_audio_links values(301,402,1,'voice',1,'" + FIXED_TIME + "')");
            execute(connection, "delete from schubert.script_files where id=101");
            assertEquals(0L, queryLong(connection, "select count(*) from schubert.script_entries where id=301"));
            assertEquals(0L, queryLong(connection, "select count(*) from schubert.entry_audio_links where entry_id=301"));

            execute(connection, questionInsert(20, false, "null", "null"));
            execute(connection, jobInsert("RECEIVED", "null", "null", "null", "null", "null"));
            execute(connection,
                    "insert into schubert.notifications(job_id,question_id,owner_user_id,notification_type,state,accepted_at,state_changed_at,created_at,updated_at) "
                            + "values(1,1,20,'ACCEPTED','ACCEPTED','" + FIXED_TIME + "','" + FIXED_TIME + "','"
                            + FIXED_TIME + "','" + FIXED_TIME + "')");
            assertRejects(connection, "23001", "delete from schubert.questions where id=1");
            execute(connection, "delete from schubert.notifications where job_id=1");
            execute(connection, "delete from schubert.questions where id=1");
            assertEquals(0L, queryLong(connection, "select count(*) from schubert.async_jobs where id=1"));
            connection.rollback();
        }
    }

    @Test
    @Order(10)
    @DisplayName("PT-DB-010 999-link boundary and deferred trigger")
    void entryAudioLinkUpperBoundaryAndDeferredTriggerAreEffective() throws SQLException {
        try (Connection connection = connection(ADMIN)) {
            connection.setAutoCommit(false);
            execute(connection, scriptFileInsert(501, 1, 10));
            execute(connection, speakerInsert(502, 1));
            execute(connection, scriptEntryInsert(503, 1, 501, 502));
            execute(connection,
                    "insert into schubert.audio_files(id,game_id,storage_relative_path,display_path,file_name,basename,audio_role,byte_size,sha256,created_at) "
                            + "select 10000+g,1,'audio/'||g,'audio/'||g,g||'.ogg',g||'.ogg','voice',1,'"
                            + HASH + "','" + FIXED_TIME + "' from generate_series(1,1000) g");
            execute(connection,
                    "insert into schubert.entry_audio_links(entry_id,audio_file_id,game_id,link_type,display_order,created_at) "
                            + "select 503,10000+g,1,'voice',g,'" + FIXED_TIME + "' from generate_series(1,999) g");
            execute(connection, "set constraints all immediate");
            assertEquals(999L, queryLong(connection,
                    "select count(*) from schubert.entry_audio_links where entry_id=503 and link_type='voice'"));

            Savepoint triggerProbe = connection.setSavepoint();
            execute(connection, "alter table schubert.entry_audio_links drop constraint uq_entry_audio_links_entry_type_order");
            execute(connection, "alter table schubert.entry_audio_links drop constraint ck_entry_audio_links_display_order");
            execute(connection, "set constraints all deferred");
            execute(connection,
                    "insert into schubert.entry_audio_links values(503,11000,1,'voice',1000,'" + FIXED_TIME + "')");
            SQLException error = assertThrows(SQLException.class,
                    () -> execute(connection, "set constraints all immediate"));
            assertEquals("23514", error.getSQLState());
            PSQLException postgresError = (PSQLException) error;
            assertNotNull(postgresError.getServerErrorMessage());
            assertEquals("ck_entry_audio_links_entry_type_limit",
                    postgresError.getServerErrorMessage().getConstraint());
            connection.rollback(triggerProbe);
            connection.rollback();
        }
    }

    @Test
    @Order(11)
    @DisplayName("PT-DB-011 initial data, security views and hold-aware cleanup functions")
    void initialDataViewsAndFunctionsMatchTheSecurityContract() throws SQLException {
        assertEquals(List.of("1|NUKITASHI1|NUKITASHI|1", "2|NUKITASHI2|NUKITASHI2|2"), queryList(ADMIN,
                "select id||'|'||code||'|'||title||'|'||display_order from schubert.games order by id"));
        assertEquals(2L, queryLong(ADMIN,
                "select count(*) from pg_class c join pg_namespace n on n.oid=c.relnamespace "
                        + "where n.nspname='schubert' and c.relname like 'v_ops_%' "
                        + "and array_to_string(c.reloptions,',') like '%security_barrier=true%'"));
        assertEquals(6L, queryLong(ADMIN,
                "select count(*) from pg_proc p join pg_namespace n on n.oid=p.pronamespace "
                        + "where n.nspname='schubert' and p.proname like 'maintenance_cleanup_%' "
                        + "and p.prosecdef and array_to_string(p.proconfig,',')="
                        + "'search_path=pg_catalog, schubert, schubert_web_session'"));
        assertFalse(queryBoolean(ADMIN,
                "select has_function_privilege('public','schubert.maintenance_cleanup_logs(uuid,timestamptz,integer)','EXECUTE')"));
        assertCleanupFunctionGuards();

        try (Connection connection = connection(ADMIN)) {
            connection.setAutoCommit(false);
            execute(connection,
                    "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status) "
                            + "values('" + UUID_2 + "','2026-09-02','BACKUP_DB',1,'" + FIXED_TIME + "','"
                            + FIXED_TIME + "','SUCCESS'),('" + UUID_2
                            + "','2026-09-02','BACKUP_CONFIG',1,'" + FIXED_TIME + "','" + FIXED_TIME
                            + "','SUCCESS')");
            execute(connection,
                    "insert into schubert.app_logs(id,logged_at,service,category,level,action,message,"
                            + "security_hold_until) values"
                            + "(701,'2026-01-01 00:00:00+00','API','SECURITY','INFO','TEST_HOLD',"
                            + "'public held log','2026-09-03 00:00:00+00'),"
                            + "(702,'2026-01-01 00:00:01+00','API','ACTION','INFO','TEST_ACTION',"
                            + "'public ordinary log',null),"
                            + "(703,'2026-01-01 00:00:02+00','API','SECURITY','INFO','TEST_EXPIRED_HOLD',"
                            + "'public expired hold log','" + FIXED_TIME + "')");
            execute(connection, "set role schubert_batch");
            assertEquals("3|2|1|OK", queryString(connection,
                    "select target_count||'|'||deleted_count||'|'||skipped_count||'|'||reason_code "
                            + "from schubert.maintenance_cleanup_logs('" + UUID_2 + "','" + FIXED_TIME + "',10)"));
            execute(connection, "reset role");
            assertEquals(1L, queryLong(connection, "select count(*) from schubert.app_logs where id=701"));
            assertEquals(0L, queryLong(connection, "select count(*) from schubert.app_logs where id in (702,703)"));

            execute(connection, userInsert(801, "cleanup-owner", 0));
            execute(connection,
                    "insert into schubert.auth_sessions(id,user_id,context_hash,context_ciphertext,key_version,"
                            + "issued_at,last_accessed_at,expires_at,client_address,created_message_id) values"
                            + "('00000000-0000-0000-0000-000000000801',801,'" + "b".repeat(64) + "'," + CIPHER
                            + ",'key-1','2026-08-30 00:00:00+00','2026-08-30 12:00:00+00',"
                            + "'2026-08-31 00:00:00+00','127.0.0.81','00000000-0000-0000-0000-000000000811'),"
                            + "('00000000-0000-0000-0000-000000000802',801,'" + "c".repeat(64) + "'," + CIPHER
                            + ",'key-1','2026-09-01 10:00:00+00','2026-09-01 11:00:00+00',"
                            + "'2026-09-01 12:00:00+00','127.0.0.82','00000000-0000-0000-0000-000000000812')");
            execute(connection,
                    "insert into schubert.login_ip_attempts values"
                            + "('127.0.0.83',1,'2026-08-31 00:00:00+00',null,'2026-08-31 00:01:00+00'),"
                            + "('127.0.0.84',1,'2026-09-01 23:50:00+00',null,'2026-09-01 23:51:00+00')");
            execute(connection,
                    "insert into schubert_web_session.web_http_sessions values"
                            + "('00000000-0000-0000-0000-000000000803','" + "d".repeat(64) + "'," + CIPHER
                            + ",'key-1','2026-08-31 00:00:00+00','2026-08-31 12:00:00+00',"
                            + "'2026-09-01 00:00:00+00',28800,0),"
                            + "('00000000-0000-0000-0000-000000000804','" + "e".repeat(64) + "'," + CIPHER
                            + ",'key-1','2026-09-01 00:00:00+00','2026-09-02 00:00:00+00',"
                            + "'2026-09-03 00:00:00+00',28800,0)");
            execute(connection, "set role schubert_batch");
            assertEquals("3|3|0|OK", queryString(connection,
                    "select target_count||'|'||deleted_count||'|'||skipped_count||'|'||reason_code "
                            + "from schubert.maintenance_cleanup_sessions('" + UUID_2 + "','" + FIXED_TIME + "',10)"));
            execute(connection, "reset role");
            assertEquals(1L, queryLong(connection, "select count(*) from schubert.auth_sessions where user_id=801"));
            assertEquals(1L, queryLong(connection,
                    "select count(*) from schubert.login_ip_attempts where client_address='127.0.0.84'"));
            assertEquals(1L, queryLong(connection,
                    "select count(*) from schubert_web_session.web_http_sessions where id="
                            + "'00000000-0000-0000-0000-000000000804'"));
            verifyNotificationAndQuestionCleanup(connection);
            verifyMessageStoreCleanup(connection);
            verifyBatchRunCleanup(connection);
            connection.rollback();
        }
    }

    private static void assertCleanupFunctionGuards() throws SQLException {
        for (Map.Entry<String, Integer> cleanup : CLEANUP_FUNCTION_LIMITS.entrySet()) {
            String function = "schubert." + cleanup.getKey();
            assertEquals("BACKUP_GATE", queryString("schubert_batch",
                    "select reason_code from " + function + "('" + UUID_1 + "','" + FIXED_TIME + "',1)"));
            assertSqlState("schubert_batch", "22023",
                    "select * from " + function + "(null,'" + FIXED_TIME + "',1)");
            assertSqlState("schubert_batch", "22023",
                    "select * from " + function + "('" + UUID_1 + "',null,1)");
            assertSqlState("schubert_batch", "22023",
                    "select * from " + function + "('" + UUID_1 + "','" + FIXED_TIME + "',0)");
            assertSqlState("schubert_batch", "22023",
                    "select * from " + function + "('" + UUID_1 + "','" + FIXED_TIME + "',"
                            + (cleanup.getValue() + 1) + ")");
        }
        try (Connection holder = connection(ADMIN)) {
            holder.setAutoCommit(false);
            execute(holder, "select pg_advisory_xact_lock(71419602)");
            for (String cleanup : CLEANUP_FUNCTION_LIMITS.keySet()) {
                assertEquals("LOCK_BUSY", queryString("schubert_batch",
                        "select reason_code from schubert." + cleanup + "('" + UUID_1 + "','"
                                + FIXED_TIME + "',1)"));
            }
            holder.rollback();
        }
    }

    private static void verifyNotificationAndQuestionCleanup(Connection connection) throws SQLException {
        execute(connection,
                "insert into schubert.questions(id,receipt_id,owner_user_id,body,operation_token,submitted_at) "
                        + "select g,lpad(g::text,26,'0'),801,'public cleanup question',"
                        + "('00000000-0000-0000-0000-'||lpad(g::text,12,'0'))::uuid,'2026-08-30 00:00:00+00' "
                        + "from generate_series(901,904) g");
        execute(connection,
                "insert into schubert.async_jobs(id,question_id,owner_user_id,state,message_id,correlation_id,"
                        + "received_at,state_changed_at) select g,g,801,'RECEIVED',"
                        + "('00000000-0000-0000-0001-'||lpad(g::text,12,'0'))::uuid,"
                        + "('00000000-0000-0000-0002-'||lpad(g::text,12,'0'))::uuid,"
                        + "'2026-08-30 00:00:00+00','2026-08-30 00:00:00+00' "
                        + "from generate_series(901,904) g");
        execute(connection,
                "insert into schubert.notifications(id,job_id,question_id,owner_user_id,notification_type,state,"
                        + "accepted_at,state_changed_at,error_code,error_message,created_at,updated_at) values"
                        + "(901,901,901,801,'ACCEPTED','CANCELLED','2026-08-30 00:00:00+00',"
                        + "'2026-09-01 00:00:00+00',null,null,'2026-08-30 00:00:00+00','2026-09-01 00:00:00+00'),"
                        + "(902,902,902,801,'COMPLETED','COMPLETED','2026-08-30 00:00:00+00',"
                        + "'2026-09-01 00:00:00+00',null,null,'2026-08-30 00:00:00+00','2026-09-01 00:00:00+00'),"
                        + "(903,903,903,801,'ERROR','ERROR','2026-08-30 00:00:00+00',"
                        + "'2026-09-01 00:00:00+00','PROCESS_FAILED','public test error',"
                        + "'2026-08-30 00:00:00+00','2026-09-01 00:00:00+00'),"
                        + "(904,904,904,801,'COMPLETED','COMPLETED','2026-09-01 00:00:00+00',"
                        + "'2026-09-01 12:00:00+00',null,null,'2026-09-01 00:00:00+00','2026-09-01 12:00:00+00')");
        execute(connection, "set role schubert_batch");
        assertEquals("3|3|0|OK", cleanupResult(connection, "maintenance_cleanup_notifications", FIXED_TIME, 10));
        execute(connection, "reset role");
        assertEquals(1L, queryLong(connection, "select count(*) from schubert.notifications where id between 901 and 904"));

        execute(connection,
                "insert into schubert.questions(id,receipt_id,owner_user_id,body,operation_token,submitted_at,is_deleted,"
                        + "deleted_at,deleted_by) select g,lpad(g::text,26,'0'),801,'public aggregate cleanup',"
                        + "('00000000-0000-0000-0003-'||lpad(g::text,12,'0'))::uuid,'2026-08-30 00:00:00+00',"
                        + "g<>913,case when g<>913 then '2026-08-31 00:00:00+00'::timestamptz else null end,"
                        + "case when g<>913 then 801 else null end from generate_series(911,913) g");
        execute(connection,
                "insert into schubert.async_jobs(id,question_id,owner_user_id,state,message_id,correlation_id,"
                        + "received_at,state_changed_at) values(912,912,801,'RECEIVED',"
                        + "'00000000-0000-0000-0004-000000000912','00000000-0000-0000-0005-000000000912',"
                        + "'2026-08-30 00:00:00+00','2026-08-30 00:00:00+00')");
        execute(connection,
                "insert into schubert.notifications(id,job_id,question_id,owner_user_id,notification_type,state,"
                        + "accepted_at,state_changed_at,created_at,updated_at) values(912,912,912,801,'ACCEPTED','ACCEPTED',"
                        + "'2026-08-30 00:00:00+00','2026-08-30 00:00:00+00',"
                        + "'2026-08-30 00:00:00+00','2026-08-30 00:00:00+00')");
        execute(connection, "set role schubert_batch");
        assertEquals("1|1|0|OK", cleanupResult(connection, "maintenance_cleanup_questions", FIXED_TIME, 10));
        execute(connection, "reset role");
        assertEquals(List.of("912", "913"), queryList(connection,
                "select id::text from schubert.questions where id between 911 and 913 order by id"));
    }

    private static void verifyMessageStoreCleanup(Connection connection) throws SQLException {
        execute(connection,
                "insert into schubert.request_inbox(message_id,correlation_id,request_layout_id,request_version,"
                        + "request_fingerprint_hmac,fingerprint_key_version,processing_state,result_ref_type,"
                        + "response_layout_id,response_version,created_at,completed_at,expires_at) values"
                        + "('00000000-0000-0000-0006-000000000001','00000000-0000-0000-0006-000000000002',"
                        + "'LGNREQ01','001','" + HASH + "','key-1','COMPLETED','NONE','LGNRSP01','001',"
                        + "'2026-08-29 00:00:00+00','2026-08-29 00:00:01+00','2026-08-31 00:00:00+00'),"
                        + "('00000000-0000-0000-0006-000000000003','00000000-0000-0000-0006-000000000004',"
                        + "'LGNREQ01','001','" + "f".repeat(64) + "','key-1','PROCESSING',null,null,null,"
                        + "'2026-08-29 00:00:00+00',null,'2026-08-31 00:00:00+00')");
        execute(connection,
                "insert into schubert.mq_outbox(id,message_id,correlation_id,destination,layout_id,layout_version,body,"
                        + "status,next_attempt_at,created_at,sent_at) values"
                        + "(921,'00000000-0000-0000-0007-000000000001','00000000-0000-0000-0007-000000000002',"
                        + "'nk.async.work','QWKREQ01','001',decode('00','hex'),'SENT','2026-08-29 00:00:00+00',"
                        + "'2026-08-29 00:00:00+00','2026-08-31 00:00:00+00'),"
                        + "(922,'00000000-0000-0000-0007-000000000003','00000000-0000-0000-0007-000000000004',"
                        + "'nk.async.work','QWKREQ01','001',decode('00','hex'),'PENDING','2026-08-29 00:00:00+00',"
                        + "'2026-08-29 00:00:00+00',null)");
        execute(connection,
                "insert into schubert_web_session.web_log_outbox(id,message_id,correlation_id,layout_id,layout_version,"
                        + "payload_ciphertext,key_version,status,next_attempt_at,created_at,sent_at) values"
                        + "(923,'00000000-0000-0000-0008-000000000001','00000000-0000-0000-0008-000000000002',"
                        + "'WLGEVT01','001'," + CIPHER + ",'key-1','SENT','2026-08-29 00:00:00+00',"
                        + "'2026-08-29 00:00:00+00','2026-08-31 00:00:00+00'),"
                        + "(924,'00000000-0000-0000-0008-000000000003','00000000-0000-0000-0008-000000000004',"
                        + "'WLGEVT01','001'," + CIPHER + ",'key-1','ERROR','2026-08-29 00:00:00+00',"
                        + "'2026-08-29 00:00:00+00',null)");
        execute(connection, "set role schubert_batch");
        assertEquals("3|3|0|OK", cleanupResult(connection, "maintenance_cleanup_message_stores", FIXED_TIME, 10));
        execute(connection, "reset role");
        assertEquals(1L, queryLong(connection,
                "select count(*) from schubert.request_inbox where message_id in "
                        + "('00000000-0000-0000-0006-000000000001','00000000-0000-0000-0006-000000000003')"));
        assertEquals(1L, queryLong(connection, "select count(*) from schubert.mq_outbox where id in (921,922)"));
        assertEquals(1L, queryLong(connection,
                "select count(*) from schubert_web_session.web_log_outbox where id in (923,924)"));
    }

    private static void verifyBatchRunCleanup(Connection connection) throws SQLException {
        execute(connection,
                "insert into schubert.batch_runs(id,run_id,business_date,step,attempt,started_at,ended_at,status) values"
                        + "(931,'00000000-0000-0000-0009-000000000001','2024-01-01','OLD_SUCCESS',1,"
                        + "'2024-01-01 00:00:00+00','2024-01-01 00:01:00+00','SUCCESS'),"
                        + "(932,'00000000-0000-0000-0009-000000000002','2024-01-01','OLD_WARNING',1,"
                        + "'2024-01-01 00:00:00+00','2024-01-01 00:01:00+00','WARNING'),"
                        + "(933,'00000000-0000-0000-0009-000000000003','2024-01-01','OLD_SKIPPED',1,"
                        + "'2024-01-01 00:00:00+00','2024-01-01 00:01:00+00','SKIPPED'),"
                        + "(934,'00000000-0000-0000-0009-000000000004','2024-01-01','OLD_FAILED',1,"
                        + "'2024-01-01 00:00:00+00','2024-01-01 00:01:00+00','FAILED'),"
                        + "(935,'00000000-0000-0000-0009-000000000005','2024-01-01','OLD_RUNNING',1,"
                        + "'2024-01-01 00:00:00+00',null,'RUNNING'),"
                        + "(936,'00000000-0000-0000-0009-000000000006','2026-01-01','RECENT_SUCCESS',1,"
                        + "'2026-01-01 00:00:00+00','2026-01-01 00:01:00+00','SUCCESS')");
        execute(connection, "set role schubert_batch");
        assertEquals("3|3|0|OK", cleanupResult(connection, "maintenance_cleanup_batch_runs",
                "2025-01-01 00:00:00+00", 10));
        execute(connection, "reset role");
        assertEquals(List.of("934", "935", "936"), queryList(connection,
                "select id::text from schubert.batch_runs where id between 931 and 936 order by id"));
    }

    private static String cleanupResult(Connection connection, String function, String cutoff, int limit)
            throws SQLException {
        return queryString(connection,
                "select target_count||'|'||deleted_count||'|'||skipped_count||'|'||reason_code from schubert."
                        + function + "('" + UUID_2 + "','" + cutoff + "'," + limit + ")");
    }

    @Test
    @Order(12)
    @DisplayName("PT-DB-012 positive and negative role grants")
    void serviceRoleGrantsDenyCrossBoundaryAccess() throws SQLException {
        assertEquals("false|false|true", queryString(ADMIN,
                "select m.admin_option||'|'||m.inherit_option||'|'||m.set_option "
                        + "from pg_auth_members m join pg_roles granted on granted.oid=m.roleid "
                        + "join pg_roles member on member.oid=m.member "
                        + "where granted.rolname='nk_owner' and member.rolname='schubert_migration'"));
        assertDenied(MIGRATION, "select count(*) from schubert.games");
        try (Connection migration = connection(MIGRATION)) {
            execute(migration, "set role nk_owner");
            assertEquals(2L, queryLong(migration, "select count(*) from schubert.games"));
        }
        assertAllowed("schubert_app", "select count(*) from schubert.games");
        assertDenied("schubert_app", "select count(*) from schubert_web_session.web_http_sessions");
        assertAllowed("schubert_web_session", "select count(*) from schubert_web_session.web_http_sessions");
        assertDenied("schubert_web_session", "select count(*) from schubert.app_users");
        assertAllowed("schubert_batch", "select count(*) from schubert.batch_runs");
        assertDenied("schubert_batch", "select count(*) from schubert.questions");
        assertAllowed("schubert_backup", "select count(*) from schubert.questions");
        assertDenied("schubert_backup", "insert into schubert.login_ip_attempts values('127.0.0.2',0,'"
                + FIXED_TIME + "',null,'" + FIXED_TIME + "')");
        assertAllowed("schubert_ops_ro", "select count(*) from schubert.v_ops_component_counts");
        assertDenied("schubert_ops_ro", "select count(*) from schubert.app_logs");
        assertDenied("schubert_ops_ro", "select count(*) from schubert.auth_sessions");
    }

    @Test
    @Order(13)
    @DisplayName("PT-DB-013 checksum drift and destructive Flyway settings")
    void checksumDriftIsDetectedAndDestructiveFlywayOperationsAreDisabled() throws Exception {
        assertTrue(flyway.getConfiguration().isCleanDisabled());
        assertFalse(flyway.getConfiguration().isOutOfOrder());
        assertFalse(flyway.getConfiguration().isBaselineOnMigrate());
        assertThrows(Exception.class, flyway::clean);

        Path changed = Files.createDirectories(MODULE.resolve("target/checksum-drift"));
        copyMigrationResources(changed);
        Path v001 = changed.resolve("V001__schemas_and_extension.sql");
        Files.writeString(v001, Files.readString(v001, StandardCharsets.UTF_8) + "-- drift probe\n",
                StandardCharsets.UTF_8);
        Flyway driftFlyway = configuredFlyway(jdbcUrl, false, "filesystem:" + changed);
        assertFalse(driftFlyway.validateWithResult().validationSuccessful);
    }

    @Test
    @Order(14)
    @DisplayName("PT-DB-014 concurrent initial migrate is serialized")
    void concurrentInitialMigrationProducesOneHistory() throws Exception {
        String parallelDatabase = "schubert_parallel";
        run(pgBinary("createdb"), "-h", "127.0.0.1", "-p", Integer.toString(port), "-U", ADMIN, parallelDatabase);
        String parallelUrl = "jdbc:postgresql://127.0.0.1:" + port + "/" + parallelDatabase;
        executeResource(ADMIN, parallelUrl, "db/provisioning/001_roles.sql");
        execute(ADMIN, parallelUrl, "create schema schubert_meta authorization nk_owner");

        Callable<Integer> migrate = () -> configuredFlyway(parallelUrl, false, "classpath:db/migration")
                .migrate().migrationsExecuted;
        try (ExecutorService executor = Executors.newFixedThreadPool(2)) {
            Future<Integer> first = executor.submit(migrate);
            Future<Integer> second = executor.submit(migrate);
            assertEquals(5, first.get() + second.get());
        }
        assertEquals(5L, queryLong(ADMIN, parallelUrl,
                "select count(*) from schubert_meta.flyway_schema_history where success"));
        assertEquals(21L, queryLong(ADMIN, parallelUrl,
                "select count(*) from information_schema.tables where table_schema in ('schubert','schubert_web_session') "
                        + "and table_type='BASE TABLE'"));
    }

    @Test
    @Order(15)
    @DisplayName("PT-DB-015 SQL resources contain no credential or unsafe bytes")
    void sqlResourcesContainNoCredentialOrUnsafeBytes() throws Exception {
        List<Path> resources = new ArrayList<>();
        try (var paths = Files.walk(MODULE.resolve("src/main/resources/db"))) {
            paths.filter(Files::isRegularFile).forEach(resources::add);
        }
        assertEquals(6, resources.size());
        for (Path resource : resources) {
            byte[] bytes = Files.readAllBytes(resource);
            String text = new String(bytes, StandardCharsets.UTF_8);
            assertFalse(text.contains("\r"), resource.toString());
            assertFalse(text.indexOf('\0') >= 0, resource.toString());
            assertFalse(text.matches("(?is).*PASSWORD\\s+['\"].*"), resource.toString());
            assertFalse(text.matches("(?is).*jdbc:postgresql://[^\\s]+:[^\\s]+@.*"), resource.toString());
            assertTrue(text.endsWith("\n"), resource.toString());
        }
        writeEvidenceSnapshots();
    }

    private static void writeEvidenceSnapshots() throws Exception {
        Path databaseEvidence = Files.createDirectories(MODULE.resolve("target/pt-evidence/database"));
        writeQueryEvidence(databaseEvidence.resolve("migration-history.tsv"),
                "version\tdescription\tchecksum\tsuccess",
                "select coalesce(version,'')||E'\\t'||description||E'\\t'||coalesce(checksum::text,'')||E'\\t'||success "
                        + "from schubert_meta.flyway_schema_history order by installed_rank");
        writeQueryEvidence(databaseEvidence.resolve("columns.tsv"),
                "table\tcolumn\ttype\tnullable\tdefault\tidentity\tgenerated",
                "select c.table_schema||'.'||c.table_name||E'\\t'||c.column_name||E'\\t'||c.data_type||E'\\t'||"
                        + "c.is_nullable||E'\\t'||replace(replace(coalesce(c.column_default,''),chr(9),' '),chr(10),' ')"
                        + "||E'\\t'||c.is_identity||E'\\t'||c.is_generated "
                        + "from information_schema.columns c join information_schema.tables t "
                        + "on t.table_schema=c.table_schema and t.table_name=c.table_name "
                        + "where t.table_type='BASE TABLE' and c.table_schema in ('schubert','schubert_web_session') "
                        + "order by c.table_schema,c.table_name,c.ordinal_position");
        writeQueryEvidence(databaseEvidence.resolve("constraints.tsv"),
                "schema\tconstraint\ttype\tdeferrable\tdefinition",
                "select n.nspname||E'\\t'||c.conname||E'\\t'||c.contype::text||E'\\t'||c.condeferrable||E'\\t'||"
                        + "replace(replace(pg_get_constraintdef(c.oid),chr(9),' '),chr(10),' ') "
                        + "from pg_constraint c join pg_namespace n on n.oid=c.connamespace "
                        + "where n.nspname in ('schubert','schubert_web_session') order by n.nspname,c.conname");
        writeQueryEvidence(databaseEvidence.resolve("indexes.tsv"), "schema\tindex\tdefinition",
                "select schemaname||E'\\t'||indexname||E'\\t'||replace(replace(indexdef,chr(9),' '),chr(10),' ') "
                        + "from pg_indexes where schemaname in ('schubert','schubert_web_session') "
                        + "order by schemaname,indexname");
        writeQueryEvidence(databaseEvidence.resolve("programmable-objects.tsv"),
                "kind\tschema\tname\tsecurity",
                "select 'FUNCTION'||E'\\t'||n.nspname||E'\\t'||p.proname||E'\\t'||"
                        + "case when p.prosecdef then 'SECURITY DEFINER' else 'INVOKER' end "
                        + "from pg_proc p join pg_namespace n on n.oid=p.pronamespace "
                        + "where n.nspname='schubert' and p.proname like 'maintenance_cleanup_%' "
                        + "union all select 'VIEW'||E'\\t'||n.nspname||E'\\t'||c.relname||E'\\t'||"
                        + "coalesce(array_to_string(c.reloptions,','),'') from pg_class c "
                        + "join pg_namespace n on n.oid=c.relnamespace "
                        + "where n.nspname='schubert' and c.relkind='v' order by 1");
        writeQueryEvidence(databaseEvidence.resolve("role-grants.tsv"),
                "role\tnk_owner_admin\tnk_owner_inherit\tnk_owner_set\tschubert_schema\tbase_table\tops_view",
                "with roles(role_name) as (values ('schubert_migration'),('schubert_app'),('schubert_batch'),"
                        + "('schubert_backup'),('schubert_web_session'),('schubert_ops_ro')) "
                        + "select r.role_name||E'\\t'||coalesce(m.admin_option::text,'false')||E'\\t'||"
                        + "coalesce(m.inherit_option::text,'false')||E'\\t'||coalesce(m.set_option::text,'false')||E'\\t'||"
                        + "has_schema_privilege(r.role_name,'schubert','USAGE')||E'\\t'||"
                        + "has_table_privilege(r.role_name,'schubert.app_logs','SELECT')||E'\\t'||"
                        + "has_table_privilege(r.role_name,'schubert.v_ops_component_counts','SELECT') "
                        + "from roles r left join pg_roles member on member.rolname=r.role_name "
                        + "left join pg_auth_members m on m.member=member.oid "
                        + "and m.roleid=(select oid from pg_roles where rolname='nk_owner') "
                        + "order by r.role_name");
        writeQueryEvidence(databaseEvidence.resolve("sql-results.tsv"), "assertion\tactual",
                "select 'games'||E'\\t'||string_agg(id||':'||code||':'||title||':'||display_order,',' order by id) "
                        + "from schubert.games union all "
                        + "select 'table_count'||E'\\t'||count(*) from information_schema.tables "
                        + "where table_schema in ('schubert','schubert_web_session') and table_type='BASE TABLE' "
                        + "union all select 'explicit_index_count'||E'\\t'||count(*) from pg_indexes "
                        + "where schemaname in ('schubert','schubert_web_session') "
                        + "and (indexname like 'ix\\_%' escape '\\' or indexname in "
                        + "('uq_request_inbox_operation','uq_batch_runs_business_step_success'))");
        Files.writeString(databaseEvidence.resolve("resource-scan.txt"),
                "resources=6\ncredential_hits=0\nunsafe_crlf=0\nnul_bytes=0\nresult=PASS\n",
                StandardCharsets.UTF_8);
    }

    private static void writeQueryEvidence(Path path, String header, String sql) throws Exception {
        List<String> lines = new ArrayList<>();
        lines.add(header);
        lines.addAll(queryList(ADMIN, sql));
        Files.write(path, lines, StandardCharsets.UTF_8);
    }

    private static Flyway configuredFlyway(String url, boolean createSchemas, String location) {
        return Flyway.configure()
                .dataSource(url, MIGRATION, "")
                .defaultSchema("schubert_meta")
                .schemas("schubert_meta")
                .createSchemas(createSchemas)
                .initSql("SET ROLE nk_owner")
                .table("flyway_schema_history")
                .locations(location)
                .validateOnMigrate(true)
                .outOfOrder(false)
                .baselineOnMigrate(false)
                .cleanDisabled(true)
                .load();
    }

    private static Path locatePostgreSqlRoot() {
        String configured = System.getenv("SCHUBERT_PG_ROOT");
        Path candidate = configured == null || configured.isBlank()
                ? Path.of("/home/mini/codex/project1/work/characterization-tools/root/usr")
                : Path.of(configured);
        Path postgres = candidate.resolve("lib/postgresql/18/bin/postgres");
        assertTrue(Files.isExecutable(postgres), "PostgreSQL 18 root not found: " + candidate);
        return candidate.toAbsolutePath().normalize();
    }

    private static String pgBinary(String name) {
        return pgRoot.resolve("lib/postgresql/18/bin").resolve(name).toString();
    }

    private static String serverOptions() {
        return "-p " + port + " -h 127.0.0.1 -k /tmp"
                + " -c extension_control_path=" + pgRoot.resolve("share/postgresql/18")
                + " -c dynamic_library_path=" + pgRoot.resolve("lib/postgresql/18/lib")
                + " -c timezone=UTC";
    }

    private static int availablePort() throws IOException {
        try (ServerSocket socket = new ServerSocket(0, 1, InetAddress.getLoopbackAddress())) {
            return socket.getLocalPort();
        }
    }

    private static void run(String... command) throws IOException, InterruptedException {
        ProcessBuilder builder = new ProcessBuilder(command);
        builder.redirectErrorStream(true);
        builder.redirectOutput(ProcessBuilder.Redirect.appendTo(clusterRoot.resolve("process.log").toFile()));
        String libraryPath = pgRoot.resolve("lib/x86_64-linux-gnu") + ":"
                + pgRoot.resolve("lib/postgresql/18/lib");
        builder.environment().put("LD_LIBRARY_PATH", libraryPath);
        Process process = builder.start();
        boolean finished = process.waitFor(Duration.ofSeconds(30));
        assertTrue(finished, "command timed out: " + command[0]);
        assertEquals(0, process.exitValue(), "command failed: " + String.join(" ", command));
    }

    private static Connection connection(String role) throws SQLException {
        return DriverManager.getConnection(jdbcUrl, role, "");
    }

    private static Connection connection(String role, String url) throws SQLException {
        return DriverManager.getConnection(url, role, "");
    }

    private static void executeResourceAsAdmin(String resource) throws Exception {
        executeResource(ADMIN, jdbcUrl, resource);
    }

    private static void executeResource(String role, String url, String resource) throws Exception {
        URI uri = resourceUri(resource);
        String sql = Files.readString(Path.of(uri), StandardCharsets.UTF_8);
        execute(role, url, sql);
    }

    private static URI resourceUri(String resource) throws URISyntaxException {
        var url = DatabaseMigrationTest.class.getClassLoader().getResource(resource);
        assertNotNull(url, "missing resource " + resource);
        return url.toURI();
    }

    private static void execute(String role, String url, String sql) throws SQLException {
        try (Connection connection = connection(role, url); Statement statement = connection.createStatement()) {
            statement.execute(sql);
        }
    }

    private static void execute(Connection connection, String sql) throws SQLException {
        try (Statement statement = connection.createStatement()) {
            statement.execute(sql);
        }
    }

    private static void assertRejects(Connection connection, String sqlState, String sql) throws SQLException {
        Savepoint savepoint = connection.setSavepoint();
        SQLException error = assertThrows(SQLException.class, () -> execute(connection, sql));
        assertEquals(sqlState, error.getSQLState());
        connection.rollback(savepoint);
    }

    private static void assertSqlState(String role, String sqlState, String sql) {
        SQLException error = assertThrows(SQLException.class, () -> execute(role, jdbcUrl, sql));
        assertEquals(sqlState, error.getSQLState());
    }

    private static void assertAllowed(String role, String sql) throws SQLException {
        execute(role, jdbcUrl, sql);
    }

    private static void assertDenied(String role, String sql) {
        assertSqlState(role, "42501", sql);
    }

    private static long queryLong(String role, String sql) throws SQLException {
        return queryLong(role, jdbcUrl, sql);
    }

    private static long queryLong(String role, String url, String sql) throws SQLException {
        try (Connection connection = connection(role, url)) {
            return queryLong(connection, sql);
        }
    }

    private static long queryLong(Connection connection, String sql) throws SQLException {
        try (Statement statement = connection.createStatement(); ResultSet result = statement.executeQuery(sql)) {
            assertTrue(result.next());
            return result.getLong(1);
        }
    }

    private static String queryString(String role, String sql) throws SQLException {
        try (Connection connection = connection(role)) {
            return queryString(connection, sql);
        }
    }

    private static String queryString(Connection connection, String sql) throws SQLException {
        try (Statement statement = connection.createStatement(); ResultSet result = statement.executeQuery(sql)) {
            assertTrue(result.next());
            return result.getString(1);
        }
    }

    private static boolean queryBoolean(String role, String sql) throws SQLException {
        try (Connection connection = connection(role); Statement statement = connection.createStatement();
                ResultSet result = statement.executeQuery(sql)) {
            assertTrue(result.next());
            return result.getBoolean(1);
        }
    }

    private static Set<String> querySet(String role, String sql) throws SQLException {
        return new TreeSet<>(queryList(role, sql));
    }

    private static List<String> queryList(String role, String sql) throws SQLException {
        try (Connection connection = connection(role)) {
            return queryList(connection, sql);
        }
    }

    private static List<String> queryList(Connection connection, String sql) throws SQLException {
        try (Statement statement = connection.createStatement(); ResultSet result = statement.executeQuery(sql)) {
            List<String> values = new ArrayList<>();
            while (result.next()) {
                values.add(result.getString(1));
            }
            return values;
        }
    }

    private static Map<String, Set<String>> queryGroupedSet(String sql) throws SQLException {
        try (Connection connection = connection(ADMIN); Statement statement = connection.createStatement();
                ResultSet result = statement.executeQuery(sql)) {
            Map<String, Set<String>> values = new LinkedHashMap<>();
            while (result.next()) {
                values.computeIfAbsent(result.getString(1), ignored -> new LinkedHashSet<>()).add(result.getString(2));
            }
            return values;
        }
    }

    private static String userInsert(long id, String username, long version) {
        return "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,"
                + "version,created_at,updated_at) values(" + id + ",'" + username + "','key" + id
                + "','{pbkdf2-v1}public-test-hash','USER','ACTIVE','" + FIXED_TIME + "'," + version + ",'"
                + FIXED_TIME + "','" + FIXED_TIME + "')";
    }

    private static String userInsertWithRole(long id, String role) {
        return "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,"
                + "created_at,updated_at) values(" + id + ",'user','key" + id
                + "','{pbkdf2-v1}public-test-hash','" + role + "','ACTIVE','" + FIXED_TIME + "','"
                + FIXED_TIME + "','" + FIXED_TIME + "')";
    }

    private static String questionInsert(long owner, boolean deleted, String deletedAt, String deletedBy) {
        return "insert into schubert.questions(id,receipt_id,owner_user_id,body,operation_token,submitted_at,is_deleted,"
                + "deleted_at,deleted_by) values(1,'0123456789ABCDEFGHJKMNPQRS'," + owner
                + ",'public test question','00000000-0000-0000-0000-000000000010','" + FIXED_TIME + "',"
                + deleted + "," + deletedAt + "," + deletedBy + ")";
    }

    private static String jobInsert(String state, String startedAt, String completedAt, String errorAt,
            String cancelledAt, String processingMessageId) {
        String errorFields = "ERROR".equals(state) ? ",'PROCESS_FAILED','public test error'" : ",null,null";
        return "insert into schubert.async_jobs(id,question_id,owner_user_id,state,message_id,correlation_id,"
                + "processing_message_id,received_at,state_changed_at,started_at,completed_at,error_at,cancelled_at,"
                + "last_error_code,last_error_message) values(1,1,"
                + "(select owner_user_id from schubert.questions where id=1),'" + state + "','"
                + "00000000-0000-0000-0000-000000000020','00000000-0000-0000-0000-000000000021',"
                + processingMessageId + ",'" + FIXED_TIME + "','" + FIXED_TIME + "'," + startedAt + ","
                + completedAt + "," + errorAt + "," + cancelledAt + errorFields + ")";
    }

    private static String scriptFileInsert(long id, int gameId, long order) {
        return "insert into schubert.script_files(id,game_id,display_order,storage_relative_path,display_path,file_name,"
                + "sha256,byte_size,created_at) values(" + id + "," + gameId + "," + order + ",'scenario/"
                + gameId + "/" + id + "','shown/" + id + "','" + id + ".ks','" + HASH + "',0,'"
                + FIXED_TIME + "')";
    }

    private static String speakerInsert(long id, int gameId) {
        return "insert into schubert.speakers(id,game_id,name,normalized_name,created_at) values(" + id + ","
                + gameId + ",'speaker" + id + "','speaker" + id + "','" + FIXED_TIME + "')";
    }

    private static String scriptEntryInsert(long id, int gameId, long fileId, long speakerId) {
        return "insert into schubert.script_entries(id,game_id,script_file_id,display_order,entry_index,entry_type,"
                + "speaker_id,speaker_label,body,raw_block,created_at) values(" + id + "," + gameId + "," + fileId
                + "," + id + ",0,'dialogue'," + speakerId + ",'speaker','body','raw','" + FIXED_TIME + "')";
    }

    private static String audioInsert(long id, int gameId) {
        return "insert into schubert.audio_files(id,game_id,storage_relative_path,display_path,file_name,basename,"
                + "audio_role,byte_size,sha256,created_at) values(" + id + "," + gameId + ",'audio/" + id
                + "','audio/" + id + "','" + id + ".ogg','" + id + ".ogg','voice',1,'" + HASH + "','"
                + FIXED_TIME + "')";
    }

    private static void copyMigrationResources(Path target) throws Exception {
        for (int version = 1; version <= 5; version++) {
            String prefix = "V%03d__".formatted(version);
            Path sourceDirectory = MODULE.resolve("src/main/resources/db/migration");
            Path source;
            try (var files = Files.list(sourceDirectory)) {
                source = files.filter(path -> path.getFileName().toString().startsWith(prefix)).findFirst().orElseThrow();
            }
            Files.copy(source, target.resolve(source.getFileName()), java.nio.file.StandardCopyOption.REPLACE_EXISTING);
        }
    }

    private static Set<String> expectedTables() {
        return Set.of(
                "schubert.app_users", "schubert.auth_sessions", "schubert.login_ip_attempts", "schubert.games",
                "schubert.script_files", "schubert.speakers", "schubert.script_entries", "schubert.audio_files",
                "schubert.entry_audio_links", "schubert.media_assets", "schubert.questions", "schubert.answers",
                "schubert.async_jobs", "schubert.notifications", "schubert.request_inbox", "schubert.mq_outbox",
                "schubert.app_logs", "schubert.batch_runs", "schubert_web_session.web_http_sessions",
                "schubert_web_session.pending_context_revocations", "schubert_web_session.web_log_outbox");
    }

    private static Set<String> expectedIdentityColumns() {
        return Set.of(
                "schubert.app_users.id", "schubert.script_files.id", "schubert.speakers.id",
                "schubert.script_entries.id", "schubert.audio_files.id", "schubert.media_assets.id",
                "schubert.questions.id", "schubert.answers.id", "schubert.async_jobs.id",
                "schubert.notifications.id", "schubert.mq_outbox.id", "schubert.app_logs.id",
                "schubert.batch_runs.id", "schubert_web_session.web_log_outbox.id");
    }

    private static Set<String> expectedSequences() {
        return expectedIdentityColumns().stream()
                .map(value -> value.substring(0, value.length() - 3) + "_id_seq")
                .collect(Collectors.toUnmodifiableSet());
    }

    private static Set<String> expectedExplicitIndexes() {
        return Set.of(
                "ix_app_users_role_status", "ix_app_users_locked_until", "ix_auth_sessions_user_active",
                "ix_auth_sessions_expires_at", "ix_login_ip_attempts_updated_at",
                "ix_script_entries_speaker_order", "ix_audio_files_basename", "ix_entry_audio_links_audio_id",
                "ix_media_assets_listing", "ix_questions_owner_active", "ix_questions_admin_active",
                "ix_questions_deleted", "ix_async_jobs_fifo", "ix_async_jobs_state_changed", "ix_async_jobs_owner",
                "ix_notifications_owner", "ix_notifications_cleanup", "uq_request_inbox_operation",
                "ix_request_inbox_expires", "ix_request_inbox_correlation", "ix_mq_outbox_dispatch",
                "ix_mq_outbox_lease", "ix_app_logs_logged_at", "ix_app_logs_category_time",
                "ix_app_logs_correlation_id", "ix_app_logs_message_id", "uq_batch_runs_business_step_success",
                "ix_batch_runs_run_step", "ix_batch_runs_status_started", "ix_web_http_sessions_expires_at",
                "ix_pending_context_revocations_due", "ix_pending_context_revocations_expires",
                "ix_web_log_outbox_dispatch", "ix_web_log_outbox_sent_cleanup",
                "ix_script_files_chapter_title_trgm", "ix_speakers_name_trgm",
                "ix_script_entries_body_search_trgm", "ix_questions_body_trgm", "ix_app_logs_message_trgm");
    }

    private static Map<String, Set<String>> expectedColumns() {
        Map<String, Set<String>> columns = new LinkedHashMap<>();
        columns.put("schubert.app_users", set("id username username_key password_hash role status failed_count failure_window_started_at locked_until last_login_at password_changed_at version created_at updated_at created_by updated_by"));
        columns.put("schubert.auth_sessions", set("id user_id context_hash context_ciphertext key_version issued_at last_accessed_at expires_at revoked revoked_at revoke_reason client_address created_message_id"));
        columns.put("schubert.login_ip_attempts", set("client_address failed_count window_started_at locked_until updated_at"));
        columns.put("schubert.games", set("id code title display_order created_at"));
        columns.put("schubert.script_files", set("id game_id display_order storage_relative_path display_path file_name section_code chapter_title sha256 byte_size created_at"));
        columns.put("schubert.speakers", set("id game_id name normalized_name is_protagonist notes created_at"));
        columns.put("schubert.script_entries", set("id game_id script_file_id display_order entry_index line_number entry_type speaker_id speaker_label body body_search raw_block created_at"));
        columns.put("schubert.audio_files", set("id game_id storage_relative_path display_path file_name basename audio_role container duration_ms byte_size sha256 created_at"));
        columns.put("schubert.entry_audio_links", set("entry_id audio_file_id game_id link_type display_order created_at"));
        columns.put("schubert.media_assets", set("id logical_id media_type title category section storage_relative_path display_path file_name byte_size sha256 mime_type parent_logical_id pair_key pair_role display_order created_at"));
        columns.put("schubert.questions", set("id receipt_id owner_user_id body operation_token submitted_at is_deleted deleted_at deleted_by version"));
        columns.put("schubert.answers", set("id question_id body answered_at provider_type is_deleted deleted_at deleted_by created_at updated_at"));
        columns.put("schubert.async_jobs", set("id question_id owner_user_id state message_id correlation_id processing_message_id received_at state_changed_at started_at completed_at error_at cancelled_at retry_count last_error_code last_error_message version"));
        columns.put("schubert.notifications", set("id job_id question_id owner_user_id notification_type state accepted_at state_changed_at error_code error_message created_at updated_at"));
        columns.put("schubert.request_inbox", set("message_id correlation_id request_layout_id request_version owner_user_id operation_token request_fingerprint_hmac fingerprint_key_version processing_state result_ref_type result_ref_id result_ref_uuid response_layout_id response_version response_body_encrypted response_key_version created_at completed_at expires_at"));
        columns.put("schubert.mq_outbox", set("id message_id correlation_id destination layout_id layout_version body status attempt_count next_attempt_at lease_owner lease_until created_at sent_at last_error_code last_error_detail"));
        columns.put("schubert.app_logs", set("id logged_at service category level action message request_id message_id correlation_id source_message_id actor_user_id actor_username http_method request_uri status_code remote_address duration_ms security_hold_until details"));
        columns.put("schubert.batch_runs", set("id run_id business_date step attempt started_at ended_at status target_count success_count failure_count byte_count error_code error_summary"));
        columns.put("schubert_web_session.web_http_sessions", set("id session_id_hash attributes_ciphertext key_version created_at last_accessed_at expires_at max_inactive_seconds version"));
        columns.put("schubert_web_session.pending_context_revocations", set("id context_ciphertext key_version requested_at attempt_count next_attempt_at expires_at last_error_code lease_owner lease_until"));
        columns.put("schubert_web_session.web_log_outbox", set("id message_id correlation_id layout_id layout_version payload_ciphertext key_version status attempt_count next_attempt_at created_at sent_at last_error_code lease_owner lease_until"));
        return columns;
    }

    private static Set<String> set(String values) {
        return Arrays.stream(values.split(" ")).collect(Collectors.toCollection(LinkedHashSet::new));
    }
}

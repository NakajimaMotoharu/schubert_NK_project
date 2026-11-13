"""Manufacture independent SSC340 DB Test sources only; never execute DB/roles/migrations."""
from pathlib import Path
import hashlib,json,datetime,re,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';o=b/'evidence/PG29696-nullable-check-source-manufacture-v1';assert not o.exists();o.mkdir()
tp=r/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/database/DatabaseMigrationTest.java';vp=tp.with_name('MigrationInventory.java');old=tp.read_text();versions=vp.read_text();assert len(re.findall(r'^  @Test$',old,re.M))==19
(o/'DatabaseMigrationTest.before.java.txt').write_text(old);(o/'MigrationInventory.before.java.txt').write_text(versions)
addition=r'''  @Test
  @Order(20)
  @DisplayName("PT-DB-NULL340-001 MUSIC key NULL and UTF-8 byte boundaries")
  void strictMusicKeyBoundaries() throws SQLException {
    withStrictNullableFixture(c -> {
      for (String role : List.of("M", "I")) {
        for (String key : List.of("null", "''", "repeat('x',257)", "repeat('あ',86)")) {
          strictCheck(c, "media_assets", "pair_role='" + role + "',pair_key=" + key,
              false, "ck_media_assets_pair");
        }
        for (String key : List.of("'x'", "repeat('x',256)", "repeat('あ',85)||'x'")) {
          strictCheck(c, "media_assets", "pair_role='" + role + "',pair_key=" + key,
              true, "ck_media_assets_pair");
        }
      }
    });
  }

  @Test
  @Order(21)
  @DisplayName("PT-DB-NULL340-002 MUSIC requires a known role")
  void strictMusicRoleIsRequired() throws SQLException {
    withStrictNullableFixture(c -> {
      for (String role : List.of("null", "'X'")) {
        strictCheck(c, "media_assets", "pair_role=" + role + ",pair_key=null",
            false, "ck_media_assets_pair");
      }
      for (String role : List.of("M", "I")) {
        strictCheck(c, "media_assets", "pair_role='" + role + "',pair_key='pair'",
            true, "ck_media_assets_pair");
      }
      strictCheck(c, "media_assets", "pair_role='N',pair_key=null", true, "ck_media_assets_pair");
    });
  }

  @Test
  @Order(22)
  @DisplayName("PT-DB-NULL340-003 VIDEO requires both pair fields NULL")
  void strictVideoPairIsAbsent() throws SQLException {
    withStrictNullableFixture(c -> {
      strictCheck(c, "media_assets", "media_type='VIDEO',pair_role=null,pair_key=null",
          true, "ck_media_assets_pair");
      for (String pair : List.of("pair_role='M',pair_key=null", "pair_role=null,pair_key='p'",
          "pair_role='M',pair_key='p'")) {
        strictCheck(c, "media_assets", "media_type='VIDEO'," + pair, false, "ck_media_assets_pair");
      }
    });
  }

  @Test
  @Order(23)
  @DisplayName("PT-DB-NULL340-004 MUSIC N has no pair key")
  void strictUnpairedMusicHasNoKey() throws SQLException {
    withStrictNullableFixture(c -> {
      strictCheck(c, "media_assets", "pair_role='N',pair_key=null", true, "ck_media_assets_pair");
      strictCheck(c, "media_assets", "pair_role='N',pair_key='p'", false, "ck_media_assets_pair");
    });
  }

  @Test
  @Order(24)
  @DisplayName("PT-DB-NULL340-005 revoked session requires timestamp and one of six reasons")
  void strictRevokedSessionFields() throws SQLException {
    withStrictNullableFixture(c -> {
      for (String reason : List.of("null", "'OTHER'")) {
        strictCheck(c, "auth_sessions", "revoked=true,revoked_at='" + FIXED_TIME
            + "',revoke_reason=" + reason, false, "ck_auth_sessions_revocation");
      }
      strictCheck(c, "auth_sessions", "revoked=true,revoked_at=null,revoke_reason='LOGOUT'",
          false, "ck_auth_sessions_revocation");
      for (String reason : List.of("LOGOUT", "DISABLED", "PASSWORD_RESET", "ADMIN", "EXPIRED", "REPLACED")) {
        strictCheck(c, "auth_sessions", "revoked=true,revoked_at='" + FIXED_TIME
            + "',revoke_reason='" + reason + "'", true, "ck_auth_sessions_revocation");
      }
    });
  }

  @Test
  @Order(25)
  @DisplayName("PT-DB-NULL340-006 active session has no revocation fields")
  void strictActiveSessionFields() throws SQLException {
    withStrictNullableFixture(c -> {
      strictCheck(c, "auth_sessions", "revoked=false,revoked_at=null,revoke_reason=null",
          true, "ck_auth_sessions_revocation");
      for (String fields : List.of("revoked_at='" + FIXED_TIME + "',revoke_reason=null",
          "revoked_at=null,revoke_reason='LOGOUT'", "revoked_at='" + FIXED_TIME + "',revoke_reason='LOGOUT'")) {
        strictCheck(c, "auth_sessions", "revoked=false," + fields, false, "ck_auth_sessions_revocation");
      }
    });
  }

  @Test
  @Order(26)
  @DisplayName("PT-DB-NULL340-007 ERROR notification requires both known code and message")
  void strictNotificationErrorFields() throws SQLException {
    withStrictNullableFixture(c -> {
      for (String fields : List.of("error_code=null,error_message='public error'",
          "error_code='PROCESS_FAILED',error_message=null", "error_code='OTHER',error_message='public error'")) {
        strictCheck(c, "notifications", "state='ERROR'," + fields, false, "ck_notifications_error");
      }
      for (String code : List.of("PROCESS_FAILED", "SYSTEM_UNAVAIL", "RESOURCE_LIMIT", "DATA_INTEGRITY", "PROTOCOL_ERROR")) {
        strictCheck(c, "notifications", "state='ERROR',error_code='" + code
            + "',error_message='public error'", true, "ck_notifications_error");
      }
    });
  }

  @Test
  @Order(27)
  @DisplayName("PT-DB-NULL340-008 non-ERROR notification has no error fields")
  void strictOtherNotificationFields() throws SQLException {
    withStrictNullableFixture(c -> {
      for (String state : List.of("RECEIVED", "PROCESSING", "COMPLETED", "CANCELLED")) {
        strictCheck(c, "notifications", "state='" + state + "',error_code=null,error_message=null",
            true, "ck_notifications_error");
        for (String fields : List.of("error_code='PROCESS_FAILED',error_message=null",
            "error_code=null,error_message='public error'", "error_code='PROCESS_FAILED',error_message='public error'")) {
          strictCheck(c, "notifications", "state='" + state + "'," + fields, false, "ck_notifications_error");
        }
      }
    });
  }

  @Test
  @Order(28)
  @DisplayName("PT-DB-NULL340-009 snapshot fields are both present or both absent")
  void strictSnapshotPair() throws SQLException {
    withStrictNullableFixture(c -> {
      strictCheck(c, "request_inbox", "response_body_encrypted=" + CIPHER + ",response_key_version=null",
          false, "ck_request_inbox_response_snapshot_pair");
      strictCheck(c, "request_inbox", "response_body_encrypted=null,response_key_version='key-1'",
          false, "ck_request_inbox_response_snapshot_pair");
      strictCheck(c, "request_inbox", "response_body_encrypted=null,response_key_version=null",
          true, "ck_request_inbox_response_snapshot_pair");
    });
  }

  @Test
  @Order(29)
  @DisplayName("PT-DB-NULL340-010 snapshot byte and key boundaries")
  void strictSnapshotBounds() throws SQLException {
    withStrictNullableFixture(c -> {
      for (int size : List.of(28, 29, 1050000, 1050001)) {
        strictCheck(c, "request_inbox", "response_body_encrypted=decode(repeat('00'," + size
            + "),'hex'),response_key_version='key-1'", size == 29 || size == 1050000,
            "ck_request_inbox_response_snapshot_pair");
      }
      for (String key : List.of("''", "'!invalid'", "repeat('x',17)")) {
        strictCheck(c, "request_inbox", "response_body_encrypted=" + CIPHER + ",response_key_version=" + key,
            false, "ck_request_inbox_response_snapshot_pair");
      }
    });
  }

  @Test
  @Order(30)
  @DisplayName("PT-DB-NULL340-011 N12 references require ID and forbid UUID")
  void strictNumericReferenceFields() throws SQLException {
    withStrictNullableFixture(c -> {
      for (String type : List.of("USER", "QUESTION", "JOB", "SCENARIO_FILE")) {
        for (String id : List.of("null", "0", "1000000000000")) {
          strictCheck(c, "request_inbox", "result_ref_type='" + type + "',result_ref_id=" + id
              + ",result_ref_uuid=null", false, "ck_request_inbox_result_reference");
        }
        strictCheck(c, "request_inbox", "result_ref_type='" + type
            + "',result_ref_id=1,result_ref_uuid='" + UUID_2 + "'", false, "ck_request_inbox_result_reference");
        for (long id : List.of(1L, 999999999999L)) {
          strictCheck(c, "request_inbox", "result_ref_type='" + type + "',result_ref_id=" + id
              + ",result_ref_uuid=null", true, "ck_request_inbox_result_reference");
        }
      }
    });
  }

  @Test
  @Order(31)
  @DisplayName("PT-DB-NULL340-012 AUTH_SESSION/NONE/PROCESSING reference shapes")
  void strictOtherReferenceFields() throws SQLException {
    withStrictNullableFixture(c -> {
      strictCheck(c, "request_inbox", "result_ref_type='AUTH_SESSION',result_ref_id=null,result_ref_uuid='"
          + UUID_2 + "'", true, "ck_request_inbox_result_reference");
      for (String fields : List.of("result_ref_type='AUTH_SESSION',result_ref_id=null,result_ref_uuid=null",
          "result_ref_type='AUTH_SESSION',result_ref_id=1,result_ref_uuid='" + UUID_2 + "'",
          "result_ref_type='NONE',result_ref_id=1,result_ref_uuid=null",
          "result_ref_type='NONE',result_ref_id=null,result_ref_uuid='" + UUID_2 + "'",
          "result_ref_type='OTHER',result_ref_id=null,result_ref_uuid=null")) {
        strictCheck(c, "request_inbox", fields, false, "ck_request_inbox_result_reference");
      }
      strictCheck(c, "request_inbox", "result_ref_type='NONE',result_ref_id=null,result_ref_uuid=null",
          true, "ck_request_inbox_result_reference");
      strictCheck(c, "request_inbox", "processing_state='PROCESSING',completed_at=null,result_ref_type=null,"
          + "result_ref_id=null,result_ref_uuid=null,response_layout_id=null,response_version=null,"
          + "response_body_encrypted=null,response_key_version=null", true, "ck_request_inbox_result_reference");
    });
  }

  @Test
  @Order(32)
  @DisplayName("PT-DB-NULL340-013 invalid V028 row aborts V029 and preserves all five old constraints")
  void strictUpgradeDoesNotRepairOrPartiallyReplaceLegacy() throws Exception {
    String database = "schubert_null340_legacy";
    run(pgBinary(FIXTURE_CREATEDB_AF6714D1), "-h", FIXTURE_127_0_0_1_88270499,
        "-p", Integer.toString(port), "-U", ADMIN, database);
    String url = FIXTURE_JDBC_POSTGRESQL_127_0_0_1_5FD48870 + port + "/" + database;
    executeResource(ADMIN, url, FIXTURE_DB_PROVISIONING_001_ROLES_SQL_71D5D411);
    execute(ADMIN, url, "create schema schubert_meta authorization nk_owner");
    Flyway old = Flyway.configure().configuration(
        configuredFlyway(url, false, FIXTURE_CLASSPATH_DB_MIGRATION_0053F0D8).getConfiguration())
        .target("028").load();
    assertEquals(28, old.migrate().migrationsExecuted);
    execute(ADMIN, url, strictMediaInsert().replace("'N',null", "'M',null"));
    String rowsSql = "select row_to_json(m)::text from schubert.media_assets m order by id";
    String checksSql = "select conname||':'||pg_get_constraintdef(oid) from pg_constraint where conname in "
        + "('ck_auth_sessions_revocation','ck_media_assets_pair','ck_notifications_error',"
        + "'ck_request_inbox_response_snapshot_pair','ck_request_inbox_result_reference') order by conname";
    String historySql = "select row_to_json(h)::text from schubert_meta.flyway_schema_history h"
        + " where success and version is not null order by installed_rank";
    List<String> rows = queryList(ADMIN, url, rowsSql);
    List<String> checks = queryList(ADMIN, url, checksSql);
    List<String> history = queryList(ADMIN, url, historySql);
    assertEquals(1, rows.size());
    assertEquals(5, checks.size());
    assertEquals(28, history.size());
    assertThrows(org.flywaydb.core.api.FlywayException.class,
        () -> configuredFlyway(url, false, FIXTURE_CLASSPATH_DB_MIGRATION_0053F0D8).migrate());
    assertEquals(rows, queryList(ADMIN, url, rowsSql));
    assertEquals(checks, queryList(ADMIN, url, checksSql));
    assertEquals(history, queryList(ADMIN, url, historySql));
    assertEquals(0L, queryLong(ADMIN, url,
        "select count(*) from schubert_meta.flyway_schema_history where version='029' and success"));
  }

  @Test
  @Order(33)
  @DisplayName("PT-DB-NULL340-014 V029 validates and all five checks remain validated")
  void strictMigrationIsAppliedValidatedAndIdempotent() throws SQLException {
    assertEquals(29, firstMigration.migrationsExecuted);
    assertTrue(flyway.validateWithResult().validationSuccessful);
    assertEquals(0, flyway.migrate().migrationsExecuted);
    assertEquals(29L, queryLong(ADMIN,
        "select count(*) from schubert_meta.flyway_schema_history where success and version is not null"));
    assertEquals(5L, queryLong(ADMIN, "select count(*) from pg_constraint where convalidated and conname in "
        + "('ck_auth_sessions_revocation','ck_media_assets_pair','ck_notifications_error',"
        + "'ck_request_inbox_response_snapshot_pair','ck_request_inbox_result_reference')"));
  }

  @Test
  @Order(34)
  @DisplayName("PT-DB-NULL340-015 QA050 unknown expiry remains optional")
  void strictMigrationPreservesUnknownRevocationExpiry() throws SQLException {
    try (Connection c = connection(ADMIN)) {
      c.setAutoCommit(false);
      execute(c, "insert into schubert_web_session.pending_context_revocations"
          + "(id,context_ciphertext,key_version,requested_at,next_attempt_at,expires_at) values('"
          + UUID_1 + "'," + CIPHER + ",'key-1','" + FIXED_TIME + "','" + FIXED_TIME + "',null)");
      assertEquals(1L, queryLong(c, "select count(*) from schubert_web_session.pending_context_revocations"
          + " where id='" + UUID_1 + "' and expires_at is null"));
      c.rollback();
    }
  }

  @FunctionalInterface
  private interface StrictNullableAction {
    void run(Connection connection) throws SQLException;
  }

  private static void withStrictNullableFixture(StrictNullableAction action) throws SQLException {
    try (Connection c = connection(ADMIN)) {
      c.setAutoCommit(false);
      execute(c, userInsert(10, "nullable-owner", 0));
      execute(c, questionInsert(10, false, "null", "null"));
      execute(c, jobInsert("RECEIVED", "null", "null", "null", "null", "null"));
      execute(c, strictMediaInsert());
      execute(c, "insert into schubert.auth_sessions(id,user_id,context_hash,context_ciphertext,key_version,"
          + "issued_at,last_accessed_at,expires_at,client_address,created_message_id) values('"
          + UUID_1 + "',10,'" + HASH + "'," + CIPHER + ",'key-1','" + FIXED_TIME + "','"
          + FIXED_TIME + "','2026-09-03 00:00:00+00','127.0.0.1','" + UUID_2 + "')");
      execute(c, "insert into schubert.notifications(id,job_id,question_id,owner_user_id,notification_type,"
          + "state,accepted_at,state_changed_at,created_at,updated_at) values(1,1,1,10,'ACCEPTED','RECEIVED','"
          + FIXED_TIME + "','" + FIXED_TIME + "','" + FIXED_TIME + "','" + FIXED_TIME + "')");
      execute(c, completedSnapshotInboxInsert(UUID_1, UUID_2, 29));
      action.run(c);
      c.rollback();
    }
  }

  private static String strictMediaInsert() {
    return "insert into schubert.media_assets(id,logical_id,media_type,title,category,storage_relative_path,"
        + "display_path,file_name,byte_size,sha256,mime_type,pair_role,pair_key,display_order,created_at) "
        + "values(1,'nullable-media','MUSIC','public title','public category','public/path','public/path',"
        + "'public.mp3',1,'" + HASH + "','audio/mpeg','N',null,1,'" + FIXED_TIME + "')";
  }

  private static void strictCheck(Connection c, String table, String fields, boolean accepted,
      String constraint) throws SQLException {
    Savepoint point = c.setSavepoint();
    try {
      String sql = "update schubert." + table + " set " + fields;
      if (accepted) {
        try (Statement statement = c.createStatement()) {
          assertEquals(1, statement.executeUpdate(sql));
        }
      } else {
        SQLException error = assertThrows(SQLException.class, () -> execute(c, sql));
        assertEquals("23514", error.getSQLState());
        assertTrue(error instanceof PSQLException);
        var details = ((PSQLException) error).getServerErrorMessage();
        assertNotNull(details);
        assertEquals(constraint, details.getConstraint());
      }
    } finally {
      c.rollback(point);
      c.releaseSavepoint(point);
    }
  }

'''
marker='  private static void writeQueryEvidence(Path path, String header, String sql) throws Exception {';assert old.count(marker)==1;new=old.replace(marker,addition+marker);assert new.replace(addition,'',1)==old
newv=versions.replace('"027", "028");','"027", "028", "029");');assert newv!=versions and newv.replace(', "029"','')==versions
assert len(re.findall(r'^  @Test$',new,re.M))==34
for i in range(1,16):assert new.count(f'PT-DB-NULL340-{i:03d}')==1
tp.write_text(new);vp.write_text(newv)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),productionCoreMain='5330eb303026206a87af466d0ffebb884b8e04b8',newSqlResource='src/schubert-nk-api/src/main/resources/db/migration/V029__strict_nullable_compound_checks.sql',oldTestDefinitions=19,newTestDefinitions=15,wholeCurrentTestDefinitions=34,oldWholeTestInverseEqual=True,versionListOld28PrefixPreserved=True,independentExpectedSource='SS331/354 SSC340 literal normal/null/boundary/SQLSTATE/constraint-name table, never production result',productTestsExecuted=0,coverage=None,dbTestState='HOLD_NOT_RUN_SOURCE_ONLY',actualDbMigrationVmRootRoleOperations=0,files={str(p.relative_to(r)):sha(p) for p in [tp,vp,r/'src/schubert-nk-api/src/main/resources/db/migration/V029__strict_nullable_compound_checks.sql']})
(o/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print('V029 five CHECKs and15 independent Testdefinitions created; whole34 NOT_RUN, old19 inverse equal')

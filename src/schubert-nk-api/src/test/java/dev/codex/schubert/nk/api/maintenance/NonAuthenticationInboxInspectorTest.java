package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.idempotency.EncryptedResponseSnapshot;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.InboxResultReferenceType;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * PT-DB-INBOX-041..048: independent UI TSV offsets, JCE envelope and literal SQL postconditions.
 */
final class NonAuthenticationInboxInspectorTest {
  private static final String FIXTURE_GAMRSP01_D6D22C8C = "GAMRSP01";
  private static final String FIXTURE_SCNRSP01_DD42C8D5 = "SCNRSP01";
  private static final String FIXTURE_ANMRSP01_94799936 = "ANMRSP01";
  private static final String FIXTURE_VIDRSP01_14BB97FD = "VIDRSP01";
  private static final String FIXTURE_UDTRSP01_F1EA7F6A = "UDTRSP01";
  private static final String FIXTURE_UCRRSP01_2349FE2E = "UCRRSP01";
  private static final String FIXTURE_USTRSP01_19F531B7 = "USTRSP01";
  private static final String FIXTURE_UPWRSP01_C630C0AA = "UPWRSP01";
  private static final String FIXTURE_ULKRSP01_6BA10E8D = "ULKRSP01";
  private static final String FIXTURE_0000_876EEFE0 = "0000";
  private static final String FIXTURE_0200_FC9DB3AC = "0200";
  private static final String FIXTURE_001_A3FEAA64 = "001";
  private static final String FIXTURE_REFERENCE_VALUE_415982AF = "reference_value";
  private static final String FIXTURE_FILE_RELATIVE_PATH_F33F0E71 = "File relative path";
  private static final String FIXTURE_READY_6630F9C3 = ".ready";
  private static final String FIXTURE_20260909090000123_0E28C2F5 = "20260909090000123";
  @TempDir static Path root;
  private static ApiLogDatabaseFixture db;
  private static final UUID MESSAGE = new UUID(0, 1);
  private static final UUID FILE = new UUID(0, 3);
  private static final Instant TIME = Instant.parse("2026-09-09T00:00:00.123Z");
  private static final List<String> LAYOUTS =
      List.of(
          FIXTURE_GAMRSP01_D6D22C8C,
          "SPKRSP01",
          "RTERSP01",
          "SCFRSP01",
          "SRCRSP01",
          FIXTURE_SCNRSP01_DD42C8D5,
          "AUDRSP01",
          FIXTURE_ANMRSP01_94799936,
          "ANLRSP01",
          FIXTURE_VIDRSP01_14BB97FD,
          "MCTRSP01",
          "MCSRSP01",
          "MTRRSP01",
          "MEDRSP01",
          "USRRSP01",
          FIXTURE_UDTRSP01_F1EA7F6A,
          "LGSRSP01",
          FIXTURE_UCRRSP01_2349FE2E,
          FIXTURE_USTRSP01_19F531B7,
          "URLRSP01",
          FIXTURE_UPWRSP01_C630C0AA,
          FIXTURE_ULKRSP01_6BA10E8D);
  private static final Set<String> MUTATIONS =
      Set.of(
          FIXTURE_UCRRSP01_2349FE2E,
          FIXTURE_USTRSP01_19F531B7,
          "URLRSP01",
          FIXTURE_UPWRSP01_C630C0AA,
          FIXTURE_ULKRSP01_6BA10E8D);
  private static final InboxResultReference USER =
      InboxResultReference.numeric(InboxResultReferenceType.USER, 9);
  private static final InboxResultReference SCRIPT =
      InboxResultReference.numeric(InboxResultReferenceType.SCENARIO_FILE, 11);

  @BeforeAll
  static void start() throws Exception {
    db = new ApiLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws SQLException {
    sql("delete from schubert.script_files");
    sql("delete from schubert.app_users");
    sql(
        "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at,version) values(9,'Target','target','synthetic-unused','USER','ACTIVE','2026-09-09','2026-09-09','2026-09-09',9)");
    sql(
        "insert into schubert.script_files(id,game_id,display_order,storage_relative_path,display_path,file_name,sha256,byte_size,created_at) values(11,1,1,'scenario/one.txt','one','one.txt',repeat('a',64),12,'2026-09-09'),(12,2,1,'scenario/two.txt','two','two.txt',repeat('a',64),12,'2026-09-09')");
  }

  @Test
  void querySuccessAndPersistentErrors() throws Exception {
    try (var f = new InboxResponseInspectorTest.Fixture();
        var c = db.api()) {
      c.setAutoCommit(false);
      var inspector = new NonAuthenticationInboxInspector(f.codec);
      for (String layout : LAYOUTS) {
        for (String code :
            List.of(
                FIXTURE_0000_876EEFE0,
                "0100",
                "0101",
                "0102",
                "0103",
                "0104",
                "0105",
                "0106",
                "0107",
                FIXTURE_0200_FC9DB3AC,
                "9000",
                "9001")) {
          boolean success = Set.of(FIXTURE_0000_876EEFE0, FIXTURE_0200_FC9DB3AC).contains(code);
          var ref = success && MUTATIONS.contains(layout) ? USER : InboxResultReference.none();
          var saved = saved(f, layout, code, ref, Map.of(), 0);
          assertTrue(
              f.inspector.isStructurallyValid(id(layout), saved), layout + "/" + code + " fixture");
          // Literal SS324 12.4 oracle, never a production predicate or enum-derived expectation.
          boolean expected =
              code.equals(FIXTURE_0000_876EEFE0)
                  || (code.equals(FIXTURE_0200_FC9DB3AC)
                      && layout.equals(FIXTURE_ULKRSP01_6BA10E8D))
                  || (code.equals("9001") && !layout.equals(FIXTURE_UDTRSP01_F1EA7F6A))
                  || (code.equals("0104")
                      && Set.of(
                              FIXTURE_UDTRSP01_F1EA7F6A,
                              FIXTURE_SCNRSP01_DD42C8D5,
                              "AUDRSP01",
                              FIXTURE_VIDRSP01_14BB97FD,
                              "MEDRSP01",
                              FIXTURE_USTRSP01_19F531B7,
                              "URLRSP01",
                              FIXTURE_UPWRSP01_C630C0AA,
                              FIXTURE_ULKRSP01_6BA10E8D)
                          .contains(layout))
                  || (code.equals("0105") && MUTATIONS.contains(layout))
                  || (code.equals("0100")
                      && Set.of(FIXTURE_UCRRSP01_2349FE2E, FIXTURE_UPWRSP01_C630C0AA)
                          .contains(layout));
          assertEquals(expected, inspector.isConsistent(c, id(layout), saved), layout + "/" + code);
          if (!success && expected) {
            assertFalse(inspector.isConsistent(c, id(layout), withReference(saved, USER)));
          }
          if (success && !MUTATIONS.contains(layout)) {
            assertFalse(inspector.isConsistent(c, id(layout), withReference(saved, USER)));
          }
        }
      }
    }
  }

  @Test
  void userMutationReferencesAndVersions() throws Exception {
    try (var f = new InboxResponseInspectorTest.Fixture();
        var c = db.api()) {
      c.setAutoCommit(false);
      var inspector = new NonAuthenticationInboxInspector(f.codec);
      for (String layout : MUTATIONS) {
        var saved = saved(f, layout, FIXTURE_0000_876EEFE0, USER, Map.of(), 0);
        assertTrue(inspector.isConsistent(c, id(layout), saved));
        for (var ref :
            List.of(
                InboxResultReference.none(),
                SCRIPT,
                InboxResultReference.numeric(InboxResultReferenceType.USER, 8))) {
          assertFalse(inspector.isConsistent(c, id(layout), withReference(saved, ref)));
        }
        assertFalse(
            check(
                f,
                c,
                layout,
                FIXTURE_0000_876EEFE0,
                USER,
                Map.of("更新後version", layout.equals(FIXTURE_UCRRSP01_2349FE2E) ? "1" : "0"),
                0));
      }
      assertTrue(
          check(
              f,
              c,
              FIXTURE_ULKRSP01_6BA10E8D,
              FIXTURE_0200_FC9DB3AC,
              USER,
              Map.of("更新後version", "0"),
              0));
      assertTrue(
          check(
              f,
              c,
              FIXTURE_USTRSP01_19F531B7,
              FIXTURE_0000_876EEFE0,
              USER,
              Map.of("更新後version", "9"),
              0));
      assertFalse(
          check(
              f,
              c,
              FIXTURE_USTRSP01_19F531B7,
              FIXTURE_0000_876EEFE0,
              USER,
              Map.of("更新後version", "10"),
              0));
      sql(
          "update schubert.app_users set role='ADMIN',status='DISABLED',username='Later',username_key='later',version=999999999 where id=9");
      assertTrue(
          check(
              f,
              c,
              FIXTURE_USTRSP01_19F531B7,
              FIXTURE_0000_876EEFE0,
              USER,
              Map.of("更新後version", "999999999"),
              0));
      assertTrue(check(f, c, FIXTURE_UCRRSP01_2349FE2E, FIXTURE_0000_876EEFE0, USER, Map.of(), 0));
      sql("delete from schubert.app_users where id=9");
      assertFalse(check(f, c, FIXTURE_UCRRSP01_2349FE2E, FIXTURE_0000_876EEFE0, USER, Map.of(), 0));
    }
  }

  @Test
  void scenarioInlineAndFileReferences() throws Exception {
    try (var f = new InboxResponseInspectorTest.Fixture();
        var c = db.api()) {
      c.setAutoCommit(false);
      assertTrue(
          check(
              f,
              c,
              FIXTURE_SCNRSP01_DD42C8D5,
              FIXTURE_0000_876EEFE0,
              InboxResultReference.none(),
              Map.of(),
              0));
      assertTrue(
          check(
              f,
              c,
              FIXTURE_SCNRSP01_DD42C8D5,
              FIXTURE_0000_876EEFE0,
              InboxResultReference.none(),
              Map.of(),
              1));
      assertFalse(
          check(f, c, FIXTURE_SCNRSP01_DD42C8D5, FIXTURE_0000_876EEFE0, SCRIPT, Map.of(), 1));
      var values = fileValues(1);
      assertTrue(check(f, c, FIXTURE_SCNRSP01_DD42C8D5, FIXTURE_0000_876EEFE0, SCRIPT, values, 0));
      for (var ref :
          List.of(
              USER,
              InboxResultReference.none(),
              InboxResultReference.numeric(InboxResultReferenceType.SCENARIO_FILE, 12))) {
        assertFalse(check(f, c, FIXTURE_SCNRSP01_DD42C8D5, FIXTURE_0000_876EEFE0, ref, values, 0));
      }
      values.put("Game code", "NUKITASHI2");
      assertFalse(check(f, c, FIXTURE_SCNRSP01_DD42C8D5, FIXTURE_0000_876EEFE0, SCRIPT, values, 0));
      values.put("Script file ID", "12");
      assertTrue(
          check(
              f,
              c,
              FIXTURE_SCNRSP01_DD42C8D5,
              FIXTURE_0000_876EEFE0,
              InboxResultReference.numeric(InboxResultReferenceType.SCENARIO_FILE, 12),
              values,
              0));
      sql("delete from schubert.script_files where id=11");
      assertFalse(
          check(f, c, FIXTURE_SCNRSP01_DD42C8D5, FIXTURE_0000_876EEFE0, SCRIPT, fileValues(1), 0));
    }
  }

  @Test
  void identityCryptoAndNullContracts() throws Exception {
    try (var f = new InboxResponseInspectorTest.Fixture();
        var c = db.api()) {
      c.setAutoCommit(false);
      var inspector = new NonAuthenticationInboxInspector(f.codec);
      var identity = id(FIXTURE_GAMRSP01_D6D22C8C);
      var saved =
          saved(
              f,
              FIXTURE_GAMRSP01_D6D22C8C,
              FIXTURE_0000_876EEFE0,
              InboxResultReference.none(),
              Map.of(),
              0);
      assertThrows(NullPointerException.class, () -> new NonAuthenticationInboxInspector(null));
      assertThrows(NullPointerException.class, () -> inspector.isConsistent(null, identity, saved));
      assertThrows(NullPointerException.class, () -> inspector.isConsistent(c, null, saved));
      assertThrows(NullPointerException.class, () -> inspector.isConsistent(c, identity, null));
      assertFalse(
          inspector.isConsistent(
              c,
              ResponseSnapshotIdentity.anonymous(
                  MESSAGE, FIXTURE_GAMRSP01_D6D22C8C, FIXTURE_001_A3FEAA64),
              saved));
      assertFalse(inspector.isConsistent(c, id("QSBRSP01"), saved));
      assertFalse(
          inspector.isConsistent(
              c,
              ResponseSnapshotIdentity.authenticated(
                  MESSAGE, FIXTURE_GAMRSP01_D6D22C8C, FIXTURE_001_A3FEAA64, 8),
              saved));
      assertFalse(
          inspector.isConsistent(
              c,
              identity,
              new InboxCompletion(
                  saved.state(),
                  saved.resultReference(),
                  FIXTURE_GAMRSP01_D6D22C8C,
                  FIXTURE_001_A3FEAA64,
                  Optional.empty(),
                  TIME)));
      byte[] damaged = saved.responseSnapshot().orElseThrow().ciphertext();
      damaged[damaged.length - 1] ^= 1;
      assertFalse(
          inspector.isConsistent(
              c,
              identity,
              new InboxCompletion(
                  saved.state(),
                  saved.resultReference(),
                  FIXTURE_GAMRSP01_D6D22C8C,
                  FIXTURE_001_A3FEAA64,
                  Optional.of(new EncryptedResponseSnapshot("v1", damaged)),
                  TIME)));
      Arrays.fill(damaged, (byte) 0);
      // Close between the first structure decrypt and the second read through a public JDBC port.
      Connection closing =
          (Connection)
              Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (p, method, args) -> {
                    if (method.getName().equals("getAutoCommit")) f.codec.close();
                    try {
                      return method.invoke(c, args);
                    } catch (InvocationTargetException failure) {
                      throw failure.getCause();
                    }
                  });
      assertFalse(inspector.isConsistent(closing, identity, saved));
      assertFalse(inspector.isConsistent(c, identity, saved));
    }
  }

  @Test
  void databaseFaultsAndNullRows() throws Exception {
    try (var f = new InboxResponseInspectorTest.Fixture();
        var c = db.api()) {
      var saved = saved(f, FIXTURE_USTRSP01_19F531B7, FIXTURE_0000_876EEFE0, USER, Map.of(), 0);
      var inspector = new NonAuthenticationInboxInspector(f.codec);
      assertFalse(inspector.isConsistent(c, id(FIXTURE_USTRSP01_19F531B7), saved));
      c.setAutoCommit(false);
      for (String fault :
          List.of(
              "getAutoCommit",
              "prepareStatement",
              "setLong",
              "executeQuery",
              "next",
              "getObject",
              "resultClose",
              "statementClose")) {
        var probe = new MaintenanceJdbcProbe();
        probe.selectedSql = FIXTURE_REFERENCE_VALUE_415982AF;
        probe.fault = fault;
        assertFalse(
            inspector.isConsistent(probe.wrap(c), id(FIXTURE_USTRSP01_19F531B7), saved), fault);
        assertEquals(0, probe.commits + probe.rollbacks + probe.closes);
      }
      for (Long value : Arrays.asList(null, -1L, 1_000_000_000L, 1L, 9L)) {
        var probe = new MaintenanceJdbcProbe();
        probe.selectedSql = FIXTURE_REFERENCE_VALUE_415982AF;
        probe.columns.put(FIXTURE_REFERENCE_VALUE_415982AF, value);
        assertEquals(
            value != null && (value == 1L || value == 9L),
            inspector.isConsistent(probe.wrap(c), id(FIXTURE_USTRSP01_19F531B7), saved));
      }
      var duplicate = new MaintenanceJdbcProbe();
      duplicate.selectedSql = FIXTURE_REFERENCE_VALUE_415982AF;
      duplicate.duplicate = true;
      assertFalse(inspector.isConsistent(duplicate.wrap(c), id(FIXTURE_USTRSP01_19F531B7), saved));
      var empty = new MaintenanceJdbcProbe();
      empty.selectedSql = FIXTURE_REFERENCE_VALUE_415982AF;
      empty.empty = true;
      assertFalse(inspector.isConsistent(empty.wrap(c), id(FIXTURE_USTRSP01_19F531B7), saved));
      var aborted = new MaintenanceJdbcProbe();
      aborted.selectedSql = FIXTURE_REFERENCE_VALUE_415982AF;
      aborted.fault = "aborted";
      assertFalse(inspector.isConsistent(aborted.wrap(c), id(FIXTURE_USTRSP01_19F531B7), saved));
      try (var s = c.createStatement()) {
        assertEquals(
            "25P02", assertThrows(SQLException.class, () -> s.execute("select 1")).getSQLState());
      }
      c.rollback();
    }
  }

  @Test
  void preservesTransactionAndBusinessState() throws Exception {
    try (var f = new InboxResponseInspectorTest.Fixture();
        var c = db.api()) {
      c.setAutoCommit(false);
      String before = state(c);
      var probe = new MaintenanceJdbcProbe();
      probe.selectedSql = FIXTURE_REFERENCE_VALUE_415982AF;
      Connection observed = probe.wrap(c);
      assertTrue(
          check(f, observed, FIXTURE_USTRSP01_19F531B7, FIXTURE_0000_876EEFE0, USER, Map.of(), 0));
      assertTrue(
          check(
              f,
              observed,
              FIXTURE_SCNRSP01_DD42C8D5,
              FIXTURE_0000_876EEFE0,
              SCRIPT,
              fileValues(1),
              0));
      assertEquals(before, state(c));
      assertFalse(c.isClosed());
      assertFalse(c.getAutoCommit());
      assertEquals(0, probe.commits + probe.rollbacks + probe.closes + probe.saves + probe.deletes);
      try (var s = c.createStatement()) {
        assertEquals(1, s.executeUpdate("update schubert.app_users set version=10 where id=9"));
      }
      c.rollback();
      assertEquals(before, state(c));
    }
  }

  @Test
  void concurrentInspectionsDoNotCross() throws Exception {
    try (var f = new InboxResponseInspectorTest.Fixture();
        var pool = Executors.newFixedThreadPool(8)) {
      var inspector = new NonAuthenticationInboxInspector(f.codec);
      var good = saved(f, FIXTURE_USTRSP01_19F531B7, FIXTURE_0000_876EEFE0, USER, Map.of(), 0);
      var bad = withReference(good, SCRIPT);
      var tasks = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 100; i++) {
        boolean expected = i % 2 == 0;
        tasks.add(
            () -> {
              try (var c = db.api()) {
                c.setAutoCommit(false);
                assertEquals(
                    expected,
                    inspector.isConsistent(
                        c, id(FIXTURE_USTRSP01_19F531B7), expected ? good : bad));
                assertFalse(c.isClosed());
              }
              return true;
            });
      }
      var results = pool.invokeAll(tasks);
      assertEquals(100, results.size());
      for (var result : results) assertTrue(result.get());
    }
  }

  @Test
  void boundaryDescriptorsAndFrozenSnapshots() throws Exception {
    try (var f = new InboxResponseInspectorTest.Fixture();
        var c = db.api()) {
      c.setAutoCommit(false);
      var malformedFlag =
          saved(
              f,
              FIXTURE_ANMRSP01_94799936,
              "9001",
              InboxResultReference.none(),
              Map.of("Opening有無", "0"),
              0);
      assertFalse(f.inspector.isStructurallyValid(id(FIXTURE_ANMRSP01_94799936), malformedFlag));
      assertFalse(
          new NonAuthenticationInboxInspector(f.codec)
              .isConsistent(c, id(FIXTURE_ANMRSP01_94799936), malformedFlag));
      assertTrue(
          check(
              f,
              c,
              FIXTURE_SCNRSP01_DD42C8D5,
              FIXTURE_0000_876EEFE0,
              SCRIPT,
              fileValues(10_000),
              0));
      for (var fault :
          List.of(
              Map.entry(
                  FIXTURE_FILE_RELATIVE_PATH_F33F0E71, "20260230/" + FILE + FIXTURE_READY_6630F9C3),
              Map.entry(
                  FIXTURE_FILE_RELATIVE_PATH_F33F0E71,
                  "20260909/" + new UUID(0, 4) + FIXTURE_READY_6630F9C3),
              Map.entry(FIXTURE_FILE_RELATIVE_PATH_F33F0E71, "../" + FILE + FIXTURE_READY_6630F9C3),
              Map.entry("File byte長", "4799"),
              Map.entry("File record長", "4799"),
              Map.entry("File record件数", "0"),
              Map.entry("File record件数", "10001"),
              Map.entry("File SHA-256", "B".repeat(64)))) {
        var values = fileValues(1);
        values.put(fault.getKey(), fault.getValue());
        assertFalse(
            check(f, c, FIXTURE_SCNRSP01_DD42C8D5, FIXTURE_0000_876EEFE0, SCRIPT, values, 0),
            fault.getKey());
      }
      var saved =
          saved(
              f,
              FIXTURE_UDTRSP01_F1EA7F6A,
              FIXTURE_0000_876EEFE0,
              InboxResultReference.none(),
              Map.of(),
              0);
      sql(
          "update schubert.app_users set username='Changed',username_key='changed',version=10,role='ADMIN',status='DISABLED' where id=9");
      var inspector = new NonAuthenticationInboxInspector(f.codec);
      for (int i = 0; i < 100; i++)
        assertTrue(inspector.isConsistent(c, id(FIXTURE_UDTRSP01_F1EA7F6A), saved));
      assertEquals(
          "InboxResultReference[type=NONE, value=<redacted>]", saved.resultReference().toString());
      // No .ready is created. Synthetic raw master hash 'a' differs from generated descriptor 'b'.
      assertTrue(
          check(f, c, FIXTURE_SCNRSP01_DD42C8D5, FIXTURE_0000_876EEFE0, SCRIPT, fileValues(1), 0));
    }
  }

  private static ResponseSnapshotIdentity id(String layout) {
    return ResponseSnapshotIdentity.authenticated(MESSAGE, layout, FIXTURE_001_A3FEAA64, 7);
  }

  private static InboxCompletion withReference(InboxCompletion saved, InboxResultReference ref) {
    return new InboxCompletion(
        saved.state(),
        ref,
        saved.responseLayoutId(),
        saved.responseVersion(),
        saved.responseSnapshot(),
        saved.completedAt());
  }

  private static boolean check(
      InboxResponseInspectorTest.Fixture f,
      Connection c,
      String layout,
      String code,
      InboxResultReference ref,
      Map<String, String> values,
      int count)
      throws Exception {
    return new NonAuthenticationInboxInspector(f.codec)
        .isConsistent(c, id(layout), saved(f, layout, code, ref, values, count));
  }

  private static InboxCompletion saved(
      InboxResponseInspectorTest.Fixture f,
      String layout,
      String code,
      InboxResultReference ref,
      Map<String, String> values,
      int count)
      throws Exception {
    byte[] wire = wire(layout, code, values, count);
    try {
      return withReference(
          f.saved(
              id(layout),
              wire,
              Set.of(FIXTURE_0000_876EEFE0, FIXTURE_0200_FC9DB3AC).contains(code)
                  ? InboxCompletionState.COMPLETED
                  : InboxCompletionState.ERROR,
              TIME),
          ref);
    } finally {
      Arrays.fill(wire, (byte) 0);
    }
  }

  static Map<String, String> fileValues(int count) {
    return new HashMap<>(
        Map.of(
            "Delivery mode",
            "F",
            "File ID",
            FILE.toString(),
            FIXTURE_FILE_RELATIVE_PATH_F33F0E71,
            "20260909/" + FILE + FIXTURE_READY_6630F9C3,
            "File byte長",
            Long.toString(4800L * count),
            "File SHA-256",
            "b".repeat(64),
            "File record長",
            "4800",
            "File record件数",
            Integer.toString(count)));
  }

  /** UI fixture, not production layout/codec. Explicit normal values; zero N/blank X for errors. */
  static byte[] wire(String layout, String code, Map<String, String> overrides, int count)
      throws Exception {
    // Shared independent test builder: no dependency on another test's BeforeAll ordering.
    Path fixtures =
        Path.of(System.getProperty("nk.pt.repository"))
            .resolve("src/schubert-nk-protocol/src/test/resources/protocol");
    var dimensions = tsv(fixtures.resolve("layouts-ui233.tsv"));
    var fields = tsv(fixtures.resolve("fields-ui234-236.tsv"));
    String[] dimension =
        dimensions.stream().filter(d -> d[0].equals(layout)).findFirst().orElseThrow();
    int dataSize = Integer.parseInt(dimension[3]);
    int recordSize = Integer.parseInt(dimension[4]);
    byte[] bytes = new byte[256 + dataSize + count * recordSize];
    Arrays.fill(bytes, (byte) ' ');
    put(bytes, 0, "SCHBNK01001" + layout + "001SS");
    put(bytes, 24, new UUID(0, 2).toString());
    put(bytes, 60, MESSAGE.toString());
    put(bytes, 96, FIXTURE_20260909090000123_0E28C2F5);
    byte[] context = new byte[32];
    new SecureRandom().nextBytes(context);
    put(bytes, 113, HexFormat.of().formatHex(context));
    Arrays.fill(context, (byte) 0);
    put(
        bytes,
        177,
        String.format(
            Locale.ROOT, "0256%06d%06d%06d%09d", dataSize, recordSize, count, bytes.length));
    put(bytes, 208, code);
    var data = new HashMap<String, String>();
    if (Set.of(FIXTURE_0000_876EEFE0, FIXTURE_0200_FC9DB3AC).contains(code)) {
      data.putAll(
          Map.of(
              "Effective page",
              "1",
              "Page size",
              layout.equals("USRRSP01") ? "50" : "100",
              "Total pages",
              "1",
              "Game code",
              "NUKITASHI1",
              "Route名",
              "Route",
              "Script file ID",
              "11",
              "Display title",
              "Title",
              "Display path",
              "scenario/one.txt",
              "Delivery mode",
              "I"));
      data.putAll(
          Map.of(
              "User ID",
              "9",
              "更新後version",
              layout.equals(FIXTURE_UCRRSP01_2349FE2E) ? "0" : "1",
              "Username",
              "Target",
              "Role",
              "USER",
              "State",
              "ACTIVE",
              "Password changed at",
              FIXTURE_20260909090000123_0E28C2F5,
              "Created at",
              FIXTURE_20260909090000123_0E28C2F5,
              "Updated at",
              FIXTURE_20260909090000123_0E28C2F5,
              "Created by",
              "SYSTEM",
              "Updated by",
              "SYSTEM"));
      String prefix =
          layout.equals("AUDRSP01")
              ? "scenario"
              : layout.equals(FIXTURE_VIDRSP01_14BB97FD) ? "video" : "music";
      String extension = layout.equals(FIXTURE_VIDRSP01_14BB97FD) ? "mp4" : "ogg";
      data.putAll(
          Map.of(
              "Media logical ID",
              "9",
              "Storage relative path",
              prefix + "/sample." + extension,
              "File name",
              "sample." + extension,
              "File byte長",
              "1",
              "SHA-256",
              "a".repeat(64),
              "MIME type",
              layout.equals(FIXTURE_VIDRSP01_14BB97FD) ? "video/mp4" : "audio/ogg",
              "Content disposition",
              "I",
              "Title",
              "Title",
              "Category",
              "MAIN"));
      if (layout.equals(FIXTURE_SCNRSP01_DD42C8D5)) data.put("File byte長", "0");
    }
    data.putAll(overrides);
    area(
        bytes,
        256,
        layout,
        "DATA",
        data,
        !Set.of(FIXTURE_0000_876EEFE0, FIXTURE_0200_FC9DB3AC).contains(code),
        fields);
    for (int i = 0; i < count; i++) {
      area(
          bytes,
          256 + dataSize + i * recordSize,
          layout,
          "RECORD",
          Map.of(
              "Entry ID",
              Integer.toString(i + 1),
              "Entry sequence",
              Integer.toString(i + 1),
              "Line番号",
              Integer.toString(i + 1),
              "Entry type",
              "narration",
              "本文",
              "Synthetic text"),
          false,
          fields);
    }
    return bytes;
  }

  private static void area(
      byte[] bytes,
      int base,
      String layout,
      String area,
      Map<String, String> values,
      boolean errorProfile,
      List<String[]> fields) {
    for (var field : fields) {
      if (!field[0].equals(layout) || !field[1].equals(area)) continue;
      int start = base + Integer.parseInt(field[3]) - 1;
      int length = Integer.parseInt(field[4]);
      String value = values.getOrDefault(field[2], "");
      boolean numeric = field[5].equals("N") || (field[5].equals("B") && !errorProfile);
      if (numeric) value = "0".repeat(length - value.length()) + value;
      assertTrue(value.getBytes(StandardCharsets.UTF_8).length <= length, field[2]);
      put(bytes, start, value);
    }
  }

  private static List<String[]> tsv(Path path) throws Exception {
    return Files.readAllLines(path).stream()
        .filter(s -> !s.startsWith("#") && !s.isBlank())
        .map(s -> s.split("\t", -1))
        .toList();
  }

  private static void put(byte[] bytes, int offset, String value) {
    byte[] input = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(input, 0, bytes, offset, input.length);
  }

  private static void sql(String sql) throws SQLException {
    try (var c = db.api();
        var s = c.createStatement()) {
      s.executeUpdate(sql);
    }
  }

  private static String state(Connection c) throws SQLException {
    try (var s = c.createStatement();
        var r =
            s.executeQuery(
                "select (select string_agg(row(id,username,role,status,version)::text,',' order by id) from schubert.app_users) || '/' || (select string_agg(row(id,game_id,sha256)::text,',' order by id) from schubert.script_files) as state")) {
      assertTrue(r.next());
      return r.getString("state");
    }
  }
}

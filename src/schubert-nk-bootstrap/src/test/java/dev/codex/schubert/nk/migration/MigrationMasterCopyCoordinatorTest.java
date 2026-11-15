package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.security.MessageDigest;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** PT-MIG-COORD001..020; fixed95SQL/six tuples and independent JDK digest, no actual DB/driver. */
final class MigrationMasterCopyCoordinatorTest {
  private static final String UNEXPECTED_COPY = "unexpected COPY";
  private static final String COPY_FAILURE = "synthetic COPY";
  private static final int PREPARE_SQL = 19;
  private static final int ALL_SQL = 95;
  private static final int TABLE_COUNT = 6;
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final String NORMAL_HASH =
      "744f7e0bd0a7dd16ab4454db3c0852c244101d25b22692de2cf167adb5dbdc90";
  private static final String EMPTY_HASH =
      "4444698baa3c905644477124201c2c291637b7c8441ed296c30acb231b1dcd90";
  private static final String BAD_INPUT = "migration copy coordinator input is invalid";
  private static final String BAD_STATE =
      "migration copy coordinator transaction or row count is invalid";
  private static final List<String> TABLES =
      List.of(
          "pg_temp.nk_mig_speakers",
          "pg_temp.nk_mig_script_files",
          "pg_temp.nk_mig_script_entries",
          "pg_temp.nk_mig_audio_files",
          "pg_temp.nk_mig_media_assets",
          "pg_temp.nk_mig_entry_audio_links");

  @Test
  void coord001FixedSixStagesSameTargetAndIndependentWireTuples() throws Exception {
    var f = MigrationMasterTargetPublisherTest.coordinatorFixture(false);
    var target = f.connection();
    var observed = new ArrayList<String>();
    var bytes = new ArrayList<String>();
    var result =
        new MigrationMasterCopyCoordinator()
            .transfer(
                target,
                mappings(),
                data(),
                (connection, table, rows) -> {
                  assertSame(target, connection);
                  assertEquals(PREPARE_SQL, f.sql.size());
                  assertEquals(TABLES.get(observed.size()), table);
                  var sink = new ByteArrayOutputStream();
                  new PostgresCopyTextWriter(new PostgresCopyTextEncoder()).writeRows(rows, sink);
                  byte[] wire = sink.toByteArray();
                  bytes.add(
                      table.substring("pg_temp.nk_mig_".length())
                          + "|"
                          + rows.size()
                          + "|"
                          + wire.length
                          + "|"
                          + HexFormat.of().formatHex(digest(wire)));
                  observed.add(table);
                  return rows.size();
                });
    assertEquals(TABLES, observed);
    assertEquals(MigrationMasterCopyFingerprintTest.NORMAL_METADATA, bytes);
    assertEquals(NORMAL_HASH, result.sha256());
    assertEquals(ALL_SQL, f.sql.size());
  }

  @Test
  void coord002EmptyCopiesAreExplicitAndFinalizeNormally() throws Exception {
    var f = MigrationMasterTargetPublisherTest.coordinatorFixture(true);
    var target = f.connection();
    var seen = new ArrayList<String>();
    var result =
        new MigrationMasterCopyCoordinator()
            .transfer(
                target,
                MigrationMasterCopyManifestTest.emptyMappings(),
                MigrationMasterCopyManifestTest.empty(),
                (connection, table, rows) -> {
                  assertSame(target, connection);
                  assertEquals(TABLES.get(seen.size()), table);
                  assertTrue(rows.isEmpty());
                  assertEquals(PREPARE_SQL, f.sql.size());
                  seen.add(table);
                  return 0;
                });
    assertEquals(TABLES, seen);
    assertEquals(EMPTY_HASH, result.sha256());
    assertEquals(ALL_SQL, f.sql.size());
  }

  @Test
  void coord003AllNullInputsRejectBeforeSql() throws Exception {
    for (int missing = 0; missing < 4; missing++) {
      var f = MigrationMasterTargetPublisherTest.coordinatorFixture(false);
      var target = f.connection();
      var mapping = mappings();
      var data = data();
      final int field = missing;
      var failure =
          assertThrows(
              IllegalArgumentException.class,
              () ->
                  new MigrationMasterCopyCoordinator()
                      .transfer(
                          field == 0 ? null : target,
                          field == 1 ? null : mapping,
                          field == 2 ? null : data,
                          field == 3
                              ? null
                              : (c, t, rows) -> {
                                throw new AssertionError(UNEXPECTED_COPY);
                              }));
      assertEquals(BAD_INPUT, failure.getMessage());
      assertNull(failure.getCause());
      assertTrue(f.sql.isEmpty());
    }
  }

  @Test
  void coord004AutoCommitRejectsBeforePrepare() throws Exception {
    var f = MigrationMasterTargetPublisherTest.coordinatorFixture(false);
    f.autoCommit = true;
    invalid(
        f,
        (c, t, rows) -> {
          throw new AssertionError(UNEXPECTED_COPY);
        });
    assertTrue(f.sql.isEmpty());
  }

  @Test
  void coord005ReadOnlyTargetRejectsBeforePrepare() throws Exception {
    var f = MigrationMasterTargetPublisherTest.coordinatorFixture(false);
    f.readOnly = true;
    invalid(
        f,
        (c, t, rows) -> {
          throw new AssertionError(UNEXPECTED_COPY);
        });
    assertTrue(f.sql.isEmpty());
  }

  @Test
  void coord006MetadataSqlFailurePropagatesBeforePrepare() throws Exception {
    for (boolean readOnly : List.of(false, true)) {
      var f = MigrationMasterTargetPublisherTest.coordinatorFixture(false);
      f.attributeFailure = new SQLException("synthetic attribute");
      f.failReadOnly = readOnly;
      assertSame(
          f.attributeFailure,
          assertThrows(
              SQLException.class,
              () ->
                  invoke(
                      f,
                      (c, t, rows) -> {
                        throw new AssertionError(UNEXPECTED_COPY);
                      })));
      assertTrue(f.sql.isEmpty());
    }
  }

  @Test
  void coord007MetadataRuntimeErrorNeverStartsPrepare() throws Exception {
    for (boolean readOnly : List.of(false, true))
      for (Throwable failure :
          List.of(
              new IllegalStateException("synthetic attribute"),
              new AssertionError("synthetic attribute"))) {
        var f = MigrationMasterTargetPublisherTest.coordinatorFixture(false);
        f.attributeFailure = failure;
        f.failReadOnly = readOnly;
        assertSame(
            failure,
            assertThrows(
                Throwable.class,
                () ->
                    invoke(
                        f,
                        (c, t, rows) -> {
                          throw new AssertionError(UNEXPECTED_COPY);
                        })));
        assertTrue(f.sql.isEmpty());
      }
  }

  @Test
  void coord008PrepareFaultsNeverInvokeCopy() throws Exception {
    for (int index = 0; index < PREPARE_SQL; index++)
      for (Throwable failure : failures()) {
        var f = MigrationMasterTargetPublisherTest.coordinatorFixture(false);
        f.badSql = index;
        f.failure = failure;
        assertSame(
            failure,
            assertThrows(
                Throwable.class,
                () ->
                    invoke(
                        f,
                        (c, t, rows) -> {
                          throw new AssertionError(UNEXPECTED_COPY);
                        })));
        assertEquals(index + 1, f.sql.size());
      }
  }

  @Test
  void coord009EveryCopySqlFailureStopsAfterOriginal() throws Exception {
    copyFault(new SQLException(COPY_FAILURE));
  }

  @Test
  void coord010EveryCopyIoFailureStopsAfterOriginal() throws Exception {
    copyFault(new IOException(COPY_FAILURE));
  }

  @Test
  void coord011EveryCopyRuntimeFailureStopsAfterOriginal() throws Exception {
    copyFault(new IllegalStateException(COPY_FAILURE));
  }

  @Test
  void coord012EveryCopyErrorStopsAfterOriginal() throws Exception {
    copyFault(new AssertionError(COPY_FAILURE));
  }

  @Test
  void coord013EveryCopyTooFewRowsRejects() throws Exception {
    badCount(0);
  }

  @Test
  void coord014EveryCopyTooManyRowsRejects() throws Exception {
    badCount(2);
  }

  @Test
  void coord015EveryCopyNegativeCountRejects() throws Exception {
    badCount(-1);
  }

  @Test
  void coord016EveryCopyHugeCountRejects() throws Exception {
    badCount(Long.MAX_VALUE);
  }

  @Test
  void coord017AllPassedRowsAndResultAreImmutable() throws Exception {
    var f = MigrationMasterTargetPublisherTest.coordinatorFixture(false);
    var result =
        invoke(
            f,
            (c, t, rows) -> {
              assertThrows(UnsupportedOperationException.class, () -> rows.clear());
              assertThrows(
                  UnsupportedOperationException.class, () -> rows.getFirst().set(0, "changed"));
              return rows.size();
            });
    byte[] first = result.canonicalBytes();
    first[0] = 0;
    assertEquals(NORMAL_HASH, result.sha256());
    assertEquals((byte) 'N', result.canonicalBytes()[0]);
    assertThrows(UnsupportedOperationException.class, () -> result.rowCounts().clear());
    var bad = MigrationMasterTargetPublisherTest.coordinatorFixture(false);
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MigrationMasterCopyCoordinator()
                .transfer(
                    bad.connection(),
                    MigrationMasterCopyManifestTest.emptyMappings(),
                    data(),
                    (c, t, rows) -> {
                      throw new AssertionError(UNEXPECTED_COPY);
                    }));
    assertTrue(bad.sql.isEmpty());
  }

  @Test
  void coord018PostCopyFaultsNeverRetryTransport() throws Exception {
    for (int index = PREPARE_SQL; index < ALL_SQL; index++)
      for (Throwable failure : failures()) {
        var f = MigrationMasterTargetPublisherTest.coordinatorFixture(false);
        f.badSql = index;
        f.failure = failure;
        var seen = new ArrayList<String>();
        assertSame(
            failure,
            assertThrows(
                Throwable.class,
                () ->
                    invoke(
                        f,
                        (c, t, rows) -> {
                          seen.add(t);
                          return rows.size();
                        })));
        assertEquals(TABLES, seen);
        assertEquals(index + 1, f.sql.size());
      }
  }

  @Test
  void coord019RepeatedCallsOwnFreshResourcesAndRedactedState() throws Exception {
    var job = new MigrationMasterCopyCoordinator();
    assertEquals("MigrationMasterCopyCoordinator[REDACTED]", job.toString());
    for (int index = 0; index < 2; index++) {
      var f = MigrationMasterTargetPublisherTest.coordinatorFixture(false);
      var seen = new ArrayList<String>();
      var result =
          job.transfer(
              f.connection(),
              mappings(),
              data(),
              (c, t, rows) -> {
                seen.add(t);
                return rows.size();
              });
      assertEquals(TABLES, seen);
      assertEquals(NORMAL_HASH, result.sha256());
      assertEquals(ALL_SQL, f.sql.size());
    }
  }

  @Test
  void coord020FiniteParallelIndependentTargetAndCopyScopes() throws Exception {
    var job = new MigrationMasterCopyCoordinator();
    var mapping = mappings();
    var declared = data();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<Void>>();
      for (int index = 0; index < TASKS; index++)
        futures.add(
            executor.submit(
                () -> {
                  var f = MigrationMasterTargetPublisherTest.coordinatorFixture(false);
                  var target = f.connection();
                  var seen = new ArrayList<String>();
                  var result =
                      job.transfer(
                          target,
                          mapping,
                          declared,
                          (c, t, rows) -> {
                            assertSame(target, c);
                            assertEquals(PREPARE_SQL, f.sql.size());
                            seen.add(t);
                            return rows.size();
                          });
                  assertEquals(TABLES, seen);
                  assertEquals(NORMAL_HASH, result.sha256());
                  assertEquals(ALL_SQL, f.sql.size());
                  return null;
                }));
      for (var future : futures) assertNull(future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static byte[] digest(byte[] bytes) {
    try {
      return MessageDigest.getInstance("SHA-256").digest(bytes);
    } catch (java.security.NoSuchAlgorithmException failure) {
      throw new AssertionError(failure);
    }
  }

  private static List<Throwable> failures() {
    return List.of(
        new SQLException("synthetic target"),
        new IllegalStateException("synthetic target"),
        new AssertionError("synthetic target"));
  }

  private static CurrentMigrationMappingManifest mappings() throws Exception {
    return MigrationMasterCopyManifestTest.mappings(-1, -2);
  }

  private static MigrationMasterCopyDataset data() throws Exception {
    return MigrationMasterTargetPublisherTest.normal();
  }

  private static MigrationMasterCopyManifest invoke(
      MigrationMasterTargetPublisherTest.Fixture f, MigrationCopyPort copy) throws Exception {
    return new MigrationMasterCopyCoordinator().transfer(f.connection(), mappings(), data(), copy);
  }

  private static void invalid(MigrationMasterTargetPublisherTest.Fixture f, MigrationCopyPort copy)
      throws Exception {
    var failure = assertThrows(SQLException.class, () -> invoke(f, copy));
    assertEquals(BAD_STATE, failure.getMessage());
    assertNull(failure.getCause());
  }

  private static void badCount(long count) throws Exception {
    for (int bad = 0; bad < TABLE_COUNT; bad++) {
      final int selected = bad;
      var f = MigrationMasterTargetPublisherTest.coordinatorFixture(false);
      var seen = new ArrayList<String>();
      invalid(
          f,
          (c, t, rows) -> {
            int index = seen.size();
            seen.add(t);
            return index == selected ? count : rows.size();
          });
      assertEquals(TABLES.subList(0, bad + 1), seen);
      assertEquals(PREPARE_SQL, f.sql.size());
    }
  }

  private static void copyFault(Throwable failure) throws Exception {
    for (int bad = 0; bad < TABLE_COUNT; bad++) {
      final int selected = bad;
      var f = MigrationMasterTargetPublisherTest.coordinatorFixture(false);
      var seen = new ArrayList<String>();
      assertSame(
          failure,
          assertThrows(
              Throwable.class,
              () ->
                  invoke(
                      f,
                      (c, t, rows) -> {
                        int index = seen.size();
                        seen.add(t);
                        if (index == selected) {
                          if (failure instanceof SQLException sql) throw sql;
                          if (failure instanceof IOException io) throw io;
                          if (failure instanceof Error error) throw error;
                          throw (RuntimeException) failure;
                        }
                        return rows.size();
                      })));
      assertEquals(TABLES.subList(0, bad + 1), seen);
      assertEquals(PREPARE_SQL, f.sql.size());
    }
  }
}

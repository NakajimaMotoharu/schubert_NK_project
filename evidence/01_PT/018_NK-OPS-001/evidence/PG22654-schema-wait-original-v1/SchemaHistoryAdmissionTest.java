package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.bootstrap.SchemaHistoryAdmission;
import dev.codex.schubert.nk.api.bootstrap.SchemaHistoryAdmission.Row;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;

/** SSC095/PG312/PT-OPS-SCHEMA001..008. Literal six-column oracle, no observed DB expected. */
final class SchemaHistoryAdmissionTest {
  private static final String FIXTURE_SCHEMA_E38F1889 = "SCHEMA";
  private static final String FIXTURE_001_A3FEAA64 = "001";
  private static final String FIXTURE_SQL_5B7E398D = "SQL";
  private static final String FIXTURE_V001_FIRST_SQL_F20888AE = "V001__first.sql";
  private static final String FIXTURE_SCRIPT_5BBD8BBB = "script";
  private static final String FIXTURE_CHECKSUM_CCB2C25E = "checksum";
  private static final String FIXTURE_INSTALLED_RANK_C438B369 = "installed_rank";
  private static final String FIXTURE_VERSION_43CCC4D0 = "version";
  private static final String FIXTURE_SUCCESS_68E7A699 = "success";
  private static final String FIXTURE_V001_A_SQL_CE2324F5 = "V001__a.sql";
  private static final String FIXTURE_NULLSTATEMENT_5A17BE38 = "nullStatement";
  private static final String FIXTURE_PREPARESTATEMENT_CB987D1F = "prepareStatement";
  private static final String FIXTURE_NEXT_CA1733B5 = "next";
  private static final String FIXTURE_ROWCLOSE_4440E762 = "rowClose";
  private static final String FIXTURE_STATEMENTCLOSE_D5A13A63 = "statementClose";
  private static final String FIXTURE_PRIVATE_D45CA6F9 = "PRIVATE";
  private static final Row SCHEMA =
      new Row(0, null, FIXTURE_SCHEMA_E38F1889, "\"schubert_meta\"", null, true);
  private static final Row FIRST =
      new Row(
          1,
          FIXTURE_001_A3FEAA64,
          FIXTURE_SQL_5B7E398D,
          FIXTURE_V001_FIRST_SQL_F20888AE,
          -170000001,
          true);
  private static final List<Row> RELEASE = List.of(SCHEMA, FIRST);

  @Test
  void opsSchema009ActualRowsAreIndependentlyReadAndImmutableAfterBothOwnersClose()
      throws Exception {
    var probe = new Probe();
    var observed = new SchemaHistoryAdmission(RELEASE).inspect(probe.connection());
    assertEquals(
        List.of(
            new Row(0, null, FIXTURE_SCHEMA_E38F1889, "\"schubert_meta\"", null, true),
            new Row(
                1,
                FIXTURE_001_A3FEAA64,
                FIXTURE_SQL_5B7E398D,
                FIXTURE_V001_FIRST_SQL_F20888AE,
                -170000001,
                true)),
        observed);
    assertNotSame(SCHEMA, observed.getFirst());
    assertNotSame(FIRST, observed.getLast());
    assertArrayEquals(new int[] {1, 1, 0}, probe.closed);
    assertThrows(UnsupportedOperationException.class, observed::clear);
    probe.rows.getLast().put(FIXTURE_SCRIPT_5BBD8BBB, "V002__changed.sql");
    assertEquals(2, observed.size());
    assertEquals(FIXTURE_V001_FIRST_SQL_F20888AE, observed.getLast().script());
    assertThrows(
        NullPointerException.class, () -> new SchemaHistoryAdmission(RELEASE).inspect(null));
    var wrong = new Probe();
    wrong.rows.getLast().put(FIXTURE_CHECKSUM_CCB2C25E, 42);
    failed(() -> new SchemaHistoryAdmission(RELEASE).inspect(wrong.connection()));
    assertArrayEquals(new int[] {1, 1, 0}, wrong.closed);
  }

  @Test
  void opsSchema001ExactFixedQueryAndBorrowedOwner() throws Exception {
    var probe = new Probe();
    new SchemaHistoryAdmission(RELEASE).verify(probe.connection());
    assertEquals(
        "select installed_rank,version,type,script,checksum,success from schubert_meta.startup_schema_history() order by installed_rank",
        probe.sql);
    assertEquals(5, probe.timeout);
    assertArrayEquals(new int[] {1, 1, 0}, probe.closed);
    new SchemaHistoryAdmission(List.of(SCHEMA)).verify(new Probe(List.of(schema())).connection());
  }

  @Test
  void opsSchema002EveryColumnMissingExtraAndFailedRow() {
    for (String column :
        List.of(
            FIXTURE_INSTALLED_RANK_C438B369,
            FIXTURE_VERSION_43CCC4D0,
            "type",
            FIXTURE_SCRIPT_5BBD8BBB,
            FIXTURE_CHECKSUM_CCB2C25E,
            FIXTURE_SUCCESS_68E7A699)) {
      for (Object wrong :
          Arrays.asList(
              null,
              switch (column) {
                case FIXTURE_INSTALLED_RANK_C438B369 -> 2;
                case FIXTURE_CHECKSUM_CCB2C25E -> 42;
                case FIXTURE_SUCCESS_68E7A699 -> false;
                default -> "UNKNOWN";
              })) {
        var probe = new Probe();
        probe.rows.get(1).put(column, wrong);
        failed(() -> new SchemaHistoryAdmission(RELEASE).verify(probe.connection()));
        assertArrayEquals(new int[] {1, 1, 0}, probe.closed);
      }
    }
    for (String column : List.of(FIXTURE_VERSION_43CCC4D0, FIXTURE_CHECKSUM_CCB2C25E)) {
      var probe = new Probe();
      probe
          .rows
          .getFirst()
          .put(column, column.equals(FIXTURE_VERSION_43CCC4D0) ? FIXTURE_001_A3FEAA64 : 42);
      failed(() -> new SchemaHistoryAdmission(RELEASE).verify(probe.connection()));
    }
    for (List<Map<String, Object>> rows :
        List.of(
            List.<Map<String, Object>>of(),
            List.of(schema()),
            List.of(first(), schema()),
            List.of(schema(), first(), first()))) {
      var probe = new Probe(rows);
      failed(() -> new SchemaHistoryAdmission(RELEASE).verify(probe.connection()));
    }
  }

  @Test
  void opsSchema003ExpectedRowInvariantBoundaries() {
    assertThrows(NullPointerException.class, () -> new Row(0, null, null, "x", null, true));
    assertThrows(
        NullPointerException.class,
        () -> new Row(0, null, FIXTURE_SCHEMA_E38F1889, null, null, true));
    assertThrows(
        IllegalArgumentException.class,
        () -> new Row(0, null, FIXTURE_SCHEMA_E38F1889, "\"schubert_meta\"", null, false));
    assertThrows(
        IllegalArgumentException.class, () -> new Row(0, null, "UNKNOWN", "x", null, true));
    for (RowInput input :
        List.of(
            new RowInput(1, null, null, "\"schubert_meta\""),
            new RowInput(0, FIXTURE_001_A3FEAA64, null, "\"schubert_meta\""),
            new RowInput(0, null, 1, "\"schubert_meta\""),
            new RowInput(0, null, null, "schubert_meta")))
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new Row(
                  input.rank,
                  input.version,
                  FIXTURE_SCHEMA_E38F1889,
                  input.script,
                  input.checksum,
                  true));
    for (RowInput input :
        List.of(
            new RowInput(0, FIXTURE_001_A3FEAA64, 1, FIXTURE_V001_A_SQL_CE2324F5),
            new RowInput(1000, FIXTURE_001_A3FEAA64, 1, FIXTURE_V001_A_SQL_CE2324F5),
            new RowInput(1, null, 1, FIXTURE_V001_A_SQL_CE2324F5),
            new RowInput(1, "000", 1, "V000__a.sql"),
            new RowInput(1, "1", 1, "V1__a.sql"),
            new RowInput(1, FIXTURE_001_A3FEAA64, null, FIXTURE_V001_A_SQL_CE2324F5),
            new RowInput(1, FIXTURE_001_A3FEAA64, 1, "V002__a.sql"),
            new RowInput(1, FIXTURE_001_A3FEAA64, 1, "V001__A.sql")))
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new Row(
                  input.rank,
                  input.version,
                  FIXTURE_SQL_5B7E398D,
                  input.script,
                  input.checksum,
                  true));
    assertEquals(
        999,
        new Row(
                999,
                "999",
                FIXTURE_SQL_5B7E398D,
                "V999__" + "a".repeat(200) + ".sql",
                Integer.MIN_VALUE,
                true)
            .installedRank());
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new Row(
                1,
                FIXTURE_001_A3FEAA64,
                FIXTURE_SQL_5B7E398D,
                "V001__" + "a".repeat(201) + ".sql",
                1,
                true));
  }

  @Test
  void opsSchema004ExpectedProfileOrderingAndDefensiveCopy() throws Exception {
    assertThrows(NullPointerException.class, () -> new SchemaHistoryAdmission(null));
    assertThrows(
        NullPointerException.class, () -> new SchemaHistoryAdmission(Arrays.asList(SCHEMA, null)));
    for (List<Row> invalid :
        List.of(
            List.<Row>of(),
            Collections.nCopies(1001, SCHEMA),
            List.of(FIRST),
            List.of(SCHEMA, SCHEMA),
            List.of(
                SCHEMA,
                FIRST,
                new Row(
                    2,
                    FIXTURE_001_A3FEAA64,
                    FIXTURE_SQL_5B7E398D,
                    FIXTURE_V001_FIRST_SQL_F20888AE,
                    1,
                    true))))
      assertThrows(IllegalArgumentException.class, () -> new SchemaHistoryAdmission(invalid));
    var mutable = new ArrayList<>(RELEASE);
    var admission = new SchemaHistoryAdmission(mutable);
    mutable.clear();
    admission.verify(new Probe().connection());
    var maximal = new ArrayList<Row>();
    maximal.add(SCHEMA);
    for (int i = 1; i <= 999; i++) {
      String version = String.format(Locale.ROOT, "%03d", i);
      maximal.add(new Row(i, version, FIXTURE_SQL_5B7E398D, "V" + version + "__a.sql", 1, true));
    }
    new SchemaHistoryAdmission(maximal);
    assertThrows(NullPointerException.class, () -> admission.verify(null));
  }

  @Test
  void opsSchema005NullProviderSqlExceptionsAndAllOwnership() {
    for (String kind :
        List.of(
            FIXTURE_NULLSTATEMENT_5A17BE38,
            "nullRows",
            FIXTURE_PREPARESTATEMENT_CB987D1F,
            "setQueryTimeout",
            "executeQuery",
            FIXTURE_NEXT_CA1733B5,
            "getObject",
            "getString",
            FIXTURE_ROWCLOSE_4440E762,
            FIXTURE_STATEMENTCLOSE_D5A13A63)) {
      var probe = new Probe();
      probe.nullStatement = kind.equals(FIXTURE_NULLSTATEMENT_5A17BE38);
      probe.nullRows = kind.equals("nullRows");
      if (!kind.startsWith("null"))
        probe.faults.put(kind, new SQLException(FIXTURE_PRIVATE_D45CA6F9, "P0001"));
      failed(() -> new SchemaHistoryAdmission(RELEASE).verify(probe.connection()));
      assertEquals(0, probe.closed[2]);
      assertEquals(
          kind.equals(FIXTURE_NULLSTATEMENT_5A17BE38)
                  || kind.equals(FIXTURE_PREPARESTATEMENT_CB987D1F)
              ? 0
              : 1,
          probe.closed[1]);
      assertEquals(
          List.of(
                      FIXTURE_NULLSTATEMENT_5A17BE38,
                      "nullRows",
                      FIXTURE_PREPARESTATEMENT_CB987D1F,
                      "setQueryTimeout",
                      "executeQuery")
                  .contains(kind)
              ? 0
              : 1,
          probe.closed[0]);
    }
  }

  @Test
  void opsSchema006KnownUnknownCloseMatrixAndSameThrowable() {
    for (int body = 0; body < 4; body++)
      for (int row = 0; row < 4; row++)
        for (int statement = 0; statement < 4; statement++) {
          var probe = new Probe();
          Throwable primary = fault(body);
          Throwable rowFault = fault(row);
          Throwable statementFault = fault(statement);
          if (primary != null) probe.faults.put(FIXTURE_NEXT_CA1733B5, primary);
          if (rowFault != null) probe.faults.put(FIXTURE_ROWCLOSE_4440E762, rowFault);
          if (statementFault != null)
            probe.faults.put(FIXTURE_STATEMENTCLOSE_D5A13A63, statementFault);
          Throwable expected =
              independentWinner(independentWinner(primary, rowFault), statementFault);
          var admission = new SchemaHistoryAdmission(RELEASE);
          if (expected == null) assertDoesNotThrow(() -> admission.verify(probe.connection()));
          else if (expected instanceof SQLException)
            failed(() -> admission.verify(probe.connection()));
          else {
            Throwable actual =
                assertThrows(expected.getClass(), () -> admission.verify(probe.connection()));
            assertSame(expected, actual);
            for (Throwable suppressed : actual.getSuppressed()) {
              assertEquals("database admission resource failure", suppressed.getMessage());
              assertNull(suppressed.getCause());
            }
          }
          assertArrayEquals(new int[] {1, 1, 0}, probe.closed);
        }
    var probe = new Probe();
    var same = new IllegalStateException(FIXTURE_PRIVATE_D45CA6F9);
    probe.faults.put(FIXTURE_NEXT_CA1733B5, same);
    probe.faults.put(FIXTURE_ROWCLOSE_4440E762, same);
    probe.faults.put(FIXTURE_STATEMENTCLOSE_D5A13A63, same);
    assertSame(
        same,
        assertThrows(
            IllegalStateException.class,
            () -> new SchemaHistoryAdmission(RELEASE).verify(probe.connection())));
    assertEquals(2, same.getSuppressed().length);
    assertArrayEquals(new int[] {1, 1, 0}, probe.closed);
  }

  @Test
  void opsSchema007InterruptBeforeAndAfterNeverAccepts() {
    var early = new Probe();
    Thread.currentThread().interrupt();
    try {
      failed(() -> new SchemaHistoryAdmission(RELEASE).verify(early.connection()));
      assertTrue(Thread.currentThread().isInterrupted());
      assertArrayEquals(new int[3], early.closed);
    } finally {
      Thread.interrupted();
    }
    var late = new Probe();
    late.interruptAtEnd = true;
    try {
      failed(() -> new SchemaHistoryAdmission(RELEASE).verify(late.connection()));
      assertTrue(Thread.currentThread().isInterrupted());
      assertArrayEquals(new int[] {1, 1, 0}, late.closed);
    } finally {
      Thread.interrupted();
    }
  }

  @Test
  void opsSchema008IndependentConcurrentOwners() throws Exception {
    var admission = new SchemaHistoryAdmission(RELEASE);
    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      var barrier = new java.util.concurrent.CyclicBarrier(8);
      var tasks = new ArrayList<java.util.concurrent.Future<int[]>>();
      for (int i = 0; i < 8; i++)
        tasks.add(
            executor.submit(
                () -> {
                  var probe = new Probe();
                  barrier.await();
                  admission.verify(probe.connection());
                  return probe.closed;
                }));
      for (var task : tasks) assertArrayEquals(new int[] {1, 1, 0}, task.get());
    }
  }

  private record RowInput(int rank, String version, Integer checksum, String script) {}

  private static Throwable fault(int kind) {
    return switch (kind) {
      case 0 -> null;
      case 1 -> new SQLException(FIXTURE_PRIVATE_D45CA6F9);
      case 2 -> new IllegalStateException(FIXTURE_PRIVATE_D45CA6F9);
      case 3 -> new AssertionError(FIXTURE_PRIVATE_D45CA6F9);
      default -> throw new AssertionError();
    };
  }

  // Independent specification matrix, deliberately does not call the production close helper.
  private static Throwable independentWinner(Throwable body, Throwable close) {
    if (close == null) return body;
    if (body == null) return close;
    if (body instanceof SQLException && !(close instanceof SQLException)) return close;
    return body;
  }

  private static void failed(org.junit.jupiter.api.function.Executable action) {
    SQLException e = assertThrows(SQLException.class, action);
    assertEquals("08001", e.getSQLState());
    assertEquals("schema history unavailable", e.getMessage());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
  }

  private static Map<String, Object> schema() {
    var row = new HashMap<String, Object>();
    row.put(FIXTURE_INSTALLED_RANK_C438B369, 0);
    row.put(FIXTURE_VERSION_43CCC4D0, null);
    row.put("type", FIXTURE_SCHEMA_E38F1889);
    row.put(FIXTURE_SCRIPT_5BBD8BBB, "\"schubert_meta\"");
    row.put(FIXTURE_CHECKSUM_CCB2C25E, null);
    row.put(FIXTURE_SUCCESS_68E7A699, true);
    return row;
  }

  private static Map<String, Object> first() {
    return new HashMap<>(
        Map.of(
            FIXTURE_INSTALLED_RANK_C438B369,
            1,
            FIXTURE_VERSION_43CCC4D0,
            FIXTURE_001_A3FEAA64,
            "type",
            FIXTURE_SQL_5B7E398D,
            FIXTURE_SCRIPT_5BBD8BBB,
            FIXTURE_V001_FIRST_SQL_F20888AE,
            FIXTURE_CHECKSUM_CCB2C25E,
            -170000001,
            FIXTURE_SUCCESS_68E7A699,
            true));
  }

  private static final class Probe {
    final List<Map<String, Object>> rows;
    final Map<String, Throwable> faults = new HashMap<>();
    final int[] closed = new int[3];
    boolean nullStatement;
    boolean nullRows;
    boolean interruptAtEnd;
    int index = -1;
    int timeout;
    String sql;

    Probe() {
      this(List.of(schema(), first()));
    }

    Probe(List<Map<String, Object>> rows) {
      this.rows = rows;
    }

    Connection connection() {
      ResultSet values =
          proxy(
              ResultSet.class,
              (p, m, args) -> {
                String name = m.getName();
                if (name.equals("close")) {
                  closed[0]++;
                  throwIf(FIXTURE_ROWCLOSE_4440E762);
                  return null;
                }
                throwIf(name);
                return switch (name) {
                  case FIXTURE_NEXT_CA1733B5 -> {
                    boolean next = ++index < rows.size();
                    if (!next && interruptAtEnd) Thread.currentThread().interrupt();
                    yield next;
                  }
                  case "getObject", "getString" -> rows.get(index).get((String) args[0]);
                  default -> throw new AssertionError(name);
                };
              });
      PreparedStatement statement =
          proxy(
              PreparedStatement.class,
              (p, m, args) -> {
                String name = m.getName();
                if (name.equals("close")) {
                  closed[1]++;
                  throwIf(FIXTURE_STATEMENTCLOSE_D5A13A63);
                  return null;
                }
                throwIf(name);
                return switch (name) {
                  case "setQueryTimeout" -> {
                    timeout = (Integer) args[0];
                    yield null;
                  }
                  case "executeQuery" -> nullRows ? null : values;
                  default -> throw new AssertionError(name);
                };
              });
      return proxy(
          Connection.class,
          (p, m, args) -> {
            String name = m.getName();
            throwIf(name);
            return switch (name) {
              case FIXTURE_PREPARESTATEMENT_CB987D1F -> {
                sql = (String) args[0];
                yield nullStatement ? null : statement;
              }
              case "close" -> {
                closed[2]++;
                yield null;
              }
              default -> throw new AssertionError(name);
            };
          });
    }

    private void throwIf(String method) throws Throwable {
      Throwable fault = faults.get(method);
      if (fault != null) throw fault;
    }

    private static <T> T proxy(Class<T> type, java.lang.reflect.InvocationHandler handler) {
      return type.cast(
          Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
    }
  }
}

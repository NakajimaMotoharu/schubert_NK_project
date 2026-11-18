package dev.codex.schubert.nk.api.bootstrap;

import java.sql.Connection;
import java.sql.SQLException;
import java.sql.SQLNonTransientConnectionException;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Fixed six-column startup projection, not generic Flyway validation or trust in caller values.
 * Assembly must bind expected rows to the independently approved, fully verified release BOM and
 * admit the fixed role/DB connection first. Borrowed connection is never configured/closed here.
 * NK-OPS-001/NK-DAT-001/DAT009/SYS002/UI212/253/SS3313.3/3439.1/SSC095/PG312;
 * PT-OPS-SCHEMA001..008. No migration credentials or table SELECT fallback.
 */
@NullMarked
public final class SchemaHistoryAdmission {
  public record Row(
      int installedRank,
      @Nullable String version,
      String type,
      String script,
      @Nullable Integer checksum,
      boolean success) {
    public Row {
      Objects.requireNonNull(type, "migration type");
      Objects.requireNonNull(script, "migration script");
      if (!success) throw new IllegalArgumentException("successful release history required");
      if (type.equals("SCHEMA")) {
        if (installedRank != 0
            || version != null
            || checksum != null
            || !script.equals("\"schubert_meta\""))
          throw new IllegalArgumentException("schema creation profile invalid");
      } else if (type.equals("SQL")) {
        if (installedRank < 1
            || installedRank > 999
            || version == null
            || !version.matches("(?!000)[0-9]{3}")
            || checksum == null
            || !script.matches("V" + version + "__[a-z0-9_]{1,200}\\.sql"))
          throw new IllegalArgumentException("versioned SQL profile invalid");
      } else throw new IllegalArgumentException("migration type refused");
    }
  }

  private static final String SQL =
      "select installed_rank,version,type,script,checksum,success"
          + " from schubert_meta.startup_schema_history() order by installed_rank";
  private final List<Row> expected;

  public SchemaHistoryAdmission(List<Row> expected) {
    this.expected = List.copyOf(Objects.requireNonNull(expected, "release schema history"));
    if (this.expected.isEmpty() || this.expected.size() > 1000)
      throw new IllegalArgumentException("release history size invalid");
    String previous = "000";
    for (int i = 0; i < this.expected.size(); i++) {
      Row row = this.expected.get(i);
      if (row.installedRank() != i)
        throw new IllegalArgumentException("release installed rank order invalid");
      // Row invariant: rank zero is SCHEMA only; every positive rank is SQL only.
      if (i > 0) {
        String version = Objects.requireNonNull(row.version(), "versioned release row");
        if (version.compareTo(previous) <= 0)
          throw new IllegalArgumentException("release version order invalid");
        previous = version;
      }
    }
  }

  public void verify(Connection connection) throws SQLException {
    inspect(connection);
  }

  /** SSC129: actual six-column rows, not the expected release vector or admission authority. */
  public List<Row> inspect(Connection connection) throws SQLException {
    Objects.requireNonNull(connection, "admitted connection");
    var observed = new ArrayList<Row>();
    try {
      require(!Thread.currentThread().isInterrupted());
      var statement = connection.prepareStatement(SQL);
      @Nullable Throwable primary = null;
      try {
        var query = required(statement);
        query.setQueryTimeout(5);
        var rows = query.executeQuery();
        @Nullable Throwable rowFailure = null;
        try {
          var values = required(rows);
          for (Row row : expected) {
            require(values.next());
            int rank = required(values.getObject("installed_rank", Integer.class));
            @Nullable String version = values.getString("version");
            String type = required(values.getString("type"));
            String script = required(values.getString("script"));
            @Nullable Integer checksum = values.getObject("checksum", Integer.class);
            boolean success = required(values.getObject("success", Boolean.class));
            require(
                row.installedRank() == rank
                    && Objects.equals(row.version(), version)
                    && row.type().equals(type)
                    && row.script().equals(script)
                    && Objects.equals(row.checksum(), checksum)
                    && success);
            observed.add(new Row(rank, version, type, script, checksum, success));
          }
          require(!values.next());
          require(!Thread.currentThread().isInterrupted());
        } catch (SQLException | RuntimeException | Error failure) {
          rowFailure = failure;
          throw failure;
        } finally {
          if (rows != null)
            try {
              rows.close();
            } catch (SQLException | RuntimeException | Error secondary) {
              if (JdbcAdmissionFailures.replace(rowFailure, secondary)) throw secondary;
            }
        }
      } catch (SQLException | RuntimeException | Error failure) {
        primary = failure;
        throw failure;
      } finally {
        if (statement != null)
          try {
            statement.close();
          } catch (SQLException | RuntimeException | Error secondary) {
            if (JdbcAdmissionFailures.replace(primary, secondary)) throw secondary;
          }
      }
      return List.copyOf(observed);
    } catch (SQLException known) {
      JdbcFailureGraph.preserveFatal(known);
      throw unavailable();
    }
  }

  private static void require(boolean accepted) throws SQLException {
    if (!accepted) throw unavailable();
  }

  private static <T> T required(@Nullable T value) throws SQLException {
    if (value == null) throw unavailable();
    return value;
  }

  private static SQLException unavailable() {
    return new SQLNonTransientConnectionException("schema history unavailable", "08001");
  }
}

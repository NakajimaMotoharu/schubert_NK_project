package org.postgresql.jdbc;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.HexFormat;
import java.util.List;
import java.util.TimeZone;
import java.util.logging.Logger;
import org.postgresql.core.BaseConnection;
import org.postgresql.core.BaseStatement;
import org.postgresql.core.Encoding;
import org.postgresql.core.Field;
import org.postgresql.core.Oid;
import org.postgresql.core.QueryExecutor;
import org.postgresql.core.Tuple;

/** Checks real PgResultSet conversion with rows owned entirely by the fixture. */
public final class PgTemporalRowContract {
  private PgTemporalRowContract() {}

  public static void main(String[] args) throws Exception {
    if (args.length != 2 || !TimeZone.getDefault().getID().equals(args[1])) {
      throw new IllegalArgumentException("expected vector path and fixed JVM zone");
    }
    TimeZone zone = TimeZone.getTimeZone(args[1]);
    QueryExecutor backendProperties =
        proxy(QueryExecutor.class, (instance, method, arguments) -> switch (method.getName()) {
          case "getIntegerDateTimes" -> true;
          case "getTimeZone" -> zone;
          default -> throw new AssertionError("unexpected query executor method " + method.getName());
        });
    BaseConnection connection =
        proxy(BaseConnection.class, (instance, method, arguments) -> switch (method.getName()) {
          case "getEncoding" -> Encoding.getJVMEncoding("UTF-8");
          case "getQueryExecutor" -> backendProperties;
          case "getLogger" -> Logger.getAnonymousLogger();
          case "getTypeInfo" -> new TypeInfoCache((BaseConnection) instance, 0);
          default -> throw new AssertionError("unexpected connection method " + method.getName());
        });
    BaseStatement statement =
        proxy(BaseStatement.class, (instance, method, arguments) -> switch (method.getName()) {
          case "getConnection" -> connection;
          default -> throw new AssertionError("unexpected statement method " + method.getName());
        });

    for (String row : Files.readAllLines(Path.of(args[0]), StandardCharsets.US_ASCII)) {
      String[] parts = row.split("\t", -1);
      if (parts.length != 4) {
        throw new IllegalArgumentException("four vector columns required");
      }
      assertValue(statement, parts[0] + "-TEXT", Field.TEXT_FORMAT,
          parts[1].getBytes(StandardCharsets.US_ASCII), parts[3]);
      assertValue(statement, parts[0] + "-BINARY", Field.BINARY_FORMAT,
          HexFormat.of().parseHex(parts[2]), parts[3]);
    }
    assertValue(statement, "PT-JDBC42-009-NULL-TEXT", Field.TEXT_FORMAT, null, "NULL");
    assertValue(statement, "PT-JDBC42-010-NULL-BINARY", Field.BINARY_FORMAT, null, "NULL");
  }

  private static void assertValue(
      BaseStatement statement, String id, int format, byte[] raw, String expected) throws SQLException {
    Field field = new Field("synthetic_timestamp", Oid.TIMESTAMPTZ);
    field.setFormat(format);
    var rows =
        new PgResultSet(null, statement, new Field[] {field},
            List.of(new Tuple(new byte[][] {raw})), null, 0, 0,
            ResultSet.TYPE_FORWARD_ONLY, ResultSet.CONCUR_READ_ONLY, ResultSet.CLOSE_CURSORS_AT_COMMIT, false);
    try {
      if (!rows.next()) {
        throw new AssertionError("synthetic row missing " + id);
      }
      OffsetDateTime value = rows.getObject(1, OffsetDateTime.class);
      String actual = value == null ? "NULL" : value.toInstant().toString();
      if (!expected.equals(actual) || rows.wasNull() != (raw == null) || rows.next()) {
        throw new AssertionError("unexpected JDBC temporal projection " + id + " " + actual);
      }
      System.out.println(id + "\t" + actual);
    } finally {
      rows.closeInternally();
      if (!rows.isClosed()) {
        throw new AssertionError("synthetic row not closed " + id);
      }
    }
  }

  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }
}

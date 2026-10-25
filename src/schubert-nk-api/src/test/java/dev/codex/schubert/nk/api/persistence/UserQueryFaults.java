package dev.codex.schubert.nk.api.persistence;

import static org.junit.jupiter.api.Assertions.assertFalse;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.Map;

/** Actual JDBC delegate with controlled boundary faults, never a replacement database/oracle. */
final class UserQueryFaults {
  final Map<String, Integer> faultOccurrences = new HashMap<>();
  final Map<String, Object> columns = new HashMap<>();
  String fault = "none";
  int changedRow;
  int statements;
  int resultCloses;
  int statementCloses;
  boolean empty;
  boolean duplicate;
  boolean wrongReadOnly;
  boolean wrongAutoCommit;

  Connection wrap(Connection connection) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (p, m, a) -> {
              fail(m.getName());
              if (m.getName().equals("getAutoCommit") && wrongAutoCommit) return true;
              if (m.getName().equals("isReadOnly") && wrongReadOnly) return false;
              Object value = invoke(connection, m, a);
              if (!m.getName().equals("prepareStatement")) return value;
              statements++;
              String sql = ((String) a[0]).toLowerCase(java.util.Locale.ROOT);
              assertFalse(sql.contains("password_hash"));
              assertFalse(sql.contains("context_hash"));
              assertFalse(sql.contains("ciphertext"));
              assertFalse(sql.contains(" for update"));
              assertFalse(sql.contains("select *"));
              return statement((PreparedStatement) value);
            });
  }

  private PreparedStatement statement(PreparedStatement statement) {
    return (PreparedStatement)
        Proxy.newProxyInstance(
            PreparedStatement.class.getClassLoader(),
            new Class<?>[] {PreparedStatement.class},
            (p, m, a) -> {
              fail(m.getName());
              Object value = invoke(statement, m, a);
              if (m.getName().equals("close")) {
                statementCloses++;
                fail("statementClose");
              }
              if (m.getName().equals("executeQuery")) return rows((ResultSet) value);
              return value;
            });
  }

  private ResultSet rows(ResultSet rows) {
    final int[] row = {0};
    final boolean[] altered = {false};
    final boolean[] wasNull = {false};
    return (ResultSet)
        Proxy.newProxyInstance(
            ResultSet.class.getClassLoader(),
            new Class<?>[] {ResultSet.class},
            (p, m, a) -> {
              String name = m.getName();
              fail(name);
              if (name.equals("wasNull") && altered[0]) return wasNull[0];
              if (name.startsWith("get")
                  && a != null
                  && (a.length == 1 || (name.equals("getObject") && a.length == 2))
                  && a[0] instanceof String column) {
                altered[0] =
                    columns.containsKey(column) && (changedRow == 0 || changedRow == row[0]);
                if (altered[0]) {
                  Object replacement = columns.get(column);
                  wasNull[0] = replacement == null;
                  if (name.equals("getLong"))
                    return replacement == null ? 0L : ((Number) replacement).longValue();
                  return replacement;
                }
              }
              Object value = invoke(rows, m, a);
              if (name.equals("next")) {
                row[0]++;
                if (empty) return false;
                if (duplicate && row[0] == 2) return true;
              }
              if (name.equals("close")) {
                resultCloses++;
                fail("resultClose");
              }
              return value;
            });
  }

  private void fail(String point) throws SQLException {
    int occurrence = faultOccurrences.merge(point, 1, Integer::sum);
    if (fault.equals(point) || fault.equals(point + "#" + occurrence))
      throw new SQLException("synthetic private JDBC fault marker");
  }

  private static Object invoke(Object target, Method method, Object[] arguments) throws Throwable {
    try {
      return method.invoke(target, arguments);
    } catch (InvocationTargetException failure) {
      throw failure.getCause();
    }
  }
}

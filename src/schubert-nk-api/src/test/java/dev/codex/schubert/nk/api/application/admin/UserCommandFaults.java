package dev.codex.schubert.nk.api.application.admin;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.Map;

/**
 * Public JDBC boundary faults over real PG; SQL and values never emitted to evidence. PT-ADM-020.
 */
final class UserCommandFaults {
  String sqlPart = "select id,username";
  String fault = "none";
  String sqlState = "08006";
  int occurrence = 1;
  int matched;
  boolean empty;
  boolean duplicate;
  Integer updateCount;
  final Map<String, Object> columns = new HashMap<>();
  Hook beforeUpdate = c -> {};

  @FunctionalInterface
  interface Hook {
    void run(Connection c) throws SQLException;
  }

  Connection wrap(Connection c) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (p, m, a) -> {
              String name = m.getName();
              if (!name.equals("prepareStatement")) {
                fail(name);
                return invoke(c, m, a);
              }
              String sql = (String) a[0];
              boolean selected = sql.contains(sqlPart) && ++matched == occurrence;
              if (selected) fail("prepareStatement");
              var statement = (PreparedStatement) invoke(c, m, a);
              return selected ? statement(c, statement) : statement;
            });
  }

  private PreparedStatement statement(Connection c, PreparedStatement s) {
    return (PreparedStatement)
        Proxy.newProxyInstance(
            PreparedStatement.class.getClassLoader(),
            new Class<?>[] {PreparedStatement.class},
            (p, m, a) -> {
              String name = m.getName();
              if (!name.equals("close")) fail(name);
              if (name.equals("executeUpdate")) {
                beforeUpdate.run(c);
                if (updateCount != null) return updateCount;
              }
              Object value = invoke(s, m, a);
              if (name.equals("close")) fail("statementClose");
              return name.equals("executeQuery") ? rows((ResultSet) value) : value;
            });
  }

  private ResultSet rows(ResultSet r) {
    int[] row = {0};
    boolean[] replaced = {false};
    boolean[] wasNull = {false};
    return (ResultSet)
        Proxy.newProxyInstance(
            ResultSet.class.getClassLoader(),
            new Class<?>[] {ResultSet.class},
            (p, m, a) -> {
              String name = m.getName();
              if (!name.equals("close")) fail(name);
              if (name.equals("wasNull") && replaced[0]) return wasNull[0];
              if (name.startsWith("get")
                  && a != null
                  && a.length == 1
                  && a[0] instanceof String column) {
                replaced[0] = columns.containsKey(column);
                if (replaced[0]) {
                  Object value = columns.get(column);
                  wasNull[0] = value == null;
                  return name.equals("getLong")
                      ? (value == null ? 0L : ((Number) value).longValue())
                      : value;
                }
              }
              Object value = invoke(r, m, a);
              if (name.equals("next")) {
                row[0]++;
                if (empty) return false;
                if (duplicate && row[0] == 2) return true;
              }
              if (name.equals("close")) fail("resultClose");
              return value;
            });
  }

  private void fail(String at) throws SQLException {
    if (fault.equals(at)) throw new SQLException("synthetic private provider marker", sqlState);
  }

  private static Object invoke(Object target, Method m, Object[] a) throws Throwable {
    try {
      return m.invoke(target, a);
    } catch (InvocationTargetException failure) {
      throw failure.getCause();
    }
  }
}

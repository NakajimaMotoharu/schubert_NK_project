package dev.codex.schubert.nk.api.maintenance;

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
 * Public JDBC interface fault/ownership probe over real PG, not private implementation reflection.
 */
final class MaintenanceJdbcProbe {
  final Map<String, Integer> faultOccurrences = new HashMap<>();
  String selectedSql = "maintenance_next_inbox";
  String fault = "none";
  String runtimeColumn = "none";
  String lastSqlState = "unobserved";
  boolean empty;
  boolean duplicate;
  boolean commitAfter;
  boolean fresh = true;
  int commits;
  int closes;
  int rollbacks;
  int saves;
  int deletes;
  int selectedStatements;
  final Map<String, Object> columns = new HashMap<>();
  Hook beforeDelete = c -> {};
  Runnable afterClose = () -> {};

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
              if (name.equals("setSavepoint")) saves++;
              if (name.equals("rollback")) rollbacks++;
              if (name.equals("getAutoCommit") && !fresh) return false;
              if (name.equals("commit")) {
                commits++;
                if (!commitAfter) fail("commit");
                Object value = invoke(c, m, a);
                if (commitAfter) fail("commit");
                return value;
              }
              if (name.equals("close")) {
                closes++;
                Object value = invoke(c, m, a);
                afterClose.run();
                fail("close");
                return value;
              }
              if (name.equals("prepareStatement")) {
                String sql = (String) a[0];
                if (sql.contains("maintenance_delete_inbox")) {
                  deletes++;
                  beforeDelete.run(c);
                }
                boolean selected = sql.contains(selectedSql);
                if (selected) {
                  selectedStatements++;
                  fail("prepareStatement");
                }
                return statement(c, (PreparedStatement) invoke(c, m, a), selected);
              }
              fail(name);
              return invoke(c, m, a);
            });
  }

  private PreparedStatement statement(Connection c, PreparedStatement s, boolean selected) {
    return (PreparedStatement)
        Proxy.newProxyInstance(
            PreparedStatement.class.getClassLoader(),
            new Class<?>[] {PreparedStatement.class},
            (p, m, a) -> {
              String name = m.getName();
              if (selected && !name.equals("close")) fail(name);
              if (selected && name.equals("executeQuery") && fault.equals("aborted")) {
                try (var abort = c.createStatement()) {
                  abort.execute("select 1 / 0");
                }
              }
              Object value = invoke(s, m, a);
              if (selected && name.equals("close")) fail("statementClose");
              return selected && name.equals("executeQuery") ? rows((ResultSet) value) : value;
            });
  }

  private ResultSet rows(ResultSet r) {
    int[] position = {0};
    return (ResultSet)
        Proxy.newProxyInstance(
            ResultSet.class.getClassLoader(),
            new Class<?>[] {ResultSet.class},
            (p, m, a) -> {
              String name = m.getName();
              if (!name.equals("close")) fail(name);
              if (name.startsWith("get")
                  && a != null
                  && a.length > 0
                  && a[0] instanceof String column
                  && columns.containsKey(column)) {
                Object replacement = columns.get(column);
                return replacement instanceof byte[] bytes ? bytes.clone() : replacement;
              }
              if (name.startsWith("get")
                  && a != null
                  && a.length > 0
                  && a[0] instanceof String column
                  && runtimeColumn.equals(column))
                throw new IllegalArgumentException("synthetic-private-provider-marker");
              Object value = invoke(r, m, a);
              if (name.equals("next")) {
                position[0]++;
                if (empty) return false;
                if (duplicate && position[0] == 2) return true;
              }
              if (name.equals("close")) fail("resultClose");
              return value;
            });
  }

  private void fail(String name) throws SQLException {
    int occurrence = faultOccurrences.merge(name, 1, Integer::sum);
    if (fault.equals(name) || fault.equals(name + "#" + occurrence))
      throw new SQLException("synthetic-private-provider-marker", "08006");
  }

  private Object invoke(Object target, Method method, Object[] args) throws Throwable {
    try {
      return method.invoke(target, args);
    } catch (InvocationTargetException failed) {
      if (failed.getCause() instanceof SQLException sqlFailure)
        lastSqlState = sqlFailure.getSQLState();
      throw failed.getCause();
    }
  }
}

package dev.codex.schubert.nk.batch.repository;

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
final class BatchJdbcProbe {
  final Map<String, Integer> faultOccurrences = new HashMap<>();
  final Map<String, Throwable> thrown = new HashMap<>();
  int liveStatements;
  int liveRows;
  int injected;
  String selectedSql = "maintenance_cleanup_";
  String fault = "none";
  String lastSqlState = "unobserved";
  String lastSql = "unobserved";
  boolean empty;
  boolean duplicate;
  boolean commitAfter;
  boolean fresh = true;
  boolean nullStatement;
  boolean nullRows;
  boolean extraLastRow;
  final Map<String, Object> connectionValues = new HashMap<>();
  int commits;
  int closes;
  int rollbacks;
  int saves;
  int deletes;
  int selectedStatements;
  int autoChanges;
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
              if (connectionValues.containsKey(name)) return connectionValues.get(name);
              if (name.equals("setSavepoint")) saves++;
              if (name.equals("setAutoCommit")) autoChanges++;
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
                lastSql = sql;
                if (sql.contains("maintenance_delete_inbox")) {
                  deletes++;
                  beforeDelete.run(c);
                }
                boolean selected = sql.contains(selectedSql);
                if (selected) {
                  selectedStatements++;
                  fail("prepareStatement");
                  if (nullStatement) return null;
                }
                var obtained = (PreparedStatement) invoke(c, m, a);
                if (selected) liveStatements++;
                return statement(c, obtained, selected);
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
              if (selected && name.equals("executeQuery") && nullRows) return null;
              Object value = invoke(s, m, a);
              if (selected && name.equals("close")) {
                liveStatements--;
                fail("statementClose");
              }
              if (selected && name.equals("executeQuery")) {
                liveRows++;
                return rows((ResultSet) value);
              }
              return value;
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
              Object value = invoke(r, m, a);
              if (name.equals("next")) {
                position[0]++;
                if (empty) return false;
                if (duplicate && position[0] == 2) return true;
                if (extraLastRow && position[0] == 8) return true;
              }
              if (name.equals("close")) {
                liveRows--;
                fail("resultClose");
              }
              return value;
            });
  }

  private void fail(String name) throws Throwable {
    int occurrence = faultOccurrences.merge(name, 1, Integer::sum);
    if (occurrence == 1 && thrown.containsKey(name)) {
      injected++;
      throw thrown.get(name);
    }
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

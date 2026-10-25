package dev.codex.schubert.nk.batch.cleanup;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/** Public JDBC calls only; deterministic failure timing, never private implementation access. */
final class ServiceJdbcProbe {
  final Map<String, Integer> failAt = new HashMap<>();
  final Map<String, Integer> seen = new HashMap<>();
  final Map<String, Throwable> thrown = new HashMap<>();
  final Map<String, Object> columns = new HashMap<>();
  final Set<String> empty = new HashSet<>();
  final Set<String> duplicate = new HashSet<>();
  String runtimeAt = "none";
  int commits;
  int rollbacks;
  int restores;
  int closes;
  int failures;
  int prepared;
  Hook afterCommit = count -> {};

  @FunctionalInterface
  interface Hook {
    void accept(int count) throws Exception;
  }

  Connection wrap(Connection connection) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (p, m, a) -> {
              String name = m.getName();
              if (name.equals("prepareStatement")) {
                prepared++;
                String sql = (String) a[0];
                String stage =
                    sql.contains("pg_try_advisory_lock")
                        ? "lock"
                        : sql.contains("pg_advisory_unlock")
                            ? "unlock"
                            : sql.contains("set_config('statement_timeout'")
                                ? "timeout"
                                : sql.contains("maintenance_cleanup_logs") ? "cleanup" : "progress";
                check(stage + ".prepareStatement");
                return statement((PreparedStatement) invoke(connection, m, a), stage);
              }
              if (name.equals("commit")) {
                check("commitBefore");
                Object result = invoke(connection, m, a);
                commits++;
                afterCommit.accept(commits);
                check("commitAfter");
                return result;
              }
              if (name.equals("rollback")) {
                rollbacks++;
                check("rollback");
              }
              if (name.equals("close")) closes++;
              if (name.equals("setAutoCommit")) {
                if ((boolean) a[0]) {
                  restores++;
                  check("restore");
                } else check("begin");
              }
              check(name);
              return invoke(connection, m, a);
            });
  }

  private PreparedStatement statement(PreparedStatement statement, String stage) {
    return (PreparedStatement)
        Proxy.newProxyInstance(
            PreparedStatement.class.getClassLoader(),
            new Class<?>[] {PreparedStatement.class},
            (p, m, a) -> {
              String name = m.getName();
              if (!name.equals("close")) check(stage + "." + name);
              Object result = invoke(statement, m, a);
              if (name.equals("close")) check(stage + ".statementClose");
              return name.equals("executeQuery") ? rows((ResultSet) result, stage) : result;
            });
  }

  private ResultSet rows(ResultSet row, String stage) {
    int[] position = {0};
    return (ResultSet)
        Proxy.newProxyInstance(
            ResultSet.class.getClassLoader(),
            new Class<?>[] {ResultSet.class},
            (p, m, a) -> {
              String name = m.getName();
              if (!name.equals("close")) check(stage + "." + name);
              if ((name.equals("getObject") || name.equals("getString"))
                  && a[0] instanceof String column
                  && columns.containsKey(stage + "." + column))
                return columns.get(stage + "." + column);
              Object result = invoke(row, m, a);
              if (name.equals("next")) {
                position[0]++;
                if (empty.contains(stage)) return false;
                if (duplicate.contains(stage) && position[0] == 2) return true;
              }
              if (name.equals("close")) check(stage + ".resultClose");
              return result;
            });
  }

  private void check(String key) throws Throwable {
    int count = seen.merge(key, 1, Integer::sum);
    if (count == 1 && thrown.containsKey(key)) {
      failures++;
      throw thrown.get(key);
    }
    if (key.equals(runtimeAt)) throw new IllegalStateException("public programming fault");
    if (Objects.equals(failAt.get(key), count)) {
      failures++;
      throw new SQLException("synthetic-private-provider-marker", "08006");
    }
  }

  private static Object invoke(Object target, Method method, Object[] args) throws Throwable {
    try {
      return method.invoke(target, args);
    } catch (InvocationTargetException failure) {
      throw failure.getCause();
    }
  }
}

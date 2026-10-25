package dev.codex.schubert.nk.batch.cleanup;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

/** Public JDBC fault/projection seam; actual resources close before injected close failures. */
final class HandoffJdbcProbe {
  final Map<String, Integer> seen = new HashMap<>();
  final Map<String, Integer> failAt = new HashMap<>();
  final Map<Integer, String> anomalies = new HashMap<>();
  int queries;
  int failures;
  int openedStatements;
  int closedStatements;
  int openedRows;
  int closedRows;

  Connection wrap(Connection connection) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (p, method, args) -> {
              String name = method.getName();
              hit("connection." + name);
              if (name.equals("prepareStatement")) {
                int query = ++queries;
                if ("nullStatement".equals(anomalies.get(query))) return null;
                var statement = (PreparedStatement) invoke(connection, method, args);
                openedStatements++;
                return statement(statement, query);
              }
              return invoke(connection, method, args);
            });
  }

  private PreparedStatement statement(PreparedStatement statement, int query) {
    return (PreparedStatement)
        Proxy.newProxyInstance(
            PreparedStatement.class.getClassLoader(),
            new Class<?>[] {PreparedStatement.class},
            (p, method, args) -> {
              String name = method.getName();
              if (name.equals("close")) {
                Object result = invoke(statement, method, args);
                closedStatements++;
                hit("statement.close");
                return result;
              }
              hit("statement." + name);
              if (name.equals("setQueryTimeout")) assertEquals(5, args[0]);
              if (name.equals("executeQuery") && "nullRows".equals(anomalies.get(query)))
                return null;
              Object result = invoke(statement, method, args);
              if (name.equals("executeQuery")) {
                openedRows++;
                return rows((ResultSet) result, query);
              }
              return result;
            });
  }

  private ResultSet rows(ResultSet row, int query) {
    int[] position = {0};
    return (ResultSet)
        Proxy.newProxyInstance(
            ResultSet.class.getClassLoader(),
            new Class<?>[] {ResultSet.class},
            (p, method, args) -> {
              String name = method.getName();
              if (name.equals("close")) {
                Object result = invoke(row, method, args);
                closedRows++;
                hit("row.close");
                return result;
              }
              hit("row." + name);
              String anomaly = anomalies.get(query);
              if (name.equals("getObject")) {
                assertEquals("value", args[0]);
                assertEquals(Boolean.class, args[1]);
                if ("null".equals(anomaly)) return null;
                if ("flip".equals(anomaly)) return !(Boolean) invoke(row, method, args);
              }
              if (name.equals("next")) {
                position[0]++;
                if ("missing".equals(anomaly)) return false;
                if ("duplicate".equals(anomaly) && position[0] == 2) return true;
              }
              return invoke(row, method, args);
            });
  }

  private void hit(String name) throws SQLException {
    int count = seen.merge(name, 1, Integer::sum);
    if (Objects.equals(failAt.get(name), count)) {
      failures++;
      throw new SQLException("private-provider-probe", "08006");
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

package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.Map;
import java.util.TreeMap;

/** Public JDBC observation only; actual owned resources close before close-fault injection. */
final class CompletionJdbcProbe {
  interface Hook {
    void call(String key, int count) throws Throwable;
  }

  final Map<String, Integer> seen = new TreeMap<>();
  Hook before = (key, count) -> {};
  Hook after = (key, count) -> {};
  int statements;
  int rows;

  Connection wrap(Connection real) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (proxy, method, args) -> {
              String key = "connection." + method.getName();
              int n = point(key);
              Object result = invoke(real, method, args);
              if (method.getName().equals("prepareStatement")) {
                statements++;
                result = statement((PreparedStatement) result);
              }
              after.call(key, n);
              return result;
            });
  }

  private PreparedStatement statement(PreparedStatement real) {
    return (PreparedStatement)
        Proxy.newProxyInstance(
            PreparedStatement.class.getClassLoader(),
            new Class<?>[] {PreparedStatement.class},
            (proxy, method, args) -> {
              String key = "statement." + method.getName();
              if (method.getName().equals("close")) {
                Object result = invoke(real, method, args);
                statements--;
                int n = point(key);
                after.call(key, n);
                return result;
              }
              int n = point(key);
              Object result = invoke(real, method, args);
              if (method.getName().equals("executeQuery")) {
                rows++;
                result = row((ResultSet) result);
              }
              after.call(key, n);
              return result;
            });
  }

  private ResultSet row(ResultSet real) {
    return (ResultSet)
        Proxy.newProxyInstance(
            ResultSet.class.getClassLoader(),
            new Class<?>[] {ResultSet.class},
            (proxy, method, args) -> {
              String key = "row." + method.getName();
              if (method.getName().equals("close")) {
                Object result = invoke(real, method, args);
                rows--;
                int n = point(key);
                after.call(key, n);
                return result;
              }
              int n = point(key);
              Object result = invoke(real, method, args);
              after.call(key, n);
              return result;
            });
  }

  private int point(String key) throws Throwable {
    int n = seen.merge(key, 1, Integer::sum);
    before.call(key, n);
    return n;
  }

  void released() {
    assertEquals(0, statements);
    assertEquals(0, rows);
    assertFalse(seen.containsKey("connection.close"));
  }

  private static Object invoke(Object target, Method method, Object[] args) throws Throwable {
    try {
      return method.invoke(target, args);
    } catch (InvocationTargetException failure) {
      throw failure.getCause();
    }
  }
}

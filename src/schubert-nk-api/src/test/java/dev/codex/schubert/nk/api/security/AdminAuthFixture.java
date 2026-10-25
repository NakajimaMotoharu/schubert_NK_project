package dev.codex.schubert.nk.api.security;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Real JDBC delegation with per-operation fault points and observed lock order. No secret logs. */
final class AdminAuthFixture {
  final Map<String, Integer> faultOccurrences = new HashMap<>();

  interface Before {
    void run(String sql) throws SQLException;
  }

  Before before = sql -> {};
  final List<String> statements = new ArrayList<>();
  final Map<String, Object> fields = new HashMap<>();
  String method = "none";
  String match = "";
  boolean empty;
  boolean duplicate;
  boolean nullNumber;
  boolean nullText;
  boolean reverseIds;
  Long ownerOverride;
  int resultsClosed;
  int statementsClosed;

  Connection wrap(Connection real) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (p, m, a) -> {
              if (m.getName().equals("prepareStatement")) {
                String sql = (String) a[0];
                before.run(sql);
                statements.add(sql);
                fail(sql, m.getName());
                return statement((PreparedStatement) invoke(real, m, a), sql);
              }
              fail("connection", m.getName());
              return invoke(real, m, a);
            });
  }

  private PreparedStatement statement(PreparedStatement real, String sql) {
    return (PreparedStatement)
        Proxy.newProxyInstance(
            PreparedStatement.class.getClassLoader(),
            new Class<?>[] {PreparedStatement.class},
            (p, m, a) -> {
              fail(sql, m.getName());
              Object result = invoke(real, m, a);
              if (m.getName().equals("executeQuery")) return rows((ResultSet) result, sql);
              if (m.getName().equals("close")) {
                statementsClosed++;
                fail(sql, "statementClose");
              }
              if (m.getName().equals("executeUpdate")
                  && method.equals("zeroUpdate")
                  && sql.contains(match)) return 0;
              return result;
            });
  }

  private ResultSet rows(ResultSet real, String sql) {
    int[] index = {0};
    return (ResultSet)
        Proxy.newProxyInstance(
            ResultSet.class.getClassLoader(),
            new Class<?>[] {ResultSet.class},
            (p, m, a) -> {
              String name = m.getName();
              fail(sql, name);
              boolean affected = sql.contains(match);
              if (affected
                  && name.startsWith("get")
                  && a != null
                  && a.length > 0
                  && a[0] instanceof String field
                  && fields.containsKey(field)) return fields.get(field);
              if (affected && name.equals("getLong")) {
                if (ownerOverride != null) return ownerOverride;
                if (nullNumber) return 0L;
                if (reverseIds) return 9L - index[0];
              }
              if (affected && name.equals("wasNull") && nullNumber) return true;
              if (affected && name.equals("getString") && nullText) return null;
              Object result = invoke(real, m, a);
              if (name.equals("next")) {
                index[0]++;
                if (affected && empty) return false;
                if (affected && duplicate && index[0] == 2) return true;
              }
              if (name.equals("close")) {
                resultsClosed++;
                fail(sql, "resultClose");
              }
              return result;
            });
  }

  private void fail(String sql, String point) throws SQLException {
    if (!sql.contains(match)) return;
    if (method.equals("providerIaeGetLongAndResultClose")) {
      if (point.equals("getLong"))
        throw new IllegalArgumentException("synthetic-private-provider-identity");
      if (point.equals("resultClose")) throw new SQLException("synthetic-private-close");
    }
    int occurrence = faultOccurrences.merge(point, 1, Integer::sum);
    if (method.equals(point) || method.equals(point + "#" + occurrence))
      throw new SQLException("synthetic private administrative JDBC marker");
  }

  private static Object invoke(Object target, Method method, Object[] args) throws Throwable {
    try {
      return method.invoke(target, args);
    } catch (InvocationTargetException failure) {
      throw failure.getCause();
    }
  }
}

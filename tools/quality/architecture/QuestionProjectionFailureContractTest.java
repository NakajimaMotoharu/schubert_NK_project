package dev.codex.schubert.nk.api.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationId;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/** PT-QRY-SV001..010; FUN012/QST005/006, UI236, SS332§3/9; own JDBC interfaces only. */
public final class QuestionProjectionFailureContractTest {
  private static final AuthenticatedActor USER = new AuthenticatedActor(7, "unit7", Role.USER);
  private static final AuthenticatedActor ADMIN = new AuthenticatedActor(8, "unit8", Role.ADMIN);
  private static final QuestionQueryRepository REPOSITORY = new QuestionQueryRepository();

  @Test
  void projection001BorrowedTransactionPreconditions() {
    for (int kind = 0; kind < 4; kind++) {
      for (int invalid = 0; invalid < 2; invalid++) {
        var jdbc = new Jdbc(List.of());
        jdbc.autoCommit = invalid == 0;
        jdbc.readOnly = invalid == 0;
        unavailable(jdbc, kind);
        assertEquals(0, jdbc.prepares);
        assertEquals(invalid == 0 ? 0 : 1, jdbc.readOnlyCalls);
        jdbc.borrowed();
      }
    }
  }

  @Test
  void projection002SqlStageFailuresCloseOwnedResources() {
    for (int kind = 0; kind < 4; kind++) {
      for (String stage : List.of("getAutoCommit", "isReadOnly", "prepareStatement", "setObject",
          "executeQuery", "next", "getObject", "getString", "resultClose", "statementClose")) {
        var jdbc = new Jdbc(List.of(kind == 0 || kind == 2 ? questionRow() : noticeRow()));
        jdbc.fault = stage;
        unavailable(jdbc, kind);
        int statement = List.of("getAutoCommit", "isReadOnly", "prepareStatement").contains(stage) ? 0 : 1;
        int result = List.of("getAutoCommit", "isReadOnly", "prepareStatement", "setObject", "executeQuery").contains(stage) ? 0 : 1;
        assertEquals(statement, jdbc.statementCloses, stage);
        assertEquals(result, jdbc.resultCloses, stage);
        jdbc.borrowed();
      }
    }
  }

  @Test
  void projection003PageTotalsAndLimits() {
    for (int kind = 0; kind < 2; kind++) {
      var row = emptyRow();
      row.put("total", 49_999_951L);
      var jdbc = new Jdbc(List.of(row));
      int selected = kind;
      var failure = assertThrows(QuestionQueryException.class, () -> query(jdbc, selected));
      assertEquals(ResultCode.RESOURCE_LIMIT, failure.resultCode());
      assertEquals(List.of("RS", "PS"), jdbc.closes);
      jdbc.borrowed();
    }
    var rows = new ArrayList<Map<String, Object>>();
    for (long id = 50; id > 0; id--) {
      var row = questionRow();
      row.put("id", id);
      row.put("total", 49_999_950L);
      row.put("pages", 999_999L);
      row.put("effective", 999_999L);
      rows.add(row);
    }
    var jdbc = new Jdbc(rows);
    var value = REPOSITORY.questionSearch(jdbc.connection, USER, question(999_999));
    assertEquals(new PagedResponseData(999_999, 50, 49_999_950, 999_999, 49_999_901, 49_999_950), value.data());
    assertEquals(50, value.records().size());
    assertEquals(999_999, jdbc.parameters.get(13));
    assertEquals(List.of("RS", "PS"), jdbc.closes);
    jdbc.borrowed();
  }

  @Test
  void projection004PageMetadataAndCardinality() {
    for (int kind = 0; kind < 2; kind++) {
      unavailable(new Jdbc(List.of()), kind);
      for (String field : List.of("total", "pages", "effective")) {
        var bad = emptyRow();
        bad.put(field, field.equals("total") ? -1L : 2L);
        unavailable(new Jdbc(List.of(bad)), kind);
        var first = kind == 0 ? questionRow() : noticeRow();
        first.put("total", 2L);
        var second = new HashMap<>(first);
        second.put(field, 3L);
        unavailable(new Jdbc(List.of(first, second)), kind);
      }
      var missingRecord = emptyRow();
      missingRecord.put("total", 1L);
      unavailable(new Jdbc(List.of(missingRecord)), kind);
      var overflow = emptyRow();
      overflow.put("pages", Long.MAX_VALUE);
      unavailable(new Jdbc(List.of(overflow)), kind);
      var first = kind == 0 ? questionRow() : noticeRow();
      unavailable(new Jdbc(List.of(first, new HashMap<>(first))), kind);
    }
  }

  @Test
  void projection005RequiredColumnsAndTypedValues() {
    for (String field : List.of("total", "pages", "effective", "receipt_id", "username", "question_body", "answer_state", "submitted_at")) {
      var row = questionRow();
      row.put(field, null);
      unavailable(new Jdbc(List.of(row)), 0);
    }
    for (String field : List.of("receipt_id", "notification_type", "state", "question_deleted", "submitted_at", "updated_at")) {
      var row = noticeRow();
      row.put(field, null);
      unavailable(new Jdbc(List.of(row)), 1);
    }
    var badState = questionRow();
    badState.put("answer_state", "UNKNOWN");
    unavailable(new Jdbc(List.of(badState)), 0);
    var wrongType = emptyRow();
    wrongType.put("total", "not a number");
    unavailable(new Jdbc(List.of(wrongType)), 0);
  }

  @Test
  void projection006DetailAbsenceDuplicateAndErrorCodes() {
    for (int kind = 2; kind < 4; kind++) {
      var absent = new Jdbc(List.of());
      assertEquals(Optional.empty(), query(absent, kind));
      assertEquals(List.of("RS", "PS"), absent.closes);
      absent.borrowed();
      var row = detailRow(kind);
      unavailable(new Jdbc(List.of(row, new HashMap<>(row))), kind);
    }
    var unknown = noticeRow();
    unknown.put("notification_type", "ERROR");
    unknown.put("state", "ERROR");
    unknown.put("error_code", "UNKNOWN");
    unavailable(new Jdbc(List.of(unknown)), 3);
    var missing = questionRow();
    missing.put("question_body", null);
    unavailable(new Jdbc(List.of(missing)), 2);
  }

  @Test
  void projection007SuppressedFailuresAndFatalIdentity() {
    for (String stage : List.of("resultClose", "statementClose")) {
      var row = emptyRow();
      row.put("total", 49_999_951L);
      var jdbc = new Jdbc(List.of(row));
      jdbc.fault = stage;
      unavailable(jdbc, 0);
      assertEquals(List.of("RS", "PS"), jdbc.closes);
      jdbc.borrowed();
    }
    for (int kind : new int[] {0, 2}) {
      var fatal = new AssertionError("PUBLIC owned fatal");
      var jdbc = new Jdbc(List.of(questionRow()));
      jdbc.fault = "executeQuery";
      jdbc.failure = new SQLException("PUBLIC provider", fatal);
      int selected = kind;
      assertSame(fatal, assertThrows(AssertionError.class, () -> query(jdbc, selected)));
      assertEquals(List.of("PS"), jdbc.closes);
      jdbc.borrowed();
    }
  }

  @Test
  void projection008RequestAndNullBoundaries() {
    var jdbc = new Jdbc(List.of());
    assertThrows(NullPointerException.class, () -> REPOSITORY.questionSearch(null, USER, question(1)));
    assertThrows(NullPointerException.class, () -> REPOSITORY.questionSearch(jdbc.connection, null, question(1)));
    assertThrows(NullPointerException.class, () -> REPOSITORY.questionSearch(jdbc.connection, USER, null));
    assertThrows(IllegalArgumentException.class, () -> REPOSITORY.questionSearch(jdbc.connection, USER, question(0)));
    assertEquals(0, jdbc.prepares);
    jdbc.borrowed();
  }

  @Test
  void projection009StableSqlAndOwnerScope() {
    for (AuthenticatedActor actor : List.of(USER, ADMIN)) {
      var q = new Jdbc(List.of());
      assertEquals(Optional.empty(), REPOSITORY.questionDetail(q.connection, actor, new QuestionDetailRequestData(new QuestionId(3))));
      assertEquals(3L, q.parameters.get(1));
      assertEquals(actor == USER ? 2 : 1, q.parameters.size());
      if (actor == USER) assertEquals(7L, q.parameters.get(2));
      assertFalse(q.sql.contains(" or owner_user_id"));
      assertTrue(q.sql.contains("not question_deleted"));
      var n = new Jdbc(List.of());
      assertEquals(Optional.empty(), REPOSITORY.notificationDetail(n.connection, actor, new NotificationDetailRequestData(new NotificationId(3))));
      assertEquals(Map.of(1, 3L, 2, actor.userId()), n.parameters);
      assertTrue(n.sql.contains("where id=? and owner_user_id=?"));
      q.borrowed();
      n.borrowed();
    }
  }

  @Test
  void projection010BorrowedLifecycleAndDiagnostics() {
    for (int kind = 0; kind < 4; kind++) {
      var jdbc = new Jdbc(kind < 2 ? List.of(emptyRow()) : List.of());
      Object actual = query(jdbc, kind);
      if (kind < 2) {
        var value = assertInstanceOf(TypedPayloadValues.class, actual);
        assertEquals(new PagedResponseData(1, 50, 0, 1, 0, 0), value.data());
        assertTrue(value.records().isEmpty());
      } else assertEquals(Optional.empty(), actual);
      assertEquals(List.of("RS", "PS"), jdbc.closes);
      jdbc.borrowed();
      var failed = new Jdbc(List.of());
      failed.fault = "prepareStatement";
      unavailable(failed, kind);
      failed.borrowed();
    }
  }

  private static QuestionSearchRequestData question(int page) {
    return new QuestionSearchRequestData(Optional.empty(), Optional.empty(), Optional.empty(), Optional.empty(), Optional.empty(), page, 50);
  }

  private static Object query(Jdbc jdbc, int kind) {
    return switch (kind) {
      case 0 -> REPOSITORY.questionSearch(jdbc.connection, USER, question(1));
      case 1 -> REPOSITORY.notificationSearch(jdbc.connection, ADMIN, new NotificationSearchRequestData(Optional.empty(), Optional.empty(), Optional.empty(), 1, 50));
      case 2 -> REPOSITORY.questionDetail(jdbc.connection, USER, new QuestionDetailRequestData(new QuestionId(3)));
      case 3 -> REPOSITORY.notificationDetail(jdbc.connection, ADMIN, new NotificationDetailRequestData(new NotificationId(3)));
      default -> throw new AssertionError("fixed four query kinds only");
    };
  }

  private static void unavailable(Jdbc jdbc, int kind) {
    var failure = assertThrows(QuestionQueryException.class, () -> query(jdbc, kind));
    assertEquals(ResultCode.TEMPORARY_FAILURE, failure.resultCode());
    assertEquals("question query is unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static Map<String, Object> emptyRow() {
    var row = new HashMap<String, Object>();
    row.put("total", 0L);
    row.put("pages", 1L);
    row.put("effective", 1L);
    return row;
  }

  private static Map<String, Object> questionRow() {
    var row = emptyRow();
    row.put("total", 1L);
    row.put("id", 3L);
    row.put("receipt_id", "00000000000000000000000001");
    row.put("username", "unit7");
    row.put("question_body", "unit question");
    row.put("answer_state", "UNANSWERED");
    row.put("submitted_at", OffsetDateTime.parse("2026-10-01T00:00:00.123456Z"));
    return row;
  }

  private static Map<String, Object> noticeRow() {
    var row = questionRow();
    row.put("notification_type", "ACCEPTED");
    row.put("state", "RECEIVED");
    row.put("question_deleted", false);
    row.put("question_id", 3L);
    row.put("updated_at", OffsetDateTime.parse("2026-10-01T00:00:00.123456Z"));
    return row;
  }

  private static Map<String, Object> detailRow(int kind) {
    return kind == 2 ? questionRow() : noticeRow();
  }

  @FunctionalInterface
  private interface Invocation {
    Object invoke(String method, Object[] arguments) throws Throwable;
  }

  private static <T> T proxy(Class<T> type, Invocation invocation) {
    return type.cast(Proxy.newProxyInstance(QuestionProjectionFailureContractTest.class.getClassLoader(), new Class<?>[] {type},
        (self, method, arguments) -> invocation.invoke(method.getName(), arguments == null ? new Object[0] : arguments)));
  }

  private static final class Jdbc {
    final List<Map<String, Object>> rows;
    final Map<Integer, Object> parameters = new HashMap<>();
    final List<String> closes = new ArrayList<>();
    final Connection connection;
    boolean autoCommit;
    boolean readOnly = true;
    int readOnlyCalls;
    int prepares;
    int statementCloses;
    int resultCloses;
    int connectionLifecycle;
    int cursor = -1;
    String sql = "";
    String fault = "";
    SQLException failure = new SQLException("PUBLIC provider");

    Jdbc(List<Map<String, Object>> rows) {
      this.rows = rows;
      connection = proxy(Connection.class, (method, args) -> {
        if (method.equals("prepareStatement")) prepares++;
        if (method.equals("isReadOnly")) readOnlyCalls++;
        trip(method);
        return switch (method) {
          case "getAutoCommit" -> autoCommit;
          case "isReadOnly" -> readOnly;
          case "prepareStatement" -> { sql = (String) args[0]; yield statement(); }
          case "commit", "rollback", "close", "setAutoCommit", "setReadOnly" -> { connectionLifecycle++; yield null; }
          default -> throw new AssertionError("unexpected owned connection callback: " + method);
        };
      });
    }

    private PreparedStatement statement() {
      return proxy(PreparedStatement.class, (method, args) -> {
        if (method.equals("close")) { statementCloses++; closes.add("PS"); trip("statementClose"); return null; }
        trip(method);
        return switch (method) {
          case "setObject", "setInt" -> { parameters.put((Integer) args[0], args[1]); yield null; }
          case "executeQuery" -> result();
          default -> throw new AssertionError("unexpected owned statement callback: " + method);
        };
      });
    }

    private ResultSet result() {
      return proxy(ResultSet.class, (method, args) -> {
        if (method.equals("close")) { resultCloses++; closes.add("RS"); trip("resultClose"); return null; }
        trip(method);
        return switch (method) {
          case "next" -> ++cursor < rows.size();
          case "getObject" -> rows.get(cursor).get((String) args[0]);
          case "getString" -> (String) rows.get(cursor).get((String) args[0]);
          default -> throw new AssertionError("unexpected owned result callback: " + method);
        };
      });
    }

    private void trip(String method) throws SQLException {
      if (method.equals(fault)) throw failure;
    }

    void borrowed() {
      assertEquals(0, connectionLifecycle, "borrowed connection must not be mutated or closed");
    }
  }
}

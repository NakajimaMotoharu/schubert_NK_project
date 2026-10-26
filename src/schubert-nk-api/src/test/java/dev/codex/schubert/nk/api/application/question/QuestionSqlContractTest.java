package dev.codex.schubert.nk.api.application.question;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.persistence.QuestionQueryException;
import dev.codex.schubert.nk.api.persistence.QuestionQueryRepository;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationRecord;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSummaryRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.AnswerState;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationId;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationState;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationType;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/**
 * NK-QRY-001/NK-NTF-001/UI236/SS332; PT-QRY-SQL001..008; QRY003. No backend or SQL fault injection.
 */
class QuestionSqlContractTest {
  private static final String ANSWERED_STATE = "ANSWERED";
  private static final String COMPLETED_STATE = "COMPLETED";
  private static final String RECEIVED_STATE = "RECEIVED";
  private static final String ROW_SUBMITTED_AT = "2026-10-01T00:00:00.123456Z";
  private static final String QSS = "QSSREQ01";
  private static final String QSD = "QSDREQ01";
  private static final String NTS = "NTSREQ01";
  private static final String NTD = "NTDREQ01";
  private static final String RECEIPT = "00000000000000000000000001";
  private static final String USERNAME = "unit7";
  private static final String ANSWER = "answer";
  private static final String SUMMARY = "😀".repeat(100);
  private static final String BODY = SUMMARY + "tail";
  private static final String PAGE_TEXT = "999999050";
  private static final int LAST_PAGE = 999999;
  private static final int FILTER_MASKS = 32;
  private static final int NOTICE_MASKS = 8;
  private static final int TYPED_ARGUMENTS = 2;
  private static final Instant NOW = Instant.parse("2026-10-01T00:00:00.123Z");
  private static final Instant ANSWERED = Instant.parse("2026-10-01T00:00:01.123Z");
  private static final OffsetDateTime FROM = OffsetDateTime.parse("2026-10-01T00:00:00.123Z");
  private static final OffsetDateTime TO = OffsetDateTime.parse("2026-10-01T00:00:01.123Z");
  private static final AuthenticatedActor USER = new AuthenticatedActor(7, USERNAME, Role.USER);
  private static final AuthenticatedActor ADMIN = new AuthenticatedActor(8, "admin8", Role.ADMIN);

  @Test
  void sql001QuestionEmptyPagesSeparateUserAndAdminOwnership() {
    for (var actor : List.of(USER, ADMIN)) {
      var jdbc = new Jdbc(List.of(emptyRow()));
      var request = search(QSS, 0);
      var value =
          request.query(new QuestionQueryRepository(), jdbc.connection(), actor).orElseThrow();
      assertEquals("QSSRSP01", value.layoutId().value());
      assertEquals(new PagedResponseData(1, 50, 0, 1, 0, 0), value.data());
      assertTrue(value.records().isEmpty());
      List<@Nullable Object> expected = new ArrayList<>();
      if (actor == USER) expected.add(7L);
      for (int i = 0; i < 11; i++) expected.add(null);
      expected.add(LAST_PAGE);
      jdbc.assertBinds(expected);
      assertEquals(actor == USER, jdbc.sql.contains("and owner_user_id=?"));
      assertTrue(jdbc.sql.contains("where not question_deleted"));
      pageSql(jdbc.sql, true);
      assertDoesNotThrow(() -> request.validateResponse(value));
      jdbc.assertReleased();
    }
  }

  @Test
  void sql002QuestionFilterMasksUseTypedDuplicateBinds() {
    for (int mask = 0; mask < FILTER_MASKS; mask++) {
      var jdbc = new Jdbc(List.of(emptyRow()));
      var request = search(QSS, mask);
      var value =
          request.query(new QuestionQueryRepository(), jdbc.connection(), ADMIN).orElseThrow();
      assertEquals(new PagedResponseData(1, 50, 0, 1, 0, 0), value.data());
      String escaped = "%é\\_\\%\\\\%";
      jdbc.assertBinds(
          Arrays.asList(
              (mask & 2) != 0 ? USERNAME : null,
              (mask & 2) != 0 ? USERNAME : null,
              (mask & 4) != 0 ? ANSWERED_STATE : null,
              (mask & 4) != 0 ? ANSWERED_STATE : null,
              (mask & 1) != 0 ? escaped : null,
              (mask & 1) != 0 ? escaped : null,
              (mask & 1) != 0 ? escaped : null,
              (mask & 8) != 0 ? FROM : null,
              (mask & 8) != 0 ? FROM : null,
              (mask & 16) != 0 ? TO : null,
              (mask & 16) != 0 ? TO : null,
              LAST_PAGE));
      assertFalse(jdbc.sql.contains("é"));
      assertFalse(jdbc.sql.contains("and owner_user_id=?"));
      assertTrue(jdbc.sql.contains("username=?"));
      assertTrue(
          jdbc.sql.contains(
              "question_body ilike ? escape '\\' or answer_body ilike ? escape '\\'"));
      pageSql(jdbc.sql, true);
      jdbc.assertReleased();
    }
  }

  @Test
  void sql003QuestionSummaryCountsCodePointsNotUtf16Units() {
    var jdbc = new Jdbc(List.of(questionRow(true)));
    var request = search(QSS, 0);
    var value = request.query(new QuestionQueryRepository(), jdbc.connection(), USER).orElseThrow();
    assertEquals(new PagedResponseData(1, 50, 1, 1, 1, 1), value.data());
    assertEquals(
        List.of(
            new QuestionSummaryRecord(
                new QuestionId(3),
                RECEIPT,
                USERNAME,
                SUMMARY,
                AnswerState.ANSWERED,
                NOW,
                Optional.of(ANSWERED))),
        value.records());
    assertDoesNotThrow(() -> request.validateResponse(value));
    jdbc.assertReleased();
  }

  @Test
  void sql004QuestionDetailBindsTargetAndOwnerAndKeepsFullText() {
    for (var actor : List.of(USER, ADMIN)) {
      for (boolean present : List.of(false, true)) {
        var jdbc = new Jdbc(present ? List.of(questionRow(actor == ADMIN)) : List.of());
        var request = detail(QSD);
        var value = request.query(new QuestionQueryRepository(), jdbc.connection(), actor);
        assertEquals(present, value.isPresent());
        jdbc.assertBinds(actor == USER ? List.of(3L, 7L) : List.of(3L));
        assertTrue(jdbc.sql.contains("where id=? and not question_deleted"));
        assertEquals(actor == USER, jdbc.sql.contains("and owner_user_id=?"));
        if (present) {
          var found = value.orElseThrow();
          assertEquals(
              new QuestionDetailResponseData(
                  new QuestionId(3),
                  RECEIPT,
                  USERNAME,
                  actor == ADMIN ? AnswerState.ANSWERED : AnswerState.UNANSWERED,
                  BODY,
                  actor == ADMIN ? Optional.of(ANSWER) : Optional.empty(),
                  NOW,
                  actor == ADMIN ? Optional.of(ANSWERED) : Optional.empty()),
              found.data());
          assertDoesNotThrow(() -> request.validateResponse(found));
        }
        jdbc.assertReleased();
      }
    }
  }

  @Test
  void sql005NotificationFiltersAlwaysBindCurrentActorIncludingAdmin() {
    for (var actor : List.of(USER, ADMIN)) {
      for (int mask = 0; mask < NOTICE_MASKS; mask++) {
        var jdbc = new Jdbc(List.of(emptyRow()));
        var request = search(NTS, mask);
        var value =
            request.query(new QuestionQueryRepository(), jdbc.connection(), actor).orElseThrow();
        assertEquals("NTSRSP01", value.layoutId().value());
        assertEquals(new PagedResponseData(1, 50, 0, 1, 0, 0), value.data());
        jdbc.assertBinds(
            Arrays.asList(
                actor == USER ? 7L : 8L,
                (mask & 1) != 0 ? COMPLETED_STATE : null,
                (mask & 1) != 0 ? COMPLETED_STATE : null,
                (mask & 2) != 0 ? FROM : null,
                (mask & 2) != 0 ? FROM : null,
                (mask & 4) != 0 ? TO : null,
                (mask & 4) != 0 ? TO : null,
                LAST_PAGE));
        assertTrue(jdbc.sql.contains("from projected where owner_user_id=?"));
        assertTrue(
            jdbc.sql.contains("case when not q.is_deleted then q.body end as question_body"));
        pageSql(jdbc.sql, false);
        assertDoesNotThrow(() -> request.validateResponse(value));
        jdbc.assertReleased();
      }
    }
  }

  @Test
  void sql006NotificationRowsPreserveDeletedLabelAndOwnerScope() {
    for (boolean deleted : List.of(false, true)) {
      var jdbc = new Jdbc(List.of(noticeRow(deleted, false)));
      var request = search(NTS, 0);
      var value =
          request.query(new QuestionQueryRepository(), jdbc.connection(), ADMIN).orElseThrow();
      assertEquals(
          List.of(
              new NotificationRecord(
                  new NotificationId(3),
                  RECEIPT,
                  NotificationType.ACCEPTED,
                  NotificationState.RECEIVED,
                  NOW,
                  NOW,
                  deleted ? "削除済み" : SUMMARY,
                  deleted)),
          value.records());
      assertEquals(8L, jdbc.parameters.get(1));
      assertDoesNotThrow(() -> request.validateResponse(value));
      jdbc.assertReleased();
    }
  }

  @Test
  void sql007NotificationDetailsPreserveOptionalStatesWithoutRevivingDeletedText() {
    for (int variant = 0; variant < 3; variant++) {
      boolean deleted = variant == 2;
      boolean completed = variant == 1;
      var jdbc = new Jdbc(List.of(noticeRow(deleted, completed)));
      var request = detail(NTD);
      var value =
          request.query(new QuestionQueryRepository(), jdbc.connection(), ADMIN).orElseThrow();
      var expected =
          new NotificationDetailResponseData(
              new NotificationId(3),
              RECEIPT,
              completed ? NotificationType.COMPLETED : NotificationType.ACCEPTED,
              completed ? NotificationState.COMPLETED : NotificationState.RECEIVED,
              NOW,
              completed ? Optional.of(NOW) : Optional.empty(),
              completed ? Optional.of(ANSWERED) : Optional.empty(),
              Optional.empty(),
              Optional.empty(),
              deleted,
              deleted ? Optional.empty() : Optional.of(BODY),
              completed ? Optional.of(ANSWER) : Optional.empty(),
              Optional.empty(),
              Optional.empty(),
              deleted ? Optional.empty() : Optional.of(new QuestionId(3)));
      assertEquals(expected, assertInstanceOf(NotificationDetailResponseData.class, value.data()));
      assertDoesNotThrow(() -> request.validateResponse(value));
      jdbc.assertBinds(List.of(3L, 8L));
      assertTrue(jdbc.sql.contains("where id=? and owner_user_id=?"));
      jdbc.assertReleased();
    }
    var absent = new Jdbc(List.of());
    assertTrue(
        detail(NTD).query(new QuestionQueryRepository(), absent.connection(), USER).isEmpty());
    absent.assertBinds(List.of(3L, 7L));
    absent.assertReleased();
  }

  @Test
  void sql008NullBoundariesAndUserUsernameGuardNeverTouchJdbc() {
    var jdbc = new Jdbc(List.of(emptyRow()));
    var repository = new QuestionQueryRepository();
    for (String layout : List.of(QSS, QSD, NTS, NTD)) {
      var request = layout.equals(QSS) || layout.equals(NTS) ? search(layout, 0) : detail(layout);
      assertThrows(NullPointerException.class, () -> request.query(null, jdbc.connection(), USER));
      assertThrows(NullPointerException.class, () -> request.query(repository, null, USER));
      assertThrows(
          NullPointerException.class, () -> request.query(repository, jdbc.connection(), null));
    }
    var failure =
        assertThrows(
            QuestionQueryException.class,
            () -> search(QSS, 2).query(repository, jdbc.connection(), USER));
    assertEquals(ResultCode.VALIDATION_ERROR, failure.resultCode());
    assertEquals(0, jdbc.connectionCalls);
    assertEquals(0, jdbc.prepares);
    assertTrue(jdbc.closed.isEmpty());
  }

  private static void pageSql(String sql, boolean question) {
    assertTrue(sql.contains("filtered as materialized"));
    assertTrue(sql.contains("totals as (select count(*) as total from filtered)"));
    assertTrue(sql.contains("greatest(1,(total+49)/50)"));
    assertTrue(sql.contains("limit 50 offset (p.effective-1)*50"));
    assertTrue(
        sql.contains(
            question ? "order by submitted_at desc,id desc" : "order by updated_at desc,id desc"));
    assertFalse(sql.contains("for update"));
  }

  private static Map<String, @Nullable Object> emptyRow() {
    var row = new HashMap<String, @Nullable Object>();
    row.put("total", 0L);
    row.put("pages", 1L);
    row.put("effective", 1L);
    row.put("id", null);
    return row;
  }

  private static Map<String, @Nullable Object> questionRow(boolean answered) {
    var row = emptyRow();
    row.put("total", 1L);
    row.put("id", 3L);
    row.put("receipt_id", RECEIPT);
    row.put("username", USERNAME);
    row.put("question_body", BODY);
    row.put("answer_state", answered ? ANSWERED_STATE : "UNANSWERED");
    row.put("answer_body", answered ? ANSWER : null);
    row.put("submitted_at", OffsetDateTime.parse(ROW_SUBMITTED_AT));
    row.put("answered_at", answered ? OffsetDateTime.parse("2026-10-01T00:00:01.123456Z") : null);
    return row;
  }

  private static Map<String, @Nullable Object> noticeRow(boolean deleted, boolean completed) {
    var row = emptyRow();
    row.put("total", 1L);
    row.put("id", 3L);
    row.put("receipt_id", RECEIPT);
    row.put("notification_type", completed ? COMPLETED_STATE : "ACCEPTED");
    row.put("state", completed ? COMPLETED_STATE : RECEIVED_STATE);
    row.put("question_deleted", deleted);
    row.put("question_body", deleted ? null : BODY);
    row.put("answer_body", completed ? ANSWER : null);
    row.put("question_id", deleted ? null : 3L);
    row.put("submitted_at", OffsetDateTime.parse(ROW_SUBMITTED_AT));
    row.put("updated_at", OffsetDateTime.parse(ROW_SUBMITTED_AT));
    row.put("started_at", completed ? OffsetDateTime.parse(ROW_SUBMITTED_AT) : null);
    row.put("completed_at", completed ? OffsetDateTime.parse("2026-10-01T00:00:01.123456Z") : null);
    row.put("error_at", null);
    row.put("cancelled_at", null);
    row.put("error_code", null);
    row.put("error_message", null);
    return row;
  }

  @FunctionalInterface
  private interface Call {
    @Nullable Object invoke(String method, Object[] arguments);
  }

  private static <T> T proxy(Class<T> type, Call call) {
    return type.cast(
        Proxy.newProxyInstance(
            QuestionSqlContractTest.class.getClassLoader(),
            new Class<?>[] {type},
            (self, method, args) ->
                call.invoke(method.getName(), args == null ? new Object[0] : args)));
  }

  private static final class Jdbc {
    private final List<Map<String, @Nullable Object>> rows;
    private final Map<Integer, @Nullable Object> parameters = new HashMap<>();
    private final List<String> closed = new ArrayList<>();
    private String sql = "";
    private int connectionCalls;
    private int prepares;
    private int queries;
    private int cursor = -1;

    Jdbc(List<Map<String, @Nullable Object>> rows) {
      this.rows = List.copyOf(rows);
    }

    Connection connection() {
      return proxy(
          Connection.class,
          (method, args) -> {
            connectionCalls++;
            return switch (method) {
              case "getAutoCommit" -> false;
              case "isReadOnly" -> true;
              case "prepareStatement" -> {
                prepares++;
                assertEquals(1, prepares);
                sql = ((String) args[0]).replaceAll("\\s+", " ");
                yield statement();
              }
              default ->
                  throw new AssertionError("borrowed connection action not permitted: " + method);
            };
          });
    }

    private PreparedStatement statement() {
      return proxy(
          PreparedStatement.class,
          (method, args) ->
              switch (method) {
                case "setObject", "setInt" -> {
                  int index = (Integer) args[0];
                  assertFalse(parameters.containsKey(index));
                  parameters.put(index, args[1]);
                  yield null;
                }
                case "executeQuery" -> {
                  queries++;
                  assertEquals(1, queries);
                  yield results();
                }
                case "close" -> {
                  closed.add("PS");
                  yield null;
                }
                default -> throw new AssertionError("unexpected statement method: " + method);
              });
    }

    private ResultSet results() {
      return proxy(
          ResultSet.class,
          (method, args) ->
              switch (method) {
                case "next" -> {
                  cursor++;
                  yield cursor < rows.size();
                }
                case "getString" -> (String) value((String) args[0]);
                case "getObject" -> {
                  Object value = value((String) args[0]);
                  if (args.length == TYPED_ARGUMENTS && value != null)
                    assertTrue(((Class<?>) args[1]).isInstance(value));
                  yield value;
                }
                case "close" -> {
                  closed.add("RS");
                  yield null;
                }
                default -> throw new AssertionError("unexpected result method: " + method);
              });
    }

    private @Nullable Object value(String name) {
      assertTrue(cursor >= 0 && cursor < rows.size());
      var row = rows.get(cursor);
      assertTrue(row.containsKey(name), "explicit synthetic column required");
      return row.get(name);
    }

    void assertBinds(List<? extends @Nullable Object> expected) {
      assertEquals(expected.size(), parameters.size());
      for (int i = 0; i < expected.size(); i++)
        assertEquals(expected.get(i), parameters.get(i + 1));
    }

    void assertReleased() {
      assertEquals(1, prepares);
      assertEquals(1, queries);
      assertEquals(3, connectionCalls);
      assertEquals(List.of("RS", "PS"), closed);
    }
  }

  private static QuestionQueryRequest search(String layout, int mask) {
    boolean question = layout.equals(QSS);
    byte[] bytes = new byte[question ? 384 : 64];
    Arrays.fill(bytes, (byte) 32);
    if (question) {
      if ((mask & 1) != 0) put(bytes, 0, "é_%\\");
      if ((mask & 2) != 0) put(bytes, 256, USERNAME);
      if ((mask & 4) != 0) put(bytes, 320, ANSWERED_STATE);
      if ((mask & 8) != 0) put(bytes, 332, "20261001090000123");
      if ((mask & 16) != 0) put(bytes, 349, "20261001090001123");
    } else {
      if ((mask & 1) != 0) put(bytes, 0, COMPLETED_STATE);
      if ((mask & 2) != 0) put(bytes, 12, "20261001090000123");
      if ((mask & 4) != 0) put(bytes, 29, "20261001090001123");
    }
    put(bytes, question ? 366 : 46, PAGE_TEXT);
    return decode(layout, bytes);
  }

  private static QuestionQueryRequest detail(String layout) {
    return decode(layout, "000000000003".getBytes(StandardCharsets.US_ASCII));
  }

  private static QuestionQueryRequest decode(String layout, byte[] bytes) {
    UUID id = new UUID(14003, 1);
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId(layout),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            id,
            id,
            NOW,
            Optional.of(AuthenticationContext.of("b".repeat(64))),
            256,
            bytes.length,
            0,
            0,
            256 + bytes.length,
            Optional.empty());
    return QuestionQueryRequest.decode(
        new WireMessage<>(header, new FixedPayload(bytes, 0, List.of())));
  }

  private static void put(byte[] bytes, int offset, String value) {
    byte[] text = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(text, 0, bytes, offset, text.length);
  }
}

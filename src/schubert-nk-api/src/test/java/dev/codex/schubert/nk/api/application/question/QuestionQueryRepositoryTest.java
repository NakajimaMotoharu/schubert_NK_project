package dev.codex.schubert.nk.api.application.question;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.persistence.QuestionQueryException;
import dev.codex.schubert.nk.api.persistence.QuestionQueryRepository;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationRecord;
import dev.codex.schubert.nk.protocol.layout.question.NotificationSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSummaryRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.AnswerState;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationId;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationState;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationType;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-QRY001..004/NTF001..004; literal SQL fixtures, typed expected values, no expected codec. */
final class QuestionQueryRepositoryTest {
  private static final String FIXTURE_SELECT_COUNT_FROM_SCHUBERT_QUESTIONS_9AA9E6E7 =
      "select count(*) from schubert.questions";
  private static final String FIXTURE_EXECUTE_7FB37A54 = "execute";
  private static final String FIXTURE_CLOSE_97959247 = "close";
  @TempDir static Path root;
  static ApiLogDatabaseFixture db;
  static final AuthenticatedActor USER = new AuthenticatedActor(1, "u1", Role.USER);
  static final AuthenticatedActor ADMIN = new AuthenticatedActor(1, "u1", Role.ADMIN);
  static final AuthenticatedActor OTHER = new AuthenticatedActor(2, "u2", Role.USER);
  final QuestionQueryRepository repository = new QuestionQueryRepository();

  @BeforeAll
  static void start() throws Exception {
    db = new ApiLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @Test
  void qry001ScopeSortPagingAndLiteralKeywordAreIndependent() throws Exception {
    try (var f = fixture();
        var c = read()) {
      assertEquals(53, f.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_QUESTIONS_9AA9E6E7));
      var user = repository.questionSearch(c, USER, questions(1));
      assertEquals(new PagedResponseData(1, 50, 50, 1, 1, 50), user.data());
      assertEquals(51, ((QuestionSummaryRecord) user.records().getFirst()).questionId().value());
      assertEquals(1, ((QuestionSummaryRecord) user.records().getLast()).questionId().value());
      var admin = repository.questionSearch(c, ADMIN, questions(999999));
      assertEquals(new PagedResponseData(2, 50, 52, 2, 51, 52), admin.data());
      assertEquals(
          List.of(2L, 1L),
          admin.records().stream()
              .map(v -> ((QuestionSummaryRecord) v).questionId().value())
              .toList());
      assertEquals(2, repository.questionSearch(c, OTHER, questions(1)).records().size());
      var filter =
          new QuestionSearchRequestData(
              Optional.empty(),
              Optional.of("u2"),
              Optional.empty(),
              Optional.empty(),
              Optional.empty(),
              1,
              50);
      assertEquals(2, repository.questionSearch(c, ADMIN, filter).records().size());
      assertEquals(
          ResultCode.VALIDATION_ERROR,
          assertThrows(
                  QuestionQueryException.class, () -> repository.questionSearch(c, USER, filter))
              .resultCode());
      for (String literal : List.of("%", "_", "\\")) {
        var query =
            new QuestionSearchRequestData(
                Optional.of(literal),
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                1,
                50);
        var actual = repository.questionSearch(c, USER, query);
        assertEquals(1, actual.records().size());
        assertEquals(3, ((QuestionSummaryRecord) actual.records().getFirst()).questionId().value());
      }
      var missing =
          new QuestionSearchRequestData(
              Optional.of("no-such-literal"),
              Optional.empty(),
              Optional.empty(),
              Optional.empty(),
              Optional.empty(),
              1,
              50);
      assertEquals(
          new PagedResponseData(1, 50, 0, 1, 0, 0),
          repository.questionSearch(c, USER, missing).data());
      assertFalse(c.isClosed());
      c.rollback();
    }
  }

  @Test
  void qry002StatesUnicodeSnippetAndUtcMicrosecondProjectionNeverUpdateDb() throws Exception {
    try (var f = fixture();
        var c = read()) {
      assertEquals(53, f.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_QUESTIONS_9AA9E6E7));
      for (AnswerState state : AnswerState.values()) {
        var query =
            new QuestionSearchRequestData(
                Optional.empty(),
                Optional.empty(),
                Optional.of(state),
                Optional.empty(),
                Optional.empty(),
                1,
                50);
        var actual = repository.questionSearch(c, USER, query);
        assertEquals(state == AnswerState.UNANSWERED ? 48 : 1, actual.records().size());
        for (var row : actual.records())
          assertEquals(state, ((QuestionSummaryRecord) row).answerState());
      }
      var detail =
          (QuestionDetailResponseData)
              repository
                  .questionDetail(c, USER, new QuestionDetailRequestData(new QuestionId(3)))
                  .orElseThrow()
                  .data();
      assertEquals(AnswerState.ANSWERED, detail.answerState());
      assertEquals(Optional.of(""), detail.answerText());
      assertEquals(Instant.parse("2026-10-01T00:00:00.125Z"), detail.answeredAt().orElseThrow());
      var rows =
          repository.questionSearch(
              c,
              USER,
              new QuestionSearchRequestData(
                  Optional.of("alpha"),
                  Optional.empty(),
                  Optional.empty(),
                  Optional.empty(),
                  Optional.empty(),
                  1,
                  50));
      assertEquals(
          "😀".repeat(100), ((QuestionSummaryRecord) rows.records().getFirst()).questionSummary());
      assertEquals(
          "2026-10-01 00:00:00.125456",
          f.text(
              "select to_char(answered_at at time zone 'UTC','YYYY-MM-DD HH24:MI:SS.US') from schubert.answers where question_id=3"));
      // BUG458/YKT348: two independently configured sessions, same UTC/ms wire and DB microseconds.
      for (String zone : List.of("UTC", "Asia/Tokyo")) {
        try (var setting = c.prepareStatement("select set_config('TimeZone',?,true)")) {
          setting.setString(1, zone);
          try (var row = setting.executeQuery()) {
            assertTrue(row.next());
            assertEquals(zone, row.getString(1));
          }
        }
        var actual =
            (QuestionDetailResponseData)
                repository
                    .questionDetail(c, USER, new QuestionDetailRequestData(new QuestionId(3)))
                    .orElseThrow()
                    .data();
        assertEquals(Instant.parse("2026-10-01T00:00:00.125Z"), actual.answeredAt().orElseThrow());
        try (var statement =
                c.prepareStatement(
                    "select to_char(answered_at at time zone 'UTC','YYYY-MM-DD HH24:MI:SS.US') from schubert.answers where question_id=3");
            var row = statement.executeQuery()) {
          assertTrue(row.next());
          assertEquals("2026-10-01 00:00:00.125456", row.getString(1));
        }
      }
      var date =
          new QuestionSearchRequestData(
              Optional.empty(),
              Optional.empty(),
              Optional.empty(),
              Optional.of(Instant.parse("2026-10-01T00:00:00.123Z")),
              Optional.of(Instant.parse("2026-10-02T00:00:00Z")),
              1,
              50);
      assertEquals(50, repository.questionSearch(c, USER, date).records().size());
      c.rollback();
    }
  }

  @Test
  void qry004DetailOwnerAdminDeletedAndAbsenceNeverLeak() throws Exception {
    try (var f = fixture();
        var c = read()) {
      assertEquals(53, f.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_QUESTIONS_9AA9E6E7));
      assertTrue(
          repository
              .questionDetail(c, USER, new QuestionDetailRequestData(new QuestionId(52)))
              .isEmpty());
      assertTrue(
          repository
              .questionDetail(c, ADMIN, new QuestionDetailRequestData(new QuestionId(52)))
              .isPresent());
      assertTrue(
          repository
              .questionDetail(c, ADMIN, new QuestionDetailRequestData(new QuestionId(5)))
              .isEmpty());
      assertTrue(
          repository
              .questionDetail(c, USER, new QuestionDetailRequestData(new QuestionId(999)))
              .isEmpty());
      var error =
          (QuestionDetailResponseData)
              repository
                  .questionDetail(c, USER, new QuestionDetailRequestData(new QuestionId(4)))
                  .orElseThrow()
                  .data();
      assertEquals(AnswerState.ERROR, error.answerState());
      assertTrue(error.answerText().isEmpty());
      assertTrue(error.answeredAt().isEmpty());
      c.rollback();
    }
  }

  @Test
  void ntf001AdminStillOnlySelfAndUpdatedAtIdOrderUsesFixedFifty() throws Exception {
    try (var f = fixture();
        var c = read()) {
      assertEquals(53, f.scalar("select count(*) from schubert.notifications"));
      var actual = repository.notificationSearch(c, ADMIN, notices(1));
      assertEquals(new PagedResponseData(1, 50, 51, 2, 1, 50), actual.data());
      assertEquals(
          List.of(4L, 3L, 2L, 1L, 51L),
          actual.records().subList(0, 5).stream()
              .map(v -> ((NotificationRecord) v).notificationId().value())
              .toList());
      var last = repository.notificationSearch(c, USER, notices(2));
      assertEquals(new PagedResponseData(2, 50, 51, 2, 51, 51), last.data());
      assertEquals("削除済み", ((NotificationRecord) last.records().getFirst()).questionSummary());
      assertTrue(((NotificationRecord) last.records().getFirst()).questionDeleted());
      for (NotificationType type : NotificationType.values()) {
        var query =
            new NotificationSearchRequestData(
                Optional.of(type),
                Optional.of(Instant.parse("2026-09-30T00:00:00Z")),
                Optional.of(Instant.parse("2026-10-02T00:00:00Z")),
                1,
                50);
        var result = repository.notificationSearch(c, ADMIN, query);
        assertEquals(type == NotificationType.ACCEPTED ? 49 : 1, result.records().size());
        for (var record : result.records())
          assertEquals(type, ((NotificationRecord) record).notificationType());
      }
      assertEquals(2, repository.notificationSearch(c, OTHER, notices(1)).records().size());
      c.rollback();
    }
  }

  @Test
  void ntf003AllFiveStatesAndDeletedProjectionPreserveNotificationRows() throws Exception {
    try (var f = fixture();
        var c = read()) {
      assertEquals(53, f.scalar("select count(*) from schubert.notifications"));
      assertTrue(
          repository
              .notificationDetail(
                  c, ADMIN, new NotificationDetailRequestData(new NotificationId(52)))
              .isEmpty());
      assertTrue(
          repository
              .notificationDetail(
                  c, USER, new NotificationDetailRequestData(new NotificationId(999)))
              .isEmpty());
      for (long id = 1; id <= 5; id++) {
        var d =
            (NotificationDetailResponseData)
                repository
                    .notificationDetail(
                        c, USER, new NotificationDetailRequestData(new NotificationId(id)))
                    .orElseThrow()
                    .data();
        assertEquals(
            List.of(
                    NotificationState.CANCELLED,
                    NotificationState.PROCESSING,
                    NotificationState.COMPLETED,
                    NotificationState.ERROR,
                    NotificationState.RECEIVED)
                .get((int) id - 1),
            d.internalState());
        assertEquals(id == 5, d.questionDeleted());
        assertEquals(id == 5, d.questionText().isEmpty());
        assertEquals(id == 5, d.questionId().isEmpty());
        assertEquals(id == 4, d.errorCode().isPresent());
        if (id == 3) assertEquals(Optional.of(""), d.answerText());
      }
      assertEquals(53, f.scalar("select count(*) from schubert.notifications"));
      c.rollback();
    }
  }

  @Test
  void qry003Ntf002NullInvalidPageAndNonReadTransactionsAreRejected() throws Exception {
    try (var f = fixture();
        var c = db.api()) {
      assertEquals(53, f.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_QUESTIONS_9AA9E6E7));
      assertThrows(
          NullPointerException.class, () -> repository.questionSearch(null, USER, questions(1)));
      assertThrows(
          NullPointerException.class, () -> repository.notificationSearch(c, null, notices(1)));
      assertThrows(NullPointerException.class, () -> repository.questionDetail(c, USER, null));
      assertThrows(NullPointerException.class, () -> repository.notificationDetail(c, USER, null));
      assertThrows(
          IllegalArgumentException.class, () -> repository.questionSearch(c, USER, questions(0)));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              repository.notificationSearch(
                  c,
                  USER,
                  new NotificationSearchRequestData(
                      Optional.empty(), Optional.empty(), Optional.empty(), 1, 49)));
      assertEquals(
          ResultCode.TEMPORARY_FAILURE,
          assertThrows(
                  QuestionQueryException.class,
                  () -> repository.questionSearch(c, USER, questions(1)))
              .resultCode());
      c.setAutoCommit(false);
      assertThrows(
          QuestionQueryException.class,
          () ->
              repository.notificationDetail(
                  c, USER, new NotificationDetailRequestData(new NotificationId(1))));
      c.rollback();
    }
  }

  @Test
  void qry005DriverProjectionShapeAndCloseFaultsCannotProduceSuccess() throws Exception {
    try (var f = fixture();
        var c = read()) {
      assertEquals(53, f.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_QUESTIONS_9AA9E6E7));
      for (String fault :
          List.of(
              "total-negative",
              "pages-zero",
              "effective-zero",
              "total-change",
              "pages-change",
              "effective-change",
              "short-rows",
              "question-body-null",
              "state-unknown",
              FIXTURE_EXECUTE_7FB37A54,
              FIXTURE_CLOSE_97959247)) {
        var failure =
            assertThrows(
                QuestionQueryException.class,
                () -> repository.questionSearch(fault(c, fault), USER, questions(1)),
                fault);
        assertEquals(ResultCode.TEMPORARY_FAILURE, failure.resultCode(), fault);
        assertEquals("question query is unavailable", failure.getMessage());
        assertNull(failure.getCause());
      }
      for (String fault : List.of("total-cap", "cap-close"))
        assertEquals(
            fault.equals("total-cap") ? ResultCode.RESOURCE_LIMIT : ResultCode.TEMPORARY_FAILURE,
            assertThrows(
                    QuestionQueryException.class,
                    () -> repository.questionSearch(fault(c, fault), USER, questions(1)))
                .resultCode());
      for (String fault :
          List.of(
              "extra-detail",
              "question-body-null",
              "state-unknown",
              FIXTURE_EXECUTE_7FB37A54,
              FIXTURE_CLOSE_97959247))
        assertThrows(
            QuestionQueryException.class,
            () ->
                repository.questionDetail(
                    fault(c, fault), USER, new QuestionDetailRequestData(new QuestionId(3))));
      for (String fault :
          List.of(
              "type-unknown", "error-unknown", FIXTURE_EXECUTE_7FB37A54, FIXTURE_CLOSE_97959247))
        assertThrows(
            QuestionQueryException.class,
            () ->
                repository.notificationDetail(
                    fault(c, fault),
                    USER,
                    new NotificationDetailRequestData(new NotificationId(4))));
      c.rollback();
    }
  }

  static QuestionSearchRequestData questions(int page) {
    return new QuestionSearchRequestData(
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        page,
        50);
  }

  @Test
  void qry027UserAndAdminHaveSeparateSqlQueryIdsWithoutRoleOrPredicate() throws Exception {
    try (var f = fixture();
        var c = read()) {
      assertEquals(53, f.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_QUESTIONS_9AA9E6E7));
      var sql = new ArrayList<String>();
      var observed =
          (Connection)
              Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (p, m, a) -> {
                    if (m.getName().equals("prepareStatement")) sql.add(a[0].toString());
                    return QuestionSubmissionServiceTest.invoke(c, m, a);
                  });
      for (boolean detail : List.of(false, true)) {
        sql.clear();
        for (var actor : List.of(USER, ADMIN)) {
          if (detail)
            repository.questionDetail(
                observed, actor, new QuestionDetailRequestData(new QuestionId(3)));
          else repository.questionSearch(observed, actor, questions(1));
        }
        assertEquals(2, sql.size());
        assertNotEquals(sql.get(0), sql.get(1));
        assertTrue(sql.get(0).contains("and owner_user_id=?"));
        assertFalse(sql.get(1).contains("owner_user_id=?"));
        for (String statement : sql) assertFalse(statement.contains("? or owner_user_id"));
      }
      c.rollback();
    }
  }

  @Test
  void qry011AllDecodedRoutesBindOriginalValuesAndBorrowReadOnlyConnection() throws Exception {
    try (var f = fixture();
        var c = read()) {
      assertEquals(53, f.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_QUESTIONS_9AA9E6E7));
      for (String layout : List.of("QSSREQ01", "QSDREQ01", "NTSREQ01", "NTDREQ01")) {
        byte[] bytes = QuestionQueryRequestTest.data(layout, false);
        if (layout.contains("DREQ")) QuestionQueryRequestTest.put(bytes, 0, "000000000003");
        var request = QuestionQueryRequest.decode(QuestionQueryRequestTest.message(layout, bytes));
        var actual = request.query(repository, c, USER).orElseThrow();
        request.validateResponse(actual);
        assertEquals(layout.substring(0, 3) + "RSP01", actual.layoutId().value());
        if (layout.equals("QSSREQ01"))
          assertEquals(new PagedResponseData(1, 50, 50, 1, 1, 50), actual.data());
        if (layout.equals("NTSREQ01"))
          assertEquals(new PagedResponseData(2, 50, 51, 2, 51, 51), actual.data());
        if (request.detailRequest()) {
          QuestionQueryRequestTest.put(bytes, 0, "000000000004");
          var different =
              QuestionQueryRequest.decode(QuestionQueryRequestTest.message(layout, bytes));
          assertThrows(IllegalArgumentException.class, () -> different.validateResponse(actual));
        }
        assertFalse(c.isClosed());
        assertTrue(c.isReadOnly());
        assertFalse(c.getAutoCommit());
        assertThrows(NullPointerException.class, () -> request.query(repository, null, USER));
        assertThrows(NullPointerException.class, () -> request.query(repository, c, null));
      }
      assertEquals(0, f.scalar("select count(*) from schubert.request_inbox"));
      c.rollback();
    }
  }

  static NotificationSearchRequestData notices(int page) {
    return new NotificationSearchRequestData(
        Optional.empty(), Optional.empty(), Optional.empty(), page, 50);
  }

  static Connection read() throws SQLException {
    var c = db.api();
    c.setAutoCommit(false);
    c.setReadOnly(true);
    return c;
  }

  static QuestionSubmissionServiceTest.Fixture fixture() throws Exception {
    return fixture(db);
  }

  static QuestionSubmissionServiceTest.Fixture fixture(ApiLogDatabaseFixture database)
      throws Exception {
    var f = new QuestionSubmissionServiceTest.Fixture(database);
    f.sql(
        """
      insert into schubert.questions(id,receipt_id,owner_user_id,body,operation_token,submitted_at,is_deleted,deleted_at,deleted_by,version)
      select i,lpad(i::text,26,'0'),case when i<=51 then 1 else 2 end,
        case when i=3 then repeat('😀',101)||'alpha%_\\' else 'question'||i end,
        ('00000000-0000-4000-8000-'||lpad(i::text,12,'0'))::uuid,'2026-10-01T00:00:00.123456Z',
        i=5,case when i=5 then '2026-10-01T00:00:00.130456Z'::timestamptz end,case when i=5 then 1 end,case when i=5 then 1 else 0 end
        from generate_series(1,53) i
      """);
    f.sql(
        """
      insert into schubert.async_jobs(id,question_id,owner_user_id,state,message_id,correlation_id,processing_message_id,received_at,state_changed_at,
        started_at,completed_at,error_at,cancelled_at,last_error_code,last_error_message,version)
      select i,i,case when i<=51 then 1 else 2 end,
        case i when 1 then 'CANCELLED' when 2 then 'PROCESSING' when 3 then 'COMPLETED' when 4 then 'ERROR' else 'RECEIVED' end,
        ('10000000-0000-4000-8000-'||lpad(i::text,12,'0'))::uuid,
        ('20000000-0000-4000-8000-'||lpad(i::text,12,'0'))::uuid,
        case when i between 2 and 4 then ('10000000-0000-4000-8000-'||lpad(i::text,12,'0'))::uuid end,
        '2026-10-01T00:00:00.123456Z',
        case when i between 3 and 4 then '2026-10-01T00:00:00.125456Z'::timestamptz when i between 1 and 2 then '2026-10-01T00:00:00.124456Z'::timestamptz else '2026-10-01T00:00:00.123456Z'::timestamptz end,
        case when i between 2 and 4 then '2026-10-01T00:00:00.124456Z'::timestamptz end,
        case when i=3 then '2026-10-01T00:00:00.125456Z'::timestamptz end,
        case when i=4 then '2026-10-01T00:00:00.125456Z'::timestamptz end,
        case when i=1 then '2026-10-01T00:00:00.124456Z'::timestamptz end,
        case when i=4 then 'PROCESS_FAILED' end,case when i=4 then 'public synthetic failure' end,case when i<=4 then 1 else 0 end
        from generate_series(1,53) i
      """);
    f.sql(
        "insert into schubert.answers(question_id,body,answered_at,provider_type,created_at,updated_at) values(3,'','2026-10-01T00:00:00.125456Z','STUB','2026-10-01T00:00:00.125456Z','2026-10-01T00:00:00.125456Z')");
    f.sql(
        """
      insert into schubert.notifications(id,job_id,question_id,owner_user_id,notification_type,state,accepted_at,state_changed_at,error_code,error_message,created_at,updated_at)
      select id,id,question_id,owner_user_id,case when state='COMPLETED' then 'COMPLETED' when state='ERROR' then 'ERROR' else 'ACCEPTED' end,
        state,received_at,state_changed_at,last_error_code,last_error_message,received_at,state_changed_at from schubert.async_jobs
      """);
    return f;
  }

  static Connection fault(Connection c, String fault) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (p, m, a) -> {
              Object result = QuestionSubmissionServiceTest.invoke(c, m, a);
              if (!m.getName().equals("prepareStatement")) return result;
              AtomicInteger next = new AtomicInteger();
              var calls = new HashMap<String, Integer>();
              return Proxy.newProxyInstance(
                  PreparedStatement.class.getClassLoader(),
                  new Class<?>[] {PreparedStatement.class},
                  (sp, sm, sa) -> {
                    if (sm.getName().equals("executeQuery")
                        && fault.equals(FIXTURE_EXECUTE_7FB37A54))
                      throw new SQLException("private-diagnostic");
                    Object rows = QuestionSubmissionServiceTest.invoke(result, sm, sa);
                    if (sm.getName().equals(FIXTURE_CLOSE_97959247)
                        && (fault.equals(FIXTURE_CLOSE_97959247) || fault.equals("cap-close")))
                      throw new SQLException("private-close");
                    if (!sm.getName().equals("executeQuery")) return rows;
                    return Proxy.newProxyInstance(
                        ResultSet.class.getClassLoader(),
                        new Class<?>[] {ResultSet.class},
                        (rp, rm, ra) -> {
                          Object value = QuestionSubmissionServiceTest.invoke(rows, rm, ra);
                          if (rm.getName().equals("next")) {
                            int number = next.incrementAndGet();
                            if (fault.equals("short-rows") && number > 1) return false;
                            if (fault.equals("extra-detail") && number == 2) return true;
                          }
                          if (rm.getName().equals("getObject")) {
                            String name = (String) ra[0];
                            int call = calls.merge(name, 1, Integer::sum);
                            if (name.equals("total")) {
                              if (fault.equals("total-cap") || fault.equals("cap-close"))
                                return 49_999_951L;
                              if (fault.equals("total-negative")) return -1L;
                              if (fault.equals("total-change") && call > 1) return 49L;
                            }
                            if (name.equals("pages")
                                && (fault.equals("pages-zero")
                                    || (fault.equals("pages-change") && call > 1))) return 0L;
                            if (name.equals("effective")
                                && (fault.equals("effective-zero")
                                    || (fault.equals("effective-change") && call > 1))) return 0L;
                          }
                          if (rm.getName().equals("getString")) {
                            String name = (String) ra[0];
                            if (name.equals("question_body") && fault.equals("question-body-null"))
                              return null;
                            if (name.equals("answer_state") && fault.equals("state-unknown"))
                              return "UNKNOWN";
                            if (name.equals("notification_type") && fault.equals("type-unknown"))
                              return "UNKNOWN";
                            if (name.equals("error_code") && fault.equals("error-unknown"))
                              return "UNKNOWN";
                          }
                          return value;
                        });
                  });
            });
  }
}

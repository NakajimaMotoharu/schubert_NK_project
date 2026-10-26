package dev.codex.schubert.nk.api.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.FieldEncodingException;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationId;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** NK-QRY-001/P01401; QRY007; SS312/323/332/354. No JDBC method may execute. */
final class QuestionQueryPreSqlBoundaryTest {
  private static final String CONNECTION_FIELD = "connection";
  private static final String ACTOR_FIELD = "actor";
  private static final String REQUEST_FIELD = "request";
  private static final String ACTOR_NAME = "PublicBoundaryActor";
  private static final AuthenticatedActor ADMIN = new AuthenticatedActor(7, ACTOR_NAME, Role.ADMIN);
  private static final AuthenticatedActor USER = new AuthenticatedActor(8, ACTOR_NAME, Role.USER);

  /** PT-QRY-PRE001. */
  @Test
  void qryPre001QuestionSearchNullContractsBeforeSql() {
    var port = new NoSql();
    Connection connection = port.port();
    var repository = new QuestionQueryRepository();
    var request = questionRequest(Optional.empty());
    missing(CONNECTION_FIELD, () -> repository.questionSearch(null, ADMIN, request));
    missing(ACTOR_FIELD, () -> repository.questionSearch(connection, null, request));
    missing(REQUEST_FIELD, () -> repository.questionSearch(connection, ADMIN, null));
    port.untouched();
  }

  /** PT-QRY-PRE002. */
  @Test
  void qryPre002NotificationSearchNullContractsBeforeSql() {
    var port = new NoSql();
    Connection connection = port.port();
    var repository = new QuestionQueryRepository();
    var request =
        new NotificationSearchRequestData(
            Optional.empty(), Optional.empty(), Optional.empty(), 1, 50);
    missing(CONNECTION_FIELD, () -> repository.notificationSearch(null, ADMIN, request));
    missing(ACTOR_FIELD, () -> repository.notificationSearch(connection, null, request));
    missing(REQUEST_FIELD, () -> repository.notificationSearch(connection, ADMIN, null));
    port.untouched();
  }

  /** PT-QRY-PRE003. */
  @Test
  void qryPre003QuestionDetailNullContractsBeforeSql() {
    var port = new NoSql();
    Connection connection = port.port();
    var repository = new QuestionQueryRepository();
    var request = new QuestionDetailRequestData(new QuestionId(9));
    missing(CONNECTION_FIELD, () -> repository.questionDetail(null, ADMIN, request));
    missing(ACTOR_FIELD, () -> repository.questionDetail(connection, null, request));
    missing(REQUEST_FIELD, () -> repository.questionDetail(connection, ADMIN, null));
    port.untouched();
  }

  /** PT-QRY-PRE004. */
  @Test
  void qryPre004NotificationDetailNullContractsBeforeSql() {
    var port = new NoSql();
    Connection connection = port.port();
    var repository = new QuestionQueryRepository();
    var request = new NotificationDetailRequestData(new NotificationId(9));
    missing(CONNECTION_FIELD, () -> repository.notificationDetail(null, ADMIN, request));
    missing(ACTOR_FIELD, () -> repository.notificationDetail(connection, null, request));
    missing(REQUEST_FIELD, () -> repository.notificationDetail(connection, ADMIN, null));
    port.untouched();
  }

  /** PT-QRY-PRE005: USER may not select another username, before any SQL. */
  @Test
  void qryPre005UserUsernameFilterDeniedBeforeSql() {
    var port = new NoSql();
    Connection connection = port.port();
    var request = questionRequest(Optional.of("other"));
    var failure =
        assertThrows(
            QuestionQueryException.class,
            () -> new QuestionQueryRepository().questionSearch(connection, USER, request));
    assertEquals(ResultCode.VALIDATION_ERROR, failure.resultCode());
    assertEquals("question query is unavailable", failure.getMessage());
    assertNull(failure.getCause());
    port.untouched();
  }

  /** PT-QRY-PRE006: X64 literal boundary, not a constructor rejection. */
  @Test
  void qryPre006OversizeUsernameRejectedBeforeSql() {
    var port = new NoSql();
    Connection connection = port.port();
    var request = questionRequest(Optional.of("x".repeat(65)));
    assertThrows(
        FieldEncodingException.class,
        () -> new QuestionQueryRepository().questionSearch(connection, ADMIN, request));
    port.untouched();
  }

  private static QuestionSearchRequestData questionRequest(Optional<String> username) {
    return new QuestionSearchRequestData(
        Optional.empty(), username, Optional.empty(), Optional.empty(), Optional.empty(), 1, 50);
  }

  private static void missing(String field, Executable operation) {
    assertEquals(field, assertThrows(NullPointerException.class, operation).getMessage());
  }

  private static final class NoSql {
    private final AtomicInteger calls = new AtomicInteger();

    Connection port() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, arguments) -> {
                calls.incrementAndGet();
                throw new AssertionError("unexpected JDBC access");
              });
    }

    void untouched() {
      assertEquals(0, calls.get());
    }
  }
}

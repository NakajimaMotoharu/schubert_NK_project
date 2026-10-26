package dev.codex.schubert.nk.api.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.api.security.AuthorizationException;
import dev.codex.schubert.nk.protocol.codec.FieldEncodingException;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.log.LogSearchRequestData;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** NK-ADM-001/P01004; ADM083; SS312/314/323/332/354. No JDBC method may execute. */
final class LogQueryPreSqlBoundaryTest {
  private static final String ACTOR_NAME = "PublicBoundaryActor";
  private static final AuthenticatedActor ADMIN = new AuthenticatedActor(7, ACTOR_NAME, Role.ADMIN);
  private static final AuthenticatedActor USER = new AuthenticatedActor(8, ACTOR_NAME, Role.USER);

  /** PT-LOG-PRE001. */
  @Test
  void logPre001NullContractsBeforeSql() {
    var port = new NoSql();
    Connection connection = port.port();
    var repository = new LogQueryRepository();
    var request = request(Optional.empty());
    missing("connection", () -> repository.search(null, ADMIN, request));
    missing("actor", () -> repository.search(connection, null, request));
    missing("request", () -> repository.search(connection, ADMIN, null));
    port.untouched();
  }

  /** PT-LOG-PRE002. */
  @Test
  void logPre002UserCannotQueryBeforeSql() {
    var port = new NoSql();
    Connection connection = port.port();
    var failure =
        assertThrows(
            AuthorizationException.class,
            () -> new LogQueryRepository().search(connection, USER, request(Optional.empty())));
    assertEquals(ResultCode.FORBIDDEN, failure.resultCode());
    assertEquals("operation is not available", failure.getMessage());
    assertNull(failure.getCause());
    port.untouched();
  }

  /** PT-LOG-PRE003: X256 literal boundary, not a constructor rejection. */
  @Test
  void logPre003OversizeKeywordRejectedBeforeSql() {
    var port = new NoSql();
    Connection connection = port.port();
    var request = request(Optional.of("x".repeat(257)));
    assertThrows(
        FieldEncodingException.class,
        () -> new LogQueryRepository().search(connection, ADMIN, request));
    port.untouched();
  }

  private static LogSearchRequestData request(Optional<String> keyword) {
    return new LogSearchRequestData(
        keyword,
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        1,
        100);
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

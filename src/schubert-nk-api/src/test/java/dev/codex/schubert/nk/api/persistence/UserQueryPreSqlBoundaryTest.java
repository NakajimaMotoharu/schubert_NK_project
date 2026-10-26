package dev.codex.schubert.nk.api.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.api.security.AuthorizationException;
import dev.codex.schubert.nk.protocol.codec.FieldEncodingException;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.admin.UserDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.time.Instant;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** NK-ADM-001/P01001; ADM083; SS312/314/323/332/354. No JDBC method may execute. */
final class UserQueryPreSqlBoundaryTest {
  private static final String ACTOR_NAME = "PublicBoundaryActor";
  private static final AuthenticatedActor ADMIN = new AuthenticatedActor(7, ACTOR_NAME, Role.ADMIN);
  private static final AuthenticatedActor USER = new AuthenticatedActor(8, ACTOR_NAME, Role.USER);
  private static final Instant NOW = Instant.parse("2026-10-26T00:00:00Z");

  /** PT-ADM-PRE001. */
  @Test
  void userPre001SearchNullContractsBeforeSql() {
    var port = new NoSql();
    Connection connection = port.port();
    var repository = new UserQueryRepository();
    var request = searchRequest(Optional.empty());
    missing("connection", () -> repository.search(null, ADMIN, request, NOW));
    missing("actor", () -> repository.search(connection, null, request, NOW));
    missing("now", () -> repository.search(connection, ADMIN, request, null));
    missing("request", () -> repository.search(connection, ADMIN, null, NOW));
    port.untouched();
  }

  /** PT-ADM-PRE002. */
  @Test
  void userPre002DetailNullContractsBeforeSql() {
    var port = new NoSql();
    Connection connection = port.port();
    var repository = new UserQueryRepository();
    var request = new UserDetailRequestData(new UserId(9));
    missing("connection", () -> repository.detail(null, ADMIN, request, NOW));
    missing("actor", () -> repository.detail(connection, null, request, NOW));
    missing("now", () -> repository.detail(connection, ADMIN, request, null));
    missing("request", () -> repository.detail(connection, ADMIN, null, NOW));
    port.untouched();
  }

  /** PT-ADM-PRE003. */
  @Test
  void userPre003UserCannotSearchOrDetailBeforeSql() {
    var port = new NoSql();
    Connection connection = port.port();
    var repository = new UserQueryRepository();
    denied(() -> repository.search(connection, USER, searchRequest(Optional.empty()), NOW));
    denied(
        () -> repository.detail(connection, USER, new UserDetailRequestData(new UserId(9)), NOW));
    port.untouched();
  }

  /** PT-ADM-PRE004: X64 literal boundary, not a constructor rejection. */
  @Test
  void userPre004OversizePrefixRejectedBeforeSql() {
    var port = new NoSql();
    Connection connection = port.port();
    var repository = new UserQueryRepository();
    var request = searchRequest(Optional.of("x".repeat(65)));
    assertThrows(
        FieldEncodingException.class, () -> repository.search(connection, ADMIN, request, NOW));
    port.untouched();
  }

  private static UserSearchRequestData searchRequest(Optional<String> prefix) {
    return new UserSearchRequestData(prefix, Optional.empty(), Optional.empty(), 1, 50);
  }

  private static void missing(String field, Executable operation) {
    assertEquals(field, assertThrows(NullPointerException.class, operation).getMessage());
  }

  private static void denied(Executable operation) {
    var failure = assertThrows(AuthorizationException.class, operation);
    assertEquals(ResultCode.FORBIDDEN, failure.resultCode());
    assertEquals("operation is not available", failure.getMessage());
    assertNull(failure.getCause());
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

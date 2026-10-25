package dev.codex.schubert.nk.api.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.admin.UserDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.log.LogSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import dev.codex.schubert.nk.protocol.layout.semantic.ScriptFileId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Optional;
import java.util.function.Function;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** SS312/324/332/354; SSC329/BUG1592/YKT1345; PT-BORROWED-GRAPH329001..009; no I/O. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class BorrowedJdbcFatal329Test {
  private static final AuthenticatedActor ADMIN = new AuthenticatedActor(1, "PUBLIC", Role.ADMIN);
  private static final Instant NOW = Instant.parse("2026-10-22T00:00:00Z");

  @Test
  void borrowed329001UserSearch() {
    verify(
        c ->
            new UserQueryRepository()
                .search(
                    c,
                    ADMIN,
                    new UserSearchRequestData(
                        Optional.empty(), Optional.empty(), Optional.empty(), 1, 50),
                    NOW),
        new UserQueryException(true),
        "user",
        true);
  }

  @Test
  void borrowed329002UserDetail() {
    verify(
        c ->
            new UserQueryRepository()
                .detail(c, ADMIN, new UserDetailRequestData(new UserId(1)), NOW),
        new UserQueryException(true),
        "user",
        false);
  }

  @Test
  void borrowed329003ScenarioRows() {
    verify(
        c -> new ScenarioRepository().games(c, ADMIN),
        new ScenarioQueryException(true),
        "scenario",
        true);
  }

  @Test
  void borrowed329004ScenarioSearch() {
    verify(
        c ->
            new ScenarioRepository()
                .search(
                    c,
                    ADMIN,
                    new ScenarioSearchRequestData(
                        Optional.empty(),
                        Optional.empty(),
                        Optional.empty(),
                        Optional.empty(),
                        Optional.empty(),
                        Optional.empty(),
                        1,
                        100)),
        new ScenarioQueryException(true),
        "scenario",
        true);
  }

  @Test
  void borrowed329005ScenarioDetail() {
    verify(
        c ->
            new ScenarioRepository()
                .detail(c, ADMIN, new ScenarioDetailRequestData(new ScriptFileId(1))),
        new ScenarioQueryException(true),
        "scenario",
        true);
  }

  @Test
  void borrowed329006MediaQuery() {
    verify(
        c -> new MediaRepository().animationMenu(c, ADMIN),
        new MediaQueryException(true),
        "media",
        true);
  }

  @Test
  void borrowed329007LogSearch() {
    verify(
        c ->
            new LogQueryRepository()
                .search(
                    c,
                    ADMIN,
                    new LogSearchRequestData(
                        Optional.empty(),
                        Optional.empty(),
                        Optional.empty(),
                        Optional.empty(),
                        Optional.empty(),
                        Optional.empty(),
                        Optional.empty(),
                        1,
                        100)),
        new LogQueryException(true),
        "log",
        true);
  }

  @Test
  void borrowed329008QuestionPaged() {
    verify(
        c ->
            new QuestionQueryRepository()
                .questionSearch(
                    c,
                    ADMIN,
                    new QuestionSearchRequestData(
                        Optional.empty(),
                        Optional.empty(),
                        Optional.empty(),
                        Optional.empty(),
                        Optional.empty(),
                        1,
                        50)),
        new QuestionQueryException(ResultCode.RESOURCE_LIMIT),
        "question",
        true);
  }

  @Test
  void borrowed329009QuestionDetail() {
    verify(
        c ->
            new QuestionQueryRepository()
                .questionDetail(c, ADMIN, new QuestionDetailRequestData(new QuestionId(1))),
        new QuestionQueryException(ResultCode.RESOURCE_LIMIT),
        "question",
        true);
  }

  private static void verify(
      Function<Connection, ?> query,
      RuntimeException marker,
      String kind,
      boolean markerTranslated) {
    for (int mode = 0; mode < 4; mode++) {
      if (mode == 2 && !markerTranslated) continue;
      var fatal = new AssertionError("PUBLIC fatal");
      var primary = new SQLException("PUBLIC primary");
      if (mode == 1) primary.setNextException(new SQLException("PUBLIC next", fatal));
      Throwable executeFailure = mode == 2 ? marker : primary;
      Throwable closeFailure = mode == 0 || mode == 2 ? fatal : new SQLException("PUBLIC close");
      var fixture = new Fixture(executeFailure, mode == 1 ? null : closeFailure);
      if (mode < 3) {
        assertSame(
            fatal, assertThrows(AssertionError.class, () -> query.apply(fixture.connection)));
      } else {
        var actual = assertThrows(marker.getClass(), () -> query.apply(fixture.connection));
        assertEquals(kind + " query is unavailable", actual.getMessage());
        ResultCode code =
            switch (actual) {
              case UserQueryException e -> e.resultCode();
              case ScenarioQueryException e -> e.resultCode();
              case MediaQueryException e -> e.resultCode();
              case LogQueryException e -> e.resultCode();
              case QuestionQueryException e -> e.resultCode();
              default -> throw new AssertionError("unexpected fixture catalog");
            };
        assertEquals(ResultCode.TEMPORARY_FAILURE, code);
        assertNull(actual.getCause());
        assertEquals(0, actual.getSuppressed().length);
      }
      assertEquals(1, fixture.prepares);
      assertEquals(1, fixture.executes);
      assertEquals(1, fixture.statementCloses);
      assertEquals(0, fixture.connectionCloses);
      assertEquals(0, fixture.commits);
      assertEquals(0, fixture.rollbacks);
    }
  }

  private static final class Fixture {
    int prepares;
    int executes;
    int statementCloses;
    int connectionCloses;
    int commits;
    int rollbacks;
    final Connection connection;

    Fixture(Throwable executeFailure, @Nullable Throwable closeFailure) {
      var statement =
          (PreparedStatement)
              Proxy.newProxyInstance(
                  PreparedStatement.class.getClassLoader(),
                  new Class<?>[] {PreparedStatement.class},
                  (proxy, method, args) -> {
                    switch (method.getName()) {
                      case "setString", "setLong", "setInt", "setObject" -> {
                        return null;
                      }
                      case "executeQuery" -> {
                        executes++;
                        throw executeFailure;
                      }
                      case "close" -> {
                        statementCloses++;
                        if (closeFailure != null) throw closeFailure;
                        return null;
                      }
                      default ->
                          throw new UnsupportedOperationException(
                              "unexpected statement fixture call");
                    }
                  });
      connection =
          (Connection)
              Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (proxy, method, args) -> {
                    return switch (method.getName()) {
                      case "getAutoCommit" -> false;
                      case "isReadOnly" -> true;
                      case "prepareStatement" -> {
                        prepares++;
                        yield statement;
                      }
                      case "close" -> {
                        connectionCloses++;
                        yield null;
                      }
                      case "commit" -> {
                        commits++;
                        yield null;
                      }
                      case "rollback" -> {
                        rollbacks++;
                        yield null;
                      }
                      default ->
                          throw new UnsupportedOperationException(
                              "unexpected connection fixture call");
                    };
                  });
    }
  }
}

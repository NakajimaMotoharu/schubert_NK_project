package dev.codex.schubert.nk.api.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.FieldEncodingException;
import dev.codex.schubert.nk.protocol.layout.scenario.RouteListRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioFileListRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.SpeakerListRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import dev.codex.schubert.nk.protocol.layout.semantic.ScriptFileId;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.BiConsumer;
import org.junit.jupiter.api.Test;

/** NK-SCN-001; FUN003/004/AUT001/003; UI223/234; SS312/332/354; SCN005/2044. */
final class ScenarioPreSqlBoundaryTest {
  private static final AuthenticatedActor ACTOR =
      new AuthenticatedActor(7, "PublicBoundaryActor", Role.USER);
  private final ScenarioRepository repository = new ScenarioRepository();

  @Test
  void scnPre001GamesNullBeforeSql() { // PT-SCN-PRE001
    boundary(repository::games);
  }

  @Test
  void scnPre002SpeakersNullBeforeSql() { // PT-SCN-PRE002
    var request = new SpeakerListRequestData(Optional.empty());
    boundary((c, a) -> repository.speakers(c, a, request));
    missingRequest((c, a) -> repository.speakers(c, a, null));
  }

  @Test
  void scnPre003RoutesNullBeforeSql() { // PT-SCN-PRE003
    var request = new RouteListRequestData(GameCode.NUKITASHI1);
    boundary((c, a) -> repository.routes(c, a, request));
    missingRequest((c, a) -> repository.routes(c, a, null));
  }

  @Test
  void scnPre004FilesNullBeforeSql() { // PT-SCN-PRE004
    var request = new ScenarioFileListRequestData(GameCode.NUKITASHI1, 1);
    boundary((c, a) -> repository.files(c, a, request));
    missingRequest((c, a) -> repository.files(c, a, null));
  }

  @Test
  void scnPre005SearchNullBeforeSql() { // PT-SCN-PRE005
    var request = search(Optional.empty(), Optional.empty(), Optional.empty());
    boundary((c, a) -> repository.search(c, a, request));
    missingRequest((c, a) -> repository.search(c, a, null));
  }

  @Test
  void scnPre006DetailNullBeforeSql() { // PT-SCN-PRE006
    var request = new ScenarioDetailRequestData(new ScriptFileId(7));
    boundary((c, a) -> repository.detail(c, a, request));
    missingRequest((c, a) -> repository.detail(c, a, null));
  }

  @Test
  void scnPre007Body257BytesBeforeSql() { // PT-SCN-PRE007
    var request = search(Optional.of("x".repeat(257)), Optional.empty(), Optional.empty());
    oversize((c, a) -> repository.search(c, a, request));
  }

  @Test
  void scnPre008Speaker129BytesBeforeSql() { // PT-SCN-PRE008
    var request = search(Optional.empty(), Optional.of("x".repeat(129)), Optional.empty());
    oversize((c, a) -> repository.search(c, a, request));
  }

  @Test
  void scnPre009Chapter257BytesBeforeSql() { // PT-SCN-PRE009
    var request = search(Optional.empty(), Optional.empty(), Optional.of("x".repeat(257)));
    oversize((c, a) -> repository.search(c, a, request));
  }

  private static ScenarioSearchRequestData search(
      Optional<String> body, Optional<String> speaker, Optional<String> chapter) {
    return new ScenarioSearchRequestData(
        body, Optional.empty(), speaker, chapter, Optional.empty(), Optional.empty(), 1, 100);
  }

  private static void boundary(BiConsumer<Connection, AuthenticatedActor> call) {
    var fixture = new NoSql();
    Connection port = fixture.port();
    assertEquals(
        "connection",
        assertThrows(NullPointerException.class, () -> call.accept(null, ACTOR)).getMessage());
    assertEquals(
        "actor",
        assertThrows(NullPointerException.class, () -> call.accept(port, null)).getMessage());
    fixture.untouched();
  }

  private static void missingRequest(BiConsumer<Connection, AuthenticatedActor> call) {
    var fixture = new NoSql();
    assertEquals(
        "request",
        assertThrows(NullPointerException.class, () -> call.accept(fixture.port(), ACTOR))
            .getMessage());
    fixture.untouched();
  }

  private static void oversize(BiConsumer<Connection, AuthenticatedActor> call) {
    var fixture = new NoSql();
    assertThrows(FieldEncodingException.class, () -> call.accept(fixture.port(), ACTOR));
    fixture.untouched();
  }

  private static final class NoSql {
    private final AtomicInteger calls = new AtomicInteger();

    Connection port() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) -> {
                calls.incrementAndGet();
                throw new AssertionError("unexpected JDBC access");
              });
    }

    void untouched() {
      assertEquals(0, calls.get());
    }
  }
}

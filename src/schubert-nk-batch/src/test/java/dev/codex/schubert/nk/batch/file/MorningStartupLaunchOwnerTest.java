package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

/** READY428007..009: literal owner order, no native ready or fake completed graph. */
final class MorningStartupLaunchOwnerTest {
  private static final String FIXTURE_API_E3AF609E = "API";
  private static final String FIXTURE_COMPLETE_575951DB = "complete";
  private static final String FIXTURE_START_API_02CEED19 = "start:API";

  @Test
  void sequence428007ApiThenWebBorrowSameApiAndNeverStopOnTrueCompletion() throws Exception {
    var events = new ArrayList<String>();
    MorningStartupLaunchOwner.sequence(
        (service, earlier) -> {
          assertEquals(
              service == ServiceConfigFiles.Service.API ? List.of() : List.of(FIXTURE_API_E3AF609E),
              earlier);
          assertThrows(UnsupportedOperationException.class, () -> earlier.add("extra"));
          events.add("start:" + service);
          return service.name();
        },
        slot -> fail("success must retain live service"),
        started -> {
          assertEquals(List.of(FIXTURE_API_E3AF609E, "WEB"), started);
          assertThrows(UnsupportedOperationException.class, () -> started.add("extra"));
          events.add(FIXTURE_COMPLETE_575951DB);
        });
    assertEquals(
        List.of(FIXTURE_START_API_02CEED19, "start:WEB", FIXTURE_COMPLETE_575951DB), events);
  }

  @Test
  void sequence428008FailedStageClosesOnlyReturnedOwnersInReverseOrder() {
    for (int stage : List.of(0, 1, 2))
      for (Throwable failure :
          List.of(
              new IOException("golden"),
              new IllegalStateException("golden"),
              new AssertionError("golden"))) {
        var events = new ArrayList<String>();
        int failAt = stage;
        Throwable actual =
            assertThrows(
                failure.getClass(),
                () ->
                    MorningStartupLaunchOwner.sequence(
                        (service, earlier) -> {
                          events.add("start:" + service);
                          if (earlier.size() == failAt) raise(failure);
                          return service.name();
                        },
                        slot -> events.add("stop:" + slot),
                        started -> {
                          events.add(FIXTURE_COMPLETE_575951DB);
                          raise(failure);
                        }));
        assertSame(failure, actual);
        assertEquals(
            switch (stage) {
              case 0 -> List.of(FIXTURE_START_API_02CEED19);
              case 1 -> List.of(FIXTURE_START_API_02CEED19, "start:WEB", "stop:API");
              default ->
                  List.of(
                      FIXTURE_START_API_02CEED19,
                      "start:WEB",
                      FIXTURE_COMPLETE_575951DB,
                      "stop:WEB",
                      "stop:API");
            },
            events);
      }
  }

  @Test
  void sequence428009NullContractsCannotMintReturnedOwnership() {
    assertThrows(
        NullPointerException.class,
        () -> MorningStartupLaunchOwner.sequence(null, ignored -> {}, ignored -> {}));
    assertThrows(
        NullPointerException.class,
        () -> MorningStartupLaunchOwner.sequence((s, e) -> s, null, ignored -> {}));
    assertThrows(
        NullPointerException.class,
        () -> MorningStartupLaunchOwner.sequence((s, e) -> s, ignored -> {}, null));
    var closed = new ArrayList<String>();
    assertThrows(
        NullPointerException.class,
        () ->
            MorningStartupLaunchOwner.<String>sequence(
                (service, earlier) ->
                    service == ServiceConfigFiles.Service.API ? FIXTURE_API_E3AF609E : null,
                closed::add,
                ignored -> {
                  fail("not complete");
                }));
    assertEquals(List.of(FIXTURE_API_E3AF609E), closed);
  }

  private static void raise(Throwable failure) throws IOException {
    if (failure instanceof IOException checked) throw checked;
    if (failure instanceof RuntimeException unchecked) throw unchecked;
    throw (Error) failure;
  }
}

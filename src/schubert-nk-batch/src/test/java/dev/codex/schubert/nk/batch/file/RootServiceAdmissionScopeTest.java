package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/UI251/SS343/PG372; PT-OPS-RASCOPE001..006. */
final class RootServiceAdmissionScopeTest {
  private static final String FIXTURE_ROOT_956E6E33 = "root";
  private static final String FIXTURE_A_RELEASED_B491D631 = "A-released";

  @Test
  void rascope001OneReservedAOwnsWholePreflightAndOuterRecheck() throws IOException {
    var events = new ArrayList<String>();
    RootServiceAdmissionScope.execute(
        () -> events.add(FIXTURE_ROOT_956E6E33),
        work -> {
          events.add("A-acquired");
          try {
            work.execute(128);
            return Optional.of(Boolean.TRUE);
          } finally {
            events.add(FIXTURE_A_RELEASED_B491D631);
          }
        },
        fd -> events.add("work-" + fd));
    assertEquals(
        List.of(
            FIXTURE_ROOT_956E6E33,
            "A-acquired",
            FIXTURE_ROOT_956E6E33,
            "work-128",
            FIXTURE_ROOT_956E6E33,
            FIXTURE_A_RELEASED_B491D631,
            FIXTURE_ROOT_956E6E33),
        events);
  }

  @Test
  void rascope002ContendedADoesNotRunWork() {
    var calls = new AtomicInteger();
    assertThrows(
        IOException.class,
        () ->
            RootServiceAdmissionScope.execute(
                () -> {}, work -> Optional.empty(), fd -> calls.incrementAndGet()));
    assertEquals(0, calls.get());
  }

  @Test
  void rascope003OnlyReservedDescriptorBoundsReachWork() throws IOException {
    for (int invalid : new int[] {0, 127, 65536}) {
      var calls = new AtomicInteger();
      assertThrows(
          IOException.class,
          () ->
              RootServiceAdmissionScope.execute(
                  () -> {},
                  work -> {
                    work.execute(invalid);
                    return Optional.of(Boolean.TRUE);
                  },
                  fd -> calls.incrementAndGet()));
      assertEquals(0, calls.get());
    }
    var seen = new ArrayList<Integer>();
    for (int accepted : new int[] {128, 65535})
      RootServiceAdmissionScope.execute(
          () -> {},
          work -> {
            work.execute(accepted);
            return Optional.of(Boolean.TRUE);
          },
          seen::add);
    assertEquals(List.of(128, 65535), seen);
  }

  @Test
  void rascope004WorkOrInnerRootFailurePropagatesUnderA() {
    var events = new ArrayList<String>();
    assertThrows(
        IOException.class,
        () ->
            RootServiceAdmissionScope.execute(
                () -> events.add(FIXTURE_ROOT_956E6E33),
                work -> {
                  try {
                    work.execute(129);
                    return Optional.of(Boolean.TRUE);
                  } finally {
                    events.add(FIXTURE_A_RELEASED_B491D631);
                  }
                },
                fd -> {
                  throw new IOException("synthetic failure");
                }));
    assertEquals(
        List.of(FIXTURE_ROOT_956E6E33, FIXTURE_ROOT_956E6E33, FIXTURE_A_RELEASED_B491D631), events);
    var checks = new AtomicInteger();
    assertThrows(
        IOException.class,
        () ->
            RootServiceAdmissionScope.execute(
                () -> {
                  if (checks.incrementAndGet() == 2) throw new IOException("root changed");
                },
                work -> {
                  work.execute(128);
                  return Optional.of(Boolean.TRUE);
                },
                fd -> fail("work after inner root change")));
    assertEquals(2, checks.get());
  }

  @Test
  void rascope005OuterRootOrFalseCallbackResultRejects() {
    var checks = new AtomicInteger();
    assertThrows(
        IOException.class,
        () ->
            RootServiceAdmissionScope.execute(
                () -> {
                  if (checks.incrementAndGet() == 4) throw new IOException("root changed after A");
                },
                work -> {
                  work.execute(128);
                  return Optional.of(Boolean.TRUE);
                },
                fd -> {}));
    assertEquals(4, checks.get());
    assertThrows(
        IOException.class,
        () ->
            RootServiceAdmissionScope.execute(
                () -> {}, work -> Optional.of(Boolean.FALSE), fd -> fail("false callback")));
  }

  @Test
  void rascope006NullAndRepeatedOwnershipStayFailClosed() throws IOException {
    assertThrows(
        NullPointerException.class,
        () -> RootServiceAdmissionScope.execute(null, work -> Optional.empty(), fd -> {}));
    assertThrows(
        NullPointerException.class,
        () -> RootServiceAdmissionScope.execute(() -> {}, null, fd -> {}));
    assertThrows(
        NullPointerException.class,
        () -> RootServiceAdmissionScope.execute(() -> {}, work -> Optional.empty(), null));
    var calls = new AtomicInteger();
    for (int iteration = 0; iteration < 2; iteration++)
      RootServiceAdmissionScope.execute(
          () -> {},
          work -> {
            work.execute(128);
            return Optional.of(Boolean.TRUE);
          },
          fd -> calls.incrementAndGet());
    assertEquals(2, calls.get());
  }
}

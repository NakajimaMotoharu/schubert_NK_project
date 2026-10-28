package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.lang.reflect.Modifier;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/UI251/SS342/343/PG370; PT-OPS-RMAIN001..006. */
final class RootServiceLauncherTest {
  private static final String FIXTURE_WEB_97D727BB = "WEB";

  @Test
  void rmain001WebOnlyGateReturnsNonSuccess() {
    var seen = new AtomicReference<ServiceConfigFiles.Service>();
    assertEquals(30, RootServiceLauncher.run(new String[] {FIXTURE_WEB_97D727BB}, seen::set));
    assertEquals(ServiceConfigFiles.Service.WEB, seen.get());
  }

  @Test
  void rmain002ApiOnlyGateReturnsNonSuccess() {
    var seen = new AtomicReference<ServiceConfigFiles.Service>();
    assertEquals(30, RootServiceLauncher.run(new String[] {"API"}, seen::set));
    assertEquals(ServiceConfigFiles.Service.API, seen.get());
  }

  @Test
  void rmain003ArbitraryArgumentsNeverEnterGate() {
    var calls = new AtomicInteger();
    RootServiceLauncher.Admission gate = ignored -> calls.incrementAndGet();
    for (String[] input :
        new String[][] {
          {}, {FIXTURE_WEB_97D727BB, "API"}, {"web"}, {"--service=WEB"}, {""}, {"OTHER"}
        }) assertEquals(70, RootServiceLauncher.run(input, gate));
    assertEquals(0, calls.get());
  }

  @Test
  void rmain004KnownFailureIsNonSuccessAndUnknownPropagates() {
    assertEquals(
        30,
        RootServiceLauncher.run(
            new String[] {FIXTURE_WEB_97D727BB},
            ignored -> {
              throw new IOException("PRIVATE");
            }));
    var unknown = new IllegalStateException("programming failure");
    assertSame(
        unknown,
        assertThrows(
            IllegalStateException.class,
            () ->
                RootServiceLauncher.run(
                    new String[] {"API"},
                    ignored -> {
                      throw unknown;
                    })));
  }

  @Test
  void rmain005NullContractAndRepeatedCallsHaveNoState() {
    assertThrows(NullPointerException.class, () -> RootServiceLauncher.run(null, ignored -> {}));
    assertThrows(
        NullPointerException.class,
        () -> RootServiceLauncher.run(new String[] {FIXTURE_WEB_97D727BB}, null));
    var calls = new AtomicInteger();
    RootServiceLauncher.Admission gate = ignored -> calls.incrementAndGet();
    assertEquals(30, RootServiceLauncher.run(new String[] {FIXTURE_WEB_97D727BB}, gate));
    assertEquals(30, RootServiceLauncher.run(new String[] {FIXTURE_WEB_97D727BB}, gate));
    assertEquals(2, calls.get());
  }

  @Test
  void rmain006OnlyPublicMainNoPublicConstructor() throws Exception {
    var constructor = RootServiceLauncher.class.getDeclaredConstructor();
    // Historical RMAIN006 ID retained; SSC299 allows only standard native Java25 noarg.
    assertTrue(Modifier.isPublic(constructor.getModifiers()));
    assertEquals(1, RootServiceLauncher.class.getConstructors().length);
    assertTrue(
        Modifier.isPublic(
            RootServiceLauncher.class.getMethod("main", String[].class).getModifiers()));
    assertFalse(
        Modifier.isStatic(
            RootServiceLauncher.class.getMethod("main", String[].class).getModifiers()));
  }
}

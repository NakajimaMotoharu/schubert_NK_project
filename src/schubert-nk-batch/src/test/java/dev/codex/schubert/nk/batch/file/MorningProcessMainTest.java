package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.batch.platform.MorningParentBudget;
import dev.codex.schubert.nk.batch.platform.StopGateException;
import dev.codex.schubert.nk.batch.platform.StopGateFailure;
import java.io.IOException;
import java.lang.reflect.Constructor;
import java.lang.reflect.Modifier;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/UI251/SS341/343/PG339/368; PT-OPS-MMAIN001-007. */
final class MorningProcessMainTest {
  @Test
  void mmain009OnlyActualSuccessfulArchiveSuppliesSameOwnerManifestOnce() throws Exception {
    var literal = dev.codex.schubert.nk.batch.repository.BackupStepFixture.manifest();
    var calls = new AtomicInteger();
    var archive =
        MorningProcessMain.archive(
            () -> {
              calls.incrementAndGet();
              return literal;
            });
    assertThrows(IOException.class, archive::verifiedManifest);
    archive.complete();
    assertEquals(literal, archive.verifiedManifest());
    assertThrows(IOException.class, archive::complete);
    assertEquals(1, calls.get());
    try (var executor = java.util.concurrent.Executors.newSingleThreadExecutor()) {
      executor
          .submit(
              () -> {
                assertThrows(IOException.class, archive::complete);
                assertThrows(IOException.class, archive::verifiedManifest);
              })
          .get(5, java.util.concurrent.TimeUnit.SECONDS);
    }
    assertThrows(NullPointerException.class, () -> MorningProcessMain.archive(null));
    var failed =
        MorningProcessMain.archive(
            () -> {
              throw new IOException("PRIVATE");
            });
    assertThrows(IOException.class, failed::complete);
    assertThrows(IOException.class, failed::verifiedManifest);
    assertThrows(IOException.class, failed::complete);
    var nullResult = MorningProcessMain.archive(() -> null);
    assertThrows(NullPointerException.class, nullResult::complete);
    assertThrows(IOException.class, nullResult::verifiedManifest);
    MorningProcessMain.Archive oldFixture = () -> {};
    assertThrows(IOException.class, oldFixture::verifiedManifest);
  }

  @Test
  void mmain008ExplicitCanonicalResumeIsSameBudgetAndCannotOverrideCutoffOrGate() {
    String literal = "31100027-2222-4a33-8444-555555555555";
    var calls = new AtomicInteger();
    assertEquals(
        30,
        MorningProcessMain.run(
            new String[] {"--resume", literal},
            b -> fail("fresh selected"),
            (b, run) -> {
              b.requireWithin();
              assertEquals(java.util.UUID.fromString(literal), run);
              calls.incrementAndGet();
            }));
    assertEquals(1, calls.get());
    for (String[] args :
        new String[][] {
          {"--resume"},
          {"--resume", ""},
          {"--resume", "00000000-0000-0000-0000-000000000000"},
          {"--resume", literal.toUpperCase(java.util.Locale.ROOT)},
          {"--resume", "1-2-3-4-5"},
          {"--resume", null},
          {"--resume", literal, "--cutoff=now"},
          {null, literal}
        }) {
      assertEquals(
          70,
          MorningProcessMain.run(
              args, b -> fail("fresh selected"), (b, run) -> fail("resume selected")));
    }
    var unknown = new NullPointerException("programming failure");
    assertSame(
        unknown,
        assertThrows(
            NullPointerException.class,
            () ->
                MorningProcessMain.run(
                    new String[] {"--resume", literal},
                    b -> {},
                    (b, run) -> {
                      throw unknown;
                    })));
    assertEquals(
        30,
        MorningProcessMain.run(
            new String[] {"--resume", literal},
            b -> {},
            (b, run) -> {
              throw new IOException("private");
            }));
    assertThrows(
        NullPointerException.class, () -> MorningProcessMain.run(new String[0], b -> {}, null));
  }

  @Test
  void mmain001AdmissionSuccessStillCannotClaimMorningSuccess() {
    var calls = new AtomicInteger();
    assertEquals(30, MorningProcessMain.run(new String[0], budget -> calls.incrementAndGet()));
    assertEquals(1, calls.get());
  }

  @Test
  void mmain002ArgumentsCannotSelectRunOrOverrideGate() {
    var calls = new AtomicInteger();
    assertEquals(
        70,
        MorningProcessMain.run(
            new String[] {"--run-id=ignored"}, budget -> calls.incrementAndGet()));
    assertEquals(70, MorningProcessMain.run(new String[] {""}, budget -> calls.incrementAndGet()));
    assertEquals(0, calls.get());
  }

  @Test
  void mmain003KnownIoAndStopFailureAreFixedNonSuccess() throws Exception {
    assertEquals(
        30,
        MorningProcessMain.run(
            new String[0],
            budget -> {
              throw new IOException("PRIVATE");
            }));
    // A fixed known stop exception is already sanitized by the stop-policy boundary.
    Constructor<StopGateException> factory =
        StopGateException.class.getDeclaredConstructor(StopGateFailure.class);
    factory.setAccessible(true);
    StopGateException known = factory.newInstance(StopGateFailure.COMMAND_FAILURE);
    assertEquals(
        30,
        MorningProcessMain.run(
            new String[0],
            budget -> {
              throw known;
            }));
  }

  @Test
  void mmain004UnknownIdentityAndNullContractAreNotNormalized() {
    var unknown = new IllegalStateException("programming failure");
    assertSame(
        unknown,
        assertThrows(
            IllegalStateException.class,
            () ->
                MorningProcessMain.run(
                    new String[0],
                    budget -> {
                      throw unknown;
                    })));
    assertThrows(NullPointerException.class, () -> MorningProcessMain.run(null, budget -> {}));
    assertThrows(NullPointerException.class, () -> MorningProcessMain.run(new String[0], null));
  }

  @Test
  void mmain005NoPublicConstructorForAlternativeLauncher() throws Exception {
    Constructor<MorningProcessMain> constructor = MorningProcessMain.class.getDeclaredConstructor();
    assertTrue(Modifier.isPrivate(constructor.getModifiers()));
    assertTrue(
        Modifier.isPublic(
            MorningProcessMain.class.getMethod("main", String[].class).getModifiers()));
  }

  @Test
  void mmain006OneParentBudgetIsBorrowedByAdmissionAndNeverClaimsReady() {
    var received = new AtomicReference<MorningParentBudget>();
    assertEquals(
        30,
        MorningProcessMain.run(
            new String[0],
            budget -> {
              assertNull(received.getAndSet(budget));
              budget.requireWithin();
            }));
    assertNotNull(received.get());
    assertDoesNotThrow(received.get()::requireWithin);
  }

  @Test
  void mmain007InvalidArgvDoesNotBorrowParentBudget() {
    var calls = new AtomicInteger();
    assertEquals(
        70, MorningProcessMain.run(new String[] {"unexpected"}, budget -> calls.incrementAndGet()));
    assertEquals(0, calls.get());
  }
}

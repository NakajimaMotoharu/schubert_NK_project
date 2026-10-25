package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

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
  void isspub009ActualMainHashesWholeCanonicalFrameBeforePermitConstruction() throws Exception {
    // Independent sha256sum of the unchanged SS343 whole-byte golden resources, not Production.
    var expected =
        java.util.Map.of(
            "new", "84190122f0b2350d4f9066100dd883d0a9c0f2636f9b4499c1ceff989d48e145",
            "failed", "abfb4ec51b908b66273bdecfa180e656ac02dd8b260a17995bf9b76be754b644",
            "reused", "87275edf593b9ad26b0221b0aebf289e47c4865bacc5b85ac77a60c0b2a971b9");
    for (var entry : expected.entrySet()) {
      String frame;
      try (var stream =
          java.util.Objects.requireNonNull(
              getClass()
                  .getResourceAsStream("/ops/issuer-prestart-" + entry.getKey() + "-golden.txt"))) {
        frame = new String(stream.readAllBytes(), java.nio.charset.StandardCharsets.US_ASCII);
      }
      assertEquals(entry.getValue(), MorningProcessMain.prestartDigest(frame));
      var epoch = MorningPrestartEvidenceTest.EPOCH;
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new StartupPermitRecords.Permit(
                  epoch.boot(),
                  epoch.epoch(),
                  epoch.activation(),
                  "b".repeat(32),
                  "1".repeat(64),
                  "2".repeat(64),
                  "3".repeat(64),
                  "4".repeat(64),
                  frame));
      var permit =
          new StartupPermitRecords.Permit(
              epoch.boot(),
              epoch.epoch(),
              epoch.activation(),
              "b".repeat(32),
              "1".repeat(64),
              "2".repeat(64),
              "3".repeat(64),
              "4".repeat(64),
              MorningProcessMain.prestartDigest(frame));
      assertEquals(entry.getValue(), permit.prestartStepsDigest());
      for (int index = 0; index < frame.length(); index++) {
        var changed = frame.toCharArray();
        changed[index] = changed[index] == 'x' ? 'y' : 'x';
        assertNotEquals(entry.getValue(), MorningProcessMain.prestartDigest(new String(changed)));
      }
      assertNotEquals(entry.getValue(), MorningProcessMain.prestartDigest(frame.stripTrailing()));
    }
    assertThrows(NullPointerException.class, () -> MorningProcessMain.prestartDigest(null));
    assertThrows(NullPointerException.class, () -> MorningProcessMain.prestartDigest("x", null));
    assertEquals(
        "prestart digest unavailable",
        assertThrows(
                IOException.class,
                () ->
                    MorningProcessMain.prestartDigest(
                        "x",
                        () -> {
                          throw new java.security.NoSuchAlgorithmException("PRIVATE");
                        }))
            .getMessage());
    var unknown = new IllegalStateException("PRIVATE");
    assertSame(
        unknown,
        assertThrows(
            IllegalStateException.class,
            () ->
                MorningProcessMain.prestartDigest(
                    "x",
                    () -> {
                      throw unknown;
                    })));
  }

  @Test
  void mmain010KnownBorrowedOwnerStopIsThirtyButProgrammingFailureIsNotNormalized() {
    for (var reason : dev.codex.schubert.nk.batch.cleanup.CleanupStopReason.values()) {
      var stopped = new dev.codex.schubert.nk.batch.cleanup.CleanupStoppedException(reason);
      assertEquals(
          30,
          MorningProcessMain.run(
              new String[0],
              budget -> {
                throw stopped;
              }));
      assertEquals(
          30,
          MorningProcessMain.run(
              new String[] {"--resume", "31100027-2222-4333-8444-555555555555"},
              budget -> fail("fresh selected"),
              (budget, run) -> {
                throw stopped;
              }));
    }
    var npe = new NullPointerException("PUBLIC_PROGRAMMING");
    assertSame(
        npe,
        assertThrows(
            NullPointerException.class,
            () ->
                MorningProcessMain.run(
                    new String[0],
                    budget -> {
                      throw npe;
                    })));
    var unknown = new IllegalStateException("PUBLIC_PROGRAMMING");
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
    var fatal = new AssertionError("PUBLIC_PROGRAMMING");
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class,
            () ->
                MorningProcessMain.run(
                    new String[0],
                    budget -> {
                      throw fatal;
                    })));
  }

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
    // SSC299: only the standard native noarg is public, never alternative data/control ports.
    assertTrue(Modifier.isPublic(constructor.getModifiers()));
    assertEquals(1, MorningProcessMain.class.getConstructors().length);
    assertTrue(
        Modifier.isPublic(
            MorningProcessMain.class.getMethod("main", String[].class).getModifiers()));
    assertFalse(
        Modifier.isStatic(
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

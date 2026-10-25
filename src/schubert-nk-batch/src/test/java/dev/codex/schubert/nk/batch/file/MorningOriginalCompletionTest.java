package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion;
import dev.codex.schubert.nk.batch.repository.MaintenanceRunState;
import java.io.IOException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/UI251/SS341342343/SSC178/318; ORIG455001..003, host scope only. */
final class MorningOriginalCompletionTest {
  private static final MaintenanceActivation ACTIVATION =
      new MaintenanceActivation(
          new BatchRun(
              UUID.fromString("00000000-0000-0000-0000-000000000455"),
              Instant.parse("2026-10-04T09:00:00.123456Z")),
          UUID.fromString("00000000-0000-0000-0000-000000000456"));
  private static final MaintenanceCompletion DONE =
      new MaintenanceCompletion(
          ACTIVATION,
          Instant.parse("2026-10-04T09:01:00.654321Z"),
          MaintenanceCompletion.Outcome.WARNING);

  private static final class Fixture implements MorningNewRunAdmission.OriginalFiles {
    final List<String> events = new ArrayList<>();
    final AtomicBoolean alive = new AtomicBoolean(true);
    Optional<MaintenanceCompletion> stored = Optional.empty();
    String fault = "";
    int kind;
    int publish;
    int roots;
    int rootFault;
    boolean wrongResult;
    boolean expireAfterPublish;
    boolean expireAfterReference;
    final IOException io = new IOException("fixed fixture failure");
    final IllegalStateException runtime = new IllegalStateException("fixed fixture failure");
    final AssertionError fatal = new AssertionError("fixed fixture failure");

    void failure() throws IOException {
      if (kind == 0) throw io;
      if (kind == 1) throw runtime;
      throw fatal;
    }

    void root() throws IOException {
      events.add("root");
      if (++roots == rootFault) failure();
    }

    public void verify(MaintenanceActivation expected) throws IOException {
      assertEquals(ACTIVATION, expected);
      events.add("pending");
      if (fault.equals("pending")) failure();
      assertTrue(stored.isEmpty());
    }

    public MaintenanceCompletion complete(MaintenanceCompletion expected) throws IOException {
      assertEquals(DONE, expected);
      events.add("publish");
      publish++;
      stored = Optional.of(expected);
      if (expireAfterPublish) alive.set(false);
      if (fault.equals("publish")) failure();
      return wrongResult
          ? new MaintenanceCompletion(ACTIVATION, DONE.endedAt().plusNanos(1000), DONE.outcome())
          : expected;
    }

    public void verifyCompleted(MaintenanceCompletion expected) throws IOException {
      events.add("done");
      if (fault.equals("done")) failure();
      assertEquals(Optional.of(expected), stored);
    }

    public BatchRun referenceRun(MaintenanceActivation current, UUID priorId, Instant observed)
        throws IOException {
      assertEquals(ACTIVATION, current);
      assertEquals(UUID.fromString("00000000-0000-0000-0000-000000000454"), priorId);
      assertEquals(Instant.parse("2026-10-04T09:00:30Z"), observed);
      events.add("reference");
      if (fault.equals("reference")) failure();
      if (expireAfterReference) alive.set(false);
      return new BatchRun(priorId, Instant.parse("2026-10-04T08:00:00Z"));
    }

    public BatchRun referenceCompletedRun(
        MaintenanceCompletion expected, UUID priorId, Instant observed) throws IOException {
      assertEquals(Optional.of(expected), stored);
      events.add("completed-reference");
      return referenceRun(expected.activation(), priorId, observed);
    }

    MorningNewRunAdmission.OriginalProof proof() {
      return MorningNewRunAdmission.scopedOriginalProof(
          this::root,
          this,
          new MaintenanceRunState(ACTIVATION, stored),
          alive,
          () -> new IOException("scope unavailable"));
    }
  }

  /** SSC240/RLOOK852003: historical SKIP precedes current WARNING DONE; no republish. */
  @Test
  void completedLookupSwitchesToTypedDataOnlyForPublishedAndExistingWarning() throws Exception {
    var id = UUID.fromString("00000000-0000-0000-0000-000000000454");
    var observed = Instant.parse("2026-10-04T09:00:30Z");
    for (boolean existing : List.of(false, true)) {
      var f = new Fixture();
      if (existing) f.stored = Optional.of(DONE);
      var proof = f.proof();
      if (!existing) assertEquals(DONE, proof.complete(DONE));
      f.events.clear();
      assertEquals(
          new BatchRun(id, Instant.parse("2026-10-04T08:00:00Z")),
          proof.referenceRun(id, observed));
      assertEquals(
          List.of(
              "root", "done", "root", "completed-reference", "reference", "root", "done", "root"),
          f.events);
      assertEquals(existing ? 0 : 1, f.publish);
      assertEquals(Optional.of(DONE), f.stored);
      f.alive.set(false);
      assertThrows(IOException.class, () -> proof.referenceRun(id, observed));
    }
  }

  /** RLOOK852004: completed reference preserves exact exception/owner and fail-closed default. */
  @Test
  void completedReferenceFailureOwnerAndMissingAdapterNeverReturnData() throws Exception {
    var id = UUID.fromString("00000000-0000-0000-0000-000000000454");
    var observed = Instant.parse("2026-10-04T09:00:30Z");
    for (int kind = 0; kind < 3; kind++) {
      var f = new Fixture();
      f.stored = Optional.of(DONE);
      f.kind = kind;
      f.fault = "reference";
      assertSame(
          kind == 0 ? f.io : kind == 1 ? f.runtime : f.fatal,
          assertThrows(Throwable.class, () -> f.proof().referenceRun(id, observed)));
      assertEquals(0, f.publish);
    }
    var f = new Fixture();
    f.stored = Optional.of(DONE);
    f.expireAfterReference = true;
    assertThrows(IOException.class, () -> f.proof().referenceRun(id, observed));
    var foreign = new Fixture();
    foreign.stored = Optional.of(DONE);
    var proof = foreign.proof();
    try (var executor = Executors.newSingleThreadExecutor()) {
      executor
          .submit(() -> assertThrows(IOException.class, () -> proof.referenceRun(id, observed)))
          .get(5, TimeUnit.SECONDS);
    }
    assertTrue(foreign.events.isEmpty());
    assertThrows(
        IOException.class,
        () ->
            new MorningNewRunAdmission.OriginalFiles() {}.referenceCompletedRun(
                DONE, id, observed));
  }

  @Test
  void rlook200002RetainedLookupCannotEscapeOriginalOwnerThreadOrLifetime() throws Exception {
    var f = new Fixture();
    var proof = f.proof();
    var id = UUID.fromString("00000000-0000-0000-0000-000000000454");
    var observed = Instant.parse("2026-10-04T09:00:30Z");
    assertEquals(
        new BatchRun(id, Instant.parse("2026-10-04T08:00:00Z")), proof.referenceRun(id, observed));
    assertEquals(
        List.of("root", "pending", "root", "reference", "root", "pending", "root"), f.events);
    assertEquals(0, f.publish);
    assertThrows(NullPointerException.class, () -> proof.referenceRun(null, observed));
    assertThrows(NullPointerException.class, () -> proof.referenceRun(id, null));
    var failure = new java.util.concurrent.atomic.AtomicReference<Throwable>();
    var thread =
        new Thread(
            () -> {
              try {
                proof.referenceRun(id, observed);
              } catch (Throwable actual) {
                failure.set(actual);
              }
            });
    thread.start();
    thread.join();
    assertInstanceOf(IOException.class, failure.get());
    f.alive.set(false);
    assertThrows(IOException.class, () -> proof.referenceRun(id, observed));
    assertEquals(1, f.events.stream().filter("reference"::equals).count());
  }

  @Test
  void rlook200002LookupFailureAndPostReadOwnerLossNeverReturnTheData() throws Exception {
    var id = UUID.fromString("00000000-0000-0000-0000-000000000454");
    var observed = Instant.parse("2026-10-04T09:00:30Z");
    for (int kind = 0; kind < 3; kind++) {
      var f = new Fixture();
      f.kind = kind;
      f.fault = "reference";
      var proof = f.proof();
      var actual = assertThrows(Throwable.class, () -> proof.referenceRun(id, observed));
      assertSame(kind == 0 ? f.io : kind == 1 ? f.runtime : f.fatal, actual);
      assertEquals(0, f.publish);
    }
    var f = new Fixture();
    f.expireAfterReference = true;
    var proof = f.proof();
    assertThrows(IOException.class, () -> proof.referenceRun(id, observed));
    assertEquals(0, f.publish);
    var empty = new MorningNewRunAdmission.OriginalFiles() {};
    assertThrows(IOException.class, () -> empty.referenceRun(ACTIVATION, id, observed));
    MorningNewRunAdmission.OriginalProof legacy = () -> {};
    assertThrows(IOException.class, () -> legacy.referenceRun(id, observed));
  }

  @Test
  void orig455001PendingPublishesOnceAndThenChecksCompletedGraph() throws Exception {
    var f = new Fixture();
    var proof = f.proof();
    proof.verify();
    assertEquals(DONE, proof.complete(DONE));
    proof.verify();
    assertEquals(
        List.of(
            "root", "pending", "root", "root", "pending", "root", "publish", "done", "root", "root",
            "done", "root", "root", "done", "root"),
        f.events);
    assertEquals(1, f.publish);
    assertThrows(IOException.class, () -> proof.complete(DONE));
    f.alive.set(false);
    assertThrows(IOException.class, proof::verify);
    assertThrows(IOException.class, () -> proof.complete(DONE));
    assertEquals(1, f.publish);
  }

  /** COMP203003: retained checks keep owner/root failures and UNKNOWN completion rejection. */
  @Test
  void comp203003RetainedOriginalIsNeverCompletionOrEscapedOwnership() throws Exception {
    var f = new Fixture();
    var proof = f.proof();
    proof.verifyRetained();
    assertEquals(List.of("root", "pending", "root"), f.events);
    assertEquals(0, f.publish);
    f.alive.set(false);
    assertThrows(IOException.class, proof::verifyRetained);
    assertEquals(3, f.events.size());
    var unknown = new Fixture();
    unknown.wrongResult = true;
    var uncertain = unknown.proof();
    assertThrows(IOException.class, () -> uncertain.complete(DONE));
    assertThrows(IOException.class, uncertain::verifyRetained);
    var defaults = new MorningNewRunAdmission.OriginalFiles() {};
    assertThrows(IOException.class, () -> defaults.verifyRetained(ACTIVATION));
    var legacyCalls = new java.util.concurrent.atomic.AtomicInteger();
    MorningNewRunAdmission.OriginalProof legacy = legacyCalls::incrementAndGet;
    legacy.verifyRetained();
    assertEquals(1, legacyCalls.get());
    var foreign = new Fixture();
    var retained = foreign.proof();
    try (var executor = Executors.newSingleThreadExecutor()) {
      executor
          .submit(() -> assertThrows(IOException.class, retained::verifyRetained))
          .get(5, TimeUnit.SECONDS);
    }
    assertTrue(foreign.events.isEmpty());
    for (int rootFault : List.of(1, 2)) {
      var fault = new Fixture();
      fault.rootFault = rootFault;
      assertSame(fault.io, assertThrows(IOException.class, fault.proof()::verifyRetained));
    }
  }

  @Test
  void orig455002ExistingDoneIsReadOnlyAndOtherTimeOutcomeNeverOverwrites() throws Exception {
    var f = new Fixture();
    f.stored = Optional.of(DONE);
    var proof = f.proof();
    proof.verify();
    for (var different :
        List.of(
            new MaintenanceCompletion(ACTIVATION, DONE.endedAt().plusNanos(1000), DONE.outcome()),
            new MaintenanceCompletion(
                ACTIVATION, DONE.endedAt(), MaintenanceCompletion.Outcome.SUCCESS))) {
      assertThrows(IOException.class, () -> proof.complete(different));
    }
    assertEquals(DONE, proof.complete(DONE));
    proof.verify();
    assertEquals(0, f.publish);
    assertFalse(f.events.contains("pending"));
    assertEquals(Optional.of(DONE), f.stored);
    assertThrows(IOException.class, () -> proof.complete(DONE));
  }

  @Test
  void orig455003ForeignThreadActivationNullAndDeadCapDoNotMutate() throws Exception {
    var f = new Fixture();
    var proof = f.proof();
    try (var executor = Executors.newSingleThreadExecutor()) {
      executor
          .submit(
              () -> {
                assertThrows(IOException.class, proof::verify);
                assertThrows(IOException.class, () -> proof.complete(DONE));
              })
          .get(5, TimeUnit.SECONDS);
    }
    var wrong =
        new MaintenanceCompletion(
            new MaintenanceActivation(ACTIVATION.run(), ACTIVATION.run().id()),
            DONE.endedAt(),
            DONE.outcome());
    assertThrows(IOException.class, () -> proof.complete(wrong));
    assertThrows(NullPointerException.class, () -> proof.complete(null));
    assertEquals(0, f.publish);
    assertTrue(f.events.isEmpty());
    f.alive.set(false);
    assertThrows(IOException.class, proof::verify);
    assertThrows(IOException.class, () -> proof.complete(DONE));
    assertTrue(f.events.isEmpty());
  }

  @Test
  void orig455004CompleteOrReadbackUncertaintyPoisonsPendingProof() throws Exception {
    for (String phase : List.of("pending", "publish", "done")) {
      for (int kind = 0; kind < 3; kind++) {
        var f = new Fixture();
        f.fault = phase;
        f.kind = kind;
        var proof = f.proof();
        Throwable actual = assertThrows(Throwable.class, () -> proof.complete(DONE));
        assertSame(kind == 0 ? f.io : kind == 1 ? f.runtime : f.fatal, actual);
        assertEquals(phase.equals("pending") ? 0 : 1, f.publish);
        if (!phase.equals("pending")) {
          f.fault = "";
          assertThrows(IOException.class, proof::verify);
          assertThrows(IOException.class, () -> proof.complete(DONE));
          assertEquals(1, f.publish);
        }
      }
    }
  }

  @Test
  void orig455005RootBeforeAndAfterChecksPreserveActualFailure() throws Exception {
    for (int rootFault = 1; rootFault <= 5; rootFault++) {
      var f = new Fixture();
      f.rootFault = rootFault;
      var proof = f.proof();
      assertSame(f.io, assertThrows(IOException.class, () -> proof.complete(DONE)));
      assertEquals(rootFault <= 2 ? 0 : 1, f.publish);
    }
  }

  @Test
  void orig455006ProviderMismatchAndExpiryAfterPublishAreUnconfirmed() throws Exception {
    for (boolean expiry : List.of(false, true)) {
      var f = new Fixture();
      f.wrongResult = !expiry;
      f.expireAfterPublish = expiry;
      var proof = f.proof();
      assertThrows(IOException.class, () -> proof.complete(DONE));
      assertThrows(IOException.class, proof::verify);
      assertEquals(1, f.publish);
    }
  }

  @Test
  void orig455007DefaultPortsHaveNoCompletionAuthorityAndFactoryRequiresContracts() {
    MorningNewRunAdmission.OriginalProof old = () -> {};
    assertThrows(IOException.class, () -> old.complete(DONE));
    var defaults = new MorningNewRunAdmission.OriginalFiles() {};
    assertThrows(IOException.class, () -> defaults.verify(ACTIVATION));
    assertThrows(IOException.class, () -> defaults.complete(DONE));
    assertThrows(IOException.class, () -> defaults.verifyCompleted(DONE));
    var f = new Fixture();
    var state = new MaintenanceRunState(ACTIVATION, Optional.empty());
    var failure =
        new java.util.function.Supplier<IOException>() {
          public IOException get() {
            return new IOException("fixed");
          }
        };
    assertThrows(
        NullPointerException.class,
        () -> MorningNewRunAdmission.scopedOriginalProof(null, f, state, f.alive, failure));
    assertThrows(
        NullPointerException.class,
        () -> MorningNewRunAdmission.scopedOriginalProof(f::root, null, state, f.alive, failure));
    assertThrows(
        NullPointerException.class,
        () -> MorningNewRunAdmission.scopedOriginalProof(f::root, f, null, f.alive, failure));
    assertThrows(
        NullPointerException.class,
        () -> MorningNewRunAdmission.scopedOriginalProof(f::root, f, state, null, failure));
    assertThrows(
        NullPointerException.class,
        () -> MorningNewRunAdmission.scopedOriginalProof(f::root, f, state, f.alive, null));
  }
}

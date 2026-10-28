package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.file.StartupPermitRecords.Epoch;
import dev.codex.schubert.nk.batch.file.StartupPermitRecords.State;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
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
import org.junit.jupiter.api.Test;

/** OPS009/UI251/SS341/343/SSC089/105; PG344/PT-OPS-MINVALID001-006. */
final class MorningCurrentInvalidationTest {
  private static final String FIXTURE_WRITE_BC2434A1 = "write";
  private static final UUID BOOT = UUID.fromString("00000000-0000-0000-0000-000000000344");
  private static final UUID EPOCH = UUID.fromString("00000000-0000-0000-0000-000000000345");
  private static final UUID RUN = UUID.fromString("00000000-0000-0000-0000-000000000346");
  private static final UUID ACTIVE = UUID.fromString("00000000-0000-0000-0000-000000000347");
  private static final MaintenanceActivation ACTIVATION =
      new MaintenanceActivation(new BatchRun(RUN, Instant.parse("2026-09-28T05:00:00Z")), ACTIVE);
  private static final MaintenanceRunState PENDING =
      new MaintenanceRunState(ACTIVATION, Optional.empty());

  private static final class Store implements MorningCurrentInvalidation.Store {
    final List<String> events = new ArrayList<>();
    Epoch written;
    Epoch readOverride;
    Epoch returnedOverride;
    IOException failure;

    @Override
    public Epoch invalidate(UUID boot, UUID epoch, MaintenanceActivation activation)
        throws IOException {
      events.add(FIXTURE_WRITE_BC2434A1);
      if (failure != null) throw failure;
      assertEquals(BOOT, boot);
      assertEquals(EPOCH, epoch);
      assertEquals(ACTIVATION, activation);
      written = new Epoch(State.INVALID, boot, epoch, activation, Optional.empty());
      return returnedOverride != null ? returnedOverride : written;
    }

    @Override
    public Epoch current() {
      events.add("readback");
      return readOverride != null ? readOverride : written;
    }
  }

  @Test
  void minvalid001DurableSameRunInvalidBeforeReturningToParent() throws Exception {
    var store = new Store();
    var events = store.events;
    Epoch result =
        MorningCurrentInvalidation.invalidate(
            () -> events.add("root"), store, BOOT, () -> EPOCH, PENDING);
    assertEquals(new Epoch(State.INVALID, BOOT, EPOCH, ACTIVATION, Optional.empty()), result);
    assertEquals(List.of("root", FIXTURE_WRITE_BC2434A1, "readback", "root"), events);
  }

  @Test
  void minvalid002CompletedOriginalCannotBeInvalidated() {
    var store = new Store();
    var complete =
        new MaintenanceRunState(
            ACTIVATION,
            Optional.of(
                new MaintenanceCompletion(
                    ACTIVATION,
                    Instant.parse("2026-09-28T05:00:01Z"),
                    MaintenanceCompletion.Outcome.SUCCESS)));
    assertThrows(
        IOException.class,
        () -> MorningCurrentInvalidation.invalidate(() -> {}, store, BOOT, () -> EPOCH, complete));
    assertTrue(store.events.isEmpty());
  }

  @Test
  void minvalid003RootFailureOrWriteFailureDoesNotContinue() {
    var store = new Store();
    var gate = new IOException("root unavailable");
    assertSame(
        gate,
        assertThrows(
            IOException.class,
            () ->
                MorningCurrentInvalidation.invalidate(
                    () -> {
                      throw gate;
                    },
                    store,
                    BOOT,
                    () -> EPOCH,
                    PENDING)));
    assertTrue(store.events.isEmpty());
    store.failure = new IOException("write unavailable");
    assertSame(
        store.failure,
        assertThrows(
            IOException.class,
            () ->
                MorningCurrentInvalidation.invalidate(
                    () -> {}, store, BOOT, () -> EPOCH, PENDING)));
    assertEquals(List.of(FIXTURE_WRITE_BC2434A1), store.events);
  }

  @Test
  void minvalid004WrongReadbackCannotBecomeSuccess() {
    var store = new Store();
    store.readOverride = new Epoch(State.INVALID, BOOT, RUN, ACTIVATION, Optional.empty());
    assertThrows(
        IOException.class,
        () -> MorningCurrentInvalidation.invalidate(() -> {}, store, BOOT, () -> EPOCH, PENDING));
    assertEquals(List.of(FIXTURE_WRITE_BC2434A1, "readback"), store.events);
    for (Epoch wrong :
        List.of(
            new Epoch(State.ISSUED, BOOT, EPOCH, ACTIVATION, Optional.of("a".repeat(64))),
            new Epoch(State.INVALID, RUN, EPOCH, ACTIVATION, Optional.empty()),
            new Epoch(State.INVALID, BOOT, RUN, ACTIVATION, Optional.empty()),
            new Epoch(
                State.INVALID,
                BOOT,
                EPOCH,
                new MaintenanceActivation(
                    new BatchRun(RUN, Instant.parse("2026-09-28T05:00:00Z")), EPOCH),
                Optional.empty()))) {
      var mismatch = new Store();
      mismatch.returnedOverride = wrong;
      assertThrows(
          IOException.class,
          () ->
              MorningCurrentInvalidation.invalidate(
                  () -> {}, mismatch, BOOT, () -> EPOCH, PENDING));
      assertEquals(List.of(FIXTURE_WRITE_BC2434A1), mismatch.events);
    }
  }

  @Test
  void minvalid005DuplicateOrNullEpochRejectedBeforeWrite() {
    for (UUID duplicate : List.of(BOOT, RUN, ACTIVE)) {
      var store = new Store();
      assertThrows(
          IOException.class,
          () ->
              MorningCurrentInvalidation.invalidate(
                  () -> {}, store, BOOT, () -> duplicate, PENDING));
      assertTrue(store.events.isEmpty());
    }
    var store = new Store();
    assertThrows(
        NullPointerException.class,
        () -> MorningCurrentInvalidation.invalidate(() -> {}, store, BOOT, () -> null, PENDING));
    assertTrue(store.events.isEmpty());
  }

  @Test
  void minvalid006WrongNativeActorAndNullContract() {
    var context = RootStartupContext.create();
    var wrong =
        new RootStartupContext.Snapshot(
            RootStartupContext.Service.CLEANUP,
            BOOT.toString(),
            "1".repeat(32),
            2,
            1,
            1,
            "/system.slice/schubert-nk-cleanup.service");
    assertThrows(
        IOException.class, () -> MorningCurrentInvalidation.invalidate(context, wrong, PENDING));
    assertThrows(
        NullPointerException.class,
        () -> MorningCurrentInvalidation.invalidate(null, wrong, PENDING));
    assertThrows(
        NullPointerException.class,
        () -> MorningCurrentInvalidation.invalidate(context, null, PENDING));
    assertThrows(
        NullPointerException.class,
        () -> MorningCurrentInvalidation.invalidate(context, wrong, null));
    var store = new Store();
    assertThrows(
        NullPointerException.class,
        () -> MorningCurrentInvalidation.invalidate(null, store, BOOT, () -> EPOCH, PENDING));
    assertThrows(
        NullPointerException.class,
        () -> MorningCurrentInvalidation.invalidate(() -> {}, null, BOOT, () -> EPOCH, PENDING));
    assertThrows(
        NullPointerException.class,
        () -> MorningCurrentInvalidation.invalidate(() -> {}, store, null, () -> EPOCH, PENDING));
    assertThrows(
        NullPointerException.class,
        () -> MorningCurrentInvalidation.invalidate(() -> {}, store, BOOT, null, PENDING));
    assertThrows(
        NullPointerException.class,
        () -> MorningCurrentInvalidation.invalidate(() -> {}, store, BOOT, () -> EPOCH, null));
  }
}

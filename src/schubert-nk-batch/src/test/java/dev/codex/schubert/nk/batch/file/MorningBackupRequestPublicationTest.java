package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.batch.platform.BackupWorkerRequest;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import java.io.IOException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/BAK001/UI251/SS341/343/SSC092/094/104; PT-OPS-MBPUB001-006. */
final class MorningBackupRequestPublicationTest {
  private static final UUID RUN = UUID.fromString("11111111-1111-4111-8111-111111111111");
  private static final UUID PART = UUID.fromString("33333333-3333-4333-8333-333333333333");
  private static final BackupWorkerRequest REQUEST =
      new BackupWorkerRequest(RUN, Instant.parse("2026-09-28T01:00:01.123456Z"));

  @Test
  void mbpub1425001NonMorningFactoryAndNullProofCannotOpenRequestRoot() {
    var context = RootStartupContext.create();
    for (var service :
        List.of(
            RootStartupContext.Service.API,
            RootStartupContext.Service.WEB,
            RootStartupContext.Service.CLEANUP,
            RootStartupContext.Service.EXPIRY)) {
      var wrong =
          new RootStartupContext.Snapshot(
              service, RUN.toString(), "1".repeat(32), 2, 1, 1, "/system.slice/" + service.unit());
      assertEquals(
          "Morning backup request unavailable",
          assertThrows(
                  IOException.class, () -> MorningBackupRequestPublication.create(context, wrong))
              .getMessage());
      assertEquals(
          "Morning backup request unavailable",
          assertThrows(
                  IOException.class,
                  () -> MorningBackupRequestPublication.create(context, wrong, Optional.empty()))
              .getMessage());
      assertThrows(
          NullPointerException.class,
          () -> MorningBackupRequestPublication.create(context, wrong, null));
      assertThrows(
          NullPointerException.class,
          () -> MorningBackupRequestPublication.create(null, wrong, Optional.empty()));
    }
    assertThrows(
        NullPointerException.class, () -> MorningBackupRequestPublication.create(context, null));
    assertThrows(
        NullPointerException.class,
        () -> MorningBackupRequestPublication.create(context, null, Optional.empty()));
  }

  private static final class FakeOwner implements MorningBackupRequestPublication.Owner {
    final List<String> events;
    IOException prepareFailure;
    IOException closeFailure;

    FakeOwner(List<String> events) {
      this.events = events;
    }

    @Override
    public void prepare(BackupWorkerRequest request, UUID part) throws IOException {
      assertSame(REQUEST, request);
      assertEquals(PART, part);
      events.add("prepare-new-only");
      if (prepareFailure != null) throw prepareFailure;
    }

    @Override
    public void close() throws IOException {
      events.add("close");
      if (closeFailure != null) throw closeFailure;
    }
  }

  @Test
  void mbpub001RootRecheckSurroundsOwnedPublicationAndClose() throws Exception {
    var events = new ArrayList<String>();
    var owner = new FakeOwner(events);
    var subject =
        new MorningBackupRequestPublication(
            () -> events.add("root"),
            () -> {
              events.add("open-fixed");
              return owner;
            });
    subject.publish(REQUEST, PART);
    assertEquals(
        List.of("root", "open-fixed", "root", "prepare-new-only", "root", "close", "root"), events);
  }

  @Test
  void mbpub002RootRefusalBeforeOpenDoesNotAcquireOwner() {
    var events = new ArrayList<String>();
    var subject =
        new MorningBackupRequestPublication(
            () -> {
              events.add("root-refuse");
              throw new IOException("raw root detail");
            },
            () -> fail("no open"));
    assertEquals(
        "Morning backup request unavailable",
        assertThrows(IOException.class, () -> subject.publish(REQUEST, PART)).getMessage());
    assertEquals(List.of("root-refuse"), events);
  }

  @Test
  void mbpub003OpenFailureOrNullOwnerNeverPrepares() {
    var failure = new IOException("raw path");
    var refused =
        new MorningBackupRequestPublication(
            () -> {},
            () -> {
              throw failure;
            });
    assertEquals(
        "Morning backup request unavailable",
        assertThrows(IOException.class, () -> refused.publish(REQUEST, PART)).getMessage());
    var missing = new MorningBackupRequestPublication(() -> {}, () -> null);
    assertThrows(NullPointerException.class, () -> missing.publish(REQUEST, PART));
  }

  @Test
  void mbpub004PreparationPostcheckAndCloseFailuresNeverSucceed() {
    var events = new ArrayList<String>();
    var owner = new FakeOwner(events);
    owner.prepareFailure = new IOException("raw file name");
    var subject = new MorningBackupRequestPublication(() -> events.add("root"), () -> owner);
    assertEquals(
        "Morning backup request unavailable",
        assertThrows(IOException.class, () -> subject.publish(REQUEST, PART)).getMessage());
    assertEquals(List.of("root", "root", "prepare-new-only", "close"), events);

    events.clear();
    owner.prepareFailure = null;
    var checks = new AtomicInteger();
    var late =
        new MorningBackupRequestPublication(
            () -> {
              events.add("root");
              if (checks.incrementAndGet() == 3) throw new IOException("raw");
            },
            () -> owner);
    assertThrows(IOException.class, () -> late.publish(REQUEST, PART));
    assertEquals(List.of("root", "root", "prepare-new-only", "root", "close"), events);

    events.clear();
    owner.closeFailure = new IOException("raw close");
    assertEquals(
        "Morning backup request unavailable",
        assertThrows(IOException.class, () -> subject.publish(REQUEST, PART)).getMessage());
    assertEquals(List.of("root", "root", "prepare-new-only", "root", "close"), events);
  }

  @Test
  void mbpub005ExistingRequestCannotBeRepairedByPublisher() {
    var events = new ArrayList<String>();
    var owner = new FakeOwner(events);
    owner.prepareFailure = new IOException("existing file");
    var subject = new MorningBackupRequestPublication(() -> events.add("root"), () -> owner);
    assertThrows(IOException.class, () -> subject.publish(REQUEST, PART));
    assertEquals(List.of("root", "root", "prepare-new-only", "close"), events);
  }

  @Test
  void mbpub006NullAndInterruptRefuseBeforeIo() {
    var events = new ArrayList<String>();
    assertThrows(
        NullPointerException.class,
        () -> new MorningBackupRequestPublication(null, () -> fail("no open")));
    assertThrows(
        NullPointerException.class,
        () -> new MorningBackupRequestPublication(() -> fail("no root"), null));
    var subject =
        new MorningBackupRequestPublication(() -> events.add("root"), () -> fail("no open"));
    assertThrows(NullPointerException.class, () -> subject.publish(null, PART));
    assertThrows(NullPointerException.class, () -> subject.publish(REQUEST, null));
    assertTrue(events.isEmpty());
    Thread.currentThread().interrupt();
    try {
      assertEquals(
          "Morning backup request unavailable",
          assertThrows(IOException.class, () -> subject.publish(REQUEST, PART)).getMessage());
      assertTrue(events.isEmpty());
    } finally {
      Thread.interrupted();
    }
  }
}

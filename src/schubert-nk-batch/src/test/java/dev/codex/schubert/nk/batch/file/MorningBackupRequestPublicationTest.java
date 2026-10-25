package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.batch.platform.BackupWorkerRequest;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-OPS-001/OPS009/BAK001/UI251/SS341/343/SSC092/094/104; PT-OPS-MBPUB001-006. */
final class MorningBackupRequestPublicationTest {
  private static final UUID RUN = UUID.fromString("11111111-1111-4111-8111-111111111111");
  private static final UUID PART = UUID.fromString("33333333-3333-4333-8333-333333333333");
  private static final BackupWorkerRequest REQUEST =
      new BackupWorkerRequest(RUN, Instant.parse("2026-09-28T01:00:01.123456Z"));

  @Test
  void mbpub007FactoryAndNullPortsRefuseBeforeAssembly() {
    var opens = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () -> MorningBackupRequestPublication.openOwned(null, directory -> fail("no assembly")));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningBackupRequestPublication.openOwned(
                () -> {
                  opens.incrementAndGet();
                  return null;
                },
                null));
    assertEquals(0, opens.get());
    IOException original = new IOException("synthetic open failure");
    assertSame(
        original,
        assertThrows(
            IOException.class,
            () ->
                MorningBackupRequestPublication.openOwned(
                    () -> {
                      throw original;
                    },
                    directory -> fail("no assembly"))));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningBackupRequestPublication.openOwned(
                () -> null, directory -> fail("no assembly")));
  }

  @Test
  void mbpub008CompleteOwnerTakesOverDirectoryExactlyOnce(@TempDir Path temporary)
      throws Exception {
    var events = new ArrayList<String>();
    try (var fixture = new BackupPublicationFixture(temporary)) {
      var owner =
          MorningBackupRequestPublication.openOwned(
              () -> {
                events.add("open");
                return fixture.root;
              },
              directory -> {
                assertSame(fixture.root, directory);
                events.add("assemble");
                return new MorningBackupRequestPublication.Owner() {
                  @Override
                  public void prepare(BackupWorkerRequest request, UUID part) {
                    assertSame(REQUEST, request);
                    assertEquals(PART, part);
                    events.add("prepare");
                  }

                  @Override
                  public void close() throws IOException {
                    events.add("owned-close");
                    directory.close();
                  }
                };
              });
      assertEquals(List.of("open", "assemble"), events);
      assertEquals(0, fixture.counts.getOrDefault("close", 0));
      assertFalse(fixture.descriptors.isEmpty());
      try (owner) {
        owner.prepare(REQUEST, PART);
      }
      assertEquals(List.of("open", "assemble", "prepare", "owned-close"), events);
      assertEquals(1, fixture.counts.get("close"));
      assertTrue(fixture.descriptors.isEmpty());
    }
  }

  @Test
  void mbpub009IncompleteAssemblyAlwaysReleasesDirectory(@TempDir Path temporary) throws Exception {
    Throwable[] failures = {
      new IOException("synthetic IO"),
      new IllegalStateException("synthetic runtime"),
      new AssertionError("synthetic error"),
      null
    };
    for (var failure : failures) {
      try (var fixture = new BackupPublicationFixture(temporary)) {
        var actual =
            assertThrows(
                Throwable.class,
                () ->
                    MorningBackupRequestPublication.openOwned(
                        () -> fixture.root,
                        directory -> {
                          assertSame(fixture.root, directory);
                          if (failure instanceof IOException value) throw value;
                          if (failure instanceof RuntimeException value) throw value;
                          if (failure instanceof Error value) throw value;
                          return null;
                        }));
        if (failure instanceof IOException) {
          assertInstanceOf(StorageIoException.class, actual);
          assertEquals(
              StorageIoException.Reason.UNAVAILABLE, ((StorageIoException) actual).reason());
        } else if (failure != null) assertSame(failure, actual);
        else assertInstanceOf(NullPointerException.class, actual);
        assertEquals(1, fixture.counts.get("close"));
        assertTrue(fixture.descriptors.isEmpty());
      }
    }
  }

  @Test
  void mbpub010AssemblyCloseMatrixPreservesIndependentFailurePriority(@TempDir Path temporary)
      throws Exception {
    String[][] expected = {
      {"IO", "CLOSE", "CLOSE"}, {"PRIMARY", "PRIMARY", "PRIMARY"}, {"PRIMARY", "PRIMARY", "PRIMARY"}
    };
    for (int p = 0; p < 3; p++) {
      for (int c = 0; c < 3; c++) {
        Throwable[] primary = {
          new IOException("primary IO"),
          new IllegalStateException("primary runtime"),
          new AssertionError("primary error")
        };
        Throwable[] closing = {
          new IOException("close IO"),
          new IllegalArgumentException("close runtime"),
          new AssertionError("close error")
        };
        Throwable before = primary[p];
        Throwable after = closing[c];
        try (var fixture = new BackupPublicationFixture(temporary)) {
          fixture.faults.put("close#1", after);
          var actual =
              assertThrows(
                  Throwable.class,
                  () ->
                      MorningBackupRequestPublication.openOwned(
                          () -> fixture.root,
                          directory -> {
                            if (before instanceof IOException value) throw value;
                            if (before instanceof RuntimeException value) throw value;
                            throw (Error) before;
                          }));
          switch (expected[p][c]) {
            case "IO" -> {
              assertInstanceOf(StorageIoException.class, actual);
              assertEquals(
                  StorageIoException.Reason.UNAVAILABLE, ((StorageIoException) actual).reason());
              assertNotSame(before, actual);
              assertNotSame(after, actual);
            }
            case "CLOSE" -> {
              assertSame(after, actual);
              assertEquals(0, actual.getSuppressed().length);
            }
            case "PRIMARY" -> {
              assertSame(before, actual);
              assertEquals(1, actual.getSuppressed().length);
              assertInstanceOf(StorageIoException.class, actual.getSuppressed()[0]);
              assertNotSame(after, actual.getSuppressed()[0]);
            }
            default -> fail("literal matrix only");
          }
          assertEquals(1, fixture.counts.get("close"));
          assertTrue(fixture.descriptors.isEmpty());
        }
      }
    }
  }

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

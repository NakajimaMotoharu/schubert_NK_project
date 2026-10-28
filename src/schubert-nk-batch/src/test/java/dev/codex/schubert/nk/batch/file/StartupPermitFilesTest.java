package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.file.StartupPermitFiles.IssuePhase;
import dev.codex.schubert.nk.batch.file.StartupPermitRecords.Epoch;
import dev.codex.schubert.nk.batch.file.StartupPermitRecords.Permit;
import dev.codex.schubert.nk.batch.file.StartupPermitRecords.State;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.function.BiConsumer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/** PT-OPS-PERMITFILE001..008; SS343 SSC089; real Linux FD IO, explicitly synthetic root/tmpfs. */
final class StartupPermitFilesTest {
  private static final String FIXTURE_PUBLIC_B7853257 = "public";
  private static final String FIXTURE_REPLACE_197D1A17 = "replace";
  private static final String FIXTURE_DIR_16E08808 = "dir";
  private static final String FIXTURE_FILE_BFDDE6F5 = "file";
  private static final String FIXTURE_MODE_B6D5C2C3 = "mode";
  private static final String FIXTURE_UID_0C18F38C = "uid";
  private static final String FIXTURE_GID_0ACDD642 = "gid";
  private static final String FIXTURE_SIZE_EB1E91E4 = "size";
  private static final String FIXTURE_INO_4BE7C1E0 = "ino";
  private static final String FIXTURE_ATTRIBUTES_D300E055 = "attributes";
  private static final String FIXTURE_NEW_80270E39 = "new";
  private static final String FIXTURE_CURRENT_694DF57A = "current";
  private static final String FIXTURE_READ_6F365882 = "read";
  private static final String FIXTURE_A_CLOSE_B364A3FB = "A-close";
  private static final String FIXTURE_RETIRE_A2A9D4FF = "retire";
  private static final String FIXTURE_INTENT_CLOSE_B54EC48E = "intent-close";
  private static final UUID BOOT = UUID.fromString("11111111-1111-1111-1111-111111111111");
  private static final UUID EPOCH = UUID.fromString("33333333-3333-3333-3333-333333333333");
  private static final UUID RUN = UUID.fromString("44444444-4444-4444-4444-444444444444");
  private static final UUID ACT = UUID.fromString("55555555-5555-5555-5555-555555555555");
  private static final MaintenanceActivation ACTIVE =
      new MaintenanceActivation(new BatchRun(RUN, Instant.parse("2026-09-27T00:00:00Z")), ACT);
  private static final String BIND =
      "boot_id=11111111-1111-1111-1111-111111111111\n"
          + "epoch_id=33333333-3333-3333-3333-333333333333\n"
          + "run_id=44444444-4444-4444-4444-444444444444\n"
          + "cutoff_utc=2026-09-27T00:00:00.000000Z\n"
          + "activation_id=55555555-5555-5555-5555-555555555555\n";
  private static final String INVALID = "NKEPOCH1\nstate=INVALID\n" + BIND + "permit_sha256=-\n";
  private static final String GOLD =
      "NKPERMIT1\n"
          + BIND
          + "broker_invocation_id="
          + "2".repeat(32)
          + "\nrelease_sha256="
          + "b".repeat(64)
          + "\napi_config_sha256="
          + "c".repeat(64)
          + "\nweb_config_sha256="
          + "d".repeat(64)
          + "\nroots_sha256="
          + "e".repeat(64)
          + "\nprestart_steps_sha256="
          + "f".repeat(64)
          + "\n";

  private static Permit permit() {
    return new Permit(
        BOOT,
        EPOCH,
        ACTIVE,
        "2".repeat(32),
        "b".repeat(64),
        "c".repeat(64),
        "d".repeat(64),
        "e".repeat(64),
        "f".repeat(64));
  }

  private static Epoch invalid() {
    return new Epoch(State.INVALID, BOOT, EPOCH, ACTIVE, Optional.empty());
  }

  @TempDir Path temporary;

  private Fixture fixture() throws Exception {
    return new Fixture(Files.createTempDirectory(temporary, "permit-"));
  }

  private static void fail(Executable work) {
    var error = assertThrows(StorageIoException.class, work);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, error.reason());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
    assertEquals("transfer storage operation failed", error.getMessage());
  }

  @Test
  void isspub001ThreeActualProofBoundariesAndSameEpochRevoke() throws Exception {
    try (var f = fixture()) {
      f.seed(INVALID);
      var phases = new ArrayList<StartupPermitFiles.IssuePhase>();
      Epoch issued =
          f.store.issue(
              invalid(),
              permit(),
              (phase, expected) -> {
                phases.add(phase);
                assertEquals(expected, f.store.current());
                if (phase == StartupPermitFiles.IssuePhase.BEFORE_PUBLICATION) {
                  assertFalse(Files.exists(f.permit));
                  assertEquals(INVALID, Files.readString(f.current));
                } else {
                  assertEquals(GOLD, Files.readString(f.permit));
                  assertEquals(
                      phase == StartupPermitFiles.IssuePhase.AFTER_READBACK,
                      expected.state() == State.ISSUED);
                }
              });
      assertEquals(
          List.of(
              StartupPermitFiles.IssuePhase.BEFORE_PUBLICATION,
              StartupPermitFiles.IssuePhase.BEFORE_ISSUED,
              StartupPermitFiles.IssuePhase.AFTER_READBACK),
          phases);
      assertEquals(issued, f.store.current());
      assertEquals(invalid(), f.store.revoke(invalid(), permit()));
      assertEquals(INVALID, Files.readString(f.current));
      assertEquals(GOLD, Files.readString(f.permit));
      fail(f.store::readIssued);
      assertEquals(invalid(), f.store.revoke(invalid(), permit()));
      assertEquals(GOLD, Files.readString(f.permit));
    }
  }

  @Test
  void isspub002EachProofFailurePreservesFilesAndUnknownIdentity() throws Exception {
    for (var stop : StartupPermitFiles.IssuePhase.values()) {
      for (boolean unknown : List.of(false, true)) {
        try (var f = fixture()) {
          f.seed(INVALID);
          var failure = new IllegalStateException("PRIVATE_PROOF");
          Executable action =
              () ->
                  f.store.issue(
                      invalid(),
                      permit(),
                      (phase, expected) -> {
                        if (phase == stop) {
                          if (unknown) throw failure;
                          throw new IOException("PRIVATE_PROOF");
                        }
                      });
          if (unknown) assertSame(failure, assertThrows(IllegalStateException.class, action));
          else fail(action);
          boolean published = stop != StartupPermitFiles.IssuePhase.BEFORE_PUBLICATION;
          assertEquals(published, Files.exists(f.permit));
          if (published) assertEquals(GOLD, Files.readString(f.permit));
          else {
            try (var entries = Files.list(f.directory)) {
              assertEquals(
                  1, entries.filter(p -> p.getFileName().toString().endsWith(".part")).count());
            }
          }
          assertEquals(invalid(), f.store.revoke(invalid(), permit()));
          assertEquals(INVALID, Files.readString(f.current));
          assertEquals(published, Files.exists(f.permit));
        }
      }
    }
  }

  @Test
  void isspub003ProofDriftAndForeignRevokeNeverRepairOriginal() throws Exception {
    for (var stop : StartupPermitFiles.IssuePhase.values()) {
      try (var f = fixture()) {
        f.seed(INVALID);
        fail(
            () ->
                f.store.issue(
                    invalid(),
                    permit(),
                    (phase, expected) -> {
                      if (phase == stop) Files.writeString(f.current, "CORRUPTED\n");
                    }));
        assertEquals("CORRUPTED\n", Files.readString(f.current));
        fail(() -> f.store.revoke(invalid(), permit()));
        assertEquals("CORRUPTED\n", Files.readString(f.current));
      }
    }
    try (var f = fixture()) {
      f.seed(INVALID);
      Epoch issued = f.store.issue(invalid(), permit());
      String before = Files.readString(f.current);
      fail(() -> f.store.revoke(issued, permit()));
      var other =
          new Permit(
              BOOT,
              ACT,
              ACTIVE,
              "2".repeat(32),
              "b".repeat(64),
              "c".repeat(64),
              "d".repeat(64),
              "e".repeat(64),
              "f".repeat(64));
      fail(() -> f.store.revoke(invalid(), other));
      var changed =
          new Permit(
              BOOT,
              EPOCH,
              ACTIVE,
              "3".repeat(32),
              "b".repeat(64),
              "c".repeat(64),
              "d".repeat(64),
              "e".repeat(64),
              "f".repeat(64));
      fail(() -> f.store.revoke(invalid(), changed));
      assertEquals(before, Files.readString(f.current));
      assertEquals(GOLD, Files.readString(f.permit));
      for (var foreign :
          List.of(
              new Permit(
                  ACT,
                  EPOCH,
                  ACTIVE,
                  "2".repeat(32),
                  "b".repeat(64),
                  "c".repeat(64),
                  "d".repeat(64),
                  "e".repeat(64),
                  "f".repeat(64)),
              new Permit(
                  BOOT,
                  EPOCH,
                  new MaintenanceActivation(ACTIVE.run(), EPOCH),
                  "2".repeat(32),
                  "b".repeat(64),
                  "c".repeat(64),
                  "d".repeat(64),
                  "e".repeat(64),
                  "f".repeat(64)))) fail(() -> f.store.revoke(invalid(), foreign));
      assertThrows(NullPointerException.class, () -> f.store.revoke(null, permit()));
      assertThrows(NullPointerException.class, () -> f.store.revoke(invalid(), null));
      assertThrows(NullPointerException.class, () -> f.store.issue(invalid(), permit(), null));
    }
  }

  @Test
  void isspub004PendingPublicationIsNotAReadableRootPermit() throws Exception {
    try (var f = fixture()) {
      f.seed(INVALID);
      Path marker = f.directory.resolve("permit-start.intent");
      Files.createFile(marker);
      f.store.issue(
          invalid(),
          permit(),
          (phase, expected) -> {
            if (phase == StartupPermitFiles.IssuePhase.AFTER_READBACK) {
              assertEquals(State.ISSUED, f.store.current().state());
              fail(f.store::readIssued);
            }
          });
      fail(f.store::readIssued);
      assertTrue(Files.exists(marker));
      assertEquals(GOLD, Files.readString(f.permit));
      f.store.revoke(invalid(), permit());
      assertEquals(INVALID, Files.readString(f.current));
      assertTrue(Files.exists(marker));
    }
  }

  @Test
  void originalsAndPublicationOrder() throws Exception {
    try (var f = fixture()) {
      Epoch current = f.store.invalidate(BOOT, EPOCH, ACTIVE);
      assertEquals(INVALID, Files.readString(f.current));
      assertEquals(invalid(), current);
      fail(f.store::readIssued);
      f.reset();
      Epoch issued = f.store.issue(current, permit());
      String digest =
          HexFormat.of()
              .formatHex(
                  MessageDigest.getInstance("SHA-256")
                      .digest(GOLD.getBytes(java.nio.charset.StandardCharsets.US_ASCII)));
      assertEquals(
          "NKEPOCH1\nstate=ISSUED\n" + BIND + "permit_sha256=" + digest + "\n",
          Files.readString(f.current));
      assertEquals(GOLD, Files.readString(f.permit));
      assertEquals(issued, f.store.current());
      assertEquals(permit(), f.store.readIssued());
      assertTrue(f.events.indexOf("force") < f.events.indexOf("publish"));
      assertTrue(f.events.indexOf("publish") < f.events.indexOf(FIXTURE_REPLACE_197D1A17));
      assertEquals(0100600, Files.getAttribute(f.current, "unix:mode"));
      assertEquals(1, Files.getAttribute(f.permit, "unix:nlink"));
      f.released();
      f.store.invalidate(BOOT, ACT, ACTIVE);
      assertEquals(State.INVALID, f.store.current().state());
      assertEquals(GOLD, Files.readString(f.permit));
      fail(f.store::readIssued);
    }
  }

  @Test
  void missingCorruptAndWrongBindings() throws Exception {
    try (var f = fixture()) {
      fail(f.store::current);
      fail(f.store::readIssued);
      fail(() -> f.store.issue(invalid(), permit()));
    }
    for (String bad :
        List.of("corrupt", INVALID.replace("INVALID", "unknown"), "x".repeat(8193), ""))
      try (var f = fixture()) {
        f.seed(bad);
        fail(() -> f.store.invalidate(BOOT, EPOCH, ACTIVE));
        assertEquals(bad, Files.readString(f.current));
      }
    for (Permit wrong :
        List.of(
            new Permit(
                ACT,
                EPOCH,
                ACTIVE,
                "2".repeat(32),
                "b".repeat(64),
                "c".repeat(64),
                "d".repeat(64),
                "e".repeat(64),
                "f".repeat(64)),
            new Permit(
                BOOT,
                ACT,
                ACTIVE,
                "2".repeat(32),
                "b".repeat(64),
                "c".repeat(64),
                "d".repeat(64),
                "e".repeat(64),
                "f".repeat(64)),
            new Permit(
                BOOT,
                EPOCH,
                new MaintenanceActivation(ACTIVE.run(), EPOCH),
                "2".repeat(32),
                "b".repeat(64),
                "c".repeat(64),
                "d".repeat(64),
                "e".repeat(64),
                "f".repeat(64))))
      try (var f = fixture()) {
        f.seed(INVALID);
        fail(() -> f.store.issue(invalid(), wrong));
        assertEquals(0, f.count("create"));
      }
    try (var f = fixture()) {
      f.seed(INVALID);
      fail(() -> f.store.invalidate(BOOT, EPOCH, ACTIVE));
      fail(() -> f.store.issue(invalid().issued("a".repeat(64)), permit()));
      f.store.issue(invalid(), permit());
      fail(() -> f.store.issue(invalid(), permit()));
      Files.writeString(f.permit, GOLD.replace("2".repeat(32), "3".repeat(32)));
      fail(f.store::readIssued);
      Files.writeString(f.current, INVALID);
      fail(f.store::readIssued);
    }
    try (var f = fixture()) {
      f.seed(INVALID.replace(EPOCH.toString(), ACT.toString()));
      fail(() -> f.store.issue(invalid(), permit()));
      assertEquals(0, f.count("create"));
    }
  }

  @Test
  void metadataAndSecurityMatrix() throws Exception {
    for (String role : List.of(FIXTURE_DIR_16E08808, FIXTURE_FILE_BFDDE6F5))
      for (String key :
          List.of(
              FIXTURE_MODE_B6D5C2C3,
              FIXTURE_UID_0C18F38C,
              FIXTURE_GID_0ACDD642,
              "nlink",
              FIXTURE_SIZE_EB1E91E4,
              "dev",
              FIXTURE_INO_4BE7C1E0,
              "lastModifiedTime",
              "ctime"))
        for (Object wrong : List.of("wrong type", -1))
          try (var f = fixture()) {
            f.seed(INVALID);
            f.mutate =
                (kind, values) -> {
                  if (kind.equals(role)) values.put(key, wrong);
                };
            fail(f.store::current);
          }
    for (String role : List.of(FIXTURE_DIR_16E08808, FIXTURE_FILE_BFDDE6F5))
      for (String bad :
          List.of(
              FIXTURE_UID_0C18F38C,
              FIXTURE_GID_0ACDD642,
              FIXTURE_MODE_B6D5C2C3,
              "links",
              FIXTURE_SIZE_EB1E91E4,
              "nullAttributes",
              "acl",
              "nullAcl",
              "filesystem",
              "nullFilesystem",
              "readonly"))
        try (var f = fixture()) {
          f.seed(INVALID);
          f.badRole = role;
          f.bad = bad;
          fail(f.store::current);
        }
    try (var f = fixture()) {
      f.uid = 1;
      fail(f.store::current);
      fail(() -> f.store.invalidate(BOOT, EPOCH, ACTIVE));
      assertEquals(0, f.count(FIXTURE_ATTRIBUTES_D300E055));
    }
    try (var f = fixture()) {
      f.seed(INVALID);
      f.mutate =
          (role, m) -> {
            if (role.equals(FIXTURE_FILE_BFDDE6F5)) m.put("dev", -17L);
          };
      fail(f.store::current);
    }
  }

  @Test
  void everyOwnedIoFaultAndUncertainPublication() throws Exception {
    try (var f = fixture()) {
      f.mutate =
          (role, m) -> {
            if (role.equals(FIXTURE_FILE_BFDDE6F5)) m.put(FIXTURE_SIZE_EB1E91E4, 1L);
          };
      fail(() -> f.store.invalidate(BOOT, EPOCH, ACTIVE));
      assertEquals(0, f.count("openWriter"));
    }
    try (var f = fixture()) {
      f.seed(INVALID);
      f.behavior = "fill";
      fail(f.store::current);
      f.released();
    }
    // Instrument each actual acquired owner/IO position; failures must never yield a result.
    for (String operation :
        List.of(
            FIXTURE_NEW_80270E39,
            FIXTURE_REPLACE_197D1A17,
            "issue",
            FIXTURE_CURRENT_694DF57A,
            FIXTURE_READ_6F365882)) {
      Map<String, Integer> inventory;
      try (var f = fixture()) {
        f.setup(operation);
        f.run(operation);
        inventory = new HashMap<>(f.counts);
        f.released();
      }
      for (var event : inventory.entrySet())
        for (int i = 1; i <= event.getValue(); i++)
          try (var f = fixture()) {
            f.setup(operation);
            f.fail = event.getKey();
            f.failAt = i;
            fail(() -> f.run(operation));
            f.released();
          }
    }
    try (var f = fixture()) {
      f.seed(INVALID);
      f.fail = "sync";
      f.failAt = 1;
      fail(() -> f.store.issue(invalid(), permit()));
      assertEquals(GOLD, Files.readString(f.permit));
      assertEquals(INVALID, Files.readString(f.current));
    }
    try (var f = fixture()) {
      f.seed(INVALID);
      f.digestFailure = true;
      fail(() -> f.store.issue(invalid(), permit()));
      assertEquals(GOLD, Files.readString(f.permit));
      assertEquals(INVALID, Files.readString(f.current));
    }
    for (String operation : List.of(FIXTURE_NEW_80270E39, FIXTURE_CURRENT_694DF57A))
      for (String behavior : List.of("zero", "negative", "overflow", "position", "short"))
        try (var f = fixture()) {
          f.setup(operation);
          f.behavior = behavior;
          fail(() -> f.run(operation));
          f.released();
        }
    for (String operation : List.of(FIXTURE_NEW_80270E39, FIXTURE_CURRENT_694DF57A))
      for (int at : List.of(1, 2, 3))
        try (var f = fixture()) {
          f.setup(operation);
          f.wrongSizeAt = at;
          if (operation.equals(FIXTURE_CURRENT_694DF57A) && at == 3) continue;
          fail(() -> f.run(operation));
          f.released();
        }
    for (boolean writer : List.of(false, true))
      try (var f = fixture()) {
        if (!writer) f.seed(INVALID);
        f.nullWriter = writer;
        f.nullReader = !writer;
        if (writer) fail(() -> f.store.invalidate(BOOT, EPOCH, ACTIVE));
        else fail(f.store::current);
      }
  }

  @Test
  void inodeChangesAndNoRepair() throws Exception {
    try (var f = fixture()) {
      Files.createSymbolicLink(f.current, Path.of("absent"));
      fail(f.store::current);
      fail(() -> f.store.invalidate(BOOT, EPOCH, ACTIVE));
      assertTrue(Files.isSymbolicLink(f.current));
    }
    try (var f = fixture()) {
      f.seed(INVALID);
      Files.writeString(f.permit, GOLD);
      fail(() -> f.store.issue(invalid(), permit()));
      assertEquals(INVALID, Files.readString(f.current));
      assertEquals(GOLD, Files.readString(f.permit));
    }
    for (String key : List.of(FIXTURE_INO_4BE7C1E0, "lastModifiedTime", "ctime"))
      try (var f = fixture()) {
        f.seed(INVALID);
        f.mutate =
            (role, m) -> {
              if (role.equals(FIXTURE_FILE_BFDDE6F5) && f.count(FIXTURE_ATTRIBUTES_D300E055) >= 3)
                m.put(
                    key,
                    key.equals(FIXTURE_INO_4BE7C1E0)
                        ? 888L
                        : java.nio.file.attribute.FileTime.fromMillis(0));
            };
        fail(f.store::current);
      }
    try (var f = fixture()) {
      f.seed(INVALID);
      f.mutate =
          (role, m) -> {
            if (role.equals(FIXTURE_DIR_16E08808) && f.count(FIXTURE_ATTRIBUTES_D300E055) > 3)
              m.put(FIXTURE_INO_4BE7C1E0, 999L);
          };
      fail(f.store::current);
    }
    try (var f = fixture()) {
      f.seed(INVALID);
      f.replaceFailure = true;
      fail(() -> f.store.invalidate(BOOT, ACT, ACTIVE));
      assertEquals(INVALID, Files.readString(f.current));
    }
  }

  @Test
  void interruptionNullAndUnknownIdentity() throws Exception {
    try (var f = fixture()) {
      assertThrows(NullPointerException.class, () -> new StartupPermitFiles(null, f));
      assertThrows(NullPointerException.class, () -> new StartupPermitFiles(f.root, null));
      assertThrows(NullPointerException.class, () -> new StartupPermitFiles(f.root, f, null, f));
      assertThrows(NullPointerException.class, () -> new StartupPermitFiles(f.root, f, f, null));
      assertThrows(NullPointerException.class, () -> f.store.issue(null, permit()));
      assertThrows(NullPointerException.class, () -> f.store.issue(invalid(), null));
      assertThrows(NullPointerException.class, () -> f.store.invalidate(null, EPOCH, ACTIVE));
      Thread.currentThread().interrupt();
      try {
        fail(f.store::current);
      } finally {
        Thread.interrupted();
      }
    }
    try (var f = fixture()) {
      f.seed(INVALID);
      RuntimeException sentinel = new IllegalStateException("public sentinel");
      f.unknown = sentinel;
      f.fail = FIXTURE_READ_6F365882;
      assertSame(sentinel, assertThrows(IllegalStateException.class, f.store::current));
      f.released();
    }
    try (var f = fixture()) {
      f.seed(INVALID);
      f.lateInterrupt = true;
      try {
        fail(f.store::current);
      } finally {
        Thread.interrupted();
      }
      f.released();
    }
  }

  @Test
  void concurrentSinglePublication() throws Exception {
    try (var f = fixture();
        var workers = Executors.newFixedThreadPool(4)) {
      f.seed(INVALID);
      var pending = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 16; i++)
        pending.add(
            () -> {
              try {
                f.store.issue(invalid(), permit());
                return true;
              } catch (StorageIoException expected) {
                return false;
              }
            });
      int winners = 0;
      for (var result : workers.invokeAll(pending)) if (result.get()) winners++;
      assertEquals(1, winners);
      assertEquals(GOLD, Files.readString(f.permit));
      assertEquals(permit(), f.store.readIssued());
      f.released();
    }
  }

  @Test
  void nativeIoAndBorrowedLifetime() throws Exception {
    try (var f = fixture()) {
      fail(
          () ->
              new StartupPermitFiles(f.root, LinuxInodeSecurity.create())
                  .invalidate(BOOT, EPOCH, ACTIVE));
      var nativeIo = new StartupPermitFiles.NioIo();
      f.seed(INVALID);
      assertNotNull(nativeIo.attributes(f.current));
      String filesystem = java.nio.file.Files.getFileStore(f.current).type();
      String expectedFilesystem =
          java.util.Set.of("ext2", "ext3", "ext4").contains(filesystem)
              ? "ext2/ext3/ext4"
              : filesystem;
      f.root.atExistingEntryHandle(
          f.current.getFileName().toString(),
          held -> {
            assertEquals(expectedFilesystem, nativeIo.filesystem(held));
            return true;
          });
      try (var channel = nativeIo.open(f.current)) {
        assertEquals(INVALID.length(), channel.size());
      }
      try (var writer = nativeIo.openWriter(f.current)) {
        assertEquals(INVALID.length(), writer.size());
        writer.force();
      }
      assertEquals("SHA-256", nativeIo.digest().getAlgorithm());
      Path part = f.directory.resolve("native.part");
      Files.writeString(part, "replacement");
      nativeIo.replace(f.directory, "native.part", "epoch.current");
      assertEquals("replacement", Files.readString(f.current));
      assertFalse(Files.exists(part));
      f.root.close();
      fail(f.store::current);
      fail(() -> f.store.invalidate(BOOT, EPOCH, ACTIVE));
    }
  }

  /** ISSPUB005: owner commit occurs only after all subordinate/A closes, not issue return. */
  @Test
  void isspub005SupervisedPublicationCommitAndStrictOwner() throws Exception {
    try (var f = fixture();
        var worker = Executors.newSingleThreadExecutor()) {
      f.seed(INVALID);
      var h = new PublicationHarness(f);
      var owner = h.owner();
      assertThrows(IOException.class, owner::expected);
      assertThrows(IOException.class, owner::commit);
      owner.bind(invalid());
      assertThrows(IOException.class, () -> owner.bind(invalid()));
      assertEquals(invalid(), owner.expected());
      assertThrows(ExecutionException.class, () -> worker.submit(owner::expected).get());
      var phases = new ArrayList<IssuePhase>();
      var issued =
          owner.issue(
              permit(),
              (phase, expected) -> {
                phases.add(phase);
                assertEquals(expected, owner.expected());
                assertTrue(Files.exists(h.marker));
                assertThrows(StorageIoException.class, f.store::readIssued);
              });
      assertEquals(
          List.of(
              IssuePhase.BEFORE_PUBLICATION, IssuePhase.BEFORE_ISSUED, IssuePhase.AFTER_READBACK),
          phases);
      assertEquals(GOLD, Files.readString(f.permit));
      assertEquals(issued, owner.expected());
      assertTrue(Files.exists(h.marker));
      assertEquals(1, h.storeCloses);
      h.events.add("nested-close");
      h.events.add(FIXTURE_A_CLOSE_B364A3FB);
      owner.commit();
      assertFalse(Files.exists(h.marker));
      assertEquals(permit(), f.store.readIssued());
      assertEquals(2, h.storeCloses);
      assertTrue(
          h.events.indexOf(FIXTURE_A_CLOSE_B364A3FB) < h.events.indexOf(FIXTURE_RETIRE_A2A9D4FF));
      assertTrue(
          h.events.indexOf(FIXTURE_RETIRE_A2A9D4FF)
              < h.events.indexOf(FIXTURE_INTENT_CLOSE_B54EC48E));
      assertThrows(IOException.class, owner::commit);
      assertThrows(IOException.class, () -> owner.issue(permit(), (p, e) -> {}));
      f.released();
    }
  }

  /** ISSPUB006: independent faults at actual publication and post-A close boundaries. */
  @Test
  void isspub006FaultsRevokeWithoutDeletingEvidenceAndUnknownRetains() throws Exception {
    for (String failure :
        List.of(
            "begin",
            "proof",
            "store-close",
            FIXTURE_A_CLOSE_B364A3FB,
            FIXTURE_RETIRE_A2A9D4FF,
            FIXTURE_INTENT_CLOSE_B54EC48E)) {
      for (boolean unknown : List.of(false, true)) {
        try (var f = fixture()) {
          f.seed(INVALID);
          var h = new PublicationHarness(f);
          h.fail = failure;
          h.unknown = unknown ? new IllegalArgumentException("independent fault") : null;
          var owner = h.owner();
          owner.bind(invalid());
          Throwable thrown =
              assertThrows(
                  Exception.class,
                  () -> {
                    owner.issue(
                        permit(),
                        (p, e) -> {
                          if (p == IssuePhase.AFTER_READBACK) h.point("proof");
                        });
                    h.point(FIXTURE_A_CLOSE_B364A3FB);
                    owner.commit();
                  });
          if (unknown) assertSame(h.unknown, thrown);
          else assertInstanceOf(IOException.class, thrown);
          owner.abort();
          assertEquals(INVALID, Files.readString(f.current));
          assertEquals(invalid(), owner.expected());
          assertTrue(Files.exists(h.marker));
          assertEquals(0, h.retains);
          if (!failure.equals("begin")) assertEquals(GOLD, Files.readString(f.permit));
          f.released();
        }
      }
    }
    for (String uncertainty :
        List.of("quarantine", "recovery-close", "revoke", "corrupt", "open")) {
      try (var f = fixture()) {
        f.seed(INVALID);
        var h = new PublicationHarness(f);
        var owner = h.owner();
        owner.bind(invalid());
        owner.issue(permit(), (p, e) -> {});
        if (uncertainty.equals("corrupt")) Files.writeString(f.current, "CORRUPTED\n");
        else if (uncertainty.equals("revoke")) {
          f.fail = FIXTURE_REPLACE_197D1A17;
          f.failAt = f.count(FIXTURE_REPLACE_197D1A17) + 1;
        } else h.fail = uncertainty;
        assertThrows(PublicationRetained.class, owner::abort);
        assertEquals(1, h.retains);
        assertTrue(Files.exists(h.marker));
        assertEquals(GOLD, Files.readString(f.permit));
        assertThrows(StorageIoException.class, f.store::readIssued);
      }
    }
    try (var f = fixture()) {
      f.seed(INVALID);
      var h = new PublicationHarness(f);
      h.owner().abort();
      assertEquals(List.of(FIXTURE_INTENT_CLOSE_B54EC48E), h.events);
      assertEquals(0, h.retains);
      h.fail = FIXTURE_INTENT_CLOSE_B54EC48E;
      assertThrows(PublicationRetained.class, h.owner()::abort);
    }
  }

  private static final class PublicationRetained extends RuntimeException {
    private static final long serialVersionUID = 1L;
  }

  @Test
  void isspub008AfterAdmissionAndLastMGuardFaultsAreSupervisedWithoutScopeExport()
      throws Exception {
    for (Throwable fault :
        List.of(
            new IOException("after DB close"),
            new IllegalStateException("after original close"),
            new AssertionError("last M gate"))) {
      try (var f = fixture()) {
        f.seed(INVALID);
        var h = new PublicationHarness(f);
        var owner = h.owner();
        owner.bind(invalid());
        owner.issue(permit(), (p, e) -> {});
        owner.commit();
        assertFalse(Files.exists(h.marker));
        var reference = new java.util.concurrent.atomic.AtomicReference<>(owner);
        Throwable actual =
            assertThrows(
                Throwable.class,
                () ->
                    MorningControlScope.protectPublication(
                        reference,
                        () -> {
                          if (fault instanceof IOException io) throw io;
                          if (fault instanceof RuntimeException runtime) throw runtime;
                          throw (Error) fault;
                        }));
        assertSame(fault, actual);
        assertEquals(INVALID, Files.readString(f.current));
        assertTrue(Files.exists(h.marker));
        assertEquals(GOLD, Files.readString(f.permit));
        int mutations = f.count(FIXTURE_REPLACE_197D1A17);
        int closes = h.storeCloses;
        owner.abort();
        assertEquals(mutations, f.count(FIXTURE_REPLACE_197D1A17));
        assertEquals(closes, h.storeCloses);
        assertEquals(0, h.retains);
        assertThrows(IOException.class, () -> owner.issue(permit(), (p, e) -> {}));
        assertEquals("normal", MorningControlScope.protectPublication(reference, () -> "normal"));
      }
    }
    var absent = new java.util.concurrent.atomic.AtomicReference<MorningPermitPublication>();
    var original = new IOException("pre-creation failure");
    assertSame(
        original,
        assertThrows(
            IOException.class,
            () ->
                MorningControlScope.protectPublication(
                    absent,
                    () -> {
                      throw original;
                    })));
    assertThrows(
        NullPointerException.class, () -> MorningControlScope.protectPublication(null, () -> true));
    assertThrows(
        NullPointerException.class, () -> MorningControlScope.protectPublication(absent, null));
  }

  /** Real current/permit IO, marker/lifetime counters are PT-only seams, never native authority. */
  private static final class PublicationHarness {
    final Fixture fixture;
    final Path marker;
    final List<String> events = new ArrayList<>();
    String fail = "";
    RuntimeException unknown;
    int storeCloses;
    int retains;

    PublicationHarness(Fixture fixture) {
      this.fixture = fixture;
      marker = fixture.directory.resolve("permit-start.intent");
    }

    void point(String value) throws IOException {
      events.add(value);
      if (fail.equals(value)) {
        fail = ""; // single injected fault, not a repaired production operation
        if (unknown != null) throw unknown;
        throw new IOException("independent fault");
      }
    }

    MorningPermitPublication.Intents intents(boolean recovery) {
      return new MorningPermitPublication.Intents() {
        public void begin() throws IOException {
          Files.createFile(marker);
          point("begin");
        }

        public void verify() {
          assertTrue(Files.exists(marker));
        }

        public void retire() throws IOException {
          Files.delete(marker);
          point(FIXTURE_RETIRE_A2A9D4FF);
        }

        public void quarantine() throws IOException {
          point("quarantine");
          if (!Files.exists(marker)) Files.createFile(marker);
        }

        public void close() throws IOException {
          point(recovery ? "recovery-close" : FIXTURE_INTENT_CLOSE_B54EC48E);
        }
      };
    }

    MorningPermitPublication owner() {
      return new MorningPermitPublication(
          intents(false),
          () -> {
            point("open");
            return new MorningPermitPublication.Store() {
              public StartupPermitFiles files() {
                return fixture.store;
              }

              public void close() throws IOException {
                storeCloses++;
                point("store-close");
              }
            };
          },
          () -> intents(true),
          () -> {},
          () -> {
            retains++;
            throw new PublicationRetained();
          });
    }
  }

  private static final class Fixture
      implements AutoCloseable,
          StartupPermitFiles.Io,
          StartupPermitFiles.Parts,
          InodeSecurityCalls {
    final Path directory;
    final Path current;
    final Path permit;
    final OwnedTransferDirectory root;
    final StartupPermitFiles store;
    final StartupPermitFiles.NioIo nativeIo = new StartupPermitFiles.NioIo();
    final Map<String, Integer> counts = new ConcurrentHashMap<>();
    final List<String> events = Collections.synchronizedList(new ArrayList<>());
    final Set<Integer> entries = ConcurrentHashMap.newKeySet();
    int readers;
    int writers;
    int failAt = 1;
    int wrongSizeAt;
    long part;
    long uid;
    String fail = "";
    String bad = "";
    String badRole = "";
    String behavior = "";
    boolean nullReader;
    boolean nullWriter;
    boolean digestFailure;
    boolean replaceFailure;
    boolean lateInterrupt;
    RuntimeException unknown;
    BiConsumer<String, Map<String, Object>> mutate = (r, m) -> {};

    Fixture(Path dir) throws Exception {
      directory = dir;
      current = dir.resolve("epoch.current");
      permit = dir.resolve(EPOCH + ".permit");
      DirectoryCalls delegate = LinuxDirectoryCalls.create();
      DirectoryCalls port =
          (DirectoryCalls)
              Proxy.newProxyInstance(
                  getClass().getClassLoader(),
                  new Class<?>[] {DirectoryCalls.class},
                  (proxy, method, args) -> {
                    String name = method.getName();
                    String event =
                        switch (name) {
                          case "createPrivateFile" -> "create";
                          case "openEntry", "publish", "sync" -> name;
                          default -> "";
                        };
                    if (!event.isEmpty()) point(event);
                    boolean closed = name.equals("close") && entries.remove((Integer) args[0]);
                    Object result;
                    try {
                      result = method.invoke(delegate, args);
                    } catch (InvocationTargetException e) {
                      throw e.getCause();
                    }
                    if (name.equals("openEntry") || name.equals("createPrivateFile"))
                      entries.add((Integer) result);
                    if (closed) point("entryClose");
                    return result;
                  });
      root = OwnedTransferDirectory.open(port, dir);
      store = new StartupPermitFiles(root, this, this, this);
    }

    int count(String name) {
      return counts.getOrDefault(name, 0);
    }

    void reset() {
      counts.clear();
      events.clear();
      fail = "";
    }

    void seed(String content) throws IOException {
      Files.writeString(current, content);
      reset();
    }

    void setup(String operation) throws Exception {
      if (List.of(
              FIXTURE_REPLACE_197D1A17, "issue", FIXTURE_CURRENT_694DF57A, FIXTURE_READ_6F365882)
          .contains(operation)) seed(INVALID);
      if (operation.equals(FIXTURE_READ_6F365882))
        store.issue(invalid(), StartupPermitFilesTest.permit());
      reset();
    }

    void run(String operation) throws Exception {
      switch (operation) {
        case FIXTURE_NEW_80270E39 -> store.invalidate(BOOT, EPOCH, ACTIVE);
        case FIXTURE_REPLACE_197D1A17 -> store.invalidate(BOOT, ACT, ACTIVE);
        case "issue" -> store.issue(invalid(), StartupPermitFilesTest.permit());
        case FIXTURE_CURRENT_694DF57A -> store.current();
        case FIXTURE_READ_6F365882 -> store.readIssued();
        default -> throw new AssertionError();
      }
    }

    void point(String name) throws StorageIoException {
      events.add(name);
      int at = counts.merge(name, 1, Integer::sum);
      if (name.equals(fail) && at == failAt) {
        if (unknown != null) throw unknown;
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
    }

    @Override
    public UUID next() {
      return new UUID(99, ++part);
    }

    @Override
    public long effectiveUid() {
      return uid;
    }

    @Override
    public Map<String, Object> attributes(Path p) throws IOException {
      point(FIXTURE_ATTRIBUTES_D300E055);
      Map<String, Object> m = new HashMap<>(nativeIo.attributes(p));
      int type = (Integer) m.get(FIXTURE_MODE_B6D5C2C3) & 0170000;
      String role = type == 040000 ? FIXTURE_DIR_16E08808 : FIXTURE_FILE_BFDDE6F5;
      m.put(FIXTURE_UID_0C18F38C, 0);
      m.put(FIXTURE_GID_0ACDD642, 0);
      m.put(FIXTURE_MODE_B6D5C2C3, type | (role.equals(FIXTURE_DIR_16E08808) ? 0700 : 0600));
      if (role.equals(badRole))
        switch (bad) {
          case "nullAttributes" -> {
            return null;
          }
          case FIXTURE_UID_0C18F38C -> m.put(FIXTURE_UID_0C18F38C, 1);
          case FIXTURE_GID_0ACDD642 -> m.put(FIXTURE_GID_0ACDD642, 1);
          case FIXTURE_MODE_B6D5C2C3 -> m.put(FIXTURE_MODE_B6D5C2C3, type | 0777);
          case "links" -> m.put("nlink", role.equals(FIXTURE_DIR_16E08808) ? 1 : 2);
          case FIXTURE_SIZE_EB1E91E4 ->
              m.put(FIXTURE_SIZE_EB1E91E4, role.equals(FIXTURE_DIR_16E08808) ? -1L : 8193L);
          default -> {}
        }
      mutate.accept(role, m);
      return m;
    }

    private String role(Path p) throws IOException {
      return (((Integer) nativeIo.attributes(p).get(FIXTURE_MODE_B6D5C2C3)) & 0170000) == 040000
          ? FIXTURE_DIR_16E08808
          : FIXTURE_FILE_BFDDE6F5;
    }

    @Override
    public String filesystem(Path p) throws IOException {
      point("filesystem");
      if (role(p).equals(badRole)) {
        if (bad.equals("nullFilesystem")) return null;
        if (bad.equals("filesystem")) return "ext4";
      }
      return "tmpfs";
    }

    @Override
    public byte[] accessAcl(Path p, int maximum) throws StorageIoException {
      point("acl");
      assertEquals(44, maximum);
      try {
        if (role(p).equals(badRole)) {
          if (bad.equals("nullAcl")) return null;
          if (bad.equals("acl")) return new byte[] {1};
        }
      } catch (IOException e) {
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
      return new byte[0];
    }

    @Override
    public boolean readOnlyFilesystem(Path p) throws StorageIoException {
      point("readonly");
      try {
        return role(p).equals(badRole) && bad.equals("readonly");
      } catch (IOException e) {
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
    }

    @Override
    public SeekableByteChannel open(Path p) throws IOException {
      point("openReader");
      if (nullReader) return null;
      SeekableByteChannel channel = nativeIo.open(p);
      readers++;
      return (SeekableByteChannel)
          Proxy.newProxyInstance(
              getClass().getClassLoader(),
              new Class<?>[] {SeekableByteChannel.class},
              (proxy, m, args) -> {
                String name = m.getName();
                if (name.equals("close")) {
                  channel.close();
                  readers--;
                  point("readClose");
                  if (lateInterrupt) Thread.currentThread().interrupt();
                  return null;
                }
                if (name.equals(FIXTURE_READ_6F365882)) {
                  point(FIXTURE_READ_6F365882);
                  ByteBuffer b = (ByteBuffer) args[0];
                  int start = b.position();
                  if (behavior.equals("zero")) return 0;
                  if (behavior.equals("negative")) return -2;
                  if (behavior.equals("short")) return -1;
                  if (behavior.equals("overflow")) return b.remaining() + 1;
                  if (behavior.equals("fill")) {
                    int count = b.remaining();
                    while (b.hasRemaining()) b.put((byte) 0);
                    return count;
                  }
                  int result = channel.read(b);
                  if (behavior.equals("position")) b.position(start);
                  return result;
                }
                if (name.equals(FIXTURE_SIZE_EB1E91E4)) {
                  point("readSize");
                  return channel.size() + (count("readSize") == wrongSizeAt ? 1 : 0);
                }
                try {
                  return m.invoke(channel, args);
                } catch (InvocationTargetException e) {
                  throw e.getCause();
                }
              });
    }

    @Override
    public InspectorEnvironmentPublisher.Writer openWriter(Path p) throws IOException {
      point("openWriter");
      if (nullWriter) return null;
      var writer = nativeIo.openWriter(p);
      writers++;
      return new InspectorEnvironmentPublisher.Writer() {
        @Override
        public int write(ByteBuffer b) throws IOException {
          point("write");
          int position = b.position();
          if (behavior.equals("zero")) return 0;
          if (behavior.equals("negative")) return -1;
          if (behavior.equals("overflow")) return b.remaining() + 1;
          if (behavior.equals("short")) return 1;
          int result = writer.write(b);
          if (behavior.equals("position")) b.position(position);
          return result;
        }

        @Override
        public long size() throws IOException {
          point("writeSize");
          return writer.size() + (count("writeSize") == wrongSizeAt ? 1 : 0);
        }

        @Override
        public void force() throws IOException {
          point("force");
          writer.force();
        }

        @Override
        public void close() throws IOException {
          writer.close();
          writers--;
          point("writeClose");
        }
      };
    }

    @Override
    public void replace(Path p, String part, String current) throws IOException {
      point(FIXTURE_REPLACE_197D1A17);
      if (replaceFailure)
        throw new AtomicMoveNotSupportedException(
            FIXTURE_PUBLIC_B7853257, FIXTURE_PUBLIC_B7853257, FIXTURE_PUBLIC_B7853257);
      nativeIo.replace(p, part, current);
    }

    @Override
    public MessageDigest digest() throws NoSuchAlgorithmException {
      if (digestFailure) throw new NoSuchAlgorithmException(FIXTURE_PUBLIC_B7853257);
      return nativeIo.digest();
    }

    void released() {
      assertEquals(0, readers);
      assertEquals(0, writers);
      assertTrue(entries.isEmpty());
    }

    @Override
    public void close() throws IOException {
      root.close();
      released();
    }
  }
}

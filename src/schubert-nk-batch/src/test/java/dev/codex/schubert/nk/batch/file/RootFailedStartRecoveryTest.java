package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.nio.channels.SeekableByteChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** ROOTREC001/003/004: real FD IO, explicitly synthetic root/tmpfs; not native authority. */
final class RootFailedStartRecoveryTest {
  @TempDir Path temporary;
  static final String PERMIT =
      "NKPERMIT1\n"
          + StartupLaunchFilesTest.BIND
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

  final class Fixture implements AutoCloseable, StartupPermitFiles.Io {
    final BackupPublicationFixture f;
    final String service;
    final String epoch = StartupLaunchFilesTest.EPOCH;
    final String sha;

    Fixture(String service) throws Exception {
      this.service = service;
      f = new BackupPublicationFixture(temporary);
      Files.delete(f.child);
      f.metadata =
          (role, values) -> {
            values.put("uid", 0);
            values.put("gid", 0);
          };
      sha =
          HexFormat.of()
              .formatHex(
                  MessageDigest.getInstance("SHA-256")
                      .digest(PERMIT.getBytes(StandardCharsets.US_ASCII)));
      put(
          "epoch.current",
          "NKEPOCH1\nstate=INVALID\n" + StartupLaunchFilesTest.BIND + "permit_sha256=-\n");
      put(epoch + ".permit", PERMIT);
      put(epoch + ".owner", StartupLaunchFilesTest.OWNER);
      put(
          epoch + "." + service + ".launch",
          StartupLaunchRecordTest.GOLD
              .replace("service=API", "service=" + service)
              .replace("a".repeat(64), sha)
              .replace(
                  "b".repeat(64),
                  HexFormat.of()
                      .formatHex(
                          MessageDigest.getInstance("SHA-256")
                              .digest(
                                  StartupLaunchFilesTest.OWNER.getBytes(
                                      StandardCharsets.US_ASCII)))));
      put(epoch + "." + service + ".start.intent", "");
      put("permit-start.intent", "");
    }

    void put(String name, String value) throws IOException {
      Files.writeString(f.parent.resolve(name), value);
      Files.setAttribute(f.parent.resolve(name), "unix:mode", 0600);
    }

    RootFailedStartRecovery.Evidence observe() throws IOException {
      return RootFailedStartRecovery.observe(f.root, f, this);
    }

    void retire(RootFailedStartRecovery.Evidence e, RootFailedStartRecovery.Proof proof)
        throws IOException {
      RootFailedStartRecovery.retire(f.root, f, this, e, proof);
    }

    public Map<String, Object> attributes(Path p) throws IOException {
      return f.attributes(p);
    }

    public String filesystem(Path p) {
      return f.filesystem(p);
    }

    public SeekableByteChannel open(Path p) throws IOException {
      return f.open(p);
    }

    public InspectorEnvironmentPublisher.Writer openWriter(Path p) throws IOException {
      return f.openWriter(p);
    }

    public void replace(Path d, String p, String c) {
      throw new AssertionError("recovery must never replace current");
    }

    public MessageDigest digest() throws NoSuchAlgorithmException {
      return MessageDigest.getInstance("SHA-256");
    }

    public void close() throws dev.codex.schubert.nk.storage.StorageIoException {
      f.close();
    }
  }

  @Test
  void bothClosedRolesRetireOnlyTwoIntentsAndPreserveInvalidAndArtifacts() throws Exception {
    for (String role : List.of("API", "WEB"))
      try (var f = new Fixture(role)) {
        var before = new HashMap<String, String>();
        for (var name :
            List.of(
                "epoch.current",
                f.epoch + ".permit",
                f.epoch + ".owner",
                f.epoch + "." + role + ".launch"))
          before.put(name, Files.readString(f.f.parent.resolve(name)));
        var evidence = f.observe();
        assertEquals(f.sha, evidence.permitSha256());
        assertEquals(role, evidence.service().name());
        assertEquals(StartupPermitRecords.State.INVALID, evidence.invalid().state());
        assertEquals("FailedRootEvidence[actual=<redacted>]", evidence.toString());
        var proofs = new ArrayList<RootFailedStartRecovery.Evidence>();
        f.retire(evidence, proofs::add);
        assertFalse(proofs.isEmpty());
        assertTrue(proofs.stream().allMatch(evidence::equals));
        assertFalse(Files.exists(f.f.parent.resolve(f.epoch + "." + role + ".start.intent")));
        assertFalse(Files.exists(f.f.parent.resolve("permit-start.intent")));
        for (var entry : before.entrySet())
          assertEquals(entry.getValue(), Files.readString(f.f.parent.resolve(entry.getKey())));
        var permits = new StartupPermitFiles(f.f.root, f.f, f, UUID::randomUUID);
        assertThrows(IOException.class, permits::readIssued);
        assertEquals(
            f.sha,
            permits.readRevoked(evidence.invalid()).formerIssued().permitDigest().orElseThrow());
        assertThrows(IOException.class, f::observe);
      }
  }

  @Test
  void unknownOrMissingAndProofFailurePreserveQuarantine() throws Exception {
    for (String bad :
        List.of("unknown", "stray.part", "41100027-4444-4333-8444-555555555555.API.start.intent"))
      try (var f = new Fixture("API")) {
        f.put(bad, "");
        assertThrows(IOException.class, f::observe);
        assertTrue(Files.exists(f.f.parent.resolve("permit-start.intent")));
      }
    try (var f = new Fixture("API")) {
      var e = f.observe();
      assertThrows(
          IOException.class,
          () ->
              f.retire(
                  e,
                  ignored -> {
                    throw new IOException("synthetic actual closure unavailable");
                  }));
      assertTrue(Files.exists(f.f.parent.resolve(f.epoch + ".API.start.intent")));
      assertTrue(Files.exists(f.f.parent.resolve("permit-start.intent")));
      assertThrows(NullPointerException.class, () -> f.retire(null, ignored -> {}));
      assertThrows(NullPointerException.class, () -> f.retire(e, null));
      f.put(f.epoch + ".WEB.start.intent", "");
      assertThrows(IOException.class, f::observe);
      Files.delete(f.f.parent.resolve(f.epoch + ".WEB.start.intent"));
      f.put("permit-start.intent", "nonempty");
      assertThrows(IOException.class, () -> f.retire(e, ignored -> {}));
    }
  }

  @Test
  void syncFailureAfterLastUnlinkMustRemainQuarantined() throws Exception {
    try (var f = new Fixture("API")) {
      var e = f.observe();
      var injected = new java.util.concurrent.atomic.AtomicBoolean();
      f.f.hook =
          (name, count) -> {
            if (name.equals("sync")
                && !Files.exists(f.f.parent.resolve("permit-start.intent"))
                && injected.compareAndSet(false, true))
              f.f.faults.put("sync#" + count, new IOException("synthetic post-unlink sync fault"));
          };
      assertThrows(IOException.class, () -> f.retire(e, ignored -> {}));
      assertTrue(injected.get());
      assertTrue(
          Files.exists(f.f.parent.resolve("permit-start.intent")),
          "unknown durability cannot become clear");
      assertEquals(
          e.invalid(), new StartupPermitFiles(f.f.root, f.f, f, UUID::randomUUID).current());
    }
  }

  @Test
  void changedOwnerPermitCurrentAndInterruptedNeverRetire() throws Exception {
    for (String name : List.of("epoch.current", "permit", "owner", "API.launch"))
      try (var f = new Fixture("API")) {
        var e = f.observe();
        f.put(name.equals("epoch.current") ? name : f.epoch + "." + name, "corrupt");
        assertThrows(IOException.class, () -> f.retire(e, ignored -> fail("changed evidence")));
        assertTrue(Files.exists(f.f.parent.resolve("permit-start.intent")));
      }
    try (var f = new Fixture("API")) {
      var e = f.observe();
      Thread.currentThread().interrupt();
      try {
        assertThrows(IOException.class, () -> f.retire(e, ignored -> fail("interrupted")));
      } finally {
        Thread.interrupted();
      }
      assertTrue(Files.exists(f.f.parent.resolve("permit-start.intent")));
    }
  }
}

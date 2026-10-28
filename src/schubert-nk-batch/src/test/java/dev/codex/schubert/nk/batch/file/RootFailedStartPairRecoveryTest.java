package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** ROOTPAIR001..008: literal role/generation oracle; real FD IO, synthetic Root only. */
final class RootFailedStartPairRecoveryTest {
  private static final String FIXTURE_API_LAUNCH_5BC1797F = ".API.launch";
  private static final String FIXTURE_WEB_LAUNCH_DD7B1D99 = ".WEB.launch";
  private static final String FIXTURE_PERMIT_START_INTENT_4794D6AC = "permit-start.intent";
  private static final String FIXTURE_EPOCH_CURRENT_92895879 = "epoch.current";
  private static final String FIXTURE_OWNER_A60B1118 = ".owner";
  private static final String FIXTURE_SYNC_5CFA1A73 = "sync";
  private static final String FIXTURE_OWNER_622F06CB = "owner";
  @TempDir Path temporary;

  final class Fixture implements AutoCloseable {
    final RootFailedStartRecoveryTest base = new RootFailedStartRecoveryTest();
    final RootFailedStartRecoveryTest.Fixture f;

    Fixture() throws Exception {
      base.temporary = temporary;
      f = base.new Fixture("API");
      // Independent literal second generation, not a Production-derived expected frame.
      String api = Files.readString(f.f.parent.resolve(f.epoch + FIXTURE_API_LAUNCH_5BC1797F));
      f.put(
          f.epoch + FIXTURE_WEB_LAUNCH_DD7B1D99,
          api.replace("service=API", "service=WEB")
              .replace("invocation=" + "2".repeat(32), "invocation=" + "3".repeat(32))
              .replace("pid=300", "pid=301"));
      f.put(f.epoch + ".WEB.start.intent", "");
    }

    RootFailedStartRecovery.PairEvidence observe() throws IOException {
      return RootFailedStartRecovery.observePair(f.f.root, f.f, f);
    }

    void retire(RootFailedStartRecovery.PairEvidence pair, RootFailedStartRecovery.PairProof proof)
        throws IOException {
      RootFailedStartRecovery.retirePair(f.f.root, f.f, f, pair, proof);
    }

    void quarantine(RootFailedStartRecovery.PairEvidence pair) throws IOException {
      RootFailedStartRecovery.quarantinePair(f.f.root, f.f, f, pair);
    }

    List<String> names() {
      return List.of(
          f.epoch + ".WEB.start.intent",
          f.epoch + ".API.start.intent",
          FIXTURE_PERMIT_START_INTENT_4794D6AC);
    }

    void assertQuarantined() throws IOException {
      for (String name : names())
        assertEquals("", Files.readString(f.f.parent.resolve(name)), name);
    }

    public void close() throws IOException {
      f.close();
    }
  }

  @Test
  void exactPairRetiresReverseOrderAndPreservesAllOriginalBytes() throws Exception {
    try (var f = new Fixture()) {
      assertThrows(IOException.class, f.f::observe); // Previous one-child contract remains strict.
      var before = new HashMap<String, String>();
      for (String name :
          List.of(
              FIXTURE_EPOCH_CURRENT_92895879,
              f.f.epoch + ".permit",
              f.f.epoch + FIXTURE_OWNER_A60B1118,
              f.f.epoch + FIXTURE_API_LAUNCH_5BC1797F,
              f.f.epoch + FIXTURE_WEB_LAUNCH_DD7B1D99))
        before.put(name, Files.readString(f.f.f.parent.resolve(name)));
      var pair = f.observe();
      assertEquals(ServiceConfigFiles.Service.API, pair.api().service());
      assertEquals(ServiceConfigFiles.Service.WEB, pair.web().service());
      assertEquals(300, pair.api().child().pid());
      assertEquals(301, pair.web().child().pid());
      assertEquals(200, pair.api().child().startTicks());
      assertEquals(200, pair.web().child().startTicks()); // Same jiffy is legitimate.
      assertEquals("FailedRootPair[actual=<redacted>]", pair.toString());
      var order = new ArrayList<String>();
      f.f.f.hook =
          (event, count) -> {
            if (event.equals(FIXTURE_SYNC_5CFA1A73)) {
              for (String name : f.names())
                if (!Files.exists(f.f.f.parent.resolve(name)) && !order.contains(name))
                  order.add(name);
            }
          };
      var proofs = new ArrayList<RootFailedStartRecovery.PairEvidence>();
      f.retire(pair, proofs::add);
      assertEquals(f.names(), order);
      assertFalse(proofs.isEmpty());
      assertTrue(proofs.stream().allMatch(pair::equals));
      for (var entry : before.entrySet())
        assertEquals(entry.getValue(), Files.readString(f.f.f.parent.resolve(entry.getKey())));
      assertThrows(
          IOException.class,
          () -> new StartupPermitFiles(f.f.f.root, f.f.f, f.f, UUID::randomUUID).readIssued());
      assertThrows(IOException.class, f::observe);
    }
  }

  @Test
  void issuedPairWithoutPublicationUsesSameEpochRevokeThenQuarantineThenReverseRetirement()
      throws Exception {
    try (var f = new Fixture()) {
      var pair = f.observe();
      String issued =
          "NKEPOCH1\nstate=ISSUED\n"
              + StartupLaunchFilesTest.BIND
              + "permit_sha256="
              + f.f.sha
              + "\n";
      String invalid =
          "NKEPOCH1\nstate=INVALID\n" + StartupLaunchFilesTest.BIND + "permit_sha256=-\n";
      f.f.put(FIXTURE_EPOCH_CURRENT_92895879, issued);
      Files.delete(f.f.f.parent.resolve(FIXTURE_PERMIT_START_INTENT_4794D6AC));
      var retained = new HashMap<String, byte[]>();
      for (String name :
          List.of(
              f.f.epoch + ".permit",
              f.f.epoch + FIXTURE_OWNER_A60B1118,
              f.f.epoch + FIXTURE_API_LAUNCH_5BC1797F,
              f.f.epoch + FIXTURE_WEB_LAUNCH_DD7B1D99))
        retained.put(name, Files.readAllBytes(f.f.f.parent.resolve(name)));
      // The old retirement-only fixture deliberately forbids current replacement. This new
      // publication fixture permits only canonical atomic current replacement, not recovery IO.
      var publication =
          new StartupPermitFiles.Io() {
            public Map<String, Object> attributes(Path p) throws IOException {
              return f.f.attributes(p);
            }

            public String filesystem(Path p) {
              return f.f.filesystem(p);
            }

            public java.nio.channels.SeekableByteChannel open(Path p) throws IOException {
              return f.f.open(p);
            }

            public InspectorEnvironmentPublisher.Writer openWriter(Path p) throws IOException {
              return f.f.openWriter(p);
            }

            public java.security.MessageDigest digest()
                throws java.security.NoSuchAlgorithmException {
              return f.f.digest();
            }

            public void replace(Path directory, String part, String current) throws IOException {
              assertEquals(FIXTURE_EPOCH_CURRENT_92895879, current);
              Files.move(
                  directory.resolve(part),
                  directory.resolve(current),
                  StandardCopyOption.ATOMIC_MOVE,
                  StandardCopyOption.REPLACE_EXISTING);
            }
          };
      var permits = new StartupPermitFiles(f.f.f.root, f.f.f, publication, UUID::randomUUID);
      assertEquals(pair.api().permit(), permits.readIssued());
      assertThrows(IOException.class, f::observe); // ISSUED is not failed-Pair authority.
      permits.revoke(pair.api().invalid(), pair.api().permit());
      assertEquals(invalid, Files.readString(f.f.f.parent.resolve(FIXTURE_EPOCH_CURRENT_92895879)));
      assertFalse(Files.exists(f.f.f.parent.resolve(FIXTURE_PERMIT_START_INTENT_4794D6AC)));
      assertThrows(IOException.class, f::observe); // Publication quarantine is still required.
      var publications = new ArrayList<String>();
      f.f.f.hook =
          (event, count) -> {
            if (event.equals(FIXTURE_SYNC_5CFA1A73)) {
              assertEquals(
                  "",
                  assertDoesNotThrow(
                      () ->
                          Files.readString(
                              f.f.f.parent.resolve(FIXTURE_PERMIT_START_INTENT_4794D6AC))));
              for (String name : f.names())
                assertEquals(
                    "", assertDoesNotThrow(() -> Files.readString(f.f.f.parent.resolve(name))));
              publications.add("publication-first");
            }
          };
      f.quarantine(pair);
      assertFalse(publications.isEmpty());
      assertEquals(pair, f.observe());
      var order = new ArrayList<String>();
      f.f.f.hook =
          (event, count) -> {
            if (event.equals(FIXTURE_SYNC_5CFA1A73))
              for (String name : f.names())
                if (!Files.exists(f.f.f.parent.resolve(name)) && !order.contains(name))
                  order.add(name);
          };
      f.retire(pair, expected -> assertEquals(pair, expected));
      assertEquals(
          List.of(
              f.f.epoch + ".WEB.start.intent",
              f.f.epoch + ".API.start.intent",
              FIXTURE_PERMIT_START_INTENT_4794D6AC),
          order);
      assertEquals(invalid, Files.readString(f.f.f.parent.resolve(FIXTURE_EPOCH_CURRENT_92895879)));
      for (var entry : retained.entrySet())
        assertArrayEquals(
            entry.getValue(), Files.readAllBytes(f.f.f.parent.resolve(entry.getKey())));
      try (var paths = Files.list(f.f.f.parent)) {
        assertEquals(
            Set.of(
                FIXTURE_EPOCH_CURRENT_92895879,
                f.f.epoch + ".permit",
                f.f.epoch + FIXTURE_OWNER_A60B1118,
                f.f.epoch + FIXTURE_API_LAUNCH_5BC1797F,
                f.f.epoch + FIXTURE_WEB_LAUNCH_DD7B1D99),
            paths
                .map(p -> p.getFileName().toString())
                .collect(java.util.stream.Collectors.toSet()));
      }
      assertThrows(IOException.class, permits::readIssued);
    }
  }

  @Test
  void sameEpochRevokeNeverRepairsForeignIssuedDigestOrCreatesPublication() throws Exception {
    try (var f = new Fixture()) {
      var pair = f.observe();
      String foreign =
          "NKEPOCH1\nstate=ISSUED\n"
              + StartupLaunchFilesTest.BIND
              + "permit_sha256="
              + "9".repeat(64)
              + "\n";
      f.f.put(FIXTURE_EPOCH_CURRENT_92895879, foreign);
      Files.delete(f.f.f.parent.resolve(FIXTURE_PERMIT_START_INTENT_4794D6AC));
      var permits = new StartupPermitFiles(f.f.f.root, f.f.f, f.f, UUID::randomUUID);
      assertThrows(
          IOException.class, () -> permits.revoke(pair.api().invalid(), pair.api().permit()));
      assertEquals(foreign, Files.readString(f.f.f.parent.resolve(FIXTURE_EPOCH_CURRENT_92895879)));
      assertFalse(Files.exists(f.f.f.parent.resolve(FIXTURE_PERMIT_START_INTENT_4794D6AC)));
      for (String role : List.of("API", "WEB"))
        assertEquals(
            "", Files.readString(f.f.f.parent.resolve(f.f.epoch + "." + role + ".start.intent")));
    }
  }

  @Test
  void eachMissingNonemptyAndSymlinkMarkerRefusesWithoutRetirement() throws Exception {
    for (int index = 0; index < 3; index++)
      for (String fault : List.of("missing", "nonempty", "symlink"))
        try (var f = new Fixture()) {
          String name = f.names().get(index);
          Path marker = f.f.f.parent.resolve(name);
          if (fault.equals("nonempty")) f.f.put(name, "not-empty");
          else {
            Files.delete(marker);
            if (fault.equals("symlink"))
              Files.createSymbolicLink(marker, Path.of(FIXTURE_EPOCH_CURRENT_92895879));
          }
          assertThrows(IOException.class, f::observe, fault + name);
          for (String unchanged : f.names())
            if (!unchanged.equals(name))
              assertEquals("", Files.readString(f.f.f.parent.resolve(unchanged)));
        }
  }

  @Test
  void crossedGenerationsOwnerDigestAndForeignNamespaceAreRejected() throws Exception {
    for (String fault : List.of("pid", "invocation", FIXTURE_OWNER_622F06CB, "permit", "foreign"))
      try (var f = new Fixture()) {
        Path launch = f.f.f.parent.resolve(f.f.epoch + FIXTURE_WEB_LAUNCH_DD7B1D99);
        String text = Files.readString(launch);
        switch (fault) {
          case "pid" ->
              f.f.put(launch.getFileName().toString(), text.replace("pid=301", "pid=300"));
          case "invocation" ->
              f.f.put(
                  launch.getFileName().toString(), text.replace("3".repeat(32), "2".repeat(32)));
          case FIXTURE_OWNER_622F06CB ->
              f.f.put(
                  launch.getFileName().toString(),
                  text.replaceAll("owner_sha256=[0-9a-f]{64}", "owner_sha256=" + "1".repeat(64)));
          case "permit" ->
              f.f.put(
                  launch.getFileName().toString(),
                  text.replaceAll("permit_sha256=[0-9a-f]{64}", "permit_sha256=" + "1".repeat(64)));
          default -> f.f.put("41100027-4444-4333-8444-555555555555.API.start.intent", "");
        }
        assertThrows(IOException.class, f::observe, fault);
        f.assertQuarantined();
      }
  }

  @Test
  void eachUnlinkAndSyncFailureRestoresAllThreeMarkers() throws Exception {
    for (String event : List.of("unlink", FIXTURE_SYNC_5CFA1A73))
      for (int stage = 1; stage <= 3; stage++)
        try (var f = new Fixture()) {
          var pair = f.observe();
          var injected = new AtomicBoolean();
          int target = stage;
          int[] seen = {0};
          f.f.f.hook =
              (name, count) -> {
                if (name.equals(event)
                    && ++seen[0] == target
                    && injected.compareAndSet(false, true))
                  f.f.f.faults.put(name + "#" + count, new IOException("synthetic pair boundary"));
              };
          assertThrows(IOException.class, () -> f.retire(pair, ignored -> {}));
          assertTrue(injected.get());
          f.assertQuarantined();
          assertEquals(pair, f.observe());
        }
  }

  @Test
  void proofFailureAtEveryRetirementBoundaryNeverSucceeds() throws Exception {
    for (int missing = 0; missing <= 3; missing++)
      try (var f = new Fixture()) {
        var pair = f.observe();
        int target = missing;
        assertThrows(
            IOException.class,
            () ->
                f.retire(
                    pair,
                    ignored -> {
                      long absent =
                          f.names().stream()
                              .filter(name -> !Files.exists(f.f.f.parent.resolve(name)))
                              .count();
                      if (absent == target)
                        throw new IOException("synthetic independent closure proof refused");
                    }));
        f.assertQuarantined();
      }
  }

  @Test
  void oneQuarantineFailureDoesNotSkipOtherRolesAndNeverOverwrites() throws Exception {
    for (String bad : List.of(FIXTURE_PERMIT_START_INTENT_4794D6AC, "API", "WEB"))
      try (var f = new Fixture()) {
        var pair = f.observe();
        for (String name : f.names()) Files.delete(f.f.f.parent.resolve(name));
        String selected =
            bad.equals(FIXTURE_PERMIT_START_INTENT_4794D6AC)
                ? bad
                : f.f.epoch + "." + bad + ".start.intent";
        f.f.put(selected, "preserve anomalous inode");
        var failure = assertThrows(IOException.class, () -> f.quarantine(pair));
        assertEquals(1, failure.getSuppressed().length);
        assertEquals("preserve anomalous inode", Files.readString(f.f.f.parent.resolve(selected)));
        for (String name : f.names())
          if (!name.equals(selected))
            assertEquals("", Files.readString(f.f.f.parent.resolve(name)));
      }
  }

  @Test
  void nullInterruptAndChangedEvidenceCannotBecomeAuthority() throws Exception {
    try (var f = new Fixture()) {
      var pair = f.observe();
      assertThrows(
          NullPointerException.class,
          () -> new RootFailedStartRecovery.PairEvidence(null, pair.web()));
      assertThrows(
          NullPointerException.class,
          () -> new RootFailedStartRecovery.PairEvidence(pair.api(), null));
      assertThrows(
          IllegalArgumentException.class,
          () -> new RootFailedStartRecovery.PairEvidence(pair.web(), pair.api()));
      assertThrows(NullPointerException.class, () -> f.retire(null, ignored -> {}));
      assertThrows(NullPointerException.class, () -> f.retire(pair, null));
      assertThrows(NullPointerException.class, () -> f.quarantine(null));
      Thread.currentThread().interrupt();
      try {
        assertThrows(IOException.class, f::observe);
      } finally {
        Thread.interrupted();
      }
      f.assertQuarantined();
      f.f.put(f.f.epoch + FIXTURE_OWNER_A60B1118, "corrupt");
      assertThrows(IOException.class, () -> f.retire(pair, ignored -> fail("changed owner")));
      f.assertQuarantined();
    }
  }

  @Test
  void finalQuarantineSyncCannotLoseEarlierMarkerOrSharedSource() throws Exception {
    for (String changed : List.of(FIXTURE_PERMIT_START_INTENT_4794D6AC, FIXTURE_OWNER_622F06CB))
      try (var f = new Fixture()) {
        var pair = f.observe();
        f.retire(pair, ignored -> {});
        int[] syncs = {0};
        f.f.f.hook =
            (name, count) -> {
              // Missing marker creation forces once, then the enclosing operation syncs once.
              if (name.equals(FIXTURE_SYNC_5CFA1A73) && ++syncs[0] == 6) {
                try {
                  if (changed.equals(FIXTURE_OWNER_622F06CB))
                    f.f.put(f.f.epoch + FIXTURE_OWNER_A60B1118, "corrupt");
                  else Files.delete(f.f.f.parent.resolve(changed));
                } catch (IOException fault) {
                  throw new AssertionError(fault);
                }
              }
            };
        assertThrows(IOException.class, () -> f.quarantine(pair), changed);
        assertEquals(6, syncs[0]);
      }
  }

  @Test
  void pairValueRejectsEverySharedInvariantBeforeBorrowingAuthority() throws Exception {
    try (var f = new Fixture()) {
      var pair = f.observe();
      var api = pair.api();
      var web = pair.web();
      var changedEpoch =
          new StartupPermitRecords.Epoch(
              StartupPermitRecords.State.INVALID,
              web.invalid().boot(),
              UUID.fromString("41100027-4444-4333-8444-555555555555"),
              web.invalid().activation(),
              Optional.empty());
      var changedPermit =
          StartupPermitRecords.readPermit(
              RootFailedStartRecoveryTest.PERMIT
                  .replace("release_sha256=" + "b".repeat(64), "release_sha256=" + "1".repeat(64))
                  .getBytes(java.nio.charset.StandardCharsets.US_ASCII));
      var owner = web.owner();
      var changedOwner =
          new dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame(
              owner.boot(),
              owner.run(),
              owner.activation(),
              owner.cutoff(),
              owner.epoch(),
              owner.morning(),
              owner.cleanup(),
              owner.deadlineNanos() + 1);
      for (var changed :
          List.of(
              new RootFailedStartRecovery.Evidence(
                  api.invalid().issued(api.permitSha256()),
                  api.permit(),
                  api.permitSha256(),
                  api.owner(),
                  api.service(),
                  api.child()),
              new RootFailedStartRecovery.Evidence(
                  api.invalid(),
                  api.permit(),
                  api.permitSha256(),
                  api.owner(),
                  ServiceConfigFiles.Service.WEB,
                  api.child())))
        assertThrows(
            IllegalArgumentException.class,
            () -> new RootFailedStartRecovery.PairEvidence(changed, web));
      for (var changed :
          List.of(
              new RootFailedStartRecovery.Evidence(
                  changedEpoch,
                  web.permit(),
                  web.permitSha256(),
                  web.owner(),
                  web.service(),
                  web.child()),
              new RootFailedStartRecovery.Evidence(
                  web.invalid(),
                  changedPermit,
                  web.permitSha256(),
                  web.owner(),
                  web.service(),
                  web.child()),
              new RootFailedStartRecovery.Evidence(
                  web.invalid(),
                  web.permit(),
                  "1".repeat(64),
                  web.owner(),
                  web.service(),
                  web.child()),
              new RootFailedStartRecovery.Evidence(
                  web.invalid(),
                  web.permit(),
                  web.permitSha256(),
                  changedOwner,
                  web.service(),
                  web.child()),
              new RootFailedStartRecovery.Evidence(
                  web.invalid(),
                  web.permit(),
                  web.permitSha256(),
                  web.owner(),
                  ServiceConfigFiles.Service.API,
                  web.child())))
        assertThrows(
            IllegalArgumentException.class,
            () -> new RootFailedStartRecovery.PairEvidence(api, changed));
      var marker =
          new BackupStartIntentFiles(
              f.f.f.root, f.f.f, f.f, () -> {}, FIXTURE_PERMIT_START_INTENT_4794D6AC);
      assertThrows(
          IOException.class,
          () -> marker.quarantineService(api.invalid(), ServiceConfigFiles.Service.API));
      assertThrows(
          IOException.class,
          () ->
              marker.quarantineService(
                  api.invalid().issued(api.permitSha256()), ServiceConfigFiles.Service.API));
      assertThrows(
          NullPointerException.class,
          () -> marker.quarantineService(null, ServiceConfigFiles.Service.API));
      assertThrows(NullPointerException.class, () -> marker.quarantineService(api.invalid(), null));
      f.assertQuarantined();
    }
  }
}

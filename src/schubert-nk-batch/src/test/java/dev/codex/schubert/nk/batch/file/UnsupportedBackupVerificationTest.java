package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.platform.InspectorUnitSnapshot;
import dev.codex.schubert.nk.bootstrap.ChildStartupContext;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.storage.InodeSecurityCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFilePermissions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** SS341/343/SSC092: absent verification implementation must never claim reused Backup success. */
final class UnsupportedBackupVerificationTest {
  @TempDir Path temporary;

  @Test
  void bverifyPort001UnsupportedVerificationRejectsAndClosesWithoutSecretOrRegeneration()
      throws Exception {
    var fixtureOwner = new BackupDatabaseWorkerTest();
    fixtureOwner.temporary = temporary;
    try (var fixture = fixtureOwner.new Fixture()) {
      String name = "20260928-000000-11111111-2222-4333-8444-555555555555";
      Path existing = fixture.privateDirectory("existing-");
      Files.move(existing, fixture.backup.resolve(name));
      Path dump = fixture.backup.resolve(name).resolve("schubert_nk.dump");
      Files.writeString(dump, "abc");
      Files.setPosixFilePermissions(dump, PosixFilePermissions.fromString("rw-------"));
      fixture.requestText =
          "NKBACKUPVERIFY1\nrun=11111111-2222-4333-8444-555555555555\n"
              + "started=2026-09-27T15:00:00Z\n"
              + "manifest_sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
              + "dump_size=3\n"
              + "dump_sha256=ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad\n";
      // Use the actual worker path, but deliberately provide a port that lacks
      // verification support. The default contract must fail closed, not succeed.
      BackupDatabaseWorker.Ports unsupported =
          new BackupDatabaseWorker.Ports() {
            public FixedServiceIdentity.Value identity() throws IOException {
              return fixture.identity();
            }

            public ChildStartupContext.Observed self() throws IOException {
              return fixture.self();
            }

            public InspectorUnitSnapshot unit() {
              return fixture.unit();
            }

            public String invocation() {
              return fixture.invocation();
            }

            public OwnedTransferDirectory credentials() throws IOException {
              return fixture.credentials();
            }

            public OwnedTransferDirectory runtime() throws IOException {
              return fixture.runtime();
            }

            public OwnedTransferDirectory backup() throws IOException {
              return fixture.backup();
            }

            public byte[] request(OwnedTransferDirectory credentials) throws IOException {
              return fixture.request(credentials);
            }

            public byte[] pgpass(OwnedTransferDirectory credentials) throws IOException {
              return fixture.pgpass(credentials);
            }

            public void dump(Path output, Path pgpass, long uid) throws IOException {
              fixture.dump(output, pgpass, uid);
            }

            public InspectorEnvironmentPublisher.Io io() {
              return fixture.io();
            }

            public InodeSecurityCalls security() {
              return fixture.security();
            }
          };
      var failure =
          assertThrows(
              StorageIoException.class, () -> new BackupDatabaseWorker(unsupported).execute());
      assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
      assertEquals("abc", Files.readString(dump));
      assertFalse(fixture.counts.containsKey("dump"));
      assertFalse(fixture.counts.containsKey("pgpass"));
      assertFalse(fixture.counts.containsKey("runtime"));
      assertFalse(fixture.counts.containsKey("createPrivateFile"));
      assertArrayEquals(new byte[fixture.request.length], fixture.request);
      fixture.released();
    }
  }
}

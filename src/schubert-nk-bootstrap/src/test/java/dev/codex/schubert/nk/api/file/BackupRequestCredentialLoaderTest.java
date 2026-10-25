package dev.codex.schubert.nk.api.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.file.InspectorCredentialLoaderTest.Fixture;
import dev.codex.schubert.nk.api.file.InspectorCredentialLoaderTest.TestIo;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PG309/PT-OPS-BREQUESTCRED001..008; public golden only, synthetic actor metadata explicit. */
final class BackupRequestCredentialLoaderTest {
  @TempDir Path temporary;
  private static final String NAME = "backup-request";
  private static final byte[] GOLDEN =
      "NKBACKUP1\nrun=11111111-2222-4333-8444-555555555555\nstarted=2026-09-27T15:00:00Z\n"
          .getBytes(StandardCharsets.US_ASCII);

  @Test
  void literalAndOwnedCopy() throws Exception {
    try (var f = new Fixture(temporary)) {
      Files.write(f.root.resolve(NAME), GOLDEN);
      var io = new TestIo();
      byte[] value = f.loader(io).readBackupRequest();
      assertArrayEquals(GOLDEN, value);
      Arrays.fill(value, (byte) 0);
      assertArrayEquals(GOLDEN, Files.readAllBytes(f.root.resolve(NAME)));
      assertEquals(1, io.opens);
      assertEquals(1, io.closes);
      io.assertCleared(401);
    }
  }

  @Test
  void boundedSource() throws Exception {
    try (var f = new Fixture(temporary)) {
      for (int length : new int[] {1, 160, 400}) {
        byte[] expected = new byte[length];
        Arrays.fill(expected, (byte) 'A');
        Files.write(f.root.resolve(NAME), expected);
        var io = new TestIo();
        io.maxRead = 17;
        assertArrayEquals(expected, f.loader(io).readBackupRequest());
        io.assertCleared(401);
      }
      for (int length : new int[] {0, 401}) {
        Files.write(f.root.resolve(NAME), new byte[length]);
        assertThrows(
            InspectorCredentialException.class, () -> f.loader(new TestIo()).readBackupRequest());
      }
    }
  }

  @Test
  void fixedNameMissingAndNoFallback() throws Exception {
    try (var f = new Fixture(temporary)) {
      Files.write(f.root.resolve("db-inbox-inspector"), GOLDEN);
      var io = new TestIo();
      assertThrows(InspectorCredentialException.class, () -> f.loader(io).readBackupRequest());
      assertEquals(0, io.opens);
    }
  }

  @Test
  void everyIoFailureClears() throws Exception {
    try (var f = new Fixture(temporary)) {
      Files.write(f.root.resolve(NAME), GOLDEN);
      for (String fault :
          List.of(
              "attributes-root",
              "attributes-file",
              "open",
              "unsupported",
              "read",
              "short",
              "zero",
              "long",
              "close",
              "root-final")) {
        var io = new TestIo();
        io.fault = fault;
        assertThrows(InspectorCredentialException.class, () -> f.loader(io).readBackupRequest());
        io.assertCleared(401);
        assertEquals(io.opens, io.closes);
      }
    }
  }

  @Test
  void namespaceAndSecurityFailures() throws Exception {
    try (var f = new Fixture(temporary)) {
      Files.write(f.root.resolve(NAME), GOLDEN);
      for (String fault : List.of("acl-root", "acl-file", "ro-file", "empty-acl-file-after")) {
        var io = new TestIo();
        io.securityFault = fault;
        assertThrows(InspectorCredentialException.class, () -> f.loader(io).readBackupRequest());
      }
      var io = new TestIo();
      io.fileChange = a -> a.put("dev", -1L);
      assertThrows(InspectorCredentialException.class, () -> f.loader(io).readBackupRequest());
      assertEquals(0, io.opens);
      var changed = new TestIo();
      changed.lateRootChange = a -> a.put("ino", -1L);
      assertThrows(InspectorCredentialException.class, () -> f.loader(changed).readBackupRequest());
      changed.assertCleared(401);
    }
  }

  @Test
  void symlinkAndHardLinkRefused() throws Exception {
    try (var f = new Fixture(temporary)) {
      Path file = f.root.resolve(NAME);
      Files.createSymbolicLink(file, Path.of("db-inbox-inspector"));
      assertThrows(
          InspectorCredentialException.class, () -> f.loader(new TestIo()).readBackupRequest());
      Files.delete(file);
      Files.write(file, GOLDEN);
      Files.createLink(f.root.resolve("alias"), file);
      assertThrows(
          InspectorCredentialException.class, () -> f.loader(new TestIo()).readBackupRequest());
    }
  }

  @Test
  void closeFailureAndNullContracts() throws Exception {
    try (var f = new Fixture(temporary)) {
      Files.write(f.root.resolve(NAME), GOLDEN);
      f.calls.closeUnavailable = true;
      assertThrows(
          InspectorCredentialException.class, () -> f.loader(new TestIo()).readBackupRequest());
      f.calls.closeUnavailable = false;
      assertThrows(
          NullPointerException.class,
          () ->
              new InspectorCredentialLoader(
                  null, new InspectorCredentialLoaderTest.TestSecurity(new TestIo())));
    }
  }

  @Test
  void independentConcurrentCopies() throws Exception {
    try (var f = new Fixture(temporary);
        var pool = Executors.newFixedThreadPool(8)) {
      Files.write(f.root.resolve(NAME), GOLDEN);
      var tasks = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 32; i++)
        tasks.add(
            () -> {
              var io = new TestIo();
              byte[] value = f.loader(io).readBackupRequest();
              assertArrayEquals(GOLDEN, value);
              Arrays.fill(value, (byte) 0);
              io.assertCleared(401);
              return true;
            });
      for (var done : pool.invokeAll(tasks)) assertTrue(done.get(5, TimeUnit.SECONDS));
      assertArrayEquals(GOLDEN, Files.readAllBytes(f.root.resolve(NAME)));
    }
  }
}

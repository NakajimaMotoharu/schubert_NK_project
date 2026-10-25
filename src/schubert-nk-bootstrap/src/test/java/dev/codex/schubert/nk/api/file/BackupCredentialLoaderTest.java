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

/** PG305/PT-OPS-BACKCRED001..008; public golden only, synthetic actor metadata explicit. */
final class BackupCredentialLoaderTest {
  @TempDir Path temporary;
  private static final String NAME = "backup-pgpass";
  private static final byte[] GOLDEN =
      "127.0.0.1:5432:schubert_nk:schubert_backup:PUBLIC_TEST_ONLY\n"
          .getBytes(StandardCharsets.US_ASCII);

  @Test
  void literalAndOwnedCopy() throws Exception {
    try (var f = new Fixture(temporary)) {
      Files.write(f.root.resolve(NAME), GOLDEN);
      var io = new TestIo();
      byte[] value = f.loader(io).readBackupPgpass();
      assertArrayEquals(GOLDEN, value);
      Arrays.fill(value, (byte) 0);
      assertArrayEquals(GOLDEN, Files.readAllBytes(f.root.resolve(NAME)));
      assertEquals(1, io.opens);
      assertEquals(1, io.closes);
      io.assertCleared(65537);
    }
  }

  @Test
  void boundedSource() throws Exception {
    try (var f = new Fixture(temporary)) {
      for (int length : new int[] {1, 65536}) {
        byte[] expected = new byte[length];
        Arrays.fill(expected, (byte) 'A');
        Files.write(f.root.resolve(NAME), expected);
        var io = new TestIo();
        io.maxRead = 17;
        assertArrayEquals(expected, f.loader(io).readBackupPgpass());
        io.assertCleared(65537);
      }
      for (int length : new int[] {0, 65537}) {
        Files.write(f.root.resolve(NAME), new byte[length]);
        assertThrows(
            InspectorCredentialException.class, () -> f.loader(new TestIo()).readBackupPgpass());
      }
    }
  }

  @Test
  void fixedNameMissingAndNoFallback() throws Exception {
    try (var f = new Fixture(temporary)) {
      Files.write(f.root.resolve("db-inbox-inspector"), GOLDEN);
      var io = new TestIo();
      assertThrows(InspectorCredentialException.class, () -> f.loader(io).readBackupPgpass());
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
        assertThrows(InspectorCredentialException.class, () -> f.loader(io).readBackupPgpass());
        io.assertCleared(65537);
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
        assertThrows(InspectorCredentialException.class, () -> f.loader(io).readBackupPgpass());
      }
      var io = new TestIo();
      io.fileChange = a -> a.put("dev", -1L);
      assertThrows(InspectorCredentialException.class, () -> f.loader(io).readBackupPgpass());
      assertEquals(0, io.opens);
      var changed = new TestIo();
      changed.lateRootChange = a -> a.put("ino", -1L);
      assertThrows(InspectorCredentialException.class, () -> f.loader(changed).readBackupPgpass());
      changed.assertCleared(65537);
    }
  }

  @Test
  void symlinkAndHardLinkRefused() throws Exception {
    try (var f = new Fixture(temporary)) {
      Path file = f.root.resolve(NAME);
      Files.createSymbolicLink(file, Path.of("db-inbox-inspector"));
      assertThrows(
          InspectorCredentialException.class, () -> f.loader(new TestIo()).readBackupPgpass());
      Files.delete(file);
      Files.write(file, GOLDEN);
      Files.createLink(f.root.resolve("alias"), file);
      assertThrows(
          InspectorCredentialException.class, () -> f.loader(new TestIo()).readBackupPgpass());
    }
  }

  @Test
  void closeFailureAndNullContracts() throws Exception {
    try (var f = new Fixture(temporary)) {
      Files.write(f.root.resolve(NAME), GOLDEN);
      f.calls.closeUnavailable = true;
      assertThrows(
          InspectorCredentialException.class, () -> f.loader(new TestIo()).readBackupPgpass());
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
              byte[] value = f.loader(io).readBackupPgpass();
              assertArrayEquals(GOLDEN, value);
              Arrays.fill(value, (byte) 0);
              io.assertCleared(65537);
              return true;
            });
      for (var done : pool.invokeAll(tasks)) assertTrue(done.get(5, TimeUnit.SECONDS));
      assertArrayEquals(GOLDEN, Files.readAllBytes(f.root.resolve(NAME)));
    }
  }
}

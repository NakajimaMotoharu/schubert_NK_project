package dev.codex.schubert.nk.api.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
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
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/** PT-DB-INBOX-197..201; real bounded IO, explicitly synthetic root-manager metadata. */
final class InspectorDatabaseCredentialLoaderTest {
  private static final String FIXTURE_MODE_B6D5C2C3 = "mode";
  private static final String FIXTURE_SIZE_EB1E91E4 = "size";
  @TempDir Path temporary;
  private static final String NAME = "db-inbox-inspector";

  @Test
  void validBoundedFile() throws Exception {
    try (var f = new Fixture(temporary)) {
      for (int length : new int[] {1, 54, 69, 65536}) {
        byte[] expected = new byte[length];
        Arrays.fill(expected, (byte) 'A');
        Files.write(f.root.resolve(NAME), expected);
        var io = new TestIo();
        io.maxRead = 4096;
        try (var value = f.loader(io).loadDatabasePassword()) {
          char[] actual = value.copyPassword();
          char[] chars = new char[length];
          Arrays.fill(chars, 'A');
          try {
            assertArrayEquals(chars, actual);
          } finally {
            Arrays.fill(actual, '\0');
          }
          assertEquals(1, io.opens);
          assertEquals(1, io.closes);
          assertEquals(2, io.fileAttributes);
          assertEquals(2, io.rootAttributes);
          io.assertCleared(65537);
        }
        assertArrayEquals(expected, Files.readAllBytes(f.root.resolve(NAME)));
      }
    }
  }

  @Test
  void missingAndInvalidContent() throws Exception {
    try (var f = new Fixture(temporary)) {
      var absent = new TestIo();
      failure(() -> f.loader(absent).loadDatabasePassword());
      assertEquals(0, absent.opens);
      for (byte[] bytes :
          List.of(
              new byte[0],
              new byte[65537],
              new byte[] {(byte) 0xc2},
              "\ufeffA".getBytes(StandardCharsets.UTF_8),
              new byte[] {10},
              new byte[] {65, 0})) {
        Files.write(f.root.resolve(NAME), bytes);
        var io = new TestIo();
        failure(() -> f.loader(io).loadDatabasePassword());
        io.assertCleared(65537);
      }
      Files.write(f.root.resolve(NAME), new byte[] {65});
      for (String fault : List.of("file-missing", "file-missing-after", "close-missing")) {
        var io = new TestIo();
        io.fault = fault;
        failure(() -> f.loader(io).loadDatabasePassword());
        io.assertCleared(65537);
      }
      f.calls.closeMissing = true;
      failure(() -> f.loader(new TestIo()).loadDatabasePassword());
      f.calls.closeMissing = false;
      Files.delete(f.root.resolve(AesCredentialFile.RESPONSE_PREVIOUS.fileName()));
      assertTrue(f.loader(new TestIo()).load(AesCredentialFile.RESPONSE_PREVIOUS).isEmpty());
    }
  }

  @Test
  void permissionsAndMetadata() throws Exception {
    try (var f = new Fixture(temporary)) {
      Path file = f.root.resolve(NAME);
      Files.write(file, new byte[] {65});
      for (var change :
          List.<Consumer<Map<String, Object>>>of(
              a -> a.put("uid", 12345),
              a -> a.put(FIXTURE_MODE_B6D5C2C3, 0100640),
              a -> a.put(FIXTURE_MODE_B6D5C2C3, 040550),
              a -> a.put("nlink", 2),
              a -> a.put("nlink", 0),
              a -> a.put(FIXTURE_SIZE_EB1E91E4, 0L),
              a -> a.put(FIXTURE_SIZE_EB1E91E4, 65537L),
              a -> a.put(FIXTURE_SIZE_EB1E91E4, null),
              a -> a.put("uid", null))) {
        var io = new TestIo();
        io.fileChange = change;
        failure(() -> f.loader(io).loadDatabasePassword());
        assertEquals(0, io.opens);
      }
      for (String key :
          List.of(
              "uid",
              "gid",
              FIXTURE_MODE_B6D5C2C3,
              "nlink",
              FIXTURE_SIZE_EB1E91E4,
              "dev",
              "ino",
              "lastModifiedTime",
              "ctime")) {
        var io = new TestIo();
        io.lateFileChange = a -> a.remove(key);
        failure(() -> f.loader(io).loadDatabasePassword());
        io.assertCleared(65537);
      }
      for (String fault :
          List.of(
              "acl-root",
              "acl-file",
              "ro-root",
              "ro-file",
              "empty-acl-root",
              "empty-acl-file",
              "empty-acl-file-after",
              "ro-file-after")) {
        var io = new TestIo();
        io.securityFault = fault;
        failure(() -> f.loader(io).loadDatabasePassword());
        io.assertCleared(65537);
      }
      var directory = new TestIo();
      directory.rootChange = a -> a.put(FIXTURE_MODE_B6D5C2C3, 040750);
      failure(() -> f.loader(directory).loadDatabasePassword());
      assertEquals(0, directory.opens);
      Path other = f.root.resolve("hard-link");
      Files.createLink(other, file);
      var hard = new TestIo();
      failure(() -> f.loader(hard).loadDatabasePassword());
      assertEquals(0, hard.opens);
      Files.delete(other);
      Files.delete(file);
      Files.createSymbolicLink(file, Path.of(AesCredentialFile.CONTEXT_CURRENT.fileName()));
      var symbolic = new TestIo();
      failure(() -> f.loader(symbolic).loadDatabasePassword());
      assertEquals(0, symbolic.opens);
    }
  }

  @Test
  void ioFailuresAndCleanup() throws Exception {
    try (var f = new Fixture(temporary)) {
      Files.write(f.root.resolve(NAME), new byte[] {65, 66, 67});
      for (String fault :
          List.of(
              "attributes-root",
              "attributes-file",
              "null-file-map",
              "open",
              "unsupported",
              "read",
              "short",
              "zero",
              "negative-read",
              "lying-read",
              "huge-read",
              "long",
              "size-error-before",
              "size-error-after",
              "size-before",
              "size-after",
              "close",
              "root-final")) {
        var io = new TestIo();
        io.fault = fault;
        failure(() -> f.loader(io).loadDatabasePassword());
        io.assertCleared(65537);
        assertEquals(io.opens, io.closes);
      }
      var changed = new TestIo();
      changed.lateRootChange = a -> a.put("ino", -1L);
      failure(() -> f.loader(changed).loadDatabasePassword());
      changed.assertCleared(65537);
      f.calls.closeUnavailable = true;
      failure(() -> f.loader(new TestIo()).loadDatabasePassword());
      f.calls.closeUnavailable = false;
      f.calls.openFailure = true;
      failure(() -> f.loader(new TestIo()).loadDatabasePassword());
      f.calls.openFailure = false;
      f.held.close();
      failure(() -> f.loader(new TestIo()).loadDatabasePassword());
    }
  }

  @Test
  void concurrentFilesAndAesRegression() throws Exception {
    try (var f = new Fixture(temporary);
        var pool = Executors.newFixedThreadPool(12)) {
      Files.write(f.root.resolve(NAME), new byte[] {65, 66, 67, 13, 10});
      var calls = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 100; i++)
        calls.add(
            () -> {
              var io = new TestIo();
              try (var value = f.loader(io).loadDatabasePassword()) {
                char[] actual = value.copyPassword();
                try {
                  assertArrayEquals(new char[] {65, 66, 67}, actual);
                } finally {
                  Arrays.fill(actual, '\0');
                }
                io.assertCleared(65537);
                return true;
              }
            });
      for (var done : pool.invokeAll(calls)) assertTrue(done.get(5, TimeUnit.SECONDS));
      for (var id : AesCredentialFile.values()) {
        var io = new TestIo();
        try (var value = f.loader(io).load(id).orElseThrow()) {
          byte[] actual = value.copyKey();
          try {
            assertArrayEquals(f.keys.get(id), actual);
          } finally {
            Arrays.fill(actual, (byte) 0);
          }
          io.assertCleared();
        }
        Files.write(f.root.resolve(id.fileName()), new byte[] {65});
        failure(() -> f.loader(new TestIo()).load(id));
      }
    }
  }

  private static void failure(Executable operation) {
    var failure = assertThrows(InspectorCredentialException.class, operation);
    assertEquals("inspector credential cannot be loaded", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}

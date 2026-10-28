package dev.codex.schubert.nk.api.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.file.InspectorCredentialLoaderTest.Fixture;
import dev.codex.schubert.nk.api.file.InspectorCredentialLoaderTest.TestIo;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Fixed bootstrap-only names/independent golden, held-inode faults/zero. SS343/SSC188/BOOT007. */
final class BootstrapCredentialLoaderTest {
  private static final String FIXTURE_BOOTSTRAP_ADMIN_USERNAME_E46B3E2D =
      "bootstrap-admin-username";
  private static final String FIXTURE_BOOTSTRAP_ADMIN_PASSWORD_55E7842A =
      "bootstrap-admin-password";
  @TempDir Path temporary;

  @Test
  void fixedGoldenUsernameAndPasswordConsumeOnlyOwnedCopies() throws Exception {
    try (var f = new Fixture(temporary)) {
      for (boolean username : List.of(true, false)) {
        String name =
            username
                ? FIXTURE_BOOTSTRAP_ADMIN_USERNAME_E46B3E2D
                : FIXTURE_BOOTSTRAP_ADMIN_PASSWORD_55E7842A;
        String expected = username ? "Initial.Admin" : "synthetic-credential";
        byte[] golden = (expected + "\r\n").getBytes(StandardCharsets.UTF_8);
        Files.write(f.root.resolve(name), golden);
        var io = new TestIo();
        try (var material =
            username
                ? f.loader(io).readBootstrapUsername()
                : f.loader(io).readBootstrapPassword()) {
          char[] copy = material.copyPassword();
          assertArrayEquals(expected.toCharArray(), copy);
          Arrays.fill(copy, '\0');
          assertEquals("InspectorDbCredential[REDACTED]", material.toString());
        }
        assertArrayEquals(golden, Files.readAllBytes(f.root.resolve(name)));
        assertEquals(io.opens, io.closes);
        io.assertCleared(username ? 257 : 65537);
      }
    }
  }

  @Test
  void missingMalformedOversizedAndNoOrdinaryFallback() throws Exception {
    try (var f = new Fixture(temporary)) {
      Files.writeString(f.root.resolve("db-api"), "synthetic-credential");
      assertThrows(
          InspectorCredentialException.class, () -> f.loader(new TestIo()).readBootstrapUsername());
      assertThrows(
          InspectorCredentialException.class, () -> f.loader(new TestIo()).readBootstrapPassword());
      for (byte[] invalid :
          List.of(new byte[] {(byte) 0xff}, new byte[] {0}, new byte[] {'\n'}, new byte[0])) {
        for (String name :
            List.of(
                FIXTURE_BOOTSTRAP_ADMIN_USERNAME_E46B3E2D,
                FIXTURE_BOOTSTRAP_ADMIN_PASSWORD_55E7842A))
          Files.write(f.root.resolve(name), invalid);
        assertThrows(
            InspectorCredentialException.class,
            () -> f.loader(new TestIo()).readBootstrapUsername());
        assertThrows(
            InspectorCredentialException.class,
            () -> f.loader(new TestIo()).readBootstrapPassword());
      }
      Files.write(f.root.resolve(FIXTURE_BOOTSTRAP_ADMIN_USERNAME_E46B3E2D), new byte[257]);
      Files.write(f.root.resolve(FIXTURE_BOOTSTRAP_ADMIN_PASSWORD_55E7842A), new byte[65537]);
      assertThrows(
          InspectorCredentialException.class, () -> f.loader(new TestIo()).readBootstrapUsername());
      assertThrows(
          InspectorCredentialException.class, () -> f.loader(new TestIo()).readBootstrapPassword());
    }
  }

  @Test
  void everyIoAndSecurityFaultRejectsWithoutReturningMaterial() throws Exception {
    try (var f = new Fixture(temporary)) {
      for (boolean username : List.of(true, false)) {
        Files.writeString(
            f.root.resolve(
                username
                    ? FIXTURE_BOOTSTRAP_ADMIN_USERNAME_E46B3E2D
                    : FIXTURE_BOOTSTRAP_ADMIN_PASSWORD_55E7842A),
            "synthetic-input\n");
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
          assertThrows(
              InspectorCredentialException.class,
              () -> {
                if (username) f.loader(io).readBootstrapUsername();
                else f.loader(io).readBootstrapPassword();
              });
          io.assertCleared(username ? 257 : 65537);
          assertEquals(io.opens, io.closes);
        }
        for (String fault : List.of("acl-root", "acl-file", "ro-file", "empty-acl-file-after")) {
          var io = new TestIo();
          io.securityFault = fault;
          assertThrows(
              InspectorCredentialException.class,
              () -> {
                if (username) f.loader(io).readBootstrapUsername();
                else f.loader(io).readBootstrapPassword();
              });
        }
      }
    }
  }
}

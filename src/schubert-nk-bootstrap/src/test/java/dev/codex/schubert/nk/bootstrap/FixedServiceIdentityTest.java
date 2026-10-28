package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** PT-OPS-SERVICEID-001..008; public literal NSS vectors, no production expected generation. */
final class FixedServiceIdentityTest {
  private static final String FIXTURE_SYNTHETIC_85DA8434 = "synthetic";
  private static final String FIXTURE_PROCESS_B140B547 = "process";
  private static final String FIXTURE_FIXED_12AFF051 = "fixed";
  private static final String FIXTURE_PASSWD_SCHUBERT_API_96EE1ECC = "passwd/schubert-api";
  private static final String FIXTURE_GROUP_SCHUBERT_API_D38A74AF = "group/schubert-api";
  private static final String FIXTURE_GROUP_SCHUBERT_37A26416 = "group/schubert";
  private static final String FIXTURE_GROUP_SCHUBERT_READ_F79F2F9D = "group/schubert-read";
  private static final String FIXTURE_USR_BIN_GETENT_556F8282 = "/usr/bin/getent";
  private static final String FIXTURE_SERVICE_IDENTITY_UNAVAILABLE_2337BF6D =
      "service identity unavailable";
  private static final String FIXTURE_PASSWD_70C0A7EE = "passwd";
  private static final String FIXTURE_GROUP_654E1E20 = "group";
  private static final String FIXTURE_SCHUBERT_DDC9117F = "schubert";
  private static final String FIXTURE_SCHUBERT_READ_57E4BB8C = "schubert-read";
  private static final String FIXTURE_PRIVATE_D45CA6F9 = "PRIVATE";

  /** PT-OPS-NSSOWN001: every getter failure/null closes only already acquired resources. */
  @Test
  void nssown001GetterNullRuntimeAndFatalKeepExactPartialCleanupOrder() {
    for (int at : List.of(1, 2, 3))
      for (Throwable failure :
          new Throwable[] {
            null,
            new IllegalStateException(FIXTURE_SYNTHETIC_85DA8434),
            new LinkageError(FIXTURE_SYNTHETIC_85DA8434)
          }) {
        var events = new ArrayList<String>();
        var process =
            new Fake() {
              public InputStream getInputStream() {
                if (at == 1) {
                  if (failure != null) throwGetter(failure);
                  return null;
                }
                return super.getInputStream();
              }

              public OutputStream getOutputStream() {
                if (at == 2) {
                  if (failure != null) throwGetter(failure);
                  return null;
                }
                return super.getOutputStream();
              }

              public InputStream getErrorStream() {
                if (at == 3) {
                  if (failure != null) throwGetter(failure);
                  return null;
                }
                return super.getErrorStream();
              }

              public void destroy() {
                events.add(FIXTURE_PROCESS_B140B547);
                super.destroy();
              }
            };
        process.alive = true;
        process.out =
            new ByteArrayInputStream(bytes("PUBLIC\n")) {
              public void close() {
                events.add("stdout");
              }
            };
        process.in =
            new ByteArrayOutputStream() {
              public void close() {
                events.add("stdin");
              }
            };
        process.err =
            new ByteArrayInputStream(new byte[0]) {
              public void close() {
                events.add("stderr");
              }
            };
        Class<? extends Throwable> expected =
            failure == null ? NullPointerException.class : failure.getClass();
        Throwable actual =
            assertThrows(
                expected,
                () ->
                    new FixedServiceIdentity.NativeQuery(command -> process)
                        .read(List.of(FIXTURE_FIXED_12AFF051)));
        if (failure != null) assertSame(failure, actual);
        assertEquals(
            switch (at) {
              case 1 -> List.of(FIXTURE_PROCESS_B140B547);
              case 2 -> List.of("stdout", FIXTURE_PROCESS_B140B547);
              default -> List.of("stdin", "stdout", FIXTURE_PROCESS_B140B547);
            },
            events);
        assertEquals(1, process.destroyed);
      }
  }

  private static void throwGetter(Throwable failure) {
    if (failure instanceof RuntimeException runtime) throw runtime;
    throw (Error) failure;
  }

  /** PT-OPS-NSSOWN002: no normalization of the declared acquisition E before scope entry. */
  @Test
  void nssown002FactoryIoRuntimeFatalAndNullNeverBecomeAProcessOwner() {
    for (Throwable failure :
        new Throwable[] {
          new IOException(FIXTURE_SYNTHETIC_85DA8434),
          new IllegalStateException(FIXTURE_SYNTHETIC_85DA8434),
          new LinkageError(FIXTURE_SYNTHETIC_85DA8434),
          null
        }) {
      int[] opens = {0};
      var query =
          new FixedServiceIdentity.NativeQuery(
              command -> {
                opens[0]++;
                if (failure instanceof IOException io) throw io;
                if (failure != null) throwGetter(failure);
                return null;
              });
      Class<? extends Throwable> expected =
          failure == null ? NullPointerException.class : failure.getClass();
      Throwable actual = assertThrows(expected, () -> query.read(List.of(FIXTURE_FIXED_12AFF051)));
      if (failure != null) assertSame(failure, actual);
      assertEquals(1, opens[0]);
    }
  }

  static byte[] bytes(String s) {
    return s.getBytes(StandardCharsets.US_ASCII);
  }

  static final Map<String, String> GOLDEN =
      Map.of(
          FIXTURE_PASSWD_SCHUBERT_API_96EE1ECC,
          "schubert-api:x:999:981::/nonexistent:/usr/sbin/nologin\n",
          "passwd/schubert-web",
          "schubert-web:x:998:980::/nonexistent:/usr/sbin/nologin\n",
          FIXTURE_GROUP_SCHUBERT_API_D38A74AF,
          "schubert-api:x:981:\n",
          "group/schubert-web",
          "schubert-web:x:980:schubert-api\n",
          FIXTURE_GROUP_SCHUBERT_37A26416,
          "schubert:x:986:schubert-api,schubert-web\n",
          FIXTURE_GROUP_SCHUBERT_READ_F79F2F9D,
          "schubert-read:x:982:schubert-api,schubert-web\n");

  static final class Fixture implements FixedServiceIdentity.Query {
    final Map<String, String> values = new HashMap<>(GOLDEN);
    final List<List<String>> commands = new ArrayList<>();

    public byte[] read(List<String> command) {
      commands.add(command);
      assertEquals(FIXTURE_USR_BIN_GETENT_556F8282, command.get(0));
      return bytes(values.getOrDefault(command.get(1) + "/" + command.get(2), ""));
    }

    FixedServiceIdentity subject() {
      return new FixedServiceIdentity(this);
    }
  }

  static void rejected(Fixture f) {
    IOException e =
        assertThrows(IOException.class, () -> f.subject().resolve(ServiceConfigFiles.Service.API));
    assertEquals(FIXTURE_SERVICE_IDENTITY_UNAVAILABLE_2337BF6D, e.getMessage());
    assertNull(e.getCause());
  }

  @Test
  void dedicatedInspectorUsesOnlyFixedPrimaryConfigurationAndReadGroups() throws Exception {
    var f = new Fixture();
    f.values.put(
        "passwd/schubert-inbox-inspector",
        "schubert-inbox-inspector:x:991:976::/nonexistent:/usr/sbin/nologin\n");
    f.values.put("group/schubert-inbox-inspector", "schubert-inbox-inspector:x:976:\n");
    assertEquals(
        new FixedServiceIdentity.Value(991, 976, List.of(976L, 982L, 986L)),
        f.subject().resolveInspector());
    assertEquals(
        List.of(
            List.of(
                FIXTURE_USR_BIN_GETENT_556F8282,
                FIXTURE_PASSWD_70C0A7EE,
                "schubert-inbox-inspector"),
            List.of(
                FIXTURE_USR_BIN_GETENT_556F8282,
                FIXTURE_GROUP_654E1E20,
                "schubert-inbox-inspector"),
            List.of(
                FIXTURE_USR_BIN_GETENT_556F8282, FIXTURE_GROUP_654E1E20, FIXTURE_SCHUBERT_DDC9117F),
            List.of(
                FIXTURE_USR_BIN_GETENT_556F8282,
                FIXTURE_GROUP_654E1E20,
                FIXTURE_SCHUBERT_READ_57E4BB8C)),
        f.commands);
    f.values.put(FIXTURE_GROUP_SCHUBERT_READ_F79F2F9D, "schubert-read:x:976:\n");
    assertThrows(IOException.class, () -> f.subject().resolveInspector());
    f.values.put(FIXTURE_GROUP_SCHUBERT_READ_F79F2F9D, "schubert-read:x:982:\n");
    f.values.put("group/schubert-inbox-inspector", "schubert-inbox-inspector:x:975:\n");
    assertThrows(IOException.class, () -> f.subject().resolveInspector());
    f.values.remove("passwd/schubert-inbox-inspector");
    assertThrows(IOException.class, () -> f.subject().resolveInspector());
  }

  @Test
  void issuerRootsUseFixedDataMigrationAndReadGroupWithoutApplicationAuthority() throws Exception {
    var f = new Fixture();
    f.values.put(
        "passwd/schubert-data", "schubert-data:x:990:975::/nonexistent:/usr/sbin/nologin\n");
    f.values.put("group/schubert-data", "schubert-data:x:975:\n");
    f.values.put(
        "passwd/schubert-migration",
        "schubert-migration:x:989:974::/nonexistent:/usr/sbin/nologin\n");
    f.values.put("group/schubert-migration", "schubert-migration:x:974:\n");
    assertEquals(
        new FixedServiceIdentity.Value(990, 975, List.of(975L, 982L)),
        f.subject().resolveDataOwner());
    assertEquals(
        new FixedServiceIdentity.Value(989, 974, List.of(974L)), f.subject().resolveMigration());
    assertEquals(982L, f.subject().dataReadGroup());
    assertEquals(
        List.of(
            List.of(FIXTURE_USR_BIN_GETENT_556F8282, FIXTURE_PASSWD_70C0A7EE, "schubert-data"),
            List.of(FIXTURE_USR_BIN_GETENT_556F8282, FIXTURE_GROUP_654E1E20, "schubert-data"),
            List.of(
                FIXTURE_USR_BIN_GETENT_556F8282,
                FIXTURE_GROUP_654E1E20,
                FIXTURE_SCHUBERT_READ_57E4BB8C),
            List.of(FIXTURE_USR_BIN_GETENT_556F8282, FIXTURE_PASSWD_70C0A7EE, "schubert-migration"),
            List.of(FIXTURE_USR_BIN_GETENT_556F8282, FIXTURE_GROUP_654E1E20, "schubert-migration"),
            List.of(
                FIXTURE_USR_BIN_GETENT_556F8282,
                FIXTURE_GROUP_654E1E20,
                FIXTURE_SCHUBERT_READ_57E4BB8C)),
        f.commands);
    f.values.put("group/schubert-data", "schubert-data:x:982:\n");
    assertThrows(IOException.class, () -> f.subject().resolveDataOwner());
    f.values.put("group/schubert-data", "schubert-data:x:975:\n");
    f.values.put(FIXTURE_GROUP_SCHUBERT_READ_F79F2F9D, "schubert-read:x:975:\n");
    assertThrows(IOException.class, () -> f.subject().resolveDataOwner());
    f.values.remove("passwd/schubert-migration");
    assertThrows(IOException.class, () -> f.subject().resolveMigration());
    f.values.put(FIXTURE_GROUP_SCHUBERT_READ_F79F2F9D, "schubert-read:x:0:\n");
    assertEquals(
        FIXTURE_SERVICE_IDENTITY_UNAVAILABLE_2337BF6D,
        assertThrows(IOException.class, () -> f.subject().dataReadGroup()).getMessage());
    f.values.remove(FIXTURE_GROUP_SCHUBERT_READ_F79F2F9D);
    assertThrows(IOException.class, () -> f.subject().dataReadGroup());
  }

  @Test
  void serviceid001BothFixedAccountsExplicitRequiredGroups() {
    var backup = new Fixture();
    backup.values.put(
        "passwd/schubert-backup", "schubert-backup:x:992:977::/nonexistent:/usr/sbin/nologin\n");
    backup.values.put("group/schubert-backup", "schubert-backup:x:977:\n");
    assertEquals(
        new FixedServiceIdentity.Value(992, 977, List.of(977L, 986L)),
        assertDoesNotThrow(() -> backup.subject().resolveBackup()));
    assertEquals(
        List.of(
            List.of(FIXTURE_USR_BIN_GETENT_556F8282, FIXTURE_PASSWD_70C0A7EE, "schubert-backup"),
            List.of(FIXTURE_USR_BIN_GETENT_556F8282, FIXTURE_GROUP_654E1E20, "schubert-backup"),
            List.of(
                FIXTURE_USR_BIN_GETENT_556F8282,
                FIXTURE_GROUP_654E1E20,
                FIXTURE_SCHUBERT_DDC9117F)),
        backup.commands);
    backup.values.put("group/schubert-backup", "schubert-backup:x:978:\n");
    assertThrows(IOException.class, () -> backup.subject().resolveBackup());
    backup.values.put("group/schubert-backup", "schubert-backup:x:977:\n");
    backup.values.put(FIXTURE_GROUP_SCHUBERT_37A26416, "schubert:x:977:\n");
    assertThrows(IOException.class, () -> backup.subject().resolveBackup());
    backup.values.remove("passwd/schubert-backup");
    assertThrows(IOException.class, () -> backup.subject().resolveBackup());
    var f = new Fixture();
    assertEquals(
        new FixedServiceIdentity.Value(999, 981, List.of(980L, 981L, 982L, 986L)),
        assertDoesNotThrow(() -> f.subject().resolve(ServiceConfigFiles.Service.API)));
    assertEquals(
        List.of(
            List.of(FIXTURE_USR_BIN_GETENT_556F8282, FIXTURE_PASSWD_70C0A7EE, "schubert-api"),
            List.of(FIXTURE_USR_BIN_GETENT_556F8282, FIXTURE_GROUP_654E1E20, "schubert-api"),
            List.of(
                FIXTURE_USR_BIN_GETENT_556F8282, FIXTURE_GROUP_654E1E20, FIXTURE_SCHUBERT_DDC9117F),
            List.of(
                FIXTURE_USR_BIN_GETENT_556F8282,
                FIXTURE_GROUP_654E1E20,
                FIXTURE_SCHUBERT_READ_57E4BB8C),
            List.of(FIXTURE_USR_BIN_GETENT_556F8282, FIXTURE_GROUP_654E1E20, "schubert-web")),
        f.commands);
    f.commands.clear();
    assertEquals(
        new FixedServiceIdentity.Value(998, 980, List.of(980L, 982L, 986L)),
        assertDoesNotThrow(() -> f.subject().resolve(ServiceConfigFiles.Service.WEB)));
    assertEquals(4, f.commands.size());
    f.commands.clear();
    assertEquals(986L, assertDoesNotThrow(() -> f.subject().configurationGroup()));
    assertEquals(
        List.of(
            List.of(
                FIXTURE_USR_BIN_GETENT_556F8282,
                FIXTURE_GROUP_654E1E20,
                FIXTURE_SCHUBERT_DDC9117F)),
        f.commands);
    f.values.put(FIXTURE_GROUP_SCHUBERT_37A26416, "schubert:x:0:\n");
    assertEquals(
        FIXTURE_SERVICE_IDENTITY_UNAVAILABLE_2337BF6D,
        assertThrows(IOException.class, () -> f.subject().configurationGroup()).getMessage());
    var v = new FixedServiceIdentity.Value(999, 981, List.of(980L, 981L, 982L, 986L));
    assertEquals("980,981,982,986", v.groupArgument());
    assertEquals("FixedServiceIdentity.Value[REDACTED]", v.toString());
    assertThrows(UnsupportedOperationException.class, () -> v.groups().add(1L));
  }

  @Test
  void serviceid002EveryFixedRowMalformedMissingAliasAndShadowMarker() {
    for (String key :
        List.of(
            FIXTURE_PASSWD_SCHUBERT_API_96EE1ECC,
            FIXTURE_GROUP_SCHUBERT_API_D38A74AF,
            FIXTURE_GROUP_SCHUBERT_37A26416,
            FIXTURE_GROUP_SCHUBERT_READ_F79F2F9D,
            "group/schubert-web"))
      for (String bad :
          List.of(
              "",
              GOLDEN.get(key) + GOLDEN.get(key),
              GOLDEN.get(key).trim(),
              GOLDEN.get(key).replace(":x:", ":PRIVATE:"),
              GOLDEN.get(key).replaceFirst(FIXTURE_SCHUBERT_DDC9117F, "other"),
              GOLDEN.get(key).replace("\n", ":extra\n"),
              GOLDEN.get(key).replaceFirst(":", ""))) {
        var f = new Fixture();
        f.values.put(key, bad);
        rejected(f);
      }
  }

  @Test
  void serviceid003UidGidBoundariesAndCanonicalDecimal() {
    for (String key :
        List.of(FIXTURE_PASSWD_SCHUBERT_API_96EE1ECC, FIXTURE_GROUP_SCHUBERT_API_D38A74AF))
      for (String bad : List.of("0", "01", "-1", "+1", "4294967295", "99999999999", "a", "1.0")) {
        var f = new Fixture();
        String original = key.startsWith(FIXTURE_PASSWD_70C0A7EE) ? ":999:" : ":981:";
        f.values.put(key, f.values.get(key).replace(original, ":" + bad + ":"));
        rejected(f);
      }
    var f = new Fixture();
    f.values.put(
        FIXTURE_PASSWD_SCHUBERT_API_96EE1ECC,
        GOLDEN.get(FIXTURE_PASSWD_SCHUBERT_API_96EE1ECC).replace(":999:", ":4294967294:"));
    assertEquals(
        4294967294L,
        assertDoesNotThrow(() -> f.subject().resolve(ServiceConfigFiles.Service.API)).uid());
    f.values.put(
        FIXTURE_PASSWD_SCHUBERT_API_96EE1ECC,
        GOLDEN.get(FIXTURE_PASSWD_SCHUBERT_API_96EE1ECC).replace(":999:", ":1:"));
    assertEquals(
        1L, assertDoesNotThrow(() -> f.subject().resolve(ServiceConfigFiles.Service.API)).uid());
  }

  @Test
  void serviceid004PrimaryMismatchDuplicateGroupsAndImplicitMembershipIgnored() {
    var f = new Fixture();
    f.values.put(FIXTURE_GROUP_SCHUBERT_API_D38A74AF, "schubert-api:x:900:\n");
    rejected(f);
    f = new Fixture();
    f.values.put(FIXTURE_GROUP_SCHUBERT_READ_F79F2F9D, "schubert-read:x:986:extra,unrelated\n");
    rejected(f);
    var publicMembers = new Fixture();
    publicMembers.values.put(FIXTURE_GROUP_SCHUBERT_37A26416, "schubert:x:986:extra,unrelated\n");
    assertEquals(
        List.of(980L, 981L, 982L, 986L),
        assertDoesNotThrow(() -> publicMembers.subject().resolve(ServiceConfigFiles.Service.API))
            .groups());
    assertTrue(publicMembers.commands.stream().noneMatch(c -> c.get(1).equals("initgroups")));
  }

  @Test
  void serviceid005ByteNullAndImmutableValueInvariant() {
    var exact = new Fixture();
    exact.values.put(FIXTURE_GROUP_SCHUBERT_37A26416, "schubert:x:986:" + "m".repeat(1008) + "\n");
    assertEquals(1024, bytes(exact.values.get(FIXTURE_GROUP_SCHUBERT_37A26416)).length);
    assertEquals(
        List.of(980L, 981L, 982L, 986L),
        assertDoesNotThrow(() -> exact.subject().resolve(ServiceConfigFiles.Service.API)).groups());
    for (String bad :
        List.of(
            "\n",
            "x".repeat(1025),
            GOLDEN.get(FIXTURE_PASSWD_SCHUBERT_API_96EE1ECC).replace("\n", "\r\n"),
            GOLDEN.get(FIXTURE_PASSWD_SCHUBERT_API_96EE1ECC).replace("x", "\t"),
            GOLDEN.get(FIXTURE_PASSWD_SCHUBERT_API_96EE1ECC).replace("x", "\u007f"))) {
      var f = new Fixture();
      f.values.put(FIXTURE_PASSWD_SCHUBERT_API_96EE1ECC, bad);
      rejected(f);
    }
    assertThrows(NullPointerException.class, () -> new FixedServiceIdentity(null));
    assertThrows(NullPointerException.class, () -> new Fixture().subject().resolve(null));
    assertThrows(
        NullPointerException.class,
        () -> new FixedServiceIdentity(c -> null).resolve(ServiceConfigFiles.Service.API));
    for (long id : List.of(0L, -1L, 4294967295L)) {
      assertThrows(
          IllegalArgumentException.class, () -> new FixedServiceIdentity.Value(id, 2, List.of(2L)));
      assertThrows(
          IllegalArgumentException.class, () -> new FixedServiceIdentity.Value(1, id, List.of(2L)));
    }
    for (List<Long> groups :
        List.of(
            List.<Long>of(),
            List.of(1L),
            List.of(2L, 2L),
            List.of(2L, 1L),
            List.of(0L, 2L),
            List.of(2L, 4294967295L),
            java.util.stream.LongStream.rangeClosed(1, 17).boxed().toList()))
      assertThrows(
          IllegalArgumentException.class, () -> new FixedServiceIdentity.Value(1, 2, groups));
    assertThrows(NullPointerException.class, () -> new FixedServiceIdentity.Value(1, 2, null));
    assertThrows(
        NullPointerException.class,
        () -> new FixedServiceIdentity.Value(1, 2, Arrays.asList(2L, null)));
    var original = new ArrayList<>(List.of(2L));
    var v = new FixedServiceIdentity.Value(4294967294L, 4294967294L, List.of(4294967294L));
    assertEquals("4294967294", v.groupArgument());
    var copy = new FixedServiceIdentity.Value(1, 2, original);
    original.add(3L);
    assertEquals(List.of(2L), copy.groups());
  }

  static class Fake extends Process {
    boolean alive;
    boolean done = true;
    boolean interrupt;
    int exit;
    int destroyed;
    InputStream out = new ByteArrayInputStream(bytes("PUBLIC\n"));
    InputStream err = new ByteArrayInputStream(new byte[0]);
    OutputStream in = new ByteArrayOutputStream();

    public InputStream getInputStream() {
      return out;
    }

    public InputStream getErrorStream() {
      return err;
    }

    public OutputStream getOutputStream() {
      return in;
    }

    public int waitFor() {
      return exit;
    }

    public boolean waitFor(long t, TimeUnit u) throws InterruptedException {
      assertEquals(5, t);
      assertEquals(TimeUnit.SECONDS, u);
      if (interrupt) throw new InterruptedException();
      return done;
    }

    public int exitValue() {
      return exit;
    }

    public boolean isAlive() {
      return alive;
    }

    public void destroy() {
      destroyed++;
      alive = false;
    }
  }

  @Test
  void serviceid006NativeQueryTimeoutExitInterruptAndNoInheritedSecrets() {
    var command =
        List.of(FIXTURE_USR_BIN_GETENT_556F8282, FIXTURE_GROUP_654E1E20, FIXTURE_SCHUBERT_DDC9117F);
    var p = new Fake();
    assertArrayEquals(
        bytes("PUBLIC\n"),
        assertDoesNotThrow(
            () ->
                new FixedServiceIdentity.NativeQuery(
                        c -> {
                          assertEquals(command, c);
                          return p;
                        })
                    .read(command)));
    assertEquals(
        Map.of("PATH", "/usr/bin:/bin", "LANG", "C", "LC_ALL", "C"),
        FixedServiceIdentity.NativeQuery.builder(command).environment());
    for (int bad : List.of(1, 2, 3)) {
      var q = new Fake();
      q.alive = true;
      if (bad == 1) q.done = false;
      if (bad == 2) q.exit = 1;
      if (bad == 3) q.interrupt = true;
      assertThrows(
          IOException.class, () -> new FixedServiceIdentity.NativeQuery(c -> q).read(command));
      assertEquals(1, q.destroyed);
      if (bad == 3) assertTrue(Thread.interrupted());
    }
    assertThrows(
        IOException.class,
        () ->
            new FixedServiceIdentity.NativeQuery(
                    c -> {
                      throw new IOException();
                    })
                .read(command));
    assertThrows(NullPointerException.class, () -> new FixedServiceIdentity.NativeQuery(null));
    assertThrows(
        NullPointerException.class,
        () -> new FixedServiceIdentity.NativeQuery(c -> null).read(command));
  }

  @Test
  void serviceid007EveryOwnedCloseAndUnknownFailurePreserved() {
    for (int position : List.of(1, 2, 3)) {
      var p = new Fake();
      p.alive = true;
      if (position == 1)
        p.out =
            new ByteArrayInputStream(new byte[0]) {
              @Override
              public void close() throws IOException {
                throw new IOException(FIXTURE_PRIVATE_D45CA6F9);
              }
            };
      if (position == 2)
        p.in =
            new ByteArrayOutputStream() {
              @Override
              public void close() throws IOException {
                throw new IOException(FIXTURE_PRIVATE_D45CA6F9);
              }
            };
      if (position == 3)
        p.err =
            new ByteArrayInputStream(new byte[0]) {
              @Override
              public void close() throws IOException {
                throw new IOException(FIXTURE_PRIVATE_D45CA6F9);
              }
            };
      assertThrows(
          IOException.class,
          () -> new FixedServiceIdentity.NativeQuery(c -> p).read(List.of(FIXTURE_FIXED_12AFF051)));
      assertEquals(1, p.destroyed);
    }
    var p = new Fake();
    p.done = false;
    p.alive = true;
    var fatal = new AssertionError(FIXTURE_PRIVATE_D45CA6F9);
    p.out =
        new ByteArrayInputStream(new byte[0]) {
          @Override
          public void close() {
            throw fatal;
          }
        };
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class,
            () ->
                new FixedServiceIdentity.NativeQuery(c -> p)
                    .read(List.of(FIXTURE_FIXED_12AFF051))));
    assertEquals(1, p.destroyed);
    IOException known = new IOException(FIXTURE_PRIVATE_D45CA6F9);
    IOException fixed =
        assertThrows(
            IOException.class,
            () ->
                new FixedServiceIdentity(
                        c -> {
                          throw known;
                        })
                    .resolve(ServiceConfigFiles.Service.API));
    assertEquals(FIXTURE_SERVICE_IDENTITY_UNAVAILABLE_2337BF6D, fixed.getMessage());
    assertNull(fixed.getCause());
  }

  @Test
  void serviceid008ConcurrentLiteralVectorsAndNativeUnprovisionedRejection() throws Exception {
    var pool = Executors.newFixedThreadPool(8);
    try {
      var jobs = new ArrayList<Callable<FixedServiceIdentity.Value>>();
      for (int i = 0; i < 32; i++)
        jobs.add(() -> new Fixture().subject().resolve(ServiceConfigFiles.Service.API));
      for (var f : pool.invokeAll(jobs))
        assertEquals(
            new FixedServiceIdentity.Value(999, 981, List.of(980L, 981L, 982L, 986L)), f.get());
    } finally {
      pool.shutdownNow();
    }
    assertThrows(
        IOException.class,
        () -> new FixedServiceIdentity().resolve(ServiceConfigFiles.Service.API));
  }
}

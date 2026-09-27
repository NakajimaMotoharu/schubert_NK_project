package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.*;
import org.junit.jupiter.api.Test;

/** PT-OPS-SERVICEID-001..008; public literal NSS vectors, no production expected generation. */
final class FixedServiceIdentityTest {
  static byte[] bytes(String s) {
    return s.getBytes(StandardCharsets.US_ASCII);
  }

  static final Map<String, String> GOLDEN =
      Map.of(
          "passwd/schubert-api", "schubert-api:x:999:981::/nonexistent:/usr/sbin/nologin\n",
          "passwd/schubert-web", "schubert-web:x:998:980::/nonexistent:/usr/sbin/nologin\n",
          "group/schubert-api", "schubert-api:x:981:\n",
          "group/schubert-web", "schubert-web:x:980:schubert-api\n",
          "group/schubert", "schubert:x:986:schubert-api,schubert-web\n",
          "group/schubert-read", "schubert-read:x:982:schubert-api,schubert-web\n");

  static final class Fixture implements FixedServiceIdentity.Query {
    final Map<String, String> values = new HashMap<>(GOLDEN);
    final List<List<String>> commands = new ArrayList<>();

    public byte[] read(List<String> command) {
      commands.add(command);
      assertEquals("/usr/bin/getent", command.get(0));
      return bytes(values.getOrDefault(command.get(1) + "/" + command.get(2), ""));
    }

    FixedServiceIdentity subject() {
      return new FixedServiceIdentity(this);
    }
  }

  static void rejected(Fixture f) {
    IOException e =
        assertThrows(IOException.class, () -> f.subject().resolve(ServiceConfigFiles.Service.API));
    assertEquals("service identity unavailable", e.getMessage());
    assertNull(e.getCause());
  }

  @Test
  void serviceid001BothFixedAccountsExplicitRequiredGroups() {
    var f = new Fixture();
    assertEquals(
        new FixedServiceIdentity.Value(999, 981, List.of(980L, 981L, 982L, 986L)),
        assertDoesNotThrow(() -> f.subject().resolve(ServiceConfigFiles.Service.API)));
    assertEquals(
        List.of(
            List.of("/usr/bin/getent", "passwd", "schubert-api"),
            List.of("/usr/bin/getent", "group", "schubert-api"),
            List.of("/usr/bin/getent", "group", "schubert"),
            List.of("/usr/bin/getent", "group", "schubert-read"),
            List.of("/usr/bin/getent", "group", "schubert-web")),
        f.commands);
    f.commands.clear();
    assertEquals(
        new FixedServiceIdentity.Value(998, 980, List.of(980L, 982L, 986L)),
        assertDoesNotThrow(() -> f.subject().resolve(ServiceConfigFiles.Service.WEB)));
    assertEquals(4, f.commands.size());
    var v = new FixedServiceIdentity.Value(999, 981, List.of(980L, 981L, 982L, 986L));
    assertEquals("980,981,982,986", v.groupArgument());
    assertEquals("FixedServiceIdentity.Value[REDACTED]", v.toString());
    assertThrows(UnsupportedOperationException.class, () -> v.groups().add(1L));
  }

  @Test
  void serviceid002EveryFixedRowMalformedMissingAliasAndShadowMarker() {
    for (String key :
        List.of(
            "passwd/schubert-api",
            "group/schubert-api",
            "group/schubert",
            "group/schubert-read",
            "group/schubert-web"))
      for (String bad :
          List.of(
              "",
              GOLDEN.get(key) + GOLDEN.get(key),
              GOLDEN.get(key).trim(),
              GOLDEN.get(key).replace(":x:", ":PRIVATE:"),
              GOLDEN.get(key).replaceFirst("schubert", "other"),
              GOLDEN.get(key).replace("\n", ":extra\n"),
              GOLDEN.get(key).replaceFirst(":", ""))) {
        var f = new Fixture();
        f.values.put(key, bad);
        rejected(f);
      }
  }

  @Test
  void serviceid003UidGidBoundariesAndCanonicalDecimal() {
    for (String key : List.of("passwd/schubert-api", "group/schubert-api"))
      for (String bad : List.of("0", "01", "-1", "+1", "4294967295", "99999999999", "a", "1.0")) {
        var f = new Fixture();
        String original = key.startsWith("passwd") ? ":999:" : ":981:";
        f.values.put(key, f.values.get(key).replace(original, ":" + bad + ":"));
        rejected(f);
      }
    var f = new Fixture();
    f.values.put(
        "passwd/schubert-api", GOLDEN.get("passwd/schubert-api").replace(":999:", ":4294967294:"));
    assertEquals(
        4294967294L,
        assertDoesNotThrow(() -> f.subject().resolve(ServiceConfigFiles.Service.API)).uid());
    f.values.put("passwd/schubert-api", GOLDEN.get("passwd/schubert-api").replace(":999:", ":1:"));
    assertEquals(
        1L, assertDoesNotThrow(() -> f.subject().resolve(ServiceConfigFiles.Service.API)).uid());
  }

  @Test
  void serviceid004PrimaryMismatchDuplicateGroupsAndImplicitMembershipIgnored() {
    var f = new Fixture();
    f.values.put("group/schubert-api", "schubert-api:x:900:\n");
    rejected(f);
    f = new Fixture();
    f.values.put("group/schubert-read", "schubert-read:x:986:extra,unrelated\n");
    rejected(f);
    var publicMembers = new Fixture();
    publicMembers.values.put("group/schubert", "schubert:x:986:extra,unrelated\n");
    assertEquals(
        List.of(980L, 981L, 982L, 986L),
        assertDoesNotThrow(() -> publicMembers.subject().resolve(ServiceConfigFiles.Service.API))
            .groups());
    assertTrue(publicMembers.commands.stream().noneMatch(c -> c.get(1).equals("initgroups")));
  }

  @Test
  void serviceid005ByteNullAndImmutableValueInvariant() {
    var exact = new Fixture();
    exact.values.put("group/schubert", "schubert:x:986:" + "m".repeat(1008) + "\n");
    assertEquals(1024, bytes(exact.values.get("group/schubert")).length);
    assertEquals(
        List.of(980L, 981L, 982L, 986L),
        assertDoesNotThrow(() -> exact.subject().resolve(ServiceConfigFiles.Service.API)).groups());
    for (String bad :
        List.of(
            "\n",
            "x".repeat(1025),
            GOLDEN.get("passwd/schubert-api").replace("\n", "\r\n"),
            GOLDEN.get("passwd/schubert-api").replace("x", "\t"),
            GOLDEN.get("passwd/schubert-api").replace("x", "\u007f"))) {
      var f = new Fixture();
      f.values.put("passwd/schubert-api", bad);
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

  static final class Fake extends Process {
    boolean alive, done = true, interrupt;
    int exit, destroyed;
    InputStream out = new ByteArrayInputStream(bytes("PUBLIC\n")),
        err = new ByteArrayInputStream(new byte[0]);
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
    var command = List.of("/usr/bin/getent", "group", "schubert");
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
                throw new IOException("PRIVATE");
              }
            };
      if (position == 2)
        p.in =
            new ByteArrayOutputStream() {
              @Override
              public void close() throws IOException {
                throw new IOException("PRIVATE");
              }
            };
      if (position == 3)
        p.err =
            new ByteArrayInputStream(new byte[0]) {
              @Override
              public void close() throws IOException {
                throw new IOException("PRIVATE");
              }
            };
      assertThrows(
          IOException.class,
          () -> new FixedServiceIdentity.NativeQuery(c -> p).read(List.of("fixed")));
      assertEquals(1, p.destroyed);
    }
    var p = new Fake();
    p.done = false;
    p.alive = true;
    var fatal = new AssertionError("PRIVATE");
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
            () -> new FixedServiceIdentity.NativeQuery(c -> p).read(List.of("fixed"))));
    assertEquals(1, p.destroyed);
    IOException known = new IOException("PRIVATE");
    IOException fixed =
        assertThrows(
            IOException.class,
            () ->
                new FixedServiceIdentity(
                        c -> {
                          throw known;
                        })
                    .resolve(ServiceConfigFiles.Service.API));
    assertEquals("service identity unavailable", fixed.getMessage());
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

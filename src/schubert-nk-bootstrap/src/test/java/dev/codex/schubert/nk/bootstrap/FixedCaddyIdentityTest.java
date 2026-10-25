package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-CADDY-ID001..003; SS342/SSC178181, literal Query only, no NSS/Unit authority. */
final class FixedCaddyIdentityTest {
  private static final String PASSWD = "caddy:x:997:993::/nonexistent:/usr/sbin/nologin\n";
  private static final String GROUP = "caddy:x:993:\n";

  private static final class Fixture implements FixedServiceIdentity.Query {
    private final String passwd;
    private final String group;
    private final List<List<String>> commands = new ArrayList<>();

    private Fixture(String passwd, String group) {
      this.passwd = passwd;
      this.group = group;
    }

    @Override
    public byte[] read(List<String> command) {
      commands.add(List.copyOf(command));
      assertEquals("/usr/bin/getent", command.get(0));
      assertEquals("caddy", command.get(2));
      String result =
          switch (command.get(1)) {
            case "passwd" -> passwd;
            case "group" -> group;
            default -> throw new AssertionError("unexpected literal query");
          };
      return result.getBytes(StandardCharsets.US_ASCII);
    }
  }

  @Test
  void caddy001FixedAccountAndPrimaryOnlyUseExactlyTwoLiteralQueries() throws Exception {
    var fixture = new Fixture(PASSWD, GROUP);
    var actual = new FixedServiceIdentity(fixture).resolveCaddy();
    assertEquals(997L, actual.uid());
    assertEquals(993L, actual.gid());
    assertEquals(List.of(993L), actual.groups());
    assertEquals("993", actual.groupArgument());
    assertEquals(
        List.of(
            List.of("/usr/bin/getent", "passwd", "caddy"),
            List.of("/usr/bin/getent", "group", "caddy")),
        fixture.commands);
    assertThrows(UnsupportedOperationException.class, () -> actual.groups().add(986L));
  }

  @Test
  void caddy002MissingMalformedAndMismatchedRecordsNeverProduceIdentity() {
    for (String passwd :
        List.of(
            "",
            PASSWD.replace("caddy:", "other:"),
            PASSWD.replace(":997:", ":0:"),
            PASSWD.replace(":997:", ":4294967295:"),
            PASSWD + PASSWD)) {
      var fixture = new Fixture(passwd, GROUP);
      rejected(fixture);
      assertEquals(1, fixture.commands.size());
    }
    for (String group :
        List.of("", "other:x:993:\n", "caddy:x:994:\n", "caddy:x:0:\n", GROUP + GROUP)) {
      var fixture = new Fixture(PASSWD, group);
      rejected(fixture);
      assertEquals(2, fixture.commands.size());
    }
  }

  private static void rejected(Fixture fixture) {
    var error =
        assertThrows(IOException.class, () -> new FixedServiceIdentity(fixture).resolveCaddy());
    assertEquals("service identity unavailable", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  @Test
  void caddy003ProviderIoIsRedactedButRuntimeAndFatalAreNotDowngraded() {
    for (Throwable marker :
        List.of(
            new IOException("synthetic private IO"),
            new IllegalStateException("synthetic provider runtime"),
            new LinkageError("synthetic fatal"))) {
      var calls = new java.util.concurrent.atomic.AtomicInteger();
      var subject =
          new FixedServiceIdentity(
              command -> {
                calls.incrementAndGet();
                if (marker instanceof IOException io) throw io;
                if (marker instanceof RuntimeException runtime) throw runtime;
                throw (Error) marker;
              });
      if (marker instanceof IOException) {
        var actual = assertThrows(IOException.class, subject::resolveCaddy);
        assertEquals("service identity unavailable", actual.getMessage());
        assertNull(actual.getCause());
        assertEquals(0, actual.getSuppressed().length);
      } else {
        assertSame(marker, assertThrows(marker.getClass(), subject::resolveCaddy));
      }
      assertEquals(1, calls.get());
    }
    var absent = assertThrows(NullPointerException.class, () -> new FixedServiceIdentity(null));
    assertEquals("fixed NSS query", absent.getMessage());
  }
}

package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Locale;
import org.junit.jupiter.api.Test;

/** ROOTUNIT001..002: exact fixed Root candidate/own ordinary credential contracts. SSC137/139. */
final class RootServiceUnitTest {
  @Test
  void bothClosedRootEntriesPreserveOwnFiveCredentialsAndOrdinaryIdentity() throws Exception {
    for (String role : List.of("api", "web")) {
      String content =
          Files.readString(
              Path.of("../../src/deployment/systemd/schubert-nk-" + role + ".service.template"));
      assertTrue(content.contains("User=schubert-" + role + "\nGroup=schubert-" + role + "\n"));
      String exec =
          content.lines().filter(x -> x.startsWith("ExecStart=")).findFirst().orElseThrow();
      assertTrue(exec.startsWith("ExecStart=!/usr/bin/java --enable-native-access=ALL-UNNAMED "));
      assertTrue(
          exec.endsWith(
              "-cp /opt/schubert-nk/current/operations/batch.jar:/opt/schubert-nk/current/operations/lib/* dev.codex.schubert.nk.batch.file.RootServiceLauncher "
                  + role.toUpperCase(Locale.ROOT)));
      assertTrue(
          content.contains(
              "CapabilityBoundingSet=CAP_SETUID CAP_SETGID CAP_SETPCAP CAP_SYS_PTRACE CAP_DAC_READ_SEARCH\n"));
      List<String> names =
          content
              .lines()
              .filter(x -> x.startsWith("LoadCredential="))
              .map(x -> x.substring(15, x.indexOf(':')))
              .toList();
      assertEquals(
          role.equals("api")
              ? List.of(
                  "db-api",
                  "mq-api",
                  "api-context-aes-current",
                  "api-inbox-response-aes-current",
                  "operation-hmac-current")
              : List.of(
                  "db-web",
                  "mq-web",
                  "web-session-aes-current",
                  "web-revoke-aes-current",
                  "web-log-aes-current"),
          names);
      assertFalse(names.contains("mq-ops"));
      assertFalse(names.contains("db-batch"));
      for (String fixed :
          List.of(
              "NoNewPrivileges=true",
              "ProtectSystem=strict",
              "SendSIGKILL=no",
              "Restart=on-failure",
              "TimeoutStartSec=120s")) assertTrue(content.contains(fixed + "\n"), fixed);
    }
  }

  @Test
  void apiCannotQueueAParentOwnedExpiryByRequires() throws Exception {
    String content =
        Files.readString(Path.of("../../src/deployment/systemd/schubert-nk-api.service.template"));
    assertEquals(
        "Requires=artemis.service postgresql.service",
        content.lines().filter(x -> x.startsWith("Requires=")).findFirst().orElseThrow());
    assertEquals(
        "After=schubert-nk-expiry-cleanup.service artemis.service postgresql.service",
        content.lines().filter(x -> x.startsWith("After=")).findFirst().orElseThrow());
  }
}

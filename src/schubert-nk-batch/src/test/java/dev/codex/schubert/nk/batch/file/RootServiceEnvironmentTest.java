package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.lang.management.ManagementFactory;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** OPS009/UI251/SS342/343; PT-OPS-ROOTENV-001..003, fixed launch environment only. */
final class RootServiceEnvironmentTest {
  @Test
  void eachServiceExportsExactlyFiveLiteralBindingsAndNoInheritedExtras() throws Exception {
    child("API", "/run/credentials/schubert-nk-api.service", "accept");
    child("WEB", "/run/credentials/schubert-nk-web.service", "accept");
  }

  @Test
  void missingWrongServiceRelativeAndExtraSuffixCredentialPathsAreRejected() throws Exception {
    for (String role : new String[] {"API", "WEB"}) {
      child(role, null, "reject");
      child(role, "/run/credentials/other.service", "reject");
      child(role, "run/credentials/relative", "reject");
      String exact =
          role.equals("API")
              ? "/run/credentials/schubert-nk-api.service"
              : "/run/credentials/schubert-nk-web.service";
      child(role, exact + ".part", "reject");
    }
  }

  @Test
  void absentOrForeignSelfFailsBeforeReadingAnyCredentialLocation() {
    var api = RootServiceProofTest.self(RootStartupContext.Service.API);
    assertThrows(
        NullPointerException.class, () -> RootServiceLauncher.environment(null, api, 128, 129));
    assertThrows(
        NullPointerException.class,
        () -> RootServiceLauncher.environment(ServiceConfigFiles.Service.API, null, 128, 129));
    assertThrows(
        IOException.class,
        () -> RootServiceLauncher.environment(ServiceConfigFiles.Service.WEB, api, 128, 129));
  }

  private static void child(String role, String location, String expected) throws Exception {
    var command = new ArrayList<String>();
    command.add(Path.of(System.getProperty("java.home"), "bin", "java").toString());
    var agents =
        ManagementFactory.getRuntimeMXBean().getInputArguments().stream()
            .filter(a -> a.startsWith("-javaagent:") && a.contains("org.jacoco.agent"))
            .toList();
    assertEquals(1, agents.size(), "same-run coverage agent is required for child observations");
    command.addAll(agents);
    command.addAll(
        java.util.List.of(
            "-cp", System.getProperty("java.class.path"), Child.class.getName(), role, expected));
    var builder = new ProcessBuilder(command).redirectErrorStream(true);
    builder.environment().clear();
    if (location != null) builder.environment().put("CREDENTIALS_DIRECTORY", location);
    builder.environment().put("INVOCATION_ID", "PUBLIC_UNTRUSTED_INHERITED_VALUE");
    builder.environment().put("SCHUBERT_NK_CONFIG_DIR", "/tmp/public-untrusted-config");
    builder.environment().put("UNAPPROVED_EXTRA", "PUBLIC_EXTRA");
    var process = builder.start();
    try {
      assertTrue(process.waitFor(30, TimeUnit.SECONDS), "owned fixture must finish");
      String output = new String(process.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
      assertEquals(0, process.exitValue(), output);
      assertEquals("ROOTENV_LITERAL_ASSERTIONS_OK\n", output);
    } finally {
      if (process.isAlive()) {
        process.destroy();
        assertTrue(process.waitFor(10, TimeUnit.SECONDS), "owned fixture normal TERM");
      }
    }
  }

  public static final class Child {
    private Child() {}

    public static void main(String[] args) throws Exception {
      var service = ServiceConfigFiles.Service.valueOf(args[0]);
      var self = RootServiceProofTest.self(RootStartupContext.Service.valueOf(args[0]));
      if (args[1].equals("accept")) {
        String credentials =
            args[0].equals("API")
                ? "/run/credentials/schubert-nk-api.service"
                : "/run/credentials/schubert-nk-web.service";
        Map<String, String> expected =
            Map.of(
                "INVOCATION_ID", "22222222222222222222222222222222",
                "CREDENTIALS_DIRECTORY", credentials,
                "SCHUBERT_NK_CONFIG_DIR", "/etc/schubert-nk",
                "SCHUBERT_NK_STARTUP_ADMISSION_FD", "128",
                "SCHUBERT_NK_STARTUP_PROOF_FD", "129");
        var actual = RootServiceLauncher.environment(service, self, 128, 129);
        assertEquals(expected, actual);
        assertEquals(5, actual.size());
        assertThrows(UnsupportedOperationException.class, () -> actual.put("OTHER", "VALUE"));
      } else {
        assertEquals("reject", args[1]);
        assertThrows(
            IOException.class, () -> RootServiceLauncher.environment(service, self, 128, 129));
      }
      System.out.println("ROOTENV_LITERAL_ASSERTIONS_OK");
    }
  }
}

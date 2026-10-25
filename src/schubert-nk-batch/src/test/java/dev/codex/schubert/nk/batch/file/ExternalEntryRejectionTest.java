package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.management.ManagementFactory;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** OPS009/UI251/SS341/342/343; PT-OPS-ENTRYREJECT-001..003, no Unit or native authority. */
final class ExternalEntryRejectionTest {
  @TempDir Path emptyWorkingDirectory;

  @Test
  void rootArgumentErrorsExitSeventyBeforeAnyAdmission() throws Exception {
    for (var args :
        List.of(List.<String>of(), List.of("OTHER"), List.of("api"), List.of("WEB", "extra")))
      observe(RootServiceLauncher.class, args, 70);
  }

  @Test
  void evenExactApiWebArgumentsCannotAcquireOsOwnershipFromAnOrdinaryJvm() throws Exception {
    for (String role : List.of("API", "WEB")) observe(RootServiceLauncher.class, List.of(role), 30);
  }

  @Test
  void malformedMorningAndCleanupArgumentsNeverSelectBusinessWork() throws Exception {
    observe(MorningProcessMain.class, List.of("--unknown"), 70);
    observe(MorningProcessMain.class, List.of("--resume", "not-a-uuid"), 70);
    observe(CleanupProcessMain.class, List.of("--unexpected"), 70);
    observe(CleanupProcessMain.class, List.of("--expiry", "extra"), 70);
  }

  private void observe(Class<?> entry, List<String> args, int expected) throws Exception {
    var command = new ArrayList<String>();
    command.add(Path.of(System.getProperty("java.home"), "bin", "java").toString());
    var agents =
        ManagementFactory.getRuntimeMXBean().getInputArguments().stream()
            .filter(a -> a.startsWith("-javaagent:") && a.contains("org.jacoco.agent"))
            .toList();
    assertEquals(1, agents.size());
    assertFalse(agents.getFirst().startsWith("-javaagent:/opt/pgpt-tools-pg390/"));
    command.addAll(agents);
    command.addAll(
        List.of(
            "--enable-native-access=ALL-UNNAMED",
            "-cp",
            System.getProperty("java.class.path"),
            entry.getName()));
    command.addAll(args);
    var builder =
        new ProcessBuilder(command)
            .directory(emptyWorkingDirectory.toFile())
            .redirectErrorStream(true);
    builder.environment().clear();
    var child = builder.start();
    try {
      assertTrue(child.waitFor(30, TimeUnit.SECONDS), "owned rejection fixture must terminate");
      String output = new String(child.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
      assertEquals(expected, child.exitValue(), output);
      assertEquals("", output, "rejected startup must not print raw diagnostics");
    } finally {
      if (child.isAlive()) {
        child.destroy();
        assertTrue(child.waitFor(10, TimeUnit.SECONDS), "owned fixture normal TERM only");
      }
    }
    try (var files = Files.list(emptyWorkingDirectory)) {
      assertEquals(0, files.count(), "no relative configuration or work artifact is created");
    }
  }
}

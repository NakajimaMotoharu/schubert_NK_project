package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.List;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** Executable browser-script unit double; PG201/UI222,223/SS313/016005/PT-SCR025-A..H. */
class ScenarioSearchScriptTest {
  private static String execute(List<String> arguments, Path output)
      throws IOException, InterruptedException {
    var process =
        new ProcessBuilder(arguments)
            .redirectErrorStream(true)
            .redirectOutput(output.toFile())
            .start();
    try {
      assertTrue(process.waitFor(30, TimeUnit.SECONDS), "Node PT timed out");
      String text = Files.readString(output, StandardCharsets.UTF_8);
      assertEquals(0, process.exitValue(), text);
      return text;
    } finally {
      process.descendants().forEach(handle -> handle.destroyForcibly());
      if (process.isAlive()) process.destroyForcibly();
    }
  }

  @Test
  void search025BrowserInputScript()
      throws IOException, InterruptedException, NoSuchAlgorithmException {
    String node = System.getProperty("nk.pt.node", "node");
    Path directory = Path.of("target/pt-search-script");
    Files.createDirectories(directory);
    String version = execute(List.of(node, "--version"), directory.resolve("version.txt")).strip();
    assertEquals("v24.19.0", version);
    Path script = Path.of("src/main/resources/static/js/search-speaker-submit.js").toAbsolutePath();
    Path test = Path.of("src/test/javascript/search-speaker-submit.test.cjs").toAbsolutePath();
    assertTrue(Files.isRegularFile(script));
    assertTrue(Files.isRegularFile(test));
    execute(List.of(node, "--check", script.toString()), directory.resolve("syntax.txt"));
    String tap =
        execute(
            List.of(
                node,
                "--test",
                "--experimental-test-coverage",
                "--test-reporter=tap",
                "--test-coverage-lines=100",
                "--test-coverage-functions=100",
                "--test-coverage-branches=100",
                "--test-coverage-include=" + script,
                test.toString()),
            directory.resolve("node.tap"));
    for (String line :
        List.of("# tests 8", "# pass 8", "# fail 0", "# cancelled 0", "# skipped 0", "# todo 0"))
      assertTrue(tap.lines().anyMatch(line::equals), line);
    assertTrue(
        tap.lines()
            .anyMatch(
                line ->
                    line.startsWith("# ")
                        && line.contains("search-speaker-submit.js")
                        && line.contains("|")),
        "Production script must be present in coverage, not an empty include");
    String hash =
        HexFormat.of()
            .formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(script)));
    Files.writeString(
        directory.resolve("PT-SCR025-node.json"),
        "{\n  \"testId\": \"PT-SCR-025\",\n  \"nodeVersion\": \"v24.19.0\",\n"
            + "  \"subcases\": 8,\n  \"failed\": 0,\n  \"skipped\": 0,\n  \"todo\": 0,\n"
            + "  \"syntaxExit\": 0,\n  \"testExit\": 0,\n"
            + "  \"lineCoverage\": 100,\n  \"functionCoverage\": 100,\n  \"branchCoverage\": 100,\n"
            + "  \"productionFiles\": 1,\n  \"scriptSha256\": \""
            + hash
            + "\",\n"
            + "  \"browserDom\": \"deterministic-event-double\",\n  \"actualNkGate\": false\n}\n",
        StandardCharsets.UTF_8);
  }
}

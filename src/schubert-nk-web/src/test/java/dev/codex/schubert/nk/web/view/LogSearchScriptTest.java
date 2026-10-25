package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.List;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** PG217/SCR014/UI222,225/SS313,352/016021/PT-SCR092-A..H. */
class LogSearchScriptTest {
  private static String execute(List<String> args, Path output) throws Exception {
    var process =
        new ProcessBuilder(args).redirectErrorStream(true).redirectOutput(output.toFile()).start();
    try {
      assertTrue(process.waitFor(30, TimeUnit.SECONDS), "Log Node PT timed out");
      String result = Files.readString(output, StandardCharsets.UTF_8);
      assertEquals(0, process.exitValue(), result);
      return result;
    } finally {
      process.descendants().forEach(child -> child.destroyForcibly());
      if (process.isAlive()) process.destroyForcibly();
    }
  }

  @Test
  void log092BrowserInputScript() throws Exception {
    String node = System.getProperty("nk.pt.node", "node");
    Path output = Path.of("target/pt-log-script");
    Files.createDirectories(output);
    assertEquals(
        "v24.19.0", execute(List.of(node, "--version"), output.resolve("version.txt")).strip());
    Path script = Path.of("src/main/resources/static/js/log-search-validation.js").toAbsolutePath();
    Path test = Path.of("src/test/javascript/log-search-validation.test.cjs").toAbsolutePath();
    assertTrue(Files.isRegularFile(script));
    assertTrue(Files.isRegularFile(test));
    execute(List.of(node, "--check", script.toString()), output.resolve("syntax.txt"));
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
            output.resolve("node.tap"));
    for (String expected :
        List.of("# tests 8", "# pass 8", "# fail 0", "# cancelled 0", "# skipped 0", "# todo 0"))
      assertTrue(tap.lines().anyMatch(expected::equals), expected);
    assertTrue(
        tap.lines()
            .anyMatch(
                line ->
                    line.startsWith("# ")
                        && line.contains("log-search-validation.js")
                        && line.contains("|")));
    String hash =
        HexFormat.of()
            .formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(script)));
    Files.writeString(
        output.resolve("PT-SCR092-node.json"),
        "{\n  \"testId\": \"PT-SCR-092\",\n  \"nodeVersion\": \"v24.19.0\",\n"
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

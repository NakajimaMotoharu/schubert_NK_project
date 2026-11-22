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

/** PG-D352/SCR018/UI224/SS313,352/016067/PT-QST-JS001-A..H. */
class QuestionInputScriptTest {
  private static String execute(List<String> args, Path output)
      throws IOException, InterruptedException {
    var process =
        new ProcessBuilder(args).redirectErrorStream(true).redirectOutput(output.toFile()).start();
    try {
      assertTrue(process.waitFor(30, TimeUnit.SECONDS), "Question Node PT timed out");
      String result = Files.readString(output, StandardCharsets.UTF_8);
      assertEquals(0, process.exitValue(), result);
      return result;
    } finally {
      process.descendants().forEach(child -> child.destroyForcibly());
      if (process.isAlive()) process.destroyForcibly();
    }
  }

  @Test
  void questionInput001BrowserInputScript()
      throws IOException, InterruptedException, NoSuchAlgorithmException {
    String node = System.getProperty("nk.pt.node", "node");
    Path output = Path.of("target/pt-question-script");
    Files.createDirectories(output);
    assertEquals(
        "v24.19.0", execute(List.of(node, "--version"), output.resolve("version.txt")).strip());
    Path script =
        Path.of("src/main/resources/static/js/question-input-validation.js").toAbsolutePath();
    Path test = Path.of("src/test/javascript/question-input-validation.test.cjs").toAbsolutePath();
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
                        && line.contains("question-input-validation.js")
                        && line.contains("|")),
        "Production script must be present in coverage");
    String hash =
        HexFormat.of()
            .formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(script)));
    Files.writeString(
        output.resolve("PT-QST-JS001-node.json"),
        "{\n  \"testId\": \"PT-QST-JS001\",\n  \"nodeVersion\": \"v24.19.0\",\n  \"subcases\": 8,\n  \"failed\": 0,\n  \"skipped\": 0,\n  \"todo\": 0,\n  \"syntaxExit\": 0,\n  \"testExit\": 0,\n  \"lineCoverage\": 100,\n  \"functionCoverage\": 100,\n  \"branchCoverage\": 100,\n  \"productionFiles\": 1,\n  \"scriptSha256\": \""
            + hash
            + "\",\n  \"browserDom\": \"deterministic-event-double\",\n  \"actualNkGate\": false\n}\n",
        StandardCharsets.UTF_8);
  }
}

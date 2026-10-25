package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** UI222§8/SS313314352/BUG1222/YKT988/PT-WEB-OPSJS2646; no native or browser authority. */
class OperationPostScriptTest {
  private static String execute(List<String> arguments, Path output) throws Exception {
    var process =
        new ProcessBuilder(arguments)
            .redirectErrorStream(true)
            .redirectOutput(output.toFile())
            .start();
    try {
      assertTrue(process.waitFor(30, TimeUnit.SECONDS), "operation script timed out");
      String result = Files.readString(output, StandardCharsets.UTF_8);
      assertEquals(0, process.exitValue(), result);
      return result;
    } finally {
      process.descendants().forEach(child -> child.destroyForcibly());
      if (process.isAlive()) process.destroyForcibly();
    }
  }

  @Test
  void operation2646001IndependentEventContractsAndEveryScriptCounter() throws Exception {
    String node = System.getProperty("nk.pt.node", "node");
    Path output = Path.of("target/pt-operation-script");
    Files.createDirectories(output);
    assertEquals(
        "v24.19.0", execute(List.of(node, "--version"), output.resolve("version.txt")).strip());
    Path script = Path.of("src/main/resources/static/js/operation-post-submit.js").toAbsolutePath();
    Path test = Path.of("src/test/javascript/operation-post-submit.test.cjs").toAbsolutePath();
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
        List.of("# tests 6", "# pass 6", "# fail 0", "# cancelled 0", "# skipped 0", "# todo 0"))
      assertTrue(tap.lines().anyMatch(expected::equals), expected);
    assertTrue(
        tap.lines()
            .anyMatch(
                line ->
                    line.startsWith("# ")
                        && line.contains("operation-post-submit.js")
                        && line.contains("|")));
  }

  @Test
  void operation2646002OnlyApprovedUpdateTemplatesConnectExternalScript() throws Exception {
    for (String name :
        List.of(
            "admin/user-new", "admin/user-detail", "notifications/detail", "questions/detail")) {
      String template = Files.readString(Path.of("src/main/resources/templates/" + name + ".html"));
      assertEquals(1, template.split("data-operation-submit", -1).length - 1, name);
      assertEquals(1, template.split("/js/operation-post-submit.js", -1).length - 1, name);
      assertTrue(template.contains("name=\"operation_token\""), name);
      assertTrue(template.contains("method=\"post\""), name);
      assertTrue(
          template.contains("<script src=\"/js/operation-post-submit.js\" defer></script>"), name);
      assertFalse(template.contains("onsubmit="), name);
    }
    for (String name : List.of("questions/new", "fragments/layout", "admin/user-list")) {
      String template = Files.readString(Path.of("src/main/resources/templates/" + name + ".html"));
      assertFalse(template.contains("data-operation-submit"), name);
      assertFalse(template.contains("/js/operation-post-submit.js"), name);
    }
  }
}

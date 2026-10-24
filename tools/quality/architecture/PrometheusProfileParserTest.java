package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.List;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-OPS-001 / SS351 / PT1804: fixed offline product parser, no daemon or scrape. */
final class PrometheusProfileParserTest {
  private static final Path ROOT = Path.of("/home/mini/codex/project1/work/pgpt-foundation");
  private static final Path TOOL =
      Path.of("/home/mini/codex/project1/work/toolchain/promtool-3.13.5-linux-amd64/promtool");
  private static final String DEBUG_SHA =
      "df964a0793af23bc61d3531fa516d0dd4787a5a5595cda64e96d3f0e01f43f6a";
  private static final String STANDARD_SHA =
      "52e6254d2eb82f4f3072f8c5a96a2b21b2fee350480a8ebe3f4018f53d8716e8";
  @TempDir Path owned;

  @Test
  void promparse001ActualDebugAccepted() throws Exception {
    check(profile("debug", DEBUG_SHA), true);
  }

  @Test
  void promparse002ActualStandardAccepted() throws Exception {
    check(profile("standard", STANDARD_SHA), true);
  }

  @Test
  void promparse003MalformedRejected() throws Exception {
    check("{", false);
  }

  @Test
  void promparse004UnknownFieldRejected() throws Exception {
    check("{\"unknown_nk_field\": true}", false);
  }

  @Test
  void promparse005InvalidDurationRejected() throws Exception {
    check("{\"global\":{\"scrape_interval\":\"NOT_DURATION\"}}", false);
  }

  @Test
  void promparse006DuplicateJobRejected() throws Exception {
    check(
        "{\"scrape_configs\":[{\"job_name\":\"duplicate\"},{\"job_name\":\"duplicate\"}]}", false);
  }

  @Test
  void promparse007TimeoutExceedsIntervalRejected() throws Exception {
    check("{\"global\":{\"scrape_interval\":\"1s\",\"scrape_timeout\":\"2s\"}}", false);
  }

  @Test
  void promparse008WrongScrapeTypeRejected() throws Exception {
    check("{\"scrape_configs\":\"not_a_list\"}", false);
  }

  private String profile(String name, String expected) throws Exception {
    byte[] bytes =
        Files.readAllBytes(
            ROOT.resolve("src/deployment/monitoring/prometheus/" + name + ".yml.template"));
    assertEquals(expected, sha(bytes));
    return new String(bytes, StandardCharsets.UTF_8);
  }

  private void check(String input, boolean accepted) throws Exception {
    assertEquals(
        "4e84296dc89ef03d856674d76d387f5ccc54a698136c2f0dc30ceef2286908ff",
        sha(Files.readAllBytes(TOOL)));
    Path config = owned.resolve("public-config.json");
    Files.writeString(config, input, StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW);
    Path log = owned.resolve("parser.log");
    List<String> command =
        List.of(
            TOOL.toString(), "check", "config", "--lint=all", "--lint-fatal", config.toString());
    ProcessBuilder builder =
        new ProcessBuilder(command)
            .directory(owned.toFile())
            .redirectErrorStream(true)
            .redirectOutput(log.toFile());
    builder.environment().clear();
    builder.environment().put("PATH", "/usr/bin:/bin");
    builder.environment().put("LANG", "C.UTF-8");
    Process process = builder.start();
    boolean ended = process.waitFor(30, TimeUnit.SECONDS);
    if (!ended) {
      process.destroyForcibly();
      assertTrue(
          process.waitFor(10, TimeUnit.SECONDS), "only this test's parser child must terminate");
    }
    assertTrue(ended, "timeout is never an accepted rejection");
    int exit = process.exitValue();
    byte[] output = Files.readAllBytes(log);
    assertEquals(input, Files.readString(config));
    assertFalse(output.length == 0, "product parser must emit an actual diagnostic");
    if (accepted) assertEquals(0, exit);
    else
      assertTrue(
          exit == 1 || exit == 3, "only documented config/lint rejection, not crash or signal");
    System.out.println(
        "PROMPARSE\t"
            + sha(input.getBytes(StandardCharsets.UTF_8))
            + "\t"
            + exit
            + "\t"
            + sha(output));
  }

  private static String sha(byte[] bytes) throws Exception {
    return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
  }
}

package dev.codex.schubert.nk.batch.bootstrap;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.regex.Pattern;
import org.junit.jupiter.api.Test;

/** PG239/PT-BAT-283; independent Batch process runtime dependency, not test classpath. */
final class BatchRuntimeDependencyTest {
  private static final Pattern DEPENDENCY =
      Pattern.compile("<dependency>(.*?)</dependency>", Pattern.DOTALL);

  @Test
  void bat283RuntimePostgresDriverAndScopeCanaries() throws Exception {
    String pom =
        Files.readString(
            Path.of(System.getProperty("nk.pt.repository"), "src/schubert-nk-batch/pom.xml"));
    String block = postgresBlock(pom);
    assertRuntimeDriver(pom);
    for (String scope : new String[] {"test", "compile", "system"}) {
      assertThrows(
          AssertionError.class,
          () ->
              assertRuntimeDriver(
                  pom.replace(
                      block,
                      block.replace("<scope>runtime</scope>", "<scope>" + scope + "</scope>"))));
    }
    assertThrows(
        AssertionError.class,
        () -> assertRuntimeDriver(pom.replace(block, block.replace("<scope>runtime</scope>", ""))));
    assertThrows(
        AssertionError.class,
        () -> assertRuntimeDriver(pom.replace(block, block.replace("42.7.13", "42.7.12"))));
    assertThrows(
        AssertionError.class, () -> assertRuntimeDriver(pom.replace(block, block + block)));
    assertThrows(AssertionError.class, () -> assertRuntimeDriver(pom.replace(block, "")));
  }

  private static String postgresBlock(String pom) {
    var blocks = new ArrayList<String>();
    var matcher = DEPENDENCY.matcher(pom);
    while (matcher.find()) {
      String block = matcher.group();
      if (block.contains("<groupId>org.postgresql</groupId>")
          && block.contains("<artifactId>postgresql</artifactId>")) blocks.add(block);
    }
    assertEquals(1, blocks.size(), "exactly one Batch JDBC declaration");
    return blocks.getFirst();
  }

  private static void assertRuntimeDriver(String pom) {
    String block = postgresBlock(pom);
    assertTrue(block.contains("<version>42.7.13</version>"), "SS-approved JDBC version");
    assertTrue(block.contains("<scope>runtime</scope>"), "Batch production runtime driver");
  }
}

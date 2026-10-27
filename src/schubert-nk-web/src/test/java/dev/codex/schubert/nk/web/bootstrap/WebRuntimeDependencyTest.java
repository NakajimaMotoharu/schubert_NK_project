package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.regex.Pattern;
import org.junit.jupiter.api.Test;

/** PG238/PT-SCR-132; production POM runtime dependency, not the JUnit test classpath. */
final class WebRuntimeDependencyTest {
  private static final String RUNTIME_SCOPE_XML = "<scope>runtime</scope>";
  private static final Pattern DEPENDENCY =
      Pattern.compile("<dependency>(.*?)</dependency>", Pattern.DOTALL);

  @Test
  void scr132RuntimePostgresDriverAndScopeCanaries() throws Exception {
    String pom =
        Files.readString(
            Path.of(System.getProperty("nk.pt.repository"), "src/schubert-nk-web/pom.xml"));
    String block = postgresBlock(pom);
    assertRuntimeDriver(pom);
    assertThrows(
        AssertionError.class,
        () ->
            assertRuntimeDriver(
                pom.replace(block, block.replace(RUNTIME_SCOPE_XML, "<scope>test</scope>"))));
    for (String scope : new String[] {"compile", "system"}) {
      assertThrows(
          AssertionError.class,
          () ->
              assertRuntimeDriver(
                  pom.replace(
                      block, block.replace(RUNTIME_SCOPE_XML, "<scope>" + scope + "</scope>"))));
    }
    assertThrows(
        AssertionError.class,
        () -> assertRuntimeDriver(pom.replace(block, block.replace(RUNTIME_SCOPE_XML, ""))));
    assertThrows(
        AssertionError.class,
        () -> assertRuntimeDriver(pom.replace(block, block.replace("42.7.13", "42.7.12"))));
    assertThrows(
        AssertionError.class, () -> assertRuntimeDriver(pom.replace(block, block + block)));
  }

  private static String postgresBlock(String pom) {
    var blocks = new ArrayList<String>();
    var matcher = DEPENDENCY.matcher(pom);
    while (matcher.find()) {
      String block = matcher.group();
      if (block.contains("<groupId>org.postgresql</groupId>")
          && block.contains("<artifactId>postgresql</artifactId>")) blocks.add(block);
    }
    assertEquals(1, blocks.size(), "exactly one Web JDBC declaration");
    return blocks.getFirst();
  }

  private static void assertRuntimeDriver(String pom) {
    String block = postgresBlock(pom);
    assertTrue(block.contains("<version>42.7.13</version>"), "SS-approved JDBC version");
    assertTrue(block.contains(RUNTIME_SCOPE_XML), "Web production runtime driver");
  }
}

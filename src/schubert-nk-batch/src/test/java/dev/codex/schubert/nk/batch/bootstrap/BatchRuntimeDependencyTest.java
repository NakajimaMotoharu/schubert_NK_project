package dev.codex.schubert.nk.batch.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.regex.Pattern;
import org.junit.jupiter.api.Test;

/** PG239/PT-BAT-283; independent Batch process runtime dependency, not test classpath. */
final class BatchRuntimeDependencyTest {
  private static final String DEPENDENCY_END_TAG = "</dependency>";
  private static final String COMPILE_SCOPE_NAME = "compile";
  private static final Pattern DEPENDENCY =
      Pattern.compile("<dependency>(.*?)</dependency>", Pattern.DOTALL);

  @Test
  void bat283RuntimePostgresDriverAndScopeCanaries() throws Exception {
    String pom =
        Files.readString(
            Path.of(System.getProperty("nk.pt.repository"), "src/schubert-nk-batch/pom.xml"));
    String block = postgresBlock(pom);
    assertRuntimeDriver(pom);
    for (String scope : new String[] {"test", COMPILE_SCOPE_NAME, "system"}) {
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
    // SS311/SSC088 and BUG267/YKT201: independent, closed root-startup dependency oracle.
    assertStartupDependencies(pom);
    assertThrows(
        AssertionError.class,
        () ->
            assertStartupDependencies(
                pom.replace(
                    "<dependencies>",
                    "<dependencies><dependency><groupId>unknown</groupId><artifactId>unknown</artifactId><version>1</version></dependency>")));
    for (String forbidden :
        new String[] {"schubert-nk-api", "schubert-nk-web", "schubert-nk-protocol"}) {
      assertThrows(
          AssertionError.class,
          () ->
              assertStartupDependencies(
                  pom.replace(
                      "<dependencies>",
                      "<dependencies><dependency><groupId>dev.codex.schubert</groupId><artifactId>"
                          + forbidden
                          + "</artifactId><version>0.1.0-SNAPSHOT</version></dependency>")));
    }
    for (String[] dependency :
        new String[][] {
          {"dev.codex.schubert", "schubert-nk-bootstrap", COMPILE_SCOPE_NAME},
          {"org.flywaydb", "flyway-core", COMPILE_SCOPE_NAME},
          {"org.flywaydb", "flyway-database-postgresql", "runtime"}
        }) {
      String declared = dependencyBlock(pom, dependency[0], dependency[1]);
      assertThrows(
          AssertionError.class, () -> assertStartupDependencies(pom.replace(declared, "")));
      assertThrows(
          AssertionError.class,
          () -> assertStartupDependencies(pom.replace(declared, declared + declared)));
      String wrong =
          declared.contains("<scope>runtime</scope>")
              ? declared.replace("<scope>runtime</scope>", "<scope>test</scope>")
              : declared.replace(DEPENDENCY_END_TAG, "<scope>test</scope></dependency>");
      assertThrows(
          AssertionError.class, () -> assertStartupDependencies(pom.replace(declared, wrong)));
      if (dependency[2].equals("runtime")) {
        assertThrows(
            AssertionError.class,
            () ->
                assertStartupDependencies(
                    pom.replace(
                        declared,
                        declared.replace("<scope>runtime</scope>", "<scope>compile</scope>"))));
      }
    }
  }

  private static void assertStartupDependencies(String pom) {
    assertBootstrapTestFixtures(pom);
    assertMonitoringDependencies(pom);
    var direct = new java.util.HashSet<String>();
    var blocks = DEPENDENCY.matcher(pom);
    while (blocks.find()) {
      String block = blocks.group();
      if (!block.contains("<scope>test</scope>")) {
        var group = Pattern.compile("<groupId>([^<]+)</groupId>").matcher(block);
        var artifact = Pattern.compile("<artifactId>([^<]+)</artifactId>").matcher(block);
        assertTrue(group.find());
        assertTrue(artifact.find());
        direct.add(group.group(1) + ":" + artifact.group(1));
      }
    }
    assertEquals(
        java.util.Set.of(
            "dev.codex.schubert:schubert-nk-storage",
            "dev.codex.schubert:schubert-nk-bootstrap",
            "org.flywaydb:flyway-core",
            "org.flywaydb:flyway-database-postgresql",
            "org.postgresql:postgresql",
            "org.apache.artemis:artemis-jakarta-client",
            "io.micrometer:micrometer-core",
            "io.micrometer:micrometer-registry-prometheus",
            "org.jspecify:jspecify",
            "com.github.spotbugs:spotbugs-annotations"),
        direct);
    for (String artifact : new String[] {"schubert-nk-bootstrap", "flyway-core"}) {
      String declared =
          dependencyBlock(
              pom,
              artifact.equals("schubert-nk-bootstrap") ? "dev.codex.schubert" : "org.flywaydb",
              artifact);
      assertFalse(declared.contains("<scope>"), "SS311 default compile dependency");
      assertFalse(declared.contains("<type>"), "fixed startup uses the main library jar");
    }
    String driver = dependencyBlock(pom, "org.flywaydb", "flyway-database-postgresql");
    assertTrue(driver.contains("<scope>runtime</scope>"), "root Flyway PG adapter runtime");
    for (String forbidden :
        new String[] {"schubert-nk-api", "schubert-nk-web", "schubert-nk-protocol"}) {
      assertFalse(pom.contains("<artifactId>" + forbidden + "</artifactId>"));
      assertThrows(
          AssertionError.class, () -> dependencyBlock(pom, "dev.codex.schubert", forbidden));
    }
  }

  private static String dependencyBlock(String pom, String group, String artifact) {
    var found = new ArrayList<String>();
    var matcher = DEPENDENCY.matcher(pom);
    while (matcher.find()) {
      String value = matcher.group();
      if (value.contains("<groupId>" + group + "</groupId>")
          && value.contains("<artifactId>" + artifact + "</artifactId>")
          && !value.contains("<scope>test</scope>")) found.add(value);
    }
    assertEquals(1, found.size(), "one fixed root startup declaration");
    return found.getFirst();
  }

  /** PT-BAT-283B/BUG1463: an independent test fixture is not a second runtime startup jar. */
  @Test
  void bat283bBootstrapFixtureCannotMaskWrongRuntimeScopeOrDuplicate() {
    String main =
        "<dependency><groupId>dev.codex.schubert</groupId><artifactId>schubert-nk-bootstrap</artifactId><version>${project.version}</version></dependency>";
    String fixture =
        "<dependency><groupId>dev.codex.schubert</groupId><artifactId>schubert-nk-bootstrap</artifactId><version>${project.version}</version><type>test-jar</type><scope>test</scope></dependency>";
    assertEquals(
        main, dependencyBlock(main + fixture, "dev.codex.schubert", "schubert-nk-bootstrap"));
    assertBootstrapTestFixtures(main + fixture);
    assertBootstrapTestFixtures(main);
    assertThrows(
        AssertionError.class,
        () -> dependencyBlock(fixture, "dev.codex.schubert", "schubert-nk-bootstrap"));
    assertThrows(
        AssertionError.class,
        () ->
            dependencyBlock(main + main + fixture, "dev.codex.schubert", "schubert-nk-bootstrap"));
    for (String wrong :
        new String[] {
          fixture + fixture,
          fixture.replace("<scope>test</scope>", "<scope>runtime</scope>"),
          fixture.replace("<scope>test</scope>", "<scope>compile</scope>"),
          fixture.replace("<scope>test</scope>", ""),
          fixture.replace("<type>test-jar</type>", "<type>jar</type>"),
          fixture.replace("<type>test-jar</type>", ""),
          fixture.replace("${project.version}", "0.0.0-foreign"),
          fixture.replace(DEPENDENCY_END_TAG, "<classifier>foreign</classifier></dependency>")
        }) {
      assertThrows(
          AssertionError.class,
          () -> {
            assertEquals(
                main, dependencyBlock(main + wrong, "dev.codex.schubert", "schubert-nk-bootstrap"));
            assertBootstrapTestFixtures(main + wrong);
          });
    }
  }

  private static void assertBootstrapTestFixtures(String pom) {
    int fixtures = 0;
    var matcher = DEPENDENCY.matcher(pom);
    while (matcher.find()) {
      String block = matcher.group();
      if (block.contains("<groupId>dev.codex.schubert</groupId>")
          && block.contains("<artifactId>schubert-nk-bootstrap</artifactId>")
          && block.contains("<scope>test</scope>")) {
        fixtures++;
        assertTrue(block.contains("<type>test-jar</type>"), "only the explicit test fixture jar");
        assertTrue(
            block.contains("<version>${project.version}</version>"),
            "same project fixture version");
        assertFalse(block.contains("<classifier>"), "no alternate fixture classifier");
      }
    }
    assertTrue(fixtures <= 1, "test-only fixture declaration cannot be duplicated");
  }

  /** PT-BAT-283C/BUG1970: SS351 and PG-D615 SDKs, not an arbitrary dependency whitelist. */
  @Test
  void bat283cApprovedMonitoringSdkCoordinatesRequireVersionCompileAndMainJar() {
    String core =
        "<dependency><groupId>io.micrometer</groupId><artifactId>micrometer-core</artifactId><version>1.17.1</version></dependency>";
    String prometheus =
        "<dependency><groupId>io.micrometer</groupId><artifactId>micrometer-registry-prometheus</artifactId><version>1.17.1</version></dependency>";
    String fixture = core + prometheus;
    assertMonitoringDependencies(fixture);
    assertMonitoringDependencies(
        fixture.replace(DEPENDENCY_END_TAG, "<scope>compile</scope><type>jar</type></dependency>"));
    for (String declared : new String[] {core, prometheus}) {
      assertThrows(
          AssertionError.class, () -> assertMonitoringDependencies(fixture.replace(declared, "")));
      assertThrows(
          AssertionError.class,
          () -> assertMonitoringDependencies(fixture.replace(declared, declared + declared)));
      for (String scope : new String[] {"", "test", "runtime", "provided", "system"}) {
        String wrong =
            declared.replace(DEPENDENCY_END_TAG, "<scope>" + scope + "</scope></dependency>");
        assertThrows(
            AssertionError.class,
            () -> assertMonitoringDependencies(fixture.replace(declared, wrong)));
      }
      for (String wrong :
          new String[] {
            declared.replace("1.17.1", "1.17.0"),
            declared.replace("io.micrometer", "foreign.group"),
            declared.replace(DEPENDENCY_END_TAG, "<type>pom</type></dependency>"),
            declared.replace(DEPENDENCY_END_TAG, "<type></type></dependency>"),
            declared.replace(DEPENDENCY_END_TAG, "<classifier>foreign</classifier></dependency>"),
            declared.replace(
                DEPENDENCY_END_TAG, "<scope>compile</scope><scope>compile</scope></dependency>"),
            declared.replace(DEPENDENCY_END_TAG, "<type>jar</type><type>jar</type></dependency>")
          }) {
        assertThrows(
            AssertionError.class,
            () -> assertMonitoringDependencies(fixture.replace(declared, wrong)));
      }
    }
    assertThrows(NullPointerException.class, () -> assertMonitoringDependencies(null));
  }

  private static void assertMonitoringDependencies(String pom) {
    for (String artifact : new String[] {"micrometer-core", "micrometer-registry-prometheus"}) {
      String declaration = dependencyBlock(pom, "io.micrometer", artifact);
      assertTrue(declaration.contains("<version>1.17.1</version>"), "approved monitoring SDK");
      var scope = Pattern.compile("<scope>([^<]*)</scope>").matcher(declaration);
      if (scope.find()) {
        assertEquals(COMPILE_SCOPE_NAME, scope.group(1));
        assertFalse(scope.find(), "one compile scope");
      }
      var type = Pattern.compile("<type>([^<]*)</type>").matcher(declaration);
      if (type.find()) {
        assertEquals("jar", type.group(1));
        assertFalse(type.find(), "one main jar type");
      }
      assertFalse(declaration.contains("<classifier>"), "monitoring SDK main jar");
    }
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

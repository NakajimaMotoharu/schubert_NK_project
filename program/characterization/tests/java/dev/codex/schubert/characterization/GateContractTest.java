package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.InputStream;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import org.junit.jupiter.api.Test;

class GateContractTest {
  private static final ObjectMapper JSON = new ObjectMapper();

  @Test
  void catalogHasExactlyTwentyFourUniqueCasesAndOnlyN01IsNkOnly() throws Exception {
    JsonNode catalog = resource("cases/catalog.json");
    List<String> ids = new ArrayList<>();
    List<String> nkOnly = new ArrayList<>();
    for (JsonNode item : catalog.path("cases")) {
      ids.add(item.path("id").asText());
      if ("NK_ONLY".equals(item.path("current").asText())) nkOnly.add(item.path("id").asText());
      assertEquals("RUN", item.path("nk").asText());
    }
    assertEquals(24, ids.size());
    assertEquals(24, new HashSet<>(ids).size());
    assertEquals(List.of("CHR-N01"), nkOnly);
  }

  @Test
  void differenceAllowlistIsCompleteUniqueAndNarrow() throws Exception {
    JsonNode dif = resource("cases/dif-allowlist.json");
    Set<String> ids = new HashSet<>();
    for (JsonNode item : dif.path("differences")) {
      String id = item.path("id").asText();
      assertTrue(ids.add(id), "duplicate " + id);
      assertFalse(item.path("field").asText().contains("*"));
      assertFalse(item.path("cases").isEmpty());
    }
    assertEquals(15, ids.size());
    for (int index = 1; index <= 15; index++) {
      assertTrue(ids.contains("DIF-%03d".formatted(index)));
    }
  }

  @Test
  void expectedBaselineContainsAllStaticCounts() throws Exception {
    JsonNode expected = resource("fixtures/expected.json");
    assertEquals(59, expected.path("sourceFileCount").asInt());
    assertEquals(18, expected.path("documentFileCount").asInt());
    assertEquals(59627, expected.path("masterFileCount").asInt());
    assertEquals(99661, expected.path("scenarioEntryCount").asInt());
    assertEquals(20, expected.path("videoCount").asInt());
    assertEquals(129, expected.path("musicCount").asInt());
  }

  @Test
  void caddyFixturePreservesAllForwardedRequestHeaders() {
    String config = CharacterizationEnvironment.renderCaddyConfig(55162, 46962, Path.of("fixture-caddy-data"));
    assertTrue(config.contains("header_up X-Real-IP {remote_host}"));
    assertTrue(config.contains("header_up X-Forwarded-Host {hostport}"));
    assertTrue(config.contains("header_up X-Forwarded-Port {port}"));
    assertTrue(config.contains("header_up X-Forwarded-Proto https"));
  }

  private static JsonNode resource(String name) throws Exception {
    try (InputStream input = GateContractTest.class.getClassLoader().getResourceAsStream(name)) {
      if (input == null) throw new IllegalStateException("resource missing: " + name);
      return JSON.readTree(input);
    }
  }
}

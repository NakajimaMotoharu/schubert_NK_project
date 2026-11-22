import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import org.flywaydb.core.api.output.OperationResultJsonBase;
import org.junit.jupiter.api.Test;
import tools.jackson.databind.json.JsonMapper;

/** PT-OPS-SBOM-024A-C / RD171 SCM-005 / SS352. Public values only. */
final class FlywayJacksonSdkContractTest {
  private final JsonMapper mapper = JsonMapper.builder().build();

  @Test
  void streamingAndBindingUseTheManagedJacksonPatch() {
    assertEquals("3.1.8", mapper.tokenStreamFactory().version().toString());
    assertEquals("3.1.8", mapper.version().toString());
  }

  @Test
  void readsIndependentUtf8Fixture() {
    byte[] body =
        "{\"description\":\"移行テスト\",\"rows\":2,\"complete\":true}".getBytes(StandardCharsets.UTF_8);
    var data = mapper.readTree(body);
    assertEquals("移行テスト", data.get("description").asString());
    assertEquals(2, data.get("rows").asInt());
    assertTrue(data.get("complete").asBoolean());
  }

  @Test
  void serializesFlywayPublicResultFields() {
    var result = new OperationResultJsonBase("{\"ok\":true}", "<p>Fixture</p>");
    var json = mapper.readTree(mapper.writeValueAsString(result));
    assertEquals(2, json.size());
    assertEquals("{\"ok\":true}", json.get("jsonReport").asString());
    assertEquals("<p>Fixture</p>", json.get("htmlReport").asString());
  }
}

package dev.codex.schubert.nk.api.application.scenario;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-SCN-SCRIPTBIND001..002; UI234 IF008 N12 independent IDs, no query or physical file. */
final class ScenarioScriptFileBindingTest {
  private static final String DETAIL_REQUEST = "SCNREQ01";
  private static final String GAME_CODE = "NUKITASHI1";

  @Test
  void scriptBind001DetailIdSurvivesCallerByteMutationAndOtherRequests() {
    for (String[] vector :
        List.of(
            new String[] {"000000000001", "1"},
            new String[] {"000000000030", "30"},
            new String[] {"999999999999", "999999999999"})) {
      byte[] input = vector[0].getBytes(StandardCharsets.US_ASCII);
      var wire = ScenarioRequestFixture.message(DETAIL_REQUEST, input);
      var request = ScenarioRequest.decode(wire);
      Arrays.fill(input, (byte) 0);
      assertSame(wire.header(), request.header());
      assertEquals(Long.parseLong(vector[1]), request.scriptFileId().orElseThrow());
      assertEquals("SCNRSP01", request.responseLayoutId().value());
      var other =
          ScenarioRequest.decode(
              ScenarioRequestFixture.message(
                  DETAIL_REQUEST, "000000000002".getBytes(StandardCharsets.US_ASCII)));
      assertEquals(2, other.scriptFileId().orElseThrow());
      assertEquals(Long.parseLong(vector[1]), request.scriptFileId().orElseThrow());
    }
  }

  @Test
  void scriptBind002EveryOtherKindHasNoDetailId() {
    for (String[] vector :
        List.of(
            new String[] {"GAMREQ01", "GAMRSP01"},
            new String[] {"SPKREQ01", "SPKRSP01"},
            new String[] {"RTEREQ01", "RTERSP01"},
            new String[] {"SCFREQ01", "SCFRSP01"},
            new String[] {"SRCREQ01", "SRCRSP01"})) {
      byte[] input =
          switch (vector[0]) {
            case "GAMREQ01" -> new byte[0];
            case "SPKREQ01" -> ScenarioRequestFixture.spaces(12);
            case "RTEREQ01" -> GAME_CODE.concat("  ").getBytes(StandardCharsets.US_ASCII);
            case "SCFREQ01" -> GAME_CODE.concat("  01").getBytes(StandardCharsets.US_ASCII);
            case "SRCREQ01" -> ScenarioRequestFixture.search();
            default -> throw new AssertionError("closed literal layout table");
          };
      var request = ScenarioRequest.decode(ScenarioRequestFixture.message(vector[0], input));
      assertTrue(request.scriptFileId().isEmpty());
      assertEquals(vector[1], request.responseLayoutId().value());
    }
  }
}

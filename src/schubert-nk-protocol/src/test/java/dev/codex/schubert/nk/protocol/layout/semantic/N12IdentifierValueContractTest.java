package dev.codex.schubert.nk.protocol.layout.semantic;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.LongFunction;
import org.junit.jupiter.api.Test;

/** PT-PRO-N12VALUE001..003; MSG001..011/UI232233/SS322323354 SSC442; pure typed values. */
final class N12IdentifierValueContractTest {
  private static final long MAXIMUM = 999_999_999_999L;
  private static final String[] NAMES = {
    "AsyncJobId",
    "AudioId",
    "EntryId",
    "LogId",
    "NotificationId",
    "QuestionId",
    "ScriptFileId",
    "SpeakerId",
    "UserId"
  };
  private static final List<LongFunction<? extends ProtocolId>> FACTORIES =
      List.of(
          AsyncJobId::new,
          AudioId::new,
          EntryId::new,
          LogId::new,
          NotificationId::new,
          QuestionId::new,
          ScriptFileId::new,
          SpeakerId::new,
          UserId::new);

  @Test
  void n12Value001IndependentPositiveRangeAndFixedDiagnosticForEveryDeclaredKind() {
    long[] valid = {1, 123, MAXIMUM};
    long[] invalid = {Long.MIN_VALUE, -1, 0, 1_000_000_000_000L, Long.MAX_VALUE};
    assertEquals(9, FACTORIES.size());
    assertEquals(9, NAMES.length);
    for (int i = 0; i < FACTORIES.size(); i++) {
      LongFunction<? extends ProtocolId> factory = FACTORIES.get(i);
      for (long value : valid) {
        assertEquals(value, factory.apply(value).value(), NAMES[i]);
      }
      for (long value : invalid) {
        assertEquals(
            "protocol ID must be between 1 and 999999999999",
            assertThrows(IllegalArgumentException.class, () -> factory.apply(value), NAMES[i])
                .getMessage());
      }
    }
  }

  @Test
  void n12Value002SameKindRecordContractIndependentHashAndLiteralText() {
    for (int i = 0; i < FACTORIES.size(); i++) {
      LongFunction<? extends ProtocolId> factory = FACTORIES.get(i);
      ProtocolId value = factory.apply(1);
      ProtocolId equal = factory.apply(1);
      ProtocolId otherValue = factory.apply(2);
      assertEquals(value, value, NAMES[i]);
      assertEquals(value, equal, NAMES[i]);
      assertEquals(equal, value, NAMES[i]);
      assertNotEquals(value, otherValue, NAMES[i]);
      assertNotEquals(otherValue, value, NAMES[i]);
      assertNotEquals(value, null, NAMES[i]);
      assertNotEquals(value, "unrelated type", NAMES[i]);
      assertEquals(1, value.hashCode(), NAMES[i]);
      assertEquals(123, factory.apply(123).hashCode(), NAMES[i]);
      // Independent signed32(n ^ (n >>> 32)) for literal999999999999, no production call.
      assertEquals(-727380201, factory.apply(MAXIMUM).hashCode(), NAMES[i]);
      assertEquals(NAMES[i] + "[value=1]", value.toString(), NAMES[i]);
      assertEquals(NAMES[i] + "[value=999999999999]", factory.apply(MAXIMUM).toString(), NAMES[i]);
    }
  }

  @Test
  void n12Value003AllKindPairsAndRealHashCollectionKeepEqualNumbersDistinct() {
    Map<ProtocolId, String> values = new HashMap<>();
    for (int i = 0; i < FACTORIES.size(); i++) {
      values.put(FACTORIES.get(i).apply(1), NAMES[i]);
    }
    assertEquals(9, values.size());
    for (int i = 0; i < FACTORIES.size(); i++) {
      assertEquals(NAMES[i], values.get(FACTORIES.get(i).apply(1)));
      for (int j = 0; j < FACTORIES.size(); j++) {
        assertEquals(
            i == j,
            FACTORIES.get(i).apply(1).equals(FACTORIES.get(j).apply(1)),
            NAMES[i] + "/" + NAMES[j]);
      }
    }
  }
}

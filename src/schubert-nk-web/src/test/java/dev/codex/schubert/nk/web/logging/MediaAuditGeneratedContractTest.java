package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.web.logging.WebMediaAudit.Failure;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-MED-AUDIT-RAW001; SS333351354/BUG3176/YKT2645; public closed value only. */
final class MediaAuditGeneratedContractTest {
  @Test
  void raw001ClosedFailureNamesOrdinalsAndDefensiveArrayAreIndependent() {
    String[] expectedNames = {"NONE", "IO", "CLIENT_ABORT", "BUSY"};
    var values = Failure.values();
    assertArrayEquals(expectedNames, Arrays.stream(values).map(Enum::name).toArray(String[]::new));
    assertEquals(4, values.length);
    for (int index = 0; index < expectedNames.length; index++) {
      assertEquals(index, values[index].ordinal());
      assertSame(values[index], Failure.valueOf(expectedNames[index]));
    }
    values[0] = Failure.BUSY;
    assertSame(Failure.NONE, Failure.values()[0]);
    for (String unknown : List.of("", "none", "BUSY ", "UNKNOWN"))
      assertThrows(IllegalArgumentException.class, () -> Failure.valueOf(unknown));
    assertThrows(NullPointerException.class, () -> Failure.valueOf(null));
  }
}

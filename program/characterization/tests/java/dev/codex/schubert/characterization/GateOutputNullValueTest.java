package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.fail;

import java.lang.reflect.Proxy;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

final class GateOutputNullValueTest {
  @Test
  @DisplayName("PT-CHR-OUTPUT-NULL-001 absent destination never reaches the output port")
  void missingDestinationDoesNotInvokeOutputPort() {
    var ioType = GateCli.JsonOutput.class;
    var io =
        ioType.cast(
            Proxy.newProxyInstance(
                ioType.getClassLoader(),
                new Class<?>[] {ioType},
                (_, method, _) -> fail("unexpected output call " + method.getName())));

    var failure =
        assertThrows(IllegalArgumentException.class, () -> GateCli.writeJson(null, "fixture", io));
    assertEquals("output is required", failure.getMessage());
  }
}

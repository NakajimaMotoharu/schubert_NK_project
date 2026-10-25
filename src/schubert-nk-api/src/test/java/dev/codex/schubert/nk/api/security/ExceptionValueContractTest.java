package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import org.junit.jupiter.api.Test;

/** PT-F03-EXC002; SS314/352/BUG1482/YKT1237: enum denials, not authentication attempts. */
final class ExceptionValueContractTest {
  @Test
  void exc002CryptoAndAuthorizationReasonsPreserveClosedContracts() {
    for (var reason : AuthContextCryptoException.Reason.values()) {
      var failure = new AuthContextCryptoException(reason);
      assertSame(reason, failure.reason());
      assertEquals("authentication context cryptography failed", failure.getMessage());
      assertNull(failure.getCause());
    }
    assertThrows(NullPointerException.class, () -> new AuthContextCryptoException(null));
    for (var code : ResultCode.values()) {
      if (code == ResultCode.FORBIDDEN || code == ResultCode.NOT_FOUND) {
        var failure = new AuthorizationException(code);
        assertSame(code, failure.resultCode());
        assertEquals("operation is not available", failure.getMessage());
      } else assertThrows(IllegalArgumentException.class, () -> new AuthorizationException(code));
    }
    assertThrows(NullPointerException.class, () -> new AuthorizationException(null));
  }
}

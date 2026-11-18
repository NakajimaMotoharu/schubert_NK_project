package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-OPS-CREDID-005/006, SS342/343, SSC-456. Only fixed designation strings are used. */
final class ServiceCredentialIdEnumValueContractTest {
  @Test
  void opsCredid005LookupAcceptsOnlyExactPublishedNames() {
    for (String name :
        List.of(
            "DB_API",
            "MQ_API",
            "API_CONTEXT_AES_CURRENT",
            "API_INBOX_RESPONSE_AES_CURRENT",
            "OPERATION_HMAC_CURRENT",
            "DB_WEB",
            "MQ_WEB",
            "WEB_SESSION_AES_CURRENT",
            "WEB_REVOKE_AES_CURRENT",
            "WEB_LOG_AES_CURRENT")) {
      assertEquals(name, ServiceCredentialId.valueOf(name).name());
    }
    for (String invalid : List.of("", "db-api", "DB_API ", "UNKNOWN")) {
      assertThrows(IllegalArgumentException.class, () -> ServiceCredentialId.valueOf(invalid));
    }
    assertThrows(NullPointerException.class, () -> ServiceCredentialId.valueOf(null));
    var invalidService =
        assertThrows(NullPointerException.class, () -> ServiceCredentialId.forService(null));
    assertEquals("service", invalidService.getMessage());
  }

  @Test
  void opsCredid006KindVocabularyIsClosedWithAnIndependentValuesArray() {
    var password = ServiceCredentialId.Kind.PASSWORD;
    var key = ServiceCredentialId.Kind.KEY;
    var expected = new ServiceCredentialId.Kind[] {password, key};
    var returned = ServiceCredentialId.Kind.values();
    assertArrayEquals(expected, returned);
    returned[0] = key;
    assertArrayEquals(expected, ServiceCredentialId.Kind.values());
    assertSame(password, ServiceCredentialId.Kind.valueOf("PASSWORD"));
    assertSame(key, ServiceCredentialId.Kind.valueOf("KEY"));
    for (String invalid : List.of("", "password", "KEY ", "UNKNOWN")) {
      assertThrows(IllegalArgumentException.class, () -> ServiceCredentialId.Kind.valueOf(invalid));
    }
    assertThrows(NullPointerException.class, () -> ServiceCredentialId.Kind.valueOf(null));
  }
}

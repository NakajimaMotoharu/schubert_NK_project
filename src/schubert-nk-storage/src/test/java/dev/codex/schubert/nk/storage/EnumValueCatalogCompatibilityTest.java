package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.ObjectStreamClass;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

/** BUG1478/YKT1237; SS342/343; PT-F03-ENUM-STO001: identifiers only, no credential access. */
final class EnumValueCatalogCompatibilityTest {
  private static final String API_NAME = "API";
  private static final String WEB_NAME = "WEB";
  private static final String PASSWORD_KIND = "PASSWORD";
  private static final String KEY_KIND = "KEY";

  @Test
  void sto001FixedCredentialCatalogKeepsNamesOwnersKindsAndOrdering() {
    assertEquals(
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
            "WEB_LOG_AES_CURRENT"),
        Arrays.stream(ServiceCredentialId.values()).map(Enum::name).toList());
    assertEquals(
        List.of(
            "db-api",
            "mq-api",
            "api-context-aes-current",
            "api-inbox-response-aes-current",
            "operation-hmac-current",
            "db-web",
            "mq-web",
            "web-session-aes-current",
            "web-revoke-aes-current",
            "web-log-aes-current"),
        Arrays.stream(ServiceCredentialId.values()).map(ServiceCredentialId::fileName).toList());
    assertEquals(
        List.of(
            API_NAME, API_NAME, API_NAME, API_NAME, API_NAME, WEB_NAME, WEB_NAME, WEB_NAME,
            WEB_NAME, WEB_NAME),
        Arrays.stream(ServiceCredentialId.values()).map(value -> value.service().name()).toList());
    assertEquals(
        List.of(
            PASSWORD_KIND,
            PASSWORD_KIND,
            KEY_KIND,
            KEY_KIND,
            KEY_KIND,
            PASSWORD_KIND,
            PASSWORD_KIND,
            KEY_KIND,
            KEY_KIND,
            KEY_KIND),
        Arrays.stream(ServiceCredentialId.values()).map(value -> value.kind().name()).toList());
    assertEquals(
        List.of(
            ServiceCredentialId.DB_API,
            ServiceCredentialId.MQ_API,
            ServiceCredentialId.API_CONTEXT_AES_CURRENT,
            ServiceCredentialId.API_INBOX_RESPONSE_AES_CURRENT,
            ServiceCredentialId.OPERATION_HMAC_CURRENT),
        ServiceCredentialId.forService(ServiceConfigFiles.Service.API));
    assertEquals(
        List.of(
            ServiceCredentialId.DB_WEB,
            ServiceCredentialId.MQ_WEB,
            ServiceCredentialId.WEB_SESSION_AES_CURRENT,
            ServiceCredentialId.WEB_REVOKE_AES_CURRENT,
            ServiceCredentialId.WEB_LOG_AES_CURRENT),
        ServiceCredentialId.forService(ServiceConfigFiles.Service.WEB));
    assertThrows(NullPointerException.class, () -> ServiceCredentialId.forService(null));
    var descriptor = ObjectStreamClass.lookup(ServiceCredentialId.class);
    assertEquals(0, descriptor.getFields().length);
    assertEquals(0L, descriptor.getSerialVersionUID());
  }
}

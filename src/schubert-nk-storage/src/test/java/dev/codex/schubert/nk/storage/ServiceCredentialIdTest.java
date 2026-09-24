package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.List;
import java.util.Set;
import org.junit.jupiter.api.Test;

/** PT-OPS-CREDID-001..004; SS342/343 fixed independent literal catalog. */
final class ServiceCredentialIdTest {
  @Test
  void opsCredid001ApiExactlyFiveRequiredIds() {
    assertEquals(
        List.of(
            "db-api",
            "mq-api",
            "api-context-aes-current",
            "api-inbox-response-aes-current",
            "operation-hmac-current"),
        ServiceCredentialId.forService(ServiceConfigFiles.Service.API).stream()
            .map(ServiceCredentialId::fileName)
            .toList());
    assertEquals(
        List.of(
            ServiceCredentialId.Kind.PASSWORD,
            ServiceCredentialId.Kind.PASSWORD,
            ServiceCredentialId.Kind.KEY,
            ServiceCredentialId.Kind.KEY,
            ServiceCredentialId.Kind.KEY),
        ServiceCredentialId.forService(ServiceConfigFiles.Service.API).stream()
            .map(ServiceCredentialId::kind)
            .toList());
  }

  @Test
  void opsCredid002WebExactlyFiveRequiredIds() {
    assertEquals(
        List.of(
            "db-web",
            "mq-web",
            "web-session-aes-current",
            "web-revoke-aes-current",
            "web-log-aes-current"),
        ServiceCredentialId.forService(ServiceConfigFiles.Service.WEB).stream()
            .map(ServiceCredentialId::fileName)
            .toList());
    assertEquals(
        List.of(
            ServiceCredentialId.Kind.PASSWORD,
            ServiceCredentialId.Kind.PASSWORD,
            ServiceCredentialId.Kind.KEY,
            ServiceCredentialId.Kind.KEY,
            ServiceCredentialId.Kind.KEY),
        ServiceCredentialId.forService(ServiceConfigFiles.Service.WEB).stream()
            .map(ServiceCredentialId::kind)
            .toList());
  }

  @Test
  void opsCredid003ServicesAreDisjointAndImmutable() {
    var api = ServiceCredentialId.forService(ServiceConfigFiles.Service.API);
    var web = ServiceCredentialId.forService(ServiceConfigFiles.Service.WEB);
    assertEquals(10, Set.copyOf(List.of(ServiceCredentialId.values())).size());
    for (var id : api) {
      assertEquals(ServiceConfigFiles.Service.API, id.service());
      assertNotEquals(ServiceConfigFiles.Service.WEB, id.service());
    }
    for (var id : web) assertEquals(ServiceConfigFiles.Service.WEB, id.service());
    assertThrows(UnsupportedOperationException.class, () -> api.clear());
    assertThrows(UnsupportedOperationException.class, () -> web.clear());
  }

  @Test
  void opsCredid004NullServiceRejected() {
    assertThrows(NullPointerException.class, () -> ServiceCredentialId.forService(null));
  }
}

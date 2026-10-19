package dev.codex.schubert.nk.api.file;

import static org.junit.jupiter.api.Assertions.assertEquals;

import dev.codex.schubert.nk.bootstrap.SystemManagerObservation;
import java.io.ObjectStreamClass;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

/** BUG1478/YKT1237; SS343; PT-F03-ENUM-BST001: pure identifiers, no file/DBus/native calls. */
final class EnumValueCatalogCompatibilityTest {
  @Test
  void bst001CredentialAndServiceIdentifiersRetainTheirLiteralCatalogs() {
    assertEquals(
        List.of("CONTEXT_CURRENT", "CONTEXT_PREVIOUS", "RESPONSE_CURRENT", "RESPONSE_PREVIOUS"),
        Arrays.stream(AesCredentialFile.values()).map(Enum::name).toList());
    assertEquals(
        List.of(
            "api-context-aes-current",
            "api-context-aes-previous",
            "api-inbox-response-aes-current",
            "api-inbox-response-aes-previous"),
        Arrays.stream(AesCredentialFile.values()).map(AesCredentialFile::fileName).toList());
    assertEquals(
        List.of(false, true, false, true),
        Arrays.stream(AesCredentialFile.values()).map(AesCredentialFile::optional).toList());
    assertEquals(
        List.of("API", "WEB", "MORNING", "CLEANUP", "EXPIRY", "INSPECTOR", "BROKER", "CADDY"),
        Arrays.stream(SystemManagerObservation.Service.values()).map(Enum::name).toList());
    assertEquals(
        List.of(
            "schubert-nk-api.service",
            "schubert-nk-web.service",
            "schubert-nk-morning-controller.service",
            "schubert-nk-cleanup.service",
            "schubert-nk-expiry-cleanup.service",
            "schubert-nk-inbox-inspector.service",
            "artemis.service",
            "caddy.service"),
        Arrays.stream(SystemManagerObservation.Service.values())
            .map(SystemManagerObservation.Service::unit)
            .toList());
    for (Class<?> type : List.of(AesCredentialFile.class, SystemManagerObservation.Service.class)) {
      var descriptor = ObjectStreamClass.lookup(type);
      assertEquals(0, descriptor.getFields().length, type.getName());
      assertEquals(0L, descriptor.getSerialVersionUID(), type.getName());
    }
  }
}

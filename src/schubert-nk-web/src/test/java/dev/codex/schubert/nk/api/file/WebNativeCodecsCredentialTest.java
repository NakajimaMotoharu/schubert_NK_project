package dev.codex.schubert.nk.api.file;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.web.bootstrap.WebNativeCodecs;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-WEB-NKEY003: fixed synthetic LoadCredential files, no secret material. */
final class WebNativeCodecsCredentialTest {
  @TempDir Path temporary;

  @Test
  void webFixedFiveCredentialSetBuildsOnlyWebCodecsAndRejectsCrossService() throws Exception {
    assertThrows(NullPointerException.class, () -> WebNativeCodecs.create(null));
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(temporary)) {
      ServiceCredentialSetTest.install(fixture, ServiceConfigFiles.Service.WEB);
      ServiceCredentialSetTest.install(fixture, ServiceConfigFiles.Service.API);
      var io = new InspectorCredentialLoaderTest.TestIo();
      var reader =
          new ServiceCredentialReader(
              fixture.held,
              new InspectorCredentialLoaderTest.TestSecurity(io),
              ServiceConfigFiles.Service.WEB,
              io);
      ServiceCredentialSet web = ServiceCredentialSet.load(reader, ServiceConfigFiles.Service.WEB);
      try (var owner = WebNativeCodecs.create(web)) {
        assertNotNull(owner.session());
        assertNotNull(owner.log());
        assertNotNull(owner.revoke());
      }
      web.close();
      assertThrows(IllegalStateException.class, () -> WebNativeCodecs.create(web));
      ServiceCredentialSetTest.assertCleared(io);

      var apiIo = new InspectorCredentialLoaderTest.TestIo();
      var apiReader =
          new ServiceCredentialReader(
              fixture.held,
              new InspectorCredentialLoaderTest.TestSecurity(apiIo),
              ServiceConfigFiles.Service.API,
              apiIo);
      try (var api = ServiceCredentialSet.load(apiReader, ServiceConfigFiles.Service.API)) {
        assertThrows(IllegalArgumentException.class, () -> WebNativeCodecs.create(api));
      }
      ServiceCredentialSetTest.assertCleared(apiIo);
    }
  }
}

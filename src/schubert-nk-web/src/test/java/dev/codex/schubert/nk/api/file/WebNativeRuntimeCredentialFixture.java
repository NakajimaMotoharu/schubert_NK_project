package dev.codex.schubert.nk.api.file;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.nio.file.Path;

/** Synthetic five-key fixture only; no native secret, DB, broker or borrowed ownership transfer. */
public final class WebNativeRuntimeCredentialFixture {
  private WebNativeRuntimeCredentialFixture() {}

  @FunctionalInterface
  public interface Action {
    void execute(ServiceCredentialSet keys) throws Exception;
  }

  public static void withKeys(Path root, Action action) throws Exception {
    try (var fixture = new InspectorCredentialLoaderTest.Fixture(root)) {
      ServiceCredentialSetTest.install(fixture, ServiceConfigFiles.Service.WEB);
      var io = new InspectorCredentialLoaderTest.TestIo();
      var reader =
          new ServiceCredentialReader(
              fixture.held,
              new InspectorCredentialLoaderTest.TestSecurity(io),
              ServiceConfigFiles.Service.WEB,
              io);
      try (var keys = ServiceCredentialSet.load(reader, ServiceConfigFiles.Service.WEB)) {
        action.execute(keys);
      }
      ServiceCredentialSetTest.assertCleared(io);
    }
  }
}

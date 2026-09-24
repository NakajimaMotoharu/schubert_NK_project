package dev.codex.schubert.nk.api.bootstrap;

import dev.codex.schubert.nk.storage.NonSecretConfigSource;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.security.NoSuchAlgorithmException;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * API-only fixed source to strict parser bridge; NK-OPS-001, RD SYS-002/004, UI253, SS343 §4–5,
 * PG276.
 */
@NullMarked
public final class ApiConfigurationLoader {
  private final NonSecretConfigSource source;

  public ApiConfigurationLoader(NonSecretConfigSource source) {
    this.source = Objects.requireNonNull(source, "non-secret source");
  }

  public static ApiConfigurationLoader production() {
    return new ApiConfigurationLoader(ServiceConfigFiles.production());
  }

  public ApiNonSecretConfig load() throws StorageIoException, NoSuchAlgorithmException {
    ServiceConfigFiles.Contents contents =
        Objects.requireNonNull(source.read(ServiceConfigFiles.Service.API), "source contents");
    return ApiNonSecretConfig.parse(contents.commonYaml(), contents.serviceYaml());
  }
}

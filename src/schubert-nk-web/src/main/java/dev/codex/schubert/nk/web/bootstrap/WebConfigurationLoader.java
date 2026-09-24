package dev.codex.schubert.nk.web.bootstrap;

import dev.codex.schubert.nk.storage.NonSecretConfigSource;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.security.NoSuchAlgorithmException;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Web-only fixed source to strict parser bridge; NK-OPS-001, RD SYS-002/004, UI253, SS343 §4–5,
 * PG276.
 */
@NullMarked
public final class WebConfigurationLoader {
  private final NonSecretConfigSource source;

  public WebConfigurationLoader(NonSecretConfigSource source) {
    this.source = Objects.requireNonNull(source, "non-secret source");
  }

  public static WebConfigurationLoader production() {
    return new WebConfigurationLoader(ServiceConfigFiles.production());
  }

  public WebNonSecretConfig load() throws StorageIoException, NoSuchAlgorithmException {
    ServiceConfigFiles.Contents contents =
        Objects.requireNonNull(source.read(ServiceConfigFiles.Service.WEB), "source contents");
    return WebNonSecretConfig.parse(contents.commonYaml(), contents.serviceYaml());
  }
}

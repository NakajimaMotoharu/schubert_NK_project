package dev.codex.schubert.nk.api.bootstrap;

import dev.codex.schubert.nk.bootstrap.ChildStartupContext;
import dev.codex.schubert.nk.storage.NonSecretConfigSource;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.security.NoSuchAlgorithmException;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * API-only fixed source to strict parser bridge; NK-OPS-001, RD SYS-002/004, UI253, SS343 §4–5,
 * PG276.
 */
@NullMarked
public final class ApiConfigurationLoader {
  private static final String CONFIG_KEY = "SCHUBERT_NK_CONFIG_DIR";
  private static final String CONFIG_ROOT = "/etc/schubert-nk";
  private final NonSecretConfigSource source;
  private final @Nullable String configLocation;
  private final boolean unknownNamespace;

  public ApiConfigurationLoader(NonSecretConfigSource source, Map<String, String> environment) {
    this.source = Objects.requireNonNull(source, "non-secret source");
    Objects.requireNonNull(environment, "environment");
    this.configLocation = environment.get(CONFIG_KEY);
    this.unknownNamespace =
        environment.keySet().stream()
            .anyMatch(
                key ->
                    key.toUpperCase(Locale.ROOT).startsWith("SCHUBERT_NK_")
                        && !CONFIG_KEY.equals(key)
                        && !ChildStartupContext.isDescriptorKey(key));
  }

  public static ApiConfigurationLoader production() {
    return new ApiConfigurationLoader(ServiceConfigFiles.production(), System.getenv());
  }

  public ApiNonSecretConfig load() throws StorageIoException, NoSuchAlgorithmException {
    validateEnvironment();
    ServiceConfigFiles.Contents contents =
        Objects.requireNonNull(source.read(ServiceConfigFiles.Service.API), "source contents");
    return ApiNonSecretConfig.parse(contents.commonYaml(), contents.serviceYaml());
  }

  void validateEnvironment() {
    if (unknownNamespace || !CONFIG_ROOT.equals(configLocation))
      throw new IllegalArgumentException("API non-secret environment unavailable");
  }
}

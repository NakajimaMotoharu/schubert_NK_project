package dev.codex.schubert.nk.api.bootstrap;

import dev.codex.schubert.nk.storage.NonSecretConfigSource;
import dev.codex.schubert.nk.storage.ServiceCredentialLocation;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.security.NoSuchAlgorithmException;
import java.util.Map;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * API startup's non-secret settings and private-credential location gate, before DB/JMS creation.
 * It does not read or certify a credential or start a process. NK-OPS-001; SYS-002/004; UI243/253;
 * SS342/343 §4/6; PG279/PT-OPS-API-INPUT-001..004.
 */
@NullMarked
public final class ApiStartupInputs {
  private final ApiConfigurationLoader config;
  private final ServiceCredentialLocation credentials;

  public ApiStartupInputs(NonSecretConfigSource source, Map<String, String> environment) {
    Objects.requireNonNull(source, "non-secret source");
    Objects.requireNonNull(environment, "environment");
    credentials = ServiceCredentialLocation.read(environment);
    config = new ApiConfigurationLoader(source, environment);
  }

  public Values load() throws StorageIoException, NoSuchAlgorithmException {
    return new Values(config.load(), credentials);
  }

  public record Values(ApiNonSecretConfig config, ServiceCredentialLocation credentials) {
    public Values {
      Objects.requireNonNull(config, "API config");
      Objects.requireNonNull(credentials, "credential location");
    }
  }
}

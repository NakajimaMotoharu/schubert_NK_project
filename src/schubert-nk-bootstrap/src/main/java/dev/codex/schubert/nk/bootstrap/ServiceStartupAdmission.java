package dev.codex.schubert.nk.bootstrap;

import dev.codex.schubert.nk.storage.LinuxStartupAdmission;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;

/**
 * Mandatory outer child gate, before credentials/DB/JMS business factories. Only the native
 * admitted root issuer may attest root-only current-permit/fullgate facts. This child reobserves
 * its own kernel/NSS/config/actual manifest and never substitutes a fixture for those facts. No
 * readiness is reported here; trusted business callback releases A at actual ready, otherwise the
 * native outer owner releases it only after all callback cleanup. NK-OPS-001; SYS002/004,OPS009;
 * UI212/251; SS342/343 SSC086..089; BUG266/YKT200; PG301; PT-OPS-STARTADMIT-001..008.
 */
@NullMarked
public final class ServiceStartupAdmission {
  @FunctionalInterface
  public interface Ready {
    void release() throws IOException;

    default Map<String, String> information() throws IOException {
      throw new IOException("release information unavailable");
    }
  }

  @FunctionalInterface
  public interface Operation {
    void execute(Ready ready) throws IOException;
  }

  public record Configuration<T>(T value, String sha256) {
    public Configuration {
      Objects.requireNonNull(value, "configuration value");
      sha256 = checkedHash(sha256);
    }
  }

  @FunctionalInterface
  public interface ConfigSource<T> {
    Configuration<T> load() throws IOException;
  }

  @FunctionalInterface
  public interface ConfiguredOperation<T> {
    void execute(T value, Ready ready) throws IOException;
  }

  @FunctionalInterface
  interface Admitted {
    void execute(LinuxStartupAdmission.Identity identity, byte[] proof, Ready ready)
        throws IOException;
  }

  @FunctionalInterface
  interface DescriptorGate {
    void execute(int admission, int proof, Admitted operation) throws IOException;
  }

  interface Observation {
    ChildStartupContext.Observed capture() throws IOException;

    FixedServiceIdentity.Value identity(ServiceConfigFiles.Service service) throws IOException;

    String releaseHash() throws IOException;

    default Map<String, String> information(String releaseHash) throws IOException {
      throw new IOException("release information unavailable");
    }
  }

  private final ServiceConfigFiles.Service service;
  private final Map<String, String> environment;
  private final Optional<String> configHash;
  private final DescriptorGate gate;
  private final Observation observation;

  public static ServiceStartupAdmission create(
      ServiceConfigFiles.Service service, Map<String, String> environment, String configHash) {
    return new ServiceStartupAdmission(
        service, environment, configHash, new NativeGate(), new NativeObservation());
  }

  /** BUG269: configuration is read only within execute(ConfigSource, ConfiguredOperation). */
  public static ServiceStartupAdmission create(
      ServiceConfigFiles.Service service, Map<String, String> environment) {
    return new ServiceStartupAdmission(
        service, environment, Optional.empty(), new NativeGate(), new NativeObservation());
  }

  ServiceStartupAdmission(
      ServiceConfigFiles.Service service,
      Map<String, String> environment,
      String configHash,
      DescriptorGate gate,
      Observation observation) {
    this(service, environment, Optional.of(checkedHash(configHash)), gate, observation);
  }

  private ServiceStartupAdmission(
      ServiceConfigFiles.Service service,
      Map<String, String> environment,
      Optional<String> configHash,
      DescriptorGate gate,
      Observation observation) {
    this.service = Objects.requireNonNull(service, "service");
    this.environment = Map.copyOf(Objects.requireNonNull(environment, "environment"));
    this.configHash = configHash;
    this.gate = Objects.requireNonNull(gate, "native descriptor admission");
    this.observation = Objects.requireNonNull(observation, "child observation");
  }

  public void execute(Operation operation) throws IOException {
    Objects.requireNonNull(operation, "business operation");
    String hash =
        configHash.orElseThrow(() -> new IllegalStateException("configuration source required"));
    execute(
        () -> new Configuration<>(Boolean.TRUE, hash),
        (ignored, ready) -> operation.execute(ready));
  }

  public <T> void execute(ConfigSource<T> configuration, ConfiguredOperation<T> operation)
      throws IOException {
    Objects.requireNonNull(configuration, "configuration source");
    Objects.requireNonNull(operation, "business operation");
    var inputs = ChildStartupContext.inputs(environment);
    gate.execute(
        inputs.admissionFd(),
        inputs.proofFd(),
        (identity, bytes, ready) -> {
          StartupProofFrame frame;
          try {
            frame = StartupProofFrame.parse(bytes);
          } catch (IllegalArgumentException failure) {
            throw new IOException("startup proof unavailable");
          }
          var config = Objects.requireNonNull(configuration.load(), "loaded configuration");
          var before = Objects.requireNonNull(observation.capture(), "child observation");
          var fixed = Objects.requireNonNull(observation.identity(service), "fixed identity");
          String release = Objects.requireNonNull(observation.releaseHash(), "actual release hash");
          ChildStartupContext.verify(
              service, inputs, frame, identity, before, fixed, config.sha256(), release);
          if (!before.equals(observation.capture()))
            throw new IOException("startup context changed");
          var completion = new ReadyOnce(ready, () -> observation.information(release));
          try {
            operation.execute(config.value(), completion);
            completion.complete();
          } finally {
            completion.finish();
          }
        });
  }

  /** Returning without the exact ready handoff cannot turn an incomplete business graph into 0. */
  @FunctionalInterface
  private interface Information {
    Map<String, String> read() throws IOException;
  }

  private static final class ReadyOnce implements Ready {
    private final Ready delegate;
    private final Information information;
    private boolean active = true;
    private boolean attempted;
    private boolean released;
    private boolean poisoned;

    private ReadyOnce(Ready delegate, Information information) {
      this.delegate = delegate;
      this.information = information;
    }

    public synchronized void release() throws IOException {
      if (!active || attempted) {
        poisoned = true;
        throw new IOException("startup readiness unavailable");
      }
      attempted = true;
      try {
        delegate.release();
        released = true;
      } catch (IOException | RuntimeException | Error failure) {
        poisoned = true;
        throw failure;
      }
    }

    public synchronized Map<String, String> information() throws IOException {
      if (!active || attempted) throw new IOException("release information unavailable");
      return Map.copyOf(information.read());
    }

    private synchronized void complete() throws IOException {
      active = false;
      if (!released || poisoned) throw new IOException("startup readiness unavailable");
    }

    private synchronized void finish() {
      active = false;
    }
  }

  private static String checkedHash(String hash) {
    Objects.requireNonNull(hash, "config hash");
    if (!hash.matches("[0-9a-f]{64}")) throw new IllegalArgumentException("invalid config hash");
    return hash;
  }

  static final class NativeGate implements DescriptorGate {
    public void execute(int admission, int proof, Admitted operation) throws IOException {
      LinuxStartupAdmission.create()
          .withAdmitted(
              admission,
              proof,
              (lease, bytes) -> {
                operation.execute(lease.identity(), bytes, lease::close);
                return Boolean.TRUE;
              });
    }
  }

  static final class NativeObservation implements Observation {
    public Map<String, String> information(String releaseHash) throws IOException {
      return StartupReleaseManifest.create(new FixedServiceIdentity().configurationGroup())
          .publicInformation(releaseHash);
    }

    public ChildStartupContext.Observed capture() throws IOException {
      return new ChildStartupContext().capture();
    }

    public FixedServiceIdentity.Value identity(ServiceConfigFiles.Service service)
        throws IOException {
      return new FixedServiceIdentity().resolve(service);
    }

    public String releaseHash() throws IOException {
      return StartupReleaseManifest.create(new FixedServiceIdentity().configurationGroup())
          .sha256();
    }
  }
}

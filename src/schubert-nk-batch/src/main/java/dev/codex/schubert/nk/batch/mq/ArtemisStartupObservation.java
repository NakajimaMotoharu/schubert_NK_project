package dev.codex.schubert.nk.batch.mq;

import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.function.Consumer;
import java.util.function.Function;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.jspecify.annotations.NullMarked;

/**
 * Composes the live Ops-only, read-only broker checks before API/Web admission. The caller owns the
 * authenticated Core session and must additionally prove journal recovery, credential provenance,
 * Expiry maintenance and the final startup policy; this observation alone never grants readiness.
 * NK-OPS-001; RD MQ-001/002/009/010,SYS-004; UI231/251/253; SS321 §13,342 §4; PG267/PT-OPS-MQ-029.
 */
@NullMarked
public final class ArtemisStartupObservation {
  private static final Set<String> ADDRESSES =
      Set.of(
          "nk.sync.request",
          "nk.sync.reply.web",
          "nk.async.work",
          "nk.web.log",
          "nk.dead.letter",
          "nk.expiry");

  /** Verified values only, never a release/permit authority. SSC130/ISSBROKER001. */
  public record Evidence(
      Map<String, Map<String, String>> topology,
      Map<String, String> broker,
      Map<String, Map<String, String>> settings,
      Map<String, String> acceptor,
      Map<String, Map<String, Map<String, Boolean>>> roles,
      Map<String, ArtemisQueuePressureClient.Value> pressure) {
    public Evidence {
      topology = pairs(topology);
      broker = Map.copyOf(broker);
      settings = pairs(settings);
      acceptor = Map.copyOf(acceptor);
      var roleCopy = new HashMap<String, Map<String, Map<String, Boolean>>>();
      roles.forEach(
          (match, values) -> {
            var copy = new HashMap<String, Map<String, Boolean>>();
            values.forEach((role, permissions) -> copy.put(role, Map.copyOf(permissions)));
            roleCopy.put(match, Map.copyOf(copy));
          });
      roles = Map.copyOf(roleCopy);
      pressure = Map.copyOf(pressure);
    }

    private static Map<String, Map<String, String>> pairs(Map<String, Map<String, String>> input) {
      var copy = new HashMap<String, Map<String, String>>();
      input.forEach((name, fields) -> copy.put(name, Map.copyOf(fields)));
      return Map.copyOf(copy);
    }

    @Override
    public Map<String, Map<String, String>> topology() {
      return Map.copyOf(topology);
    }

    @Override
    public Map<String, Map<String, String>> settings() {
      return Map.copyOf(settings);
    }

    @Override
    public String toString() {
      return "ArtemisEvidence[observations=<redacted>]";
    }
  }

  private final Optional<Function<ClientSession, Evidence>> detailed;
  private final Consumer<ClientSession> topology;
  private final Consumer<ClientSession> broker;
  private final Consumer<ClientSession> settings;
  private final Consumer<ClientSession> acceptor;
  private final Consumer<ClientSession> roles;
  private final Function<ClientSession, Map<String, ArtemisQueuePressureClient.Pressure>> pressure;

  public ArtemisStartupObservation() {
    this(
        new ArtemisReadinessClient()::verifyTopology,
        new ArtemisManagementReadinessClient()::verifyBroker,
        new ArtemisAddressSettingsReadinessClient()::verify,
        new ArtemisAcceptorReadinessClient()::verify,
        new ArtemisRoleReadinessClient()::verify,
        new ArtemisQueuePressureClient()::inspect,
        Optional.of(ArtemisStartupObservation::readEvidence));
  }

  ArtemisStartupObservation(
      Consumer<ClientSession> topology,
      Consumer<ClientSession> broker,
      Consumer<ClientSession> settings,
      Consumer<ClientSession> acceptor,
      Consumer<ClientSession> roles,
      Function<ClientSession, Map<String, ArtemisQueuePressureClient.Pressure>> pressure) {
    this(topology, broker, settings, acceptor, roles, pressure, Optional.empty());
  }

  private ArtemisStartupObservation(
      Consumer<ClientSession> topology,
      Consumer<ClientSession> broker,
      Consumer<ClientSession> settings,
      Consumer<ClientSession> acceptor,
      Consumer<ClientSession> roles,
      Function<ClientSession, Map<String, ArtemisQueuePressureClient.Pressure>> pressure,
      Optional<Function<ClientSession, Evidence>> detailed) {
    this.detailed = Objects.requireNonNull(detailed);
    this.topology = Objects.requireNonNull(topology, "topology");
    this.broker = Objects.requireNonNull(broker, "broker");
    this.settings = Objects.requireNonNull(settings, "settings");
    this.acceptor = Objects.requireNonNull(acceptor, "acceptor");
    this.roles = Objects.requireNonNull(roles, "roles");
    this.pressure = Objects.requireNonNull(pressure, "pressure");
  }

  /** Return an immutable six-Queue observation, not a final go/no-go decision. */
  public Map<String, ArtemisQueuePressureClient.Pressure> inspect(ClientSession session) {
    Objects.requireNonNull(session, "ops session");
    if (detailed.isPresent()) {
      var states = new HashMap<String, ArtemisQueuePressureClient.Pressure>();
      inspectEvidence(session)
          .pressure()
          .forEach((address, actual) -> states.put(address, actual.state()));
      return Map.copyOf(states);
    }
    {
      try {
        topology.accept(session);
      } catch (ArtemisReadinessException declaredTopology) {
        throw new ArtemisManagementReadinessException();
      }
      broker.accept(session);
      settings.accept(session);
      acceptor.accept(session);
      roles.accept(session);
      Map<String, ArtemisQueuePressureClient.Pressure> observed = readPressure(session);
      if (!ADDRESSES.equals(observed.keySet())) throw new ArtemisManagementReadinessException();
      return observed;
    }
  }

  /** Legacy injected void callbacks cannot manufacture native observations. */
  public Evidence inspectEvidence(ClientSession session) {
    Objects.requireNonNull(session, "ops session");
    if (detailed.isEmpty()) throw new ArtemisManagementReadinessException();
    return Objects.requireNonNull(detailed.orElseThrow().apply(session), "actual broker evidence");
  }

  private static Evidence readEvidence(ClientSession session) {
    Map<String, Map<String, String>> topology;
    try {
      topology = new ArtemisReadinessClient().inspectTopology(session);
    } catch (ArtemisReadinessException declared) {
      throw new ArtemisManagementReadinessException();
    }
    return new Evidence(
        topology,
        new ArtemisManagementReadinessClient().inspectBroker(session),
        new ArtemisAddressSettingsReadinessClient().inspect(session),
        new ArtemisAcceptorReadinessClient().inspect(session),
        new ArtemisRoleReadinessClient().inspect(session),
        new ArtemisQueuePressureClient().inspectValues(session));
  }

  private Map<String, ArtemisQueuePressureClient.Pressure> readPressure(ClientSession session) {
    var actual = pressure.apply(session);
    if (actual == null || actual.values().stream().anyMatch(Objects::isNull))
      throw new ArtemisManagementReadinessException();
    return Map.copyOf(actual);
  }
}

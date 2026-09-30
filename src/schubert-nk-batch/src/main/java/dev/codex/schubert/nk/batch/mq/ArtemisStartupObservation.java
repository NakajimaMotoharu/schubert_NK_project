package dev.codex.schubert.nk.batch.mq;

import java.util.Map;
import java.util.Objects;
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
        new ArtemisQueuePressureClient()::inspect);
  }

  ArtemisStartupObservation(
      Consumer<ClientSession> topology,
      Consumer<ClientSession> broker,
      Consumer<ClientSession> settings,
      Consumer<ClientSession> acceptor,
      Consumer<ClientSession> roles,
      Function<ClientSession, Map<String, ArtemisQueuePressureClient.Pressure>> pressure) {
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

  private Map<String, ArtemisQueuePressureClient.Pressure> readPressure(ClientSession session) {
    var actual = pressure.apply(session);
    if (actual == null || actual.values().stream().anyMatch(Objects::isNull))
      throw new ArtemisManagementReadinessException();
    return Map.copyOf(actual);
  }
}

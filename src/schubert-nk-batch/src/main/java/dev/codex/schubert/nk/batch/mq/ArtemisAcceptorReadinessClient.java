package dev.codex.schubert.nk.batch.mq;

import java.util.Objects;
import java.util.Set;
import org.apache.activemq.artemis.api.core.JsonUtil;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.apache.activemq.artemis.json.JsonObject;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Live, effective single loopback Core acceptor and started status through Ops-only management. No
 * application role receives management permission. NK-OPS-001; RD MQ-001/002/009/010,SYS-004;
 * UI231/251/253; SS321 §2/10/13,342 §2/4; PG240; PT-OPS-MQ-013..015. Other broker readiness and
 * Production credential binding remain mandatory.
 */
@NullMarked
public final class ArtemisAcceptorReadinessClient {
  @FunctionalInterface
  interface Reader {
    @Nullable Object read(ClientSession session);
  }

  private static final String NETTY_FACTORY =
      "org.apache.activemq.artemis.core.remoting.impl.netty.NettyAcceptorFactory";
  private static final Set<String> ACCEPTOR_FIELDS =
      Set.of("name", "factoryClassName", "params", "extraProps");
  private static final Set<String> PARAM_FIELDS = Set.of("scheme", "host", "port", "protocols");

  private final Reader acceptors;
  private final Reader started;

  public ArtemisAcceptorReadinessClient() {
    this(
        ArtemisManagementReadinessClient::acceptors,
        ArtemisManagementReadinessClient::acceptorStarted);
  }

  ArtemisAcceptorReadinessClient(Reader acceptors, Reader started) {
    this.acceptors = Objects.requireNonNull(acceptors, "acceptor reader");
    this.started = Objects.requireNonNull(started, "started reader");
  }

  /** Borrow the Ops session; fail closed without disclosing management responses. */
  public void verify(ClientSession session) {
    Objects.requireNonNull(session, "ops session");
    try {
      Object response = acceptors.read(session);
      if (!(response instanceof String json)) throw new ArtemisManagementReadinessException();
      var values = JsonUtil.readJsonArray(json);
      if (values.size() != 1) throw new ArtemisManagementReadinessException();
      JsonObject acceptor = values.getJsonObject(0);
      if (!ACCEPTOR_FIELDS.equals(acceptor.keySet())
          || !"core".equals(acceptor.getString("name"))
          || !NETTY_FACTORY.equals(acceptor.getString("factoryClassName"))
          || !acceptor.getJsonObject("extraProps").isEmpty())
        throw new ArtemisManagementReadinessException();
      JsonObject params = acceptor.getJsonObject("params");
      if (!PARAM_FIELDS.equals(params.keySet())
          || !"tcp".equals(params.getString("scheme"))
          || !"127.0.0.1".equals(params.getString("host"))
          || !"61616".equals(params.getString("port"))
          || !"CORE".equals(params.getString("protocols"))
          || !Boolean.TRUE.equals(started.read(session)))
        throw new ArtemisManagementReadinessException();
    } catch (RuntimeException failure) {
      throw new ArtemisManagementReadinessException();
    }
  }
}

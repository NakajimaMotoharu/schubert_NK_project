package dev.codex.schubert.nk.batch.mq;

import dev.codex.schubert.nk.api.bootstrap.JdbcFailureGraph;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.function.Function;
import org.apache.activemq.artemis.api.core.JsonUtil;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.apache.activemq.artemis.json.JsonArray;
import org.apache.activemq.artemis.json.JsonObject;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Live, effective single loopback Core acceptor and started status through Ops-only management. No
 * application role receives management permission. NK-OPS-001; RD MQ-001/002/009/010,SYS-004;
 * UI231/251/253; SS321 §2/10/13,342 §2/4; PG240; PT-OPS-MQ-013..015. Other broker readiness and
 * Production credential binding remain mandatory. OPS-ACC-PORT-001..013 independently check the SDK
 * parser boundary; injecting that internal boundary never grants broker or startup authority.
 */
@NullMarked
public final class ArtemisAcceptorReadinessClient {
  private static final int EXPECTED_ACCEPTOR_COUNT = 1;

  private static final java.lang.String LITERAL_NAME = "name";

  private static final java.lang.String LITERAL_FACTORYCLASSNAME = "factoryClassName";

  private static final java.lang.String LITERAL_SCHEME = "scheme";

  private static final java.lang.String LITERAL_HOST = "host";

  private static final java.lang.String LITERAL_PORT = "port";

  private static final java.lang.String LITERAL_PROTOCOLS = "protocols";

  @FunctionalInterface
  interface Reader {
    @Nullable Object read(ClientSession session);
  }

  private static final String NETTY_FACTORY =
      "org.apache.activemq.artemis.core.remoting.impl.netty.NettyAcceptorFactory";
  private static final Set<String> ACCEPTOR_FIELDS =
      Set.of(LITERAL_NAME, LITERAL_FACTORYCLASSNAME, "params", "extraProps");
  private static final Set<String> PARAM_FIELDS =
      Set.of(LITERAL_SCHEME, LITERAL_HOST, LITERAL_PORT, LITERAL_PROTOCOLS);

  private final Reader acceptors;
  private final Reader started;
  private final Function<String, JsonArray> parser;

  public ArtemisAcceptorReadinessClient() {
    this(
        ArtemisManagementReadinessClient::acceptors,
        ArtemisManagementReadinessClient::acceptorStarted);
  }

  ArtemisAcceptorReadinessClient(Reader acceptors, Reader started) {
    this(acceptors, started, JsonUtil::readJsonArray);
  }

  /** Internal SDK boundary: independently test parser failures without a live management query. */
  ArtemisAcceptorReadinessClient(
      Reader acceptors, Reader started, Function<String, JsonArray> parser) {
    this.acceptors = Objects.requireNonNull(acceptors, "acceptor reader");
    this.started = Objects.requireNonNull(started, "started reader");
    this.parser = Objects.requireNonNull(parser, "acceptor parser");
  }

  /** Borrow the Ops session; fail closed without disclosing management responses. */
  public void verify(ClientSession session) {
    inspect(session);
  }

  /** SSC130 actual singleton/config/started values, data only. */
  public Map<String, String> inspect(ClientSession session) {
    Objects.requireNonNull(session, "ops session");
    Object response = acceptors.read(session);
    if (!(response instanceof String json)) throw new ArtemisManagementReadinessException();
    var actual = new LinkedHashMap<>(verifyResponse(json, parser));
    Object running = started.read(session);
    if (!(running instanceof Boolean bit)) throw new ArtemisManagementReadinessException();
    actual.put("started", bit ? "1" : "0");
    if (!bit) throw new ArtemisManagementReadinessException();
    return Map.copyOf(actual);
  }

  private static Map<String, String> verifyResponse(
      String json, Function<String, JsonArray> parser) {
    try {
      var values = Objects.requireNonNull(parser.apply(json), "parsed acceptor array");
      if (values.size() != EXPECTED_ACCEPTOR_COUNT) throw new ArtemisManagementReadinessException();
      if (!(values.get(0) instanceof JsonObject acceptor))
        throw new ArtemisManagementReadinessException();
      if (!ACCEPTOR_FIELDS.equals(acceptor.keySet())
          || !"core".equals(acceptor.getString(LITERAL_NAME))
          || !NETTY_FACTORY.equals(acceptor.getString(LITERAL_FACTORYCLASSNAME))
          || !(acceptor.get("extraProps") instanceof JsonObject extra)
          || !extra.isEmpty()) throw new ArtemisManagementReadinessException();
      if (!(acceptor.get("params") instanceof JsonObject params))
        throw new ArtemisManagementReadinessException();
      if (!PARAM_FIELDS.equals(params.keySet())
          || !"tcp".equals(params.getString(LITERAL_SCHEME))
          || !"127.0.0.1".equals(params.getString(LITERAL_HOST))
          || !"61616".equals(params.getString(LITERAL_PORT))
          || !"CORE".equals(params.getString(LITERAL_PROTOCOLS)))
        throw new ArtemisManagementReadinessException();
      return Map.of(
          LITERAL_NAME,
          acceptor.getString(LITERAL_NAME),
          LITERAL_FACTORYCLASSNAME,
          acceptor.getString(LITERAL_FACTORYCLASSNAME),
          LITERAL_SCHEME,
          params.getString(LITERAL_SCHEME),
          LITERAL_HOST,
          params.getString(LITERAL_HOST),
          LITERAL_PORT,
          params.getString(LITERAL_PORT),
          LITERAL_PROTOCOLS,
          params.getString(LITERAL_PROTOCOLS));
    } catch (org.apache.activemq.artemis.commons.shaded.json.JsonException
        | ClassCastException
        | IllegalStateException malformed) {
      JdbcFailureGraph.preserveFatal(malformed);
      throw new ArtemisManagementReadinessException();
    }
  }
}

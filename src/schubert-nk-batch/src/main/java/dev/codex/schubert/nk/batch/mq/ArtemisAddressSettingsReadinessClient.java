package dev.codex.schubert.nk.batch.mq;

import dev.codex.schubert.nk.api.bootstrap.JdbcFailureGraph;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Objects;
import org.apache.activemq.artemis.api.core.JsonUtil;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.apache.activemq.artemis.json.JsonObject;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Live, effective settings for all six approved business addresses. Uses only an Ops-authenticated,
 * caller-owned Core session; per-request temporary reply lifecycle and 2-second bound are shared
 * with PG236. NK-OPS-001; RD MQ-001/002/009/010; UI231/251/253; SS321 §5/10/13; PG237;
 * PT-OPS-MQ-010..012. Other SS321 startup checks remain mandatory.
 */
@NullMarked
public final class ArtemisAddressSettingsReadinessClient {
  private static final java.lang.String LITERAL_FALSE = "false";

  @FunctionalInterface
  interface Reader {
    @Nullable Object read(ClientSession session, String address);
  }

  private static final long MIB = 1024L * 1024L;
  private static final Map<String, Capacity> RETAINED_CAPACITIES = capacities();
  private static final Map<String, String> COMMON =
      Map.ofEntries(
          Map.entry("deadLetterAddress", "\"nk.dead.letter\""),
          Map.entry("expiryAddress", "\"nk.expiry\""),
          Map.entry("autoCreateDeadLetterResources", LITERAL_FALSE),
          Map.entry("autoCreateExpiryResources", LITERAL_FALSE),
          Map.entry("autoCreateAddresses", LITERAL_FALSE),
          Map.entry("autoCreateQueues", LITERAL_FALSE),
          Map.entry("autoDeleteAddresses", LITERAL_FALSE),
          Map.entry("autoDeleteQueues", LITERAL_FALSE),
          Map.entry("autoDeleteCreatedQueues", LITERAL_FALSE),
          Map.entry("addressFullMessagePolicy", "\"PAGE\""),
          Map.entry("pageFullMessagePolicy", "\"FAIL\""),
          Map.entry("diskFullMessagePolicy", "\"BLOCK\""),
          Map.entry("pageSizeBytes", Long.toString(8 * MIB)),
          Map.entry("maxReadPageBytes", Long.toString(16 * MIB)),
          Map.entry("maxReadPageMessages", "100"),
          Map.entry("redeliveryCollisionAvoidanceFactor", "0.0"),
          Map.entry("redeliveryDelay", "1000"),
          Map.entry("redeliveryMultiplier", "5.0"),
          Map.entry("maxRedeliveryDelay", "30000"),
          Map.entry("maxDeliveryAttempts", "4"),
          Map.entry("enableMetrics", "true"),
          Map.entry("enableIngressTimestamp", "true"));

  private final Reader reader;

  public ArtemisAddressSettingsReadinessClient() {
    this(ArtemisManagementReadinessClient::addressSettings);
  }

  ArtemisAddressSettingsReadinessClient(Reader reader) {
    this.reader = Objects.requireNonNull(reader, "management reader");
  }

  /** Fails closed on any missing, malformed, unknown or drifted effective value. */
  public void verify(ClientSession session) {
    inspect(session);
  }

  /** SSC130: actual approved fields from each one response, not the expected policy map. */
  public Map<String, Map<String, String>> inspect(ClientSession session) {
    Objects.requireNonNull(session, "ops session");
    var actual = new LinkedHashMap<String, Map<String, String>>();
    for (var entry : RETAINED_CAPACITIES.entrySet()) {
      Object response = reader.read(session, entry.getKey());
      if (!(response instanceof String json)) throw new ArtemisManagementReadinessException();
      actual.put(entry.getKey(), verifyResponse(json, entry.getValue()));
    }
    return Map.copyOf(actual);
  }

  private static Map<String, String> verifyResponse(String json, Capacity capacity) {
    try {
      JsonObject values = JsonUtil.readJsonObject(json);
      var actual = new LinkedHashMap<String, String>();
      for (var field : COMMON.entrySet())
        actual.put(field.getKey(), expect(values, field.getKey(), field.getValue()));
      actual.put(
          "maxSizeBytes",
          expect(values, "maxSizeBytes", Long.toString(capacity.memoryMib() * MIB)));
      actual.put(
          "maxSizeMessages",
          expect(values, "maxSizeMessages", Long.toString(capacity.memoryMessages())));
      actual.put(
          "pageLimitBytes",
          expect(values, "pageLimitBytes", Long.toString(capacity.pageMib() * MIB)));
      actual.put(
          "pageLimitMessages",
          expect(values, "pageLimitMessages", Long.toString(capacity.pageMessages())));
      return Map.copyOf(actual);
    } catch (org.apache.activemq.artemis.commons.shaded.json.JsonException
        | IllegalStateException malformed) {
      JdbcFailureGraph.preserveFatal(malformed);
      throw new ArtemisManagementReadinessException();
    }
  }

  private static String expect(JsonObject values, String field, String literal) {
    var observed = values.get(field);
    if (observed == null || !literal.equals(observed.toString()))
      throw new ArtemisManagementReadinessException();
    return observed.toString();
  }

  private static Map<String, Capacity> capacities() {
    var values = new LinkedHashMap<String, Capacity>();
    values.put("nk.sync.request", new Capacity(32, 50, 224, 450));
    values.put("nk.sync.reply.web", new Capacity(32, 50, 224, 450));
    values.put("nk.async.work", new Capacity(128, 1_000, 896, 9_000));
    values.put("nk.web.log", new Capacity(64, 1_000, 192, 9_000));
    values.put("nk.dead.letter", new Capacity(128, 1_000, 1_920, 9_000));
    values.put("nk.expiry", new Capacity(64, 1_000, 960, 9_000));
    return Map.copyOf(values);
  }

  private record Capacity(long memoryMib, long memoryMessages, long pageMib, long pageMessages) {}
}

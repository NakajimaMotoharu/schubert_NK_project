package dev.codex.schubert.nk.batch.mq;

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
  @FunctionalInterface
  interface Reader {
    @Nullable Object read(ClientSession session, String address);
  }

  private static final long MIB = 1024L * 1024L;
  private static final Map<String, Capacity> CAPACITIES = capacities();
  private static final Map<String, String> COMMON =
      Map.ofEntries(
          Map.entry("deadLetterAddress", "\"nk.dead.letter\""),
          Map.entry("expiryAddress", "\"nk.expiry\""),
          Map.entry("autoCreateDeadLetterResources", "false"),
          Map.entry("autoCreateExpiryResources", "false"),
          Map.entry("autoCreateAddresses", "false"),
          Map.entry("autoCreateQueues", "false"),
          Map.entry("autoDeleteAddresses", "false"),
          Map.entry("autoDeleteQueues", "false"),
          Map.entry("autoDeleteCreatedQueues", "false"),
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
    Objects.requireNonNull(session, "ops session");
    for (var entry : CAPACITIES.entrySet()) {
      Object response = reader.read(session, entry.getKey());
      if (!(response instanceof String json)) throw new ArtemisManagementReadinessException();
      verifyResponse(json, entry.getValue());
    }
  }

  private static void verifyResponse(String json, Capacity capacity) {
    try {
      JsonObject values = JsonUtil.readJsonObject(json);
      for (var field : COMMON.entrySet()) expect(values, field.getKey(), field.getValue());
      expect(values, "maxSizeBytes", Long.toString(capacity.memoryMib() * MIB));
      expect(values, "maxSizeMessages", Long.toString(capacity.memoryMessages()));
      expect(values, "pageLimitBytes", Long.toString(capacity.pageMib() * MIB));
      expect(values, "pageLimitMessages", Long.toString(capacity.pageMessages()));
    } catch (org.apache.activemq.artemis.commons.shaded.json.JsonException
        | IllegalStateException malformed) {
      throw new ArtemisManagementReadinessException();
    }
  }

  private static void expect(JsonObject values, String field, String literal) {
    var observed = values.get(field);
    if (observed == null || !literal.equals(observed.toString()))
      throw new ArtemisManagementReadinessException();
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

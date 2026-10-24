package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import io.micrometer.core.instrument.MockClock;
import io.micrometer.prometheusmetrics.PrometheusConfig;
import io.micrometer.prometheusmetrics.PrometheusMeterRegistry;
import io.prometheus.metrics.model.registry.PrometheusRegistry;
import java.lang.ref.Reference;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Pattern;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** MQPROM001..006/1743. Own synthetic memory only; no broker, JMS or control authority. */
class MqPrometheusGaugeContractTest {
  private static final Map<BrokerTopology, String> DESTINATIONS =
      Map.of(
          BrokerTopology.SYNC_REQUEST,
          "nk.sync.request",
          BrokerTopology.SYNC_REPLY_WEB,
          "nk.sync.reply.web",
          BrokerTopology.ASYNC_WORK,
          "nk.async.work",
          BrokerTopology.WEB_LOG,
          "nk.web.log",
          BrokerTopology.DEAD_LETTER,
          "nk.dead.letter",
          BrokerTopology.EXPIRY,
          "nk.expiry");
  private static final List<String> NAMES =
      List.of(
          "nk_mq_queue_messages",
          "nk_mq_queue_bytes",
          "nk_mq_address_memory_bytes",
          "nk_mq_address_paged_bytes",
          "nk_mq_paging_active",
          "nk_mq_page_files");
  private static final Pattern LINE =
      Pattern.compile("([a-z_]+)\\{(queue|address)=\"([a-z.]+)\"\\} (NaN|[-+0-9.eE]+)");

  private static final PrometheusConfig CONFIG =
      new PrometheusConfig() {
        @Override
        public @Nullable String get(String key) {
          return null;
        }

        @Override
        public Properties prometheusProperties() {
          var p = new Properties();
          p.setProperty("io.prometheus.exporter.include_created_timestamps", "false");
          p.setProperty("io.prometheus.exporter.exemplars_on_all_metric_types", "false");
          return p;
        }
      };

  private static final class Registry extends PrometheusMeterRegistry implements AutoCloseable {
    final AtomicInteger closes = new AtomicInteger();

    Registry() {
      super(CONFIG, new PrometheusRegistry(), new MockClock());
    }

    @Override
    public void close() {
      closes.incrementAndGet();
      super.close();
    }
  }

  private static Map<String, Double> text(Registry registry, MqPressureMetricRecorder owner) {
    try {
      var actual = new HashMap<String, Double>();
      var types = new HashMap<String, String>();
      for (String line : registry.scrape().split("\n")) {
        if (line.isEmpty() || line.startsWith("# HELP ")) continue;
        if (line.startsWith("# TYPE ")) {
          String[] p = line.split(" ");
          assertEquals(4, p.length);
          assertEquals(null, types.put(p[2], p[3]));
          continue;
        }
        var match = LINE.matcher(line);
        assertTrue(match.matches(), "closed literal labels and plain actual text");
        int n = NAMES.indexOf(match.group(1));
        assertTrue(n >= 0);
        assertEquals(n < 2 ? "queue" : "address", match.group(2));
        assertEquals(
            null,
            actual.put(match.group(1) + ":" + match.group(3), Double.valueOf(match.group(4))));
      }
      if (actual.isEmpty()) assertTrue(types.isEmpty());
      else {
        var expected = new HashMap<String, String>();
        for (String name : NAMES) expected.put(name, "gauge");
        assertEquals(expected, types);
        var expectedKeys = new java.util.HashSet<String>();
        for (int n = 0; n < 6; n++)
          for (String address :
              List.of(
                  "nk.sync.request",
                  "nk.sync.reply.web",
                  "nk.async.work",
                  "nk.web.log",
                  "nk.dead.letter",
                  "nk.expiry"))
            expectedKeys.add(NAMES.get(n) + ":" + address + (n < 2 ? ".q" : ""));
        assertEquals(expectedKeys, actual.keySet());
      }
      return Map.copyOf(actual);
    } finally {
      Reference.reachabilityFence(owner);
    }
  }

  private static void vector(Map<String, Double> actual, String address, double... expected) {
    assertEquals(6, expected.length);
    for (int n = 0; n < 6; n++)
      assertEquals(
          expected[n],
          actual.get(NAMES.get(n) + ":" + address + (n < 2 ? ".q" : "")).doubleValue());
  }

  @Test
  void mqprom001AllSixFamiliesAndThirtySixClosedSamplesStartUnknown() {
    try (var r = new Registry()) {
      var owner = new MqPressureMetricRecorder(r, "DEBUG");
      var actual = text(r, owner);
      assertEquals(36, actual.size());
      assertTrue(actual.values().stream().allMatch(v -> Double.isNaN(v)));
      assertEquals(0, r.closes.get());
    }
  }

  @Test
  void mqprom002EveryDestinationPublishesIndependentFieldVector() {
    try (var r = new Registry()) {
      var owner = new MqPressureMetricRecorder(r, "DEBUG");
      for (var d : DESTINATIONS.keySet())
        owner.record(d, new MqPressureMetricRecorder.Snapshot(11, 23, 37, 41, true, 53));
      var actual = text(r, owner);
      for (String address : DESTINATIONS.values()) vector(actual, address, 11, 23, 37, 41, 1, 53);
      assertEquals(36, actual.size());
    }
  }

  @Test
  void mqprom003MissingZeroMaximumAndUnaffectedOwnerDataRemainDistinct() {
    try (var r = new Registry()) {
      var owner = new MqPressureMetricRecorder(r, "DEBUG");
      var original = new MqPressureMetricRecorder.Snapshot(11, 23, 37, 41, true, 53);
      owner.record(BrokerTopology.SYNC_REQUEST, original);
      owner.record(
          BrokerTopology.WEB_LOG, new MqPressureMetricRecorder.Snapshot(0, 0, 0, 0, false, 0));
      vector(text(r, owner), "nk.web.log", 0, 0, 0, 0, 0, 0);
      owner.missing(BrokerTopology.SYNC_REQUEST);
      vector(
          text(r, owner),
          "nk.sync.request",
          Double.NaN,
          Double.NaN,
          Double.NaN,
          Double.NaN,
          Double.NaN,
          Double.NaN);
      vector(text(r, owner), "nk.web.log", 0, 0, 0, 0, 0, 0);
      owner.record(
          BrokerTopology.SYNC_REQUEST,
          new MqPressureMetricRecorder.Snapshot(
              Long.MAX_VALUE,
              Long.MAX_VALUE,
              Long.MAX_VALUE,
              Long.MAX_VALUE,
              false,
              Long.MAX_VALUE));
      vector(
          text(r, owner),
          "nk.sync.request",
          9.223372036854776E18,
          9.223372036854776E18,
          9.223372036854776E18,
          9.223372036854776E18,
          0,
          9.223372036854776E18);
      assertEquals(11, original.messages());
      assertEquals(53, original.pageFiles());
    }
  }

  @Test
  void mqprom004StandardRetainsNothingAndNeverClosesBorrowedRegistry() {
    try (var r = new Registry()) {
      var owner = new MqPressureMetricRecorder(r, "STANDARD");
      owner.record(
          BrokerTopology.WEB_LOG, new MqPressureMetricRecorder.Snapshot(11, 23, 37, 41, true, 53));
      owner.missing(BrokerTopology.WEB_LOG);
      assertTrue(text(r, owner).isEmpty());
      assertTrue(r.getMeters().isEmpty());
      assertTrue(owner.snapshot(BrokerTopology.WEB_LOG).isEmpty());
      assertEquals(0, r.closes.get());
    }
  }

  @Test
  void mqprom005TwoOwnersAndRepeatedSupplyNeverShareOrGrow() {
    try (var a = new Registry();
        var b = new Registry()) {
      var first = new MqPressureMetricRecorder(a, "DEBUG");
      var second = new MqPressureMetricRecorder(b, "DEBUG");
      for (int n = 0; n < 1000; n++)
        first.record(
            BrokerTopology.WEB_LOG,
            new MqPressureMetricRecorder.Snapshot(11, 23, 37, 41, true, 53));
      vector(text(a, first), "nk.web.log", 11, 23, 37, 41, 1, 53);
      assertTrue(text(b, second).values().stream().allMatch(v -> Double.isNaN(v)));
      assertEquals(36, a.getMeters().size());
      assertEquals(36, b.getMeters().size());
      assertEquals(0, a.closes.get());
      assertEquals(0, b.closes.get());
    }
  }

  @Test
  void mqprom006FiniteOwnedPublicationKeepsClosedCardinality() throws Exception {
    try (var r = new Registry()) {
      var owner = new MqPressureMetricRecorder(r, "DEBUG");
      var pool = Executors.newFixedThreadPool(4);
      try {
        var futures = new ArrayList<java.util.concurrent.Future<?>>();
        for (int n = 0; n < 64; n++)
          futures.add(
              pool.submit(
                  () -> {
                    for (var d : DESTINATIONS.keySet())
                      owner.record(
                          d, new MqPressureMetricRecorder.Snapshot(11, 23, 37, 41, true, 53));
                  }));
        for (var f : futures) f.get(5, TimeUnit.SECONDS);
        var actual = text(r, owner);
        for (String address : DESTINATIONS.values()) vector(actual, address, 11, 23, 37, 41, 1, 53);
        assertEquals(36, r.getMeters().size());
      } finally {
        pool.shutdownNow();
        assertTrue(pool.awaitTermination(5, TimeUnit.SECONDS));
      }
    }
  }
}

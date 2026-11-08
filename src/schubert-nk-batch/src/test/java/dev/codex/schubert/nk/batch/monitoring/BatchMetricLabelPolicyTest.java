package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.micrometer.core.instrument.Tag;
import java.util.AbstractList;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** BATCHLABEL001..014/1775: independent SS literal domain matrix, no business or IO operation. */
class BatchMetricLabelPolicyTest {
  private static final String BACKUP_DB_STEP_NAME = "BACKUP_DB";
  private static final String STEP_LABEL = "step";
  private static final String SUFFIX_LABEL = "suffix";
  private static final String PART_SUFFIX = ".part";
  private static final String READY_SUFFIX = ".ready";
  private static final String ACTOR_LABEL = "actor";
  private static final String RUNS = "nk_batch_runs_total";
  private static final String SUCCESS = "nk_batch_last_success_timestamp_seconds";
  private static final String FILES = "nk_file_transfer_files";
  private static final String BYTES = "nk_file_transfer_bytes";
  private static final String INTEGRITY = "nk_integrity_failures_total";
  private static final String RESTARTS = "nk_process_restarts_total";
  private static final List<String> STEPS =
      List.of(
          BACKUP_DB_STEP_NAME,
          "BACKUP_CONFIG",
          "CLEAN_NOTIFICATION",
          "CLEAN_QUESTION",
          "CLEAN_SESSION",
          "CLEAN_INBOX_OUTBOX",
          "CLEAN_LOG",
          "CLEAN_BATCH_RUN",
          "CLEAN_TRANSFER",
          "CLEAN_EXPIRY");
  private static final Map<String, Map<String, String>> FIXED =
      Map.of(
          RUNS, Map.of(STEP_LABEL, BACKUP_DB_STEP_NAME, "status", "SUCCESS"),
          SUCCESS, Map.of(STEP_LABEL, BACKUP_DB_STEP_NAME),
          FILES, Map.of(SUFFIX_LABEL, PART_SUFFIX),
          BYTES, Map.of(SUFFIX_LABEL, READY_SUFFIX),
          INTEGRITY, Map.of("area", "HASH", STEP_LABEL, BACKUP_DB_STEP_NAME),
          RESTARTS, Map.of("service", "BATCH", "reason", "NONZERO_EXIT"));
  private final BatchMetricLabelPolicy policy = new BatchMetricLabelPolicy();

  private static List<Tag> tags(Map<String, String> labels) {
    return labels.entrySet().stream().map(e -> Tag.of(e.getKey(), e.getValue())).toList();
  }

  private void check(String name, Map<String, String> expected) {
    assertEquals(expected, policy.labels(name, tags(expected)));
  }

  private static class MutableTag implements Tag {
    String key;
    String value;

    MutableTag(String key, String value) {
      this.key = key;
      this.value = value;
    }

    public String getKey() {
      return key;
    }

    public String getValue() {
      return value;
    }

    public int compareTo(Tag other) {
      return key.compareTo(other.getKey());
    }
  }

  @Test
  void batchlabel001ExactSixFamilyTypesAndKeys() {
    assertEquals(
        Map.of(
            RUNS,
            Set.of(STEP_LABEL, "status"),
            INTEGRITY,
            Set.of("area", STEP_LABEL),
            RESTARTS,
            Set.of("service", "reason")),
        policy.names(MetricContract.Kind.COUNTER));
    assertEquals(
        Map.of(
            SUCCESS, Set.of(STEP_LABEL), FILES, Set.of(SUFFIX_LABEL), BYTES, Set.of(SUFFIX_LABEL)),
        policy.names(MetricContract.Kind.GAUGE));
    assertEquals(Map.of(), policy.names(MetricContract.Kind.HISTOGRAM));
  }

  @Test
  void batchlabel002AllIndependentBatchAndTransferDomains() {
    assertEquals(10, STEPS.size());
    assertEquals(10, Set.copyOf(STEPS).size());
    int runs = 0;
    int success = 0;
    int transfer = 0;
    for (String step : STEPS) {
      check(SUCCESS, Map.of(STEP_LABEL, step));
      success++;
      for (String status : List.of("SUCCESS", "WARNING", "FAILED", "SKIPPED")) {
        check(RUNS, Map.of(STEP_LABEL, step, "status", status));
        runs++;
      }
    }
    for (String name : List.of(FILES, BYTES))
      for (String suffix : List.of(PART_SUFFIX, READY_SUFFIX)) {
        check(name, Map.of(SUFFIX_LABEL, suffix));
        transfer++;
      }
    assertEquals(40, runs);
    assertEquals(10, success);
    assertEquals(4, transfer);
  }

  @Test
  void batchlabel003AllThirtyIntegrityTuples() {
    int count = 0;
    for (String area : List.of("HASH", "PATH", "CONFIG"))
      for (String step : STEPS) {
        check(INTEGRITY, Map.of("area", area, STEP_LABEL, step));
        count++;
      }
    assertEquals(30, count);
  }

  @Test
  void batchlabel004AllTwentyFourRestartTuples() {
    int count = 0;
    for (String service : List.of("WEB", "API", "BATCH", "BROKER", "DB", "CADDY"))
      for (String reason : List.of("NONZERO_EXIT", "SIGNAL_EXIT", "OOM", "UNKNOWN")) {
        check(RESTARTS, Map.of("service", service, "reason", reason));
        count++;
      }
    assertEquals(24, count);
  }

  @Test
  void batchlabel005UnknownMetricRejectedBeforeTagsAreRead() {
    List<Tag> unread =
        new AbstractList<>() {
          public Tag get(int index) {
            throw new AssertionError("unknown must not inspect tags");
          }

          public int size() {
            throw new AssertionError("unknown must not inspect size");
          }
        };
    for (String name :
        List.of(
            "nk_http_requests_total",
            "nk_inbox_replays_total",
            "nk_unknown_fixture",
            "",
            "nk_batch_runs_total_extra"))
      assertEquals(
          "unknown Batch metric",
          assertThrows(IllegalArgumentException.class, () -> policy.labels(name, unread))
              .getMessage());
  }

  @Test
  void batchlabel006EveryFieldRejectsUnknownAndHighCardinalityKey() {
    FIXED.forEach(
        (name, expected) -> {
          expected.forEach(
              (key, unused) -> {
                var bad = new HashMap<>(expected);
                bad.put(key, "UNAPPROVED_FIXTURE");
                assertEquals(
                    "invalid Batch metric label",
                    assertThrows(
                            IllegalArgumentException.class, () -> policy.labels(name, tags(bad)))
                        .getMessage());
              });
          var bad = new HashMap<>(expected);
          bad.put(ACTOR_LABEL, "UNAPPROVED_FIXTURE");
          assertEquals(
              "invalid Batch metric label",
              assertThrows(IllegalArgumentException.class, () -> policy.labels(name, tags(bad)))
                  .getMessage());
        });
  }

  @Test
  void batchlabel007EveryFamilyRejectsMissingAndExtraKeys() {
    FIXED.forEach(
        (name, expected) -> {
          expected.forEach(
              (key, unused) -> {
                var missing = new HashMap<>(expected);
                missing.remove(key);
                assertEquals(
                    "missing Batch metric label",
                    assertThrows(
                            IllegalArgumentException.class,
                            () -> policy.labels(name, tags(missing)))
                        .getMessage());
              });
          var extra = new HashMap<>(expected);
          extra.put("path", "UNAPPROVED_FIXTURE");
          assertThrows(IllegalArgumentException.class, () -> policy.labels(name, tags(extra)));
        });
  }

  @Test
  void batchlabel008ActualDuplicateTagsAreRejected() {
    var duplicate = List.of(Tag.of(SUFFIX_LABEL, PART_SUFFIX), Tag.of(SUFFIX_LABEL, PART_SUFFIX));
    assertEquals(List.of(SUFFIX_LABEL, SUFFIX_LABEL), duplicate.stream().map(Tag::getKey).toList());
    assertEquals(
        "duplicate Batch metric label",
        assertThrows(IllegalArgumentException.class, () -> policy.labels(FILES, duplicate))
            .getMessage());
  }

  @Test
  void batchlabel009NullContractsNeverBecomeUnknownOrSuccess() {
    assertThrows(NullPointerException.class, () -> policy.names(null));
    assertThrows(NullPointerException.class, () -> policy.labels(null, List.of()));
    assertThrows(NullPointerException.class, () -> policy.labels(FILES, null));
    var tags = new ArrayList<Tag>();
    tags.add(null);
    assertThrows(NullPointerException.class, () -> policy.labels(FILES, tags));
    assertThrows(
        NullPointerException.class,
        () -> policy.labels(FILES, List.of(new MutableTag(null, PART_SUFFIX))));
    assertThrows(
        NullPointerException.class,
        () -> policy.labels(FILES, List.of(new MutableTag(SUFFIX_LABEL, null))));
  }

  @Test
  void batchlabel010ValueCopyIsDetachedAndImmutable() {
    var tag = new MutableTag(SUFFIX_LABEL, PART_SUFFIX);
    var original = new ArrayList<Tag>();
    original.add(tag);
    var result = policy.labels(FILES, original);
    tag.key = ACTOR_LABEL;
    tag.value = "UNAPPROVED";
    original.clear();
    assertEquals(Map.of(SUFFIX_LABEL, PART_SUFFIX), result);
    assertThrows(UnsupportedOperationException.class, () -> result.put(SUFFIX_LABEL, READY_SUFFIX));
    assertThrows(UnsupportedOperationException.class, () -> result.clear());
    assertThrows(
        UnsupportedOperationException.class,
        () -> result.entrySet().iterator().next().setValue(READY_SUFFIX));
  }

  @Test
  void batchlabel011NamespacesAreDeepImmutable() {
    for (var kind :
        List.of(
            MetricContract.Kind.COUNTER,
            MetricContract.Kind.GAUGE,
            MetricContract.Kind.HISTOGRAM)) {
      var result = policy.names(kind);
      assertThrows(UnsupportedOperationException.class, () -> result.put("nk_unknown", Set.of()));
      for (var keys : result.values())
        assertThrows(UnsupportedOperationException.class, () -> keys.add(ACTOR_LABEL));
    }
    assertEquals(3, policy.names(MetricContract.Kind.COUNTER).size());
    assertEquals(3, policy.names(MetricContract.Kind.GAUGE).size());
    FIXED.forEach(this::check);
  }

  @Test
  void batchlabel012ProviderFailuresKeepTheirIdentity() {
    var failure = new IllegalStateException("fixture");
    var broken =
        new MutableTag(SUFFIX_LABEL, PART_SUFFIX) {
          public String getKey() {
            throw failure;
          }
        };
    assertSame(
        failure,
        assertThrows(IllegalStateException.class, () -> policy.labels(FILES, List.of(broken))));
    var fatal = new AssertionError("fixture");
    var bad =
        new MutableTag(SUFFIX_LABEL, PART_SUFFIX) {
          public String getValue() {
            throw fatal;
          }
        };
    assertSame(fatal, assertThrows(AssertionError.class, () -> policy.labels(FILES, List.of(bad))));
  }

  @Test
  void batchlabel013FiniteConcurrentCallsHaveNoSharedMutableState() throws Exception {
    var workers = Executors.newFixedThreadPool(4);
    try {
      var other = new BatchMetricLabelPolicy();
      var jobs = new ArrayList<Future<?>>();
      for (int i = 0; i < 64; i++)
        jobs.add(
            workers.submit(
                () -> {
                  FIXED.forEach(
                      (name, expected) -> {
                        check(name, expected);
                        assertEquals(expected, other.labels(name, tags(expected)));
                      });
                }));
      for (var job : jobs) job.get(10, TimeUnit.SECONDS);
    } finally {
      workers.shutdownNow();
      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  @Test
  void batchlabel014ProviderKeyAndValueAreEachReadOnce() {
    var keyReads = new AtomicInteger();
    var valueReads = new AtomicInteger();
    var mutable =
        new MutableTag(SUFFIX_LABEL, PART_SUFFIX) {
          public String getKey() {
            return keyReads.incrementAndGet() == 1 ? SUFFIX_LABEL : ACTOR_LABEL;
          }

          public String getValue() {
            return valueReads.incrementAndGet() == 1 ? PART_SUFFIX : "UNAPPROVED";
          }
        };
    var result = policy.labels(FILES, List.of(mutable));
    assertEquals(Map.of(SUFFIX_LABEL, PART_SUFFIX), result);
    assertEquals(1, keyReads.get());
    assertEquals(1, valueReads.get());
    assertThrows(IllegalArgumentException.class, () -> policy.labels(FILES, List.of(mutable)));
    assertEquals(Map.of(SUFFIX_LABEL, PART_SUFFIX), result);
  }
}

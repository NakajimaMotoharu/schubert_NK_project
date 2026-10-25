package dev.codex.schubert.nk.api.application.scenario;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.api.persistence.ScenarioDetailSnapshot;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.file.LargeResultDescriptor;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioEntryRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.DeliveryMode;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryId;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryType;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import dev.codex.schubert.nk.protocol.layout.semantic.ScriptFileId;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/**
 * UI234 handwritten offsets; publisher stub tests projection only, not real file hash/lifecycle.
 */
class ScenarioDetailDeliveryTest {
  private static final Instant GENERATED = Instant.parse("2026-09-07T15:00:00Z");
  private static final UUID FILE = UUID.fromString("00000000-0000-4000-8000-000000000123");
  private static final String RELATIVE = "20260908/00000000-0000-4000-8000-000000000123.ready";
  private static final String HASH =
      "a".repeat(64); // Projection fixture only, not a content oracle.

  @Test
  void r01ZeroThrough200RecordsStayInlineAndNeverPublish() throws Exception {
    var delivery =
        new ScenarioDetailDelivery(
            (records, time) -> {
              fail("inline must not touch the filesystem publisher");
              throw new AssertionError("publisher must not run");
            });
    for (int count : new int[] {0, 1, 199, 200}) {
      var result = delivery.deliver(snapshot(count), GENERATED);
      assertEquals("SCNRSP01", result.layoutId().value());
      var bytes = PayloadCodec.standard().encode(PayloadTypeCatalog.encode(result), false);
      assertArrayEquals(data(false, 0), bytes.copyData());
      assertEquals(count, bytes.recordCount());
      assertEquals(4800, bytes.recordLength());
      List<byte[]> records = bytes.copyRecords();
      for (int index = 0; index < count; index++)
        assertArrayEquals(record(index), records.get(index));
      assertEquals(
          1984 + count * 4800,
          256 + bytes.dataLength() + bytes.recordLength() * bytes.recordCount());
      assertTrue(256 + bytes.dataLength() + bytes.recordLength() * bytes.recordCount() < 1_000_000);
      assertThrows(
          UnsupportedOperationException.class,
          () -> result.records().add(snapshot(1).records().getFirst()));
    }
  }

  @Test
  void r02Above200PublishesOnceAndProjectsEveryFileDescriptorField() throws Exception {
    for (int count : new int[] {201, 10000}) {
      var snapshot = snapshot(count);
      AtomicInteger calls = new AtomicInteger();
      var delivery =
          new ScenarioDetailDelivery(
              (records, time) -> {
                calls.incrementAndGet();
                assertSame(snapshot.records(), records);
                assertEquals(GENERATED, time);
                assertEquals(count, records.size());
                assertThrows(
                    UnsupportedOperationException.class, () -> records.add(records.getFirst()));
                return descriptor(count);
              });
      var result = delivery.deliver(snapshot, GENERATED);
      assertEquals(1, calls.get());
      var bytes = PayloadCodec.standard().encode(PayloadTypeCatalog.encode(result), false);
      assertArrayEquals(data(true, count), bytes.copyData());
      assertEquals(0, bytes.recordCount());
      assertTrue(bytes.copyRecords().isEmpty());
      assertEquals(count, snapshot.records().size());
      assertEquals(DeliveryMode.INLINE, snapshot.metadata().deliveryMode());
    }
  }

  @Test
  void r03NullPortFailureAndMismatchedDescriptorNeverFallbackOrRegenerate() throws Exception {
    assertThrows(NullPointerException.class, () -> new ScenarioDetailDelivery(null));
    var delivery = new ScenarioDetailDelivery((records, time) -> descriptor(records.size()));
    assertThrows(NullPointerException.class, () -> delivery.deliver(null, GENERATED));
    assertThrows(NullPointerException.class, () -> delivery.deliver(snapshot(0), null));
    AtomicInteger calls = new AtomicInteger();
    IOException failure = new IOException("synthetic publisher unavailable");
    var failed =
        new ScenarioDetailDelivery(
            (records, time) -> {
              calls.incrementAndGet();
              throw failure;
            });
    assertSame(
        failure, assertThrows(IOException.class, () -> failed.deliver(snapshot(201), GENERATED)));
    assertEquals(1, calls.get());
    var wrong =
        new ScenarioDetailDelivery(
            (records, time) -> {
              calls.incrementAndGet();
              return descriptor(1);
            });
    assertEquals(
        "published scenario record count differs from snapshot",
        assertThrows(IllegalStateException.class, () -> wrong.deliver(snapshot(201), GENERATED))
            .getMessage());
    assertEquals(2, calls.get());
    var missing = new ScenarioDetailDelivery((records, time) -> null);
    assertThrows(NullPointerException.class, () -> missing.deliver(snapshot(201), GENERATED));
  }

  private static ScenarioDetailSnapshot snapshot(int count) {
    var metadata =
        new ScenarioDetailResponseData(
            new ScriptFileId(30),
            GameCode.NUKITASHI_1,
            "Chapter",
            DisplayPath.of("scenario/01.txt"),
            Optional.of(new ScriptFileId(20)),
            Optional.of("Previous"),
            Optional.of(new ScriptFileId(40)),
            Optional.of("Next"),
            DeliveryMode.INLINE,
            Optional.empty(),
            Optional.empty(),
            0,
            Optional.empty(),
            0,
            0);
    List<ScenarioEntryRecord> records = new ArrayList<>();
    for (int i = 0; i < count; i++) {
      records.add(
          new ScenarioEntryRecord(
              new EntryId(1000 + i),
              i + 1,
              42 + i,
              EntryType.NARRATION,
              Optional.empty(),
              "本文 " + i,
              0,
              Optional.empty(),
              Optional.empty()));
    }
    return new ScenarioDetailSnapshot(metadata, records);
  }

  private static LargeResultDescriptor descriptor(int count) {
    return new LargeResultDescriptor(FILE, RELATIVE, 4800L * count, HASH, count);
  }

  private static byte[] data(boolean file, int count) {
    byte[] bytes = spaces(1728);
    number(bytes, 0, 12, 30);
    text(bytes, 12, "NUKITASHI1");
    text(bytes, 24, "Chapter");
    text(bytes, 280, "scenario/01.txt");
    text(bytes, 792, "20");
    text(bytes, 804, "Previous");
    text(bytes, 1060, "40");
    text(bytes, 1072, "Next");
    text(bytes, 1328, file ? "F" : "I");
    number(bytes, 1621, 12, file ? 4800L * count : 0);
    number(bytes, 1697, 6, file ? 4800 : 0);
    number(bytes, 1703, 9, file ? count : 0);
    if (file) {
      text(bytes, 1329, "00000000-0000-4000-8000-000000000123");
      text(bytes, 1365, RELATIVE);
      text(bytes, 1633, HASH);
    }
    return bytes;
  }

  private static byte[] record(int index) {
    byte[] bytes = spaces(4800);
    number(bytes, 0, 12, 1000L + index);
    number(bytes, 12, 6, index + 1L);
    number(bytes, 18, 8, 42L + index);
    text(bytes, 26, "narration");
    text(bytes, 164, "本文 " + index);
    number(bytes, 4260, 3, 0);
    return bytes;
  }

  private static byte[] spaces(int count) {
    byte[] bytes = new byte[count];
    Arrays.fill(bytes, (byte) ' ');
    return bytes;
  }

  private static void number(byte[] bytes, int offset, int width, long value) {
    text(bytes, offset, String.format(Locale.ROOT, "%0" + width + "d", value));
  }

  private static void text(byte[] bytes, int offset, String value) {
    byte[] utf8 = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(utf8, 0, bytes, offset, utf8.length);
  }
}

package dev.codex.schubert.nk.protocol.codec;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FieldDefinition;
import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutFieldCatalog;
import dev.codex.schubert.nk.protocol.layout.LayoutFields;
import dev.codex.schubert.nk.protocol.layout.PayloadValues;
import dev.codex.schubert.nk.protocol.layout.Presence;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import org.junit.jupiter.api.Test;

class PayloadGoldenVectorTest {
  @Test
  void allSixtyFourLayoutsMatchIndependentMinimumMaximumAndErrorHashes() throws IOException {
    Map<String, GoldenHashes> golden = readGoldenHashes();
    PayloadCodec codec = PayloadCodec.standard();
    int responseCount = 0;

    for (LayoutFields layout : LayoutFieldCatalog.standard().all()) {
      GoldenHashes expected = golden.get(layout.id().value());
      assertTrue(expected != null, layout.id().value());

      FieldValueSet minimumData = boundaryValues(layout.dataFields(), false);
      List<FieldValueSet> minimumRecords =
          layout.recordFields().isEmpty()
              ? List.of()
              : List.of(boundaryValues(layout.recordFields(), false));
      FixedPayload minimum =
          codec.encode(new PayloadValues(layout.id(), minimumData, minimumRecords), false);
      assertEquals(expected.minimumData(), sha256(minimum.copyData()), layout.id().value());
      assertEquals(
          expected.minimumRecord(),
          sha256(minimumRecords.isEmpty() ? new byte[0] : minimum.copyRecords().getFirst()),
          layout.id().value());
      assertEquals(
          new PayloadValues(layout.id(), minimumData, minimumRecords),
          codec.decode(layout.id(), minimum.copyData(), minimum.copyRecords(), false),
          layout.id().value());

      FieldValueSet maximumData = boundaryValues(layout.dataFields(), true);
      List<FieldValueSet> maximumRecords =
          layout.recordFields().isEmpty()
              ? List.of()
              : List.of(boundaryValues(layout.recordFields(), true));
      FixedPayload maximum =
          codec.encode(new PayloadValues(layout.id(), maximumData, maximumRecords), false);
      assertEquals(expected.maximumData(), sha256(maximum.copyData()), layout.id().value());
      assertEquals(
          expected.maximumRecord(),
          sha256(maximumRecords.isEmpty() ? new byte[0] : maximum.copyRecords().getFirst()),
          layout.id().value());
      assertEquals(
          new PayloadValues(layout.id(), maximumData, maximumRecords),
          codec.decode(layout.id(), maximum.copyData(), maximum.copyRecords(), false),
          layout.id().value());

      if (layout.layout().messageKind() == MessageKind.RESPONSE) {
        responseCount++;
        FixedPayload error =
            codec.encode(new PayloadValues(layout.id(), FieldValueSet.empty(), List.of()), true);
        assertEquals(expected.errorData(), sha256(error.copyData()), layout.id().value());
        codec.decode(layout.id(), error.copyData(), List.of(), true);
      } else {
        assertEquals("-", expected.errorData(), layout.id().value());
      }
    }
    assertEquals(64, golden.size());
    assertEquals(31, responseCount);
  }

  @Test
  void everyRepeatingLayoutAcceptsItsMaximumRecordBoundary() {
    PayloadCodec codec = PayloadCodec.standard();
    int repeatingLayouts = 0;
    for (LayoutFields layout : LayoutFieldCatalog.standard().all()) {
      int count = layout.layout().maximumRecordCount();
      if (layout.recordFields().isEmpty()) {
        assertEquals(0, count, layout.id().value());
        continue;
      }
      repeatingLayouts++;
      FieldValueSet record = boundaryValues(layout.recordFields(), false);
      List<FieldValueSet> records = Collections.nCopies(count, record);
      FixedPayload encoded =
          codec.encode(
              new PayloadValues(layout.id(), boundaryValues(layout.dataFields(), false), records),
              false);
      assertEquals(count, encoded.recordCount(), layout.id().value());
      assertEquals(
          layout.layout().maximumTotalLength(),
          256 + encoded.dataLength() + encoded.recordLength() * encoded.recordCount(),
          layout.id().value());
      assertEquals(
          count,
          codec
              .decode(layout.id(), encoded.copyData(), encoded.copyRecords(), false)
              .records()
              .size(),
          layout.id().value());
    }
    assertEquals(14, repeatingLayouts);
  }

  @Test
  void sharedCodecProducesIdenticalBytesUnderConcurrentUse() throws Exception {
    PayloadCodec codec = PayloadCodec.standard();
    LayoutFields layout = LayoutFieldCatalog.standard().require("LGNREQ01");
    PayloadValues values =
        new PayloadValues(layout.id(), boundaryValues(layout.dataFields(), false), List.of());
    // BUG1285/YKT1051: UI234 LGNREQ01: Username 1/64, Password 65/256,
    // Client address 321/45, Reserved 366/19. Never encode expected with codec.
    byte[] expected = new byte[384];
    java.util.Arrays.fill(expected, (byte) ' ');
    expected[0] = 'A';
    expected[64] = 'A';
    expected[320] = 'A';
    CountDownLatch ready = new CountDownLatch(8);
    CountDownLatch start = new CountDownLatch(1);
    try (var executor = Executors.newFixedThreadPool(8)) {
      List<Future<byte[]>> futures = new ArrayList<>();
      for (int index = 0; index < 8; index++) {
        futures.add(
            executor.submit(
                () -> {
                  ready.countDown();
                  start.await();
                  return codec.encode(values, false).copyData();
                }));
      }
      ready.await();
      start.countDown();
      for (Future<byte[]> future : futures) {
        assertTrue(MessageDigest.isEqual(expected, future.get()));
      }
    }
    assertSame(codec, PayloadCodec.standard());
  }

  private static FieldValueSet boundaryValues(List<FieldDefinition<?>> fields, boolean maximum) {
    LinkedHashMap<String, FieldValue> values = new LinkedHashMap<>();
    for (FieldDefinition<?> field : fields) {
      if (field.presence() == Presence.FIXED) {
        continue;
      }
      FieldValue value;
      if (!maximum && field.presence() != Presence.MANDATORY) {
        value = FieldValue.Unset.INSTANCE;
      } else {
        value =
            switch (field.wireType()) {
              case TEXT -> new FieldValue.Text(maximum ? "Z".repeat(field.length()) : "A");
              case NUMERIC ->
                  new FieldValue.Numeric(
                      maximum ? PayloadCodec.maximumForDigits(field.length()) : 0);
              case BOOLEAN -> new FieldValue.Flag(maximum);
            };
      }
      if (field.name().equals("Log type") && field.start() == 18) {
        value = new FieldValue.Text("REQUEST"); // QA054: preserve original REQUEST golden bytes.
      }
      values.put(field.name(), value);
    }
    return new FieldValueSet(values);
  }

  private static Map<String, GoldenHashes> readGoldenHashes() throws IOException {
    LinkedHashMap<String, GoldenHashes> result = new LinkedHashMap<>();
    try (BufferedReader reader =
        new BufferedReader(
            new InputStreamReader(
                Objects.requireNonNull(
                    PayloadGoldenVectorTest.class.getResourceAsStream(
                        "/protocol/payload-golden-ui234-236.tsv")),
                StandardCharsets.UTF_8))) {
      for (String line = reader.readLine(); line != null; line = reader.readLine()) {
        if (line.startsWith("#")) {
          continue;
        }
        String[] columns = line.split("\\t", -1);
        assertEquals(6, columns.length, line);
        assertNull(
            result.put(
                columns[0],
                new GoldenHashes(columns[1], columns[2], columns[3], columns[4], columns[5])),
            columns[0]);
      }
    }
    return Map.copyOf(result);
  }

  private static String sha256(byte[] value) {
    try {
      return java.util.HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(value));
    } catch (NoSuchAlgorithmException exception) {
      throw new AssertionError(exception);
    }
  }

  private record GoldenHashes(
      String minimumData,
      String maximumData,
      String minimumRecord,
      String maximumRecord,
      String errorData) {}
}

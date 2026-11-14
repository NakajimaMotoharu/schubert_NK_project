package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-STREAM001..012; literal wire values, memory-only borrowed sinks. */
final class PostgresCopyTextWriterTest {
  private static final String ORACLE_FIRST_ROW = "A\t\\N\t\\\\N\t改行\\n😀\n";
  private static final String ORACLE_SECOND_ROW = "\t\\t\t\\\\\té\n";
  private static final String DIAGNOSTIC = "migration COPY stream input is invalid";
  private static final String CODEC_DIAGNOSTIC = "migration COPY text data is invalid";

  @Test
  void independentGoldenRetainsNullEscapesAndUtf8AcrossTwoRows() throws Exception {
    var sink = new TrackingSink();
    writer().writeRows(List.of(first(), second()), sink);
    assertArrayEquals(
        (ORACLE_FIRST_ROW + ORACLE_SECOND_ROW).getBytes(StandardCharsets.UTF_8), sink.bytes());
    assertFalse(sink.closed);
    assertFalse(sink.flushed);
  }

  @Test
  void emptyIterableMakesNoSinkCallsAndDoesNotOwnIt() throws Exception {
    var sink = new TrackingSink();
    writer().writeRows(List.of(), sink);
    assertArrayEquals(new byte[0], sink.bytes());
    assertEquals(0, sink.writes);
    assertFalse(sink.closed);
    assertFalse(sink.flushed);
  }

  @Test
  void obtainsOneIteratorAndWritesCurrentRowBeforeObtainingTheNext() throws Exception {
    var sink = new TrackingSink();
    var iterators = new int[1];
    Iterable<List<@Nullable String>> input =
        () -> {
          iterators[0]++;
          return new Iterator<>() {
            private int position;

            @Override
            public boolean hasNext() {
              return position < 2;
            }

            @Override
            public List<@Nullable String> next() {
              int previousPosition = position;
              position++;
              if (previousPosition == 0) return first();
              assertArrayEquals(ORACLE_FIRST_ROW.getBytes(StandardCharsets.UTF_8), sink.bytes());
              return second();
            }
          };
        };
    writer().writeRows(input, sink);
    assertEquals(1, iterators[0]);
    assertArrayEquals(
        (ORACLE_FIRST_ROW + ORACLE_SECOND_ROW).getBytes(StandardCharsets.UTF_8), sink.bytes());
  }

  @Test
  void constructorRejectsNullEncoderWithFixedDiagnostic() {
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> new PostgresCopyTextWriter(null))
            .getMessage());
  }

  @Test
  void nullSourceAndSinkAreRejectedBeforeRequestingAnIterator() {
    Iterable<List<@Nullable String>> never =
        () -> {
          throw new AssertionError("must not iterate");
        };
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class, () -> writer().writeRows(null, new TrackingSink()))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> writer().writeRows(never, null))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> writer().writeRows(null, null))
            .getMessage());
  }

  @Test
  void nullOrEmptyRowsFailWithoutWritingThatRow() {
    var nullRow = new ArrayList<List<@Nullable String>>();
    nullRow.add(null);
    var sink = new TrackingSink();
    assertEquals(
        DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> writer().writeRows(nullRow, sink))
            .getMessage());
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class, () -> writer().writeRows(List.of(List.of()), sink))
            .getMessage());
    assertArrayEquals(new byte[0], sink.bytes());
  }

  @Test
  void mixedWidthRejectsBeforeSendingTheSecondRowAndKeepsTheDeclaredPrefix() {
    var sink = new TrackingSink();
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class,
                () -> writer().writeRows(List.of(first(), List.of("short")), sink))
            .getMessage());
    assertArrayEquals(ORACLE_FIRST_ROW.getBytes(StandardCharsets.UTF_8), sink.bytes());
    assertFalse(sink.closed);
    assertFalse(sink.flushed);
  }

  @Test
  void invalidFieldPreservesCodecDiagnosticAndDoesNotSendMalformedRow() {
    for (String invalid : List.of("bad\u0000value", "\ud800", "\udc00")) {
      var row = second();
      row.set(3, invalid);
      var sink = new TrackingSink();
      assertEquals(
          CODEC_DIAGNOSTIC,
          assertThrows(
                  IllegalArgumentException.class,
                  () -> writer().writeRows(List.of(first(), row), sink))
              .getMessage());
      assertArrayEquals(ORACLE_FIRST_ROW.getBytes(StandardCharsets.UTF_8), sink.bytes());
    }
  }

  @Test
  void originalSinkFailureStopsBeforeObtainingAnotherRowWithoutCloseOrFlush() {
    for (int failureOffset : List.of(0, 3)) {
      var acquired = new int[1];
      var prefix = new ByteArrayOutputStream();
      var failure = new IOException("synthetic sink failure");
      Iterable<List<@Nullable String>> input =
          () ->
              new Iterator<>() {
                @Override
                public boolean hasNext() {
                  return acquired[0] < 2;
                }

                @Override
                public List<@Nullable String> next() {
                  acquired[0]++;
                  return first();
                }
              };
      var sink =
          new OutputStream() {
            @Override
            public void write(int value) throws IOException {
              if (prefix.size() == failureOffset) throw failure;
              prefix.write(value);
            }

            @Override
            public void close() {
              throw new AssertionError("borrowed close");
            }

            @Override
            public void flush() {
              throw new AssertionError("borrowed flush");
            }
          };
      assertSame(failure, assertThrows(IOException.class, () -> writer().writeRows(input, sink)));
      assertEquals(1, acquired[0]);
      assertArrayEquals(
          (failureOffset == 0 ? "" : "A\t\\").getBytes(StandardCharsets.US_ASCII),
          prefix.toByteArray());
    }
  }

  @Test
  void originalIteratorFailureRemainsFailureAfterThePreviousRowWasSent() {
    var failure = new IllegalStateException("synthetic iterator failure");
    var sink = new TrackingSink();
    Iterable<List<@Nullable String>> input =
        () ->
            new Iterator<>() {
              private int position;

              @Override
              public boolean hasNext() {
                return position < 2;
              }

              @Override
              public List<@Nullable String> next() {
                int previousPosition = position;
                position++;
                if (previousPosition == 0) return first();
                throw failure;
              }
            };
    assertSame(
        failure, assertThrows(IllegalStateException.class, () -> writer().writeRows(input, sink)));
    assertArrayEquals(ORACLE_FIRST_ROW.getBytes(StandardCharsets.UTF_8), sink.bytes());
    assertFalse(sink.closed);
    assertFalse(sink.flushed);
  }

  @Test
  void callerOwnsInputsSinkAndLaterCallsAndRedactionStaysFixed() throws Exception {
    var row = first();
    var unchanged = new ArrayList<>(row);
    var sink = new TrackingSink();
    var writer = writer();
    writer.writeRows(List.of(row), sink);
    assertEquals(unchanged, row);
    assertFalse(sink.closed);
    assertFalse(sink.flushed);
    sink.close();
    assertTrue(sink.closed);
    var independent = new TrackingSink();
    writer.writeRows(List.of(first()), independent);
    assertArrayEquals(ORACLE_FIRST_ROW.getBytes(StandardCharsets.UTF_8), independent.bytes());
    assertEquals("PostgresCopyTextWriter[REDACTED]", writer.toString());
  }

  @Test
  void finiteOwnedConcurrentWritesUseIndependentSinksAndLiteralGolden() throws Exception {
    var writer = writer();
    var executor = Executors.newFixedThreadPool(8);
    try {
      var futures = new ArrayList<Future<byte[]>>();
      for (int index = 0; index < 64; index++)
        futures.add(
            executor.submit(
                () -> {
                  var sink = new TrackingSink();
                  writer.writeRows(List.of(first(), second()), sink);
                  return sink.bytes();
                }));
      for (var future : futures)
        assertArrayEquals(
            (ORACLE_FIRST_ROW + ORACLE_SECOND_ROW).getBytes(StandardCharsets.UTF_8),
            future.get(5, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  private static PostgresCopyTextWriter writer() {
    return new PostgresCopyTextWriter(new PostgresCopyTextEncoder());
  }

  private static List<@Nullable String> first() {
    return new ArrayList<>(Arrays.asList("A", null, "\\N", "改行\n😀"));
  }

  private static List<@Nullable String> second() {
    return new ArrayList<>(List.of("", "\t", "\\", "é"));
  }

  private static final class TrackingSink extends OutputStream {
    private final ByteArrayOutputStream output = new ByteArrayOutputStream();
    private boolean closed;
    private boolean flushed;
    private int writes;

    @Override
    public void write(int value) {
      writes++;
      output.write(value);
    }

    @Override
    public void close() {
      closed = true;
    }

    @Override
    public void flush() {
      flushed = true;
    }

    byte[] bytes() {
      return output.toByteArray();
    }
  }
}

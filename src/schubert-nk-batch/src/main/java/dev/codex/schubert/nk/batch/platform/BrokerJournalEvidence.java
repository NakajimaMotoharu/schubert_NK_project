package dev.codex.schubert.nk.batch.platform;

import com.google.gson.Strictness;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonToken;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.IOException;
import java.io.StringReader;
import java.math.BigInteger;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.TreeMap;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * Full fresh-invocation native console journal; no raw messages escape or become a permit.
 * SS321§13/341/343 SSC125 BROKERSTART003. Vendor2.56 logger_impl primary constants: 221013 NIO,
 * 221007 active, 221001 started; successful recovery also requires actual Ops gates.
 */
@NullMarked
public final class BrokerJournalEvidence {
  private static final int MAX = 4 * 1024 * 1024;
  private static final Set<String> REQUIRED =
      Set.of(
          "MESSAGE",
          "PRIORITY",
          "_SYSTEMD_INVOCATION_ID",
          "_BOOT_ID",
          "_SYSTEMD_UNIT",
          "__CURSOR",
          "__MONOTONIC_TIMESTAMP",
          "__REALTIME_TIMESTAMP");
  private static final Set<String> OPTIONAL = Set.of("__SEQNUM", "__SEQNUM_ID");

  public record Summary(int entries, String sha256) {
    @Override
    public String toString() {
      return "BrokerJournalSummary[redacted]";
    }
  }

  private BrokerJournalEvidence() {}

  /** SSC132 complete decoded content, independent of journalctl JSON object member order. */
  static String contentSha256(byte[] bytes) throws IOException {
    Objects.requireNonNull(bytes);
    require(bytes.length > 0 && bytes.length <= MAX && bytes[bytes.length - 1] == '\n');
    var canonical = new StringBuilder("NKJOURNAL1\n");
    int ordinal = 0;
    String text = decode(bytes);
    for (String line : text.substring(0, text.length() - 1).split("\n", -1)) {
      for (var entry : new TreeMap<>(fields(line)).entrySet()) {
        byte[] encoded;
        try {
          var buffer =
              StandardCharsets.UTF_8
                  .newEncoder()
                  .onMalformedInput(CodingErrorAction.REPORT)
                  .onUnmappableCharacter(CodingErrorAction.REPORT)
                  .encode(java.nio.CharBuffer.wrap(entry.getValue()));
          encoded = new byte[buffer.remaining()];
          buffer.get(encoded);
        } catch (CharacterCodingException malformed) {
          throw unavailable();
        }
        try {
          canonical
              .append("ROW|")
              .append(ordinal)
              .append('|')
              .append(entry.getKey())
              .append('|')
              .append(HexFormat.of().formatHex(encoded))
              .append('\n');
        } finally {
          Arrays.fill(encoded, (byte) 0);
        }
      }
      ordinal++;
    }
    byte[] actual = canonical.toString().getBytes(StandardCharsets.US_ASCII);
    try {
      return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(actual));
    } catch (NoSuchAlgorithmException known) {
      throw unavailable();
    } finally {
      Arrays.fill(actual, (byte) 0);
    }
  }

  /** SSC131 bounded metadata selector; raw journal fields never become public diagnostics. */
  record Anchor(String invocation, BigInteger monotonic, String cursor, String contentSha256) {
    @Override
    public String toString() {
      return "BrokerJournalAnchor[redacted]";
    }
  }

  static Anchor anchor(byte[] bytes, UUID boot, boolean requireStarted) throws IOException {
    Objects.requireNonNull(bytes);
    Objects.requireNonNull(boot);
    require(bytes.length > 0 && bytes.length <= 65536 && bytes[bytes.length - 1] == '\n');
    String text = decode(bytes);
    require(text.indexOf('\n') == text.length() - 1);
    var fields = fields(text.substring(0, text.length() - 1));
    require(boot.toString().replace("-", "").equals(fields.get("_BOOT_ID")));
    require("artemis.service".equals(fields.get("_SYSTEMD_UNIT")));
    String invocation = Objects.requireNonNull(fields.get("_SYSTEMD_INVOCATION_ID"));
    require(invocation.matches("[0-9a-f]{32}") && !invocation.equals("0".repeat(32)));
    String mono = Objects.requireNonNull(fields.get("__MONOTONIC_TIMESTAMP"));
    require(mono.matches("[1-9][0-9]{0,19}"));
    require(Objects.requireNonNull(fields.get("__REALTIME_TIMESTAMP")).matches("[1-9][0-9]{0,19}"));
    String cursor = Objects.requireNonNull(fields.get("__CURSOR"));
    require(!cursor.isEmpty());
    String message = Objects.requireNonNull(fields.get("MESSAGE"));
    require(Objects.requireNonNull(fields.get("PRIORITY")).matches("[4-7]"));
    require(!message.contains("AMQ224") && !message.matches("(?s).*\\b(ERROR|FATAL)\\b.*"));
    if (requireStarted)
      require(
          message.contains("AMQ221001: Apache Artemis Message Broker version 2.56.0")
              && message.contains("schubert-nk-broker"));
    return new Anchor(invocation, new BigInteger(mono), cursor, contentSha256(bytes));
  }

  static Summary consumeClosedHistory(byte[] bytes, UUID boot, Anchor latest) throws IOException {
    Objects.requireNonNull(latest);
    // There is no retained native ExecStart for a GC'd Unit. Check actual positive journal times,
    // not a fabricated native timestamp; the upper bound is the actual latest entry.
    var result =
        consume(bytes, boot, latest.invocation(), BigInteger.ONE, Optional.of(latest.monotonic()));
    consume(bytes, boot, latest.invocation(), BigInteger.ONE, Optional.empty());
    String text = decode(bytes);
    String lastLine = text.substring(0, text.length() - 1).split("\n", -1)[result.entries() - 1];
    var last = fields(lastLine);
    require(
        latest.cursor().equals(last.get("__CURSOR"))
            && latest.monotonic().toString().equals(last.get("__MONOTONIC_TIMESTAMP")));
    byte[] lastBytes = (lastLine + "\n").getBytes(StandardCharsets.UTF_8);
    try {
      require(latest.contentSha256().equals(contentSha256(lastBytes)));
    } finally {
      Arrays.fill(lastBytes, (byte) 0);
    }
    return result;
  }

  public static Summary inspect(
      MorningBrokerUnitCycle.Live actual, UUID boot, MaintenanceOwnerFrame.Guard parent)
      throws IOException {
    Objects.requireNonNull(actual);
    Objects.requireNonNull(boot);
    Objects.requireNonNull(parent);
    parent.check();
    actual.recheck();
    String invocation = actual.invocation();
    var command =
        List.of(
            "/usr/bin/journalctl",
            "--no-pager",
            "--quiet",
            "--all",
            "--output=json",
            "--output-fields=MESSAGE,PRIORITY,_SYSTEMD_INVOCATION_ID,_BOOT_ID,_SYSTEMD_UNIT",
            "_SYSTEMD_UNIT=artemis.service",
            "_SYSTEMD_INVOCATION_ID=" + invocation,
            "_BOOT_ID=" + boot.toString().replace("-", ""));
    byte[] bytes =
        InspectorUnitProbe.NativeReader.forTarget(InspectorUnitSnapshot.Target.ARTEMIS)
            .executeStreaming(command, MAX, parent.remainingNanos());
    try {
      Summary result = consume(bytes, boot, invocation, actual.startedMonotonicMicros());
      actual.recheck();
      parent.check();
      return result;
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  /** Data-only independent parser PT; ownership and native identity stay at inspect's caller. */
  static Summary consume(byte[] bytes, UUID boot, String invocation, BigInteger began)
      throws IOException {
    return consume(bytes, boot, invocation, began, Optional.empty());
  }

  /** Same owned stopped target; the native caller independently rechecks all kernels/manager. */
  static Summary inspectStopped(
      InspectorUnitSnapshot actual, UUID boot, MaintenanceOwnerFrame.Guard parent)
      throws IOException {
    Objects.requireNonNull(actual);
    Objects.requireNonNull(boot);
    Objects.requireNonNull(parent);
    require(actual.brokerStoppedNormally());
    parent.check();
    String invocation = actual.invocationId().orElseThrow().toString().replace("-", "");
    byte[] bytes =
        InspectorUnitProbe.NativeReader.forTarget(InspectorUnitSnapshot.Target.ARTEMIS)
            .executeStreaming(
                List.of(
                    "/usr/bin/journalctl",
                    "--no-pager",
                    "--quiet",
                    "--all",
                    "--output=json",
                    "--output-fields=MESSAGE,PRIORITY,_SYSTEMD_INVOCATION_ID,_BOOT_ID,_SYSTEMD_UNIT",
                    "_SYSTEMD_UNIT=artemis.service",
                    "_SYSTEMD_INVOCATION_ID=" + invocation,
                    "_BOOT_ID=" + boot.toString().replace("-", "")),
                MAX,
                parent.remainingNanos());
    try {
      var result =
          consumeStopped(bytes, boot, invocation, actual.executionStart(), actual.executionEnd());
      parent.check();
      return result;
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  static Summary consumeStopped(
      byte[] bytes, UUID boot, String invocation, BigInteger began, BigInteger ended)
      throws IOException {
    Objects.requireNonNull(ended);
    require(ended.compareTo(began) >= 0);
    return consume(bytes, boot, invocation, began, Optional.of(ended));
  }

  private static Summary consume(
      byte[] bytes, UUID boot, String invocation, BigInteger began, Optional<BigInteger> stopEnd)
      throws IOException {
    Objects.requireNonNull(bytes);
    Objects.requireNonNull(boot);
    Objects.requireNonNull(invocation);
    Objects.requireNonNull(began);
    require(bytes.length > 0 && bytes.length <= MAX && bytes[bytes.length - 1] == '\n');
    String text = decode(bytes);
    boolean nio = false;
    boolean active = false;
    boolean started = false;
    boolean stopped = false;
    int count = 0;
    var cursors = new HashSet<String>();
    for (String line : text.substring(0, text.length() - 1).split("\n", -1)) {
      var fields = fields(line);
      require(
          boot.toString().replace("-", "").equals(fields.get("_BOOT_ID"))
              && invocation.equals(fields.get("_SYSTEMD_INVOCATION_ID"))
              && "artemis.service".equals(fields.get("_SYSTEMD_UNIT")));
      require(Objects.requireNonNull(fields.get("PRIORITY")).matches("[4-7]"));
      String cursor = Objects.requireNonNull(fields.get("__CURSOR"));
      require(!cursor.isEmpty() && cursors.add(cursor));
      String monotonic = Objects.requireNonNull(fields.get("__MONOTONIC_TIMESTAMP"));
      require(
          monotonic.matches("[1-9][0-9]{0,19}") && new BigInteger(monotonic).compareTo(began) >= 0);
      if (stopEnd.isPresent())
        require(new BigInteger(monotonic).compareTo(stopEnd.orElseThrow()) <= 0);
      require(
          Objects.requireNonNull(fields.get("__REALTIME_TIMESTAMP")).matches("[1-9][0-9]{0,19}"));
      String message = Objects.requireNonNull(fields.get("MESSAGE"));
      require(!message.contains("AMQ224") && !message.matches("(?s).*\\b(ERROR|FATAL)\\b.*"));
      nio |= message.contains("AMQ221013: Using NIO Journal");
      active |= message.contains("AMQ221007: Server is now active");
      started |=
          message.contains("AMQ221001: Apache Artemis Message Broker version 2.56.0")
              && message.contains("schubert-nk-broker");
      stopped |=
          message.contains("AMQ221002: Apache Artemis Message Broker version 2.56.0")
              && message.contains(" stopped, uptime ");
      count++;
    }
    if (stopEnd.isPresent()) require(stopped);
    else require(nio && active && started);
    try {
      return new Summary(
          count, HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes)));
    } catch (NoSuchAlgorithmException unavailable) {
      throw unavailable();
    }
  }

  private static void require(boolean accepted) throws IOException {
    if (!accepted) throw unavailable();
  }

  private static String decode(byte[] bytes) throws IOException {
    try {
      return StandardCharsets.UTF_8
          .newDecoder()
          .onMalformedInput(CodingErrorAction.REPORT)
          .onUnmappableCharacter(CodingErrorAction.REPORT)
          .decode(java.nio.ByteBuffer.wrap(bytes))
          .toString();
    } catch (CharacterCodingException known) {
      throw unavailable();
    }
  }

  private static Map<String, String> fields(String line) throws IOException {
    var fields = new HashMap<String, String>();
    try (var reader = new JsonReader(new StringReader(line))) {
      reader.setStrictness(Strictness.STRICT);
      reader.beginObject();
      while (reader.hasNext()) {
        String key = reader.nextName();
        require(REQUIRED.contains(key) || OPTIONAL.contains(key));
        require(reader.peek() == JsonToken.STRING);
        require(fields.putIfAbsent(key, reader.nextString()) == null);
      }
      reader.endObject();
      // Pinned STRICT JsonReader: after endObject, peek either validates EOF or throws.
      // Keep this mandatory trailing-data read; do not switch to LENIENT or skip peek.
      reader.peek();
    } catch (IllegalStateException known) {
      throw unavailable();
    }
    require(fields.keySet().containsAll(REQUIRED));
    return fields;
  }

  private static IOException unavailable() {
    return new IOException("Broker journal evidence unavailable");
  }
}

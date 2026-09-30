package dev.codex.schubert.nk.batch.platform;

import com.google.gson.Strictness;
import com.google.gson.stream.*;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.*;
import java.math.BigInteger;
import java.nio.charset.*;
import java.security.*;
import java.util.*;
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
    String text;
    try {
      text =
          StandardCharsets.UTF_8
              .newDecoder()
              .onMalformedInput(CodingErrorAction.REPORT)
              .onUnmappableCharacter(CodingErrorAction.REPORT)
              .decode(java.nio.ByteBuffer.wrap(bytes))
              .toString();
    } catch (CharacterCodingException known) {
      throw unavailable();
    }
    boolean nio = false, active = false, started = false, stopped = false;
    int count = 0;
    var cursors = new HashSet<String>();
    for (String line : text.substring(0, text.length() - 1).split("\n", -1)) {
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
        require(reader.peek() == JsonToken.END_DOCUMENT);
      } catch (IllegalStateException known) {
        throw unavailable();
      }
      require(fields.keySet().containsAll(REQUIRED));
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

  private static IOException unavailable() {
    return new IOException("Broker journal evidence unavailable");
  }
}

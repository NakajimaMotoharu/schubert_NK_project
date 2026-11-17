package dev.codex.schubert.nk.batch.platform;

import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Objects;
import java.util.Set;
import org.jspecify.annotations.NullMarked;

/**
 * Exact bounded state projection, not a lease. NK-OPS-001; UI251; SS341/343; PT-OPS-STOP-001..004.
 */
@NullMarked
final class UnitStateParser {
  private static final Set<String> KEYS =
      Set.of("Id", "LoadState", "ActiveState", "SubState", "Job", "MainPID", "ControlPID");

  private UnitStateParser() {
    throw new AssertionError("static namespace");
  }

  static void requireStopped(ApplicationUnit expected, byte[] bytes) {
    Objects.requireNonNull(expected, "unit");
    Objects.requireNonNull(bytes, "state");
    valid(bytes.length > 0 && bytes.length <= 1024);
    for (byte value : bytes) valid(value == '\n' || (value >= 32 && value <= 126));
    String text = new String(bytes, StandardCharsets.US_ASCII);
    valid(text.endsWith("\n"));
    String[] lines = text.split("\n", -1);
    valid(lines.length == 8);
    var fields = new HashMap<String, String>();
    for (int i = 0; i < 7; i++) {
      String line = lines[i];
      int equals = line.indexOf('=');
      valid(equals > 0 && equals == line.lastIndexOf('='));
      valid(fields.putIfAbsent(line.substring(0, equals), line.substring(equals + 1)) == null);
    }
    valid(fields.keySet().equals(KEYS));
    valid(expected.serviceName().equals(fields.get("Id")));
    if (!"loaded".equals(fields.get("LoadState"))
        || !"inactive".equals(fields.get("ActiveState"))
        || !"dead".equals(fields.get("SubState"))
        || !"".equals(fields.get("Job"))
        || !"0".equals(fields.get("MainPID"))
        || !"0".equals(fields.get("ControlPID")))
      throw new StopGateException(StopGateFailure.NOT_STOPPED);
  }

  private static void valid(boolean accepted) {
    if (!accepted) throw new StopGateException(StopGateFailure.MALFORMED_STATE);
  }
}

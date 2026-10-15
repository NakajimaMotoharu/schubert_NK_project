package dev.codex.schubert.nk.batch.platform;

import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import org.jspecify.annotations.NullMarked;

/**
 * Parent-only necessary terminal observation, NOT a lease, whole-cgroup proof or clean-stop
 * receipt. NK-OPS-001/SYS002/004/OPS009/AVL/UI251/253/SS3415/343/SSC100; MSTOP001..007. Caller
 * additionally owns continuous M/A, fixed stop policy, genuine kernel and all owner closes.
 */
@NullMarked
public final class MaintenanceStopSnapshot {
  static final String PROPERTIES =
      "Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,Slice,Delegate,ControlGroup,"
          + "InvocationID,StateChangeTimestampMonotonic";
  private static final Set<String> KEYS = Set.copyOf(List.of(PROPERTIES.split(",")));
  private static final BigInteger U32 = new BigInteger("4294967295");
  private static final BigInteger U64 = new BigInteger("18446744073709551615");
  private final MaintenanceUnit retainedUnit;
  private final Map<String, String> fields;

  private MaintenanceStopSnapshot(MaintenanceUnit unit, Map<String, String> fields) {
    this.retainedUnit = unit;
    this.fields = Map.copyOf(fields);
  }

  public static MaintenanceStopSnapshot parse(MaintenanceUnit unit, byte[] input) {
    Objects.requireNonNull(unit, "fixed Unit");
    Objects.requireNonNull(input, "terminal projection");
    require(input.length > 0 && input.length <= 2048);
    byte[] copy = input.clone();
    try {
      for (byte value : copy) require(value == 10 || (value >= 32 && value <= 126));
      String[] lines = new String(copy, StandardCharsets.US_ASCII).split("\n", -1);
      require(lines.length == 13 && lines[12].isEmpty());
      Map<String, String> fields = new HashMap<>();
      for (int i = 0; i < 12; i++) {
        int separator = lines[i].indexOf('=');
        require(separator > 0 && separator == lines[i].lastIndexOf('='));
        String key = lines[i].substring(0, separator);
        require(KEYS.contains(key));
        require(fields.putIfAbsent(key, lines[i].substring(separator + 1)) == null);
      }
      // Exactly twelve unique keys from the closed twelve-key set establishes completeness.
      require(unit.serviceName().equals(fields.get("Id")));
      require("loaded".equals(fields.get("LoadState")));
      require("system.slice".equals(fields.get("Slice")));
      require("no".equals(fields.get("Delegate")));
      var result = new MaintenanceStopSnapshot(unit, fields);
      require(result.controlGroup().isEmpty() || unit.controlGroup().equals(result.controlGroup()));
      for (String key : List.of("ActiveState", "SubState"))
        require(result.value(key).matches("[a-z][a-z0-9-]{0,63}"));
      String job = result.value("Job");
      if (!job.isEmpty()) require(number(job, U32).signum() > 0);
      number(result.value("MainPID"), U32);
      number(result.value("ControlPID"), U32);
      number(result.value("StateChangeTimestampMonotonic"), U64);
      String invocation = result.value("InvocationID");
      require(
          invocation.isEmpty()
              || (invocation.matches("[0-9a-f]{32}") && !invocation.equals("0".repeat(32))));
      return result;
    } finally {
      Arrays.fill(copy, (byte) 0);
    }
  }

  public MaintenanceUnit unit() {
    return retainedUnit;
  }

  public String controlGroup() {
    return value("ControlGroup");
  }

  /**
   * SSC126: original twelve observed values in the SS fixed property order, never claimed state.
   */
  public List<String> observedValues() {
    return Arrays.stream(PROPERTIES.split(",")).map(this::value).toList();
  }

  /** Necessary state only; active/exited is not an explicit parent stop completion. */
  public boolean quiescent() {
    return value("Job").isEmpty()
        && value("MainPID").equals("0")
        && value("ControlPID").equals("0")
        && Set.of("inactive/dead", "failed/failed")
            .contains(value("ActiveState") + "/" + value("SubState"));
  }

  public boolean matches(MaintenanceStopSnapshot other) {
    Objects.requireNonNull(other, "terminal observation");
    return retainedUnit == other.retainedUnit && fields.equals(other.fields);
  }

  @Override
  public String toString() {
    return "MaintenanceStopSnapshot[redacted]";
  }

  private String value(String key) {
    return Objects.requireNonNull(fields.get(key), "fixed field");
  }

  private static BigInteger number(String text, BigInteger maximum) {
    require(text.matches("0|[1-9][0-9]{0,19}"));
    BigInteger number = new BigInteger(text);
    require(number.compareTo(maximum) <= 0);
    return number;
  }

  private static void require(boolean accepted) {
    if (!accepted) throw new StopGateException(StopGateFailure.MALFORMED_STATE);
  }
}

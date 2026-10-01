package dev.codex.schubert.nk.batch.platform;

import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/**
 * Immutable observation, not process ownership or startup authorization.
 * NK-OPS-001/OPS009/UI251/SS341 7.4/343; SSC060/PG167; UNIT001..008.
 */
@NullMarked
public final class InspectorUnitSnapshot {
  /** Fixed maintenance targets only; no arbitrary Unit string. */
  public enum Target {
    INSPECTOR("schubert-nk-inbox-inspector.service"),
    BACKUP("schubert-nk-backup.service"),
    CLEANUP("schubert-nk-cleanup.service"),
    EXPIRY("schubert-nk-expiry-cleanup.service"),
    ARTEMIS("artemis.service"),
    MORNING("schubert-nk-morning-controller.service"),
    API("schubert-nk-api.service"),
    WEB("schubert-nk-web.service");
    private final String unit;

    Target(String unit) {
      this.unit = unit;
    }

    public String unit() {
      return unit;
    }
  }

  static final String UNIT = "schubert-nk-inbox-inspector.service";
  static final String PROPERTIES =
      "Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,InvocationID,"
          + "ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic,"
          + "Result,Type,Restart,RemainAfterExit,KillMode,SendSIGKILL";
  private static final Set<String> KEYS = Set.copyOf(List.of(PROPERTIES.split(",")));
  private static final BigInteger U32 = new BigInteger("4294967295");
  private static final BigInteger U64 = new BigInteger("18446744073709551615");
  private final Map<String, String> values;
  private final Target target;

  private InspectorUnitSnapshot(Map<String, String> values, Target target) {
    this.values = Map.copyOf(values);
    this.target = target;
  }

  public static InspectorUnitSnapshot parse(byte[] input) {
    return parse(input, Target.INSPECTOR);
  }

  public static InspectorUnitSnapshot parse(byte[] input, Target target) {
    Objects.requireNonNull(target, "fixed Unit target");
    Objects.requireNonNull(input, "unit state bytes");
    require(input.length > 0 && input.length <= 2048);
    byte[] copy = input.clone();
    try {
      for (byte value : copy) require(value == 10 || (value >= 32 && value <= 126));
      String[] lines = new String(copy, StandardCharsets.US_ASCII).split("\n", -1);
      require(lines.length == 19 && lines[18].isEmpty());
      Map<String, String> fields = new HashMap<>();
      for (int i = 0; i < 18; i++) {
        int separator = lines[i].indexOf('=');
        require(separator > 0);
        String key = lines[i].substring(0, separator);
        String value = lines[i].substring(separator + 1);
        require(KEYS.contains(key) && fields.putIfAbsent(key, value) == null);
      }
      var result = new InspectorUnitSnapshot(fields, target);
      require(result.value("Id").equals(target.unit()));
      for (var fixed :
          Map.of(
                  "LoadState",
                  "loaded",
                  "Type",
                  target == Target.ARTEMIS || target == Target.API || target == Target.WEB
                      ? "simple"
                      : "oneshot",
                  "Restart",
                  target == Target.ARTEMIS || target == Target.API || target == Target.WEB
                      ? "on-failure"
                      : "no",
                  "KillMode",
                  "control-group",
                  "SendSIGKILL",
                  "no")
              .entrySet()) require(result.value(fixed.getKey()).equals(fixed.getValue()));
      require(Set.of("yes", "no").contains(result.value("RemainAfterExit")));
      if (target == Target.ARTEMIS
          || target == Target.MORNING
          || target == Target.API
          || target == Target.WEB) require(result.value("RemainAfterExit").equals("no"));
      if (target == Target.BACKUP || target == Target.CLEANUP)
        require(result.value("RemainAfterExit").equals("yes"));
      for (String token : List.of("ActiveState", "SubState", "Result"))
        require(result.value(token).matches("[a-z][a-z0-9-]{0,63}"));
      String job = result.value("Job");
      if (!job.isEmpty()) require(number(job, U32).signum() > 0);
      number(result.value("MainPID"), U32);
      number(result.value("ControlPID"), U32);
      number(result.value("ExecMainCode"), BigInteger.valueOf(6));
      number(result.value("ExecMainStatus"), BigInteger.valueOf(255));
      number(result.value("ExecMainStartTimestampMonotonic"), U64);
      number(result.value("ExecMainExitTimestampMonotonic"), U64);
      String id = result.value("InvocationID");
      if (!id.isEmpty()) require(id.matches("[0-9a-f]{32}") && !id.equals("0".repeat(32)));
      return result;
    } finally {
      Arrays.fill(copy, (byte) 0);
    }
  }

  public Optional<UUID> invocationId() {
    String id = value("InvocationID");
    if (id.isEmpty()) return Optional.empty();
    return Optional.of(
        new UUID(
            Long.parseUnsignedLong(id.substring(0, 16), 16),
            Long.parseUnsignedLong(id.substring(16), 16)));
  }

  /**
   * Necessary unit state only. Probe must also establish empty processes and stable observations.
   */
  public boolean quiescent() {
    return value("Job").isEmpty()
        && value("MainPID").equals("0")
        && value("ControlPID").equals("0")
        && Set.of("inactive/dead", "active/exited", "failed/failed")
            .contains(value("ActiveState") + "/" + value("SubState"));
  }

  /** Values alone never certify that startup was requested by the current parent/run. */
  public OptionalInt receiptAfter(Optional<UUID> previous) {
    Objects.requireNonNull(previous, "previous invocation");
    if (target == Target.ARTEMIS
        || target == Target.MORNING
        || target == Target.API
        || target == Target.WEB)
      return OptionalInt.empty(); // A daemon stop is not worker completion.
    var current = invocationId();
    if (!quiescent()
        || current.isEmpty()
        || current.equals(previous)
        || value("ActiveState").equals("failed")
        || !value("Result").equals("success")
        || !value("ExecMainCode").equals("1")) return OptionalInt.empty();
    BigInteger start = new BigInteger(value("ExecMainStartTimestampMonotonic"));
    BigInteger end = new BigInteger(value("ExecMainExitTimestampMonotonic"));
    if (start.signum() == 0 || end.compareTo(start) < 0) return OptionalInt.empty();
    String status = value("ExecMainStatus");
    return status.equals("0")
        ? OptionalInt.of(0)
        : status.equals("10")
                && (target == Target.INSPECTOR
                    || target == Target.CLEANUP
                    || target == Target.EXPIRY)
            ? OptionalInt.of(10)
            : OptionalInt.empty();
  }

  /** SSC144 failed generation data only; independently requires full kernel/M/A/original proof. */
  public boolean failedRootGeneration(String invocation) {
    Objects.requireNonNull(invocation);
    return (target == Target.MORNING || target == Target.API || target == Target.WEB)
        && quiescent()
        && value("InvocationID").equals(invocation)
        && invocationId().isPresent()
        && value("Result").equals("exit-code")
        && value("ExecMainCode").equals("1")
        && value("ExecMainStatus").equals("30")
        && executionStart().signum() > 0
        && executionEnd().compareTo(executionStart()) >= 0;
  }

  /** Current normal stop recheck of a captured failed Root/parent, never success authority. */
  public boolean failedRootStillStoppedAfter(InspectorUnitSnapshot before) {
    Objects.requireNonNull(before);
    return target == before.target
        && before.failedRootGeneration(before.value("InvocationID"))
        && quiescent()
        && sameStoppedExecution(before);
  }

  /** Backup only: a fresh normal nonzero exit is failure, never an unknown/signal success. */
  public Optional<MorningBackupUnitCycle.Outcome> backupTerminalAfter(Optional<UUID> previous) {
    Objects.requireNonNull(previous, "previous invocation");
    if (target != Target.BACKUP
        || !quiescent()
        || invocationId().isEmpty()
        || invocationId().equals(previous)
        || !value("ExecMainCode").equals("1")) return Optional.empty();
    BigInteger start = new BigInteger(value("ExecMainStartTimestampMonotonic"));
    BigInteger end = new BigInteger(value("ExecMainExitTimestampMonotonic"));
    if (start.signum() == 0 || end.compareTo(start) < 0) return Optional.empty();
    if (receiptAfter(previous).orElse(-1) == 0)
      return Optional.of(MorningBackupUnitCycle.Outcome.SUCCESS);
    if (value("ActiveState").equals("failed")
        && value("SubState").equals("failed")
        && value("Result").equals("exit-code")
        && !value("ExecMainStatus").equals("0"))
      return Optional.of(MorningBackupUnitCycle.Outcome.FAILED);
    return Optional.empty();
  }

  /** SSC120: narrow known Cleanup rejection, never a success receipt or UNKNOWN repair. */
  boolean cleanupRejectedAfter(Optional<UUID> previous) {
    return normalRejectedAfter(Target.CLEANUP, previous);
  }

  boolean expiryRejectedAfter(Optional<UUID> previous) {
    return normalRejectedAfter(Target.EXPIRY, previous);
  }

  private boolean normalRejectedAfter(Target expected, Optional<UUID> previous) {
    Objects.requireNonNull(previous, "previous invocation");
    return target == expected
        && value("RemainAfterExit").equals("yes")
        && quiescent()
        && invocationId().isPresent()
        && !invocationId().equals(previous)
        && value("ActiveState").equals("failed")
        && value("SubState").equals("failed")
        && value("Result").equals("exit-code")
        && value("ExecMainCode").equals("1")
        && value("ExecMainStatus").equals("30")
        && executionStart().signum() > 0
        && executionEnd().compareTo(executionStart()) >= 0;
  }

  /** Necessary worker-self binding only; independent kernel/NSS/namespace gates remain required. */
  public boolean running(long pid, String invocation) {
    Objects.requireNonNull(invocation, "manager invocation");
    if (target == Target.ARTEMIS)
      return value("MainPID").equals(Long.toString(pid)) && brokerRunningInvocation(invocation);
    return pid >= 2
        && pid <= Integer.MAX_VALUE
        && value("MainPID").equals(Long.toString(pid))
        && value("ControlPID").equals("0")
        && value("InvocationID").equals(invocation)
        && new BigInteger(value("ExecMainStartTimestampMonotonic")).signum() > 0
        && value("ActiveState").equals("activating")
        && value("SubState").equals("start");
  }

  public boolean runningInvocation(String invocation) {
    Objects.requireNonNull(invocation, "expected manager Invocation");
    return running(Long.parseLong(value("MainPID")), invocation);
  }

  /** SSC125/BROKERLIVE001..004: data only, never Ops/journal/root/permit authority. */
  public boolean brokerRunningInvocation(String invocation) {
    Objects.requireNonNull(invocation, "same actual broker invocation");
    return target == Target.ARTEMIS
        && value("ActiveState").equals("active")
        && value("SubState").equals("running")
        && value("Job").isEmpty()
        && new BigInteger(value("MainPID")).compareTo(BigInteger.valueOf(2)) >= 0
        && new BigInteger(value("MainPID")).compareTo(BigInteger.valueOf(Integer.MAX_VALUE)) <= 0
        && value("ControlPID").equals("0")
        && invocationId().isPresent()
        && value("InvocationID").equals(invocation)
        && executionStart().signum() > 0
        && executionEnd().signum() == 0
        && value("ExecMainCode").equals("0")
        && value("ExecMainStatus").equals("0")
        && value("Result").equals("success");
  }

  public boolean matches(InspectorUnitSnapshot other) {
    return values.equals(Objects.requireNonNull(other, "unit snapshot").values);
  }

  @Override
  public String toString() {
    return "InspectorUnitSnapshot[redacted]";
  }

  private String value(String name) {
    return Objects.requireNonNull(values.get(name));
  }

  /** Package claims only; genuine gate/owner/freshness remain mandatory. */
  int normalExitCode() {
    require(value("ExecMainCode").equals("1"));
    return Integer.parseInt(value("ExecMainStatus"));
  }

  BigInteger executionStart() {
    return new BigInteger(value("ExecMainStartTimestampMonotonic"));
  }

  BigInteger executionEnd() {
    return new BigInteger(value("ExecMainExitTimestampMonotonic"));
  }

  /** SSC135: complete manager GC only, never an execution result or receipt zero. */
  boolean coldStopped() {
    return inactiveBaseline()
        && value("InvocationID").isEmpty()
        && value("ExecMainCode").equals("0")
        && value("ExecMainStatus").equals("0")
        && value("ExecMainStartTimestampMonotonic").equals("0")
        && value("ExecMainExitTimestampMonotonic").equals("0")
        && value("Result").equals("success");
  }

  /** Same five real execution values despite the legitimate stop state transition. */
  boolean sameStoppedExecution(InspectorUnitSnapshot before) {
    return Set.of("inactive/dead", "failed/failed")
            .contains(value("ActiveState") + "/" + value("SubState"))
        && Set.of("success", "exit-code").contains(value("Result"))
        && value("ExecMainCode").equals("1")
        && value("InvocationID").equals(before.value("InvocationID"))
        && value("ExecMainStatus").equals(before.value("ExecMainStatus"))
        && value("ExecMainStartTimestampMonotonic")
            .equals(before.value("ExecMainStartTimestampMonotonic"))
        && value("ExecMainExitTimestampMonotonic")
            .equals(before.value("ExecMainExitTimestampMonotonic"));
  }

  boolean inactiveBaseline() {
    return value("ActiveState").equals("inactive")
        && value("SubState").equals("dead")
        && (target != Target.INSPECTOR || value("RemainAfterExit").equals("yes"))
        && quiescent();
  }

  /** SSC127: old normal stop data only, NEVER a fresh worker receipt or journal proof. */
  boolean brokerStoppedNormally() {
    return target == Target.ARTEMIS
        && quiescent()
        && invocationId().isPresent()
        && value("ExecMainCode").equals("1")
        && value("ExecMainStatus").equals("143")
        && executionStart().signum() > 0
        && executionEnd().compareTo(executionStart()) >= 0
        && ((value("ActiveState").equals("failed")
                && value("SubState").equals("failed")
                && value("Result").equals("exit-code"))
            || (value("ActiveState").equals("inactive")
                && value("SubState").equals("dead")
                && value("Result").equals("success")));
  }

  boolean heldCleanup() {
    return target == Target.CLEANUP
        && value("ActiveState").equals("active")
        && value("SubState").equals("exited")
        && quiescent();
  }

  boolean heldMaintenance() {
    return (target == Target.CLEANUP || target == Target.INSPECTOR || target == Target.EXPIRY)
        && value("RemainAfterExit").equals("yes")
        && value("ActiveState").equals("active")
        && value("SubState").equals("exited")
        && quiescent();
  }

  boolean isTarget(Target expected) {
    return target == expected;
  }

  private static BigInteger number(String text, BigInteger maximum) {
    require(text.matches("0|[1-9][0-9]{0,19}"));
    BigInteger value = new BigInteger(text);
    require(value.compareTo(maximum) <= 0);
    return value;
  }

  private static void require(boolean valid) {
    if (!valid) throw new StopGateException(StopGateFailure.MALFORMED_STATE);
  }
}

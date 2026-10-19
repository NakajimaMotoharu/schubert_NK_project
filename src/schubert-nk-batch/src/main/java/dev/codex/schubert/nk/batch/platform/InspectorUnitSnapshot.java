package dev.codex.schubert.nk.batch.platform;

import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalInt;
import java.util.Set;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * Immutable observation, not process ownership or startup authorization.
 * NK-OPS-001/OPS009/UI251/SS341 7.4/343; SSC060/PG167; UNIT001..008.
 */
@NullMarked
public final class InspectorUnitSnapshot {
  private static final java.lang.String LITERAL_YES = "yes";

  private static final java.lang.String LITERAL_REMAINAFTEREXIT = "RemainAfterExit";

  private static final java.lang.String LITERAL_ACTIVESTATE = "ActiveState";

  private static final java.lang.String LITERAL_SUBSTATE = "SubState";

  private static final java.lang.String LITERAL_RESULT = "Result";

  private static final java.lang.String LITERAL_MAINPID = "MainPID";

  private static final java.lang.String LITERAL_CONTROLPID = "ControlPID";

  private static final java.lang.String LITERAL_EXECMAINCODE = "ExecMainCode";

  private static final java.lang.String LITERAL_EXECMAINSTATUS = "ExecMainStatus";

  private static final java.lang.String LITERAL_EXECMAINSTARTTIMESTAMPMONOTONIC =
      "ExecMainStartTimestampMonotonic";

  private static final java.lang.String LITERAL_EXECMAINEXITTIMESTAMPMONOTONIC =
      "ExecMainExitTimestampMonotonic";

  private static final java.lang.String LITERAL_INVOCATIONID = "InvocationID";

  private static final java.lang.String LITERAL_FAILED = "failed";

  private static final java.lang.String LITERAL_SUCCESS = "success";

  private static final java.lang.String LITERAL_EXIT_CODE = "exit-code";

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
    private final String systemUnit;

    Target(String unit) {
      this.systemUnit = unit;
    }

    public String unit() {
      return systemUnit;
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
      require(Set.of(LITERAL_YES, "no").contains(result.value(LITERAL_REMAINAFTEREXIT)));
      if (target == Target.ARTEMIS
          || target == Target.MORNING
          || target == Target.API
          || target == Target.WEB) require(result.value(LITERAL_REMAINAFTEREXIT).equals("no"));
      if (target == Target.BACKUP || target == Target.CLEANUP)
        require(result.value(LITERAL_REMAINAFTEREXIT).equals(LITERAL_YES));
      for (String token : List.of(LITERAL_ACTIVESTATE, LITERAL_SUBSTATE, LITERAL_RESULT))
        require(result.value(token).matches("[a-z][a-z0-9-]{0,63}"));
      String job = result.value("Job");
      if (!job.isEmpty()) require(number(job, U32).signum() > 0);
      number(result.value(LITERAL_MAINPID), U32);
      number(result.value(LITERAL_CONTROLPID), U32);
      number(result.value(LITERAL_EXECMAINCODE), BigInteger.valueOf(6));
      number(result.value(LITERAL_EXECMAINSTATUS), BigInteger.valueOf(255));
      number(result.value(LITERAL_EXECMAINSTARTTIMESTAMPMONOTONIC), U64);
      number(result.value(LITERAL_EXECMAINEXITTIMESTAMPMONOTONIC), U64);
      String id = result.value(LITERAL_INVOCATIONID);
      if (!id.isEmpty()) require(id.matches("[0-9a-f]{32}") && !id.equals("0".repeat(32)));
      return result;
    } finally {
      Arrays.fill(copy, (byte) 0);
    }
  }

  public Optional<UUID> invocationId() {
    String id = value(LITERAL_INVOCATIONID);
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
        && value(LITERAL_MAINPID).equals("0")
        && value(LITERAL_CONTROLPID).equals("0")
        && Set.of("inactive/dead", "active/exited", "failed/failed")
            .contains(value(LITERAL_ACTIVESTATE) + "/" + value(LITERAL_SUBSTATE));
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
        || value(LITERAL_ACTIVESTATE).equals(LITERAL_FAILED)
        || !value(LITERAL_RESULT).equals(LITERAL_SUCCESS)
        || !value(LITERAL_EXECMAINCODE).equals("1")) return OptionalInt.empty();
    BigInteger start = new BigInteger(value(LITERAL_EXECMAINSTARTTIMESTAMPMONOTONIC));
    BigInteger end = new BigInteger(value(LITERAL_EXECMAINEXITTIMESTAMPMONOTONIC));
    if (start.signum() == 0 || end.compareTo(start) < 0) return OptionalInt.empty();
    String status = value(LITERAL_EXECMAINSTATUS);
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
        && value(LITERAL_INVOCATIONID).equals(invocation)
        && invocationId().isPresent()
        && value(LITERAL_RESULT).equals(LITERAL_EXIT_CODE)
        && value(LITERAL_EXECMAINCODE).equals("1")
        && value(LITERAL_EXECMAINSTATUS).equals("30")
        && executionStart().signum() > 0
        && executionEnd().compareTo(executionStart()) >= 0;
  }

  /** Current normal stop recheck of a captured failed Root/parent, never success authority. */
  public boolean failedRootStillStoppedAfter(InspectorUnitSnapshot before) {
    Objects.requireNonNull(before);
    return target == before.target
        && before.failedRootGeneration(before.value(LITERAL_INVOCATIONID))
        && quiescent()
        && (sameStoppedExecution(before) || coldStopped());
  }

  /** Backup only: a fresh normal nonzero exit is failure, never an unknown/signal success. */
  public Optional<MorningBackupUnitCycle.Outcome> backupTerminalAfter(Optional<UUID> previous) {
    Objects.requireNonNull(previous, "previous invocation");
    if (target != Target.BACKUP
        || !quiescent()
        || invocationId().isEmpty()
        || invocationId().equals(previous)
        || !value(LITERAL_EXECMAINCODE).equals("1")) return Optional.empty();
    BigInteger start = new BigInteger(value(LITERAL_EXECMAINSTARTTIMESTAMPMONOTONIC));
    BigInteger end = new BigInteger(value(LITERAL_EXECMAINEXITTIMESTAMPMONOTONIC));
    if (start.signum() == 0 || end.compareTo(start) < 0) return Optional.empty();
    if (receiptAfter(previous).orElse(-1) == 0)
      return Optional.of(MorningBackupUnitCycle.Outcome.SUCCESS);
    if (value(LITERAL_ACTIVESTATE).equals(LITERAL_FAILED)
        && value(LITERAL_RESULT).equals(LITERAL_EXIT_CODE)
        && !value(LITERAL_EXECMAINSTATUS).equals("0"))
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
        && value(LITERAL_REMAINAFTEREXIT).equals(LITERAL_YES)
        && quiescent()
        && invocationId().isPresent()
        && !invocationId().equals(previous)
        && value(LITERAL_ACTIVESTATE).equals(LITERAL_FAILED)
        && value(LITERAL_RESULT).equals(LITERAL_EXIT_CODE)
        && value(LITERAL_EXECMAINCODE).equals("1")
        && value(LITERAL_EXECMAINSTATUS).equals("30")
        && executionStart().signum() > 0
        && executionEnd().compareTo(executionStart()) >= 0;
  }

  /** Necessary worker-self binding only; independent kernel/NSS/namespace gates remain required. */
  public boolean running(long pid, String invocation) {
    Objects.requireNonNull(invocation, "manager invocation");
    if (target == Target.ARTEMIS)
      return value(LITERAL_MAINPID).equals(Long.toString(pid))
          && brokerRunningInvocation(invocation);
    return pid >= 2
        && pid <= Integer.MAX_VALUE
        && value(LITERAL_MAINPID).equals(Long.toString(pid))
        && value(LITERAL_CONTROLPID).equals("0")
        && value(LITERAL_INVOCATIONID).equals(invocation)
        && new BigInteger(value(LITERAL_EXECMAINSTARTTIMESTAMPMONOTONIC)).signum() > 0
        && value(LITERAL_ACTIVESTATE).equals("activating")
        && value(LITERAL_SUBSTATE).equals("start");
  }

  public boolean runningInvocation(String invocation) {
    Objects.requireNonNull(invocation, "expected manager Invocation");
    return running(Long.parseLong(value(LITERAL_MAINPID)), invocation);
  }

  /** SSC125/BROKERLIVE001..004: data only, never Ops/journal/root/permit authority. */
  public boolean brokerRunningInvocation(String invocation) {
    Objects.requireNonNull(invocation, "same actual broker invocation");
    return target == Target.ARTEMIS
        && value(LITERAL_ACTIVESTATE).equals("active")
        && value(LITERAL_SUBSTATE).equals("running")
        && value("Job").isEmpty()
        && new BigInteger(value(LITERAL_MAINPID)).compareTo(BigInteger.valueOf(2)) >= 0
        && new BigInteger(value(LITERAL_MAINPID)).compareTo(BigInteger.valueOf(Integer.MAX_VALUE))
            <= 0
        && value(LITERAL_CONTROLPID).equals("0")
        && invocationId().isPresent()
        && value(LITERAL_INVOCATIONID).equals(invocation)
        && executionStart().signum() > 0
        && executionEnd().signum() == 0
        && value(LITERAL_EXECMAINCODE).equals("0")
        && value(LITERAL_EXECMAINSTATUS).equals("0")
        && value(LITERAL_RESULT).equals(LITERAL_SUCCESS);
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
    require(value(LITERAL_EXECMAINCODE).equals("1"));
    return Integer.parseInt(value(LITERAL_EXECMAINSTATUS));
  }

  BigInteger executionStart() {
    return new BigInteger(value(LITERAL_EXECMAINSTARTTIMESTAMPMONOTONIC));
  }

  BigInteger executionEnd() {
    return new BigInteger(value(LITERAL_EXECMAINEXITTIMESTAMPMONOTONIC));
  }

  /** SSC135: complete manager GC only, never an execution result or receipt zero. */
  boolean coldStopped() {
    return inactiveBaseline()
        && value(LITERAL_INVOCATIONID).isEmpty()
        && value(LITERAL_EXECMAINCODE).equals("0")
        && value(LITERAL_EXECMAINSTATUS).equals("0")
        && value(LITERAL_EXECMAINSTARTTIMESTAMPMONOTONIC).equals("0")
        && value(LITERAL_EXECMAINEXITTIMESTAMPMONOTONIC).equals("0")
        && value(LITERAL_RESULT).equals(LITERAL_SUCCESS);
  }

  /** Same five real execution values despite the legitimate stop state transition. */
  boolean sameStoppedExecution(InspectorUnitSnapshot before) {
    return Set.of("inactive/dead", "failed/failed")
            .contains(value(LITERAL_ACTIVESTATE) + "/" + value(LITERAL_SUBSTATE))
        && Set.of(LITERAL_SUCCESS, LITERAL_EXIT_CODE).contains(value(LITERAL_RESULT))
        && value(LITERAL_EXECMAINCODE).equals("1")
        && value(LITERAL_INVOCATIONID).equals(before.value(LITERAL_INVOCATIONID))
        && value(LITERAL_EXECMAINSTATUS).equals(before.value(LITERAL_EXECMAINSTATUS))
        && value(LITERAL_EXECMAINSTARTTIMESTAMPMONOTONIC)
            .equals(before.value(LITERAL_EXECMAINSTARTTIMESTAMPMONOTONIC))
        && value(LITERAL_EXECMAINEXITTIMESTAMPMONOTONIC)
            .equals(before.value(LITERAL_EXECMAINEXITTIMESTAMPMONOTONIC));
  }

  boolean inactiveBaseline() {
    return value(LITERAL_ACTIVESTATE).equals("inactive")
        && value(LITERAL_SUBSTATE).equals("dead")
        && (target != Target.INSPECTOR || value(LITERAL_REMAINAFTEREXIT).equals(LITERAL_YES))
        && quiescent();
  }

  /** SSC127: old normal stop data only, NEVER a fresh worker receipt or journal proof. */
  boolean brokerStoppedNormally() {
    return target == Target.ARTEMIS
        && quiescent()
        && invocationId().isPresent()
        && value(LITERAL_EXECMAINCODE).equals("1")
        && value(LITERAL_EXECMAINSTATUS).equals("143")
        && executionStart().signum() > 0
        && executionEnd().compareTo(executionStart()) >= 0
        && ((value(LITERAL_ACTIVESTATE).equals(LITERAL_FAILED)
                && value(LITERAL_RESULT).equals(LITERAL_EXIT_CODE))
            || (value(LITERAL_ACTIVESTATE).equals("inactive")
                && value(LITERAL_RESULT).equals(LITERAL_SUCCESS)));
  }

  boolean heldCleanup() {
    return target == Target.CLEANUP
        && value(LITERAL_ACTIVESTATE).equals("active")
        && value(LITERAL_SUBSTATE).equals("exited")
        && quiescent();
  }

  boolean heldMaintenance() {
    return (target == Target.CLEANUP || target == Target.INSPECTOR || target == Target.EXPIRY)
        && value(LITERAL_REMAINAFTEREXIT).equals(LITERAL_YES)
        && value(LITERAL_ACTIVESTATE).equals("active")
        && value(LITERAL_SUBSTATE).equals("exited")
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

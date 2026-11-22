package dev.codex.schubert.nk.batch.monitoring;

import org.jspecify.annotations.Nullable;

/**
 * Classifies the update result and pre-reboot observations supplied by daily maintenance.
 * NK-OPS-001, OPS-008, UI251 §3, SS341 §4.1, PT-OPS-MAINT-PREBOOT003-U01..U06.
 */
public final class MaintenanceUpdateAssessment {
  private MaintenanceUpdateAssessment() {}

  public enum UpdateResult {
    SUCCESS,
    WARNING,
    UNVERIFIED
  }

  public enum Observation {
    CONFIRMED_SAFE,
    UNSAFE,
    UNVERIFIED
  }

  public enum Decision {
    CONDITIONS_MET,
    CONDITIONS_MET_WITH_WARNING,
    KEEP_PRIVATE
  }

  public record SafetyChecks(
      Observation packageManagerLock,
      Observation packageConsistency,
      Observation filesystem,
      Observation bootPartition,
      Observation kernelAndInitramfs) {
    public SafetyChecks(
        @Nullable Observation packageManagerLock,
        @Nullable Observation packageConsistency,
        @Nullable Observation filesystem,
        @Nullable Observation bootPartition,
        @Nullable Observation kernelAndInitramfs) {
      this.packageManagerLock = present(packageManagerLock);
      this.packageConsistency = present(packageConsistency);
      this.filesystem = present(filesystem);
      this.bootPartition = present(bootPartition);
      this.kernelAndInitramfs = present(kernelAndInitramfs);
    }
  }

  /** An absent or unverified receipt leaves the system in the private state. */
  public static Decision assess(@Nullable UpdateResult update, @Nullable SafetyChecks checks) {
    if (checks == null
        || checks.packageManagerLock() != Observation.CONFIRMED_SAFE
        || checks.packageConsistency() != Observation.CONFIRMED_SAFE
        || checks.filesystem() != Observation.CONFIRMED_SAFE
        || checks.bootPartition() != Observation.CONFIRMED_SAFE
        || checks.kernelAndInitramfs() != Observation.CONFIRMED_SAFE
        || update == null) {
      return Decision.KEEP_PRIVATE;
    }
    return switch (update) {
      case SUCCESS -> Decision.CONDITIONS_MET;
      case WARNING -> Decision.CONDITIONS_MET_WITH_WARNING;
      case UNVERIFIED -> Decision.KEEP_PRIVATE;
    };
  }

  private static Observation present(@Nullable Observation result) {
    return result == null ? Observation.UNVERIFIED : result;
  }
}

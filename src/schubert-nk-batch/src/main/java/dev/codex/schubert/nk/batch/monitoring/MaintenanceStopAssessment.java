package dev.codex.schubert.nk.batch.monitoring;

import java.time.Duration;
import java.util.List;
import java.util.UUID;
import org.jspecify.annotations.Nullable;

/**
 * Checks the observations for the fixed stop sequence before a daily maintenance update.
 * NK-OPS-001, OPS-003, UI251 §3, SS341 §4.1, PT-OPS-MAINT-PREBOOT002-S01..S05.
 */
public final class MaintenanceStopAssessment {
  private static final Duration WEB_GRACE = Duration.ofSeconds(30);
  private static final Duration API_GRACE = Duration.ofSeconds(60);
  private static final List<Stage> STOP_ORDER =
      List.of(Stage.CADDY, Stage.WEB, Stage.API, Stage.ARTEMIS, Stage.POSTGRESQL);

  private MaintenanceStopAssessment() {}

  public enum Stage {
    CADDY,
    WEB,
    API,
    ARTEMIS,
    POSTGRESQL
  }

  public enum Result {
    CONFIRMED,
    FAILED,
    TIMED_OUT,
    UNVERIFIED
  }

  /**
   * Observed elapsed covers the stage's complete graceful-stop wait. CONFIRMED requires the
   * caller's verified terminal observations, including the public request barrier, journal flush,
   * or inactive and readiness checks where those conditions apply.
   */
  public record StopReceipt(
      @Nullable UUID runId,
      @Nullable Stage stage,
      @Nullable Result result,
      @Nullable Duration elapsed) {}

  /** Checks purpose-specific observations. The caller owns collection, authority and dispatch. */
  public static boolean hasConfirmedStops(
      @Nullable UUID runId, @Nullable List<? extends @Nullable StopReceipt> receipts) {
    if (runId == null || receipts == null || receipts.size() != STOP_ORDER.size()) return false;
    for (int i = 0; i < STOP_ORDER.size(); i++) {
      Stage stage = STOP_ORDER.get(i);
      StopReceipt receipt = receipts.get(i);
      if (receipt == null
          || !runId.equals(receipt.runId())
          || stage != receipt.stage()
          || receipt.result() != Result.CONFIRMED
          || !withinGrace(stage, receipt.elapsed())) return false;
    }
    return true;
  }

  private static boolean withinGrace(Stage stage, @Nullable Duration elapsed) {
    if (elapsed == null || elapsed.isNegative()) return false;
    if (stage == Stage.WEB) return elapsed.compareTo(WEB_GRACE) <= 0;
    if (stage == Stage.API) return elapsed.compareTo(API_GRACE) <= 0;
    return true;
  }
}

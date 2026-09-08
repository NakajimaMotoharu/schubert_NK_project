package dev.codex.schubert.security;

import dev.codex.schubert.nk.api.security.LoginAttemptKind;
import dev.codex.schubert.nk.api.security.LoginAttemptState;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;

/** Read-only Current boundary diagnostic: no credentials, deployed DB, HTTP or baseline writes. */
public final class CurrentWindowBoundaryProbe {
  public static void main(String[] args) {
    int mismatches = 0;
    for (LoginAttemptKind kind : LoginAttemptKind.values()) {
      for (long delta : new long[] {-1, 0, 1}) {
        ProbeClock clock = new ProbeClock();
        LoginAttemptService current =
            new LoginAttemptService(10, 5, Duration.ofMinutes(15), Duration.ofMinutes(15), clock);
        current.recordFailure("127.0.0.1", "synthetic-user");
        LoginAttemptState nk = LoginAttemptState.empty(kind).afterFailure(clock.now);
        clock.now = Instant.parse("2026-09-08T00:15:00Z").plusNanos(delta);
        int additional = kind == LoginAttemptKind.USER ? 4 : 9;
        for (int count = 0; count < additional; count++) {
          current.recordFailure(
              "127.0.0.1",
              kind == LoginAttemptKind.USER ? "synthetic-user" : "synthetic-other-" + count);
          nk = nk.afterFailure(clock.now);
        }
        boolean currentLocked =
            current
                .lockStatus(
                    "127.0.0.1", kind == LoginAttemptKind.USER ? "synthetic-user" : "unused-user")
                .locked();
        boolean nkLocked = nk.isLocked(clock.now);
        if (currentLocked != nkLocked) mismatches++;
        System.out.println(
            "kind="
                + kind
                + " boundaryOffsetNanos="
                + delta
                + " currentLocked="
                + currentLocked
                + " nkLocked="
                + nkLocked);
      }
    }
    System.out.println("cases=6 mismatches=" + mismatches);
    if (mismatches != 0) System.exit(2);
  }

  private static final class ProbeClock extends Clock {
    Instant now = Instant.parse("2026-09-08T00:00:00Z");

    @Override
    public ZoneId getZone() {
      return ZoneOffset.UTC;
    }

    @Override
    public Clock withZone(ZoneId zone) {
      return this;
    }

    @Override
    public Instant instant() {
      return now;
    }
  }
}

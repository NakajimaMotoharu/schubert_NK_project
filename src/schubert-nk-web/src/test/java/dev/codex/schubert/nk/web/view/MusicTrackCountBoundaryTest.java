package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertThrowsExactly;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.media.MusicTrackResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SCR013, UI235 §9, SS313 §2, PT-WEB-SCR013-COUNT-001. */
final class MusicTrackCountBoundaryTest {
  @Test
  void rejectsDeclaredOneWhenTheTrackRecordsAreEmpty() {
    var actor =
        new SessionPrincipal(
            "listener",
            UserRole.USER,
            AuthenticationContext.of("a".repeat(64)),
            Instant.parse("2026-09-19T00:00:00Z"));

    assertThrowsExactly(
        IllegalArgumentException.class,
        () ->
            MusicTrackViewModel.from(
                actor, "BGM", "ゲーム", new MusicTrackResponseData(1), List.of()));
  }
}

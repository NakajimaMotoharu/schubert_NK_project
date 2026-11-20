package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertThrowsExactly;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.media.AnimationListResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.AnimationListCategory;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SCR009, UI235 §5, SS313 §2, PT-WEB-SCR009-COUNT-001. */
final class AnimationListCountBoundaryTest {
  @Test
  void rejectsDeclaredOneWhenTheAnimationRecordsAreEmpty() {
    var actor =
        new SessionPrincipal(
            "viewer",
            UserRole.USER,
            AuthenticationContext.of("a".repeat(64)),
            Instant.parse("2026-09-19T00:00:00Z"));

    assertThrowsExactly(
        IllegalArgumentException.class,
        () ->
            AnimationListViewModel.from(
                actor, AnimationListCategory.MAIN, new AnimationListResponseData(1), List.of()));
  }
}

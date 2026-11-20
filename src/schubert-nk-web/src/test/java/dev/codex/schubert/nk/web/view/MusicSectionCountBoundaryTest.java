package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertThrowsExactly;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.media.MusicSectionRecord;
import dev.codex.schubert.nk.protocol.layout.media.MusicSectionResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SCR012, UI235 §8, SS313 §2, PT-WEB-SCR012-COUNT-001. */
final class MusicSectionCountBoundaryTest {
  @Test
  void rejectsDeclaredZeroWhenOneSectionRecordIsPresent() {
    var actor =
        new SessionPrincipal(
            "listener",
            UserRole.USER,
            AuthenticationContext.of("a".repeat(64)),
            Instant.parse("2026-09-19T00:00:00Z"));
    var response = new MusicSectionResponseData(0);
    var records = List.of(new MusicSectionRecord("ゲーム", 9));

    assertThrowsExactly(
        IllegalArgumentException.class,
        () -> MusicSectionViewModel.from(actor, "曲", response, records));
  }
}

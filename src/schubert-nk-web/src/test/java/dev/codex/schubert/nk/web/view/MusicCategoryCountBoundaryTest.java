package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertThrowsExactly;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.media.MusicCategoryRecord;
import dev.codex.schubert.nk.protocol.layout.media.MusicCategoryResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SCR011, UI235 §7, SS313 §2, PT-WEB-SCR011-COUNT-001. */
final class MusicCategoryCountBoundaryTest {
  @Test
  void rejectsDeclaredZeroWhenOneCategoryRecordIsPresent() {
    var actor =
        new SessionPrincipal(
            "listener",
            UserRole.USER,
            AuthenticationContext.of("a".repeat(64)),
            Instant.parse("2026-09-19T00:00:00Z"));
    var response = new MusicCategoryResponseData(0);
    var records = List.of(new MusicCategoryRecord("曲", 9));

    assertThrowsExactly(
        IllegalArgumentException.class,
        () -> MusicCategoryViewModel.from(actor, response, records));
  }
}

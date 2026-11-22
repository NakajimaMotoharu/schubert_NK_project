package dev.codex.schubert.nk.api.dispatch;

import static java.util.Map.entry;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.admin.PasswordResetRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserCreateRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserRoleRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserStatusRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserUnlockRequestData;
import dev.codex.schubert.nk.protocol.layout.auth.LoginRequestData;
import dev.codex.schubert.nk.protocol.layout.auth.LogoutRequestData;
import dev.codex.schubert.nk.protocol.layout.log.LogSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationListRequestData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationMenuRequestData;
import dev.codex.schubert.nk.protocol.layout.media.AudioDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicCategoryRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicSectionRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicTrackRequestData;
import dev.codex.schubert.nk.protocol.layout.media.VideoDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationCancelRequestData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDeleteRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSubmitRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.GameListRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.RouteListRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioFileListRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.SpeakerListRequestData;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/** Explicit SS323 input catalog and independent registration cases, PT-JMS-HREG001..006. */
final class LayoutHandlerRegistryTest {
  private static final LayoutId GAME = new LayoutId("GAMREQ01");
  private static final LayoutId GAME_REPLY = new LayoutId("GAMRSP01");
  private static final LayoutId QUESTION_WORK = new LayoutId("QWKREQ01");
  private static final LayoutId WEB_EVENT = new LayoutId("WLGEVT01");
  private static final LayoutId UNKNOWN = new LayoutId("ZZZREQ99");
  private static final Map<String, Class<?>> EXPECTED =
      Map.ofEntries(
          entry("LGNREQ01", LoginRequestData.class),
          entry("LOGREQ01", LogoutRequestData.class),
          entry("GAMREQ01", GameListRequestData.class),
          entry("SPKREQ01", SpeakerListRequestData.class),
          entry("SRCREQ01", ScenarioSearchRequestData.class),
          entry("RTEREQ01", RouteListRequestData.class),
          entry("SCFREQ01", ScenarioFileListRequestData.class),
          entry("SCNREQ01", ScenarioDetailRequestData.class),
          entry("AUDREQ01", AudioDescriptorRequestData.class),
          entry("ANMREQ01", AnimationMenuRequestData.class),
          entry("ANLREQ01", AnimationListRequestData.class),
          entry("VIDREQ01", VideoDescriptorRequestData.class),
          entry("MCTREQ01", MusicCategoryRequestData.class),
          entry("MCSREQ01", MusicSectionRequestData.class),
          entry("MTRREQ01", MusicTrackRequestData.class),
          entry("MEDREQ01", MusicDescriptorRequestData.class),
          entry("LGSREQ01", LogSearchRequestData.class),
          entry("USRREQ01", UserSearchRequestData.class),
          entry("UCRREQ01", UserCreateRequestData.class),
          entry("UDTREQ01", UserDetailRequestData.class),
          entry("USTREQ01", UserStatusRequestData.class),
          entry("URLREQ01", UserRoleRequestData.class),
          entry("UPWREQ01", PasswordResetRequestData.class),
          entry("ULKREQ01", UserUnlockRequestData.class),
          entry("QSBREQ01", QuestionSubmitRequestData.class),
          entry("NTSREQ01", NotificationSearchRequestData.class),
          entry("NTDREQ01", NotificationDetailRequestData.class),
          entry("NTCREQ01", NotificationCancelRequestData.class),
          entry("QSSREQ01", QuestionSearchRequestData.class),
          entry("QSDREQ01", QuestionDetailRequestData.class),
          entry("QDLREQ01", QuestionDeleteRequestData.class));

  private record TestHandler<Q>(LayoutId requestLayout, Class<Q> requestType)
      implements LayoutHandler<Q, Integer> {
    @Override
    public Integer handle(RequestContext context, Q request) {
      throw new AssertionError("registration must not execute a handler");
    }
  }

  private static List<LayoutHandler<?, ?>> completeHandlers() {
    List<LayoutHandler<?, ?>> handlers = new ArrayList<>();
    EXPECTED.forEach((id, type) -> handlers.add(new TestHandler<>(new LayoutId(id), type)));
    return handlers;
  }

  @Test
  @DisplayName("PT-JMS-HREG001 frozen independent 31 layout and request type rows")
  void registersAllApprovedRequestTypesExactlyOnce() {
    var entries = completeHandlers();
    assertEquals(31, entries.size());
    var registry = new LayoutHandlerRegistry(entries);
    for (var entry : entries) {
      var resolved = registry.find(entry.requestLayout()).orElseThrow();
      assertSame(entry, resolved);
      assertEquals(EXPECTED.get(resolved.requestLayout().value()), resolved.requestType());
    }
  }

  @Test
  @DisplayName("PT-JMS-HREG002 snapshot and lookup without side effects")
  void preservesRegisteredHandlersAfterCallerListChanges() {
    var entries = completeHandlers();
    var registry = new LayoutHandlerRegistry(entries);
    var original = registry.find(GAME).orElseThrow();
    entries.clear();
    assertSame(original, registry.find(GAME).orElseThrow());
    for (var notRequest : List.of(GAME_REPLY, QUESTION_WORK, WEB_EVENT, UNKNOWN)) {
      assertEquals(Optional.empty(), registry.find(notRequest));
    }
  }

  @Test
  @DisplayName("PT-JMS-HREG003 missing and duplicate handlers")
  void rejectsIncompleteAndDuplicateRegistration() {
    var missing = completeHandlers();
    missing.removeFirst();
    assertEquals(
        "required request handlers are missing",
        assertThrows(IllegalArgumentException.class, () -> new LayoutHandlerRegistry(missing))
            .getMessage());
    assertThrows(IllegalArgumentException.class, () -> new LayoutHandlerRegistry(List.of()));

    var duplicate = completeHandlers();
    duplicate.add(duplicate.getFirst());
    assertEquals(
        "duplicate request handler layout",
        assertThrows(IllegalArgumentException.class, () -> new LayoutHandlerRegistry(duplicate))
            .getMessage());
  }

  @Test
  @DisplayName("PT-JMS-HREG004 wrong concrete type despite a known layout")
  void rejectsIncorrectTypeForAnApprovedLayout() {
    var handlers = completeHandlers();
    handlers.removeIf(handler -> handler.requestLayout().equals(GAME));
    handlers.add(new TestHandler<>(GAME, LogoutRequestData.class));
    assertEquals(
        "handler request type does not match its layout",
        assertThrows(IllegalArgumentException.class, () -> new LayoutHandlerRegistry(handlers))
            .getMessage());
  }

  @Test
  @DisplayName("PT-JMS-HREG005 unrelated layouts cannot be registered")
  void rejectsResponsesInternalEventsAndUnknownLayouts() {
    for (var notRequest : List.of(GAME_REPLY, QUESTION_WORK, WEB_EVENT, UNKNOWN)) {
      var registrations = completeHandlers();
      registrations.add(new TestHandler<>(notRequest, GameListRequestData.class));
      assertEquals(
          "handler layout is outside the synchronous requests",
          assertThrows(
                  IllegalArgumentException.class, () -> new LayoutHandlerRegistry(registrations))
              .getMessage());
    }
  }

  @Test
  @DisplayName("PT-JMS-HREG006 null boundaries")
  void rejectsNullEntriesAndNullMetadataExplicitly() {
    assertThrows(NullPointerException.class, () -> new LayoutHandlerRegistry(null));
    var entries = completeHandlers();
    entries.add(null);
    assertThrows(NullPointerException.class, () -> new LayoutHandlerRegistry(entries));
    assertThrows(
        NullPointerException.class,
        () ->
            new LayoutHandlerRegistry(List.of(new TestHandler<>(null, GameListRequestData.class))));
    assertThrows(
        NullPointerException.class,
        () -> new LayoutHandlerRegistry(List.of(new TestHandler<>(GAME, null))));
    var registry = new LayoutHandlerRegistry(completeHandlers());
    assertThrows(NullPointerException.class, () -> registry.find(null));
  }
}

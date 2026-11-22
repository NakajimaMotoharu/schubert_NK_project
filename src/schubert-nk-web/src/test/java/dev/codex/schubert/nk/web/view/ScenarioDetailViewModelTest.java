package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioEntryRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.AudioId;
import dev.codex.schubert.nk.protocol.layout.semantic.DeliveryMode;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryId;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryType;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import dev.codex.schubert.nk.protocol.layout.semantic.RelativePath;
import dev.codex.schubert.nk.protocol.layout.semantic.ScriptFileId;
import dev.codex.schubert.nk.protocol.layout.semantic.Sha256Hex;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.beans.IntrospectionException;
import java.beans.Introspector;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.jsoup.Jsoup;
import org.junit.jupiter.api.Test;
import org.thymeleaf.context.Context;
import org.thymeleaf.spring6.SpringTemplateEngine;
import org.thymeleaf.templateresolver.StringTemplateResolver;

/** Independent literals: PG195/UI223,234/SS313,333/015008/PT-WEB194..205. */
class ScenarioDetailViewModelTest {
  private static final String READER_USERNAME = "reader";
  private static final String SCENARIO_BODY_TEXT = "本文<&>";

  private static SessionPrincipal actor() {
    return new SessionPrincipal(
        READER_USERNAME,
        UserRole.USER,
        AuthenticationContext.of("a".repeat(64)),
        Instant.parse("2026-09-20T00:00:00Z"));
  }

  private static ScenarioDetailResponseData data(
      DeliveryMode mode,
      int count,
      Optional<ScriptFileId> previous,
      Optional<String> previousTitle,
      Optional<ScriptFileId> next,
      Optional<String> nextTitle) {
    return new ScenarioDetailResponseData(
        new ScriptFileId(23),
        GameCode.NUKITASHI_1,
        "章<script>",
        DisplayPath.of("文章/01.txt"),
        previous,
        previousTitle,
        next,
        nextTitle,
        mode,
        mode == DeliveryMode.FILE
            ? Optional.of(UUID.fromString("12345678-1234-4234-8234-123456789abc"))
            : Optional.empty(),
        mode == DeliveryMode.FILE
            ? Optional.of(RelativePath.of("20260920/12345678-1234-4234-8234-123456789abc.ready"))
            : Optional.empty(),
        mode == DeliveryMode.FILE ? count * 4800L : 0,
        mode == DeliveryMode.FILE ? Optional.of(Sha256Hex.of("a".repeat(64))) : Optional.empty(),
        mode == DeliveryMode.FILE ? 4800 : 0,
        mode == DeliveryMode.FILE ? count : 0);
  }

  private static ScenarioDetailResponseData data(DeliveryMode mode, int count) {
    return data(
        mode, count, Optional.empty(), Optional.empty(), Optional.empty(), Optional.empty());
  }

  private static ScenarioEntryRecord entry(long id, int sequence, int audio, String text) {
    return new ScenarioEntryRecord(
        new EntryId(id),
        sequence,
        sequence + 10,
        audio == 0 ? EntryType.NARRATION : EntryType.DIALOGUE,
        audio == 0 ? Optional.empty() : Optional.of("話者<img>"),
        text,
        audio,
        audio == 0 ? Optional.empty() : Optional.of(new AudioId(id * 10 + audio)),
        audio == 0
            ? Optional.empty()
            : Optional.of(DisplayPath.of("音声/" + id + "-" + audio + ".ogg")));
  }

  private static List<ScenarioEntryRecord> records() {
    return List.of(
        entry(9, 1, 0, "地の文"),
        entry(3, 2, 1, SCENARIO_BODY_TEXT),
        entry(3, 2, 2, SCENARIO_BODY_TEXT),
        entry(7, 3, 1, "最後"));
  }

  private static ScenarioDetailViewModel page(List<ScenarioEntryRecord> records) {
    return ScenarioDetailViewModel.from(actor(), data(DeliveryMode.INLINE, 0), records);
  }

  @Test
  void web194HeaderAndNavigation() {
    for (var role : UserRole.values())
      for (var game : GameCode.values())
        for (boolean before : List.of(false, true))
          for (boolean after : List.of(false, true)) {
            var base =
                data(
                    DeliveryMode.INLINE,
                    0,
                    before ? Optional.of(new ScriptFileId(1)) : Optional.empty(),
                    before ? Optional.of("前章") : Optional.empty(),
                    after ? Optional.of(new ScriptFileId(999999999999L)) : Optional.empty(),
                    after ? Optional.of("次章") : Optional.empty());
            var input =
                new ScenarioDetailResponseData(
                    base.scriptFileId(),
                    game,
                    base.displayTitle(),
                    base.displayPath(),
                    base.previousFileId(),
                    base.previousTitle(),
                    base.nextFileId(),
                    base.nextTitle(),
                    base.deliveryMode(),
                    base.fileId(),
                    base.fileRelativePath(),
                    base.fileByteLength(),
                    base.fileSha256(),
                    base.fileRecordLength(),
                    base.fileRecordCount());
            var actor =
                new SessionPrincipal(
                    READER_USERNAME, role, AuthenticationContext.of("a".repeat(64)), Instant.EPOCH);
            var view = ScenarioDetailViewModel.from(actor, input, List.of());
            assertEquals(23, view.getId());
            assertEquals(
                game == GameCode.NUKITASHI_1 ? "NUKITASHI1" : "NUKITASHI2", view.getGame());
            assertEquals("章<script>", view.getTitle());
            assertEquals("文章/01.txt", view.getDisplayPath());
            assertEquals(READER_USERNAME, view.getTopBar().getUsername());
            assertEquals(role == UserRole.USER ? "USER" : "ADMIN", view.getTopBar().getRole());
            assertEquals(before, view.getPrevious().isPresent());
            assertEquals(after, view.getNext().isPresent());
            if (before) {
              var link = view.getPrevious().orElseThrow();
              assertEquals(1, link.getId());
              assertEquals("前章", link.getTitle());
              assertEquals("/scenarios/1", link.getHref());
            }
            if (after) {
              var link = view.getNext().orElseThrow();
              assertEquals(999999999999L, link.getId());
              assertEquals("次章", link.getTitle());
              assertEquals("/scenarios/999999999999", link.getHref());
            }
          }
  }

  @Test
  void web195GroupingAndAudio() {
    var entries = page(records()).getEntries();
    assertEquals(
        List.of(9L, 3L, 7L), entries.stream().map(ScenarioDetailViewModel.Entry::getId).toList());
    assertEquals(
        List.of("地の文", SCENARIO_BODY_TEXT, "最後"),
        entries.stream().map(ScenarioDetailViewModel.Entry::getBody).toList());
    assertEquals(
        List.of(1, 2, 3),
        entries.stream().map(ScenarioDetailViewModel.Entry::getSequence).toList());
    assertEquals(
        List.of(11, 12, 13),
        entries.stream().map(ScenarioDetailViewModel.Entry::getLineNumber).toList());
    assertEquals(
        List.of("entry-9", "entry-3", "entry-7"),
        entries.stream().map(ScenarioDetailViewModel.Entry::getAnchor).toList());
    assertEquals("", entries.get(0).getSpeaker());
    assertFalse(entries.get(0).isDialogue());
    assertTrue(entries.get(1).isDialogue());
    assertEquals("話者<img>", entries.get(1).getSpeaker());
    assertTrue(entries.get(0).getAudio().isEmpty());
    assertEquals(
        List.of(31L, 32L),
        entries.get(1).getAudio().stream().map(ScenarioDetailViewModel.Audio::getId).toList());
    assertEquals(
        List.of(1, 2),
        entries.get(1).getAudio().stream()
            .map(ScenarioDetailViewModel.Audio::getSequence)
            .toList());
    assertEquals(
        List.of("音声/3-1.ogg", "音声/3-2.ogg"),
        entries.get(1).getAudio().stream()
            .map(ScenarioDetailViewModel.Audio::getDisplayPath)
            .toList());
    assertEquals(
        List.of("/audio/31", "/audio/32"),
        entries.get(1).getAudio().stream().map(ScenarioDetailViewModel.Audio::getHref).toList());
    assertEquals(
        List.of("/audio/31/download", "/audio/32/download"),
        entries.get(1).getAudio().stream()
            .map(ScenarioDetailViewModel.Audio::getDownloadHref)
            .toList());
    assertEquals(1, entries.get(2).getAudio().size());
  }

  @Test
  void web196EmptyAndBounds() {
    assertTrue(page(List.of()).getEntries().isEmpty());
    var values = new ArrayList<ScenarioEntryRecord>();
    for (int i = 1; i <= 10001; i++) values.add(entry(i, i, 0, "本文"));
    assertEquals(200, page(values.subList(0, 200)).getEntries().size());
    assertThrows(IllegalArgumentException.class, () -> page(values.subList(0, 201)));
    for (int count : List.of(1, 10000)) {
      var result =
          ScenarioDetailViewModel.from(
              actor(), data(DeliveryMode.FILE, count), values.subList(0, count));
      assertEquals(count, result.getEntries().size());
      assertEquals(count, result.getEntries().get(count - 1).getId());
    }
    for (int count : List.of(0, 2, 10001)) {
      List<ScenarioEntryRecord> input =
          count == 2 ? values.subList(0, 1) : values.subList(0, count);
      assertThrows(
          IllegalArgumentException.class,
          () -> ScenarioDetailViewModel.from(actor(), data(DeliveryMode.FILE, count), input));
    }
  }

  @Test
  void web197NullContracts() {
    assertThrows(
        NullPointerException.class,
        () -> ScenarioDetailViewModel.from(null, data(DeliveryMode.INLINE, 0), List.of()));
    assertThrows(
        NullPointerException.class, () -> ScenarioDetailViewModel.from(actor(), null, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> ScenarioDetailViewModel.from(actor(), data(DeliveryMode.INLINE, 0), null));
    assertThrows(NullPointerException.class, () -> page(Arrays.asList((ScenarioEntryRecord) null)));
  }

  @Test
  void web198NavigationPairs() {
    for (int mismatch = 0; mismatch < 4; mismatch++) {
      var input =
          data(
              DeliveryMode.INLINE,
              0,
              mismatch == 0 ? Optional.of(new ScriptFileId(1)) : Optional.empty(),
              mismatch == 1 ? Optional.of("前") : Optional.empty(),
              mismatch == 2 ? Optional.of(new ScriptFileId(2)) : Optional.empty(),
              mismatch == 3 ? Optional.of("次") : Optional.empty());
      assertThrows(
          IllegalArgumentException.class,
          () -> ScenarioDetailViewModel.from(actor(), input, List.of()));
    }
  }

  @Test
  void web199SequenceRejection() {
    for (var invalid :
        List.of(
            List.of(entry(1, 2, 0, "x")),
            List.of(entry(1, 1, 2, "x")),
            List.of(entry(1, 1, 1, "x"), entry(1, 1, 3, "x")),
            List.of(entry(1, 1, 1, "x"), entry(1, 1, 2, "y")),
            List.of(entry(1, 1, 0, "x"), entry(2, 2, 0, "y"), entry(1, 3, 0, "x"))))
      assertThrows(IllegalArgumentException.class, () -> page(invalid));
    var base = entry(1, 1, 1, "x");
    var noPath =
        new ScenarioEntryRecord(
            base.entryId(),
            1,
            11,
            base.entryType(),
            base.speakerName(),
            "x",
            1,
            base.audioId(),
            Optional.empty());
    assertThrows(IllegalArgumentException.class, () -> page(List.of(noPath)));
  }

  @Test
  void web200EntryMetadataConsistency() {
    var first = entry(1, 1, 1, "x");
    for (int change = 0; change < 3; change++) {
      var other =
          new ScenarioEntryRecord(
              first.entryId(),
              1,
              change == 0 ? 12 : 11,
              change == 1 ? EntryType.NARRATION : EntryType.DIALOGUE,
              change == 2 ? Optional.of("他") : first.speakerName(),
              "x",
              2,
              Optional.of(new AudioId(12)),
              Optional.of(DisplayPath.of("音声/2.ogg")));
      assertThrows(IllegalArgumentException.class, () -> page(List.of(first, other)));
    }
    assertEquals(
        2, page(List.of(first, entry(1, 1, 2, "x"))).getEntries().getFirst().getAudio().size());
  }

  @Test
  void web201ImmutableSnapshot() {
    var input = new ArrayList<>(records());
    var result = page(input);
    input.clear();
    assertEquals(3, result.getEntries().size());
    assertThrows(UnsupportedOperationException.class, () -> result.getEntries().clear());
    assertThrows(
        UnsupportedOperationException.class, () -> result.getEntries().get(1).getAudio().clear());
    assertEquals(2, result.getEntries().get(1).getAudio().size());
  }

  @Test
  void web202ClosedBeanContract() throws IntrospectionException {
    Map<Class<?>, Set<String>> expected =
        Map.of(
            ScenarioDetailViewModel.class,
                Set.of(
                    "topBar", "id", "game", "title", "displayPath", "previous", "next", "entries"),
            ScenarioDetailViewModel.Navigation.class, Set.of("id", "title", "href"),
            ScenarioDetailViewModel.Entry.class,
                Set.of(
                    "id",
                    "sequence",
                    "lineNumber",
                    "dialogue",
                    "speaker",
                    "body",
                    "anchor",
                    "audio"),
            ScenarioDetailViewModel.Audio.class,
                Set.of("id", "sequence", "displayPath", "href", "downloadHref"));
    for (var item : expected.entrySet()) {
      var actual = new HashSet<String>();
      for (var property :
          Introspector.getBeanInfo(item.getKey(), Object.class).getPropertyDescriptors()) {
        actual.add(property.getName());
        assertNull(property.getWriteMethod());
      }
      assertEquals(item.getValue(), actual);
      for (var field : item.getKey().getDeclaredFields()) {
        assertFalse(field.getGenericType().getTypeName().contains(".protocol."));
        assertFalse(field.getGenericType().getTypeName().contains("SessionPrincipal"));
      }
    }
  }

  @Test
  void web203SyntheticHtmlEscaping() {
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(new StringTemplateResolver());
    var context = new Context();
    context.setVariable("page", page(records()));
    var html =
        engine.process(
            "<h1 th:text='${page.title}'></h1><article th:each='entry : ${page.entries}'"
                + " th:id='${entry.anchor}'><span th:text='${entry.speaker}'></span><p"
                + " th:text='${entry.body}'></p><a th:each='audio : ${entry.audio}'"
                + " th:href='${audio.href}' th:text='${audio.displayPath}'></a></article>",
            context);
    var dom = Jsoup.parse(html);
    assertEquals("章<script>", dom.selectFirst("h1").text());
    assertTrue(dom.select("script,img").isEmpty());
    assertEquals(List.of("地の文", SCENARIO_BODY_TEXT, "最後"), dom.select("article p").eachText());
    assertEquals(
        List.of("/audio/31", "/audio/32", "/audio/71"), dom.select("article a").eachAttr("href"));
    assertEquals(List.of("entry-9", "entry-3", "entry-7"), dom.select("article").eachAttr("id"));
  }

  @Test
  void web204ConcurrentProjection()
      throws InterruptedException, ExecutionException, TimeoutException {
    var pool = Executors.newFixedThreadPool(8);
    try {
      var tasks = new ArrayList<Future<ScenarioDetailViewModel>>();
      for (int i = 0; i < 64; i++) {
        final int n = i;
        tasks.add(
            pool.submit(
                () ->
                    ScenarioDetailViewModel.from(
                        new SessionPrincipal(
                            READER_USERNAME + n,
                            UserRole.USER,
                            AuthenticationContext.of("b".repeat(64)),
                            Instant.EPOCH),
                        data(DeliveryMode.INLINE, 0),
                        List.of(entry(n + 1, 1, 0, "本文" + n)))));
      }
      for (int i = 0; i < 64; i++) {
        var result = tasks.get(i).get(10, TimeUnit.SECONDS);
        assertEquals(READER_USERNAME + i, result.getTopBar().getUsername());
        assertEquals("本文" + i, result.getEntries().getFirst().getBody());
        assertEquals(i + 1, result.getEntries().getFirst().getId());
      }
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  @Test
  void web205RedactedDiagnostics() {
    var input =
        data(
            DeliveryMode.INLINE,
            0,
            Optional.of(new ScriptFileId(1)),
            Optional.of("前章"),
            Optional.empty(),
            Optional.empty());
    var result = ScenarioDetailViewModel.from(actor(), input, records());
    assertEquals("ScenarioDetailViewModel[REDACTED]", result.toString());
    assertEquals("ScenarioNavigation[REDACTED]", result.getPrevious().orElseThrow().toString());
    assertEquals("ScenarioEntry[REDACTED]", result.getEntries().get(1).toString());
    assertEquals(
        "ScenarioAudio[REDACTED]", result.getEntries().get(1).getAudio().getFirst().toString());
  }
}

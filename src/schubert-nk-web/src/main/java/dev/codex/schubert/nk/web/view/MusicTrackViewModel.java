package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.media.MusicTrackRecord;
import dev.codex.schubert.nk.protocol.layout.media.MusicTrackResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.PairRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import org.springframework.web.util.UriUtils;

/** Stored pair/order projection, no matching/filesystem inference. UI223235/SS313/PG-D365. */
public final class MusicTrackViewModel {
  private static final java.lang.String LITERAL_TITLE = "title";

  private final Map<String, Object> values;

  private MusicTrackViewModel(
      SessionPrincipal actor,
      String category,
      String section,
      MusicTrackResponseData data,
      List<MusicTrackRecord> input) {
    var records = List.copyOf(input);
    if (records.size() > 200 || data.totalCount() != records.size())
      throw new IllegalArgumentException("invalid music track count");
    var tracks = new ArrayList<Map<String, Object>>();
    var pairs = new LinkedHashMap<String, Map<String, Object>>();
    var ids = new HashSet<String>();
    int previousOrder = -1;
    for (var record : records) {
      if (!category.equals(record.category())
          || !section.equals(record.section())
          || !ids.add(record.trackId())
          || record.fileByteLength() < 1
          || record.displayOrder() < previousOrder)
        throw new IllegalArgumentException("invalid bound music track");
      previousOrder = record.displayOrder();
      var track =
          Map.<String, Object>of(
              LITERAL_TITLE,
              record.title(),
              "displayPath",
              record.displayPath().wireValue(),
              "byteSize",
              record.fileByteLength(),
              "mediaHref",
              "/music/media/" + segment(record.trackId()),
              "downloadHref",
              "/music/download/" + segment(record.trackId()));
      tracks.add(track);
      if (category.equals("曲")) {
        String key =
            record.pairRole() == PairRole.NONE
                ? "single:" + record.trackId()
                : "pair:" + record.pairKey().orElseThrow(IllegalArgumentException::new);
        var pair =
            pairs.computeIfAbsent(
                key,
                ignored -> {
                  var result = new HashMap<String, Object>();
                  result.put(LITERAL_TITLE, displayTitle(record.title()));
                  result.put("main", Optional.empty());
                  result.put("instrumental", Optional.empty());
                  return result;
                });
        String slot = record.pairRole() == PairRole.INSTRUMENTAL ? "instrumental" : "main";
        if (!Optional.empty().equals(pair.get(slot)))
          throw new IllegalArgumentException("duplicate music pair role");
        pair.put(slot, Optional.of(track));
        if (record.pairRole() != PairRole.INSTRUMENTAL)
          pair.put(LITERAL_TITLE, displayTitle(record.title()));
      }
    }
    values =
        Map.of(
            "topBar",
            TopBarViewModel.from(actor),
            "category",
            category,
            "section",
            section,
            LITERAL_TITLE,
            category + " / " + section,
            "trackCount",
            records.size(),
            "songs",
            category.equals("曲"),
            "categoryHref",
            "/music/" + segment(category),
            "tracks",
            List.copyOf(tracks),
            "pairs",
            pairs.values().stream().map(Map::copyOf).toList());
  }

  public static MusicTrackViewModel from(
      SessionPrincipal actor,
      String category,
      String section,
      MusicTrackResponseData data,
      List<MusicTrackRecord> records) {
    return new MusicTrackViewModel(
        Objects.requireNonNull(actor, "actor"),
        Objects.requireNonNull(category, "category"),
        Objects.requireNonNull(section, "section"),
        Objects.requireNonNull(data, "data"),
        records);
  }

  private static String segment(String value) {
    if (value.isEmpty() || value.equals(".") || value.equals(".."))
      throw new IllegalArgumentException("invalid music link segment");
    return UriUtils.encode(value, StandardCharsets.UTF_8);
  }

  // Current display-only title rule; stored pair_key/role/order are never recomputed.
  private static String displayTitle(String title) {
    return title
        .replaceFirst("^\\d+-\\d+\\s+", "")
        .replaceAll("(?i)\\s*[\\(（][^\\)）]*(?:inst|instrument)[^\\)）]*[\\)）]?.*$", "")
        .replaceAll("(?i)\\s+(?:inst|instrument).*$", "")
        .trim();
  }

  public Map<String, Object> getValues() {
    return values;
  }

  @Override
  public String toString() {
    return "MusicTrackViewModel[REDACTED]";
  }
}

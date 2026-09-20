package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.media.*;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.nio.charset.StandardCharsets;
import java.util.*;
import org.jspecify.annotations.NullMarked;
import org.springframework.web.util.UriUtils;

/**
 * SCR012/FUN007/UI223,235/SS311,313,323,352/PG208/PT-WEB246..253. Validated-wire display snapshot.
 */
@NullMarked
public final class MusicSectionViewModel {
  private final TopBarViewModel topBar;
  private final String category;
  private final List<Card> sections;
  private final int trackCount;

  private MusicSectionViewModel(
      SessionPrincipal actor, String category, List<Card> sections, int count) {
    topBar = TopBarViewModel.from(actor);
    this.category = category;
    this.sections = List.copyOf(sections);
    trackCount = count;
  }

  public static MusicSectionViewModel from(
      SessionPrincipal actor,
      String category,
      MusicSectionResponseData data,
      List<MusicSectionRecord> records) {
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(category, "category");
    Objects.requireNonNull(data, "data");
    String parent = "/music/" + segment(category) + "/";
    var copy = List.copyOf(records);
    if (copy.size() > 100 || data.totalCount() != copy.size())
      throw new IllegalArgumentException("invalid music section count");
    var names = new HashSet<String>();
    var cards = new ArrayList<Card>();
    int total = 0;
    for (var record : copy) {
      if (!names.add(record.section()))
        throw new IllegalArgumentException("duplicate music section");
      cards.add(new Card(record.section(), record.trackCount(), parent));
      total += record.trackCount();
    }
    return new MusicSectionViewModel(actor, category, cards, total);
  }

  public TopBarViewModel getTopBar() {
    return topBar;
  }

  public String getCategory() {
    return category;
  }

  public List<Card> getSections() {
    return sections;
  }

  public int getTrackCount() {
    return trackCount;
  }

  @Override
  public String toString() {
    return "MusicSectionViewModel[REDACTED]";
  }

  private static String segment(String value) {
    if (value.isEmpty() || value.equals(".") || value.equals(".."))
      throw new IllegalArgumentException("invalid music link segment");
    return UriUtils.encode(value, StandardCharsets.UTF_8);
  }

  public static final class Card {
    private final String name, href;
    private final int trackCount;

    private Card(String name, int trackCount, String parent) {
      this.name = name;
      this.trackCount = trackCount;
      href = parent + segment(name);
    }

    public String getName() {
      return name;
    }

    public String getHref() {
      return href;
    }

    public int getTrackCount() {
      return trackCount;
    }

    @Override
    public String toString() {
      return "MusicSectionCard[REDACTED]";
    }
  }
}

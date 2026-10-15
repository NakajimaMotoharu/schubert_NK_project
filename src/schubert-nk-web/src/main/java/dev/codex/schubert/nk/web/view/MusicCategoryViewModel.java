package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.media.MusicCategoryRecord;
import dev.codex.schubert.nk.protocol.layout.media.MusicCategoryResponseData;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.springframework.web.util.UriUtils;

/**
 * SCR011/FUN007/UI223,235/SS311,313,323,352/PG208/PT-WEB246..253. Validated-wire display snapshot.
 */
@NullMarked
public final class MusicCategoryViewModel {
  private final TopBarViewModel topBar;
  private final List<Card> categories;
  private final int trackCount;

  private MusicCategoryViewModel(SessionPrincipal actor, List<Card> categories, int count) {
    topBar = TopBarViewModel.from(actor);
    this.categories = List.copyOf(categories);
    trackCount = count;
  }

  public static MusicCategoryViewModel from(
      SessionPrincipal actor, MusicCategoryResponseData data, List<MusicCategoryRecord> records) {
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(data, "data");
    var copy = List.copyOf(records);
    if (copy.size() > 20 || data.totalCount() != copy.size())
      throw new IllegalArgumentException("invalid music category count");
    var names = new HashSet<String>();
    var cards = new ArrayList<Card>();
    int total = 0;
    for (var record : copy) {
      if (!names.add(record.category()))
        throw new IllegalArgumentException("duplicate music category");
      cards.add(new Card(record.category(), record.trackCount()));
      total += record.trackCount();
    }
    return new MusicCategoryViewModel(actor, cards, total);
  }

  public TopBarViewModel getTopBar() {
    return topBar;
  }

  public List<Card> getCategories() {
    return categories;
  }

  public int getTrackCount() {
    return trackCount;
  }

  @Override
  public String toString() {
    return "MusicCategoryViewModel[REDACTED]";
  }

  private static String segment(String value) {
    if (value.isEmpty() || value.equals(".") || value.equals(".."))
      throw new IllegalArgumentException("invalid music link segment");
    return UriUtils.encode(value, StandardCharsets.UTF_8);
  }

  public static final class Card {
    private final String name;
    private final String href;
    private final int trackCount;

    private Card(String name, int trackCount) {
      this.name = name;
      this.trackCount = trackCount;
      href = "/music/" + segment(name);
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
      return "MusicCategoryCard[REDACTED]";
    }
  }
}

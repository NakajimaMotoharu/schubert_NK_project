package dev.codex.schubert.nk.web.view;

import dev.codex.schubert.nk.protocol.layout.media.AnimationListResponseData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.AnimationCategory;
import dev.codex.schubert.nk.protocol.layout.semantic.AnimationListCategory;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;
import org.springframework.web.util.UriUtils;

/** SCR009/FUN006/UI223,235/SS313,323,352/PG204/PT-WEB230..237. No file capabilities. */
@NullMarked
public final class AnimationListViewModel {
  private final TopBarViewModel topBar;
  private final String title;
  private final String section;
  private final int totalCount;
  private final List<Video> videos;
  private final List<Row> rows;

  private AnimationListViewModel(
      SessionPrincipal actor, AnimationListCategory category, List<Video> videos, List<Row> rows) {
    topBar = TopBarViewModel.from(actor);
    boolean main = category == AnimationListCategory.MAIN;
    title = main ? "メインパート一覧" : "OVA一覧";
    section = main ? "main" : "ova";
    totalCount = videos.size();
    this.videos = List.copyOf(videos);
    this.rows = List.copyOf(rows);
  }

  public static AnimationListViewModel from(
      SessionPrincipal actor,
      AnimationListCategory category,
      AnimationListResponseData data,
      List<AnimationRecord> records) {
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(category, "category");
    Objects.requireNonNull(data, "data");
    var copy = List.copyOf(records);
    if (copy.size() > 50 || data.totalCount() != copy.size())
      throw new IllegalArgumentException("invalid animation count");
    var byId = new LinkedHashMap<String, AnimationRecord>();
    var videos = new ArrayList<Video>();
    var subtracks = new HashMap<String, Video>();
    for (var record : copy) {
      boolean subtrack = record.category() == AnimationCategory.SUBTRACK;
      if ((category == AnimationListCategory.OVA) != (record.category() == AnimationCategory.OVA)
          || subtrack != record.parentMainId().isPresent()
          || record.fileByteLength() < 1)
        throw new IllegalArgumentException("invalid animation category or parent");
      var video = new Video(record);
      if (byId.putIfAbsent(record.videoId(), record) != null)
        throw new IllegalArgumentException("duplicate animation ID");
      videos.add(video);
      if (subtrack && subtracks.putIfAbsent(record.parentMainId().orElseThrow(), video) != null)
        throw new IllegalArgumentException("duplicate animation subtrack");
    }
    for (String parent : subtracks.keySet()) {
      var main = byId.get(parent);
      if (main == null || main.category() != AnimationCategory.MAIN)
        throw new IllegalArgumentException("orphan animation subtrack");
    }
    var rows = new ArrayList<Row>();
    for (int i = 0; i < copy.size(); i++) {
      var record = copy.get(i);
      if (record.category() == AnimationCategory.MAIN)
        rows.add(new Row(videos.get(i), Optional.ofNullable(subtracks.get(record.videoId()))));
    }
    return new AnimationListViewModel(actor, category, videos, rows);
  }

  public TopBarViewModel getTopBar() {
    return topBar;
  }

  public String getTitle() {
    return title;
  }

  public String getSection() {
    return section;
  }

  public int getTotalCount() {
    return totalCount;
  }

  public List<Video> getVideos() {
    return videos;
  }

  public List<Row> getRows() {
    return rows;
  }

  @Override
  public String toString() {
    return "AnimationListViewModel[REDACTED]";
  }

  public static final class Video {
    private final String title;
    private final String category;
    private final String displayPath;
    private final String href;
    private final long byteSize;

    private Video(AnimationRecord record) {
      String id = record.videoId();
      if (id.isEmpty() || id.equals(".") || id.equals(".."))
        throw new IllegalArgumentException("invalid animation link ID");
      title = record.title();
      category = record.category() == AnimationCategory.OVA ? "OVA" : "メインパート";
      displayPath = record.displayPath().wireValue();
      byteSize = record.fileByteLength();
      href = "/animation/videos/" + UriUtils.encode(id, StandardCharsets.UTF_8);
    }

    public String getTitle() {
      return title;
    }

    public String getCategory() {
      return category;
    }

    public String getDisplayPath() {
      return displayPath;
    }

    public long getByteSize() {
      return byteSize;
    }

    public String getHref() {
      return href;
    }

    @Override
    public String toString() {
      return "AnimationVideo[REDACTED]";
    }
  }

  public static final class Row {
    private final Video main;
    private final Optional<Video> subtrack;

    private Row(Video main, Optional<Video> subtrack) {
      this.main = main;
      this.subtrack = subtrack;
    }

    public Video getMain() {
      return main;
    }

    public Optional<Video> getSubtrack() {
      return subtrack;
    }

    @Override
    public String toString() {
      return "AnimationRow[REDACTED]";
    }
  }
}

package dev.codex.schubert.nk.migration;

import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * UI223's closed20 video catalogue and declared COPY binding, never real file or migration
 * admission. NK-MIG-001; MIG-DAT-003/MIG-DAT-005/MIG-003/MIG-005/MIG-006/DAT-004/FIL-003/FIL-005;
 * UI223/242/243/254; SS311/331/333/343 SSC358; PT-MIG-VIDEO001..024.
 */
@NullMarked
public final class VideoMigrationCatalogue {
  private static final String CATEGORY_MAIN = "メインパート";
  private static final String CATEGORY_OVA = "OVA";
  private static final String CATEGORY_OPENING = "オープニング";
  private static final long MINIMUM_TARGET_ID = 1;
  private static final long MAXIMUM_TARGET_ID = 999999999999L;
  private static final List<Video> CATALOGUE_ITEMS =
      List.of(
          new Video(
              1, "main-01", "第1話", CATEGORY_MAIN, "main_part/NUKITASHI_THE_ANIMATION_01.mp4", null),
          new Video(
              2,
              "main-01-subtrack",
              "第1話 SUBTRACK版",
              CATEGORY_MAIN,
              "main_part/NUKITASHI_THE_ANIMATION_01_SUBTRACK.mp4",
              "main-01"),
          new Video(
              3, "main-02", "第2話", CATEGORY_MAIN, "main_part/NUKITASHI_THE_ANIMATION_02.mp4", null),
          new Video(
              4, "main-03", "第3話", CATEGORY_MAIN, "main_part/NUKITASHI_THE_ANIMATION_03.mp4", null),
          new Video(
              5, "main-04", "第4話", CATEGORY_MAIN, "main_part/NUKITASHI_THE_ANIMATION_04.mp4", null),
          new Video(
              6,
              "main-04-subtrack",
              "第4話 SUBTRACK版",
              CATEGORY_MAIN,
              "main_part/NUKITASHI_THE_ANIMATION_04_SUBTRACK.mp4",
              "main-04"),
          new Video(
              7, "main-05", "第5話", CATEGORY_MAIN, "main_part/NUKITASHI_THE_ANIMATION_05.mp4", null),
          new Video(
              8, "main-06", "第6話", CATEGORY_MAIN, "main_part/NUKITASHI_THE_ANIMATION_06.mp4", null),
          new Video(
              9, "main-07", "第7話", CATEGORY_MAIN, "main_part/NUKITASHI_THE_ANIMATION_07.mp4", null),
          new Video(
              10,
              "main-08",
              "第8話",
              CATEGORY_MAIN,
              "main_part/NUKITASHI_THE_ANIMATION_08.mp4",
              null),
          new Video(
              11,
              "main-09",
              "第9話",
              CATEGORY_MAIN,
              "main_part/NUKITASHI_THE_ANIMATION_09.mp4",
              null),
          new Video(
              12,
              "main-10",
              "第10話",
              CATEGORY_MAIN,
              "main_part/NUKITASHI_THE_ANIMATION_10.mp4",
              null),
          new Video(
              13,
              "main-10-subtrack",
              "第10話 SUBTRACK版",
              CATEGORY_MAIN,
              "main_part/NUKITASHI_THE_ANIMATION_10_SUBTRACK.mp4",
              "main-10"),
          new Video(
              14,
              "main-11",
              "第11話",
              CATEGORY_MAIN,
              "main_part/NUKITASHI_THE_ANIMATION_11.mp4",
              null),
          new Video(
              15,
              "main-11-subtrack",
              "第11話 SUBTRACK版",
              CATEGORY_MAIN,
              "main_part/NUKITASHI_THE_ANIMATION_11_SUBTRACK.mp4",
              "main-11"),
          new Video(16, "ova-hinami", "OVA hinami", CATEGORY_OVA, "dosukebe_part/hinami.mp4", null),
          new Video(17, "ova-humino", "OVA humino", CATEGORY_OVA, "dosukebe_part/humino.mp4", null),
          new Video(18, "ova-misaki", "OVA misaki", CATEGORY_OVA, "dosukebe_part/misaki.mp4", null),
          new Video(19, "ova-nanase", "OVA nanase", CATEGORY_OVA, "dosukebe_part/nanase.mp4", null),
          new Video(20, "opening", "オープニング映像", CATEGORY_OPENING, "op.mp4", null));

  public List<Video> videos() {
    return CATALOGUE_ITEMS;
  }

  public Optional<Video> find(@Nullable String id) {
    if (id == null) throw invalid();
    for (var video : CATALOGUE_ITEMS) {
      if (video.logicalId().equals(id)) return Optional.of(video);
    }
    return Optional.empty();
  }

  /**
   * Snapshots declared claims; caller separately authenticates real assets and owns the DB work.
   */
  public List<MediaAssetCopyRow> copyRows(
      @Nullable Map<? extends @Nullable String, ? extends @Nullable Long> targetIds,
      @Nullable AssetMigrationManifest declaredAssets,
      @Nullable String createdAt)
      throws NoSuchAlgorithmException {
    if (targetIds == null || declaredAssets == null || createdAt == null) throw invalid();
    var ids = new HashMap<@Nullable String, @Nullable Long>(targetIds);
    if (ids.size() != CATALOGUE_ITEMS.size()
        || declaredAssets.entries().size() != CATALOGUE_ITEMS.size()) throw invalid();
    var assets = new HashMap<String, AssetMigrationManifest.Entry>();
    for (var entry : declaredAssets.entries()) {
      if (entry.kind() != AssetMigrationManifest.Kind.VIDEO) throw invalid();
      // The final manifest constructor has already established unique immutable current paths.
      assets.put(entry.currentPath(), entry);
    }
    var usedIds = new HashSet<Long>();
    var rows = new ArrayList<MediaAssetCopyRow>();
    for (var video : CATALOGUE_ITEMS) {
      @Nullable Long id = ids.get(video.logicalId());
      if (id == null || id < MINIMUM_TARGET_ID || id > MAXIMUM_TARGET_ID || !usedIds.add(id))
        throw invalid();
      @Nullable AssetMigrationManifest.Entry claim = assets.get(video.sourceRelativePath());
      if (claim == null) throw invalid();
      String source = video.sourceRelativePath();
      var fields =
          new ArrayList<@Nullable String>(
              Arrays.asList(
                  Long.toString(id),
                  video.logicalId(),
                  "VIDEO",
                  video.title(),
                  video.category(),
                  null,
                  claim.targetPath(),
                  source,
                  source.substring(source.lastIndexOf('/') + 1),
                  Long.toString(claim.byteLength()),
                  claim.sha256(),
                  "video/mp4",
                  video.parentLogicalId().orElse(null),
                  null,
                  null,
                  Integer.toString(video.displayOrder()),
                  createdAt));
      rows.add(new MediaAssetCopyRow(fields));
    }
    return List.copyOf(rows);
  }

  @Override
  public String toString() {
    return "VideoMigrationCatalogue[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration video catalogue input is invalid");
  }

  /** Closed-table immutable value; constructor has no external input. */
  public static final class Video {
    private final int retainedDisplayOrder;
    private final String retainedLogicalId;
    private final String retainedTitle;
    private final String retainedCategory;
    private final String retainedSourceRelativePath;
    private final @Nullable String retainedParent;

    private Video(
        int order,
        String id,
        String title,
        String category,
        String source,
        @Nullable String parent) {
      retainedDisplayOrder = order;
      retainedLogicalId = id;
      retainedTitle = title;
      retainedCategory = category;
      retainedSourceRelativePath = source;
      retainedParent = parent;
    }

    public int displayOrder() {
      return retainedDisplayOrder;
    }

    public String logicalId() {
      return retainedLogicalId;
    }

    public String title() {
      return retainedTitle;
    }

    public String category() {
      return retainedCategory;
    }

    public String sourceRelativePath() {
      return retainedSourceRelativePath;
    }

    public Optional<String> parentLogicalId() {
      return Optional.ofNullable(retainedParent);
    }

    @Override
    public String toString() {
      return "MigrationVideo[REDACTED]";
    }
  }
}

package dev.codex.schubert.nk.migration;

import java.nio.charset.StandardCharsets;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Bind declared Music129 metadata into stored pair/order COPY rows, never real migration
 * acceptance. NK-MIG-001; MIG-DAT-004/MIG-DAT-005/MIG-003/MIG-005/MIG-006/DAT-004;
 * UI223/242/243/254; SS311/331/333/343 SSC361; PT-MIG-MUSICCAT001..024.
 */
@NullMarked
public final class MusicMigrationCatalogue {
  private static final int CURRENT_MUSIC_FILES = 129;
  private static final long MINIMUM_TARGET_ID = 1;
  private static final long MAXIMUM_TARGET_ID = 999999999999L;
  private static final String SONG_CATEGORY = "曲";
  private static final Map<String, String> MIMES =
      Map.of(
          ".m4a",
          "audio/mp4",
          ".mp3",
          "audio/mpeg",
          ".ogg",
          "audio/ogg",
          ".wav",
          "audio/wav",
          ".flac",
          "audio/flac");

  public List<MediaAssetCopyRow> copyRows(
      @Nullable Map<? extends @Nullable String, ? extends @Nullable Long> targetIds,
      @Nullable AssetMigrationManifest declaredMusic,
      @Nullable String createdAt)
      throws NoSuchAlgorithmException {
    if (targetIds == null || declaredMusic == null || createdAt == null) throw invalid();
    var ids = new HashMap<@Nullable String, @Nullable Long>(targetIds);
    if (ids.size() != CURRENT_MUSIC_FILES || declaredMusic.entries().size() != CURRENT_MUSIC_FILES)
      throw invalid();
    var entries = new ArrayList<>(declaredMusic.entries());
    for (var entry : entries)
      if (entry.kind() != AssetMigrationManifest.Kind.MUSIC) throw invalid();
    entries.sort((left, right) -> comparePaths(left.currentPath(), right.currentPath()));
    var groups = new LinkedHashMap<String, List<AssetMigrationManifest.Entry>>();
    for (var entry : entries) {
      String[] parts = entry.currentPath().split("/");
      String section = parts.length > 1 ? parts[1] : "";
      // Manifest paths reject control characters, so the separator cannot collide with either name.
      String group = parts[0] + '\n' + section;
      groups.computeIfAbsent(group, ignored -> new ArrayList<>()).add(entry);
    }
    var usedIds = new HashSet<Long>();
    var rows = new ArrayList<MediaAssetCopyRow>();
    for (var group : groups.values()) {
      String[] parts = group.getFirst().currentPath().split("/");
      String category = parts[0];
      String section = parts.length > 1 ? parts[1] : "";
      int order = 1;
      if (category.equals(SONG_CATEGORY)) {
        var titles = new LinkedHashMap<String, String>();
        for (var entry : group) titles.put(entry.currentPath(), title(entry.currentPath()));
        var paired = new MusicMigrationPairing().plan(titles);
        if (!paired.shadowedPaths().isEmpty()) throw invalid();
        for (var pair : paired.pairs()) {
          if (pair.key().isEmpty()) throw invalid();
          for (var entry : group) {
            if (pair.mainDisplayPath().filter(entry.currentPath()::equals).isPresent()) {
              rows.add(
                  row(entry, ids, usedIds, category, section, pair.key(), "M", order, createdAt));
            } else if (pair.instrumentalDisplayPath()
                .filter(entry.currentPath()::equals)
                .isPresent()) {
              rows.add(
                  row(entry, ids, usedIds, category, section, pair.key(), "I", order, createdAt));
            }
          }
          order++;
        }
      } else {
        for (var entry : group) {
          rows.add(row(entry, ids, usedIds, category, section, null, "N", order, createdAt));
          order++;
        }
      }
    }
    rows.sort((left, right) -> comparePaths(left.displayPath(), right.displayPath()));
    return List.copyOf(rows);
  }

  @Override
  public String toString() {
    return "MusicMigrationCatalogue[REDACTED]";
  }

  private static MediaAssetCopyRow row(
      AssetMigrationManifest.Entry entry,
      Map<@Nullable String, @Nullable Long> ids,
      HashSet<Long> usedIds,
      String category,
      String section,
      @Nullable String pairKey,
      String role,
      int order,
      String createdAt)
      throws NoSuchAlgorithmException {
    String logicalId = new MusicLogicalId().fromDisplayPath(entry.currentPath());
    @Nullable Long id = ids.get(logicalId);
    if (id == null || id < MINIMUM_TARGET_ID || id > MAXIMUM_TARGET_ID || !usedIds.add(id))
      throw invalid();
    String path = entry.currentPath();
    String name = path.substring(path.lastIndexOf('/') + 1);
    int dot = name.lastIndexOf('.');
    @Nullable String mime = dot < 0 ? null : MIMES.get(name.substring(dot));
    if (mime == null) throw invalid();
    return new MediaAssetCopyRow(
        Arrays.<@Nullable String>asList(
            Long.toString(id),
            logicalId,
            "MUSIC",
            title(path),
            category,
            section,
            entry.targetPath(),
            path,
            name,
            Long.toString(entry.byteLength()),
            entry.sha256(),
            mime,
            null,
            pairKey,
            role,
            Integer.toString(order),
            createdAt));
  }

  private static String title(String path) {
    String name = path.substring(path.lastIndexOf('/') + 1);
    int dot = name.lastIndexOf('.');
    return dot > 0 ? name.substring(0, dot) : name;
  }

  private static int comparePaths(String left, String right) {
    return Arrays.compareUnsigned(
        left.getBytes(StandardCharsets.UTF_8), right.getBytes(StandardCharsets.UTF_8));
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration music catalogue input is invalid");
  }
}

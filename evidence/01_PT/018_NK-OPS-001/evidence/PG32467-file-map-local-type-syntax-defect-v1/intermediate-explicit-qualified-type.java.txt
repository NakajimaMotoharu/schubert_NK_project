package dev.codex.schubert.nk.migration;

import java.text.Normalizer;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Current eight-column values plus declared game-root/asset claims to COPY; no FS/DB authority.
 * NK-MIG-001; MIG003005006/MIG-DAT005/FUN004/DAT004/TST; UI223242254; SS311331/V002/343 SSC392;
 * PT-MIG-FILEMAP001..024. Metadata agreement never qualifies a real file, root, hash or migration.
 */
@NullMarked
public final class CurrentScenarioFileMapper {
  private static final int CURRENT_COLUMNS = 8;
  private static final int NANOSECONDS_PER_MICROSECOND = 1000;
  private static final String CURRENT_ID_PATTERN = "0|-?[1-9][0-9]{0,18}";
  private static final Instant EARLIEST = Instant.parse("0001-01-01T00:00:00Z");
  private static final Instant LATEST = Instant.parse("9999-12-31T23:59:59.999999Z");
  private final ScenarioFileMigrationMap retainedFiles;
  private final Map<String, AssetMigrationManifest.Entry> retainedScenarioAssets;
  private final String retainedGameOneRoot;
  private final String retainedGameTwoRoot;

  public CurrentScenarioFileMapper(
      @Nullable ScenarioFileMigrationMap files,
      @Nullable AssetMigrationManifest assets,
      @Nullable String gameOneRoot,
      @Nullable String gameTwoRoot) {
    if (files == null || assets == null) throw invalid();
    String one = root(gameOneRoot);
    String two = root(gameTwoRoot);
    if (one.equals(two)) throw invalid();
    var byPath = new HashMap<String, AssetMigrationManifest.Entry>();
    for (var asset : assets.entries())
      if (asset.kind() == AssetMigrationManifest.Kind.SCENARIO)
        byPath.put(asset.currentPath(), asset);
    if (byPath.size() != files.files().size()) throw invalid();
    retainedFiles = files;
    retainedScenarioAssets = Map.copyOf(byPath);
    retainedGameOneRoot = one;
    retainedGameTwoRoot = two;
  }

  public ScenarioFileCopyBatch copyRows(
      @Nullable List<? extends @Nullable List<@Nullable String>> currentRows,
      @Nullable Instant migratedAt) {
    if (currentRows == null || migratedAt == null) throw invalid();
    validTime(migratedAt);
    var data = new ArrayList<>(currentRows);
    if (data.size() != retainedFiles.files().size()) throw invalid();
    var assets = new HashMap<>(retainedScenarioAssets);
    var ids = new HashSet<Long>();
    var byTarget = new HashMap<Long, List<@Nullable String>>();
    for (@Nullable List<@Nullable String> source : data) {
      if (source == null) throw invalid();
      var row = new ArrayList<@Nullable String>(source);
      if (row.size() != CURRENT_COLUMNS) throw invalid();
      long id = parseCurrent(row.get(0));
      int game = game(row.get(1));
      var file = retainedFiles.lookup(game, id);
      if (!ids.add(id)) throw invalid();
      String relativePath = required(row.get(2));
      String prefix = game == 1 ? retainedGameOneRoot : retainedGameTwoRoot;
      @Nullable AssetMigrationManifest.Entry asset = assets.remove(prefix + "/" + relativePath);
      if (asset == null) throw invalid();
      @Nullable String sourceHash = row.get(6);
      if (sourceHash != null && !sourceHash.equals(asset.sha256())) throw invalid();
      @Nullable String sourceSize = row.get(7);
      if (sourceSize != null && parseCurrent(sourceSize) != asset.byteLength()) throw invalid();
      var target = new ArrayList<@Nullable String>();
      target.add(Long.toString(file.targetFileId()));
      target.add(Integer.toString(game));
      target.add(Long.toString(file.displayOrder()));
      target.add(asset.targetPath());
      target.add(relativePath);
      target.add(required(row.get(3)));
      target.add(row.get(4));
      target.add(row.get(5));
      target.add(asset.sha256());
      target.add(Long.toString(asset.byteLength()));
      target.add(migratedAt.toString());
      byTarget.put(file.targetFileId(), target);
    }
    var ordered = new ArrayList<List<@Nullable String>>();
    // Equal known unique source membership and one-use asset claims establish full bijections.
    for (var file : retainedFiles.files())
      ordered.add(Objects.requireNonNull(byTarget.get(file.targetFileId())));
    return new ScenarioFileCopyBatch(retainedFiles, ordered);
  }

  private static int game(@Nullable String value) {
    if ("1".equals(value)) return 1;
    if ("2".equals(value)) return 2;
    throw invalid();
  }

  private static String required(@Nullable String value) {
    if (value == null) throw invalid();
    return value;
  }

  private static long parseCurrent(@Nullable String value) {
    if (value == null || !value.matches(CURRENT_ID_PATTERN)) throw invalid();
    try {
      return Long.parseLong(value);
    } catch (NumberFormatException failure) {
      throw invalid();
    }
  }

  private static String root(@Nullable String value) {
    if (value == null
        || value.isEmpty()
        || value.startsWith("/")
        || value.endsWith("/")
        || value.contains("\\")
        || !Normalizer.isNormalized(value, Normalizer.Form.NFC)
        || value.codePoints().anyMatch(CurrentScenarioFileMapper::invalidScalar)) throw invalid();
    for (String segment : value.split("/", -1))
      if (segment.isEmpty() || segment.equals(".") || segment.equals("..")) throw invalid();
    return value;
  }

  private static boolean invalidScalar(int point) {
    return Character.isISOControl(point)
        || (point >= Character.MIN_SURROGATE && point <= Character.MAX_SURROGATE);
  }

  private static void validTime(Instant value) {
    if (value.isBefore(EARLIEST)
        || value.isAfter(LATEST)
        || value.getNano() % NANOSECONDS_PER_MICROSECOND != 0) throw invalid();
  }

  @Override
  public String toString() {
    return "CurrentScenarioFileMapper[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration file conversion is invalid");
  }
}

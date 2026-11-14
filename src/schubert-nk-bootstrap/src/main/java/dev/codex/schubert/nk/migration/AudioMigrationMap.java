package dev.codex.schubert.nk.migration;

import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Declared Current audio ID/asset/duration adapter, never actual file or DB qualification.
 * NK-MIG-001; MIG003005006/MIG-DAT002005/FUN005/DAT004/TST; UI227242254; SS311331/V002/V030/343
 * SSC398; PT-MIG-AUDIOMAP001..024. Preserves signed Current ordering and stored text without
 * repair.
 */
@NullMarked
public final class AudioMigrationMap {
  private static final long MAXIMUM_N12 = 999_999_999_999L;
  private static final int CURRENT_COLUMNS = 10;
  private static final int MILLISECOND_SCALE = 3;
  private static final int NANOSECONDS_PER_MICROSECOND = 1000;
  private static final String GAME_ONE_TEXT = "1";
  private static final String GAME_TWO_TEXT = "2";
  private static final String CURRENT_ID_PATTERN = "0|-?[1-9][0-9]{0,18}";
  private static final String DURATION_PATTERN = "-?(0|[1-9][0-9]{0,8})(\\.[0-9]{1,3})?";
  private static final Instant EARLIEST = Instant.parse("0001-01-01T00:00:00Z");
  private static final Instant LATEST = Instant.parse("9999-12-31T23:59:59.999999Z");

  public record AudioMapping(int gameId, long currentAudioId, long targetAudioId) {
    public AudioMapping {
      if (gameId < 1 || gameId > 2 || targetAudioId < 1 || targetAudioId > MAXIMUM_N12)
        throw invalid();
    }

    @Override
    public String toString() {
      return "AudioMapping[REDACTED]";
    }
  }

  private final List<AudioMapping> retainedMappings;
  private final Map<Long, AudioMapping> retainedByCurrent;
  private final Map<String, AssetMigrationManifest.Entry> retainedAudioAssets;
  private final String retainedGameOneRoot;
  private final String retainedGameTwoRoot;

  public AudioMigrationMap(
      @Nullable List<@Nullable AudioMapping> input,
      @Nullable AssetMigrationManifest assets,
      @Nullable String gameOneRoot,
      @Nullable String gameTwoRoot) {
    if (input == null || assets == null) throw invalid();
    String one = root(gameOneRoot);
    String two = root(gameTwoRoot);
    if (one.equals(two)) throw invalid();
    var sorted = new ArrayList<AudioMapping>();
    for (@Nullable AudioMapping item : input) {
      if (item == null) throw invalid();
      sorted.add(item);
    }
    sorted.sort(Comparator.comparingLong(AudioMapping::currentAudioId));
    var byId = new HashMap<Long, AudioMapping>();
    long previousTarget = 0;
    for (var item : sorted) {
      if (byId.putIfAbsent(item.currentAudioId(), item) != null
          || item.targetAudioId() <= previousTarget) throw invalid();
      previousTarget = item.targetAudioId();
    }
    var byPath = new HashMap<String, AssetMigrationManifest.Entry>();
    for (var asset : assets.entries())
      if (asset.kind() == AssetMigrationManifest.Kind.AUDIO) byPath.put(asset.currentPath(), asset);
    if (byPath.size() != sorted.size()) throw invalid();
    retainedMappings = List.copyOf(sorted);
    retainedByCurrent = Map.copyOf(byId);
    retainedAudioAssets = Map.copyOf(byPath);
    retainedGameOneRoot = one;
    retainedGameTwoRoot = two;
  }

  public List<AudioMapping> mappings() {
    return retainedMappings;
  }

  public long targetAudioId(int gameId, long currentAudioId) {
    @Nullable AudioMapping item = retainedByCurrent.get(currentAudioId);
    if (item == null || item.gameId() != gameId) throw invalid();
    return item.targetAudioId();
  }

  public byte[] canonicalBytes() {
    var text = new StringBuilder("game_id\tcurrent_audio_id\ttarget_audio_id\n");
    for (var item : retainedMappings)
      text.append(item.gameId())
          .append('\t')
          .append(item.currentAudioId())
          .append('\t')
          .append(item.targetAudioId())
          .append('\n');
    return text.toString().getBytes(StandardCharsets.UTF_8);
  }

  public List<AudioFileCopyRow> copyRows(
      @Nullable List<? extends @Nullable List<@Nullable String>> currentRows,
      @Nullable Instant migratedAt) {
    if (currentRows == null || migratedAt == null) throw invalid();
    if (migratedAt.isBefore(EARLIEST)
        || migratedAt.isAfter(LATEST)
        || migratedAt.getNano() % NANOSECONDS_PER_MICROSECOND != 0) throw invalid();
    var data = new ArrayList<>(currentRows);
    if (data.size() != retainedMappings.size()) throw invalid();
    var assets = new HashMap<>(retainedAudioAssets);
    var ids = new HashSet<Long>();
    var byId = new HashMap<Long, AudioFileCopyRow>();
    for (@Nullable List<@Nullable String> source : data) {
      if (source == null) throw invalid();
      var row = new ArrayList<@Nullable String>(source);
      if (row.size() != CURRENT_COLUMNS) throw invalid();
      long id = parseCurrent(row.get(0));
      int game = game(row.get(1));
      long targetId = targetAudioId(game, id);
      if (!ids.add(id)) throw invalid();
      String relativePath = required(row.get(2));
      String prefix = game == 1 ? retainedGameOneRoot : retainedGameTwoRoot;
      AssetMigrationManifest.@Nullable Entry asset = assets.remove(prefix + "/" + relativePath);
      if (asset == null) throw invalid();
      @Nullable String sourceHash = row.get(9);
      if (sourceHash != null && !sourceHash.equals(asset.sha256())) throw invalid();
      @Nullable String sourceSize = row.get(8);
      if (sourceSize != null && parseCurrent(sourceSize) != asset.byteLength()) throw invalid();
      var target = new ArrayList<@Nullable String>();
      target.add(Long.toString(targetId));
      target.add(Integer.toString(game));
      target.add(asset.targetPath());
      target.add(relativePath);
      target.add(required(row.get(3)));
      target.add(required(row.get(4)));
      target.add(required(row.get(5)));
      target.add(row.get(6));
      target.add(duration(row.get(7)));
      target.add(Long.toString(asset.byteLength()));
      target.add(asset.sha256());
      target.add(migratedAt.toString());
      byId.put(id, new AudioFileCopyRow(target));
    }
    var ordered = new ArrayList<AudioFileCopyRow>();
    // Known unique IDs/assets with equal cardinality prove both bijections; no partial output.
    for (var item : retainedMappings)
      ordered.add(Objects.requireNonNull(byId.get(item.currentAudioId())));
    return List.copyOf(ordered);
  }

  private static String root(@Nullable String value) {
    if (value == null) throw invalid();
    try {
      AssetMigrationManifest.path(value);
    } catch (IllegalArgumentException failure) {
      throw invalid();
    }
    return value;
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

  private static int game(@Nullable String value) {
    if (GAME_ONE_TEXT.equals(value)) return 1;
    if (GAME_TWO_TEXT.equals(value)) return 2;
    throw invalid();
  }

  private static @Nullable String duration(@Nullable String value) {
    if (value == null) return null;
    if (!value.matches(DURATION_PATTERN)) throw invalid();
    var decimal = new BigDecimal(value);
    if (!decimal.toPlainString().equals(value)) throw invalid();
    return Long.toString(decimal.movePointRight(MILLISECOND_SCALE).longValueExact());
  }

  @Override
  public String toString() {
    return "AudioMigrationMap[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration audio conversion is invalid");
  }
}

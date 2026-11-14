package dev.codex.schubert.nk.migration;

import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Current-compatible declared pairing within one song group; not actual inventory or DB acceptance.
 * NK-MIG-001; MIG-DAT-004/MIG-DAT-005/MIG-003/MIG-005/MIG-006/DAT-004; UI223/242/243/254;
 * SS311/331/343 SSC360; PT-MIG-MUSICPAIR001..026.
 */
@NullMarked
public final class MusicMigrationPairing {
  private static final int MAXIMUM_PATH_BYTES = 512;
  private static final int MAXIMUM_TITLE_BYTES = 256;
  private static final int OUTSIDE_MATCH_DISTANCE = 3;

  public Result plan(
      @Nullable Map<? extends @Nullable String, ? extends @Nullable String> declaredTracks) {
    if (declaredTracks == null) throw invalid();
    var snapshot = new HashMap<@Nullable String, @Nullable String>(declaredTracks);
    var tracks = new ArrayList<Map.Entry<String, String>>();
    for (var entry : snapshot.entrySet()) {
      @Nullable String path = entry.getKey();
      @Nullable String title = entry.getValue();
      if (path == null || title == null) throw invalid();
      text(path, MAXIMUM_PATH_BYTES);
      text(title, MAXIMUM_TITLE_BYTES);
      path(path);
      tracks.add(Map.entry(path, title));
    }
    // For valid UTF-8 scalars this is Unicode codepoint order, including supplementary characters.
    tracks.sort(
        (left, right) ->
            Arrays.compareUnsigned(
                left.getKey().getBytes(StandardCharsets.UTF_8),
                right.getKey().getBytes(StandardCharsets.UTF_8)));
    var mains = new LinkedHashMap<String, Map.Entry<String, String>>();
    var instrumentals = new LinkedHashMap<String, Map.Entry<String, String>>();
    var shadowed = new ArrayList<String>();
    for (var track : tracks) {
      var destination = instrumental(track.getValue()) ? instrumentals : mains;
      Map.@Nullable Entry<String, String> previous = destination.put(key(track.getValue()), track);
      // Current put overwrites a colliding value without moving its original key position.
      if (previous != null) shadowed.add(previous.getKey());
    }
    var pairs = new ArrayList<Pair>();
    for (var main : mains.values()) {
      String pairKey = key(main.getValue());
      Map.@Nullable Entry<String, String> inst = instrumentals.remove(pairKey);
      if (inst == null) inst = closest(pairKey, instrumentals);
      pairs.add(
          new Pair(
              displayTitle(main.getValue()),
              pairKey,
              main.getKey(),
              inst == null ? null : inst.getKey()));
    }
    for (var inst : instrumentals.values()) {
      pairs.add(new Pair(displayTitle(inst.getValue()), key(inst.getValue()), null, inst.getKey()));
    }
    return new Result(pairs, shadowed);
  }

  @Override
  public String toString() {
    return "MusicMigrationPairing[REDACTED]";
  }

  private static boolean instrumental(String title) {
    String lower = title.toLowerCase(Locale.getDefault());
    // instrument implies inst; the first predicate exactly represents Current's OR.
    return lower.contains("inst");
  }

  private static String displayTitle(String title) {
    return title
        .replaceFirst("^\\d+-\\d+\\s+", "")
        .replaceAll("(?i)\\s*[\\(（][^\\)）]*(?:inst|instrument)[^\\)）]*[\\)）]?.*$", "")
        .replaceAll("(?i)\\s+(?:inst|instrument).*$", "")
        .trim();
  }

  private static String key(String title) {
    return displayTitle(title)
        .toLowerCase(Locale.getDefault())
        .replaceAll("[\\s　_＿!！+＋^\\[\\]【】()（）.,.．・'’`´-]+", "");
  }

  private static Map.@Nullable Entry<String, String> closest(
      String key, LinkedHashMap<String, Map.Entry<String, String>> remaining) {
    @Nullable String best = null;
    int bestDistance = OUTSIDE_MATCH_DISTANCE;
    for (String candidate : remaining.keySet()) {
      int distance = distance(key, candidate);
      if (distance < bestDistance) {
        best = candidate;
        bestDistance = distance;
      }
    }
    return best == null ? null : remaining.remove(best);
  }

  private static int distance(String left, String right) {
    int[] previous = new int[right.length() + 1];
    int[] current = new int[right.length() + 1];
    for (int column = 0; column <= right.length(); column++) previous[column] = column;
    for (int row = 1; row <= left.length(); row++) {
      current[0] = row;
      for (int column = 1; column <= right.length(); column++) {
        int cost = left.charAt(row - 1) == right.charAt(column - 1) ? 0 : 1;
        current[column] =
            Math.min(
                Math.min(current[column - 1] + 1, previous[column] + 1),
                previous[column - 1] + cost);
      }
      int[] swap = previous;
      previous = current;
      current = swap;
    }
    return previous[right.length()];
  }

  private static void text(String value, int limit) {
    if (!StandardCharsets.UTF_8.newEncoder().canEncode(value)) throw invalid();
    if (!Normalizer.isNormalized(value, Normalizer.Form.NFC)) throw invalid();
    int bytes = value.getBytes(StandardCharsets.UTF_8).length;
    if (bytes == 0 || bytes > limit) throw invalid();
    for (int i = 0; i < value.length(); i++)
      if (Character.isISOControl(value.charAt(i))) throw invalid();
  }

  private static void path(String value) {
    if (value.startsWith("/") || value.endsWith("/") || value.contains("\\")) throw invalid();
    for (String segment : value.split("/", -1))
      if (segment.isEmpty() || segment.equals(".") || segment.equals("..")) throw invalid();
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration music pairing input is invalid");
  }

  public static final class Pair {
    private final String retainedTitle;
    private final String retainedKey;
    private final @Nullable String retainedMain;
    private final @Nullable String retainedInstrumental;

    private Pair(String title, String key, @Nullable String main, @Nullable String instrumental) {
      retainedTitle = title;
      retainedKey = key;
      retainedMain = main;
      retainedInstrumental = instrumental;
    }

    public String title() {
      return retainedTitle;
    }

    public String key() {
      return retainedKey;
    }

    public Optional<String> mainDisplayPath() {
      return Optional.ofNullable(retainedMain);
    }

    public Optional<String> instrumentalDisplayPath() {
      return Optional.ofNullable(retainedInstrumental);
    }

    @Override
    public String toString() {
      return "MigrationMusicPair[REDACTED]";
    }
  }

  public static final class Result {
    private final List<Pair> retainedPairs;
    private final List<String> retainedShadowed;

    private Result(List<Pair> pairs, List<String> shadowed) {
      retainedPairs = List.copyOf(pairs);
      retainedShadowed = List.copyOf(shadowed);
    }

    public List<Pair> pairs() {
      return retainedPairs;
    }

    public List<String> shadowedPaths() {
      return retainedShadowed;
    }

    @Override
    public String toString() {
      return "MigrationMusicPairingResult[REDACTED]";
    }
  }
}

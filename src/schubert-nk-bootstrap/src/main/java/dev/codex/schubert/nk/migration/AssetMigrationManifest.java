package dev.codex.schubert.nk.migration;

import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Immutable declared file metadata, never an inode/hash/ETL or migration admission witness.
 * NK-MIG-001; FIL003005/MIG003006; UI254; SS343 SSC342; PT-MIG-ASSET001..012. Callers separately
 * authenticate real observations, full baseline counts, IDs and display order.
 */
@NullMarked
public final class AssetMigrationManifest {
  public enum Kind {
    SCENARIO,
    AUDIO,
    VIDEO,
    MUSIC
  }

  public record Entry(
      Kind kind, String currentPath, String targetPath, long byteLength, String sha256) {
    public Entry {
      Objects.requireNonNull(kind, "asset kind");
      path(currentPath);
      path(targetPath);
      metadata(byteLength, sha256);
    }

    @Override
    public String toString() {
      return "MigrationAssetEntry[REDACTED]";
    }
  }

  public record Observation(String targetPath, long byteLength, String sha256) {
    public Observation {
      path(targetPath);
      metadata(byteLength, sha256);
    }

    @Override
    public String toString() {
      return "MigrationAssetObservation[REDACTED]";
    }
  }

  public record Comparison(
      long missingFiles,
      long unexpectedFiles,
      long sizeMismatches,
      long hashMismatches,
      long observedFiles,
      long observedBytes) {
    public Comparison {
      if (missingFiles < 0
          || unexpectedFiles < 0
          || sizeMismatches < 0
          || hashMismatches < 0
          || observedFiles < 0
          || observedBytes < 0) throw invalid();
    }

    /** Agreement of supplied claims only; not file integrity, migration completion or Go. */
    public boolean metadataMatches() {
      return missingFiles == 0
          && unexpectedFiles == 0
          && sizeMismatches == 0
          && hashMismatches == 0;
    }
  }

  private final List<Entry> retainedEntries;
  private final long byteLength;

  public AssetMigrationManifest(List<Entry> input) {
    var snapshot = List.copyOf(input);
    var currentPaths = new HashSet<String>();
    var targetPaths = new HashSet<String>();
    long bytes = 0;
    for (Entry entry : snapshot) {
      if (!currentPaths.add(entry.currentPath()) || !targetPaths.add(entry.targetPath()))
        throw invalid();
      bytes = sum(bytes, entry.byteLength());
    }
    retainedEntries =
        List.copyOf(snapshot.stream().sorted(Comparator.comparing(Entry::currentPath)).toList());
    byteLength = bytes;
  }

  public List<Entry> entries() {
    return retainedEntries;
  }

  public long totalBytes() {
    return byteLength;
  }

  public byte[] canonicalBytes() {
    var text = new StringBuilder("NKMIGASSET1\n");
    for (Entry entry : retainedEntries) {
      text.append(entry.kind().name())
          .append('\t')
          .append(entry.currentPath())
          .append('\t')
          .append(entry.targetPath())
          .append('\t')
          .append(entry.byteLength())
          .append('\t')
          .append(entry.sha256())
          .append('\n');
    }
    return text.toString().getBytes(StandardCharsets.UTF_8);
  }

  public Comparison compareClaims(List<Observation> input) {
    var observations = List.copyOf(input);
    var byPath = new HashMap<String, Observation>();
    long observedBytes = 0;
    for (Observation observation : observations) {
      if (byPath.putIfAbsent(observation.targetPath(), observation) != null) throw invalid();
      observedBytes = sum(observedBytes, observation.byteLength());
    }
    long missing = 0;
    long size = 0;
    long hash = 0;
    for (Entry entry : retainedEntries) {
      @Nullable Observation observation = byPath.remove(entry.targetPath());
      if (observation == null) {
        missing++;
      } else {
        if (entry.byteLength() != observation.byteLength()) size++;
        if (!entry.sha256().equals(observation.sha256())) hash++;
      }
    }
    return new Comparison(missing, byPath.size(), size, hash, observations.size(), observedBytes);
  }

  @Override
  public String toString() {
    return "AssetMigrationManifest[REDACTED]";
  }

  static void path(String value) {
    Objects.requireNonNull(value, "relative asset path");
    if (value.isEmpty()
        || value.startsWith("/")
        || value.contains("\\")
        || !Normalizer.isNormalized(value, Normalizer.Form.NFC)
        || value.codePoints().anyMatch(AssetMigrationManifest::invalidScalar)) throw invalid();
    for (String segment : value.split("/", -1))
      if (segment.isEmpty() || segment.equals(".") || segment.equals("..")) throw invalid();
  }

  private static boolean invalidScalar(int point) {
    return Character.isISOControl(point)
        || (point >= Character.MIN_SURROGATE && point <= Character.MAX_SURROGATE);
  }

  private static void metadata(long bytes, String hash) {
    Objects.requireNonNull(hash, "asset SHA-256");
    if (bytes < 0 || !hash.matches("[0-9a-f]{64}")) throw invalid();
  }

  private static long sum(long first, long second) {
    try {
      return Math.addExact(first, second);
    } catch (ArithmeticException overflow) {
      throw invalid();
    }
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration asset metadata is invalid");
  }
}

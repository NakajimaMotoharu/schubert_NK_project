package dev.codex.schubert.nk.migration;

import java.io.IOException;
import java.io.OutputStream;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import javax.annotation.concurrent.Immutable;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Streamed declared COPY metadata, never actual master/DB/authorization acceptance. NK-MIG-001;
 * MIG-DAT005/MIG003005006/FUN004/DAT004/TST; UI223242254; SS311/331/V002/343 SSC374;
 * PT-MIG-FINGER001..020. All six digests/counters are owned memory values, never retained wire.
 */
@NullMarked
public final class MigrationMasterCopyFingerprint {
  private static final List<String> TABLE_NAMES =
      List.of(
          "speakers",
          "script_files",
          "script_entries",
          "audio_files",
          "media_assets",
          "entry_audio_links");

  public List<TableFingerprint> fingerprint(@Nullable MigrationMasterCopyDataset declared)
      throws IOException, NoSuchAlgorithmException {
    if (declared == null) throw invalid();
    var content = declared.content();
    var rows =
        List.of(
            (long) declared.speakers().rows().size(),
            (long) content.scenario().files().rows().size(),
            (long) content.scenario().entries().rows().size(),
            (long) content.audio().audioRows().size(),
            (long) content.media().rows().size(),
            (long) content.audio().linkRows().size());
    var sinks = new ArrayList<DigestSink>();
    for (int index = 0; index < TABLE_NAMES.size(); index++) sinks.add(new DigestSink());
    declared.writeAll(
        new PostgresCopyTextWriter(new PostgresCopyTextEncoder()),
        sinks.get(0),
        sinks.get(1),
        sinks.get(2),
        sinks.get(3),
        sinks.get(4),
        sinks.get(5));
    var result = new ArrayList<TableFingerprint>();
    for (int index = 0; index < TABLE_NAMES.size(); index++) {
      var sink = sinks.get(index);
      result.add(
          new TableFingerprint(TABLE_NAMES.get(index), rows.get(index), sink.count, sink.finish()));
    }
    return List.copyOf(result);
  }

  public List<String> difference(
      @Nullable MigrationMasterCopyDataset expected, @Nullable MigrationMasterCopyDataset actual)
      throws IOException, NoSuchAlgorithmException {
    if (expected == null || actual == null) throw invalid();
    var before = fingerprint(expected);
    var after = fingerprint(actual);
    var differences = new ArrayList<String>();
    for (int index = 0; index < TABLE_NAMES.size(); index++) {
      var left = before.get(index);
      var right = after.get(index);
      if (left.rows() != right.rows()
          || left.bytes() != right.bytes()
          || !left.sha256().equals(right.sha256())) differences.add(TABLE_NAMES.get(index));
    }
    return List.copyOf(differences);
  }

  @Override
  public String toString() {
    return "MigrationMasterCopyFingerprint[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration COPY fingerprint input is invalid");
  }

  /**
   * Private construction establishes fixed table names, nonnegative counts and owned SHA output.
   */
  @Immutable
  public static final class TableFingerprint {
    private final String retainedTable;
    private final long retainedRows;
    private final long retainedBytes;
    private final String retainedSha256;

    private TableFingerprint(String table, long rows, long bytes, String sha256) {
      retainedTable = table;
      retainedRows = rows;
      retainedBytes = bytes;
      retainedSha256 = sha256;
    }

    public String table() {
      return retainedTable;
    }

    public long rows() {
      return retainedRows;
    }

    public long bytes() {
      return retainedBytes;
    }

    public String sha256() {
      return retainedSha256;
    }

    @Override
    public String toString() {
      return "TableFingerprint[REDACTED]";
    }
  }

  private static final class DigestSink extends OutputStream {
    private final MessageDigest digest;
    private long count;

    private DigestSink() throws NoSuchAlgorithmException {
      // SHA-256 is mandatory in the pinned Java25 environment; provider failure propagates.
      digest = MessageDigest.getInstance("SHA-256");
    }

    @Override
    public void write(int value) {
      digest.update((byte) value);
      count = Math.incrementExact(count);
    }

    private String finish() {
      return HexFormat.of().formatHex(digest.digest());
    }
  }
}

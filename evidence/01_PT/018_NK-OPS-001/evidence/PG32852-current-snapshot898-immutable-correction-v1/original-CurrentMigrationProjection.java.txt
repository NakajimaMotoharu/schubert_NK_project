package dev.codex.schubert.nk.migration;

import java.sql.Connection;
import java.sql.SQLException;
import java.util.List;
import javax.annotation.concurrent.Immutable;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Coordinates five readers on a caller-owned connection; no real snapshot or migration witness.
 * NK-MIG-001; MIG003005006/MIG-DAT001002005/DAT004/TST; UI242254; SS311331343 SSC401;
 * PT-MIG-CURRENTSNAPSHOT001..012. Caller already authenticates and exclusively owns the
 * transaction.
 */
@NullMarked
public final class CurrentMigrationProjection {
  @Immutable
  public static final class SourceSnapshot {
    private final List<List<@Nullable String>> retainedSpeakers;
    private final List<List<@Nullable String>> retainedFiles;
    private final List<List<@Nullable String>> retainedEntries;
    private final List<List<@Nullable String>> retainedAudio;
    private final List<List<@Nullable String>> retainedLinks;

    private SourceSnapshot(
        List<List<@Nullable String>> speakers,
        List<List<@Nullable String>> files,
        List<List<@Nullable String>> entries,
        List<List<@Nullable String>> audio,
        List<List<@Nullable String>> links) {
      // Only the five final readers produce these already deep-immutable values. No public factory.
      retainedSpeakers = speakers;
      retainedFiles = files;
      retainedEntries = entries;
      retainedAudio = audio;
      retainedLinks = links;
    }

    public List<List<@Nullable String>> speakers() {
      return retainedSpeakers;
    }

    public List<List<@Nullable String>> files() {
      return retainedFiles;
    }

    public List<List<@Nullable String>> entries() {
      return retainedEntries;
    }

    public List<List<@Nullable String>> audio() {
      return retainedAudio;
    }

    public List<List<@Nullable String>> links() {
      return retainedLinks;
    }

    @Override
    public String toString() {
      return "CurrentSourceSnapshot[REDACTED]";
    }
  }

  public SourceSnapshot read(
      @Nullable Connection connection,
      int expectedSpeakers,
      int expectedFiles,
      int expectedEntries,
      int expectedAudio,
      int expectedLinks)
      throws SQLException {
    if (connection == null
        || expectedSpeakers < 0
        || expectedFiles < 0
        || expectedEntries < 0
        || expectedAudio < 0
        || expectedLinks < 0)
      throw new IllegalArgumentException("migration source snapshot input is invalid");
    int initialMode = snapshotMode(connection);
    var speakers = new CurrentSpeakerProjectionReader().read(connection, expectedSpeakers);
    var files = new CurrentScenarioFileProjectionReader().read(connection, expectedFiles);
    var entries = new CurrentScenarioEntryProjectionReader().read(connection, expectedEntries);
    var audio = new CurrentAudioProjectionReader().read(connection, expectedAudio);
    var links = new CurrentAudioLinkProjectionReader().read(connection, expectedLinks);
    if (snapshotMode(connection) != initialMode) throw invalid();
    return new SourceSnapshot(speakers, files, entries, audio, links);
  }

  private static int snapshotMode(Connection connection) throws SQLException {
    if (connection.getAutoCommit() || !connection.isReadOnly()) throw invalid();
    int mode = connection.getTransactionIsolation();
    if (mode != Connection.TRANSACTION_REPEATABLE_READ
        && mode != Connection.TRANSACTION_SERIALIZABLE) throw invalid();
    return mode;
  }

  @Override
  public String toString() {
    return "CurrentMigrationProjection[REDACTED]";
  }

  private static SQLException invalid() {
    return new SQLException("migration source snapshot attributes are invalid");
  }
}

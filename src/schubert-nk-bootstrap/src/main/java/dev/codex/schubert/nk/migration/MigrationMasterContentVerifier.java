package dev.codex.schubert.nk.migration;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Objects;
import javax.annotation.concurrent.Immutable;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Compare all declared COPY payload columns through borrowed migration-transaction SELECTs.
 * NK-MIG-001; MIG003005006/MIG-DAT005/FUN004/DAT004/TST; UI223242254; SS311/331/V002/343 SSC378;
 * PT-MIG-CONTENT001..028. No transaction, actor, catalog, generated-column or DB qualification.
 */
@NullMarked
@Immutable
public final class MigrationMasterContentVerifier {
  private static final int QUERY_TIMEOUT_SECONDS = 30;
  private static final int FETCH_ROWS = 1000;
  private static final int LINK_TABLE = 5;
  private static final List<String> QUERIES =
      List.of(
          "SELECT id,game_id,name,normalized_name,is_protagonist,notes,created_at FROM schubert.speakers ORDER BY id",
          "SELECT id,game_id,display_order,storage_relative_path,display_path,file_name,section_code,chapter_title,sha256,byte_size,created_at FROM schubert.script_files ORDER BY id",
          "SELECT id,game_id,script_file_id,display_order,entry_index,line_number,entry_type,speaker_id,speaker_label,body,raw_block,created_at FROM schubert.script_entries ORDER BY id",
          "SELECT id,game_id,storage_relative_path,display_path,file_name,basename,audio_role,container,duration_ms,byte_size,sha256,created_at FROM schubert.audio_files ORDER BY id",
          "SELECT id,logical_id,media_type,title,category,section,storage_relative_path,display_path,file_name,byte_size,sha256,mime_type,parent_logical_id,pair_key,pair_role,display_order,created_at FROM schubert.media_assets ORDER BY id",
          "SELECT entry_id,audio_file_id,game_id,link_type,display_order,created_at FROM schubert.entry_audio_links ORDER BY entry_id,audio_file_id,link_type COLLATE \"C\"");
  private static final List<String> KINDS =
      List.of(
          "LISSBST", "LILSSSSSSLT", "LILLIISLSSST", "LISSSSSSLLST", "LSSSSSSSSLSSSSSIT", "LLISIT");

  public void verify(@Nullable Connection connection, @Nullable MigrationMasterCopyDataset declared)
      throws SQLException {
    if (connection == null || declared == null) throw invalidInput();
    if (connection.getAutoCommit()) throw invalid();
    var tables = expectedRows(declared);
    Statement statement = requireStatement(connection.createStatement());
    @Nullable Throwable primary = null;
    try {
      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);
      statement.setFetchSize(FETCH_ROWS);
      for (int table = 0; table < QUERIES.size(); table++) {
        var expected = orderedRows(tables.get(table), table);
        verifyRows(statement.executeQuery(QUERIES.get(table)), expected, KINDS.get(table));
      }
    } catch (SQLException | RuntimeException | Error failure) {
      primary = failure;
      throw failure;
    } finally {
      closeStatement(statement, primary);
    }
  }

  private static List<List<List<@Nullable String>>> expectedRows(
      MigrationMasterCopyDataset declared) {
    var content = declared.content();
    return List.of(
        declared.speakers().rows().stream().map(SpeakerCopyRow::fields).toList(),
        content.scenario().files().rows(),
        content.scenario().entries().rows().stream().map(ScenarioEntryCopyRow::fields).toList(),
        content.audio().audioRows().stream().map(AudioFileCopyRow::fields).toList(),
        content.media().rows().stream().map(MediaAssetCopyRow::fields).toList(),
        content.audio().linkRows());
  }

  private static List<List<@Nullable String>> orderedRows(
      List<List<@Nullable String>> declaredRows, int table) {
    var ordered = new ArrayList<List<@Nullable String>>(declaredRows);
    // Final Row/Batch constructors have established nonnull positive numeric primary keys.
    Comparator<List<@Nullable String>> order =
        Comparator.comparingLong(row -> Long.parseLong(Objects.requireNonNull(row.get(0))));
    if (table == LINK_TABLE) {
      order =
          order
              .thenComparingLong(row -> Long.parseLong(Objects.requireNonNull(row.get(1))))
              .thenComparing(row -> Objects.requireNonNull(row.get(3)));
    }
    ordered.sort(order);
    return List.copyOf(ordered);
  }

  private static Statement requireStatement(@Nullable Statement created) throws SQLException {
    if (created == null) throw invalid();
    return created;
  }

  private static void verifyRows(
      @Nullable ResultSet created, List<List<@Nullable String>> expected, String kinds)
      throws SQLException {
    if (created == null) throw invalid();
    ResultSet result = created;
    @Nullable Throwable primary = null;
    try {
      for (var row : expected) {
        if (!result.next()) throw invalid();
        for (int column = 0; column < kinds.length(); column++) {
          @Nullable String actual = value(result, column + 1, kinds.charAt(column));
          if (!Objects.equals(row.get(column), actual)) throw invalid();
        }
      }
      if (result.next()) throw invalid();
    } catch (SQLException | RuntimeException | Error failure) {
      primary = failure;
      throw failure;
    } finally {
      closeResult(result, primary);
    }
  }

  private static @Nullable String value(ResultSet result, int column, char kind)
      throws SQLException {
    if (kind == 'L') {
      long actual = result.getLong(column);
      return result.wasNull() ? null : Long.toString(actual);
    }
    if (kind == 'I') {
      int actual = result.getInt(column);
      return result.wasNull() ? null : Integer.toString(actual);
    }
    if (kind == 'B') {
      boolean actual = result.getBoolean(column);
      return result.wasNull() ? null : Boolean.toString(actual);
    }
    if (kind == 'T') {
      @Nullable Timestamp actual = result.getTimestamp(column);
      return actual == null ? null : actual.toInstant().toString();
    }
    return result.getString(column);
  }

  private static void closeStatement(Statement resource, @Nullable Throwable primary)
      throws SQLException {
    if (primary == null) {
      resource.close();
      return;
    }
    try {
      resource.close();
    } catch (SQLException | RuntimeException | Error cleanup) {
      if (cleanup != primary) primary.addSuppressed(cleanup);
    }
  }

  private static void closeResult(ResultSet resource, @Nullable Throwable primary)
      throws SQLException {
    if (primary == null) {
      resource.close();
      return;
    }
    try {
      resource.close();
    } catch (SQLException | RuntimeException | Error cleanup) {
      if (cleanup != primary) primary.addSuppressed(cleanup);
    }
  }

  private static SQLException invalid() {
    return new SQLException("migration master content verification is invalid");
  }

  private static IllegalArgumentException invalidInput() {
    return new IllegalArgumentException("migration master content input is invalid");
  }

  @Override
  public String toString() {
    return "MigrationMasterContentVerifier[REDACTED]";
  }
}

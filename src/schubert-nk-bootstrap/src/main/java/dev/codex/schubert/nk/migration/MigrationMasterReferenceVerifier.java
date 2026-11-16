package dev.codex.schubert.nk.migration;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Read-only count/reference/order and stored constraint checks, never full catalog/data/migration
 * acceptance. NK-MIG-001; MIG003005006/MIG-DAT005/FUN004/DAT004/TST; UI223242254;
 * SS311/331/V002/343 SSC372/377/385/386; PT-MIG-REF001..021. Caller retains authentication,
 * exclusive loading and the transaction.
 */
@NullMarked
public final class MigrationMasterReferenceVerifier {
  private static final int QUERY_TIMEOUT_SECONDS = 30;
  private static final List<SqlQuery> COUNTS =
      List.of(
          statement -> statement.executeQuery("SELECT count(*) FROM schubert.speakers"),
          statement -> statement.executeQuery("SELECT count(*) FROM schubert.script_files"),
          statement -> statement.executeQuery("SELECT count(*) FROM schubert.script_entries"),
          statement -> statement.executeQuery("SELECT count(*) FROM schubert.audio_files"),
          statement -> statement.executeQuery("SELECT count(*) FROM schubert.media_assets"),
          statement -> statement.executeQuery("SELECT count(*) FROM schubert.entry_audio_links"));
  private static final List<SqlQuery> INSPECTIONS =
      List.of(
          statement ->
              statement.executeQuery(
                  "SELECT count(*) FROM schubert.script_files c LEFT JOIN schubert.games p ON p.id=c.game_id WHERE p.id IS NULL"),
          statement ->
              statement.executeQuery(
                  "SELECT count(*) FROM schubert.speakers c LEFT JOIN schubert.games p ON p.id=c.game_id WHERE p.id IS NULL"),
          statement ->
              statement.executeQuery(
                  "SELECT count(*) FROM schubert.script_entries c LEFT JOIN schubert.games p ON p.id=c.game_id WHERE p.id IS NULL"),
          statement ->
              statement.executeQuery(
                  "SELECT count(*) FROM schubert.audio_files c LEFT JOIN schubert.games p ON p.id=c.game_id WHERE p.id IS NULL"),
          statement ->
              statement.executeQuery(
                  "SELECT count(*) FROM schubert.script_entries c LEFT JOIN schubert.script_files p ON p.id=c.script_file_id AND p.game_id=c.game_id WHERE p.id IS NULL"),
          statement ->
              statement.executeQuery(
                  "SELECT count(*) FROM schubert.script_entries c LEFT JOIN schubert.speakers p ON p.id=c.speaker_id AND p.game_id=c.game_id WHERE c.speaker_id IS NOT NULL AND p.id IS NULL"),
          statement ->
              statement.executeQuery(
                  "SELECT count(*) FROM schubert.entry_audio_links c LEFT JOIN schubert.script_entries p ON p.id=c.entry_id AND p.game_id=c.game_id WHERE p.id IS NULL"),
          statement ->
              statement.executeQuery(
                  "SELECT count(*) FROM schubert.entry_audio_links c LEFT JOIN schubert.audio_files p ON p.id=c.audio_file_id AND p.game_id=c.game_id WHERE p.id IS NULL"),
          statement ->
              statement.executeQuery(
                  "SELECT count(*) FROM schubert.media_assets c LEFT JOIN schubert.media_assets p ON p.logical_id=c.parent_logical_id WHERE c.parent_logical_id IS NOT NULL AND p.logical_id IS NULL"),
          statement ->
              statement.executeQuery(
                  "SELECT count(*) FROM (SELECT entry_id,link_type FROM schubert.entry_audio_links GROUP BY entry_id,link_type HAVING count(*)>999 OR min(display_order)<1 OR max(display_order)>999 OR count(DISTINCT display_order)<>count(*)) violations"),
          statement ->
              statement.executeQuery(
                  "SELECT count(*) FROM schubert.speakers WHERE ((id BETWEEN 1 AND 999999999999) AND (octet_length(name) BETWEEN 1 AND 128) AND (octet_length(normalized_name) BETWEEN 1 AND 128)) IS FALSE"),
          statement ->
              statement.executeQuery(
                  "SELECT count(*) FROM schubert.script_files WHERE ((byte_size BETWEEN 0 AND 999999999999) AND (\n        chapter_title IS NULL OR octet_length(chapter_title) <= 256) AND (display_order BETWEEN 1 AND 999999999999) AND (octet_length(display_path) BETWEEN 1 AND 512) AND (octet_length(file_name) BETWEEN 1 AND 256) AND (id BETWEEN 1 AND 999999999999) AND (sha256 ~ '^[0-9a-f]{64}$') AND (octet_length(storage_relative_path) BETWEEN 1 AND 512) AND (\n        storage_relative_path !~ '(^/|\\\\|(^|/)\\.\\.?(/|$)|//)')) IS FALSE"),
          statement ->
              statement.executeQuery(
                  "SELECT count(*) FROM schubert.script_entries WHERE ((octet_length(body) BETWEEN 1 AND 4096) AND (display_order BETWEEN 1 AND 999999999999) AND (entry_index >= 0) AND (entry_type IN ('dialogue', 'narration')) AND (id BETWEEN 1 AND 999999999999) AND (line_number IS NULL OR line_number >= 1) AND (\n        (entry_type = 'dialogue' AND speaker_id IS NOT NULL)\n        OR (entry_type = 'narration' AND speaker_id IS NULL)) AND (\n        speaker_label IS NULL OR octet_length(speaker_label) <= 128)) IS FALSE"),
          statement ->
              statement.executeQuery(
                  "SELECT count(*) FROM schubert.audio_files WHERE ((octet_length(audio_role) BETWEEN 1 AND 11) AND (octet_length(basename) BETWEEN 1 AND 255) AND (byte_size BETWEEN 1 AND 999999999999) AND (octet_length(display_path) BETWEEN 1 AND 512) AND (duration_ms IS NULL OR duration_ms BETWEEN 0 AND 999999999999) AND (octet_length(file_name) BETWEEN 1 AND 256) AND (id BETWEEN 1 AND 999999999999) AND (sha256 ~ '^[0-9a-f]{64}$') AND (octet_length(storage_relative_path) BETWEEN 1 AND 512) AND (\n        storage_relative_path !~ '(^/|\\\\|(^|/)\\.\\.?(/|$)|//)')) IS FALSE"),
          statement ->
              statement.executeQuery(
                  "SELECT count(*) FROM schubert.media_assets WHERE ((byte_size BETWEEN 1 AND 999999999999) AND (octet_length(category) BETWEEN 1 AND 64) AND (display_order BETWEEN 1 AND 9999) AND (octet_length(display_path) BETWEEN 1 AND 512) AND (octet_length(file_name) BETWEEN 1 AND 256) AND (id BETWEEN 1 AND 999999999999) AND (octet_length(logical_id) BETWEEN 1 AND 64) AND (media_type IN ('VIDEO', 'MUSIC')) AND (\n        mime_type IN ('video/mp4', 'audio/mp4', 'audio/mpeg', 'audio/ogg', 'audio/wav', 'audio/flac')) AND ((\n        (media_type = 'VIDEO' AND pair_key IS NULL AND pair_role IS NULL)\n        OR (media_type = 'MUSIC' AND (\n            (pair_role IN ('M', 'I') AND octet_length(pair_key) BETWEEN 1 AND 256)\n            OR (pair_role = 'N' AND pair_key IS NULL)))\n    ) IS TRUE) AND (section IS NULL OR octet_length(section) <= 128) AND (sha256 ~ '^[0-9a-f]{64}$') AND (octet_length(storage_relative_path) BETWEEN 1 AND 512) AND (\n        storage_relative_path !~ '(^/|\\\\|(^|/)\\.\\.?(/|$)|//)') AND (octet_length(title) BETWEEN 1 AND 256)) IS FALSE"),
          statement ->
              statement.executeQuery(
                  "SELECT count(*) FROM schubert.entry_audio_links WHERE ((display_order BETWEEN 1 AND 999) AND (link_type IN ('voice', 'se', 'bgm', 'other'))) IS FALSE"),
          statement ->
              statement.executeQuery(
                  "SELECT count(*) FROM (SELECT 1 FROM schubert.speakers GROUP BY id HAVING count(*)>1 OR (id IS NULL) UNION ALL SELECT 1 FROM schubert.speakers WHERE game_id IS NOT NULL AND normalized_name IS NOT NULL GROUP BY game_id,normalized_name HAVING count(*)>1 UNION ALL SELECT 1 FROM schubert.speakers WHERE id IS NOT NULL AND game_id IS NOT NULL GROUP BY id,game_id HAVING count(*)>1) violations"),
          statement ->
              statement.executeQuery(
                  "SELECT count(*) FROM (SELECT 1 FROM schubert.script_files GROUP BY id HAVING count(*)>1 OR (id IS NULL) UNION ALL SELECT 1 FROM schubert.script_files WHERE game_id IS NOT NULL AND display_order IS NOT NULL GROUP BY game_id,display_order HAVING count(*)>1 UNION ALL SELECT 1 FROM schubert.script_files WHERE game_id IS NOT NULL AND storage_relative_path IS NOT NULL GROUP BY game_id,storage_relative_path HAVING count(*)>1 UNION ALL SELECT 1 FROM schubert.script_files WHERE id IS NOT NULL AND game_id IS NOT NULL GROUP BY id,game_id HAVING count(*)>1) violations"),
          statement ->
              statement.executeQuery(
                  "SELECT count(*) FROM (SELECT 1 FROM schubert.script_entries GROUP BY id HAVING count(*)>1 OR (id IS NULL) UNION ALL SELECT 1 FROM schubert.script_entries WHERE display_order IS NOT NULL GROUP BY display_order HAVING count(*)>1 UNION ALL SELECT 1 FROM schubert.script_entries WHERE script_file_id IS NOT NULL AND entry_index IS NOT NULL GROUP BY script_file_id,entry_index HAVING count(*)>1 UNION ALL SELECT 1 FROM schubert.script_entries WHERE id IS NOT NULL AND game_id IS NOT NULL GROUP BY id,game_id HAVING count(*)>1) violations"),
          statement ->
              statement.executeQuery(
                  "SELECT count(*) FROM (SELECT 1 FROM schubert.audio_files GROUP BY id HAVING count(*)>1 OR (id IS NULL) UNION ALL SELECT 1 FROM schubert.audio_files WHERE game_id IS NOT NULL AND storage_relative_path IS NOT NULL GROUP BY game_id,storage_relative_path HAVING count(*)>1 UNION ALL SELECT 1 FROM schubert.audio_files WHERE id IS NOT NULL AND game_id IS NOT NULL GROUP BY id,game_id HAVING count(*)>1) violations"),
          statement ->
              statement.executeQuery(
                  "SELECT count(*) FROM (SELECT 1 FROM schubert.media_assets GROUP BY id HAVING count(*)>1 OR (id IS NULL) UNION ALL SELECT 1 FROM schubert.media_assets WHERE logical_id IS NOT NULL GROUP BY logical_id HAVING count(*)>1 UNION ALL SELECT 1 FROM schubert.media_assets WHERE media_type IS NOT NULL AND storage_relative_path IS NOT NULL GROUP BY media_type,storage_relative_path HAVING count(*)>1) violations"),
          statement ->
              statement.executeQuery(
                  "SELECT count(*) FROM (SELECT 1 FROM schubert.entry_audio_links GROUP BY entry_id,audio_file_id,link_type HAVING count(*)>1 OR (entry_id IS NULL OR audio_file_id IS NULL OR link_type IS NULL) UNION ALL SELECT 1 FROM schubert.entry_audio_links WHERE entry_id IS NOT NULL AND link_type IS NOT NULL AND display_order IS NOT NULL GROUP BY entry_id,link_type,display_order HAVING count(*)>1) violations"));

  public void verify(@Nullable Connection connection, @Nullable MigrationMasterCopyDataset declared)
      throws SQLException {
    if (connection == null || declared == null) throw invalidInput();
    var content = declared.content();
    var expected =
        List.of(
            (long) declared.speakers().rows().size(),
            (long) content.scenario().files().rows().size(),
            (long) content.scenario().entries().rows().size(),
            (long) content.audio().audioRows().size(),
            (long) content.media().rows().size(),
            (long) content.audio().linkRows().size());
    Statement statement = open(connection);
    @Nullable Throwable primary = null;
    try {
      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);
      for (int index = 0; index < COUNTS.size(); index++)
        requireResult(COUNTS.get(index).execute(statement), expected.get(index));
      for (var query : INSPECTIONS) requireResult(query.execute(statement), 0);
    } catch (SQLException | RuntimeException | Error failure) {
      primary = failure;
      throw failure;
    } finally {
      closeStatement(statement, primary);
    }
  }

  private static Statement open(Connection connection) throws SQLException {
    if (connection.getAutoCommit()) throw invalid();
    return requireStatement(connection.createStatement());
  }

  private static Statement requireStatement(@Nullable Statement created) throws SQLException {
    if (created == null) throw invalid();
    return created;
  }

  private static void requireResult(@Nullable ResultSet created, long expected)
      throws SQLException {
    if (created == null) throw invalid();
    ResultSet result = created;
    @Nullable Throwable primary = null;
    try {
      if (!result.next()) throw invalid();
      long actual = result.getLong(1);
      if (result.wasNull() || actual != expected || result.next()) throw invalid();
    } catch (SQLException | RuntimeException | Error failure) {
      primary = failure;
      throw failure;
    } finally {
      closeResult(result, primary);
    }
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

  @Override
  public String toString() {
    return "MigrationMasterReferenceVerifier[REDACTED]";
  }

  private static IllegalArgumentException invalidInput() {
    return new IllegalArgumentException("migration master reference input is invalid");
  }

  private static SQLException invalid() {
    return new SQLException("migration master reference verification is invalid");
  }

  @FunctionalInterface
  private interface SqlQuery {
    @Nullable ResultSet execute(Statement statement) throws SQLException;
  }
}

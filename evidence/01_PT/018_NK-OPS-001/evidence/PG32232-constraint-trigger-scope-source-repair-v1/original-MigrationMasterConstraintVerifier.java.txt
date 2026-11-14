package dev.codex.schubert.nk.migration;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;
import javax.annotation.concurrent.Immutable;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Fixed V002 physical constraint structure, never full catalog or actual DB qualification.
 * NK-MIG-001; MIG003005006/MIG-DAT005/DAT004/TST; UI242254; SS311/331/V002/343 SSC382;
 * PT-MIG-CONSTRAINT001..022. The caller owns authentication, exclusivity and the transaction.
 */
@NullMarked
@Immutable
public final class MigrationMasterConstraintVerifier {
  private static final int QUERY_TIMEOUT_SECONDS = 30;
  private static final int FETCH_ROWS = 1000;
  private static final String QUERY_PREFIX =
      "SELECT (row_number() OVER (ORDER BY k.conname COLLATE \"C\"))::integer,k.conname,k.contype::text,pg_catalog.array_to_string(k.conkey,','),(k.convalidated AND k.conenforced AND NOT k.condeferrable AND NOT k.condeferred AND k.conislocal AND k.coninhcount=0 AND k.conparentid=0 AND k.contypid=0 AND NOT k.conperiod),CASE WHEN k.contype='f' THEN rn.nspname||'.'||rc.relname||'('||pg_catalog.array_to_string(k.confkey,',')||')' ELSE '-' END,CASE WHEN k.contype='f' THEN k.confupdtype::text||'/'||k.confdeltype::text||'/'||k.confmatchtype::text ELSE '-' END FROM pg_catalog.pg_constraint k JOIN pg_catalog.pg_class c ON c.oid=k.conrelid JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_catalog.pg_class rc ON rc.oid=k.confrelid LEFT JOIN pg_catalog.pg_namespace rn ON rn.oid=rc.relnamespace WHERE n.nspname='schubert' AND k.connamespace=n.oid AND c.relname='";
  private static final String QUERY_SUFFIX =
      "' AND c.relkind='r' AND c.relpersistence='p' AND k.contype<>'n' ORDER BY k.conname COLLATE \"C\"";
  private static final List<String> QUERIES =
      List.of(
          QUERY_PREFIX + "speakers" + QUERY_SUFFIX,
          QUERY_PREFIX + "script_files" + QUERY_SUFFIX,
          QUERY_PREFIX + "script_entries" + QUERY_SUFFIX,
          QUERY_PREFIX + "audio_files" + QUERY_SUFFIX,
          QUERY_PREFIX + "media_assets" + QUERY_SUFFIX,
          QUERY_PREFIX + "entry_audio_links" + QUERY_SUFFIX);
  private static final List<List<String>> EXPECTED =
      List.of(
          List.of(
              "ck_speakers_id_n12\tc\t1\ttrue\t-\t-",
              "ck_speakers_name_bytes\tc\t3\ttrue\t-\t-",
              "ck_speakers_normalized_name_bytes\tc\t4\ttrue\t-\t-",
              "fk_speakers_games_game_id\tf\t2\ttrue\tschubert.games(1)\ta/r/s",
              "pk_speakers\tp\t1\ttrue\t-\t-",
              "uq_speakers_game_normalized_name\tu\t2,4\ttrue\t-\t-",
              "uq_speakers_id_game\tu\t1,2\ttrue\t-\t-"),
          List.of(
              "ck_script_files_byte_size\tc\t10\ttrue\t-\t-",
              "ck_script_files_chapter_title_bytes\tc\t8\ttrue\t-\t-",
              "ck_script_files_display_order_n12\tc\t3\ttrue\t-\t-",
              "ck_script_files_display_path_bytes\tc\t5\ttrue\t-\t-",
              "ck_script_files_file_name_bytes\tc\t6\ttrue\t-\t-",
              "ck_script_files_id_n12\tc\t1\ttrue\t-\t-",
              "ck_script_files_sha256\tc\t9\ttrue\t-\t-",
              "ck_script_files_storage_path_bytes\tc\t4\ttrue\t-\t-",
              "ck_script_files_storage_path_safe\tc\t4\ttrue\t-\t-",
              "fk_script_files_games_game_id\tf\t2\ttrue\tschubert.games(1)\ta/r/s",
              "pk_script_files\tp\t1\ttrue\t-\t-",
              "uq_script_files_game_display_order\tu\t2,3\ttrue\t-\t-",
              "uq_script_files_game_storage_path\tu\t2,4\ttrue\t-\t-",
              "uq_script_files_id_game\tu\t1,2\ttrue\t-\t-"),
          List.of(
              "ck_script_entries_body_bytes\tc\t10\ttrue\t-\t-",
              "ck_script_entries_display_order_n12\tc\t4\ttrue\t-\t-",
              "ck_script_entries_entry_index\tc\t5\ttrue\t-\t-",
              "ck_script_entries_entry_type\tc\t7\ttrue\t-\t-",
              "ck_script_entries_id_n12\tc\t1\ttrue\t-\t-",
              "ck_script_entries_line_number\tc\t6\ttrue\t-\t-",
              "ck_script_entries_speaker_by_type\tc\t7,8\ttrue\t-\t-",
              "ck_script_entries_speaker_label_bytes\tc\t9\ttrue\t-\t-",
              "fk_script_entries_games_game_id\tf\t2\ttrue\tschubert.games(1)\ta/r/s",
              "fk_script_entries_script_files_file_game\tf\t3,2\ttrue\tschubert.script_files(1,2)\ta/c/s",
              "fk_script_entries_speakers_speaker_game\tf\t8,2\ttrue\tschubert.speakers(1,2)\ta/r/s",
              "pk_script_entries\tp\t1\ttrue\t-\t-",
              "uq_script_entries_display_order\tu\t4\ttrue\t-\t-",
              "uq_script_entries_file_entry_index\tu\t3,5\ttrue\t-\t-",
              "uq_script_entries_id_game\tu\t1,2\ttrue\t-\t-"),
          List.of(
              "ck_audio_files_audio_role_bytes\tc\t7\ttrue\t-\t-",
              "ck_audio_files_basename_bytes\tc\t6\ttrue\t-\t-",
              "ck_audio_files_byte_size\tc\t10\ttrue\t-\t-",
              "ck_audio_files_display_path_bytes\tc\t4\ttrue\t-\t-",
              "ck_audio_files_duration_ms\tc\t9\ttrue\t-\t-",
              "ck_audio_files_file_name_bytes\tc\t5\ttrue\t-\t-",
              "ck_audio_files_id_n12\tc\t1\ttrue\t-\t-",
              "ck_audio_files_sha256\tc\t11\ttrue\t-\t-",
              "ck_audio_files_storage_path_bytes\tc\t3\ttrue\t-\t-",
              "ck_audio_files_storage_path_safe\tc\t3\ttrue\t-\t-",
              "fk_audio_files_games_game_id\tf\t2\ttrue\tschubert.games(1)\ta/r/s",
              "pk_audio_files\tp\t1\ttrue\t-\t-",
              "uq_audio_files_game_storage_path\tu\t2,3\ttrue\t-\t-",
              "uq_audio_files_id_game\tu\t1,2\ttrue\t-\t-"),
          List.of(
              "ck_media_assets_byte_size\tc\t10\ttrue\t-\t-",
              "ck_media_assets_category_bytes\tc\t5\ttrue\t-\t-",
              "ck_media_assets_display_order\tc\t16\ttrue\t-\t-",
              "ck_media_assets_display_path_bytes\tc\t8\ttrue\t-\t-",
              "ck_media_assets_file_name_bytes\tc\t9\ttrue\t-\t-",
              "ck_media_assets_id_n12\tc\t1\ttrue\t-\t-",
              "ck_media_assets_logical_id_bytes\tc\t2\ttrue\t-\t-",
              "ck_media_assets_media_type\tc\t3\ttrue\t-\t-",
              "ck_media_assets_mime_type\tc\t12\ttrue\t-\t-",
              "ck_media_assets_pair\tc\t3,14,15\ttrue\t-\t-",
              "ck_media_assets_section_bytes\tc\t6\ttrue\t-\t-",
              "ck_media_assets_sha256\tc\t11\ttrue\t-\t-",
              "ck_media_assets_storage_path_bytes\tc\t7\ttrue\t-\t-",
              "ck_media_assets_storage_path_safe\tc\t7\ttrue\t-\t-",
              "ck_media_assets_title_bytes\tc\t4\ttrue\t-\t-",
              "fk_media_assets_media_assets_parent_logical_id\tf\t13\ttrue\tschubert.media_assets(2)\ta/r/s",
              "pk_media_assets\tp\t1\ttrue\t-\t-",
              "uq_media_assets_logical_id\tu\t2\ttrue\t-\t-",
              "uq_media_assets_type_storage_path\tu\t3,7\ttrue\t-\t-"),
          List.of(
              "ck_entry_audio_links_display_order\tc\t5\ttrue\t-\t-",
              "ck_entry_audio_links_link_type\tc\t4\ttrue\t-\t-",
              "fk_entry_audio_links_audio_files_audio_game\tf\t2,3\ttrue\tschubert.audio_files(1,2)\ta/r/s",
              "fk_entry_audio_links_script_entries_entry_game\tf\t1,3\ttrue\tschubert.script_entries(1,2)\ta/c/s",
              "pk_entry_audio_links\tp\t1,2,4\ttrue\t-\t-",
              "uq_entry_audio_links_entry_type_order\tu\t1,4,5\ttrue\t-\t-"));

  public void verify(@Nullable Connection connection) throws SQLException {
    if (connection == null)
      throw new IllegalArgumentException("migration constraint input is invalid");
    if (connection.getAutoCommit()) throw invalid();
    Statement statement = requireStatement(connection.createStatement());
    @Nullable Throwable primary = null;
    try {
      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);
      statement.setFetchSize(FETCH_ROWS);
      for (int table = 0; table < QUERIES.size(); table++) {
        verifyRows(statement.executeQuery(QUERIES.get(table)), EXPECTED.get(table));
      }
    } catch (SQLException | RuntimeException | Error failure) {
      primary = failure;
      throw failure;
    } finally {
      closeStatement(statement, primary);
    }
  }

  private static Statement requireStatement(@Nullable Statement created) throws SQLException {
    if (created == null) throw invalid();
    return created;
  }

  private static void verifyRows(@Nullable ResultSet created, List<String> expected)
      throws SQLException {
    if (created == null) throw invalid();
    ResultSet result = created;
    @Nullable Throwable primary = null;
    try {
      int ordinal = 0;
      for (String descriptor : expected) {
        ordinal++;
        if (!result.next()) throw invalid();
        int actualOrdinal = result.getInt(1);
        if (result.wasNull() || actualOrdinal != ordinal) throw invalid();
        var fields = new ArrayList<@Nullable String>();
        fields.add(result.getString(2));
        fields.add(result.getString(3));
        fields.add(result.getString(4));
        boolean valid = result.getBoolean(5);
        if (result.wasNull()) throw invalid();
        fields.add(Boolean.toString(valid));
        fields.add(result.getString(6));
        fields.add(result.getString(7));
        // Private fixed descriptors contain six nonnull structural attributes including status.
        if (!fields.equals(List.of(descriptor.split("\t", -1)))) throw invalid();
      }
      if (result.next()) throw invalid();
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

  private static SQLException invalid() {
    return new SQLException("migration constraint structure is invalid");
  }

  @Override
  public String toString() {
    return "MigrationMasterConstraintVerifier[REDACTED]";
  }
}

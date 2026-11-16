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
 * Fixed V002 physical column attributes, never full catalog or actual DB qualification. NK-MIG-001;
 * MIG003005006/MIG-DAT005/DAT004/TST; UI242254; SS311/331/V002/343 SSC380/387/388/404/405;
 * PT-MIG-COLUMN001..026. The caller owns authentication, exclusivity and the transaction.
 */
@NullMarked
@Immutable
public final class MigrationMasterColumnVerifier {
  private static final int QUERY_TIMEOUT_SECONDS = 30;
  private static final int FETCH_ROWS = 1000;
  private static final String QUERY_PREFIX =
      "SELECT a.attnum,a.attname,t.typname,pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity::text,a.attgenerated::text,CASE WHEN a.attnotnull THEN EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS TRUE) AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS NOT TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum]) END,CASE WHEN a.attidentity='d' THEN (SELECT count(*) FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a'))=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid LEFT JOIN pg_catalog.pg_sequence sq ON sq.seqrelid=sc.oid LEFT JOIN pg_catalog.pg_type st ON st.oid=sq.seqtypid LEFT JOIN pg_catalog.pg_namespace stn ON stn.oid=st.typnamespace WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a') AND (dep.deptype='i' AND sc.relnamespace=c.relnamespace AND sc.relowner=c.relowner AND sc.relpersistence='p' AND stn.nspname='pg_catalog' AND st.typname='int8' AND sq.seqstart=1 AND sq.seqincrement=1 AND sq.seqmin=1 AND sq.seqmax=999999999999 AND sq.seqcache=1 AND NOT sq.seqcycle) IS TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a')) END,pg_catalog.pg_get_userbyid(c.relowner),CASE WHEN (c.relname='speakers' AND a.attname='is_protagonist') OR (c.relname='script_entries' AND a.attname='body_search') THEN a.atthasdef AND (SELECT count(*) FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum)=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum AND pg_catalog.pg_get_expr(ad.adbin,ad.adrelid,false)=CASE WHEN c.relname='speakers' THEN 'false' ELSE 'lower(body)' END) ELSE NOT a.atthasdef AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum) END FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid JOIN pg_catalog.pg_type t ON t.oid=a.atttypid JOIN pg_catalog.pg_namespace tn ON tn.oid=t.typnamespace WHERE n.nspname='schubert' AND c.relname='";
  private static final String QUERY_SUFFIX =
      "' AND c.relkind='r' AND c.relpersistence='p' AND tn.nspname='pg_catalog' AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum";
  private static final List<SqlQuery> QUERIES =
      List.of(
          statement -> statement.executeQuery(QUERY_PREFIX + "speakers" + QUERY_SUFFIX),
          statement -> statement.executeQuery(QUERY_PREFIX + "script_files" + QUERY_SUFFIX),
          statement -> statement.executeQuery(QUERY_PREFIX + "script_entries" + QUERY_SUFFIX),
          statement -> statement.executeQuery(QUERY_PREFIX + "audio_files" + QUERY_SUFFIX),
          statement -> statement.executeQuery(QUERY_PREFIX + "media_assets" + QUERY_SUFFIX),
          statement -> statement.executeQuery(QUERY_PREFIX + "entry_audio_links" + QUERY_SUFFIX));
  private static final String IDENTITY_ID_COLUMN = "id\tint8\tbigint\ttrue\td\t";
  private static final String GAME_ID_COLUMN = "game_id\tint2\tsmallint\ttrue\t\t";
  private static final String CREATED_AT_COLUMN =
      "created_at\ttimestamptz\ttimestamp with time zone\ttrue\t\t";
  private static final List<List<String>> EXPECTED =
      List.of(
          List.of(
              IDENTITY_ID_COLUMN,
              GAME_ID_COLUMN,
              "name\ttext\ttext\ttrue\t\t",
              "normalized_name\ttext\ttext\ttrue\t\t",
              "is_protagonist\tbool\tboolean\ttrue\t\t",
              "notes\ttext\ttext\tfalse\t\t",
              CREATED_AT_COLUMN),
          List.of(
              IDENTITY_ID_COLUMN,
              GAME_ID_COLUMN,
              "display_order\tint8\tbigint\ttrue\t\t",
              "storage_relative_path\ttext\ttext\ttrue\t\t",
              "display_path\ttext\ttext\ttrue\t\t",
              "file_name\ttext\ttext\ttrue\t\t",
              "section_code\tvarchar\tcharacter varying(64)\tfalse\t\t",
              "chapter_title\ttext\ttext\tfalse\t\t",
              "sha256\tbpchar\tcharacter(64)\ttrue\t\t",
              "byte_size\tint8\tbigint\ttrue\t\t",
              CREATED_AT_COLUMN),
          List.of(
              IDENTITY_ID_COLUMN,
              GAME_ID_COLUMN,
              "script_file_id\tint8\tbigint\ttrue\t\t",
              "display_order\tint8\tbigint\ttrue\t\t",
              "entry_index\tint4\tinteger\ttrue\t\t",
              "line_number\tint4\tinteger\tfalse\t\t",
              "entry_type\tvarchar\tcharacter varying(9)\ttrue\t\t",
              "speaker_id\tint8\tbigint\tfalse\t\t",
              "speaker_label\ttext\ttext\tfalse\t\t",
              "body\ttext\ttext\ttrue\t\t",
              "body_search\ttext\ttext\tfalse\t\ts",
              "raw_block\ttext\ttext\ttrue\t\t",
              CREATED_AT_COLUMN),
          List.of(
              IDENTITY_ID_COLUMN,
              GAME_ID_COLUMN,
              "storage_relative_path\ttext\ttext\ttrue\t\t",
              "display_path\ttext\ttext\ttrue\t\t",
              "file_name\ttext\ttext\ttrue\t\t",
              "basename\ttext\ttext\ttrue\t\t",
              "audio_role\tvarchar\tcharacter varying(11)\ttrue\t\t",
              "container\tvarchar\tcharacter varying(16)\tfalse\t\t",
              "duration_ms\tint8\tbigint\tfalse\t\t",
              "byte_size\tint8\tbigint\ttrue\t\t",
              "sha256\tbpchar\tcharacter(64)\ttrue\t\t",
              CREATED_AT_COLUMN),
          List.of(
              IDENTITY_ID_COLUMN,
              "logical_id\tvarchar\tcharacter varying(64)\ttrue\t\t",
              "media_type\tvarchar\tcharacter varying(8)\ttrue\t\t",
              "title\ttext\ttext\ttrue\t\t",
              "category\ttext\ttext\ttrue\t\t",
              "section\ttext\ttext\tfalse\t\t",
              "storage_relative_path\ttext\ttext\ttrue\t\t",
              "display_path\ttext\ttext\ttrue\t\t",
              "file_name\ttext\ttext\ttrue\t\t",
              "byte_size\tint8\tbigint\ttrue\t\t",
              "sha256\tbpchar\tcharacter(64)\ttrue\t\t",
              "mime_type\tvarchar\tcharacter varying(64)\ttrue\t\t",
              "parent_logical_id\tvarchar\tcharacter varying(64)\tfalse\t\t",
              "pair_key\ttext\ttext\tfalse\t\t",
              "pair_role\tbpchar\tcharacter(1)\tfalse\t\t",
              "display_order\tint4\tinteger\ttrue\t\t",
              CREATED_AT_COLUMN),
          List.of(
              "entry_id\tint8\tbigint\ttrue\t\t",
              "audio_file_id\tint8\tbigint\ttrue\t\t",
              GAME_ID_COLUMN,
              "link_type\tvarchar\tcharacter varying(5)\ttrue\t\t",
              "display_order\tint2\tsmallint\ttrue\t\t",
              CREATED_AT_COLUMN));

  public void verify(@Nullable Connection connection) throws SQLException {
    if (connection == null) throw new IllegalArgumentException("migration column input is invalid");
    if (connection.getAutoCommit()) throw invalid();
    Statement statement = requireStatement(connection.createStatement());
    @Nullable Throwable primary = null;
    try {
      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);
      statement.setFetchSize(FETCH_ROWS);
      for (int table = 0; table < QUERIES.size(); table++) {
        verifyRows(QUERIES.get(table).execute(statement), EXPECTED.get(table));
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
        boolean notNull = result.getBoolean(5);
        if (result.wasNull()) throw invalid();
        fields.add(Boolean.toString(notNull));
        fields.add(result.getString(6));
        fields.add(result.getString(7));
        // Private fixed descriptors have exactly six nonnull attributes, including empty flags.
        if (!fields.equals(List.of(descriptor.split("\t", -1)))) throw invalid();
        boolean notNullConstraintValid = result.getBoolean(8);
        if (result.wasNull() || !notNullConstraintValid) throw invalid();
        boolean identitySequenceValid = result.getBoolean(9);
        if (result.wasNull() || !identitySequenceValid) throw invalid();
        if (!"nk_owner".equals(result.getString(10))) throw invalid();
        boolean defaultDefinitionValid = result.getBoolean(11);
        if (result.wasNull() || !defaultDefinitionValid) throw invalid();
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
    return new SQLException("migration column attributes are invalid");
  }

  @Override
  public String toString() {
    return "MigrationMasterColumnVerifier[REDACTED]";
  }

  @FunctionalInterface
  private interface SqlQuery {
    @Nullable ResultSet execute(Statement statement) throws SQLException;
  }
}

package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.SQLWarning;
import java.sql.Statement;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.stream.IntStream;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/**
 * PT-MIG-TARGET001..038; independent95 SQL/56 scalar, content7 and catalog12 result vectors,
 * memory-only borrowed JDBC.
 */
final class MigrationMasterTargetPublisherTest {
  private static final String TRUE_TEXT = "true";
  private static final String FILE_ID_TEXT = "700";
  private static final String FILE_NAME_TEXT = "file.txt";
  private static final String ENTRY_ID_TEXT = "900";
  private static final String AUDIO_ID_TEXT = "500";
  private static final String VOICE_TEXT = "voice";
  private static final String NEXT_METHOD = "next";
  private static final String WAS_NULL_METHOD = "wasNull";
  private static final String CLOSE_METHOD = "close";
  private static final String SHA =
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  private static final String STAMP = "2026-01-02T03:04:05Z";
  private static final String ONE = "1";
  private static final String THREE = "3";
  private static final String SOURCE_VIDEO = "current/a.mp4";
  private static final String TARGET_VIDEO = "video/a.mp4";
  private static final String VIDEO = "VIDEO";
  private static final String SPEAKER_ID = "42";
  private static final String FLUSH_SQL =
      "SET CONSTRAINTS schubert.ck_entry_audio_links_entry_type_limit IMMEDIATE";
  private static final int PREPARE_END = 19;
  private static final int TRANSFER_END = 43;
  private static final int REFERENCE_END = 71;
  private static final int CONTENT_END = 78;
  private static final int CONTENT_TABLES = 7;
  private static final int CATALOG_TABLES = 12;
  private static final int CATALOG_END = 12;
  private static final int CATALOG_COLUMNS = 141;
  private static final int CATALOG_FIELDS = 7;
  private static final int COLUMN_CATALOG_FIELDS = 11;
  private static final int DEFAULT_FIELD = 10;
  private static final int OWNER_FIELD = 9;
  private static final int COLUMN_CATALOG_TABLES = 6;
  private static final int MIXED_CATALOG_GETTERS = 1251;
  private static final int CONTENT_COLUMNS = 66;
  private static final int RESULTS = 76;
  private static final int CLOSES = 17;
  private static final int CONTENT_CLOSE = 10;
  private static final String GET_LONG = "getLong";
  private static final String GET_INT = "getInt";
  private static final String GET_BOOLEAN = "getBoolean";
  private static final String GET_TIMESTAMP = "getTimestamp";
  private static final String GET_STRING = "getString";
  private static final int SETVAL_FIRST = 84;
  private static final int ANALYZE_FIRST = 89;
  private static final int SQL_COUNT = 95;
  private static final int SCALARS = 56;
  private static final int TRANSFER_SCALARS = 18;
  private static final int ORPHAN_FIRST = 24;
  private static final int REFERENCE_SCALARS_END = 46;
  private static final int SETVAL_SCALAR_FIRST = 51;
  private static final int PREPARED_FIRST_CLOSE = 11;
  private static final int OUTER_FINAL_CLOSE = 16;
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final List<Integer> OWNER_START =
      List.of(0, 6, 12, 13, 14, 16, 19, 23, 31, 43, 71, 78);
  private static final List<Integer> CLOSE_SQL_PREFIX =
      List.of(6, 12, 13, 14, 16, 19, 23, 31, 43, 71, 78, 85, 86, 87, 88, 89, 95);
  private static final List<Integer> CLOSE_RESULTS =
      List.of(6, 12, 13, 13, 13, 13, 16, 22, 31, 59, 66, 72, 73, 74, 75, 76, 76);
  private static final String CATALOG_IDENTITY_COLUMN =
      "1\tid\tint8\tbigint\ttrue\td\t\ttrue\ttrue\tnk_owner\ttrue";
  private static final String CATALOG_GAME_COLUMN =
      "2\tgame_id\tint2\tsmallint\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue";
  private static final String GAMES_SQL =
      "SELECT id,code,title,display_order,created_at FROM schubert.games ORDER BY id";
  private static final String GAMES_STAMP = "2026-09-01T00:00:00Z";
  private static final int GAME_RESULTS = 1;
  private static final int GAMES_QUERY_INDEX = 12;
  private static final int GAMES_FIELDS = 5;
  private static final int GAMES_OWNER_CLOSE = 2;
  private static final int GAME_ORDER_FIELD = 3;
  private static final int GAME_TIME_FIELD = 4;
  private static final List<List<String>> GAMES_ROWS =
      List.of(
          List.of("1", "NUKITASHI1", "NUKITASHI", "1", GAMES_STAMP),
          List.of("2", "NUKITASHI2", "NUKITASHI2", "2", GAMES_STAMP));
  private static final List<String> CATALOG_SQL =
      List.of(
          "SELECT a.attnum,a.attname,t.typname,pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity::text,a.attgenerated::text,CASE WHEN a.attnotnull THEN EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS TRUE) AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS NOT TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum]) END,CASE WHEN a.attidentity='d' THEN (SELECT count(*) FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a'))=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid LEFT JOIN pg_catalog.pg_sequence sq ON sq.seqrelid=sc.oid LEFT JOIN pg_catalog.pg_type st ON st.oid=sq.seqtypid LEFT JOIN pg_catalog.pg_namespace stn ON stn.oid=st.typnamespace WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a') AND (dep.deptype='i' AND sc.relnamespace=c.relnamespace AND sc.relowner=c.relowner AND sc.relpersistence='p' AND stn.nspname='pg_catalog' AND st.typname='int8' AND sq.seqstart=1 AND sq.seqincrement=1 AND sq.seqmin=1 AND sq.seqmax=999999999999 AND sq.seqcache=1 AND NOT sq.seqcycle) IS TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a')) END,pg_catalog.pg_get_userbyid(c.relowner),CASE WHEN (c.relname='speakers' AND a.attname='is_protagonist') OR (c.relname='script_entries' AND a.attname='body_search') THEN a.atthasdef AND (SELECT count(*) FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum)=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum AND pg_catalog.pg_get_expr(ad.adbin,ad.adrelid,false)=CASE WHEN c.relname='speakers' THEN 'false' ELSE 'lower(body)' END) ELSE NOT a.atthasdef AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum) END FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid JOIN pg_catalog.pg_type t ON t.oid=a.atttypid JOIN pg_catalog.pg_namespace tn ON tn.oid=t.typnamespace WHERE n.nspname='schubert' AND c.relname='speakers' AND c.relkind='r' AND c.relpersistence='p' AND tn.nspname='pg_catalog' AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum",
          "SELECT a.attnum,a.attname,t.typname,pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity::text,a.attgenerated::text,CASE WHEN a.attnotnull THEN EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS TRUE) AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS NOT TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum]) END,CASE WHEN a.attidentity='d' THEN (SELECT count(*) FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a'))=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid LEFT JOIN pg_catalog.pg_sequence sq ON sq.seqrelid=sc.oid LEFT JOIN pg_catalog.pg_type st ON st.oid=sq.seqtypid LEFT JOIN pg_catalog.pg_namespace stn ON stn.oid=st.typnamespace WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a') AND (dep.deptype='i' AND sc.relnamespace=c.relnamespace AND sc.relowner=c.relowner AND sc.relpersistence='p' AND stn.nspname='pg_catalog' AND st.typname='int8' AND sq.seqstart=1 AND sq.seqincrement=1 AND sq.seqmin=1 AND sq.seqmax=999999999999 AND sq.seqcache=1 AND NOT sq.seqcycle) IS TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a')) END,pg_catalog.pg_get_userbyid(c.relowner),CASE WHEN (c.relname='speakers' AND a.attname='is_protagonist') OR (c.relname='script_entries' AND a.attname='body_search') THEN a.atthasdef AND (SELECT count(*) FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum)=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum AND pg_catalog.pg_get_expr(ad.adbin,ad.adrelid,false)=CASE WHEN c.relname='speakers' THEN 'false' ELSE 'lower(body)' END) ELSE NOT a.atthasdef AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum) END FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid JOIN pg_catalog.pg_type t ON t.oid=a.atttypid JOIN pg_catalog.pg_namespace tn ON tn.oid=t.typnamespace WHERE n.nspname='schubert' AND c.relname='script_files' AND c.relkind='r' AND c.relpersistence='p' AND tn.nspname='pg_catalog' AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum",
          "SELECT a.attnum,a.attname,t.typname,pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity::text,a.attgenerated::text,CASE WHEN a.attnotnull THEN EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS TRUE) AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS NOT TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum]) END,CASE WHEN a.attidentity='d' THEN (SELECT count(*) FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a'))=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid LEFT JOIN pg_catalog.pg_sequence sq ON sq.seqrelid=sc.oid LEFT JOIN pg_catalog.pg_type st ON st.oid=sq.seqtypid LEFT JOIN pg_catalog.pg_namespace stn ON stn.oid=st.typnamespace WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a') AND (dep.deptype='i' AND sc.relnamespace=c.relnamespace AND sc.relowner=c.relowner AND sc.relpersistence='p' AND stn.nspname='pg_catalog' AND st.typname='int8' AND sq.seqstart=1 AND sq.seqincrement=1 AND sq.seqmin=1 AND sq.seqmax=999999999999 AND sq.seqcache=1 AND NOT sq.seqcycle) IS TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a')) END,pg_catalog.pg_get_userbyid(c.relowner),CASE WHEN (c.relname='speakers' AND a.attname='is_protagonist') OR (c.relname='script_entries' AND a.attname='body_search') THEN a.atthasdef AND (SELECT count(*) FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum)=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum AND pg_catalog.pg_get_expr(ad.adbin,ad.adrelid,false)=CASE WHEN c.relname='speakers' THEN 'false' ELSE 'lower(body)' END) ELSE NOT a.atthasdef AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum) END FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid JOIN pg_catalog.pg_type t ON t.oid=a.atttypid JOIN pg_catalog.pg_namespace tn ON tn.oid=t.typnamespace WHERE n.nspname='schubert' AND c.relname='script_entries' AND c.relkind='r' AND c.relpersistence='p' AND tn.nspname='pg_catalog' AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum",
          "SELECT a.attnum,a.attname,t.typname,pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity::text,a.attgenerated::text,CASE WHEN a.attnotnull THEN EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS TRUE) AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS NOT TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum]) END,CASE WHEN a.attidentity='d' THEN (SELECT count(*) FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a'))=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid LEFT JOIN pg_catalog.pg_sequence sq ON sq.seqrelid=sc.oid LEFT JOIN pg_catalog.pg_type st ON st.oid=sq.seqtypid LEFT JOIN pg_catalog.pg_namespace stn ON stn.oid=st.typnamespace WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a') AND (dep.deptype='i' AND sc.relnamespace=c.relnamespace AND sc.relowner=c.relowner AND sc.relpersistence='p' AND stn.nspname='pg_catalog' AND st.typname='int8' AND sq.seqstart=1 AND sq.seqincrement=1 AND sq.seqmin=1 AND sq.seqmax=999999999999 AND sq.seqcache=1 AND NOT sq.seqcycle) IS TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a')) END,pg_catalog.pg_get_userbyid(c.relowner),CASE WHEN (c.relname='speakers' AND a.attname='is_protagonist') OR (c.relname='script_entries' AND a.attname='body_search') THEN a.atthasdef AND (SELECT count(*) FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum)=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum AND pg_catalog.pg_get_expr(ad.adbin,ad.adrelid,false)=CASE WHEN c.relname='speakers' THEN 'false' ELSE 'lower(body)' END) ELSE NOT a.atthasdef AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum) END FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid JOIN pg_catalog.pg_type t ON t.oid=a.atttypid JOIN pg_catalog.pg_namespace tn ON tn.oid=t.typnamespace WHERE n.nspname='schubert' AND c.relname='audio_files' AND c.relkind='r' AND c.relpersistence='p' AND tn.nspname='pg_catalog' AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum",
          "SELECT a.attnum,a.attname,t.typname,pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity::text,a.attgenerated::text,CASE WHEN a.attnotnull THEN EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS TRUE) AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS NOT TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum]) END,CASE WHEN a.attidentity='d' THEN (SELECT count(*) FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a'))=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid LEFT JOIN pg_catalog.pg_sequence sq ON sq.seqrelid=sc.oid LEFT JOIN pg_catalog.pg_type st ON st.oid=sq.seqtypid LEFT JOIN pg_catalog.pg_namespace stn ON stn.oid=st.typnamespace WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a') AND (dep.deptype='i' AND sc.relnamespace=c.relnamespace AND sc.relowner=c.relowner AND sc.relpersistence='p' AND stn.nspname='pg_catalog' AND st.typname='int8' AND sq.seqstart=1 AND sq.seqincrement=1 AND sq.seqmin=1 AND sq.seqmax=999999999999 AND sq.seqcache=1 AND NOT sq.seqcycle) IS TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a')) END,pg_catalog.pg_get_userbyid(c.relowner),CASE WHEN (c.relname='speakers' AND a.attname='is_protagonist') OR (c.relname='script_entries' AND a.attname='body_search') THEN a.atthasdef AND (SELECT count(*) FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum)=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum AND pg_catalog.pg_get_expr(ad.adbin,ad.adrelid,false)=CASE WHEN c.relname='speakers' THEN 'false' ELSE 'lower(body)' END) ELSE NOT a.atthasdef AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum) END FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid JOIN pg_catalog.pg_type t ON t.oid=a.atttypid JOIN pg_catalog.pg_namespace tn ON tn.oid=t.typnamespace WHERE n.nspname='schubert' AND c.relname='media_assets' AND c.relkind='r' AND c.relpersistence='p' AND tn.nspname='pg_catalog' AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum",
          "SELECT a.attnum,a.attname,t.typname,pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity::text,a.attgenerated::text,CASE WHEN a.attnotnull THEN EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS TRUE) AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS NOT TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum]) END,CASE WHEN a.attidentity='d' THEN (SELECT count(*) FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a'))=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid LEFT JOIN pg_catalog.pg_sequence sq ON sq.seqrelid=sc.oid LEFT JOIN pg_catalog.pg_type st ON st.oid=sq.seqtypid LEFT JOIN pg_catalog.pg_namespace stn ON stn.oid=st.typnamespace WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a') AND (dep.deptype='i' AND sc.relnamespace=c.relnamespace AND sc.relowner=c.relowner AND sc.relpersistence='p' AND stn.nspname='pg_catalog' AND st.typname='int8' AND sq.seqstart=1 AND sq.seqincrement=1 AND sq.seqmin=1 AND sq.seqmax=999999999999 AND sq.seqcache=1 AND NOT sq.seqcycle) IS TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a')) END,pg_catalog.pg_get_userbyid(c.relowner),CASE WHEN (c.relname='speakers' AND a.attname='is_protagonist') OR (c.relname='script_entries' AND a.attname='body_search') THEN a.atthasdef AND (SELECT count(*) FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum)=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum AND pg_catalog.pg_get_expr(ad.adbin,ad.adrelid,false)=CASE WHEN c.relname='speakers' THEN 'false' ELSE 'lower(body)' END) ELSE NOT a.atthasdef AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum) END FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid JOIN pg_catalog.pg_type t ON t.oid=a.atttypid JOIN pg_catalog.pg_namespace tn ON tn.oid=t.typnamespace WHERE n.nspname='schubert' AND c.relname='entry_audio_links' AND c.relkind='r' AND c.relpersistence='p' AND tn.nspname='pg_catalog' AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum",
          "SELECT (row_number() OVER (ORDER BY k.conname COLLATE \"C\"))::integer,k.conname,k.contype::text,pg_catalog.array_to_string(k.conkey,','),(k.convalidated AND k.conenforced AND NOT k.condeferrable AND NOT k.condeferred AND k.conislocal AND k.coninhcount=0 AND k.conparentid=0 AND k.contypid=0 AND NOT k.conperiod),CASE WHEN k.contype='f' THEN rn.nspname||'.'||rc.relname||'('||pg_catalog.array_to_string(k.confkey,',')||')' ELSE '-' END,CASE WHEN k.contype='f' THEN k.confupdtype::text||'/'||k.confdeltype::text||'/'||k.confmatchtype::text ELSE '-' END FROM pg_catalog.pg_constraint k JOIN pg_catalog.pg_class c ON c.oid=k.conrelid JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_catalog.pg_class rc ON rc.oid=k.confrelid LEFT JOIN pg_catalog.pg_namespace rn ON rn.oid=rc.relnamespace WHERE n.nspname='schubert' AND k.connamespace=n.oid AND c.relname='speakers' AND c.relkind='r' AND c.relpersistence='p' AND k.contype NOT IN ('n','t') ORDER BY k.conname COLLATE \"C\"",
          "SELECT (row_number() OVER (ORDER BY k.conname COLLATE \"C\"))::integer,k.conname,k.contype::text,pg_catalog.array_to_string(k.conkey,','),(k.convalidated AND k.conenforced AND NOT k.condeferrable AND NOT k.condeferred AND k.conislocal AND k.coninhcount=0 AND k.conparentid=0 AND k.contypid=0 AND NOT k.conperiod),CASE WHEN k.contype='f' THEN rn.nspname||'.'||rc.relname||'('||pg_catalog.array_to_string(k.confkey,',')||')' ELSE '-' END,CASE WHEN k.contype='f' THEN k.confupdtype::text||'/'||k.confdeltype::text||'/'||k.confmatchtype::text ELSE '-' END FROM pg_catalog.pg_constraint k JOIN pg_catalog.pg_class c ON c.oid=k.conrelid JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_catalog.pg_class rc ON rc.oid=k.confrelid LEFT JOIN pg_catalog.pg_namespace rn ON rn.oid=rc.relnamespace WHERE n.nspname='schubert' AND k.connamespace=n.oid AND c.relname='script_files' AND c.relkind='r' AND c.relpersistence='p' AND k.contype NOT IN ('n','t') ORDER BY k.conname COLLATE \"C\"",
          "SELECT (row_number() OVER (ORDER BY k.conname COLLATE \"C\"))::integer,k.conname,k.contype::text,pg_catalog.array_to_string(k.conkey,','),(k.convalidated AND k.conenforced AND NOT k.condeferrable AND NOT k.condeferred AND k.conislocal AND k.coninhcount=0 AND k.conparentid=0 AND k.contypid=0 AND NOT k.conperiod),CASE WHEN k.contype='f' THEN rn.nspname||'.'||rc.relname||'('||pg_catalog.array_to_string(k.confkey,',')||')' ELSE '-' END,CASE WHEN k.contype='f' THEN k.confupdtype::text||'/'||k.confdeltype::text||'/'||k.confmatchtype::text ELSE '-' END FROM pg_catalog.pg_constraint k JOIN pg_catalog.pg_class c ON c.oid=k.conrelid JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_catalog.pg_class rc ON rc.oid=k.confrelid LEFT JOIN pg_catalog.pg_namespace rn ON rn.oid=rc.relnamespace WHERE n.nspname='schubert' AND k.connamespace=n.oid AND c.relname='script_entries' AND c.relkind='r' AND c.relpersistence='p' AND k.contype NOT IN ('n','t') ORDER BY k.conname COLLATE \"C\"",
          "SELECT (row_number() OVER (ORDER BY k.conname COLLATE \"C\"))::integer,k.conname,k.contype::text,pg_catalog.array_to_string(k.conkey,','),(k.convalidated AND k.conenforced AND NOT k.condeferrable AND NOT k.condeferred AND k.conislocal AND k.coninhcount=0 AND k.conparentid=0 AND k.contypid=0 AND NOT k.conperiod),CASE WHEN k.contype='f' THEN rn.nspname||'.'||rc.relname||'('||pg_catalog.array_to_string(k.confkey,',')||')' ELSE '-' END,CASE WHEN k.contype='f' THEN k.confupdtype::text||'/'||k.confdeltype::text||'/'||k.confmatchtype::text ELSE '-' END FROM pg_catalog.pg_constraint k JOIN pg_catalog.pg_class c ON c.oid=k.conrelid JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_catalog.pg_class rc ON rc.oid=k.confrelid LEFT JOIN pg_catalog.pg_namespace rn ON rn.oid=rc.relnamespace WHERE n.nspname='schubert' AND k.connamespace=n.oid AND c.relname='audio_files' AND c.relkind='r' AND c.relpersistence='p' AND k.contype NOT IN ('n','t') ORDER BY k.conname COLLATE \"C\"",
          "SELECT (row_number() OVER (ORDER BY k.conname COLLATE \"C\"))::integer,k.conname,k.contype::text,pg_catalog.array_to_string(k.conkey,','),(k.convalidated AND k.conenforced AND NOT k.condeferrable AND NOT k.condeferred AND k.conislocal AND k.coninhcount=0 AND k.conparentid=0 AND k.contypid=0 AND NOT k.conperiod),CASE WHEN k.contype='f' THEN rn.nspname||'.'||rc.relname||'('||pg_catalog.array_to_string(k.confkey,',')||')' ELSE '-' END,CASE WHEN k.contype='f' THEN k.confupdtype::text||'/'||k.confdeltype::text||'/'||k.confmatchtype::text ELSE '-' END FROM pg_catalog.pg_constraint k JOIN pg_catalog.pg_class c ON c.oid=k.conrelid JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_catalog.pg_class rc ON rc.oid=k.confrelid LEFT JOIN pg_catalog.pg_namespace rn ON rn.oid=rc.relnamespace WHERE n.nspname='schubert' AND k.connamespace=n.oid AND c.relname='media_assets' AND c.relkind='r' AND c.relpersistence='p' AND k.contype NOT IN ('n','t') ORDER BY k.conname COLLATE \"C\"",
          "SELECT (row_number() OVER (ORDER BY k.conname COLLATE \"C\"))::integer,k.conname,k.contype::text,pg_catalog.array_to_string(k.conkey,','),(k.convalidated AND k.conenforced AND NOT k.condeferrable AND NOT k.condeferred AND k.conislocal AND k.coninhcount=0 AND k.conparentid=0 AND k.contypid=0 AND NOT k.conperiod),CASE WHEN k.contype='f' THEN rn.nspname||'.'||rc.relname||'('||pg_catalog.array_to_string(k.confkey,',')||')' ELSE '-' END,CASE WHEN k.contype='f' THEN k.confupdtype::text||'/'||k.confdeltype::text||'/'||k.confmatchtype::text ELSE '-' END FROM pg_catalog.pg_constraint k JOIN pg_catalog.pg_class c ON c.oid=k.conrelid JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_catalog.pg_class rc ON rc.oid=k.confrelid LEFT JOIN pg_catalog.pg_namespace rn ON rn.oid=rc.relnamespace WHERE n.nspname='schubert' AND k.connamespace=n.oid AND c.relname='entry_audio_links' AND c.relkind='r' AND c.relpersistence='p' AND k.contype NOT IN ('n','t') ORDER BY k.conname COLLATE \"C\"");
  private static final List<List<String>> CATALOG_ROWS =
      List.of(
          List.of(
              CATALOG_IDENTITY_COLUMN,
              CATALOG_GAME_COLUMN,
              "3\tname\ttext\ttext\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "4\tnormalized_name\ttext\ttext\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "5\tis_protagonist\tbool\tboolean\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "6\tnotes\ttext\ttext\tfalse\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "7\tcreated_at\ttimestamptz\ttimestamp with time zone\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue"),
          List.of(
              CATALOG_IDENTITY_COLUMN,
              CATALOG_GAME_COLUMN,
              "3\tdisplay_order\tint8\tbigint\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "4\tstorage_relative_path\ttext\ttext\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "5\tdisplay_path\ttext\ttext\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "6\tfile_name\ttext\ttext\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "7\tsection_code\tvarchar\tcharacter varying(64)\tfalse\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "8\tchapter_title\ttext\ttext\tfalse\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "9\tsha256\tbpchar\tcharacter(64)\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "10\tbyte_size\tint8\tbigint\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "11\tcreated_at\ttimestamptz\ttimestamp with time zone\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue"),
          List.of(
              CATALOG_IDENTITY_COLUMN,
              CATALOG_GAME_COLUMN,
              "3\tscript_file_id\tint8\tbigint\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "4\tdisplay_order\tint8\tbigint\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "5\tentry_index\tint4\tinteger\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "6\tline_number\tint4\tinteger\tfalse\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "7\tentry_type\tvarchar\tcharacter varying(9)\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "8\tspeaker_id\tint8\tbigint\tfalse\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "9\tspeaker_label\ttext\ttext\tfalse\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "10\tbody\ttext\ttext\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "11\tbody_search\ttext\ttext\tfalse\t\ts\ttrue\ttrue\tnk_owner\ttrue",
              "12\traw_block\ttext\ttext\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "13\tcreated_at\ttimestamptz\ttimestamp with time zone\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue"),
          List.of(
              CATALOG_IDENTITY_COLUMN,
              CATALOG_GAME_COLUMN,
              "3\tstorage_relative_path\ttext\ttext\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "4\tdisplay_path\ttext\ttext\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "5\tfile_name\ttext\ttext\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "6\tbasename\ttext\ttext\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "7\taudio_role\tvarchar\tcharacter varying(11)\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "8\tcontainer\tvarchar\tcharacter varying(16)\tfalse\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "9\tduration_ms\tint8\tbigint\tfalse\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "10\tbyte_size\tint8\tbigint\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "11\tsha256\tbpchar\tcharacter(64)\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "12\tcreated_at\ttimestamptz\ttimestamp with time zone\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue"),
          List.of(
              CATALOG_IDENTITY_COLUMN,
              "2\tlogical_id\tvarchar\tcharacter varying(64)\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "3\tmedia_type\tvarchar\tcharacter varying(8)\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "4\ttitle\ttext\ttext\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "5\tcategory\ttext\ttext\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "6\tsection\ttext\ttext\tfalse\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "7\tstorage_relative_path\ttext\ttext\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "8\tdisplay_path\ttext\ttext\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "9\tfile_name\ttext\ttext\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "10\tbyte_size\tint8\tbigint\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "11\tsha256\tbpchar\tcharacter(64)\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "12\tmime_type\tvarchar\tcharacter varying(64)\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "13\tparent_logical_id\tvarchar\tcharacter varying(64)\tfalse\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "14\tpair_key\ttext\ttext\tfalse\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "15\tpair_role\tbpchar\tcharacter(1)\tfalse\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "16\tdisplay_order\tint4\tinteger\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "17\tcreated_at\ttimestamptz\ttimestamp with time zone\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue"),
          List.of(
              "1\tentry_id\tint8\tbigint\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "2\taudio_file_id\tint8\tbigint\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "3\tgame_id\tint2\tsmallint\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "4\tlink_type\tvarchar\tcharacter varying(5)\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "5\tdisplay_order\tint2\tsmallint\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "6\tcreated_at\ttimestamptz\ttimestamp with time zone\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue"),
          List.of(
              "1\tck_speakers_id_n12\tc\t1\ttrue\t-\t-",
              "2\tck_speakers_name_bytes\tc\t3\ttrue\t-\t-",
              "3\tck_speakers_normalized_name_bytes\tc\t4\ttrue\t-\t-",
              "4\tfk_speakers_games_game_id\tf\t2\ttrue\tschubert.games(1)\ta/r/s",
              "5\tpk_speakers\tp\t1\ttrue\t-\t-",
              "6\tuq_speakers_game_normalized_name\tu\t2,4\ttrue\t-\t-",
              "7\tuq_speakers_id_game\tu\t1,2\ttrue\t-\t-"),
          List.of(
              "1\tck_script_files_byte_size\tc\t10\ttrue\t-\t-",
              "2\tck_script_files_chapter_title_bytes\tc\t8\ttrue\t-\t-",
              "3\tck_script_files_display_order_n12\tc\t3\ttrue\t-\t-",
              "4\tck_script_files_display_path_bytes\tc\t5\ttrue\t-\t-",
              "5\tck_script_files_file_name_bytes\tc\t6\ttrue\t-\t-",
              "6\tck_script_files_id_n12\tc\t1\ttrue\t-\t-",
              "7\tck_script_files_sha256\tc\t9\ttrue\t-\t-",
              "8\tck_script_files_storage_path_bytes\tc\t4\ttrue\t-\t-",
              "9\tck_script_files_storage_path_safe\tc\t4\ttrue\t-\t-",
              "10\tfk_script_files_games_game_id\tf\t2\ttrue\tschubert.games(1)\ta/r/s",
              "11\tpk_script_files\tp\t1\ttrue\t-\t-",
              "12\tuq_script_files_game_display_order\tu\t2,3\ttrue\t-\t-",
              "13\tuq_script_files_game_storage_path\tu\t2,4\ttrue\t-\t-",
              "14\tuq_script_files_id_game\tu\t1,2\ttrue\t-\t-"),
          List.of(
              "1\tck_script_entries_body_bytes\tc\t10\ttrue\t-\t-",
              "2\tck_script_entries_display_order_n12\tc\t4\ttrue\t-\t-",
              "3\tck_script_entries_entry_index\tc\t5\ttrue\t-\t-",
              "4\tck_script_entries_entry_type\tc\t7\ttrue\t-\t-",
              "5\tck_script_entries_id_n12\tc\t1\ttrue\t-\t-",
              "6\tck_script_entries_line_number\tc\t6\ttrue\t-\t-",
              "7\tck_script_entries_speaker_by_type\tc\t7,8\ttrue\t-\t-",
              "8\tck_script_entries_speaker_label_bytes\tc\t9\ttrue\t-\t-",
              "9\tfk_script_entries_games_game_id\tf\t2\ttrue\tschubert.games(1)\ta/r/s",
              "10\tfk_script_entries_script_files_file_game\tf\t3,2\ttrue\tschubert.script_files(1,2)\ta/c/s",
              "11\tfk_script_entries_speakers_speaker_game\tf\t8,2\ttrue\tschubert.speakers(1,2)\ta/r/s",
              "12\tpk_script_entries\tp\t1\ttrue\t-\t-",
              "13\tuq_script_entries_display_order\tu\t4\ttrue\t-\t-",
              "14\tuq_script_entries_file_entry_index\tu\t3,5\ttrue\t-\t-",
              "15\tuq_script_entries_id_game\tu\t1,2\ttrue\t-\t-"),
          List.of(
              "1\tck_audio_files_audio_role_bytes\tc\t7\ttrue\t-\t-",
              "2\tck_audio_files_basename_bytes\tc\t6\ttrue\t-\t-",
              "3\tck_audio_files_byte_size\tc\t10\ttrue\t-\t-",
              "4\tck_audio_files_display_path_bytes\tc\t4\ttrue\t-\t-",
              "5\tck_audio_files_duration_ms\tc\t9\ttrue\t-\t-",
              "6\tck_audio_files_file_name_bytes\tc\t5\ttrue\t-\t-",
              "7\tck_audio_files_id_n12\tc\t1\ttrue\t-\t-",
              "8\tck_audio_files_sha256\tc\t11\ttrue\t-\t-",
              "9\tck_audio_files_storage_path_bytes\tc\t3\ttrue\t-\t-",
              "10\tck_audio_files_storage_path_safe\tc\t3\ttrue\t-\t-",
              "11\tfk_audio_files_games_game_id\tf\t2\ttrue\tschubert.games(1)\ta/r/s",
              "12\tpk_audio_files\tp\t1\ttrue\t-\t-",
              "13\tuq_audio_files_game_storage_path\tu\t2,3\ttrue\t-\t-",
              "14\tuq_audio_files_id_game\tu\t1,2\ttrue\t-\t-"),
          List.of(
              "1\tck_media_assets_byte_size\tc\t10\ttrue\t-\t-",
              "2\tck_media_assets_category_bytes\tc\t5\ttrue\t-\t-",
              "3\tck_media_assets_display_order\tc\t16\ttrue\t-\t-",
              "4\tck_media_assets_display_path_bytes\tc\t8\ttrue\t-\t-",
              "5\tck_media_assets_file_name_bytes\tc\t9\ttrue\t-\t-",
              "6\tck_media_assets_id_n12\tc\t1\ttrue\t-\t-",
              "7\tck_media_assets_logical_id_bytes\tc\t2\ttrue\t-\t-",
              "8\tck_media_assets_media_type\tc\t3\ttrue\t-\t-",
              "9\tck_media_assets_mime_type\tc\t12\ttrue\t-\t-",
              "10\tck_media_assets_pair\tc\t3,14,15\ttrue\t-\t-",
              "11\tck_media_assets_section_bytes\tc\t6\ttrue\t-\t-",
              "12\tck_media_assets_sha256\tc\t11\ttrue\t-\t-",
              "13\tck_media_assets_storage_path_bytes\tc\t7\ttrue\t-\t-",
              "14\tck_media_assets_storage_path_safe\tc\t7\ttrue\t-\t-",
              "15\tck_media_assets_title_bytes\tc\t4\ttrue\t-\t-",
              "16\tfk_media_assets_media_assets_parent_logical_id\tf\t13\ttrue\tschubert.media_assets(2)\ta/r/s",
              "17\tpk_media_assets\tp\t1\ttrue\t-\t-",
              "18\tuq_media_assets_logical_id\tu\t2\ttrue\t-\t-",
              "19\tuq_media_assets_type_storage_path\tu\t3,7\ttrue\t-\t-"),
          List.of(
              "1\tck_entry_audio_links_display_order\tc\t5\ttrue\t-\t-",
              "2\tck_entry_audio_links_link_type\tc\t4\ttrue\t-\t-",
              "3\tfk_entry_audio_links_audio_files_audio_game\tf\t2,3\ttrue\tschubert.audio_files(1,2)\ta/r/s",
              "4\tfk_entry_audio_links_script_entries_entry_game\tf\t1,3\ttrue\tschubert.script_entries(1,2)\ta/c/s",
              "5\tpk_entry_audio_links\tp\t1,2,4\ttrue\t-\t-",
              "6\tuq_entry_audio_links_entry_type_order\tu\t1,4,5\ttrue\t-\t-"));
  private static final List<String> CONTENT_SQL =
      List.of(
          "SELECT id,game_id,name,normalized_name,is_protagonist,notes,created_at FROM schubert.speakers ORDER BY id",
          "SELECT id,game_id,display_order,storage_relative_path,display_path,file_name,section_code,chapter_title,sha256,byte_size,created_at FROM schubert.script_files ORDER BY id",
          "SELECT id,game_id,script_file_id,display_order,entry_index,line_number,entry_type,speaker_id,speaker_label,body,raw_block,created_at FROM schubert.script_entries ORDER BY id",
          "SELECT id,game_id,storage_relative_path,display_path,file_name,basename,audio_role,container,duration_ms,byte_size,sha256,created_at FROM schubert.audio_files ORDER BY id",
          "SELECT id,logical_id,media_type,title,category,section,storage_relative_path,display_path,file_name,byte_size,sha256,mime_type,parent_logical_id,pair_key,pair_role,display_order,created_at FROM schubert.media_assets ORDER BY id",
          "SELECT entry_id,audio_file_id,game_id,link_type,display_order,created_at FROM schubert.entry_audio_links ORDER BY entry_id,audio_file_id,link_type COLLATE \"C\"",
          "SELECT count(*) FROM schubert.script_entries WHERE body_search IS DISTINCT FROM pg_catalog.lower(body)");
  private static final List<String> CONTENT_TYPES =
      List.of(
          "LISSBST",
          "LILSSSSSSLT",
          "LILLIISLSSST",
          "LISSSSSSLLST",
          "LSSSSSSSSLSSSSSIT",
          "LLISIT",
          "L");
  private static final List<String> SQL =
      List.of(
          "SELECT a.attnum,a.attname,t.typname,pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity::text,a.attgenerated::text,CASE WHEN a.attnotnull THEN EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS TRUE) AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS NOT TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum]) END,CASE WHEN a.attidentity='d' THEN (SELECT count(*) FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a'))=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid LEFT JOIN pg_catalog.pg_sequence sq ON sq.seqrelid=sc.oid LEFT JOIN pg_catalog.pg_type st ON st.oid=sq.seqtypid LEFT JOIN pg_catalog.pg_namespace stn ON stn.oid=st.typnamespace WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a') AND (dep.deptype='i' AND sc.relnamespace=c.relnamespace AND sc.relowner=c.relowner AND sc.relpersistence='p' AND stn.nspname='pg_catalog' AND st.typname='int8' AND sq.seqstart=1 AND sq.seqincrement=1 AND sq.seqmin=1 AND sq.seqmax=999999999999 AND sq.seqcache=1 AND NOT sq.seqcycle) IS TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a')) END,pg_catalog.pg_get_userbyid(c.relowner),CASE WHEN (c.relname='speakers' AND a.attname='is_protagonist') OR (c.relname='script_entries' AND a.attname='body_search') THEN a.atthasdef AND (SELECT count(*) FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum)=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum AND pg_catalog.pg_get_expr(ad.adbin,ad.adrelid,false)=CASE WHEN c.relname='speakers' THEN 'false' ELSE 'lower(body)' END) ELSE NOT a.atthasdef AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum) END FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid JOIN pg_catalog.pg_type t ON t.oid=a.atttypid JOIN pg_catalog.pg_namespace tn ON tn.oid=t.typnamespace WHERE n.nspname='schubert' AND c.relname='speakers' AND c.relkind='r' AND c.relpersistence='p' AND tn.nspname='pg_catalog' AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum",
          "SELECT a.attnum,a.attname,t.typname,pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity::text,a.attgenerated::text,CASE WHEN a.attnotnull THEN EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS TRUE) AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS NOT TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum]) END,CASE WHEN a.attidentity='d' THEN (SELECT count(*) FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a'))=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid LEFT JOIN pg_catalog.pg_sequence sq ON sq.seqrelid=sc.oid LEFT JOIN pg_catalog.pg_type st ON st.oid=sq.seqtypid LEFT JOIN pg_catalog.pg_namespace stn ON stn.oid=st.typnamespace WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a') AND (dep.deptype='i' AND sc.relnamespace=c.relnamespace AND sc.relowner=c.relowner AND sc.relpersistence='p' AND stn.nspname='pg_catalog' AND st.typname='int8' AND sq.seqstart=1 AND sq.seqincrement=1 AND sq.seqmin=1 AND sq.seqmax=999999999999 AND sq.seqcache=1 AND NOT sq.seqcycle) IS TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a')) END,pg_catalog.pg_get_userbyid(c.relowner),CASE WHEN (c.relname='speakers' AND a.attname='is_protagonist') OR (c.relname='script_entries' AND a.attname='body_search') THEN a.atthasdef AND (SELECT count(*) FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum)=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum AND pg_catalog.pg_get_expr(ad.adbin,ad.adrelid,false)=CASE WHEN c.relname='speakers' THEN 'false' ELSE 'lower(body)' END) ELSE NOT a.atthasdef AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum) END FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid JOIN pg_catalog.pg_type t ON t.oid=a.atttypid JOIN pg_catalog.pg_namespace tn ON tn.oid=t.typnamespace WHERE n.nspname='schubert' AND c.relname='script_files' AND c.relkind='r' AND c.relpersistence='p' AND tn.nspname='pg_catalog' AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum",
          "SELECT a.attnum,a.attname,t.typname,pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity::text,a.attgenerated::text,CASE WHEN a.attnotnull THEN EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS TRUE) AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS NOT TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum]) END,CASE WHEN a.attidentity='d' THEN (SELECT count(*) FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a'))=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid LEFT JOIN pg_catalog.pg_sequence sq ON sq.seqrelid=sc.oid LEFT JOIN pg_catalog.pg_type st ON st.oid=sq.seqtypid LEFT JOIN pg_catalog.pg_namespace stn ON stn.oid=st.typnamespace WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a') AND (dep.deptype='i' AND sc.relnamespace=c.relnamespace AND sc.relowner=c.relowner AND sc.relpersistence='p' AND stn.nspname='pg_catalog' AND st.typname='int8' AND sq.seqstart=1 AND sq.seqincrement=1 AND sq.seqmin=1 AND sq.seqmax=999999999999 AND sq.seqcache=1 AND NOT sq.seqcycle) IS TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a')) END,pg_catalog.pg_get_userbyid(c.relowner),CASE WHEN (c.relname='speakers' AND a.attname='is_protagonist') OR (c.relname='script_entries' AND a.attname='body_search') THEN a.atthasdef AND (SELECT count(*) FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum)=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum AND pg_catalog.pg_get_expr(ad.adbin,ad.adrelid,false)=CASE WHEN c.relname='speakers' THEN 'false' ELSE 'lower(body)' END) ELSE NOT a.atthasdef AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum) END FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid JOIN pg_catalog.pg_type t ON t.oid=a.atttypid JOIN pg_catalog.pg_namespace tn ON tn.oid=t.typnamespace WHERE n.nspname='schubert' AND c.relname='script_entries' AND c.relkind='r' AND c.relpersistence='p' AND tn.nspname='pg_catalog' AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum",
          "SELECT a.attnum,a.attname,t.typname,pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity::text,a.attgenerated::text,CASE WHEN a.attnotnull THEN EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS TRUE) AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS NOT TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum]) END,CASE WHEN a.attidentity='d' THEN (SELECT count(*) FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a'))=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid LEFT JOIN pg_catalog.pg_sequence sq ON sq.seqrelid=sc.oid LEFT JOIN pg_catalog.pg_type st ON st.oid=sq.seqtypid LEFT JOIN pg_catalog.pg_namespace stn ON stn.oid=st.typnamespace WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a') AND (dep.deptype='i' AND sc.relnamespace=c.relnamespace AND sc.relowner=c.relowner AND sc.relpersistence='p' AND stn.nspname='pg_catalog' AND st.typname='int8' AND sq.seqstart=1 AND sq.seqincrement=1 AND sq.seqmin=1 AND sq.seqmax=999999999999 AND sq.seqcache=1 AND NOT sq.seqcycle) IS TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a')) END,pg_catalog.pg_get_userbyid(c.relowner),CASE WHEN (c.relname='speakers' AND a.attname='is_protagonist') OR (c.relname='script_entries' AND a.attname='body_search') THEN a.atthasdef AND (SELECT count(*) FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum)=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum AND pg_catalog.pg_get_expr(ad.adbin,ad.adrelid,false)=CASE WHEN c.relname='speakers' THEN 'false' ELSE 'lower(body)' END) ELSE NOT a.atthasdef AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum) END FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid JOIN pg_catalog.pg_type t ON t.oid=a.atttypid JOIN pg_catalog.pg_namespace tn ON tn.oid=t.typnamespace WHERE n.nspname='schubert' AND c.relname='audio_files' AND c.relkind='r' AND c.relpersistence='p' AND tn.nspname='pg_catalog' AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum",
          "SELECT a.attnum,a.attname,t.typname,pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity::text,a.attgenerated::text,CASE WHEN a.attnotnull THEN EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS TRUE) AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS NOT TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum]) END,CASE WHEN a.attidentity='d' THEN (SELECT count(*) FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a'))=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid LEFT JOIN pg_catalog.pg_sequence sq ON sq.seqrelid=sc.oid LEFT JOIN pg_catalog.pg_type st ON st.oid=sq.seqtypid LEFT JOIN pg_catalog.pg_namespace stn ON stn.oid=st.typnamespace WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a') AND (dep.deptype='i' AND sc.relnamespace=c.relnamespace AND sc.relowner=c.relowner AND sc.relpersistence='p' AND stn.nspname='pg_catalog' AND st.typname='int8' AND sq.seqstart=1 AND sq.seqincrement=1 AND sq.seqmin=1 AND sq.seqmax=999999999999 AND sq.seqcache=1 AND NOT sq.seqcycle) IS TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a')) END,pg_catalog.pg_get_userbyid(c.relowner),CASE WHEN (c.relname='speakers' AND a.attname='is_protagonist') OR (c.relname='script_entries' AND a.attname='body_search') THEN a.atthasdef AND (SELECT count(*) FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum)=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum AND pg_catalog.pg_get_expr(ad.adbin,ad.adrelid,false)=CASE WHEN c.relname='speakers' THEN 'false' ELSE 'lower(body)' END) ELSE NOT a.atthasdef AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum) END FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid JOIN pg_catalog.pg_type t ON t.oid=a.atttypid JOIN pg_catalog.pg_namespace tn ON tn.oid=t.typnamespace WHERE n.nspname='schubert' AND c.relname='media_assets' AND c.relkind='r' AND c.relpersistence='p' AND tn.nspname='pg_catalog' AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum",
          "SELECT a.attnum,a.attname,t.typname,pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity::text,a.attgenerated::text,CASE WHEN a.attnotnull THEN EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS TRUE) AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS NOT TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum]) END,CASE WHEN a.attidentity='d' THEN (SELECT count(*) FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a'))=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid LEFT JOIN pg_catalog.pg_sequence sq ON sq.seqrelid=sc.oid LEFT JOIN pg_catalog.pg_type st ON st.oid=sq.seqtypid LEFT JOIN pg_catalog.pg_namespace stn ON stn.oid=st.typnamespace WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a') AND (dep.deptype='i' AND sc.relnamespace=c.relnamespace AND sc.relowner=c.relowner AND sc.relpersistence='p' AND stn.nspname='pg_catalog' AND st.typname='int8' AND sq.seqstart=1 AND sq.seqincrement=1 AND sq.seqmin=1 AND sq.seqmax=999999999999 AND sq.seqcache=1 AND NOT sq.seqcycle) IS TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a')) END,pg_catalog.pg_get_userbyid(c.relowner),CASE WHEN (c.relname='speakers' AND a.attname='is_protagonist') OR (c.relname='script_entries' AND a.attname='body_search') THEN a.atthasdef AND (SELECT count(*) FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum)=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum AND pg_catalog.pg_get_expr(ad.adbin,ad.adrelid,false)=CASE WHEN c.relname='speakers' THEN 'false' ELSE 'lower(body)' END) ELSE NOT a.atthasdef AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum) END FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid JOIN pg_catalog.pg_type t ON t.oid=a.atttypid JOIN pg_catalog.pg_namespace tn ON tn.oid=t.typnamespace WHERE n.nspname='schubert' AND c.relname='entry_audio_links' AND c.relkind='r' AND c.relpersistence='p' AND tn.nspname='pg_catalog' AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum",
          "SELECT (row_number() OVER (ORDER BY k.conname COLLATE \"C\"))::integer,k.conname,k.contype::text,pg_catalog.array_to_string(k.conkey,','),(k.convalidated AND k.conenforced AND NOT k.condeferrable AND NOT k.condeferred AND k.conislocal AND k.coninhcount=0 AND k.conparentid=0 AND k.contypid=0 AND NOT k.conperiod),CASE WHEN k.contype='f' THEN rn.nspname||'.'||rc.relname||'('||pg_catalog.array_to_string(k.confkey,',')||')' ELSE '-' END,CASE WHEN k.contype='f' THEN k.confupdtype::text||'/'||k.confdeltype::text||'/'||k.confmatchtype::text ELSE '-' END FROM pg_catalog.pg_constraint k JOIN pg_catalog.pg_class c ON c.oid=k.conrelid JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_catalog.pg_class rc ON rc.oid=k.confrelid LEFT JOIN pg_catalog.pg_namespace rn ON rn.oid=rc.relnamespace WHERE n.nspname='schubert' AND k.connamespace=n.oid AND c.relname='speakers' AND c.relkind='r' AND c.relpersistence='p' AND k.contype NOT IN ('n','t') ORDER BY k.conname COLLATE \"C\"",
          "SELECT (row_number() OVER (ORDER BY k.conname COLLATE \"C\"))::integer,k.conname,k.contype::text,pg_catalog.array_to_string(k.conkey,','),(k.convalidated AND k.conenforced AND NOT k.condeferrable AND NOT k.condeferred AND k.conislocal AND k.coninhcount=0 AND k.conparentid=0 AND k.contypid=0 AND NOT k.conperiod),CASE WHEN k.contype='f' THEN rn.nspname||'.'||rc.relname||'('||pg_catalog.array_to_string(k.confkey,',')||')' ELSE '-' END,CASE WHEN k.contype='f' THEN k.confupdtype::text||'/'||k.confdeltype::text||'/'||k.confmatchtype::text ELSE '-' END FROM pg_catalog.pg_constraint k JOIN pg_catalog.pg_class c ON c.oid=k.conrelid JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_catalog.pg_class rc ON rc.oid=k.confrelid LEFT JOIN pg_catalog.pg_namespace rn ON rn.oid=rc.relnamespace WHERE n.nspname='schubert' AND k.connamespace=n.oid AND c.relname='script_files' AND c.relkind='r' AND c.relpersistence='p' AND k.contype NOT IN ('n','t') ORDER BY k.conname COLLATE \"C\"",
          "SELECT (row_number() OVER (ORDER BY k.conname COLLATE \"C\"))::integer,k.conname,k.contype::text,pg_catalog.array_to_string(k.conkey,','),(k.convalidated AND k.conenforced AND NOT k.condeferrable AND NOT k.condeferred AND k.conislocal AND k.coninhcount=0 AND k.conparentid=0 AND k.contypid=0 AND NOT k.conperiod),CASE WHEN k.contype='f' THEN rn.nspname||'.'||rc.relname||'('||pg_catalog.array_to_string(k.confkey,',')||')' ELSE '-' END,CASE WHEN k.contype='f' THEN k.confupdtype::text||'/'||k.confdeltype::text||'/'||k.confmatchtype::text ELSE '-' END FROM pg_catalog.pg_constraint k JOIN pg_catalog.pg_class c ON c.oid=k.conrelid JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_catalog.pg_class rc ON rc.oid=k.confrelid LEFT JOIN pg_catalog.pg_namespace rn ON rn.oid=rc.relnamespace WHERE n.nspname='schubert' AND k.connamespace=n.oid AND c.relname='script_entries' AND c.relkind='r' AND c.relpersistence='p' AND k.contype NOT IN ('n','t') ORDER BY k.conname COLLATE \"C\"",
          "SELECT (row_number() OVER (ORDER BY k.conname COLLATE \"C\"))::integer,k.conname,k.contype::text,pg_catalog.array_to_string(k.conkey,','),(k.convalidated AND k.conenforced AND NOT k.condeferrable AND NOT k.condeferred AND k.conislocal AND k.coninhcount=0 AND k.conparentid=0 AND k.contypid=0 AND NOT k.conperiod),CASE WHEN k.contype='f' THEN rn.nspname||'.'||rc.relname||'('||pg_catalog.array_to_string(k.confkey,',')||')' ELSE '-' END,CASE WHEN k.contype='f' THEN k.confupdtype::text||'/'||k.confdeltype::text||'/'||k.confmatchtype::text ELSE '-' END FROM pg_catalog.pg_constraint k JOIN pg_catalog.pg_class c ON c.oid=k.conrelid JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_catalog.pg_class rc ON rc.oid=k.confrelid LEFT JOIN pg_catalog.pg_namespace rn ON rn.oid=rc.relnamespace WHERE n.nspname='schubert' AND k.connamespace=n.oid AND c.relname='audio_files' AND c.relkind='r' AND c.relpersistence='p' AND k.contype NOT IN ('n','t') ORDER BY k.conname COLLATE \"C\"",
          "SELECT (row_number() OVER (ORDER BY k.conname COLLATE \"C\"))::integer,k.conname,k.contype::text,pg_catalog.array_to_string(k.conkey,','),(k.convalidated AND k.conenforced AND NOT k.condeferrable AND NOT k.condeferred AND k.conislocal AND k.coninhcount=0 AND k.conparentid=0 AND k.contypid=0 AND NOT k.conperiod),CASE WHEN k.contype='f' THEN rn.nspname||'.'||rc.relname||'('||pg_catalog.array_to_string(k.confkey,',')||')' ELSE '-' END,CASE WHEN k.contype='f' THEN k.confupdtype::text||'/'||k.confdeltype::text||'/'||k.confmatchtype::text ELSE '-' END FROM pg_catalog.pg_constraint k JOIN pg_catalog.pg_class c ON c.oid=k.conrelid JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_catalog.pg_class rc ON rc.oid=k.confrelid LEFT JOIN pg_catalog.pg_namespace rn ON rn.oid=rc.relnamespace WHERE n.nspname='schubert' AND k.connamespace=n.oid AND c.relname='media_assets' AND c.relkind='r' AND c.relpersistence='p' AND k.contype NOT IN ('n','t') ORDER BY k.conname COLLATE \"C\"",
          "SELECT (row_number() OVER (ORDER BY k.conname COLLATE \"C\"))::integer,k.conname,k.contype::text,pg_catalog.array_to_string(k.conkey,','),(k.convalidated AND k.conenforced AND NOT k.condeferrable AND NOT k.condeferred AND k.conislocal AND k.coninhcount=0 AND k.conparentid=0 AND k.contypid=0 AND NOT k.conperiod),CASE WHEN k.contype='f' THEN rn.nspname||'.'||rc.relname||'('||pg_catalog.array_to_string(k.confkey,',')||')' ELSE '-' END,CASE WHEN k.contype='f' THEN k.confupdtype::text||'/'||k.confdeltype::text||'/'||k.confmatchtype::text ELSE '-' END FROM pg_catalog.pg_constraint k JOIN pg_catalog.pg_class c ON c.oid=k.conrelid JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_catalog.pg_class rc ON rc.oid=k.confrelid LEFT JOIN pg_catalog.pg_namespace rn ON rn.oid=rc.relnamespace WHERE n.nspname='schubert' AND k.connamespace=n.oid AND c.relname='entry_audio_links' AND c.relkind='r' AND c.relpersistence='p' AND k.contype NOT IN ('n','t') ORDER BY k.conname COLLATE \"C\"",
          GAMES_SQL,
          "CREATE TEMP TABLE nk_mig_speakers ON COMMIT DROP AS SELECT id, game_id, name, normalized_name, is_protagonist, notes, created_at FROM schubert.speakers WITH NO DATA",
          "CREATE TEMP TABLE nk_mig_script_files ON COMMIT DROP AS SELECT id, game_id, display_order, storage_relative_path, display_path, file_name, section_code, chapter_title, sha256, byte_size, created_at FROM schubert.script_files WITH NO DATA",
          "CREATE TEMP TABLE nk_mig_script_entries ON COMMIT DROP AS SELECT id, game_id, script_file_id, display_order, entry_index, line_number, entry_type, speaker_id, speaker_label, body, raw_block, created_at FROM schubert.script_entries WITH NO DATA",
          "CREATE TEMP TABLE nk_mig_audio_files ON COMMIT DROP AS SELECT id, game_id, storage_relative_path, display_path, file_name, basename, audio_role, container, duration_ms, byte_size, sha256, created_at FROM schubert.audio_files WITH NO DATA",
          "CREATE TEMP TABLE nk_mig_media_assets ON COMMIT DROP AS SELECT id, logical_id, media_type, title, category, section, storage_relative_path, display_path, file_name, byte_size, sha256, mime_type, parent_logical_id, pair_key, pair_role, display_order, created_at FROM schubert.media_assets WITH NO DATA",
          "CREATE TEMP TABLE nk_mig_entry_audio_links ON COMMIT DROP AS SELECT entry_id, audio_file_id, game_id, link_type, display_order, created_at FROM schubert.entry_audio_links WITH NO DATA",
          "SELECT count(*) FROM schubert.speakers",
          "SELECT count(*) FROM pg_temp.nk_mig_speakers",
          "INSERT INTO schubert.speakers (id, game_id, name, normalized_name, is_protagonist, notes, created_at) SELECT id, game_id, name, normalized_name, is_protagonist, notes, created_at FROM pg_temp.nk_mig_speakers ORDER BY id",
          "SELECT count(*) FROM schubert.speakers",
          "SELECT count(*) FROM schubert.script_files",
          "SELECT count(*) FROM schubert.script_entries",
          "SELECT count(*) FROM pg_temp.nk_mig_script_files",
          "SELECT count(*) FROM pg_temp.nk_mig_script_entries",
          "INSERT INTO schubert.script_files (id, game_id, display_order, storage_relative_path, display_path, file_name, section_code, chapter_title, sha256, byte_size, created_at) SELECT id, game_id, display_order, storage_relative_path, display_path, file_name, section_code, chapter_title, sha256, byte_size, created_at FROM pg_temp.nk_mig_script_files ORDER BY game_id, display_order",
          "INSERT INTO schubert.script_entries (id, game_id, script_file_id, display_order, entry_index, line_number, entry_type, speaker_id, speaker_label, body, raw_block, created_at) SELECT id, game_id, script_file_id, display_order, entry_index, line_number, entry_type, speaker_id, speaker_label, body, raw_block, created_at FROM pg_temp.nk_mig_script_entries ORDER BY display_order",
          "SELECT count(*) FROM schubert.script_files",
          "SELECT count(*) FROM schubert.script_entries",
          "SELECT count(*) FROM schubert.audio_files",
          "SELECT count(*) FROM schubert.media_assets",
          "SELECT count(*) FROM schubert.entry_audio_links",
          "SELECT count(*) FROM pg_temp.nk_mig_audio_files",
          "SELECT count(*) FROM pg_temp.nk_mig_media_assets",
          "SELECT count(*) FROM pg_temp.nk_mig_entry_audio_links",
          "INSERT INTO schubert.audio_files (id, game_id, storage_relative_path, display_path, file_name, basename, audio_role, container, duration_ms, byte_size, sha256, created_at) SELECT id, game_id, storage_relative_path, display_path, file_name, basename, audio_role, container, duration_ms, byte_size, sha256, created_at FROM pg_temp.nk_mig_audio_files ORDER BY id",
          "INSERT INTO schubert.media_assets (id, logical_id, media_type, title, category, section, storage_relative_path, display_path, file_name, byte_size, sha256, mime_type, parent_logical_id, pair_key, pair_role, display_order, created_at) SELECT id, logical_id, media_type, title, category, section, storage_relative_path, display_path, file_name, byte_size, sha256, mime_type, parent_logical_id, pair_key, pair_role, display_order, created_at FROM pg_temp.nk_mig_media_assets ORDER BY id",
          "INSERT INTO schubert.entry_audio_links (entry_id, audio_file_id, game_id, link_type, display_order, created_at) SELECT entry_id, audio_file_id, game_id, link_type, display_order, created_at FROM pg_temp.nk_mig_entry_audio_links ORDER BY entry_id, link_type, display_order, audio_file_id",
          "SELECT count(*) FROM schubert.audio_files",
          "SELECT count(*) FROM schubert.media_assets",
          "SELECT count(*) FROM schubert.entry_audio_links",
          "SELECT count(*) FROM schubert.speakers",
          "SELECT count(*) FROM schubert.script_files",
          "SELECT count(*) FROM schubert.script_entries",
          "SELECT count(*) FROM schubert.audio_files",
          "SELECT count(*) FROM schubert.media_assets",
          "SELECT count(*) FROM schubert.entry_audio_links",
          "SELECT count(*) FROM schubert.script_files c LEFT JOIN schubert.games p ON p.id=c.game_id WHERE p.id IS NULL",
          "SELECT count(*) FROM schubert.speakers c LEFT JOIN schubert.games p ON p.id=c.game_id WHERE p.id IS NULL",
          "SELECT count(*) FROM schubert.script_entries c LEFT JOIN schubert.games p ON p.id=c.game_id WHERE p.id IS NULL",
          "SELECT count(*) FROM schubert.audio_files c LEFT JOIN schubert.games p ON p.id=c.game_id WHERE p.id IS NULL",
          "SELECT count(*) FROM schubert.script_entries c LEFT JOIN schubert.script_files p ON p.id=c.script_file_id AND p.game_id=c.game_id WHERE p.id IS NULL",
          "SELECT count(*) FROM schubert.script_entries c LEFT JOIN schubert.speakers p ON p.id=c.speaker_id AND p.game_id=c.game_id WHERE c.speaker_id IS NOT NULL AND p.id IS NULL",
          "SELECT count(*) FROM schubert.entry_audio_links c LEFT JOIN schubert.script_entries p ON p.id=c.entry_id AND p.game_id=c.game_id WHERE p.id IS NULL",
          "SELECT count(*) FROM schubert.entry_audio_links c LEFT JOIN schubert.audio_files p ON p.id=c.audio_file_id AND p.game_id=c.game_id WHERE p.id IS NULL",
          "SELECT count(*) FROM schubert.media_assets c LEFT JOIN schubert.media_assets p ON p.logical_id=c.parent_logical_id WHERE c.parent_logical_id IS NOT NULL AND p.logical_id IS NULL",
          "SELECT count(*) FROM (SELECT entry_id,link_type FROM schubert.entry_audio_links GROUP BY entry_id,link_type HAVING count(*)>999 OR min(display_order)<1 OR max(display_order)>999 OR count(DISTINCT display_order)<>count(*)) violations",
          "SELECT count(*) FROM schubert.speakers WHERE ((id BETWEEN 1 AND 999999999999) AND (octet_length(name) BETWEEN 1 AND 128) AND (octet_length(normalized_name) BETWEEN 1 AND 128)) IS FALSE",
          "SELECT count(*) FROM schubert.script_files WHERE ((byte_size BETWEEN 0 AND 999999999999) AND (\n        chapter_title IS NULL OR octet_length(chapter_title) <= 256) AND (display_order BETWEEN 1 AND 999999999999) AND (octet_length(display_path) BETWEEN 1 AND 512) AND (octet_length(file_name) BETWEEN 1 AND 256) AND (id BETWEEN 1 AND 999999999999) AND (sha256 ~ '^[0-9a-f]{64}$') AND (octet_length(storage_relative_path) BETWEEN 1 AND 512) AND (\n        storage_relative_path !~ '(^/|\\\\|(^|/)\\.\\.?(/|$)|//)')) IS FALSE",
          "SELECT count(*) FROM schubert.script_entries WHERE ((octet_length(body) BETWEEN 1 AND 4096) AND (display_order BETWEEN 1 AND 999999999999) AND (entry_index >= 0) AND (entry_type IN ('dialogue', 'narration')) AND (id BETWEEN 1 AND 999999999999) AND (line_number IS NULL OR line_number >= 1) AND (\n        (entry_type = 'dialogue' AND speaker_id IS NOT NULL)\n        OR (entry_type = 'narration' AND speaker_id IS NULL)) AND (\n        speaker_label IS NULL OR octet_length(speaker_label) <= 128)) IS FALSE",
          "SELECT count(*) FROM schubert.audio_files WHERE ((octet_length(audio_role) BETWEEN 1 AND 11) AND (octet_length(basename) BETWEEN 1 AND 255) AND (byte_size BETWEEN 1 AND 999999999999) AND (octet_length(display_path) BETWEEN 1 AND 512) AND (duration_ms IS NULL OR duration_ms BETWEEN 0 AND 999999999999) AND (octet_length(file_name) BETWEEN 1 AND 256) AND (id BETWEEN 1 AND 999999999999) AND (sha256 ~ '^[0-9a-f]{64}$') AND (octet_length(storage_relative_path) BETWEEN 1 AND 512) AND (\n        storage_relative_path !~ '(^/|\\\\|(^|/)\\.\\.?(/|$)|//)')) IS FALSE",
          "SELECT count(*) FROM schubert.media_assets WHERE ((byte_size BETWEEN 1 AND 999999999999) AND (octet_length(category) BETWEEN 1 AND 64) AND (display_order BETWEEN 1 AND 9999) AND (octet_length(display_path) BETWEEN 1 AND 512) AND (octet_length(file_name) BETWEEN 1 AND 256) AND (id BETWEEN 1 AND 999999999999) AND (octet_length(logical_id) BETWEEN 1 AND 64) AND (media_type IN ('VIDEO', 'MUSIC')) AND (\n        mime_type IN ('video/mp4', 'audio/mp4', 'audio/mpeg', 'audio/ogg', 'audio/wav', 'audio/flac')) AND ((\n        (media_type = 'VIDEO' AND pair_key IS NULL AND pair_role IS NULL)\n        OR (media_type = 'MUSIC' AND (\n            (pair_role IN ('M', 'I') AND octet_length(pair_key) BETWEEN 1 AND 256)\n            OR (pair_role = 'N' AND pair_key IS NULL)))\n    ) IS TRUE) AND (section IS NULL OR octet_length(section) <= 128) AND (sha256 ~ '^[0-9a-f]{64}$') AND (octet_length(storage_relative_path) BETWEEN 1 AND 512) AND (\n        storage_relative_path !~ '(^/|\\\\|(^|/)\\.\\.?(/|$)|//)') AND (octet_length(title) BETWEEN 1 AND 256)) IS FALSE",
          "SELECT count(*) FROM schubert.entry_audio_links WHERE ((display_order BETWEEN 1 AND 999) AND (link_type IN ('voice', 'se', 'bgm', 'other'))) IS FALSE",
          "SELECT count(*) FROM (SELECT 1 FROM schubert.speakers GROUP BY id HAVING count(*)>1 OR (id IS NULL) UNION ALL SELECT 1 FROM schubert.speakers WHERE game_id IS NOT NULL AND normalized_name IS NOT NULL GROUP BY game_id,normalized_name HAVING count(*)>1 UNION ALL SELECT 1 FROM schubert.speakers WHERE id IS NOT NULL AND game_id IS NOT NULL GROUP BY id,game_id HAVING count(*)>1) violations",
          "SELECT count(*) FROM (SELECT 1 FROM schubert.script_files GROUP BY id HAVING count(*)>1 OR (id IS NULL) UNION ALL SELECT 1 FROM schubert.script_files WHERE game_id IS NOT NULL AND display_order IS NOT NULL GROUP BY game_id,display_order HAVING count(*)>1 UNION ALL SELECT 1 FROM schubert.script_files WHERE game_id IS NOT NULL AND storage_relative_path IS NOT NULL GROUP BY game_id,storage_relative_path HAVING count(*)>1 UNION ALL SELECT 1 FROM schubert.script_files WHERE id IS NOT NULL AND game_id IS NOT NULL GROUP BY id,game_id HAVING count(*)>1) violations",
          "SELECT count(*) FROM (SELECT 1 FROM schubert.script_entries GROUP BY id HAVING count(*)>1 OR (id IS NULL) UNION ALL SELECT 1 FROM schubert.script_entries WHERE display_order IS NOT NULL GROUP BY display_order HAVING count(*)>1 UNION ALL SELECT 1 FROM schubert.script_entries WHERE script_file_id IS NOT NULL AND entry_index IS NOT NULL GROUP BY script_file_id,entry_index HAVING count(*)>1 UNION ALL SELECT 1 FROM schubert.script_entries WHERE id IS NOT NULL AND game_id IS NOT NULL GROUP BY id,game_id HAVING count(*)>1) violations",
          "SELECT count(*) FROM (SELECT 1 FROM schubert.audio_files GROUP BY id HAVING count(*)>1 OR (id IS NULL) UNION ALL SELECT 1 FROM schubert.audio_files WHERE game_id IS NOT NULL AND storage_relative_path IS NOT NULL GROUP BY game_id,storage_relative_path HAVING count(*)>1 UNION ALL SELECT 1 FROM schubert.audio_files WHERE id IS NOT NULL AND game_id IS NOT NULL GROUP BY id,game_id HAVING count(*)>1) violations",
          "SELECT count(*) FROM (SELECT 1 FROM schubert.media_assets GROUP BY id HAVING count(*)>1 OR (id IS NULL) UNION ALL SELECT 1 FROM schubert.media_assets WHERE logical_id IS NOT NULL GROUP BY logical_id HAVING count(*)>1 UNION ALL SELECT 1 FROM schubert.media_assets WHERE media_type IS NOT NULL AND storage_relative_path IS NOT NULL GROUP BY media_type,storage_relative_path HAVING count(*)>1) violations",
          "SELECT count(*) FROM (SELECT 1 FROM schubert.entry_audio_links GROUP BY entry_id,audio_file_id,link_type HAVING count(*)>1 OR (entry_id IS NULL OR audio_file_id IS NULL OR link_type IS NULL) UNION ALL SELECT 1 FROM schubert.entry_audio_links WHERE entry_id IS NOT NULL AND link_type IS NOT NULL AND display_order IS NOT NULL GROUP BY entry_id,link_type,display_order HAVING count(*)>1) violations",
          "SELECT id,game_id,name,normalized_name,is_protagonist,notes,created_at FROM schubert.speakers ORDER BY id",
          "SELECT id,game_id,display_order,storage_relative_path,display_path,file_name,section_code,chapter_title,sha256,byte_size,created_at FROM schubert.script_files ORDER BY id",
          "SELECT id,game_id,script_file_id,display_order,entry_index,line_number,entry_type,speaker_id,speaker_label,body,raw_block,created_at FROM schubert.script_entries ORDER BY id",
          "SELECT id,game_id,storage_relative_path,display_path,file_name,basename,audio_role,container,duration_ms,byte_size,sha256,created_at FROM schubert.audio_files ORDER BY id",
          "SELECT id,logical_id,media_type,title,category,section,storage_relative_path,display_path,file_name,byte_size,sha256,mime_type,parent_logical_id,pair_key,pair_role,display_order,created_at FROM schubert.media_assets ORDER BY id",
          "SELECT entry_id,audio_file_id,game_id,link_type,display_order,created_at FROM schubert.entry_audio_links ORDER BY entry_id,audio_file_id,link_type COLLATE \"C\"",
          "SELECT count(*) FROM schubert.script_entries WHERE body_search IS DISTINCT FROM pg_catalog.lower(body)",
          FLUSH_SQL,
          "SELECT COALESCE(MAX(id),0) FROM schubert.speakers",
          "SELECT COALESCE(MAX(id),0) FROM schubert.script_files",
          "SELECT COALESCE(MAX(id),0) FROM schubert.script_entries",
          "SELECT COALESCE(MAX(id),0) FROM schubert.audio_files",
          "SELECT COALESCE(MAX(id),0) FROM schubert.media_assets",
          "SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert.speakers', 'id'), ?, ?)",
          "SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert.script_files', 'id'), ?, ?)",
          "SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert.script_entries', 'id'), ?, ?)",
          "SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert.audio_files', 'id'), ?, ?)",
          "SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert.media_assets', 'id'), ?, ?)",
          "ANALYZE schubert.speakers",
          "ANALYZE schubert.script_files",
          "ANALYZE schubert.script_entries",
          "ANALYZE schubert.audio_files",
          "ANALYZE schubert.media_assets",
          "ANALYZE schubert.entry_audio_links");

  private static final long[] NORMAL_SCALARS = {
    0L, 1L, 1L, 0L, 0L, 1L, 1L, 1L, 1L, 0L, 0L, 0L, 1L, 1L, 1L, 1L, 1L, 1L, 1L, 1L, 1L, 1L, 1L, 1L,
    0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 0L, 42L,
    700L, 900L, 500L, 600L, 42L, 700L, 900L, 500L, 600L
  };

  @Test
  void target001OneConnectionFixedNinetyFourSqlAndExactResources() throws Exception {
    var f = new Fixture();
    workflow(new MigrationMasterTargetPublisher(), f, normal());
    assertEquals(SQL, f.sql);
    assertEquals(RESULTS, f.resultCloses);
    assertEquals(CLOSES, f.closeAttempts);
    assertEquals(12, f.autoReads);
    assertEquals(12, f.statementCreates);
    assertEquals(5, f.preparedCreates);
    assertEquals(5, f.preparedExecutions);
    assertEquals(6, f.analyzes);
    assertEquals(java.util.Collections.nCopies(CLOSES, 30), f.timeouts);
    assertEquals(List.of(42L, 700L, 900L, 500L, 600L), f.boundLong);
    assertEquals(java.util.Collections.nCopies(5, true), f.boundBoolean);
  }

  @Test
  void target002EmptyHasNoInventedRowsAndOneFalseSetval() throws Exception {
    var f = new Fixture();
    f.empty = true;
    f.scalars = new long[SCALARS];
    Arrays.fill(f.scalars, SETVAL_SCALAR_FIRST, SCALARS, 1L);
    workflow(
        new MigrationMasterTargetPublisher(),
        f,
        new MigrationMasterCopyDataset(new SpeakerCopyBatch(List.of()), emptyContent()));
    assertEquals(SQL, f.sql);
    assertEquals(List.of(1L, 1L, 1L, 1L, 1L), f.boundLong);
    assertEquals(java.util.Collections.nCopies(5, false), f.boundBoolean);
    assertEquals(RESULTS, f.resultCloses);
    assertEquals(CLOSES, f.closeAttempts);
  }

  @Test
  void target003NullPrepareIsRejectedBeforeDelegation() {
    assertEquals(
        "migration master target input is invalid",
        assertThrows(
                IllegalArgumentException.class,
                () -> new MigrationMasterTargetPublisher().prepare(null))
            .getMessage());
  }

  @Test
  void target004AllNullTransferCombinationsHaveNoConnectionCalls() throws Exception {
    var f = new Fixture();
    var conn = f.connection();
    var declared = normal();
    var publisher = new MigrationMasterTargetPublisher();
    assertThrows(
        IllegalArgumentException.class, () -> publisher.transferAndFinalize(null, declared));
    assertThrows(IllegalArgumentException.class, () -> publisher.transferAndFinalize(conn, null));
    assertEquals(
        "migration master target input is invalid",
        assertThrows(
                IllegalArgumentException.class, () -> publisher.transferAndFinalize(null, null))
            .getMessage());
    assertEquals(0, f.autoReads);
    assertEquals(0, f.statementCreates);
    assertTrue(f.sql.isEmpty());
  }

  @Test
  void target005AutoCommitDelegationNeverMutatesConnection() throws Exception {
    var prepare = new Fixture();
    prepare.autoCommit = true;
    assertThrows(
        SQLException.class,
        () -> new MigrationMasterTargetPublisher().prepare(prepare.connection()));
    assertTrue(prepare.sql.isEmpty());
    assertEquals(0, prepare.closeAttempts);
    var transfer = new Fixture();
    transfer.autoCommit = true;
    assertThrows(
        SQLException.class,
        () ->
            new MigrationMasterTargetPublisher()
                .transferAndFinalize(transfer.connection(), normal()));
    assertTrue(transfer.sql.isEmpty());
    assertEquals(0, transfer.closeAttempts);
  }

  @Test
  void target006EveryPrepareSqlOriginalFailureStopsThePath() throws Exception {
    sqlFailures(0, PREPARE_END);
  }

  @Test
  void target007EveryTransferSqlOriginalFailureStopsThePath() throws Exception {
    sqlFailures(PREPARE_END, TRANSFER_END);
  }

  @Test
  void target008EveryReferenceSqlFailurePreventsSetvalAndAnalyze() throws Exception {
    sqlFailures(TRANSFER_END, REFERENCE_END);
  }

  @Test
  void target009EveryFinalizationSqlAndPreparedExecuteOriginalFailure() throws Exception {
    sqlFailures(CONTENT_END, SQL_COUNT);
    for (int slot = 0; slot < 5; slot++)
      for (Throwable failure : failures()) {
        var f = new Fixture();
        f.badPreparedExecute = slot;
        f.failure = failure;
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () -> workflow(new MigrationMasterTargetPublisher(), f, normal())));
        assertEquals(SQL.subList(0, SETVAL_FIRST + slot + 1), f.sql);
        assertEquals(
            SETVAL_SCALAR_FIRST + CONTENT_TABLES + CATALOG_TABLES + GAME_RESULTS + slot,
            f.resultCloses);
        assertEquals(13 + slot, f.closeAttempts);
        assertEquals(slot + 1, f.preparedExecutions);
        assertEquals(0, f.analyzes);
      }
  }

  @Test
  void target010EveryTransferScalarMismatchCannotReachLaterStage() throws Exception {
    for (int query = 0; query < TRANSFER_SCALARS; query++) {
      var f = new Fixture();
      f.badScalar = query;
      assertThrows(
          SQLException.class, () -> workflow(new MigrationMasterTargetPublisher(), f, normal()));
      int sqlIndex = scalarSqlIndex(query);
      assertEquals(SQL.subList(0, sqlIndex + 1), f.sql);
      assertEquals(CATALOG_TABLES + GAME_RESULTS + query + 1, f.resultCloses);
      assertEquals(ordinaryOwnersThrough(sqlIndex), f.closeAttempts);
      assertEquals(0, f.preparedExecutions);
    }
  }

  @Test
  void target011EveryReferenceOrphanAndOrderViolationPreventsSequenceMutation() throws Exception {
    for (int query = ORPHAN_FIRST; query < REFERENCE_SCALARS_END; query++) {
      var f = new Fixture();
      f.badScalar = query;
      assertThrows(
          SQLException.class, () -> workflow(new MigrationMasterTargetPublisher(), f, normal()));
      assertEquals(SQL.subList(0, scalarSqlIndex(query) + 1), f.sql);
      assertEquals(CATALOG_TABLES + GAME_RESULTS + query + 1, f.resultCloses);
      assertEquals(10, f.closeAttempts);
      assertEquals(0, f.preparedExecutions);
      assertEquals(0, f.analyzes);
    }
  }

  @Test
  void target012PartialSetvalAndAnalyzeWarningAreNotRetriedOrSuccess() throws Exception {
    for (int slot = 0; slot < 5; slot++) {
      var f = new Fixture();
      f.badScalar = SETVAL_SCALAR_FIRST + slot;
      assertThrows(
          SQLException.class, () -> workflow(new MigrationMasterTargetPublisher(), f, normal()));
      assertEquals(SQL.subList(0, SETVAL_FIRST + slot + 1), f.sql);
      assertEquals(slot + 1, f.preparedExecutions);
      assertEquals(13 + slot, f.closeAttempts);
      assertEquals(0, f.analyzes);
    }
    for (int slot = 0; slot < 6; slot++) {
      var f = new Fixture();
      f.badWarning = slot;
      assertThrows(
          SQLException.class, () -> workflow(new MigrationMasterTargetPublisher(), f, normal()));
      assertEquals(SQL.subList(0, ANALYZE_FIRST + slot + 1), f.sql);
      assertEquals(5, f.preparedExecutions);
      assertEquals(slot + 1, f.analyzes);
      assertEquals(CLOSES, f.closeAttempts);
      assertEquals(RESULTS, f.resultCloses);
    }
  }

  @Test
  void target013EveryOwnedStatementCloseFailureKeepsExactPrefixAndOuterOwnership()
      throws Exception {
    for (int close = 0; close < CLOSES; close++)
      for (Throwable failure : failures()) {
        var f = new Fixture();
        f.badClose = close;
        f.closeFailure = failure;
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () -> workflow(new MigrationMasterTargetPublisher(), f, normal())));
        assertEquals(SQL.subList(0, CLOSE_SQL_PREFIX.get(close)), f.sql);
        assertEquals(CLOSE_RESULTS.get(close), f.resultCloses);
        assertEquals(
            close + 1 + (close >= PREPARED_FIRST_CLOSE && close < OUTER_FINAL_CLOSE ? 1 : 0),
            f.closeAttempts);
      }
  }

  @Test
  void target014OriginalReadFailureKeepsResultThenStatementSuppressedOrder() throws Exception {
    for (Throwable primary : failures()) {
      var f = new Fixture();
      f.badRead = 0;
      f.failure = primary;
      f.extraResultAt = 0;
      var result = new SQLException("synthetic inner close");
      var outer = new IllegalStateException("synthetic statement close");
      f.extraResult = result;
      f.badClose = 6;
      f.closeFailure = outer;
      assertSame(
          primary,
          assertThrows(
              primary.getClass(),
              () -> workflow(new MigrationMasterTargetPublisher(), f, normal())));
      assertEquals(List.of(result, outer), List.of(primary.getSuppressed()));
      assertEquals(SQL.subList(0, 20), f.sql);
      assertEquals(CATALOG_TABLES + GAME_RESULTS + 1, f.resultCloses);
      assertEquals(7, f.closeAttempts);
      assertEquals(0, f.preparedExecutions);
    }
  }

  @Test
  void target015FixedRedactionAndSamePublisherFreshConnectionAfterFailure() throws Exception {
    var publisher = new MigrationMasterTargetPublisher();
    assertEquals("MigrationMasterTargetPublisher[REDACTED]", publisher.toString());
    var failed = new Fixture();
    failed.badSql = PREPARE_END;
    assertThrows(SQLException.class, () -> workflow(publisher, failed, normal()));
    var next = new Fixture();
    workflow(publisher, next, normal());
    assertEquals(SQL, next.sql);
    assertEquals(PREPARE_END + 1, failed.sql.size());
    assertEquals(CLOSES, next.closeAttempts);
  }

  @Test
  void target016SharedPublisherFiniteIndependentConnectionsAndTermination() throws Exception {
    var publisher = new MigrationMasterTargetPublisher();
    var declared = normal();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<List<String>>>();
      for (int index = 0; index < TASKS; index++)
        futures.add(
            executor.submit(
                () -> {
                  var f = new Fixture();
                  workflow(publisher, f, declared);
                  assertEquals(CLOSES, f.closeAttempts);
                  assertEquals(RESULTS, f.resultCloses);
                  return f.sql;
                }));
      for (var future : futures) assertEquals(SQL, future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  @Test
  void target017AllSixContentQueryFaultsStopBeforeFinalization() throws Exception {
    sqlFailures(REFERENCE_END, CONTENT_END);
  }

  @Test
  void target018AllSixtyFiveValueChangesStopBeforeMaxSetvalAnalyze() throws Exception {
    for (int table = 0; table < CONTENT_TABLES; table++) {
      for (int column = 0; column < CONTENT_TYPES.get(table).length(); column++) {
        var f = new Fixture();
        f.badContentTable = table;
        f.badContentColumn = column;
        assertThrows(
            SQLException.class, () -> workflow(new MigrationMasterTargetPublisher(), f, normal()));
        contentFailurePost(f, table, true);
      }
    }
  }

  @Test
  void target019NullContentResultsDoNotCreateResultOwnership() throws Exception {
    for (int table = 0; table < CONTENT_TABLES; table++) {
      var f = new Fixture();
      f.nullContentResult = table;
      assertThrows(
          SQLException.class, () -> workflow(new MigrationMasterTargetPublisher(), f, normal()));
      contentFailurePost(f, table, false);
    }
  }

  @Test
  void target020MissingAndExtraRowsHaveNoExtraColumnReads() throws Exception {
    for (int table = 0; table < CONTENT_TABLES; table++) {
      for (boolean missing : List.of(true, false)) {
        var f = new Fixture();
        if (missing) f.missingContent = table;
        else f.extraContent = table;
        assertThrows(
            SQLException.class, () -> workflow(new MigrationMasterTargetPublisher(), f, normal()));
        int expected = CONTENT_TYPES.subList(0, table).stream().mapToInt(String::length).sum();
        if (!missing) expected += CONTENT_TYPES.get(table).length();
        assertEquals(expected, f.contentFieldReads);
        contentFailurePost(f, table, true);
      }
    }
  }

  @Test
  void target021RequiredSqlNullNeverBecomesZeroFalseOrEmpty() throws Exception {
    for (int table = 0; table < CONTENT_TABLES; table++) {
      for (int column = 0; column < CONTENT_TYPES.get(table).length(); column++) {
        if (contentLiteral(table).get(column) == null) continue;
        var f = new Fixture();
        f.badContentTable = table;
        f.badContentColumn = column;
        f.nullContentValue = true;
        assertThrows(
            SQLException.class, () -> workflow(new MigrationMasterTargetPublisher(), f, normal()));
        contentFailurePost(f, table, true);
      }
    }
  }

  @Test
  void target022EveryContentGetterKeepsPrimaryThenBothCleanupIdentities() throws Exception {
    for (int table = 0; table < CONTENT_TABLES; table++) {
      for (int column = 0; column < CONTENT_TYPES.get(table).length(); column++) {
        for (Throwable primary : failures()) {
          var f = new Fixture();
          f.badContentTable = table;
          f.badContentColumn = column;
          f.failContentRead = true;
          f.failure = primary;
          var inner = new SQLException("synthetic content close");
          var outer = new IllegalStateException("synthetic content statement close");
          f.extraResult = inner;
          f.badClose = CONTENT_CLOSE;
          f.closeFailure = outer;
          assertSame(
              primary,
              assertThrows(
                  primary.getClass(),
                  () -> workflow(new MigrationMasterTargetPublisher(), f, normal())));
          assertEquals(2, primary.getSuppressed().length);
          assertSame(inner, primary.getSuppressed()[0]);
          assertSame(outer, primary.getSuppressed()[1]);
          contentFailurePost(f, table, true);
        }
      }
    }
  }

  @Test
  void target023ScalarAndTypedResultsRemainSeparateOnOneBorrowedConnection() throws Exception {
    var f = new Fixture();
    var declared = normal();
    workflow(new MigrationMasterTargetPublisher(), f, declared);
    assertEquals(CONTENT_COLUMNS, f.contentFieldReads);
    assertEquals(SCALARS, f.scalarReads);
    assertEquals(RESULTS, f.resultCloses);
    assertEquals(CLOSES, f.closeAttempts);
    assertEquals(List.of(1000, 1000, 1000, 1000), f.fetchSizes);
    assertEquals(SQL, f.sql);
    assertEquals(SPEAKER_ID, declared.speakers().rows().getFirst().fields().getFirst());
  }

  @Test
  void target024FiniteFailedContentCallsCannotReachFinalizerOrRetainResources() throws Exception {
    var publisher = new MigrationMasterTargetPublisher();
    var declared = normal();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<Integer>>();
      for (int index = 0; index < TASKS; index++) {
        int table = index % CONTENT_TABLES;
        futures.add(
            executor.submit(
                () -> {
                  var f = new Fixture();
                  f.badContentTable = table;
                  f.badContentColumn = 0;
                  assertThrows(SQLException.class, () -> workflow(publisher, f, declared));
                  contentFailurePost(f, table, true);
                  return f.closeAttempts;
                }));
      }
      for (var future : futures) assertEquals(11, future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  @Test
  void target025AllCatalogSqlFaultsPreventAnyStagingDdl() throws Exception {
    sqlFailures(0, CATALOG_END);
    for (int table = 0; table < CATALOG_TABLES; table++) {
      var f = new Fixture();
      f.badSql = table;
      Throwable primary = f.failure;
      assertSame(
          primary,
          assertThrows(
              primary.getClass(),
              () -> workflow(new MigrationMasterTargetPublisher(), f, normal())));
      catalogFailurePost(f, table, false);
    }
  }

  @Test
  void target026All141CatalogRowAttributesMismatchBeforeDdl() throws Exception {
    for (int table = 0; table < CATALOG_TABLES; table++) {
      for (int row = 0; row < CATALOG_ROWS.get(table).size(); row++) {
        for (int field = 0; field < catalogFieldCount(table); field++) {
          var f = new Fixture();
          f.badCatalogTable = table;
          f.badCatalogRow = row;
          f.badCatalogField = field;
          assertThrows(
              SQLException.class,
              () -> workflow(new MigrationMasterTargetPublisher(), f, normal()));
          catalogFailurePost(f, table, true);
        }
      }
    }
  }

  @Test
  void target027NullCatalogResultHasOnlyPreviousResultOwnership() throws Exception {
    for (int table = 0; table < CATALOG_TABLES; table++) {
      var f = new Fixture();
      f.nullCatalogResult = table;
      assertThrows(
          SQLException.class, () -> workflow(new MigrationMasterTargetPublisher(), f, normal()));
      catalogFailurePost(f, table, false);
    }
  }

  @Test
  void target028MissingExtraCatalogColumnsHaveNoExtraFieldRead() throws Exception {
    for (int table = 0; table < CATALOG_TABLES; table++) {
      for (boolean missing : List.of(true, false)) {
        var f = new Fixture();
        if (missing) f.missingCatalog = table;
        else f.extraCatalog = table;
        assertThrows(
            SQLException.class, () -> workflow(new MigrationMasterTargetPublisher(), f, normal()));
        int expected =
            IntStream.rangeClosed(0, table)
                .map(index -> CATALOG_ROWS.get(index).size() * catalogFieldCount(index))
                .sum();
        assertEquals(expected - (missing ? catalogFieldCount(table) : 0), f.catalogFieldReads);
        catalogFailurePost(f, table, true);
      }
    }
  }

  @Test
  void target029EveryMetadataSqlNullDiffersFromZeroFalseAndEmpty() throws Exception {
    for (int table = 0; table < CATALOG_TABLES; table++) {
      for (int row = 0; row < CATALOG_ROWS.get(table).size(); row++) {
        for (int field = 0; field < catalogFieldCount(table); field++) {
          var f = new Fixture();
          f.badCatalogTable = table;
          f.badCatalogRow = row;
          f.badCatalogField = field;
          f.nullCatalogValue = true;
          assertThrows(
              SQLException.class,
              () -> workflow(new MigrationMasterTargetPublisher(), f, normal()));
          catalogFailurePost(f, table, true);
        }
      }
    }
  }

  @Test
  void target030EveryCatalogGetterKeepsPrimaryThenBothCleanupIdentities() throws Exception {
    for (int table = 0; table < CATALOG_TABLES; table++) {
      for (int row = 0; row < CATALOG_ROWS.get(table).size(); row++) {
        for (int field = 0; field < catalogFieldCount(table); field++) {
          for (Throwable primary : failures()) {
            var f = new Fixture();
            f.badCatalogTable = table;
            f.badCatalogRow = row;
            f.badCatalogField = field;
            f.failCatalogRead = true;
            f.failure = primary;
            var inner = new SQLException("synthetic catalog close");
            var outer = new IllegalStateException("synthetic catalog statement close");
            f.extraResult = inner;
            f.badClose = table / 6;
            f.closeFailure = outer;
            assertSame(
                primary,
                assertThrows(
                    primary.getClass(),
                    () -> workflow(new MigrationMasterTargetPublisher(), f, normal())));
            assertEquals(2, primary.getSuppressed().length);
            assertSame(inner, primary.getSuppressed()[0]);
            assertSame(outer, primary.getSuppressed()[1]);
            catalogFailurePost(f, table, true);
          }
        }
      }
    }
  }

  @Test
  void target031CatalogContentScalarResultsKeepSeparateOwnershipAndCounts() throws Exception {
    var f = new Fixture();
    workflow(new MigrationMasterTargetPublisher(), f, normal());
    assertEquals(MIXED_CATALOG_GETTERS, f.catalogFieldReads);
    assertEquals(CONTENT_COLUMNS, f.contentFieldReads);
    assertEquals(SCALARS, f.scalarReads);
    assertEquals(10, f.gamesFieldReads);
    assertEquals(RESULTS, f.resultCloses);
    assertEquals(CLOSES, f.closeAttempts);
    assertEquals(List.of(1000, 1000, 1000, 1000), f.fetchSizes);
    assertEquals(SQL, f.sql);
  }

  @Test
  void target032FiniteCatalogFailureCannotReachDdlOrRetainResources() throws Exception {
    var publisher = new MigrationMasterTargetPublisher();
    var declared = normal();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<Integer>>();
      for (int index = 0; index < TASKS; index++) {
        int table = index % CATALOG_TABLES;
        futures.add(
            executor.submit(
                () -> {
                  var f = new Fixture();
                  f.badCatalogTable = table;
                  f.badCatalogRow = 0;
                  f.badCatalogField = 1;
                  assertThrows(SQLException.class, () -> workflow(publisher, f, declared));
                  catalogFailurePost(f, table, true);
                  return f.preparedCreates;
                }));
      }
      for (var future : futures) assertEquals(0, future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  @Test
  void target033AllInitialGameValueChangesPreventAnyStagingDdl() throws Exception {
    for (int row = 0; row < 2; row++)
      for (int field = 0; field < GAMES_FIELDS; field++)
        for (boolean nul : List.of(false, true)) {
          var f = new Fixture();
          f.badGamesRow = row;
          f.badGamesField = field;
          f.nullGamesValue = nul;
          assertThrows(
              SQLException.class,
              () -> workflow(new MigrationMasterTargetPublisher(), f, normal()));
          assertEquals(SQL.subList(0, GAMES_QUERY_INDEX + 1), f.sql);
          assertEquals(CATALOG_TABLES + GAME_RESULTS, f.resultCloses);
          assertEquals(GAMES_OWNER_CLOSE + 1, f.closeAttempts);
          assertEquals(0, f.preparedCreates);
          assertEquals(0, f.preparedExecutions);
          assertEquals(0, f.analyzes);
          assertTrue(
              f.sql.stream()
                  .noneMatch(query -> query.startsWith("CREATE ") || query.startsWith("INSERT ")));
        }
  }

  @Test
  void target034AllTenGameGettersKeepPrimaryAndBothCleanupIdentities() throws Exception {
    for (int row = 0; row < 2; row++)
      for (int field = 0; field < GAMES_FIELDS; field++)
        for (int kind = 0; kind < 3; kind++) {
          for (boolean self : List.of(false, true)) {
            Throwable primary = failures().get(kind);
            var f = new Fixture();
            f.badGamesRow = row;
            f.badGamesField = field;
            f.failGamesRead = true;
            f.failure = primary;
            Throwable inner = self ? primary : new SQLException("synthetic game result close");
            Throwable outer =
                self ? primary : new IllegalStateException("synthetic game statement close");
            f.gamesCloseFailure = inner;
            f.badClose = GAMES_OWNER_CLOSE;
            f.closeFailure = outer;
            assertSame(
                primary,
                assertThrows(
                    primary.getClass(),
                    () -> workflow(new MigrationMasterTargetPublisher(), f, normal())));
            if (self) assertEquals(0, primary.getSuppressed().length);
            else {
              assertSame(inner, primary.getSuppressed()[0]);
              assertSame(outer, primary.getSuppressed()[1]);
            }
            assertEquals(SQL.subList(0, GAMES_QUERY_INDEX + 1), f.sql);
            assertEquals(CATALOG_TABLES + GAME_RESULTS, f.resultCloses);
            assertEquals(GAMES_OWNER_CLOSE + 1, f.closeAttempts);
            assertEquals(0, f.preparedCreates);
          }
        }
  }

  @Test
  void target035EveryColumnOwnerMismatchStopsBeforeAnyStaging() throws Exception {
    var publisher = new MigrationMasterTargetPublisher();
    var declared = normal();
    for (int table = 0; table < COLUMN_CATALOG_TABLES; table++) {
      for (int row = 0; row < CATALOG_ROWS.get(table).size(); row++) {
        for (boolean sqlNull : List.of(false, true)) {
          var f = new Fixture();
          f.badCatalogTable = table;
          f.badCatalogRow = row;
          f.badCatalogField = OWNER_FIELD;
          f.nullCatalogValue = sqlNull;
          assertThrows(SQLException.class, () -> workflow(publisher, f, declared));
          catalogFailurePost(f, table, true);
        }
      }
    }
  }

  @Test
  void target036EveryDefaultMetadataRejectionStopsBeforeAnyStaging() throws Exception {
    var publisher = new MigrationMasterTargetPublisher();
    var declared = normal();
    for (int table = 0; table < COLUMN_CATALOG_TABLES; table++) {
      for (int row = 0; row < CATALOG_ROWS.get(table).size(); row++) {
        for (boolean sqlNull : List.of(false, true)) {
          var f = new Fixture();
          f.badCatalogTable = table;
          f.badCatalogRow = row;
          f.badCatalogField = DEFAULT_FIELD;
          f.nullCatalogValue = sqlNull;
          assertThrows(SQLException.class, () -> workflow(publisher, f, declared));
          catalogFailurePost(f, table, true);
        }
      }
    }
  }

  @Test
  void target037DeferredConstraintRejectionStopsBeforeSequence() throws Exception {
    var publisher = new MigrationMasterTargetPublisher();
    var declared = normal();
    for (boolean warning : List.of(false, true)) {
      var f = new Fixture();
      f.badConstraintUpdate = !warning;
      f.badConstraintWarning = warning;
      assertThrows(SQLException.class, () -> workflow(publisher, f, declared));
      assertEquals(SQL.subList(0, CONTENT_END + 1), f.sql);
      assertEquals(REFERENCE_SCALARS_END, f.scalarReads);
      assertEquals(0, f.preparedCreates);
      assertEquals(0, f.preparedExecutions);
      assertEquals(0, f.analyzes);
      assertEquals(CLOSE_RESULTS.get(CONTENT_CLOSE), f.resultCloses);
      assertEquals(PREPARED_FIRST_CLOSE + 1, f.closeAttempts);
    }
  }

  @Test
  void target038DeferredPhaseFailureKeepsPrimaryAndCleanupIdentity() throws Exception {
    var publisher = new MigrationMasterTargetPublisher();
    var declared = normal();
    for (boolean warningPhase : List.of(false, true)) {
      for (int kind = 0; kind < failures().size(); kind++) {
        for (int cleanup = 0; cleanup <= failures().size(); cleanup++) {
          Throwable primary = failures().get(kind);
          Throwable secondary = cleanup == failures().size() ? primary : failures().get(cleanup);
          var f = new Fixture();
          f.badSql = warningPhase ? -1 : CONTENT_END;
          f.failConstraintWarning = warningPhase;
          f.failure = primary;
          f.badClose = PREPARED_FIRST_CLOSE;
          f.closeFailure = secondary;
          assertSame(
              primary, assertThrows(primary.getClass(), () -> workflow(publisher, f, declared)));
          assertEquals(secondary == primary ? 0 : 1, primary.getSuppressed().length);
          if (secondary != primary) assertSame(secondary, primary.getSuppressed()[0]);
          assertEquals(SQL.subList(0, CONTENT_END + 1), f.sql);
          assertEquals(0, f.preparedCreates);
          assertEquals(0, f.preparedExecutions);
          assertEquals(0, f.analyzes);
          assertEquals(CLOSE_RESULTS.get(CONTENT_CLOSE), f.resultCloses);
          assertEquals(PREPARED_FIRST_CLOSE + 1, f.closeAttempts);
        }
      }
    }
  }

  private static int catalogFieldCount(int table) {
    return table < COLUMN_CATALOG_TABLES ? COLUMN_CATALOG_FIELDS : CATALOG_FIELDS;
  }

  private static void catalogFailurePost(Fixture f, int table, boolean ownedResult) {
    assertEquals(CATALOG_SQL.subList(0, table + 1), f.sql);
    assertEquals(table + (ownedResult ? 1 : 0), f.resultCloses);
    assertEquals(table / 6 + 1, f.closeAttempts);
    assertEquals(0, f.preparedCreates);
    assertEquals(0, f.preparedExecutions);
    assertEquals(0, f.analyzes);
    assertTrue(
        f.sql.stream()
            .noneMatch(
                query ->
                    query.startsWith("CREATE ")
                        || query.startsWith("INSERT ")
                        || query.startsWith("ANALYZE ")));
  }

  private static void contentFailurePost(Fixture f, int table, boolean ownedResult) {
    assertEquals(SQL.subList(0, REFERENCE_END + table + 1), f.sql);
    assertEquals(
        REFERENCE_SCALARS_END + CATALOG_TABLES + GAME_RESULTS + table + (ownedResult ? 1 : 0),
        f.resultCloses);
    assertEquals(11, f.closeAttempts);
    assertEquals(0, f.preparedCreates);
    assertEquals(0, f.preparedExecutions);
    assertEquals(0, f.analyzes);
  }

  private static String contentGetter(char kind) {
    return switch (kind) {
      case 'L' -> GET_LONG;
      case 'I' -> GET_INT;
      case 'B' -> GET_BOOLEAN;
      case 'T' -> GET_TIMESTAMP;
      default -> GET_STRING;
    };
  }

  private static String changedContent(@Nullable String value, char kind) {
    if (value == null) return kind == 'L' || kind == 'I' ? ONE : "changed";
    return switch (kind) {
      case 'L', 'I' -> Long.toString(Long.parseLong(value) + 1);
      case 'B' -> value.equals(TRUE_TEXT) ? "false" : TRUE_TEXT;
      case 'T' -> Instant.parse(value).plusNanos(1000).toString();
      default -> value + "X";
    };
  }

  private static List<@Nullable String> contentLiteral(int table) {
    return switch (table) {
      case 0 ->
          Arrays.<@Nullable String>asList(
              SPEAKER_ID, ONE, "Alice", "alice", TRUE_TEXT, null, STAMP);
      case 1 ->
          Arrays.<@Nullable String>asList(
              FILE_ID_TEXT,
              ONE,
              ONE,
              "script/file.txt",
              FILE_NAME_TEXT,
              FILE_NAME_TEXT,
              null,
              "chapter",
              SHA,
              THREE,
              STAMP);
      case 2 ->
          Arrays.<@Nullable String>asList(
              ENTRY_ID_TEXT,
              ONE,
              FILE_ID_TEXT,
              ONE,
              "0",
              null,
              "dialogue",
              SPEAKER_ID,
              null,
              "hello",
              "raw",
              STAMP);
      case 3 ->
          Arrays.<@Nullable String>asList(
              AUDIO_ID_TEXT,
              ONE,
              "voice/a.ogg",
              "表示",
              "a.ogg",
              "a",
              VOICE_TEXT,
              "ogg",
              "1200",
              THREE,
              SHA,
              STAMP);
      case 4 ->
          Arrays.<@Nullable String>asList(
              "600",
              "video-a",
              VIDEO,
              "A",
              "MAIN",
              null,
              TARGET_VIDEO,
              SOURCE_VIDEO,
              "a.mp4",
              THREE,
              SHA,
              "video/mp4",
              null,
              null,
              null,
              ONE,
              STAMP);
      case 5 ->
          Arrays.<@Nullable String>asList(
              ENTRY_ID_TEXT, AUDIO_ID_TEXT, ONE, VOICE_TEXT, ONE, STAMP);
      default -> List.of("0");
    };
  }

  private static void workflow(
      MigrationMasterTargetPublisher publisher, Fixture f, MigrationMasterCopyDataset declared)
      throws SQLException {
    var connection = f.connection();
    publisher.prepare(connection);
    publisher.transferAndFinalize(connection, declared);
  }

  private static List<Throwable> failures() {
    return List.of(
        new SQLException("synthetic sql"),
        new IllegalStateException("synthetic runtime"),
        new AssertionError("synthetic error"));
  }

  private static int ordinaryOwnersThrough(int sqlIndex) {
    return (int) OWNER_START.stream().filter(index -> index <= sqlIndex).count();
  }

  private static int scalarSqlIndex(int query) {
    return IntStream.range(0, SQL_COUNT)
        .filter(
            index ->
                SQL.get(index).startsWith("SELECT ")
                    && !CONTENT_SQL.contains(SQL.get(index))
                    && !CATALOG_SQL.contains(SQL.get(index))
                    && !GAMES_SQL.equals(SQL.get(index)))
        .skip(query)
        .findFirst()
        .orElseThrow();
  }

  private static void sqlFailures(int first, int end) throws Exception {
    var declared = normal();
    for (int index = first; index < end; index++)
      for (Throwable failure : failures()) {
        var f = new Fixture();
        f.badSql = index;
        f.failure = failure;
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () -> workflow(new MigrationMasterTargetPublisher(), f, declared)));
        assertEquals(SQL.subList(0, index + 1), f.sql);
        assertEquals(
            (int)
                SQL.subList(0, index).stream().filter(query -> query.startsWith("SELECT ")).count(),
            f.resultCloses);
        assertEquals(
            ordinaryOwnersThrough(index) + Math.max(0, Math.min(5, index - SETVAL_FIRST)),
            f.closeAttempts);
        assertEquals(0, failure.getSuppressed().length);
        if (index < CONTENT_END) {
          assertEquals(0, f.preparedExecutions);
          assertEquals(0, f.analyzes);
        }
      }
  }

  static final class Fixture {
    final List<String> sql = new ArrayList<>();
    private final List<Integer> timeouts = new ArrayList<>();
    private final List<Long> boundLong = new ArrayList<>();
    private final List<Boolean> boundBoolean = new ArrayList<>();
    private long[] scalars = NORMAL_SCALARS.clone();
    private boolean empty;
    boolean autoCommit;
    boolean readOnly;
    boolean failReadOnly;
    @Nullable Throwable attributeFailure;
    private int badGamesRow = -1;
    private int badGamesField = -1;
    private boolean nullGamesValue;
    private boolean failGamesRead;
    private int gamesFieldReads;
    private @Nullable Throwable gamesCloseFailure;
    private int badContentTable = -1;
    private int badCatalogTable = -1;
    private int badCatalogRow = -1;
    private int badCatalogField = -1;
    private int nullCatalogResult = -1;
    private int missingCatalog = -1;
    private int extraCatalog = -1;
    private boolean nullCatalogValue;
    private boolean failCatalogRead;
    private int catalogFieldReads;
    private int badContentColumn = -1;
    private int nullContentResult = -1;
    private int missingContent = -1;
    private int extraContent = -1;
    private boolean nullContentValue;
    private boolean failContentRead;
    private int contentFieldReads;
    private final List<Integer> fetchSizes = new ArrayList<>();
    int badSql = -1;
    private int badScalar = -1;
    private int badRead = -1;
    private int badPreparedExecute = -1;
    private int badWarning = -1;
    private int badClose = -1;
    private int extraResultAt = -1;
    Throwable failure = new SQLException("synthetic primary");
    private Throwable closeFailure = new SQLException("synthetic close");
    private @Nullable Throwable extraResult;
    private int autoReads;
    private int statementCreates;
    private int preparedCreates;
    private int preparedExecutions;
    private boolean badConstraintUpdate;
    private boolean badConstraintWarning;
    private boolean failConstraintWarning;
    private boolean constraintWarningPending;
    private int analyzes;
    private int scalarReads;
    private int resultCloses;
    private int closeAttempts;

    private void recordSql(String actual) throws Throwable {
      int index = sql.size();
      sql.add(actual);
      assertEquals(SQL.get(index), actual);
      if (index == badSql) throw failure;
    }

    private void closeOwned() throws Throwable {
      int index = closeAttempts;
      closeAttempts++;
      if (index == badClose) throw closeFailure;
    }

    Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "getAutoCommit":
                    autoReads++;
                    if (attributeFailure != null && !failReadOnly) throw attributeFailure;
                    return autoCommit;
                  case "isReadOnly":
                    if (attributeFailure != null && failReadOnly) throw attributeFailure;
                    return readOnly;
                  case "createStatement":
                    statementCreates++;
                    return statement();
                  case "prepareStatement":
                    recordSql((String) args[0]);
                    int slot = preparedCreates;
                    preparedCreates++;
                    return prepared(slot);
                  default:
                    throw new AssertionError(
                        "Unexpected borrowed Connection operation: " + method.getName());
                }
              });
    }

    private Statement statement() {
      return (Statement)
          Proxy.newProxyInstance(
              Statement.class.getClassLoader(),
              new Class<?>[] {Statement.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "setQueryTimeout":
                    assertEquals(30, args[0]);
                    timeouts.add((Integer) args[0]);
                    return null;
                  case "executeUpdate":
                    String update = (String) args[0];
                    int operation = sql.size();
                    assertTrue(
                        operation < PREPARE_END
                            || operation == CONTENT_END
                            || List.of(27, 28).contains(operation)
                            || operation >= ANALYZE_FIRST);
                    recordSql(update);
                    if (FLUSH_SQL.equals(update)) {
                      constraintWarningPending = true;
                      return badConstraintUpdate ? 1 : 0;
                    }
                    if (update.startsWith("ANALYZE ")) analyzes++;
                    return update.startsWith("INSERT INTO ") ? (empty ? 0 : 1) : 0;
                  case "executeLargeUpdate":
                    assertTrue(List.of(21, 37, 38, 39).contains(sql.size()));
                    recordSql((String) args[0]);
                    return empty ? 0L : 1L;
                  case "setFetchSize":
                    assertEquals(1000, args[0]);
                    fetchSizes.add((Integer) args[0]);
                    return null;
                  case "executeQuery":
                    String query = (String) args[0];
                    recordSql(query);
                    if (GAMES_SQL.equals(query)) return gamesResult();
                    int catalogTable = CATALOG_SQL.indexOf(query);
                    if (catalogTable >= 0)
                      return catalogTable == nullCatalogResult ? null : catalogResult(catalogTable);
                    int contentTable = CONTENT_SQL.indexOf(query);
                    if (contentTable >= 0)
                      return contentTable == nullContentResult ? null : contentResult(contentTable);
                    return result();
                  case "getWarnings":
                    if (constraintWarningPending) {
                      constraintWarningPending = false;
                      if (failConstraintWarning) throw failure;
                      return badConstraintWarning
                          ? new SQLWarning("synthetic deferred constraint")
                          : null;
                    }
                    return badWarning == analyzes - 1
                        ? new SQLWarning("synthetic skipped analyze")
                        : null;
                  case CLOSE_METHOD:
                    closeOwned();
                    return null;
                  default:
                    throw new AssertionError("Unexpected Statement operation: " + method.getName());
                }
              });
    }

    private PreparedStatement prepared(int slot) {
      return (PreparedStatement)
          Proxy.newProxyInstance(
              PreparedStatement.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "setQueryTimeout":
                    assertEquals(30, args[0]);
                    timeouts.add((Integer) args[0]);
                    return null;
                  case "setLong":
                    assertEquals(1, args[0]);
                    boundLong.add((Long) args[1]);
                    return null;
                  case "setBoolean":
                    assertEquals(2, args[0]);
                    boundBoolean.add((Boolean) args[1]);
                    return null;
                  case "executeQuery":
                    preparedExecutions++;
                    if (slot == badPreparedExecute) throw failure;
                    return result();
                  case CLOSE_METHOD:
                    closeOwned();
                    return null;
                  default:
                    throw new AssertionError(
                        "Unexpected PreparedStatement operation: " + method.getName());
                }
              });
    }

    private ResultSet gamesResult() {
      int[] position = {-1};
      boolean[] wasNull = {false};
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.equals(NEXT_METHOD)) {
                  position[0]++;
                  return position[0] < GAMES_ROWS.size();
                }
                if (name.equals(WAS_NULL_METHOD)) return wasNull[0];
                if (name.equals(CLOSE_METHOD)) {
                  resultCloses++;
                  if (gamesCloseFailure != null) throw gamesCloseFailure;
                  return null;
                }
                if (List.of(GET_INT, GET_STRING, GET_TIMESTAMP).contains(name)) {
                  int field = (Integer) args[0] - 1;
                  assertEquals(
                      field == 0 || field == GAME_ORDER_FIELD
                          ? GET_INT
                          : field == GAME_TIME_FIELD ? GET_TIMESTAMP : GET_STRING,
                      name);
                  gamesFieldReads++;
                  boolean bad = position[0] == badGamesRow && field == badGamesField;
                  if (bad && failGamesRead) throw failure;
                  @Nullable String value = GAMES_ROWS.get(position[0]).get(field);
                  if (bad)
                    value =
                        nullGamesValue
                            ? null
                            : field == 0 || field == GAME_ORDER_FIELD
                                ? Integer.toString(Integer.parseInt(value) + 1)
                                : field == GAME_TIME_FIELD
                                    ? Instant.parse(value).plusSeconds(1).toString()
                                    : value + "X";
                  wasNull[0] = value == null;
                  return switch (name) {
                    case GET_INT -> value == null ? 0 : Integer.parseInt(value);
                    case GET_TIMESTAMP ->
                        value == null ? null : Timestamp.from(Instant.parse(value));
                    default -> value;
                  };
                }
                throw new AssertionError("Unexpected games ResultSet operation " + name);
              });
    }

    private ResultSet catalogResult(int table) {
      int[] position = {-1};
      boolean[] wasNull = {false};
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.equals(NEXT_METHOD)) {
                  position[0]++;
                  int count =
                      CATALOG_ROWS.get(table).size()
                          + (table == extraCatalog ? 1 : 0)
                          - (table == missingCatalog ? 1 : 0);
                  return position[0] < count;
                }
                if (name.equals(WAS_NULL_METHOD)) return wasNull[0];
                if (name.equals(CLOSE_METHOD)) {
                  resultCloses++;
                  if (table == badCatalogTable && extraResult != null) throw extraResult;
                  return null;
                }
                if (List.of(GET_INT, GET_BOOLEAN, GET_STRING).contains(name)) {
                  int field = (Integer) args[0] - 1;
                  assertEquals(
                      field == 0
                          ? GET_INT
                          : (field == 4 || field == 7 || field == 8 || field == DEFAULT_FIELD)
                              ? GET_BOOLEAN
                              : GET_STRING,
                      name);
                  catalogFieldReads++;
                  boolean bad =
                      table == badCatalogTable
                          && position[0] == badCatalogRow
                          && field == badCatalogField;
                  if (bad && failCatalogRead) throw failure;
                  String value = CATALOG_ROWS.get(table).get(position[0]).split("\t", -1)[field];
                  if (bad)
                    value =
                        nullCatalogValue
                            ? null
                            : field == 0
                                ? Integer.toString(Integer.parseInt(value) + 1)
                                : field == 4
                                    ? Boolean.toString(!Boolean.parseBoolean(value))
                                    : value + "X";
                  wasNull[0] = value == null;
                  return switch (name) {
                    case GET_INT -> value == null ? 0 : Integer.parseInt(value);
                    case GET_BOOLEAN -> value != null && Boolean.parseBoolean(value);
                    default -> value;
                  };
                }
                throw new AssertionError("Unexpected catalog ResultSet operation " + name);
              });
    }

    private ResultSet contentResult(int table) {
      int[] position = {-1};
      boolean[] wasNull = {false};
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.equals(NEXT_METHOD)) {
                  position[0]++;
                  if ((empty && table < 6) || table == missingContent) return false;
                  return position[0] == 0 || table == extraContent && position[0] == 1;
                }
                if (name.equals(WAS_NULL_METHOD)) return wasNull[0];
                if (name.equals(CLOSE_METHOD)) {
                  resultCloses++;
                  if (table == badContentTable && extraResult != null) throw extraResult;
                  return null;
                }
                if (List.of(GET_LONG, GET_INT, GET_BOOLEAN, GET_TIMESTAMP, GET_STRING)
                    .contains(name)) {
                  int column = (Integer) args[0] - 1;
                  assertEquals(contentGetter(CONTENT_TYPES.get(table).charAt(column)), name);
                  contentFieldReads++;
                  boolean bad = table == badContentTable && column == badContentColumn;
                  if (bad && failContentRead) throw failure;
                  String value = contentLiteral(table).get(column);
                  if (bad)
                    value =
                        nullContentValue
                            ? null
                            : changedContent(value, CONTENT_TYPES.get(table).charAt(column));
                  wasNull[0] = value == null;
                  return switch (name) {
                    case GET_LONG -> value == null ? 0L : Long.parseLong(value);
                    case GET_INT -> value == null ? 0 : Integer.parseInt(value);
                    case GET_BOOLEAN -> value != null && Boolean.parseBoolean(value);
                    case GET_TIMESTAMP ->
                        value == null ? null : Timestamp.from(Instant.parse(value));
                    default -> value;
                  };
                }
                throw new AssertionError("Unexpected content ResultSet operation " + name);
              });
    }

    private ResultSet result() {
      int query = scalarReads;
      scalarReads++;
      int[] nextCalls = {0};
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case NEXT_METHOD:
                    int call = nextCalls[0];
                    nextCalls[0]++;
                    return call == 0;
                  case "getLong":
                    assertEquals(1, args[0]);
                    if (query == badRead) throw failure;
                    return scalars[query] + (query == badScalar ? 1 : 0);
                  case WAS_NULL_METHOD:
                    return false;
                  case CLOSE_METHOD:
                    resultCloses++;
                    if (query == extraResultAt && extraResult != null) throw extraResult;
                    return null;
                  default:
                    throw new AssertionError("Unexpected ResultSet operation: " + method.getName());
                }
              });
    }
  }

  static Fixture coordinatorFixture(boolean empty) {
    var f = new Fixture();
    if (empty) {
      f.empty = true;
      f.scalars = new long[SCALARS];
      Arrays.fill(f.scalars, SETVAL_SCALAR_FIRST, SCALARS, 1L);
    }
    return f;
  }

  static MigrationMasterCopyDataset normal() throws Exception {
    return new MigrationMasterCopyDataset(speakers(STAMP), content(STAMP));
  }

  private static MigrationCopyDataset content(String stamp) throws Exception {
    return new MigrationCopyDataset(
        scenario(true, SPEAKER_ID, ONE, stamp),
        List.of(audio(stamp)),
        List.of(
            Arrays.<@Nullable String>asList(
                ENTRY_ID_TEXT, AUDIO_ID_TEXT, ONE, VOICE_TEXT, ONE, stamp)),
        media(stamp));
  }

  private static MigrationCopyDataset emptyContent() {
    return new MigrationCopyDataset(emptyScenario(), List.of(), List.of(), emptyMedia());
  }

  private static SpeakerCopyBatch speakers(String stamp) {
    return new SpeakerCopyBatch(
        List.of(
            new SpeakerCopyRow(
                Arrays.<@Nullable String>asList(
                    SPEAKER_ID, ONE, "Alice", "alice", TRUE_TEXT, null, stamp))));
  }

  private static ScenarioCopyDataset scenario(
      boolean withEntry, @Nullable String speaker, String game, String stamp) {
    var files =
        new ScenarioFileMigrationMap(
            List.of(new ScenarioFileMigrationMap.FilePair(Integer.parseInt(game), 10, 700)));
    var entries =
        new ScenarioEntryMigrationMap(
            withEntry ? List.of(new ScenarioEntryMigrationMap.IdPair(20, 900)) : List.of());
    var placement =
        new ScenarioEntryPlacementMap(
            files,
            entries,
            withEntry
                ? List.of(
                    new ScenarioEntryPlacementMap.Placement(Integer.parseInt(game), 10, 20, 0))
                : List.of());
    var fileRows =
        new ScenarioFileCopyBatch(
            files,
            List.of(
                Arrays.<@Nullable String>asList(
                    FILE_ID_TEXT,
                    game,
                    ONE,
                    "script/file.txt",
                    FILE_NAME_TEXT,
                    FILE_NAME_TEXT,
                    null,
                    "chapter",
                    SHA,
                    THREE,
                    stamp)));
    var entryRows =
        withEntry
            ? List.of(
                new ScenarioEntryCopyRow(
                    Arrays.<@Nullable String>asList(
                        ENTRY_ID_TEXT,
                        game,
                        FILE_ID_TEXT,
                        ONE,
                        "0",
                        null,
                        speaker == null ? "narration" : "dialogue",
                        speaker,
                        null,
                        "hello",
                        "raw",
                        stamp)))
            : List.<ScenarioEntryCopyRow>of();
    return new ScenarioCopyDataset(fileRows, new ScenarioEntryCopyBatch(placement, entryRows));
  }

  private static ScenarioCopyDataset emptyScenario() {
    var files = new ScenarioFileMigrationMap(List.of());
    var entries = new ScenarioEntryMigrationMap(List.of());
    return new ScenarioCopyDataset(
        new ScenarioFileCopyBatch(files, List.of()),
        new ScenarioEntryCopyBatch(
            new ScenarioEntryPlacementMap(files, entries, List.of()), List.of()));
  }

  private static AudioFileCopyRow audio(String stamp) {
    return new AudioFileCopyRow(
        Arrays.<@Nullable String>asList(
            AUDIO_ID_TEXT,
            ONE,
            "voice/a.ogg",
            "表示",
            "a.ogg",
            "a",
            VOICE_TEXT,
            "ogg",
            "1200",
            THREE,
            SHA,
            stamp));
  }

  private static MediaAssetCopyBatch media(String stamp) throws Exception {
    var manifest =
        new AssetMigrationManifest(
            List.of(
                new AssetMigrationManifest.Entry(
                    AssetMigrationManifest.Kind.VIDEO, SOURCE_VIDEO, TARGET_VIDEO, 3, SHA)));
    var row =
        new MediaAssetCopyRow(
            Arrays.<@Nullable String>asList(
                "600",
                "video-a",
                VIDEO,
                "A",
                "MAIN",
                null,
                TARGET_VIDEO,
                SOURCE_VIDEO,
                "a.mp4",
                THREE,
                SHA,
                "video/mp4",
                null,
                null,
                null,
                ONE,
                stamp));
    return new MediaAssetCopyBatch(manifest, List.of(row));
  }

  private static MediaAssetCopyBatch emptyMedia() {
    return new MediaAssetCopyBatch(new AssetMigrationManifest(List.of()), List.of());
  }
}

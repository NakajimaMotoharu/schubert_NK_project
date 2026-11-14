package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-COLUMN001..026; independent V002 column matrix and JDBC resource-event oracle. */
final class MigrationMasterColumnVerifierTest {
  private static final String FIXTURE_LITERAL_1 =
      "1\tid\tint8\tbigint\ttrue\td\t\ttrue\ttrue\tnk_owner\ttrue";
  private static final String FIXTURE_LITERAL_2 =
      "2\tgame_id\tint2\tsmallint\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue";
  private static final int TABLES = 6;
  private static final int COLUMNS = 66;
  private static final int FIELDS = 11;
  private static final int DEFAULT_FIELD = 10;
  private static final int OWNER_FIELD = 9;
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;
  private static final String SQL_FALSE = "false";
  private static final String DIAGNOSTIC = "migration column attributes are invalid";
  private static final String GET_INT = "getInt";
  private static final String GET_BOOLEAN = "getBoolean";
  private static final String GET_STRING = "getString";
  private static final String AUTO = "auto";
  private static final String CREATE = "create";
  private static final String TIMEOUT = "timeout";
  private static final String FETCH = "fetch";
  private static final String STATEMENT_CLOSE = "statement.close";
  private static final String QUERY = ":query";
  private static final String NEXT = ":next";
  private static final String WAS_NULL = ":wasNull";
  private static final String CLOSE = ":close";
  private static final List<String> SQL =
      List.of(
          "SELECT a.attnum,a.attname,t.typname,pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity::text,a.attgenerated::text,CASE WHEN a.attnotnull THEN EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS TRUE) AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS NOT TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum]) END,CASE WHEN a.attidentity='d' THEN (SELECT count(*) FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a'))=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid LEFT JOIN pg_catalog.pg_sequence sq ON sq.seqrelid=sc.oid LEFT JOIN pg_catalog.pg_type st ON st.oid=sq.seqtypid LEFT JOIN pg_catalog.pg_namespace stn ON stn.oid=st.typnamespace WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a') AND (dep.deptype='i' AND sc.relnamespace=c.relnamespace AND sc.relowner=c.relowner AND sc.relpersistence='p' AND stn.nspname='pg_catalog' AND st.typname='int8' AND sq.seqstart=1 AND sq.seqincrement=1 AND sq.seqmin=1 AND sq.seqmax=999999999999 AND sq.seqcache=1 AND NOT sq.seqcycle) IS TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a')) END,pg_catalog.pg_get_userbyid(c.relowner),CASE WHEN (c.relname='speakers' AND a.attname='is_protagonist') OR (c.relname='script_entries' AND a.attname='body_search') THEN a.atthasdef AND (SELECT count(*) FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum)=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum AND pg_catalog.pg_get_expr(ad.adbin,ad.adrelid,false)=CASE WHEN c.relname='speakers' THEN 'false' ELSE 'lower(body)' END) ELSE NOT a.atthasdef AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum) END FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid JOIN pg_catalog.pg_type t ON t.oid=a.atttypid JOIN pg_catalog.pg_namespace tn ON tn.oid=t.typnamespace WHERE n.nspname='schubert' AND c.relname='speakers' AND c.relkind='r' AND c.relpersistence='p' AND tn.nspname='pg_catalog' AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum",
          "SELECT a.attnum,a.attname,t.typname,pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity::text,a.attgenerated::text,CASE WHEN a.attnotnull THEN EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS TRUE) AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS NOT TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum]) END,CASE WHEN a.attidentity='d' THEN (SELECT count(*) FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a'))=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid LEFT JOIN pg_catalog.pg_sequence sq ON sq.seqrelid=sc.oid LEFT JOIN pg_catalog.pg_type st ON st.oid=sq.seqtypid LEFT JOIN pg_catalog.pg_namespace stn ON stn.oid=st.typnamespace WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a') AND (dep.deptype='i' AND sc.relnamespace=c.relnamespace AND sc.relowner=c.relowner AND sc.relpersistence='p' AND stn.nspname='pg_catalog' AND st.typname='int8' AND sq.seqstart=1 AND sq.seqincrement=1 AND sq.seqmin=1 AND sq.seqmax=999999999999 AND sq.seqcache=1 AND NOT sq.seqcycle) IS TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a')) END,pg_catalog.pg_get_userbyid(c.relowner),CASE WHEN (c.relname='speakers' AND a.attname='is_protagonist') OR (c.relname='script_entries' AND a.attname='body_search') THEN a.atthasdef AND (SELECT count(*) FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum)=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum AND pg_catalog.pg_get_expr(ad.adbin,ad.adrelid,false)=CASE WHEN c.relname='speakers' THEN 'false' ELSE 'lower(body)' END) ELSE NOT a.atthasdef AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum) END FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid JOIN pg_catalog.pg_type t ON t.oid=a.atttypid JOIN pg_catalog.pg_namespace tn ON tn.oid=t.typnamespace WHERE n.nspname='schubert' AND c.relname='script_files' AND c.relkind='r' AND c.relpersistence='p' AND tn.nspname='pg_catalog' AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum",
          "SELECT a.attnum,a.attname,t.typname,pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity::text,a.attgenerated::text,CASE WHEN a.attnotnull THEN EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS TRUE) AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS NOT TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum]) END,CASE WHEN a.attidentity='d' THEN (SELECT count(*) FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a'))=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid LEFT JOIN pg_catalog.pg_sequence sq ON sq.seqrelid=sc.oid LEFT JOIN pg_catalog.pg_type st ON st.oid=sq.seqtypid LEFT JOIN pg_catalog.pg_namespace stn ON stn.oid=st.typnamespace WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a') AND (dep.deptype='i' AND sc.relnamespace=c.relnamespace AND sc.relowner=c.relowner AND sc.relpersistence='p' AND stn.nspname='pg_catalog' AND st.typname='int8' AND sq.seqstart=1 AND sq.seqincrement=1 AND sq.seqmin=1 AND sq.seqmax=999999999999 AND sq.seqcache=1 AND NOT sq.seqcycle) IS TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a')) END,pg_catalog.pg_get_userbyid(c.relowner),CASE WHEN (c.relname='speakers' AND a.attname='is_protagonist') OR (c.relname='script_entries' AND a.attname='body_search') THEN a.atthasdef AND (SELECT count(*) FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum)=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum AND pg_catalog.pg_get_expr(ad.adbin,ad.adrelid,false)=CASE WHEN c.relname='speakers' THEN 'false' ELSE 'lower(body)' END) ELSE NOT a.atthasdef AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum) END FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid JOIN pg_catalog.pg_type t ON t.oid=a.atttypid JOIN pg_catalog.pg_namespace tn ON tn.oid=t.typnamespace WHERE n.nspname='schubert' AND c.relname='script_entries' AND c.relkind='r' AND c.relpersistence='p' AND tn.nspname='pg_catalog' AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum",
          "SELECT a.attnum,a.attname,t.typname,pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity::text,a.attgenerated::text,CASE WHEN a.attnotnull THEN EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS TRUE) AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS NOT TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum]) END,CASE WHEN a.attidentity='d' THEN (SELECT count(*) FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a'))=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid LEFT JOIN pg_catalog.pg_sequence sq ON sq.seqrelid=sc.oid LEFT JOIN pg_catalog.pg_type st ON st.oid=sq.seqtypid LEFT JOIN pg_catalog.pg_namespace stn ON stn.oid=st.typnamespace WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a') AND (dep.deptype='i' AND sc.relnamespace=c.relnamespace AND sc.relowner=c.relowner AND sc.relpersistence='p' AND stn.nspname='pg_catalog' AND st.typname='int8' AND sq.seqstart=1 AND sq.seqincrement=1 AND sq.seqmin=1 AND sq.seqmax=999999999999 AND sq.seqcache=1 AND NOT sq.seqcycle) IS TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a')) END,pg_catalog.pg_get_userbyid(c.relowner),CASE WHEN (c.relname='speakers' AND a.attname='is_protagonist') OR (c.relname='script_entries' AND a.attname='body_search') THEN a.atthasdef AND (SELECT count(*) FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum)=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum AND pg_catalog.pg_get_expr(ad.adbin,ad.adrelid,false)=CASE WHEN c.relname='speakers' THEN 'false' ELSE 'lower(body)' END) ELSE NOT a.atthasdef AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum) END FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid JOIN pg_catalog.pg_type t ON t.oid=a.atttypid JOIN pg_catalog.pg_namespace tn ON tn.oid=t.typnamespace WHERE n.nspname='schubert' AND c.relname='audio_files' AND c.relkind='r' AND c.relpersistence='p' AND tn.nspname='pg_catalog' AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum",
          "SELECT a.attnum,a.attname,t.typname,pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity::text,a.attgenerated::text,CASE WHEN a.attnotnull THEN EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS TRUE) AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS NOT TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum]) END,CASE WHEN a.attidentity='d' THEN (SELECT count(*) FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a'))=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid LEFT JOIN pg_catalog.pg_sequence sq ON sq.seqrelid=sc.oid LEFT JOIN pg_catalog.pg_type st ON st.oid=sq.seqtypid LEFT JOIN pg_catalog.pg_namespace stn ON stn.oid=st.typnamespace WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a') AND (dep.deptype='i' AND sc.relnamespace=c.relnamespace AND sc.relowner=c.relowner AND sc.relpersistence='p' AND stn.nspname='pg_catalog' AND st.typname='int8' AND sq.seqstart=1 AND sq.seqincrement=1 AND sq.seqmin=1 AND sq.seqmax=999999999999 AND sq.seqcache=1 AND NOT sq.seqcycle) IS TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a')) END,pg_catalog.pg_get_userbyid(c.relowner),CASE WHEN (c.relname='speakers' AND a.attname='is_protagonist') OR (c.relname='script_entries' AND a.attname='body_search') THEN a.atthasdef AND (SELECT count(*) FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum)=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum AND pg_catalog.pg_get_expr(ad.adbin,ad.adrelid,false)=CASE WHEN c.relname='speakers' THEN 'false' ELSE 'lower(body)' END) ELSE NOT a.atthasdef AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum) END FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid JOIN pg_catalog.pg_type t ON t.oid=a.atttypid JOIN pg_catalog.pg_namespace tn ON tn.oid=t.typnamespace WHERE n.nspname='schubert' AND c.relname='media_assets' AND c.relkind='r' AND c.relpersistence='p' AND tn.nspname='pg_catalog' AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum",
          "SELECT a.attnum,a.attname,t.typname,pg_catalog.format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity::text,a.attgenerated::text,CASE WHEN a.attnotnull THEN EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS TRUE) AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum] AND (nn.connamespace=c.relnamespace AND nn.conenforced AND nn.convalidated AND NOT nn.condeferrable AND NOT nn.condeferred AND nn.conislocal AND nn.coninhcount=0 AND nn.conparentid=0 AND nn.contypid=0) IS NOT TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_constraint nn WHERE nn.conrelid=c.oid AND nn.contype='n' AND nn.conkey=ARRAY[a.attnum]) END,CASE WHEN a.attidentity='d' THEN (SELECT count(*) FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a'))=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid LEFT JOIN pg_catalog.pg_sequence sq ON sq.seqrelid=sc.oid LEFT JOIN pg_catalog.pg_type st ON st.oid=sq.seqtypid LEFT JOIN pg_catalog.pg_namespace stn ON stn.oid=st.typnamespace WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a') AND (dep.deptype='i' AND sc.relnamespace=c.relnamespace AND sc.relowner=c.relowner AND sc.relpersistence='p' AND stn.nspname='pg_catalog' AND st.typname='int8' AND sq.seqstart=1 AND sq.seqincrement=1 AND sq.seqmin=1 AND sq.seqmax=999999999999 AND sq.seqcache=1 AND NOT sq.seqcycle) IS TRUE) ELSE NOT EXISTS (SELECT 1 FROM pg_catalog.pg_depend dep JOIN pg_catalog.pg_class sc ON sc.oid=dep.objid WHERE dep.classid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.objsubid=0 AND dep.refclassid='pg_catalog.pg_class'::pg_catalog.regclass AND dep.refobjid=c.oid AND dep.refobjsubid=a.attnum AND sc.relkind='S' AND dep.deptype IN ('i','a')) END,pg_catalog.pg_get_userbyid(c.relowner),CASE WHEN (c.relname='speakers' AND a.attname='is_protagonist') OR (c.relname='script_entries' AND a.attname='body_search') THEN a.atthasdef AND (SELECT count(*) FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum)=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum AND pg_catalog.pg_get_expr(ad.adbin,ad.adrelid,false)=CASE WHEN c.relname='speakers' THEN 'false' ELSE 'lower(body)' END) ELSE NOT a.atthasdef AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum) END FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_attribute a ON a.attrelid=c.oid JOIN pg_catalog.pg_type t ON t.oid=a.atttypid JOIN pg_catalog.pg_namespace tn ON tn.oid=t.typnamespace WHERE n.nspname='schubert' AND c.relname='entry_audio_links' AND c.relkind='r' AND c.relpersistence='p' AND tn.nspname='pg_catalog' AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum");
  private static final List<List<String>> DATA =
      List.of(
          List.of(
              FIXTURE_LITERAL_1,
              FIXTURE_LITERAL_2,
              "3\tname\ttext\ttext\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "4\tnormalized_name\ttext\ttext\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "5\tis_protagonist\tbool\tboolean\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "6\tnotes\ttext\ttext\tfalse\t\t\ttrue\ttrue\tnk_owner\ttrue",
              "7\tcreated_at\ttimestamptz\ttimestamp with time zone\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue"),
          List.of(
              FIXTURE_LITERAL_1,
              FIXTURE_LITERAL_2,
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
              FIXTURE_LITERAL_1,
              FIXTURE_LITERAL_2,
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
              FIXTURE_LITERAL_1,
              FIXTURE_LITERAL_2,
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
              FIXTURE_LITERAL_1,
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
              "6\tcreated_at\ttimestamptz\ttimestamp with time zone\ttrue\t\t\ttrue\ttrue\tnk_owner\ttrue"));

  @Test
  void column001SixQueriesSixtySixColumnsAndExactResources() throws Exception {
    var f = new Fixture();
    verify(f);
    assertEquals(SQL, f.sql);
    assertEquals(List.of(7, 11, 13, 12, 17, 6), f.rows.stream().map(List::size).toList());
    assertEquals(COLUMNS, f.rows.stream().mapToInt(List::size).sum());
    assertEquals(COLUMNS * FIELDS, f.calls.stream().filter(c -> c.contains(":get")).count());
    assertEquals(List.of(30), f.timeouts);
    assertEquals(List.of(1000), f.fetchSizes);
    assertEquals(List.of(TABLES, 1), List.of(f.resultCloses, f.statementCloses));
    assertEquals(expectedCalls(), f.calls);
  }

  @Test
  void column002NullConnectionFailsBeforeIo() {
    var failure =
        assertThrows(
            IllegalArgumentException.class, () -> new MigrationMasterColumnVerifier().verify(null));
    assertEquals("migration column input is invalid", failure.getMessage());
    assertNull(failure.getCause());
  }

  @Test
  void column003AutoCommitIsNotChangedOrUsed() {
    var f = new Fixture();
    f.auto = true;
    reject(f);
    assertEquals(List.of(AUTO), f.calls);
  }

  @Test
  void column004NullVendorStatementHasNoOwnedHandle() {
    var f = new Fixture();
    f.nullStatement = true;
    reject(f);
    assertEquals(List.of(AUTO, CREATE), f.calls);
    assertEquals(0, f.statementCloses);
  }

  @Test
  void column005EachNullResultClosesOnlyPreviousResults() {
    for (int table = 0; table < TABLES; table++) {
      var f = new Fixture();
      f.nullResult = table;
      reject(f);
      assertEquals(table, f.resultCloses);
      assertEquals(1, f.statementCloses);
      assertEquals(SQL.subList(0, table + 1), f.sql);
    }
  }

  @Test
  void column006AnyMissingPhysicalColumnIsRejected() {
    for (int table = 0; table < TABLES; table++) {
      for (int column = 0; column < DATA.get(table).size(); column++) {
        var f = new Fixture();
        f.rows.get(table).remove(column);
        reject(f);
        assertEquals(SQL.subList(0, table + 1), f.sql);
        assertEquals(table + 1, f.resultCloses);
      }
    }
  }

  @Test
  void column007ExtraMetadataRowsAreNotReadAsAnotherColumn() {
    for (int table = 0; table < TABLES; table++) {
      var f = new Fixture();
      f.rows.get(table).add(new ArrayList<>(f.rows.get(table).getFirst()));
      reject(f);
      assertEquals(
          DATA.get(table).size(),
          f.calls.stream().filter(c -> c.equals(key(f.lastQuery()) + ":getInt:1")).count());
      assertEquals(table + 1, f.resultCloses);
    }
  }

  @Test
  void column008NullZeroNegativeDuplicateAndWrongOrdinalsFail() {
    for (int table = 0; table < TABLES; table++) {
      for (String value : java.util.Arrays.asList(null, "0", "-1", "2147483647", "2")) {
        var f = new Fixture();
        f.rows.get(table).getFirst().set(0, value);
        reject(f);
        assertEquals(table + 1, f.resultCloses);
      }
      var duplicate = new Fixture();
      duplicate.rows.get(table).get(1).set(0, "1");
      reject(duplicate);
    }
  }

  @Test
  void column009EveryColumnAttributeMismatchIsDetected() {
    for (int table = 0; table < TABLES; table++) {
      for (int row = 0; row < DATA.get(table).size(); row++) {
        for (int field = 1; field < FIELDS; field++) {
          var f = new Fixture();
          String old = f.rows.get(table).get(row).get(field);
          f.rows
              .get(table)
              .get(row)
              .set(
                  field,
                  (field == 4 || field == 7 || field == 8 || field == DEFAULT_FIELD)
                      ? Boolean.toString(!Boolean.parseBoolean(old))
                      : old + "X");
          reject(f);
          assertEquals(table + 1, f.resultCloses);
          assertEquals(1, f.statementCloses);
        }
      }
    }
  }

  @Test
  void column010AllStringMetadataSqlNullsDifferFromEmptyFlags() {
    for (int table = 0; table < TABLES; table++) {
      for (int row = 0; row < DATA.get(table).size(); row++) {
        for (int field : List.of(1, 2, 3, 5, 6, OWNER_FIELD)) {
          var f = new Fixture();
          f.rows.get(table).get(row).set(field, null);
          reject(f);
          assertEquals(table + 1, f.resultCloses);
        }
      }
    }
  }

  @Test
  void column011SqlNullBooleanCannotMasqueradeAsFalse() throws Exception {
    for (int table = 0; table < TABLES; table++) {
      for (int row = 0; row < DATA.get(table).size(); row++) {
        var f = new Fixture();
        f.rows.get(table).get(row).set(4, null);
        reject(f);
      }
    }
    var normal = new Fixture();
    verify(normal);
    assertEquals(SQL_FALSE, normal.rows.get(2).get(10).get(4));
  }

  @Test
  void column012NotNullFlagsAreCheckedIndividuallyIncludingImplicitPk() {
    for (int table = 0; table < TABLES; table++) {
      for (int row = 0; row < DATA.get(table).size(); row++) {
        var f = new Fixture();
        var value = f.rows.get(table).get(row);
        value.set(4, Boolean.toString(!Boolean.parseBoolean(value.get(4))));
        reject(f);
      }
    }
  }

  @Test
  void column013IdentityAlwaysDefaultMissingAndUnknownAreDistinct() {
    flagAlternatives(5, List.of("", "d", "a", "unknown"));
  }

  @Test
  void column014StoredVirtualMissingAndUnknownGenerationAreDistinct() {
    flagAlternatives(6, List.of("", "s", "v", "unknown"));
  }

  @Test
  void column015BuiltinWidthsAndNamespaceTablekindPredicatesAreFixed() {
    for (String query : SQL) {
      assertTrue(query.contains("tn.nspname='pg_catalog'"));
      assertTrue(query.contains("c.relkind='r'"));
      assertTrue(query.contains("c.relpersistence='p'"));
      assertTrue(query.contains("a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum"));
    }
    var varchar = new Fixture();
    varchar.rows.get(1).get(6).set(3, "character varying(63)");
    reject(varchar);
    var character = new Fixture();
    character.rows.get(4).get(14).set(3, "character(2)");
    reject(character);
    var domain = new Fixture();
    domain.rows.getFirst().getFirst().set(2, "custom_int8");
    reject(domain);
  }

  @Test
  void column016EveryJdbcEventSqlRuntimeAndErrorKeepsOwnership() throws Exception {
    var calls = expectedCalls();
    for (int index = 0; index < calls.size(); index++) {
      for (Throwable primary : failures()) {
        var f = new Fixture();
        f.failAt = index;
        f.failure = primary;
        assertFailure(f, primary, List.of());
        var expected = new ArrayList<>(calls.subList(0, index + 1));
        int active = -1;
        for (int event = 0; event <= index; event++) {
          String call = calls.get(event);
          if (call.endsWith(QUERY) && event != index)
            active = Integer.parseInt(call.substring(1, 2));
          if (call.endsWith(CLOSE)) active = -1;
        }
        if (active >= 0) expected.add(key(active) + CLOSE);
        if (index > 1 && !calls.get(index).equals(STATEMENT_CLOSE)) expected.add(STATEMENT_CLOSE);
        assertEquals(expected, f.calls);
        assertEquals(index > 1 ? 1 : 0, f.statementCloses);
        assertEquals(expected.stream().filter(c -> c.endsWith(CLOSE)).count(), f.resultCloses);
      }
    }
  }

  @Test
  void column017EveryResultCloseFailureStopsLaterQueries() throws Exception {
    for (int table = 0; table < TABLES; table++) {
      for (Throwable primary : failures()) {
        var f = new Fixture();
        f.resultFailureTable = table;
        f.resultFailure = primary;
        assertFailure(f, primary, List.of());
        assertEquals(SQL.subList(0, table + 1), f.sql);
        assertEquals(table + 1, f.resultCloses);
      }
    }
  }

  @Test
  void column018StatementCloseFailureCannotBecomeSuccess() throws Exception {
    for (Throwable primary : failures()) {
      var f = new Fixture();
      f.statementFailure = primary;
      assertFailure(f, primary, List.of());
      assertEquals(TABLES, f.resultCloses);
      assertEquals(1, f.statementCloses);
    }
  }

  @Test
  void column019AllFaultKindsPreserveResultThenStatementSuppression() throws Exception {
    for (int p = 0; p < 3; p++) {
      for (int rc = 0; rc < 3; rc++) {
        for (int sc = 0; sc < 3; sc++) {
          Throwable primary = failures().get(p);
          Throwable inner = failures().get(rc);
          Throwable outer = failures().get(sc);
          var f = readFailure(primary);
          f.resultFailureTable = 0;
          f.resultFailure = inner;
          f.statementFailure = outer;
          assertFailure(f, primary, List.of(inner, outer));
          assertEquals(List.of(1, 1), List.of(f.resultCloses, f.statementCloses));
        }
      }
    }
  }

  @Test
  void column020SamePrimaryAndEqualValuedDistinctCleanupIdentities() throws Exception {
    for (boolean closeOrigin : List.of(true, false)) {
      for (Throwable primary : failures()) {
        var f = closeOrigin ? new Fixture() : readFailure(primary);
        f.resultFailureTable = 0;
        f.resultFailure = primary;
        f.statementFailure = primary;
        assertFailure(f, primary, List.of());
      }
    }
    var primary = new EqualFailure();
    var cleanup = new EqualFailure();
    assertTrue(primary.equals(cleanup));
    var f = readFailure(primary);
    f.resultFailureTable = 0;
    f.resultFailure = cleanup;
    f.statementFailure = cleanup;
    assertFailure(f, primary, List.of(cleanup, cleanup));
  }

  @Test
  void column021RedactionFreshSuccessAndBorrowedConnectionContract() throws Exception {
    var verifier = new MigrationMasterColumnVerifier();
    var bad = new Fixture();
    bad.nullStatement = true;
    var failure = assertThrows(SQLException.class, () -> verifier.verify(bad.connection()));
    assertEquals(DIAGNOSTIC, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    var good = new Fixture();
    verifier.verify(good.connection());
    assertEquals(SQL, good.sql);
    assertEquals(List.of(AUTO, CREATE), good.connectionCalls);
    assertEquals("MigrationMasterColumnVerifier[REDACTED]", verifier.toString());
  }

  @Test
  void column022FiniteSharedVerifierHasOnlyPerCallOwnedResources() throws Exception {
    var verifier = new MigrationMasterColumnVerifier();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<Integer>>();
      for (int index = 0; index < TASKS; index++) {
        futures.add(
            executor.submit(
                () -> {
                  var f = new Fixture();
                  verifier.verify(f.connection());
                  assertEquals(SQL, f.sql);
                  assertEquals(1, f.statementCloses);
                  return f.resultCloses;
                }));
      }
      for (var future : futures) assertEquals(TABLES, future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  @Test
  void column023NotNullCatalogValidityFalseOrSqlNullNeverPassesAnyColumn() throws Exception {
    for (int table = 0; table < TABLES; table++) {
      for (int row = 0; row < DATA.get(table).size(); row++) {
        for (String status : java.util.Arrays.asList(SQL_FALSE, null)) {
          var f = new Fixture();
          f.rows.get(table).get(row).set(7, status);
          reject(f);
          assertEquals(SQL.subList(0, table + 1), f.sql);
          assertEquals(table + 1, f.resultCloses);
          assertEquals(1, f.statementCloses);
        }
      }
    }
    var normal = new Fixture();
    verify(normal);
    assertEquals(
        COLUMNS, normal.calls.stream().filter(call -> call.endsWith(":getBoolean:8")).count());
  }

  @Test
  void column024IdentitySequenceDefinitionFalseOrSqlNullNeverPassesAnyColumn() throws Exception {
    for (int table = 0; table < TABLES; table++) {
      for (int row = 0; row < DATA.get(table).size(); row++) {
        for (String status : java.util.Arrays.asList(SQL_FALSE, null)) {
          var f = new Fixture();
          f.rows.get(table).get(row).set(8, status);
          reject(f);
          assertEquals(SQL.subList(0, table + 1), f.sql);
          assertEquals(table + 1, f.resultCloses);
          assertEquals(1, f.statementCloses);
        }
      }
    }
    var normal = new Fixture();
    verify(normal);
    assertEquals(
        COLUMNS, normal.calls.stream().filter(call -> call.endsWith(":getBoolean:9")).count());
  }

  @Test
  void column025EveryOwnerMustMatchAbsoluteDeclaredRole() throws Exception {
    for (int table = 0; table < TABLES; table++) {
      for (int row = 0; row < DATA.get(table).size(); row++) {
        for (String owner :
            java.util.Arrays.asList(null, "", "NK_OWNER", "nk_owner ", " nk_owner", "other_role")) {
          var f = new Fixture();
          f.rows.get(table).get(row).set(OWNER_FIELD, owner);
          reject(f);
          assertEquals(SQL.subList(0, table + 1), f.sql);
          assertEquals(table + 1, f.resultCloses);
          assertEquals(1, f.statementCloses);
        }
      }
    }
    var normal = new Fixture();
    verify(normal);
    assertEquals(
        COLUMNS, normal.calls.stream().filter(call -> call.endsWith(":getString:10")).count());
  }

  @Test
  void column026DefaultAndGeneratedValidityFalseOrSqlNullFailsEachColumn() throws Exception {
    for (int table = 0; table < TABLES; table++) {
      for (int row = 0; row < DATA.get(table).size(); row++) {
        for (String status : java.util.Arrays.asList(SQL_FALSE, null)) {
          var f = new Fixture();
          f.rows.get(table).get(row).set(DEFAULT_FIELD, status);
          reject(f);
          assertEquals(SQL.subList(0, table + 1), f.sql);
          assertEquals(table + 1, f.resultCloses);
          assertEquals(1, f.statementCloses);
        }
      }
    }
    var normal = new Fixture();
    verify(normal);
    assertEquals(
        COLUMNS, normal.calls.stream().filter(call -> call.endsWith(":getBoolean:11")).count());
  }

  private static void verify(Fixture f) throws SQLException {
    new MigrationMasterColumnVerifier().verify(f.connection());
  }

  private static void reject(Fixture f) {
    assertEquals(DIAGNOSTIC, assertThrows(SQLException.class, () -> verify(f)).getMessage());
  }

  private static void assertFailure(Fixture f, Throwable primary, List<Throwable> suppressed) {
    assertSame(primary, assertThrows(primary.getClass(), () -> verify(f)));
    assertEquals(suppressed.size(), primary.getSuppressed().length);
    for (int index = 0; index < suppressed.size(); index++)
      assertSame(suppressed.get(index), primary.getSuppressed()[index]);
  }

  private static Fixture readFailure(Throwable primary) {
    var f = new Fixture();
    f.failAt = expectedCalls().indexOf("q0:getInt:1");
    f.failure = primary;
    return f;
  }

  private static void flagAlternatives(int field, List<String> alternatives) {
    for (int table = 0; table < TABLES; table++) {
      for (int row = 0; row < DATA.get(table).size(); row++) {
        for (String flag : alternatives) {
          var f = new Fixture();
          if (flag.equals(f.rows.get(table).get(row).get(field))) continue;
          f.rows.get(table).get(row).set(field, flag);
          reject(f);
        }
      }
    }
  }

  private static List<Throwable> failures() {
    return List.of(
        new SQLException("synthetic sql"),
        new IllegalStateException("synthetic runtime"),
        new AssertionError("synthetic error"));
  }

  private static String key(int table) {
    return "q" + table;
  }

  private static List<String> expectedCalls() {
    var result = new ArrayList<>(List.of(AUTO, CREATE, TIMEOUT, FETCH));
    for (int table = 0; table < TABLES; table++) {
      String key = key(table);
      result.add(key + QUERY);
      for (int row = 0; row < DATA.get(table).size(); row++) {
        result.add(key + NEXT);
        result.add(key + ":getInt:1");
        result.add(key + WAS_NULL);
        result.add(key + ":getString:2");
        result.add(key + ":getString:3");
        result.add(key + ":getString:4");
        result.add(key + ":getBoolean:5");
        result.add(key + WAS_NULL);
        result.add(key + ":getString:6");
        result.add(key + ":getString:7");
        result.add(key + ":getBoolean:8");
        result.add(key + WAS_NULL);
        result.add(key + ":getBoolean:9");
        result.add(key + WAS_NULL);
        result.add(key + ":getString:10");
        result.add(key + ":getBoolean:11");
        result.add(key + WAS_NULL);
      }
      result.add(key + NEXT);
      result.add(key + CLOSE);
    }
    result.add(STATEMENT_CLOSE);
    return result;
  }

  private static final class EqualFailure extends SQLException {
    private static final long serialVersionUID = 1L;

    private EqualFailure() {
      super("synthetic equal-valued failure");
    }

    @Override
    public boolean equals(@Nullable Object other) {
      return other instanceof EqualFailure;
    }

    @Override
    public int hashCode() {
      return 1;
    }
  }

  private static final class Fixture {
    final List<List<List<@Nullable String>>> rows = new ArrayList<>();
    final List<String> calls = new ArrayList<>();
    final List<String> sql = new ArrayList<>();
    final List<String> connectionCalls = new ArrayList<>();
    final List<Integer> timeouts = new ArrayList<>();
    final List<Integer> fetchSizes = new ArrayList<>();
    boolean auto;
    boolean nullStatement;
    int nullResult = -1;
    int resultFailureTable = -1;
    @Nullable Throwable resultFailure;
    @Nullable Throwable statementFailure;
    int failAt = -1;
    Throwable failure = new SQLException("synthetic primary");
    int query;
    int resultCloses;
    int statementCloses;

    Fixture() {
      for (var table : DATA) {
        var copied = new ArrayList<List<@Nullable String>>();
        for (String row : table) copied.add(new ArrayList<>(List.of(row.split("\t", -1))));
        rows.add(copied);
      }
    }

    int lastQuery() {
      return query - 1;
    }

    void hit(String call) throws Throwable {
      int index = calls.size();
      calls.add(call);
      if (index == failAt) throw failure;
    }

    Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "getAutoCommit" -> {
                    connectionCalls.add(AUTO);
                    hit(AUTO);
                    return auto;
                  }
                  case "createStatement" -> {
                    connectionCalls.add(CREATE);
                    hit(CREATE);
                    return nullStatement ? null : statement();
                  }
                  default ->
                      throw new AssertionError(
                          "unexpected connection operation " + method.getName());
                }
              });
    }

    Statement statement() {
      return (Statement)
          Proxy.newProxyInstance(
              Statement.class.getClassLoader(),
              new Class<?>[] {Statement.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "setQueryTimeout" -> {
                    hit(TIMEOUT);
                    timeouts.add((Integer) args[0]);
                    return null;
                  }
                  case "setFetchSize" -> {
                    hit(FETCH);
                    fetchSizes.add((Integer) args[0]);
                    return null;
                  }
                  case "executeQuery" -> {
                    int table = query;
                    query++;
                    sql.add((String) args[0]);
                    hit(key(table) + QUERY);
                    return table == nullResult ? null : result(table);
                  }
                  case "close" -> {
                    statementCloses++;
                    hit(STATEMENT_CLOSE);
                    if (statementFailure != null) throw statementFailure;
                    return null;
                  }
                  default ->
                      throw new AssertionError(
                          "unexpected statement operation " + method.getName());
                }
              });
    }

    ResultSet result(int table) {
      int[] row = {-1};
      boolean[] wasNull = {false};
      String key = key(table);
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.equals("next")) {
                  hit(key + NEXT);
                  row[0]++;
                  return row[0] < rows.get(table).size();
                }
                if (name.equals("wasNull")) {
                  hit(key + WAS_NULL);
                  return wasNull[0];
                }
                if (name.equals("close")) {
                  resultCloses++;
                  hit(key + CLOSE);
                  if (table == resultFailureTable && resultFailure != null) throw resultFailure;
                  return null;
                }
                if (List.of(GET_INT, GET_BOOLEAN, GET_STRING).contains(name)) {
                  int column = (Integer) args[0];
                  hit(key + ":" + name + ":" + column);
                  String value = rows.get(table).get(row[0]).get(column - 1);
                  wasNull[0] = value == null;
                  return switch (name) {
                    case GET_INT -> value == null ? 0 : Integer.parseInt(value);
                    case GET_BOOLEAN -> value != null && Boolean.parseBoolean(value);
                    default -> value;
                  };
                }
                throw new AssertionError("unexpected result operation " + name);
              });
    }
  }
}

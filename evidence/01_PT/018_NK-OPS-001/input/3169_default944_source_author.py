"""Exact eleventh default/generated predicate; independent fixtures remain explicit literal rows."""
from pathlib import Path
import json,re,hashlib
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG33042-default944-source-v1';assert not e.exists();d=r/'src/schubert-nk-bootstrap/src';m=d/'main/java/dev/codex/schubert/nk/migration/MigrationMasterColumnVerifier.java';ct=d/'test/java/dev/codex/schubert/nk/migration/MigrationMasterColumnVerifierTest.java';tt=ct.with_name('MigrationMasterTargetPublisherTest.java');paths=[m,ct,tt];old={p:p.read_text() for p in paths};needle='pg_catalog.pg_get_userbyid(c.relowner) FROM pg_catalog.pg_class c';predicate="CASE WHEN (c.relname='speakers' AND a.attname='is_protagonist') OR (c.relname='script_entries' AND a.attname='body_search') THEN a.atthasdef AND (SELECT count(*) FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum)=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum AND pg_catalog.pg_get_expr(ad.adbin,ad.adrelid,false)=CASE WHEN c.relname='speakers' THEN 'false' ELSE 'lower(body)' END) ELSE NOT a.atthasdef AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum) END";replacement=needle.replace(' FROM pg_catalog.pg_class c',','+predicate+' FROM pg_catalog.pg_class c')
assert old[m].count(needle)==1 and old[ct].count(needle)==6 and old[tt].count(needle)==12
assert old[ct].count('void column025')==1 and old[tt].count('void target035')==1 and 'void column026' not in old[ct] and 'void target036' not in old[tt]
e.mkdir()
for p,s in old.items():(e/('original-'+p.name+'.txt')).open('x').write(s)
s=old[m].replace(needle,replacement).replace('SSC380/387/388/404;','SSC380/387/388/404/405;').replace('PT-MIG-COLUMN001..025','PT-MIG-COLUMN001..026');anchor='        if (!"nk_owner".equals(result.getString(10))) throw invalid();';assert s.count(anchor)==1;s=s.replace(anchor,anchor+'\n        boolean defaultDefinitionValid = result.getBoolean(11);\n        if (result.wasNull() || !defaultDefinitionValid) throw invalid();');m.write_text(s)
for p in [ct,tt]:
 s=old[p].replace(needle,replacement);count=[0]
 def app(match):
  raw=match.group()
  if len(raw[1:-1].split('\\t'))==10:count[0]+=1;return raw[:-1]+'\\ttrue"'
  return raw
 s=re.sub(r'"(?:[^"\\]|\\.)*"',app,s);assert count[0]==59
 if p==ct:
  s=s.replace('PT-MIG-COLUMN001..025','PT-MIG-COLUMN001..026').replace('private static final int FIELDS = 10;','private static final int FIELDS = 11;\n  private static final int DEFAULT_FIELD = 10;').replace('(field == 4 || field == 7 || field == 8)','(field == 4 || field == 7 || field == 8 || field == DEFAULT_FIELD)')
  anchor='        result.add(key + ":getString:10");';assert s.count(anchor)==1;s=s.replace(anchor,anchor+'\n        result.add(key + ":getBoolean:11");\n        result.add(key + WAS_NULL);')
  anchor='  private static void verify(Fixture f) throws SQLException {'
  body='''  @Test
  void column026DefaultAndGeneratedValidityFalseOrSqlNullFailsEachColumn() throws Exception {
    for (int table = 0; table < TABLES; table++) {
      for (int row = 0; row < DATA.get(table).size(); row++) {
        for (String status : java.util.Arrays.asList("false", null)) {
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
    assertEquals(COLUMNS, normal.calls.stream().filter(call -> call.endsWith(":getBoolean:11")).count());
  }

'''
 else:
  s=s.replace('PT-MIG-TARGET001..035','PT-MIG-TARGET001..036').replace('private static final int COLUMN_CATALOG_FIELDS = 10;','private static final int COLUMN_CATALOG_FIELDS = 11;\n  private static final int DEFAULT_FIELD = 10;').replace('private static final int MIXED_CATALOG_GETTERS = 1185;','private static final int MIXED_CATALOG_GETTERS = 1251;').replace('(field == 4 || field == 7 || field == 8)','(field == 4 || field == 7 || field == 8 || field == DEFAULT_FIELD)')
  anchor='  private static int catalogFieldCount(int table) {'
  body='''  @Test
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

'''
 assert s.count(anchor)==1;s=s.replace(anchor,body+anchor);p.write_text(s)
(e/'author-receipt.json').open('x').write(json.dumps(dict(actualExit=0,sourceOnly=True,sqlPredicate=predicate,oldFields=10,newFields=11,expected944=True,actualDbOperations=0),ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,sourceOnly=True,newDefinitions=2,whole=944))

"""SSC450 private literal SQL operations; preserve SQL corpus, method bodies and whole test inputs."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';base=r/'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/migration'
core='e8822b0e40d08a0a733bd21b6866b3ece3de5b65'
approved=json.loads((b/'evidence/PG36866-ssc450-design-main-v2/manifest.json').read_text())
assert approved['actualExit']==0 and approved['ssc']=='SSC450'
names=['AssetStagingTables','MigrationMasterColumnVerifier','MigrationMasterConstraintVerifier',
       'MigrationMasterContentVerifier','MigrationMasterFinalizer','MigrationMasterReferenceVerifier']
before={name:(base/(name+'.java')).read_text() for name in names}
for name,text in before.items():
    path=str((base/(name+'.java')).relative_to(r))
    assert subprocess.check_output(['git','show',core+':'+path]).decode()==text
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tests={str(p.relative_to(r)):sha(p) for name in names for p in
       (r/'src/schubert-nk-bootstrap/src/test/java').rglob(name+'Test.java')}
assert len(tests)==6
out=b/'evidence/PG36868-ssc450-sql-source-manufacture-v1'
assert not out.exists()
def items(text):
    result=[];start=0;quoted=False;escaped=False;depth=0
    for i,char in enumerate(text):
        if quoted:
            if escaped:escaped=False
            elif char=='\\':escaped=True
            elif char=='"':quoted=False
        elif char=='"':quoted=True
        elif char=='(':depth+=1
        elif char==')':depth-=1
        elif char==',' and depth==0:result.append(text[start:i].strip());start=i+1
    assert not quoted and depth==0
    result.append(text[start:].strip());assert all(result)
    return result
def list_block(source,field):
    match=re.search(r'  private static final List<String> '+field+r' =\s*List\.of\((.*?)\);',source,re.S)
    assert match,field
    return match,items(match.group(1))
query_interface='''
  @FunctionalInterface
  private interface SqlQuery {
    @Nullable ResultSet execute(Statement statement) throws SQLException;
  }
'''
mutation_interface='''
  @FunctionalInterface
  private interface SqlMutation {
    long execute(Statement statement) throws SQLException;
  }
'''
prepare_interface='''
  @FunctionalInterface
  private interface SqlPrepare {
    @Nullable PreparedStatement create(Connection connection) throws SQLException;
  }
'''
after={};corpus={}
for name in names[1:4]:
    text=before[name];match,expressions=list_block(text,'QUERIES')
    assert len(expressions)==(7 if name=='MigrationMasterContentVerifier' else 6)
    replacement='  private static final List<SqlQuery> QUERIES =\n      List.of(\n          '+',\n          '.join(
        'statement -> statement.executeQuery('+expr+')' for expr in expressions)+');'
    text=text[:match.start()]+replacement+text[match.end():]
    assert text.count('statement.executeQuery(QUERIES.get(table))')==1
    text=text.replace('statement.executeQuery(QUERIES.get(table))','QUERIES.get(table).execute(statement)')
    after[name]=text.rstrip()[:-1]+query_interface+'}\n';corpus[name]=dict(queriesBefore=expressions,queriesAfter=expressions)
name='MigrationMasterReferenceVerifier';text=before[name];corpus[name]={}
for field in ['COUNTS','INSPECTIONS']:
    match,expressions=list_block(text,field)
    replacement='  private static final List<SqlQuery> '+field+' =\n      List.of(\n          '+',\n          '.join(
        'statement -> statement.executeQuery('+expr+')' for expr in expressions)+');'
    text=text[:match.start()]+replacement+text[match.end():];corpus[name][field]=expressions
assert text.count('statement.executeQuery(COUNTS.get(index))')==1
assert text.count('statement.executeQuery(query)')==1
text=text.replace('statement.executeQuery(COUNTS.get(index))','COUNTS.get(index).execute(statement)').replace(
    'statement.executeQuery(query)','query.execute(statement)')
after[name]=text.rstrip()[:-1]+query_interface+'}\n'
name='MigrationMasterFinalizer';text=before[name]
identity_match,identity_expr=list_block(text,'IDENTITY_TABLES')
identity=[json.loads(x) for x in identity_expr];assert len(identity)==5
analyze_match,analyze_expr=list_block(text,'ANALYZE_TABLES')
analyze=[json.loads(x) for x in analyze_expr];assert len(analyze)==6
literal=lambda value:json.dumps(value,ensure_ascii=False)
max_sql=['SELECT COALESCE(MAX(id),0) FROM schubert.'+t for t in identity]
prepare_sql=["SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert."+t+"', 'id'), ?, ?)" for t in identity]
analyze_sql=['ANALYZE schubert.'+t for t in analyze]
new_fields='  private static final List<SqlQuery> MAXIMUM_QUERIES =\n      List.of(\n          '+',\n          '.join(
    'statement -> statement.executeQuery('+literal(x)+')' for x in max_sql)+');\n'
new_fields+='  private static final List<SqlPrepare> SYNCHRONIZERS =\n      List.of(\n          '+',\n          '.join(
    'connection -> connection.prepareStatement('+literal(x)+')' for x in prepare_sql)+');\n'
new_fields+='  private static final List<SqlMutation> ANALYZE_OPERATIONS =\n      List.of(\n          '+',\n          '.join(
    'statement -> statement.executeUpdate('+literal(x)+')' for x in analyze_sql)+');'
text=text[:identity_match.start()]+new_fields+text[analyze_match.end():]
text=text.replace('IDENTITY_TABLES.size()','MAXIMUM_QUERIES.size()')
old='statement.executeQuery(\n                "SELECT COALESCE(MAX(id),0) FROM schubert." + IDENTITY_TABLES.get(index))'
assert text.count(old)==1;text=text.replace(old,'MAXIMUM_QUERIES.get(index).execute(statement)')
text=text.replace('synchronize(connection, IDENTITY_TABLES.get(index), expected.get(index))',
                  'synchronize(connection, SYNCHRONIZERS.get(index), expected.get(index))')
text=text.replace('for (var table : ANALYZE_TABLES)','for (var operation : ANALYZE_OPERATIONS)').replace(
    'statement.executeUpdate("ANALYZE schubert." + table)','operation.execute(statement)')
text=text.replace('synchronize(Connection connection, String table, long maximum)',
                  'synchronize(Connection connection, SqlPrepare operation, long maximum)')
old='''requirePrepared(
            connection.prepareStatement(
                "SELECT pg_catalog.setval(pg_catalog.pg_get_serial_sequence('schubert."
                    + table
                    + "', 'id'), ?, ?)"))'''
assert text.count(old)==1;text=text.replace(old,'requirePrepared(operation.create(connection))')
assert 'IDENTITY_TABLES' not in text and 'ANALYZE_TABLES' not in text
after[name]=text.rstrip()[:-1]+query_interface+mutation_interface+prepare_interface+'}\n'
corpus[name]=dict(maximum=max_sql,prepare=prepare_sql,analyze=analyze_sql)
name='AssetStagingTables';text=before[name]
block=re.search(r'  private static final List<Table> TABLES =\s*List\.of\((.*?)\);',text,re.S);assert block
tables=[]
for row in items(block.group(1)):
    match=re.fullmatch(r'new Table\((.*)\)',row,re.S);assert match
    values=[json.loads(x) for x in items(match.group(1))];assert len(values)==3;tables.append(values)
assert len(tables)==3
plans=[];asset_corpus=[]
for table,columns,order in tables:
    ddl='CREATE TEMP TABLE nk_mig_'+table+' ON COMMIT DROP AS SELECT '+columns+' FROM schubert.'+table+' WITH NO DATA'
    target='SELECT count(*) FROM schubert.'+table;stage='SELECT count(*) FROM pg_temp.nk_mig_'+table
    insert='INSERT INTO schubert.'+table+' ('+columns+') SELECT '+columns+' FROM pg_temp.nk_mig_'+table+' ORDER BY '+order
    plans.append('new Table(\n              statement -> statement.executeUpdate('+literal(ddl)+'),\n'
        '              statement -> statement.executeQuery('+literal(target)+'),\n'
        '              statement -> statement.executeQuery('+literal(stage)+'),\n'
        '              statement -> statement.executeLargeUpdate('+literal(insert)+'))')
    asset_corpus.append(dict(table=table,prepare=ddl,targetCount=target,stagedCount=stage,insert=insert))
replacement='  private static final List<Table> TABLES =\n      List.of(\n          '+',\n          '.join(plans)+');'
text=text[:block.start()]+replacement+text[block.end():]
start=text.index('      for (var table : TABLES) {');end=text.index('\n    } catch ',start)
text=text[:start]+'''      for (var table : TABLES)
        if (table.prepareOperation.execute(statement) != 0) throw invalid();'''+text[end:]
start=text.index('      for (var table : TABLES) requireCount(');end=text.index('\n    } catch ',start)
text=text[:start]+'''      for (var table : TABLES) requireResult(table.targetCountOperation.execute(statement), 0);
      for (int index = 0; index < TABLES.size(); index++)
        requireResult(TABLES.get(index).stageCountOperation.execute(statement), expected[index]);
      for (int index = 0; index < TABLES.size(); index++)
        if (TABLES.get(index).insertOperation.execute(statement) != expected[index]) throw invalid();
      for (int index = 0; index < TABLES.size(); index++)
        requireResult(TABLES.get(index).targetCountOperation.execute(statement), expected[index]);'''+text[end:]
start=text.index('  private static void requireCount(');end=text.index('  private static void requireResult(',start)
text=text[:start]+text[end:]
start=text.index('  /** Fixed approved SQL identifiers only, never caller-supplied metadata. */')
end=text.index('  // SSC366:',start)
text=text[:start]+'''  /** SSC450: fixed operations capture no resource and cannot accept external SQL. */
  private static final class Table {
    private final SqlMutation prepareOperation;
    private final SqlQuery targetCountOperation;
    private final SqlQuery stageCountOperation;
    private final SqlMutation insertOperation;

    private Table(SqlMutation prepareOperation, SqlQuery targetCountOperation,
        SqlQuery stageCountOperation, SqlMutation insertOperation) {
      this.prepareOperation = prepareOperation;
      this.targetCountOperation = targetCountOperation;
      this.stageCountOperation = stageCountOperation;
      this.insertOperation = insertOperation;
    }
  }

'''+text[end:]
after[name]=text.rstrip()[:-1]+query_interface+mutation_interface+'}\n';corpus[name]=asset_corpus
assert set(after)==set(before)
for name,text in after.items():
    assert text.count('SuppressFBWarnings')==before[name].count('SuppressFBWarnings')
    assert 'DriverManager' not in text and 'DataSource' not in text
    assert 'private interface SqlQuery' in text
assert all(sha(r/p)==h for p,h in tests.items()),'original independent whole tests unchanged'
out.mkdir()
for name,text in after.items():
    (out/(name+'-before.java.txt')).open('x').write(before[name])
    (base/(name+'.java')).write_text(text)
(out/'sql-corpus-equivalence-inputs.json').open('x').write(json.dumps(corpus,ensure_ascii=False,indent=2)+'\n')
(out/'manifest.json').open('x').write(json.dumps(dict(actualExit=0,sourceBefore=core,
    ssc='SSC450',designMain=approved['mainCommit'],mainChanged=6,independentWholeTests=160,
    originalTestSourceHashes=tests,generatedOnlyCandidateNotTested=True,
    sourceHashesAfter={str((base/(name+'.java')).relative_to(r)):sha(base/(name+'.java')) for name in names},
    actualDbVmNativeServiceActions=0,heldClassfileActions=0,formalUpdated=False),indent=2)+'\n')
print(json.dumps(dict(actualExit=0,mainChanged=6,testsChanged=0,wholeTestsNotRun=160)))

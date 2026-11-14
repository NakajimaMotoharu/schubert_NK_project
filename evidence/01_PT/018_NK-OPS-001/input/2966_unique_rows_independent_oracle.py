"""V002 nineteen declared keys and independent SQL NULL/duplicate vectors; no product or DB calls."""
from pathlib import Path
import json,re,hashlib,datetime,collections
r=Path.cwd();i=r/'evidence/01_PT/018_NK-OPS-001/input';constraints=json.loads((i/'2937_constraint_scope_independent_oracle.json').read_text());columns=json.loads((i/'2901_master_column_independent_oracle.json').read_text());ddl=r/'src/schubert-nk-api/src/main/resources/db/migration/V002__account_session_and_master_tables.sql';source=ddl.read_text();tables={};counts=collections.Counter()
for table,rows in constraints['tables'].items():
 cols=columns['tables'][table];keys=[];queries=[];block=source.split('CREATE TABLE schubert.'+table+' (',1)[1].split('\n);',1)[0]
 for name,kind,ordinals,_,_,_ in rows:
  if kind not in ['p','u']:continue
  indices=[int(v)-1 for v in ordinals.split(',')];names=[cols[idx][0] for idx in indices];assert all(cols[idx][3]=='true' for idx in indices);assert all(re.fullmatch('[a-z_]+',v) for v in names)
  match=re.search(r'CONSTRAINT '+re.escape(name)+r' (?:PRIMARY KEY|UNIQUE) \(([^)]+)\)',block);assert match and match.group(1).replace(' ','').split(',')==names
  base='SELECT 1 FROM schubert.'+table
  if kind=='u':base+=' WHERE '+' AND '.join(col+' IS NOT NULL' for col in names)
  base+=' GROUP BY '+','.join(names)+' HAVING count(*)>1'
  if kind=='p':base+=' OR ('+' OR '.join(col+' IS NULL' for col in names)+')'
  keys.append(dict(name=name,kind=kind,columns=names,declaredColumnOrdinals=ordinals,allDeclaredNotNull=True,violationGroupSql=base));queries.append(base);counts[kind]+=1
 tables[table]=dict(keys=keys,query='SELECT count(*) FROM ('+' UNION ALL '.join(queries)+') violations')
assert counts==dict(p=6,u=13) and [len(v['keys']) for v in tables.values()]==[3,4,4,3,3,2]
# Independent literal input/expected vectors; only simple equality keys, no locale emulation.
vectors=[dict(kind='p',rows=[[None]],expected=1),dict(kind='p',rows=[[1],[1]],expected=1),dict(kind='p',rows=[[1],[2]],expected=0),dict(kind='u',rows=[[None],[None]],expected=0),dict(kind='u',rows=[[None,1],[None,1]],expected=0),dict(kind='u',rows=[[1,'A'],[1,'A']],expected=1),dict(kind='u',rows=[[1,'A'],[2,'A']],expected=0)]
for v in vectors:
 groups=collections.Counter(tuple(row) for row in v['rows'] if v['kind']=='p' or all(value is not None for value in row));actual=sum(n>1 or v['kind']=='p' and any(value is None for value in key) for key,n in groups.items());assert actual==v['expected']
out=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceDdl=dict(path=str(ddl.relative_to(r)),sha256=hashlib.sha256(ddl.read_bytes()).hexdigest()),tables=tables,queries=[v['query'] for v in tables.values()],primaryKeys=6,uniqueKeys=13,expectedCounts=[0]*6,nullAndDuplicateGoldenVectors=vectors,all19KeysMatchManualMatrixAndDdl=True,nullsDistinctForUniquePreserved=True,primaryNullRejected=True,productionMethodsCalled=0,actualDatabaseOrSqlEvaluatorExecuted=False,indexAndCollationNotQualified=True,technicalSource='https://www.postgresql.org/docs/18/ddl-constraints.html')
(i/'2966_unique_rows_independent_oracle.json').open('x').write(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,primary=6,unique=13,tableKeys=[len(v['keys']) for v in tables.values()],goldenVectors=7,productTestsExecuted=0))

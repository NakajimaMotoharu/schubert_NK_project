"""Independent V002 declarations and fixed catalog predicate truth vectors; no database execution."""
from pathlib import Path
import json,re,hashlib,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG33042-default944-source-v1';ref=lambda p:dict(path=str(p.relative_to(r)),sha256=hashlib.sha256(p.read_bytes()).hexdigest());base='src/schubert-nk-bootstrap/src/';m=base+'main/java/dev/codex/schubert/nk/migration/MigrationMasterColumnVerifier.java';ct=m.replace('/main/','/test/').replace('.java','Test.java');tt=ct.replace('ColumnVerifier','TargetPublisher');changed={m,ct,tt};old={}
for folder,source in [('main','6ece31a0ea'),('test','7f4c4c045522f7e799e71ff02c891c8029483c18')]:
 for p in (r/(base+folder+'/java/dev/codex/schubert/nk/migration')).glob('*.java'):
  path=str(p.relative_to(r))
  if path in changed:continue
  digest=hashlib.sha256(subprocess.check_output(['git','show',source+':'+path])).hexdigest();assert digest==ref(p)['sha256'],path;old[path]=digest
assert len(old)==89
# Build SQL independently from the approved SS405 fixed predicates, not a production constant.
pred="CASE WHEN (c.relname='speakers' AND a.attname='is_protagonist') OR (c.relname='script_entries' AND a.attname='body_search') THEN a.atthasdef AND (SELECT count(*) FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum)=1 AND EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum AND pg_catalog.pg_get_expr(ad.adbin,ad.adrelid,false)=CASE WHEN c.relname='speakers' THEN 'false' ELSE 'lower(body)' END) ELSE NOT a.atthasdef AND NOT EXISTS (SELECT 1 FROM pg_catalog.pg_attrdef ad WHERE ad.adrelid=c.oid AND ad.adnum=a.attnum) END";needle='pg_catalog.pg_get_userbyid(c.relowner) FROM pg_catalog.pg_class c';new=needle.replace(' FROM pg_catalog.pg_class c',','+pred+' FROM pg_catalog.pg_class c')
def rows(text,name):
 start=text.index('  private static final List<List<String>> '+name+' =');end=text.index(';',start);block=text[start:end];constants={x:json.loads(v) for x,v in re.findall(r'private static final String (FIXTURE_LITERAL_[12]|CATALOG_IDENTITY_COLUMN|CATALOG_GAME_COLUMN)\s*=\s*("(?:[^"\\]|\\.)*")',text)};tokens=re.findall(r'"(?:[^"\\]|\\.)*"|FIXTURE_LITERAL_[12]|CATALOG_IDENTITY_COLUMN|CATALOG_GAME_COLUMN',block);return [json.loads(x) if x.startswith('"') else constants[x] for x in tokens]
receipts=[];columnrows=[]
for path,name,n in [(ct,'DATA',6),(tt,'CATALOG_ROWS',12)]:
 p=r/path;s=p.read_text();before=(e/('original-'+p.name+'.txt')).read_text();assert s.count(needle)==0 and s.count(new)==n;a=rows(before,name);z=rows(s,name);assert len(a)==len(z)==(66 if path==ct else 141);assert z[:66]==[x+'\ttrue' for x in a[:66]] and z[66:]==a[66:];assert all(len(x.split('\t'))==11 for x in z[:66]);assert len(re.findall(r'@Test\b',s))==(26 if path==ct else 36)
 if path==ct:columnrows=a
 else:assert 'MIXED_CATALOG_GETTERS = 1251;' in s and 1251==66*11+75*7
 for line in before.splitlines():
  if line.lstrip().startswith('"SELECT a.attnum,'):assert line.replace(needle,new) in s
 receipts.append(dict(source=ref(p),old=ref(e/('original-'+p.name+'.txt')),rows=len(z),ownerDefaultRows=66))
s=(r/m).read_text();before=(e/('original-'+Path(m).name+'.txt')).read_text();expected=before.replace(needle,new).replace('SSC380/387/388/404;','SSC380/387/388/404/405;').replace('PT-MIG-COLUMN001..025','PT-MIG-COLUMN001..026').replace('        if (!"nk_owner".equals(result.getString(10))) throw invalid();','        if (!"nk_owner".equals(result.getString(10))) throw invalid();\n        boolean defaultDefinitionValid = result.getBoolean(11);\n        if (result.wasNull() || !defaultDefinitionValid) throw invalid();');assert s==expected
names=['speakers','script_files','script_entries','audio_files','media_assets','entry_audio_links'];sizes=[7,11,13,12,17,6];assert sum(sizes)==66;ddl=r/'src/schubert-nk-api/src/main/resources/db/migration/V002__account_session_and_master_tables.sql';text=ddl.read_text();definitions={}
for table in names:
 block=re.search(r'CREATE TABLE schubert\.'+table+r' \(\n([\s\S]*?)\n\);',text).group(1);defaults=re.findall(r'^\s*(\w+)\s+[^\n]*?\bDEFAULT\s+(false)\b',block,re.M);generated=re.findall(r'^\s*(\w+)\s+text GENERATED ALWAYS AS \((lower\(body\))\) STORED',block,re.M)
 for col,expr in defaults+generated:definitions[(table,col)]=expr
assert definitions=={('speakers','is_protagonist'):'false',('script_entries','body_search'):'lower(body)'}
def independent(table,col,hasdef,exprs):
 wanted=definitions.get((table,col))
 if wanted is None:return not hasdef and not exprs
 return hasdef and exprs==[wanted]
vectors=[];offset=0
for table,size in zip(names,sizes):
 for row in columnrows[offset:offset+size]:
  col=row.split('\t')[1];wanted=definitions.get((table,col));normal=[] if wanted is None else [wanted]
  cases=[(wanted is not None,normal,True),(wanted is None,normal,False),(True,[],False),(False,['unexpected'],False),(True,['unexpected'],False),(True,[None],False),(True,[wanted,wanted],False)]
  if wanted is not None:cases += [(True,[wanted+' '],False),(True,[wanted.upper()],False),(False,[wanted],False)]
  for flag,exprs,expectedValue in cases:
   actual=independent(table,col,flag,exprs);assert actual==expectedValue,(table,col,flag,exprs);vectors.append(dict(table=table,column=col,atthasdef=flag,attrdefExpressions=exprs,expected=expectedValue,actual=actual))
 offset+=size
v=dict(actualExit=0,oldUnchangedSourceHashes=old,changes=receipts,newMain=0,changedMain=1,newTests=2,wholeExpected=944,physicalClasses=65,catalogGetters=1251,queryCount=94,results=76,ownedStatementCloses=17,production=ref(r/m),fixedV002=ref(ddl),independentDefaultExpressions=[dict(table=t,column=c,expression=x) for (t,c),x in definitions.items()],independentTruthVectors=vectors,truthVectorsExecutedInPython=len(vectors),sqlPredicate=pred,sqlActuallyExecuted=False,actualDbExecuted=False,deparserAndSearchPathRuntimeHold=True,authorityActions=0,expectedFromProduction=False,formalAccepted=False)
(e/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,new=2,whole=944,rows=66,logicalVectors=len(vectors),sqlActuallyExecuted=False))

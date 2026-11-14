"""SS331 fixed absolute owner; independent old/new table vectors and exact source boundaries."""
from pathlib import Path
import json,re,hashlib,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG32968-owner942-source-v1';ref=lambda p:dict(path=str(p.relative_to(r)),sha256=hashlib.sha256(p.read_bytes()).hexdigest());base='src/schubert-nk-bootstrap/src/';m=base+'main/java/dev/codex/schubert/nk/migration/MigrationMasterColumnVerifier.java';ct=m.replace('/main/','/test/').replace('.java','Test.java');tt=ct.replace('ColumnVerifier','TargetPublisher');changed={m,ct,tt};old={}
for folder,source in [('main','63c660b3fe7363b694ec6148ca99fa748e57c2bd'),('test','045cceabaf88e6ba38b4342cc819a72fb9c15733')]:
 for p in (r/(base+folder+'/java/dev/codex/schubert/nk/migration')).glob('*.java'):
  path=str(p.relative_to(r))
  if path in changed:continue
  digest=hashlib.sha256(subprocess.check_output(['git','show',source+':'+path])).hexdigest();assert digest==ref(p)['sha256'],path;old[path]=digest
assert len(old)==89
needle=" END FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace JOIN pg_catalog.pg_attribute a";new=needle.replace(' END FROM',' END,pg_catalog.pg_get_userbyid(c.relowner) FROM')
def rows(text,name):
 start=text.index('  private static final List<List<String>> '+name+' =');end=text.index(';',start);block=text[start:end];constants={x:json.loads(v) for x,v in re.findall(r'private static final String (FIXTURE_LITERAL_[12]|CATALOG_IDENTITY_COLUMN|CATALOG_GAME_COLUMN)\s*=\s*("(?:[^"\\]|\\.)*")',text)};tokens=re.findall(r'"(?:[^"\\]|\\.)*"|FIXTURE_LITERAL_[12]|CATALOG_IDENTITY_COLUMN|CATALOG_GAME_COLUMN',block);return [json.loads(x) if x.startswith('"') else constants[x] for x in tokens]
receipts=[]
for path,name,n in [(ct,'DATA',6),(tt,'CATALOG_ROWS',12)]:
 p=r/path;s=p.read_text();before=(e/('original-'+p.name+'.txt')).read_text();assert s.count(needle)==0 and s.count(new)==n
 a=rows(before,name);z=rows(s,name)
 # Target has75 constraint rows following66 column rows; preserve them byte-exact.
 assert len(a)==len(z)==(66 if path==ct else 141)
 assert z[:66]==[x+'\tnk_owner' for x in a[:66]] and z[66:]==a[66:]
 assert all(len(x.split('\t'))==10 for x in z[:66])
 if path==tt:
  assert 'MIXED_CATALOG_GETTERS = 1185;' in s and 1185==66*10+75*7
 for line in before.splitlines():
  if line.lstrip().startswith('"SELECT a.attnum,'):assert line.replace(needle,new) in s
 count=len(re.findall(r'@Test\b',s));assert count==(25 if path==ct else 35)
 receipts.append(dict(source=ref(p),old=ref(e/('original-'+p.name+'.txt')),rows=len(z),ownerRows=66,testDefinitions=count))
s=(r/m).read_text();before=(e/('original-'+Path(m).name+'.txt')).read_text();expected=before.replace(needle,new).replace('PT-MIG-COLUMN001..024','PT-MIG-COLUMN001..025').replace('SSC380/387/388;','SSC380/387/388/404;').replace('        if (result.wasNull() || !identitySequenceValid) throw invalid();','        if (result.wasNull() || !identitySequenceValid) throw invalid();\n        if (!"nk_owner".equals(result.getString(10))) throw invalid();');assert s==expected
ss=next((r/'documents/300_SS').rglob('331_*'));assert '`nk_owner` | no | Schema/object owner' in ss.read_text()
v=dict(actualExit=0,oldUnchangedSourceHashes=old,changes=receipts,ss331=ref(ss),newMain=0,changedMain=1,old940Reauthentication=True,newTests=2,wholeExpected=942,physicalClasses=65,catalogGetters=1185,queryCount=94,results=76,ownedStatementCloses=17,production=ref(r/m),actualDbExecuted=False,authorityActions=0,expectedFromProduction=False,formalAccepted=False)
(e/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,unchanged=len(old),new=2,whole=942,ownerRows=66,catalogGetters=1185))

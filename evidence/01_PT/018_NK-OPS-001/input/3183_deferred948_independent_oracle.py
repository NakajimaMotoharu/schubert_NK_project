"""V002 deferred declaration, original SQL preserved plus one command; no actual trigger execution."""
from pathlib import Path
import json,re,hashlib,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG33086-deferred948-source-v1';ref=lambda p:dict(path=str(p.relative_to(r)),sha256=hashlib.sha256(p.read_bytes()).hexdigest());base='src/schubert-nk-bootstrap/src/';m=base+'main/java/dev/codex/schubert/nk/migration/MigrationMasterFinalizer.java';p=m.replace('Finalizer','TargetPublisher');ft=m.replace('/main/','/test/').replace('.java','Test.java');tt=p.replace('/main/','/test/').replace('.java','Test.java');changed={m,p,ft,tt};old={}
for folder,source in [('main','f0e845f421f342d196e311e5dd78e97c01116ee8'),('test','dfa344cd7d2a387c4a2084aaa9cfdacf63243558')]:
 for path in (r/(base+folder+'/java/dev/codex/schubert/nk/migration')).glob('*.java'):
  rel=str(path.relative_to(r))
  if rel in changed:continue
  digest=hashlib.sha256(subprocess.check_output(['git','show',source+':'+rel])).hexdigest();assert digest==ref(path)['sha256'],rel;old[rel]=digest
assert len(old)==88 and sum(len(re.findall(r'@Test\b',(r/x).read_text())) for x in old if '/test/' in x)==880
SQL='SET CONSTRAINTS schubert.ck_entry_audio_links_entry_type_limit IMMEDIATE';GAME='SELECT id,code,title,display_order,created_at FROM schubert.games ORDER BY id'
def block(s,name,kind='String'):
 a=s.index('  private static final List<'+kind+'> '+name+' =');return s[a:s.index(';',a)]
def queries(s,name):
 return [SQL if x=='FLUSH_SQL' else GAME if x=='GAMES_SQL' else json.loads(x) for x in re.findall(r'"(?:[^"\\]|\\.)*"|FLUSH_SQL|GAMES_SQL',block(s,name))]
def ints(s,name):return [int(x) for x in re.findall(r'\d+',block(s,name,'Integer'))]
def tokens(s):return [x for x in re.findall(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:[^"\\]|\\.)*"|\w+|[^\s]',s) if not x.startswith(('//','/*'))]
a=(e/'original-MigrationMasterTargetPublisherTest.java.txt').read_text();z=(r/tt).read_text();before=queries(a,'SQL');after=queries(z,'SQL');assert len(before)==94 and len(after)==95 and after==before[:78]+[SQL]+before[78:];assert after[78]==SQL and after[79].startswith('SELECT COALESCE(MAX(id),0)')
for name in ['CATALOG_SQL','CONTENT_SQL']:assert queries(a,name)==queries(z,name)
assert ints(a,'OWNER_START')==ints(z,'OWNER_START');assert ints(a,'CLOSE_RESULTS')==ints(z,'CLOSE_RESULTS');assert ints(z,'CLOSE_SQL_PREFIX')==[x if x<=78 else x+1 for x in ints(a,'CLOSE_SQL_PREFIX')]
for name,val in dict(SQL_COUNT=95,RESULTS=76,CLOSES=17,MIXED_CATALOG_GETTERS=1251,SCALARS=56,CONTENT_END=78,SETVAL_FIRST=84,ANALYZE_FIRST=89).items():assert 'private static final int '+name+' = '+str(val)+';' in z
assert tokens((r/p).read_text())==tokens((e/'original-MigrationMasterTargetPublisher.java.txt').read_text())
beforeMain=(e/'original-MigrationMasterFinalizer.java.txt').read_text();actual=(r/m).read_text();anchor='      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);\n      // All five checks';expected=beforeMain.replace(anchor,'      statement.setQueryTimeout(QUERY_TIMEOUT_SECONDS);\n      if (statement.executeUpdate("'+SQL+'") != 0\n          || statement.getWarnings() != null) throw invalid();\n      // All five checks');assert expected!=beforeMain and tokens(expected)==tokens(actual)
f=(r/ft).read_text();oldft=(e/'original-MigrationMasterFinalizerTest.java.txt').read_text()
for name in ['MAX_SQL','SET_SQL','ANALYZE_SQL']:assert queries(f,name)==queries(oldft,name)
assert len(re.findall(r'@Test\b',f))==30 and len(re.findall(r'@Test\b',z))==38
assert all(x in f and x in z for x in ['Throwable primary = failures().get(kind);','secondary == primary ? 0 : 1','if (secondary != primary) assertSame(secondary, primary.getSuppressed()[0]);'])
ddl=r/'src/schubert-nk-api/src/main/resources/db/migration/V002__account_session_and_master_tables.sql';decl='CREATE CONSTRAINT TRIGGER ck_entry_audio_links_entry_type_limit\nAFTER INSERT OR UPDATE OF entry_id, link_type ON schubert.entry_audio_links\nDEFERRABLE INITIALLY DEFERRED\nFOR EACH ROW EXECUTE FUNCTION schubert.check_entry_audio_link_limit();';assert decl in ddl.read_text()
v=dict(actualExit=0,oldUnchangedSourceHashes=old,changedSources=[ref(r/x) for x in [m,p,ft,tt]],originalSources=[ref(e/('original-'+Path(x).name+'.txt')) for x in [m,p,ft,tt]],fixedV002=ref(ddl),deferredTriggerDeclaration=decl,fixedCommand=SQL,firstFlushIndex=78,old94SqlPreserved=True,old94SqlCanonicalSha256=hashlib.sha256(json.dumps(before,separators=(',',':')).encode()).hexdigest(),new95SqlCanonicalSha256=hashlib.sha256(json.dumps(after,separators=(',',':')).encode()).hexdigest(),newTests=4,wholeExpected=948,physicalClasses=65,oldOtherMain=43,oldOtherTest=45,unchangedTestDefinitions=880,queryCount=95,selectResultCount=76,ownerCloseCount=17,scalarResults=56,catalogGetters=1251,preparedMaxSetvalBytesUnchanged=True,targetMainBodyTokenUnchanged=True,actualDbExecuted=False,actualDeferredTriggerFired=False,sqlActuallyExecuted=False,authorityActions=0,formalAccepted=False)
(e/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,new=4,whole=948,oldSql=94,newSql=95,results=76,oldSource=88))

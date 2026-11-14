"""Independent V004 row oracle, immutable old93 SQL, and named owner/result counter insertion."""
from pathlib import Path
import json,hashlib,datetime,subprocess,re
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG32922-games940-source-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));main='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/migration/MigrationGamesVerifier.java';test=main.replace('/main/','/test/').replace('.java','Test.java');target=main.replace('MigrationGamesVerifier','MigrationMasterTargetPublisher');tt=target.replace('/main/','/test/').replace('.java','Test.java');old={}
def tokens(t):return [x for x in re.findall(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:[^"\\]|\\.)*"|\w+|[^\s]',t) if not x.startswith(('//','/*'))]
for folder,source in [('main','ec0356001d89aaab6a6e73e500dbba86a3d2dff3'),('test','e0e411860ffa68b897cfe6ed255e285e42315175')]:
 for p in (r/('src/schubert-nk-bootstrap/src/'+folder+'/java/dev/codex/schubert/nk/migration')).glob('*.java'):
  path=str(p.relative_to(r))
  if path in [main,test,target,tt]:continue
  assert sha(p)==hashlib.sha256(subprocess.check_output(['git','show',source+':'+path])).hexdigest(),path;old[path]=sha(p)
assert len(old)==88
beforeMain=subprocess.check_output(['git','show','ec0356001d89aaab6a6e73e500dbba86a3d2dff3:'+target],text=True);currentMain=(r/target).read_text();assert currentMain.count('    new MigrationGamesVerifier().verify(connection);')==1;assert tokens(currentMain.replace('    new MigrationGamesVerifier().verify(connection);\n',''))==tokens(beforeMain)
beforeTest=(e/'original-MigrationMasterTargetPublisherTest.java.txt').read_text();assert hashlib.sha256(beforeTest.encode()).hexdigest()==hashlib.sha256(subprocess.check_output(['git','show','e0e411860ffa68b897cfe6ed255e285e42315175:'+tt])).hexdigest();currentTest=(r/tt).read_text()
GAME_SQL='SELECT id,code,title,display_order,created_at FROM schubert.games ORDER BY id'
def block(t,name):
 a=t.index('  private static final List<String> '+name+' =');z=t.index('\n  private static ',a+4);return t[a:z]
def sqls(t,name):
 return [GAME_SQL if m.group()=='GAMES_SQL' else json.loads(m.group()) for m in re.finditer(r'"(?:[^"\\]|\\.)*"|\bGAMES_SQL\b',block(t,name))]
oldSql=sqls(beforeTest,'SQL');newSql=sqls(currentTest,'SQL');assert len(oldSql)==93 and len(newSql)==94 and newSql==oldSql[:12]+[GAME_SQL]+oldSql[12:];assert sum(x.startswith('SELECT ') for x in oldSql)==75 and sum(x.startswith('SELECT ') for x in newSql)==76
assert sqls(beforeTest,'CATALOG_SQL')==sqls(currentTest,'CATALOG_SQL') and sqls(beforeTest,'CONTENT_SQL')==sqls(currentTest,'CONTENT_SQL')
def ints(t,name):
 a=t.index('  private static final List<Integer> '+name);z=t.index(';',a);part=t[a:z];return [int(x) for x in re.findall(r'\d+',part)]
assert ints(currentTest,'OWNER_START')==sorted([12]+[x if x<12 else x+1 for x in ints(beforeTest,'OWNER_START')])
for name in ['CLOSE_SQL_PREFIX','CLOSE_RESULTS']:
 prior=ints(beforeTest,name);assert ints(currentTest,name)==prior[:2]+[13]+[x+1 for x in prior[2:]],name
for name,value in {'SQL_COUNT':94,'RESULTS':76,'CLOSES':17,'CATALOG_TABLES':12,'MIXED_CATALOG_GETTERS':1119,'SCALARS':56,'CONTENT_COLUMNS':66}.items():assert 'private static final int '+name+' = '+str(value)+';' in currentTest
for source,count in [(test,20),(tt,34)]:assert len(re.findall(r'@Test\b',(r/source).read_text()))==count
rows=[['1','NUKITASHI1','NUKITASHI','1','2026-09-01T00:00:00Z'],['2','NUKITASHI2','NUKITASHI2','2','2026-09-01T00:00:00Z']];ddl=r/'src/schubert-nk-api/src/main/resources/db/migration/V004__indexes_and_initial_data.sql';matches=re.findall(r"\((1|2), '(NUKITASHI[12])', '(NUKITASHI2?)', (1|2), TIMESTAMPTZ '(2026-09-01 00:00:00\+00)'\)",ddl.read_text());parsed=[list(m[:4])+[datetime.datetime.fromisoformat(m[4]).isoformat().replace('+00:00','Z')] for m in matches];assert parsed==rows
assert 'Throwable primary = failures().get(kind);' in currentTest
v=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),previousProductionCoreMain='ec0356001d89aaab6a6e73e500dbba86a3d2dff3',previousUnitSource='e0e411860ffa68b897cfe6ed255e285e42315175',oldUnchangedSourceHashes=old,changedPublisher=ref(r/target),publisherOnlyOneCallAdded=True,changedTargetTest=ref(r/tt),originalTargetTest=ref(e/'original-MigrationMasterTargetPublisherTest.java.txt'),newMain=ref(r/main),newTest=ref(r/test),gameRowsIndependent=rows,gameFixedSql=GAME_SQL,gameTypedGetters=['getInt','getString','getString','getInt','getTimestamp'],wasNullAfterFields=[1,4],fixedV004=ref(ddl),old93SqlPreservedByteAndOrder=True,old93SqlCanonicalSha256=hashlib.sha256(json.dumps(oldSql,separators=(',',':')).encode()).hexdigest(),new94SqlCanonicalSha256=hashlib.sha256(json.dumps(newSql,separators=(',',':')).encode()).hexdigest(),newGameSlot=12,selectResults=dict(before=75,after=76),ownedStatementCloses=dict(before=16,after=17),scalarResultsUnchanged=56,catalogTypedGettersUnchanged=1119,newGameTypedGetters=10,normalNew940Expected=True,newDefinitions=22,oldDefinitions=918,allMain=45,physicalClasses=65,bug='BUG2958',ykt='YKT2487',target034FreshPrimaryPerSelfVariant=True,productTestsExecuted=0,expectedFromProduction=False,privateRootOrHeldClassActions=0,actualDbOrMasterBackupKeyFileVmAuthorityActions=0,newAcceptance=0)
(e/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,new=22,old=918,whole=940,oldSqlPreserved=93,newSql=94,catalog=1119,gameGetters=10))

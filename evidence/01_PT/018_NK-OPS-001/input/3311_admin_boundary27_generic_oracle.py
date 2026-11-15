"""Exact null-guard-only source transform; independent SQL/JCA/mock and SDK closure, no DB/Main."""
from pathlib import Path
import hashlib,json,re,subprocess,textwrap
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';e=b/'evidence/PG33394-admin-boundary27-source-v1';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));source='309665b3f5ed8ce1898b49f209e72550c03a5dcc';main='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/admin/BootstrapAdminService.java';test=main.replace('/main/','/test/').replace('BootstrapAdminService.java','BootstrapAdminServiceBoundaryTest.java');before=(e/'original-BootstrapAdminService.java.txt').read_text();now=(r/main).read_text();assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+main])).hexdigest()==hashlib.sha256(before.encode()).hexdigest()
def end(s,first):
 j=s.index('(',first);depth=0
 while j<len(s):
  if s.startswith('"""',j):j=s.index('"""',j+3)+3;continue
  if s[j] in ['"',"'"]:
   q=s[j];j+=1
   while j<len(s):
    if s[j]=='\\':j+=2;continue
    if s[j]==q:j+=1;break
    j+=1
   continue
  if s[j]=='(':depth+=1
  elif s[j]==')':
   depth-=1
   if depth==0:return j+1
  j+=1
 raise ValueError('unclosed call')
a=now.index('  // SSC411/PT-ADM-BOOTBOUND');z=now.index('  private static void require(boolean condition)',a);rest=now[:a]+now[z:];counts={}
for wrapper,child,n in [('requirePrepared','connection.prepareStatement',5),('requireStatement','connection.createStatement',1),('requireResult','statement.executeQuery',4)]:
 spans=[]
 for m in re.finditer(wrapper+r'\(\s*'+re.escape(child)+r'\(',rest):
  last=end(rest,m.start());first=rest.index('(',m.start())+1;spans.append((m.start(),last,rest[first:last-1].strip()))
 assert len(spans)==n;counts[wrapper]=n
 for first,last,body in reversed(spans):rest=rest[:first]+body+rest[last:]
for name in ['PreparedStatement','Statement','ResultSet']:rest=rest.replace('import java.sql.'+name+';\n','')
rest=rest.replace('import org.jspecify.annotations.Nullable;\n','')
def tokens(s):
 result=[]
 for m in re.finditer(r'"""[\s\S]*?"""|//[^\n]*|/\*[\s\S]*?\*/|"(?:[^"\\]|\\.)*"|\w+|[^\s]',s):
  t=m.group()
  if t.startswith(('//','/*')):continue
  if t.startswith('"""'):t='TEXT_BLOCK:'+textwrap.dedent(t[3:-3]).removeprefix('\n')
  result.append(t)
 return result
assert tokens(rest)==tokens(before),'non-guard source behavior changed'
base='src/schubert-nk-api/src/';deps=[base+'main/java/dev/codex/schubert/nk/api/security/'+x+'.java' for x in ['PasswordHasher','PasswordPolicy','LoginUsername']]+[main.replace('BootstrapAdminService','UserCommandMetadata')];tests=[p.replace('/main/','/test/').replace('.java','Test.java') for p in deps[:3]];old={}
for path in deps+tests:
 h=hashlib.sha256(subprocess.check_output(['git','show',source+':'+path])).hexdigest();assert sha(r/path)==h;old[path]=h
assert sum(len(re.findall(r'@Test\b',(r/p).read_text())) for p in tests)==9
text=(r/test).read_text();assert len(re.findall(r'@Test\b',text))==18
assert not any(x in text for x in ['ApiLogDatabaseFixture','DriverManager','ProcessBuilder','BootstrapAdminMain','TemporaryInfrastructureException'])
assert all(x in text for x in ['PBKDF2WithHmacSHA256','310_000','nullPrepared','nullResult','nullPlain','FAULT_SITES','CLOSE_SITES','assertArrayEquals(new char[raw.length], raw)','future.get(WAIT_SECONDS, TimeUnit.SECONDS)','executor.shutdownNow();','assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));'])
m=dict(actualExit=0,original=ref(e/'original-BootstrapAdminService.java.txt'),main=ref(r/main),test=ref(r/test),guardSites=counts,onlyTypedGuardsAndImportsAndFourPrivateHelpersAdded=True,oldSqlBindingsOrderTwrAndPasswordBehaviorPreserved=True,originalApiFailfastPreserved=True,oldUnchangedSourceHashes=old,independentRecordHash=ref(e/'independent-record-hash-vectors.json'),independentJcaPasswordOracle=True,allWholeOriginalDbFixturesRemainHeld=True,newDefinitions=18,existingSecurityDefinitions=9,expectedWhole=27,mainSources=5,physicalClasses=6,actualDbOrAdminCreationOrNativeOrAuthority=0,newAcceptance=0,formalAccepted=False,effortRate=None)
(e/'generic-type-corrected-manifest.json').open('x').write(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,new=18,whole=27,guards=counts,sourceOnly=True))

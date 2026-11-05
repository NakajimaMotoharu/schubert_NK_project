"""Compile-only positive/seven negative actual SessionAuditWriter null contracts; no Product calls."""
from pathlib import Path
import json,hashlib,subprocess,sys,datetime,re,shutil,importlib.util
import pg9666_pagination_static as runner
ROOT=Path.cwd();RUNS=ROOT.parent/'pgpt-runs/PG379';SLOT=RUNS/'pg19784-session-audit-null-compile-v1';PUBLIC=ROOT/'evidence/01_PT/007_NK-AUT-001/evidence/PG19784-session-audit-null-compile-v1';TC=ROOT.parent/'toolchain';NORMAL=RUNS/'pg19740-f03-index-style-six-main-compile-v1';MAVEN=TC/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn';JAR=TC/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def inputs():
 assert sha(NORMAL/'manifest.safe.json')=='45fa13f0a99583a03cb765e2c0ce05d94bd9d9adeadd89187ff3334c58f31d8b';m=json.loads((NORMAL/'manifest.safe.json').read_text());assert m['actualExit']==0 and m['source']=='28af318d0198fe7432ca6fcd234d3fabbfd10173';assert all(sha(ROOT/n)==h for n,h in m['begin']['inputHashes'].items());assert all(sha(j['path'])==j['sha256'] for j in m['jars'].values());return m

def source(negative):
 header='''package dev.codex.schubert.nk.api.security;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.sql.Connection;
import java.sql.SQLException;
import java.net.InetAddress;
import java.util.Optional;
import java.util.UUID;
import java.time.Instant;
import org.jspecify.annotations.NullMarked;
@NullMarked
final class SessionAuditNonnullCaller {
  static void check(SessionAuditWriter writer, Connection connection,
      Optional<InetAddress> client, UUID messageId, UUID correlationId, Instant at,
      SessionRevocationReason reason, ResultCode result) throws SQLException {
'''
 args=['connection','17','41','client','messageId','correlationId','at','reason','result'];rows=[];lines={}
 for i in ([0,3,4,5,6,7,8] if negative else [-1]):
  call=list(args)
  if i>=0:call[i]='null'
  line='    writer.write('+', '.join(call)+');';rows.append(line);lines[len(header.splitlines())+len(rows)]=args[i] if i>=0 else 'VALID_NONNULL'
 return header+'\n'.join(rows)+'\n  }\n}\n',lines

def pom(main):
 deps=''.join('<dependency><groupId>fixture.pinned</groupId><artifactId>'+name+'</artifactId><version>1</version><scope>system</scope><systemPath>'+path+'</systemPath></dependency>' for name,path in [('api',main['jars']['api']['path']),('protocol',main['jars']['protocol']['path']),('jspecify',str(JAR))])
 return '''<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion><parent><groupId>dev.codex.schubert</groupId><artifactId>schubert-nk</artifactId><version>0.1.0-SNAPSHOT</version><relativePath>../parent-pom.xml</relativePath></parent><artifactId>session-audit-null-contract-canary</artifactId><dependencies>'''+deps+'''</dependencies><build><sourceDirectory>src</sourceDirectory></build></project>\n'''

def run():
 main=inputs();assert not SLOT.exists() and not PUBLIC.exists();SLOT.mkdir();runner.SLOT=SLOT;shutil.copyfile(ROOT/'pom.xml',SLOT/'parent-pom.xml');begin={'source':main['source'],'orchestrationHead':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'driverSha256':sha(__file__),'parentPomSha256':sha(ROOT/'pom.xml'),'normalManifestSha256':sha(NORMAL/'manifest.safe.json'),'jars':{r:j for r,j in main['jars'].items() if r in ['api','protocol']},'jspecifySha256':sha(JAR),'mavenSha256':sha(MAVEN),'atJST':datetime.datetime.now().astimezone().isoformat(),'productCallsExecuted':0,'noApplicationOrRootEntry':True,'mainCompilerConfigurationUnchanged':True};(SLOT/'begin.safe.json').write_text(json.dumps(begin,indent=2)+'\n');stages={};checks={}
 for label,negative in [('positive',False),('negative',True)]:
  d=SLOT/label;(d/'src/dev/codex/schubert/nk/api/security').mkdir(parents=True);text,expected=source(negative);f=d/'src/dev/codex/schubert/nk/api/security/SessionAuditNonnullCaller.java';f.write_text(text);(d/'pom.xml').write_text(pom(main));(d/'expected-lines.json').write_text(json.dumps(expected,indent=2)+'\n');cmd=[str(MAVEN),'-o','--no-transfer-progress','-Dmaven.repo.local='+str(TC/'m2/repository'),'-f',str(d/'pom.xml'),'compile'];t=runner.step(label,cmd,d,timeout=120);stages[label]=t;assert not t['timedOut'];log=(SLOT/(label+'.stdout')).read_text()+(SLOT/(label+'.stderr')).read_text();diagnostics=[]
  for line in log.splitlines():
   if '[NullAway]' in line and 'SessionAuditNonnullCaller.java:' in line:
    match=re.search(r'SessionAuditNonnullCaller\.java:(?:\[(\d+),\d+\]|(\d+):).*?\[NullAway\](.*)',line)
    if match:diagnostics.append({'line':int(match.group(1) or match.group(2)),'message':match.group(3).strip()})
  unique={v['line']:v['message'] for v in diagnostics};ok=(t['actualExit']==(1 if negative else 0) and (set(unique)==set(expected) and all("passing @Nullable parameter 'null' where @NonNull is required" in msg for msg in unique.values()) if negative else not unique and 'BUILD SUCCESS' in log));checks[label]={'expectedExit':1 if negative else 0,'actualExit':t['actualExit'],'expectedSourceLines':expected,'actualUniqueNullAwayDiagnostics':unique,'sourceSha256':sha(f),'pomSha256':sha(d/'pom.xml'),'passed':ok};assert ok,(label,t['actualExit'],unique)
 inputs();m={'actualExit':0,'source':main['source'],'atJST':datetime.datetime.now().astimezone().isoformat(),'checks':checks,'stages':stages,'nonnullPositiveCompile':True,'deliberateJavaNullRejectedAtSevenActualMainContractSites':True,'productTestsExecuted':0,'coverageMeasured':False,'canaryNotCountedAsJUnit':True,'whole451Accepted':False,'files':{str(p.relative_to(SLOT)):sha(p) for p in SLOT.rglob('*') if p.is_file() and '/target/' not in str(p)}};(SLOT/'manifest.safe.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'actualExit':0,'positiveExit':0,'negativeExpectedActualExit':1,'rejectedNullCallSites':7,'productTestsExecuted':0}))

def post():
 inputs();m=json.loads((SLOT/'manifest.safe.json').read_text());b=json.loads((SLOT/'begin.safe.json').read_text());assert m['actualExit']==0 and b['driverSha256']==sha(__file__) and b['parentPomSha256']==sha(ROOT/'pom.xml') and b['mavenSha256']==sha(MAVEN) and b['jspecifySha256']==sha(JAR);assert all(sha(SLOT/n)==h for n,h in m['files'].items())
 for label,negative in [('positive',False),('negative',True)]:
  log=(SLOT/(label+'.stdout')).read_text()+(SLOT/(label+'.stderr')).read_text();found={}
  for line in log.splitlines():
   if 'SessionAuditNonnullCaller.java:' in line and 'error:' in line:assert '[NullAway]' in line
   match=re.search(r'SessionAuditNonnullCaller\.java:(?:\[(\d+),\d+\]|(\d+):).*?\[NullAway\](.*)',line)
   if match:found[int(match.group(1) or match.group(2))]=match.group(3).strip()
  assert found=={int(k):v for k,v in m['checks'][label]['actualUniqueNullAwayDiagnostics'].items()}
  assert all("passing @Nullable parameter 'null' where @NonNull is required" in msg for msg in found.values())
  f=SLOT/label/'src/dev/codex/schubert/nk/api/security/SessionAuditNonnullCaller.java';s,expected=source(negative);assert f.read_text()==s;assert {int(k):v for k,v in m['checks'][label]['expectedSourceLines'].items()}==expected;t=m['stages'][label];assert t['actualExit']==(1 if negative else 0) and t['startUTC']<=t['endUTC'] and not t['timedOut']
 assert not PUBLIC.exists();PUBLIC.mkdir(parents=True)
 for rel in [*m['files'],'manifest.safe.json']:
  dest=PUBLIC/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(SLOT/rel,dest)
 out=dict(m,independentPost=True,originalManifestSha256=sha(SLOT/'manifest.safe.json'),files={str(p.relative_to(PUBLIC)):sha(p) for p in PUBLIC.rglob('*') if p.is_file()});(PUBLIC/'manifest.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'actualExit':0,'manifestSha256':sha(PUBLIC/'manifest.json'),'compileOnlyNotProductPT':True}))

if __name__=='__main__':
 assert len(sys.argv)==2 and sys.argv[1] in ['run','post']
 if sys.argv[1]=='run':run()
 else:post()

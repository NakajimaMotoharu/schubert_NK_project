"""Independent same-source four-case XML/Code/CRC/probe/class-init/side-effect closure."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as E
import zipfile
R=Path(__file__).resolve().parents[4]
RUNS=R.parent/'pgpt-runs/PG379'
U=RUNS/'pg22304-security-factory-four-unit-v1'
META=RUNS/'pg22306-security-factory-passive-metadata-v1'
OUT=R/'evidence/01_PT/015_NK-WEB-001/evidence/PG22308-security-factory-independent-post-v1'
SOURCE='6693e9593936b83bc4a0c07dc1a814213517adfb'
CORE='7aed8eace7c844c2f79f2e39db766faf914890d5'
P='dev/codex/schubert/nk/web/'
TARGET=P+'security/WebSecurityFilterFactory'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def main():
    assert not OUT.exists();m=load(U/'manifest.json');b=m['begin']
    assert b==load(U/'begin.json') and b['source']==SOURCE and b['normalSource']==CORE
    assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,4,0,0,0)
    for path,h in b['inputHashes'].items():
        assert sha(R/path)==h==hashlib.sha256(subprocess.check_output(['git','show',SOURCE+':'+path],cwd=R)).hexdigest()
    terminal=load(U/'unit-exit.safe.json');assert terminal==m['stages']['unit'] and terminal['actualExit']==0 and not terminal['timedOut']
    assert sha(U/'unit.stdout')==terminal['stdoutSha256'] and sha(U/'unit.stderr')==terminal['stderrSha256']
    for stage in m['stages'].values():assert stage['actualExit']==0 and not stage['timedOut']
    cmd=terminal['command'];assert '-Djunit.jupiter.extensions.autodetection.enabled=false' in cmd and '-Djunit.jupiter.execution.parallel.enabled=false' in cmd and cmd.count('--select-class')==1 and '--scan-classpath' not in cmd
    assert b['selected']==['dev.codex.schubert.nk.web.security.WebSecurityFactoryGuardPortTest'] and b['expectedTests']==b['newMethods']==4
    for path,h in b['dependencies'].items():
        assert sha(path)==h
        assert not any(x in path for x in ['/schubert-nk-api/','/schubert-nk-bootstrap/','/schubert-nk-batch/','/postgresql/','/artemis-','/playwright/'])
    normal_path=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';normal=load(normal_path);assert sha(normal_path)==b['normalManifestSha256']=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27' and normal['actualExit']==0 and normal['source']==CORE
    family={TARGET}
    with zipfile.ZipFile(normal['jars']['web']['path']) as jar:
        assert sha(normal['jars']['web']['path'])==normal['jars']['web']['sha256'];names={n[:-6] for n in jar.namelist() if n==TARGET+'.class' or n.startswith(TARGET+'$')};assert names==family==set(m['physical'])
        for name in family:assert hashlib.sha256(jar.read(name+'.class')).hexdigest()==m['physical'][name]==sha(U/'component'/(name+'.class'))
    expected={'missingDependenciesAreRejectedWithoutRequestIdsOrBackendWork','fullyConstructedCompositesAreFreshAndDoNotIssueAnyIdentifier','untrustedPeerGets403AndExactHeadersBeforeSessionFormOrBusinessAccess','ownedRequestIdFailurePropagatesWithoutAuditSessionOrBusinessCallbacks'}
    test_path='src/schubert-nk-web/src/test/java/'+P+'security/WebSecurityFactoryGuardPortTest.java';assert set(re.findall(r'@Test\s+void\s+(\w+)\s*\(', (R/test_path).read_text()))==expected
    cases=[];environment={}
    for path in sorted((U/'xml').glob('TEST-*.xml')):
        tree=E.parse(path).getroot()
        assert not tree.findall('.//failure') and not tree.findall('.//error') and not tree.findall('.//skipped')
        for x in tree.findall('testcase'):
            assert x.get('classname')=='dev.codex.schubert.nk.web.security.WebSecurityFactoryGuardPortTest';cases.append(x.get('name'))
        for x in tree.findall('./properties/property'):
            if x.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']:environment[x.get('name')]=x.get('value')
    assert len(cases)==len(set(cases))==4 and set(cases)=={x+'()' for x in expected}
    tree=E.parse(U/'coverage.xml').getroot();counters={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in tree.findall('counter')}
    assert {x.get('name') for x in tree.findall('.//class')}==family and all(x['missed']==0 for x in counters.values()) and 'BRANCH' not in counters
    assert {k:counters[k]['covered'] for k in ['INSTRUCTION','LINE','METHOD','CLASS']}==dict(INSTRUCTION=163,LINE=26,METHOD=2,CLASS=1)
    ids={name:crc for crc,name in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(U/'classinfo.stdout').read_text())};assert set(ids)==family
    ex=(U/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG22304-SECURITY-FACTORY4"' in ex;probes={}
    for name,total in [(TARGET,27)]:
        found=re.findall(r'^'+ids[name]+r'\s+(\d+) of\s+(\d+)\s+'+re.escape(name)+r'$',ex,re.M);assert found==[(str(total),str(total))];probes[name]=dict(hit=total,total=total,crc64=ids[name])
    meta=load(META/'manifest.json');assert meta['actualExit']==0 and all(x['actualExit']==0 and not x['timedOut'] for x in meta['stages'].values())
    allowed={'dev/codex/schubert/nk/web/session/JdbcWebSessionStore': {'<init>'}, 'dev/codex/schubert/nk/web/session/SpringEncryptedSessionRepository': {'<init>'}, 'dev/codex/schubert/nk/web/session/EncryptedWebSessionRepository': {'<init>'}, 'dev/codex/schubert/nk/web/session/SessionPayloadCodec': {'validateKey', 'close', '<clinit>', '<init>'}, 'dev/codex/schubert/nk/web/session/SessionAttributeCodec': {'<clinit>', '<init>'}, 'dev/codex/schubert/nk/web/session/EncryptedSessionPayload': {'validateVersion'}, 'dev/codex/schubert/nk/web/session/WebSessionFilterFactory': {'<init>', 'create'}, 'dev/codex/schubert/nk/web/security/WebCsrfDeniedHandler': {'<init>'}, 'dev/codex/schubert/nk/web/security/EncryptedSessionSecurityContextRepository': {'<init>'}, 'dev/codex/schubert/nk/web/security/WebInfrastructureFailureFilter': {'<init>'}, 'dev/codex/schubert/nk/web/security/EncryptedSessionRequestCache': {'<init>'}, 'dev/codex/schubert/nk/web/security/MqLoginFailureHandler': {'<init>'}, 'dev/codex/schubert/nk/web/security/CaddyRequestRejectedException': {'<init>'}, 'dev/codex/schubert/nk/web/security/EncryptedSessionCsrfTokenRepository': {'<init>'}, 'dev/codex/schubert/nk/web/security/ClosedServletSecurityFilter': {'<init>'}, 'dev/codex/schubert/nk/web/security/MqAuthenticationProvider': {'<init>'}, 'dev/codex/schubert/nk/web/security/WebErrorDispatchFilter': {'<init>'}, 'dev/codex/schubert/nk/web/security/MqFormLoginFilterFactory$1': {'<init>'}, 'dev/codex/schubert/nk/web/security/WebDisplayContextFilter': {'<init>'}, 'dev/codex/schubert/nk/web/security/FormCsrfTokenRequestHandler': {'<init>'}, 'dev/codex/schubert/nk/web/security/EncryptedSessionAuthenticationStrategy': {'<init>'}, 'dev/codex/schubert/nk/web/security/MqLoginSuccessHandler': {'<init>'}, 'dev/codex/schubert/nk/web/security/InternalErrorDispatchRouter': {'<init>'}, 'dev/codex/schubert/nk/web/security/LoginClientAddress': {'<init>'}, 'dev/codex/schubert/nk/web/security/WebSecurityFilterFactory': {'<init>', 'create'}, 'dev/codex/schubert/nk/web/security/WebCsrfFilterFactory': {'<init>', 'create'}, 'dev/codex/schubert/nk/web/security/WebAccessExceptionFilterFactory': {'<init>', 'create'}, 'dev/codex/schubert/nk/web/security/MqFormLoginFilterFactory': {'<init>', 'create'}, 'dev/codex/schubert/nk/web/security/WebSecurityHeaderFilterFactory': {'<init>', 'create'}, 'dev/codex/schubert/nk/web/security/MqLoginClient': {'<clinit>', '<init>'}, 'dev/codex/schubert/nk/web/security/MqLoginContextProbe': {'<clinit>', '<init>'}, 'dev/codex/schubert/nk/web/security/LoginFormAuthenticationConverter': {'<clinit>', '<init>'}, 'dev/codex/schubert/nk/web/security/WebAccessFailureHandler': {'<clinit>', '<init>'}, 'dev/codex/schubert/nk/web/security/WebAuthorizationFilterFactory': {'readResource', '<init>', 'create'}, 'dev/codex/schubert/nk/web/security/WebSecurityHeaderWriter': {'writeHeaders', '<init>'}, 'dev/codex/schubert/nk/web/security/CaddyClientAddressResolver': {'resolve', '<init>'}, 'dev/codex/schubert/nk/web/security/CaddyTransportContextFilter': {'doFilter', '<init>'}, 'dev/codex/schubert/nk/web/security/WebRequestContext': {'existing', '<clinit>', 'identify'}, 'dev/codex/schubert/nk/web/messaging/JmsRequestReplyClient': {'<clinit>', '<init>'}, 'dev/codex/schubert/nk/web/messaging/ReplyCorrelationRegistry': {'<init>'}, 'dev/codex/schubert/nk/web/logging/WebSecurityAudit$Event': {'<clinit>', '<init>'}, 'dev/codex/schubert/nk/web/logging/WebSecurityAudit$Route': {'<clinit>', '<init>'}, 'dev/codex/schubert/nk/web/logging/WebSecurityAudit': {'version', '<clinit>', 'record', '<init>'}, 'dev/codex/schubert/nk/protocol/layout/LayoutId': {'<clinit>', '<init>'}, 'dev/codex/schubert/nk/protocol/header/ResultCode': {'<clinit>', '<init>'}}
    actual={}
    for module in ['web','protocol']:
        for cl in E.parse(META/(module+'-methods.xml')).getroot().findall('.//class'):
            methods=[dict(name=x.get('name'),desc=x.get('desc')) for x in cl.findall('method') if any(c.get('type')=='INSTRUCTION' and int(c.get('covered'))>0 for c in x.findall('counter'))]
            if methods:actual[cl.get('name')]=methods
    assert {k:{x['name'] for x in v} for k,v in actual.items()}==allowed
    init=set(re.findall(r"Initializing '([^']+)",(U/'class-init.log').read_text()));test_owners=[P+'security/WebSecurityFactoryGuardPortTest',P+'session/SecurityContextOwnerPortFixture']
    extras={n for n in init if n.startswith('dev/codex/schubert/nk/') and n not in actual and not any(n==v or n.startswith(v+'$') for v in test_owners)}
    lambda_counts={}
    for name in extras:
        owner=next((x for x in [P+'logging/WebSecurityAudit',P+'security/MqFormLoginFilterFactory'] if re.fullmatch(re.escape(x)+r'\$\$Lambda\+0x[0-9a-f]{16}',name)),None)
        assert owner is not None
        lambda_counts[owner]=lambda_counts.get(owner,0)+1
    assert lambda_counts=={P+'logging/WebSecurityAudit':3,P+'security/MqFormLoginFilterFactory':2}
    assert not any(n.startswith(('dev/codex/schubert/nk/api/','dev/codex/schubert/nk/bootstrap/','dev/codex/schubert/nk/storage/',P+'bootstrap/WebStartupException','org/postgresql/','org/apache/activemq/','javax/crypto/Cipher','java/net/Socket','sun/nio/ch/SocketChannelImpl')) for n in init)
    stat_path=R/'evidence/01_PT/015_NK-WEB-001/evidence/PG22302-security-factory-four-static-v1/manifest.json';stat=load(stat_path);assert stat['inputHashes']==b['inputHashes'] and stat['rawPmdExit']==4 and stat['pmdRaw']==1 and stat['applicableViolations']==stat['checkstyle']==stat['spotbugs']==stat['processingErrors']==0 and len(stat['individualClassifications'])==1
    assert all(x['classification']=='NOT_APPLICABLE' and x['reason'] for x in stat['individualClassifications']) and sha(stat['staticManifest']['path'])==stat['staticManifest']['sha256']
    OUT.mkdir();files={}
    for base,prefix in [(U,'original-'),(META,'passive-')]:
        for path in [*base.iterdir(),*sorted((base/'xml').glob('TEST-*.xml'))]:
            if path.is_file() and path.name!='jacoco.exec':
                name=prefix+('class-init.stdout' if path.name=='class-init.log' else path.name);assert name not in files;shutil.copyfile(path,OUT/name);files[name]=sha(OUT/name)
    shutil.copyfile(U/'jacoco.exec',OUT/'jacoco.exec');files['jacoco.exec']=sha(OUT/'jacoco.exec')
    (OUT/'executed-main-methods.json').write_text(json.dumps(actual,indent=2)+'\n');files['executed-main-methods.json']=sha(OUT/'executed-main-methods.json')
    result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=SOURCE,productionCoreMain=CORE,tests=4,newUniqueTests=4,requalifiedExistingTests=0,sourceProofNew=1,failures=0,errors=0,skipped=0,productTestsReexecuted=0,inputHashes=b['inputHashes'],physical=m['physical'],classIds=ids,probes=probes,counters=counters,branchStatus='NATURAL_ZERO_BRANCH',branchRatio=None,sourceMethods=sorted(expected),environment=environment,dependencies=b['dependencies'],staticClassification=dict(path=str(stat_path.relative_to(R)),sha256=sha(stat_path)),originalRun=dict(path=str(U/'manifest.json'),sha256=sha(U/'manifest.json')),passiveMetadata=dict(path=str(META/'manifest.json'),sha256=sha(META/'manifest.json')),executedMainClasses=len(actual),supportWholeSourceCredit=0,heapMockSessionOperations=True,realSessionOrCookieIssued=False,realDbCryptoAuthGrantRootNativeNetwork=False,heldFourInitialisations=0,oldExecCombined=False,manualExclusions=[],newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,files=files,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__)),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()))
    (OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=4,newUniqueTests=4,newSourceProofs=1,manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()

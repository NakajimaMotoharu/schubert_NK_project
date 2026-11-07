"""Independent same-source fifteen-case XML/Code/CRC/probe/class-init/side-effect closure."""
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
U=RUNS/'pg22350-session-jdbc-store-fifteen-unit-v1'
META=RUNS/'pg22366-session-jdbc-store-passive-metadata-v1'
OUT=R/'evidence/01_PT/015_NK-WEB-001/evidence/PG22368-jdbc-session-store-independent-post-v1'
SOURCE='d87efbe02857b397d6af100d61ede8a77dcf69ce'
CORE='7aed8eace7c844c2f79f2e39db766faf914890d5'
P='dev/codex/schubert/nk/web/'
TARGET=P+'session/JdbcWebSessionStore'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
def main():
    assert not OUT.exists();m=load(U/'manifest.json');b=m['begin']
    assert b==load(U/'begin.json') and b['source']==SOURCE and b['normalSource']==CORE
    assert (m['actualExit'],m['tests'],m['failures'],m['errors'],m['skipped'])==(0,15,0,0,0)
    for path,h in b['inputHashes'].items():
        assert sha(R/path)==h==hashlib.sha256(subprocess.check_output(['git','show',SOURCE+':'+path],cwd=R)).hexdigest()
    prepared=RUNS/'pg22360-session-jdbc-store-fifteen-compile-v1/manifest.json';assert sha(prepared)==b['compileManifestSha256'];pc=load(prepared);assert pc['actualExit']==0 and pc['inputHashes']==b['inputHashes'] and pc['dependencies']==b['dependencies']
    terminal=load(U/'unit-exit.safe.json');assert terminal==m['stages']['unit'] and terminal['actualExit']==0 and not terminal['timedOut']
    assert sha(U/'unit.stdout')==terminal['stdoutSha256'] and sha(U/'unit.stderr')==terminal['stderrSha256']
    for stage in m['stages'].values():assert stage['actualExit']==0 and not stage['timedOut']
    cmd=terminal['command'];assert '-Djunit.jupiter.extensions.autodetection.enabled=false' in cmd and '-Djunit.jupiter.execution.parallel.enabled=false' in cmd and cmd.count('--select-class')==1 and '--scan-classpath' not in cmd
    assert b['selected']==['dev.codex.schubert.nk.web.session.JdbcSessionStorePortTest'] and b['expectedTests']==b['newMethods']==15
    for path,h in b['dependencies'].items():
        assert sha(path)==h
        assert not any(x in path for x in ['/schubert-nk-api/','/schubert-nk-bootstrap/','/schubert-nk-batch/','/postgresql/','/artemis-','/playwright/'])
    normal_path=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';normal=load(normal_path);assert sha(normal_path)==b['normalManifestSha256']=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27' and normal['actualExit']==0 and normal['source']==CORE
    family={TARGET,TARGET+'$InvalidStoredRow'}
    with zipfile.ZipFile(normal['jars']['web']['path']) as jar:
        assert sha(normal['jars']['web']['path'])==normal['jars']['web']['sha256'];names={n[:-6] for n in jar.namelist() if n==TARGET+'.class' or n.startswith(TARGET+'$')};assert names==family==set(m['physical'])
        for name in family:assert hashlib.sha256(jar.read(name+'.class')).hexdigest()==m['physical'][name]==sha(U/'component'/(name+'.class'))
    expected=set(['publicNullHashVersionAndReplacementBoundsNeverReachJdbc', 'absentFindUsesLiteralSqlAndClosesOnlyOwnedResources', 'presentFindDetachesNineTypedColumnsAndCiphertextBeforeClosing', 'duplicateRowsNeverEscapeAsAValidSessionProjection', 'eachNullOrMalformedDetachedColumnIsInvalidAfterCleanClose', 'malformedRowsWithCleanupFailureNeverGrantInvalidationClassification', 'fatalMalformedCleanupAndGetterCauseKeepOriginalIdentityAfterClose', 'insertHasNineLiteralBindsAndNeverUpdatesOrOwnsTransaction', 'replaceHasExactTenCasBindsAndReturnsOnlyZeroOrOne', 'bothDeleteFormsRetainTheirDistinctIdentityPredicatesAndCountBounds', 'transactionAndMissingJdbcObjectsFailBeforeUnownedEffects', 'everyRequiredJdbcStageFaultIsFixedAndCreatedResourcesStillClose', 'directAndNestedFatalPrioritySurvivesMultipleOwnedCleanupFailures', 'offsetDateTimeRangeFailureIsFixedAfterOwnedStatementClose', 'independentConcurrentConnectionsNeverExchangeBindsOrRows'])
    test_path='src/schubert-nk-web/src/test/java/'+P+'session/JdbcSessionStorePortTest.java';assert set(re.findall(r'@Test\s+void\s+(\w+)\s*\(', (R/test_path).read_text()))==expected
    cases=[];environment={}
    for path in sorted((U/'xml').glob('TEST-*.xml')):
        tree=E.parse(path).getroot()
        assert not tree.findall('.//failure') and not tree.findall('.//error') and not tree.findall('.//skipped')
        for x in tree.findall('testcase'):
            assert x.get('classname')=='dev.codex.schubert.nk.web.session.JdbcSessionStorePortTest';cases.append(x.get('name'))
        for x in tree.findall('./properties/property'):
            if x.get('name') in ['os.name','os.arch','java.version','file.encoding','user.timezone']:environment[x.get('name')]=x.get('value')
    assert len(cases)==len(set(cases))==15 and set(cases)=={x+'()' for x in expected}
    tree=E.parse(U/'coverage.xml').getroot();counters={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in tree.findall('counter')}
    assert {x.get('name') for x in tree.findall('.//class')}==family and all(x['missed']==0 for x in counters.values()) and counters['BRANCH']==dict(covered=30,missed=0)
    assert {k:counters[k]['covered'] for k in ['INSTRUCTION','LINE','METHOD','CLASS']}==dict(INSTRUCTION=511,LINE=123,METHOD=13,CLASS=1)
    ids={name:crc for crc,name in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(U/'classinfo.stdout').read_text())};assert set(ids)==family
    ex=(U/'execinfo.stdout').read_text();assert ex.count('Session "')==1 and 'Session "PG22350-JDBC-SESSION-STORE15"' in ex;probes={}
    for name,hit,total,crc in [(TARGET,160,172,'15f3bcdbf41381d4'),(TARGET+'$InvalidStoredRow',1,1,'125a9ee56a055ad6')]:
        assert ids[name]==crc
        found=re.findall(r'^'+ids[name]+r'\s+(\d+) of\s+(\d+)\s+'+re.escape(name)+r'$',ex,re.M);assert found==[(str(hit),str(total))];probes[name]=dict(hit=hit,total=total,crc64=ids[name])
    marker=tree.find(".//class[@name='"+TARGET+"$InvalidStoredRow']");assert marker is not None and not marker.findall('counter')
    meta=load(META/'manifest.json');assert meta['actualExit']==0 and meta['stage']['actualExit']==0 and not meta['stage']['timedOut']
    allowed={
        P+'session/InvalidSessionRowException':{'<init>'},
        TARGET:{'<init>','changed','column','delete','deleteByHash','findLocked','identity','insert','read','replace','requireHash','required','transaction'},
        P+'session/SessionPayloadIdentity':{'<init>'},
        P+'session/SessionStoreException':{'<init>','preserveFatal'},
        P+'session/WebSessionRow':{'<init>','requireVersion'},
        P+'session/EncryptedSessionPayload':{'<init>','ciphertext','validateVersion'}}
    actual={}
    for cl in E.parse(META/'all-web-methods.xml').getroot().findall('.//class'):
        methods=[dict(name=x.get('name'),desc=x.get('desc')) for x in cl.findall('method') if any(c.get('type')=='INSTRUCTION' and int(c.get('covered'))>0 for c in x.findall('counter'))]
        if methods:actual[cl.get('name')]=methods
    assert {k:{x['name'] for x in v} for k,v in actual.items()}==allowed
    init=set(re.findall(r"Initializing '([^']+)",(U/'class-init.log').read_text()));owner=P+'session/JdbcSessionStorePortTest'
    extras={n for n in init if n.startswith('dev/codex/schubert/nk/') and n not in actual and n!=TARGET+'$InvalidStoredRow' and n!=owner and not n.startswith(owner+'$')}
    assert not extras and TARGET+'$InvalidStoredRow' in init
    assert not any(n.startswith(('dev/codex/schubert/nk/api/','dev/codex/schubert/nk/bootstrap/','dev/codex/schubert/nk/batch/','dev/codex/schubert/nk/storage/','dev/codex/schubert/nk/protocol/',P+'bootstrap/WebStartupException','org/postgresql/','org/apache/activemq/','javax/crypto/Cipher','java/net/Socket','sun/nio/ch/SocketChannelImpl')) for n in init)
    generated=RUNS/'pg22370-jdbc-generated-constructor-metadata-v1';g=load(generated/'manifest.json');assert g['actualExit']==0 and g['productTestsExecuted']==0
    for name,stage in g['stages'].items():
        assert stage['actualExit']==0 and not stage['timedOut']
        for stream in ['stdout','stderr']:assert sha(generated/(name+'.'+stream))==stage[stream+'Sha256']
    marker_text=(generated/'marker.stdout').read_text();assert 'aload_0' in marker_text and 'java/lang/RuntimeException."<init>":()V' in marker_text and 'return' in marker_text
    filter_text=(generated/'standard-filter.stdout').read_text();assert 'PrivateEmptyNoArgConstructorFilter' in filter_text and 'getSuperClassName' in filter_text
    stat_path=R/'evidence/01_PT/015_NK-WEB-001/evidence/PG22362-session-jdbc-store-fifteen-static-v1/manifest.json';stat=load(stat_path);assert stat['inputHashes']==b['inputHashes'] and stat['rawPmdExit']==4 and stat['pmdRaw']==11 and stat['applicableViolations']==stat['checkstyle']==stat['spotbugs']==stat['processingErrors']==0 and len(stat['individualClassifications'])==11
    assert all(x['classification']=='NOT_APPLICABLE' and x['reason'] for x in stat['individualClassifications']) and sha(stat['staticManifest']['path'])==stat['staticManifest']['sha256']
    OUT.mkdir();files={}
    for base,prefix in [(U,'original-'),(META,'passive-'),(generated,'generated-')]:
        for path in [*base.iterdir(),*sorted((base/'xml').glob('TEST-*.xml'))]:
            if path.is_file() and path.name!='jacoco.exec':
                name=prefix+('class-init.stdout' if path.name=='class-init.log' else path.name);assert name not in files;shutil.copyfile(path,OUT/name);files[name]=sha(OUT/name)
    shutil.copyfile(U/'jacoco.exec',OUT/'jacoco.exec');files['jacoco.exec']=sha(OUT/'jacoco.exec')
    (OUT/'executed-main-methods.json').write_text(json.dumps(actual,indent=2)+'\n');files['executed-main-methods.json']=sha(OUT/'executed-main-methods.json')
    result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=SOURCE,productionCoreMain=CORE,tests=15,newUniqueTests=15,requalifiedExistingTests=0,sourceProofNew=1,failures=0,errors=0,skipped=0,productTestsReexecuted=0,inputHashes=b['inputHashes'],physical=m['physical'],classIds=ids,probes=probes,counters=counters,branchStatus='ALL_30_COVERED',branchRatio=1.0,physicalClassCount=2,codeClassCount=1,generatedConstructorStandardFilter=dict(className=TARGET+'$InvalidStoredRow',codeDenominator=0,rawProbes=dict(hit=1,total=1),manualExclusion=False,metadataManifest=dict(path=str(generated/'manifest.json'),sha256=sha(generated/'manifest.json'))),sourceMethods=sorted(expected),environment=environment,dependencies=b['dependencies'],staticClassification=dict(path=str(stat_path.relative_to(R)),sha256=sha(stat_path)),originalRun=dict(path=str(U/'manifest.json'),sha256=sha(U/'manifest.json')),passiveMetadata=dict(path=str(META/'manifest.json'),sha256=sha(META/'manifest.json')),executedMainClasses=len(actual),supportWholeSourceCredit=0,borrowedJdbcInterfacePorts=True,realSqlConstraintsOrLocksQualified=False,realSessionOrCookieIssued=False,realDbCryptoAuthGrantRootNativeNetwork=False,heldFourInitialisations=0,oldExecCombined=False,manualExclusions=[],newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,files=files,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__)),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()))
    (OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=15,newUniqueTests=15,newSourceProofs=1,manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()

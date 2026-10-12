"""Independent exact selected XML/count/source qualification, read-only originals.

BUG1140/YKT908. Never re-executes tests, compiles Main, or operates the VM.
"""
import hashlib
import inspect
import json
import os
from lan_server import copy, run
from pg1625_unsupported_ports_selected import W, SOURCE

METHODS = {
    'dev.codex.schubert.nk.batch.file.UnsupportedBackupVerificationTest:bverifyPort001UnsupportedVerificationRejectsAndClosesWithoutSecretOrRegeneration',
    'dev.codex.schubert.nk.batch.platform.UnsupportedServiceMarkerTest:serviceMarkerPort001MissingRetainedProofNeverGrantsDaemonReadiness',
    'dev.codex.schubert.nk.batch.platform.UnsupportedServiceMarkerTest:serviceMarkerPort002MissingObservationClosePreservesUnknownAndCannotRetire',
    'dev.codex.schubert.nk.batch.file.UnsupportedOriginalProofTest:originalPort001DefaultResumeVerificationNeverProvesOriginalOrRetainedOwnership',
    'dev.codex.schubert.nk.batch.platform.UnsupportedRootIdentityTest:rootIdentityPort001AbsentUidProviderRejectsOtherwiseValidSamePeerService',
    'dev.codex.schubert.nk.batch.file.TransferCleanupFailureTest:transferFailure001OneUnlinkFailureRetainsBytesCountsWarningAndContinuesOtherFile',
}


def qualified_tests(manifest, xml_bytes, expected):
    import xml.etree.ElementTree as ET
    if type(expected) is not set or len(expected) not in (3, 6):
        raise ValueError('fixed independent method oracle required')
    if type(manifest) is not dict or manifest.get('tests') != len(expected) or any(type(manifest.get(k)) is not int or manifest[k] != 0 for k in ['actualExit', 'failures', 'errors', 'skipped', 'aborted', 'notRun', 'javacWarnings', 'classByteMismatch']):
        raise ValueError('actual successful selected count required')
    x = ET.fromstring(xml_bytes)
    if x.tag != 'testsuite' or int(x.attrib['tests']) != len(expected) or any(int(x.attrib[k]) != 0 for k in ['failures', 'errors', 'skipped']):
        raise ValueError('actual independent XML count required')
    cases = x.findall('testcase')
    found = {c.attrib['classname'] + ':' + c.attrib['name'] for c in cases}
    if found != expected or len(cases) != len(found) or any(c.attrib.get('status') in ['skipped', 'not-run'] or any(v.tag not in ['system-out', 'system-err'] for v in c) for c in cases):
        raise ValueError('exact unique passing methods required')
    return len(cases)


SERVER = r'''
import datetime,hashlib,json,os,platform,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
os.umask(0o077)
b=Path('/home/mini/schubert-nk-pgpt');out=b/'runs/PG1627-selected-qualification-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(v):
 if not v:raise ValueError('actual selected source/byte qualification refused')
require(not out.exists());out.mkdir(mode=0o700);results={}
for number,expected in [(1625,{v for v in METHODS if v.split(':')[0].split('.')[-1] in ['UnsupportedBackupVerificationTest','UnsupportedServiceMarkerTest']}),(1626,METHODS)]:
 root=b/'runs'/('PG'+str(number)+'-selected-v1');p=root/'manifest.safe.json'
 require(sha(p)==INPUT[str(number)]);m=json.loads(p.read_bytes());require(m['productionSource']==SOURCE)
 xml=root/'tests.xml';require(sha(xml)==m['xmlSha256'] and sha(root/'selected.exec')==m['execSha256'])
 tests=qualified_tests(m,xml.read_bytes(),expected)
 require(m['fixtureBytesUnchanged']is True and m['formalAccepted']is False and m['vmMutation0']is True)
 for name,h in m['testFiles'].items():require(sha(b/'transfer'/('PG'+str(number)+'-selected-v1')/name)==h)
 for name,h in m['libraries'].items():require(sha(b/'m2/repository'/name)==h)
 source=b/'source-full-PG1532'
 for module,h in m['mainJarHashes'].items():require(sha(source/'src'/('schubert-nk-'+module)/'target'/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar'))==h)
 fixtures=source/'src/schubert-nk-batch/target/test-classes'
 require({str(p.relative_to(fixtures)):sha(p)for p in fixtures.rglob('*.class')}==m['fixtureClassHashes'])
 for module,h in m['coverageXmlHashes'].items():
  p=root/(module+'.xml');require(sha(p)==h)
  cs={c.attrib['type']:{'missed':int(c.attrib['missed']),'covered':int(c.attrib['covered'])}for c in ET.parse(p).getroot().findall('counter')}
  require(all(cs[k]==m['coverage'][module][k] for k in ['LINE','METHOD','CLASS','BRANCH']))
 results[str(number)]={'tests':tests,'FESAbortedNotRun':0,'testSource':m['testSource'],'originalManifestSha256':INPUT[str(number)],'originalXmlSha256':m['xmlSha256'],'originalExecSha256':m['execSha256'],'remaining':{k:sum(v[k]['missed']for v in m['coverage'].values())for k in ['LINE','METHOD','CLASS','BRANCH']},'sourceFixturesLibrariesMainBytesStillUnchanged':True,'vmMutation0':True,'formalAccepted':False}
require(results['1625']['tests']==3 and results['1626']['tests']==6)
version=subprocess.run([str(b/'tools/jdk-25.0.4/bin/java'),'--version'],capture_output=True,text=True,check=True)
require(version.stdout.startswith('openjdk 25.0.4') and not version.stderr)
result={'actualExit':0,'source':SOURCE,'results':results,'readOnlyQualification':True,'oldArtifactsUnchanged':True,'testsNotReissued':True,'vmOperations':0,'formalAccepted':False,'environment':{'osRelease':Path('/etc/os-release').read_text(),'kernel':platform.release(),'architecture':platform.machine(),'javaVersion':version.stdout,'junitJupiter':'5.13.4','junitPlatform':'1.13.4','jacoco':'0.8.15'},'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
print(json.dumps({'actualExit':0,'testsByRun':{n:v['tests']for n,v in results.items()},'manifestSha256':sha(out/'manifest.safe.json'),'remaining':results['1626']['remaining'],'formalAccepted':False,'testsNotReissued':True,'vmOperations':0}))
'''


def main():
    os.umask(0o077);out=W/'pg1627-selected-contract-qualification-v1';out.mkdir(mode=0o700)
    data={str(n):json.loads((W/('pg'+str(n)+'-unsupported-ports-selected-v1')/'manifest.safe.json').read_bytes())['manifestSha256'] for n in (1625,1626)}
    code='INPUT='+repr(data)+'\nSOURCE='+repr(SOURCE)+'\nMETHODS='+repr(METHODS)+'\n'+inspect.getsource(qualified_tests)+'\n'+SERVER
    from pyflakes.api import check
    if check(code,'<actual selected immutable-source qualification>'):raise ValueError('generated static gate refused')
    p=out/'pg1627-qualification.private.py';p.write_text(code)
    exit_code,output=run('test ! -e /home/mini/schubert-nk-pgpt/transfer/pg1627-qualification.private.py && test ! -e /home/mini/schubert-nk-pgpt/runs/PG1627-selected-qualification-v1',timeout=30)
    if exit_code:raise ValueError('new qualification namespace required')
    exit_code,output=copy(p,'/home/mini/schubert-nk-pgpt/transfer/',timeout=60)
    if exit_code:raise ValueError('fixed qualification source transfer refused')
    exit_code,output=run('python3 -B /home/mini/schubert-nk-pgpt/transfer/pg1627-qualification.private.py',timeout=90)
    (out/'server.private.log').write_text(output)
    safe={'actualExit':exit_code,'scriptSha256':hashlib.sha256(code.encode()).hexdigest(),'formalAccepted':False}
    if exit_code==0:safe.update(json.loads(next(v for v in output.splitlines()if v.startswith('{'))))
    with(out/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(safe));return exit_code


if __name__=='__main__':raise SystemExit(main())

"""Actual JUnit BeforeAll IO regression with no secondary cleanup NPE; PT credit0."""
import hashlib
import inspect
import json
import os
from pathlib import Path
import shlex
import subprocess

from pyflakes.api import check

from lan_server import copy, run
from pg3294_protocol_directional_oracle import fixed_jdk, launcher_path, require

ROOT = Path(__file__).resolve().parents[2]
W = Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
SOURCE = 'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25'
SLOT = 'PG3370-db-beforeall-canary-v1'
JAVA = 'tools/quality/vm/050_s1/DbFixtureBeforeAllFailureLauncher.java'
TEST = 'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/ExpiryAuditRepositoryTest.java'

SERVER = r'''
import hashlib,json,os,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
os.umask(0o077);B=Path('/home/mini/schubert-nk-pgpt');S=B/'source-PG3366-related-v2';T=S/'src/schubert-nk-batch/target';I=B/'transfer'/INPUT['slot'];O=B/'runs'/INPUT['slot'];O.mkdir(mode=0o700)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=B/'runs/PG3366-related-v2/manifest.safe.json'
require(sha(manifest)==INPUT['relatedManifestSha256'],'genuine related54 source authority')
v=json.loads(manifest.read_bytes());require(v['actualExit']==v['mavenExit']==0 and v['tests']==54 and v['sourceSnapshot']==INPUT['snapshot']and v['productionSource']==INPUT['source'],'completed same54 source')
require(sha(S/INPUT['test'])==INPUT['testSha256'],'exact actually executed guarded Test source')
source=I/'DbFixtureBeforeAllFailureLauncher.java';require(sha(source)==INPUT['launcherSha256'],'fixed independent diagnostic source')
xml=T/'surefire-reports/TEST-dev.codex.schubert.nk.batch.repository.ExpiryAuditRepositoryTest.xml';require(sha(xml)==INPUT['batchXmlSha256'],'actual same-source original XML classpath')
node=ET.parse(xml).getroot();props={p.get('name'):p.get('value')for p in node.findall('properties/property')};repo=B/'m2/repository';cp=[];libraries=[]
for entry in props['java.class.path'].split(os.pathsep):
 p=Path(entry);require(p.exists()and(p.resolve().is_relative_to(S.resolve())or p.resolve().is_relative_to(repo.resolve())),'only actual current project/repo classpath')
 cp.append(p)
 if p.suffix=='.jar':libraries.append(p)
launcher=launcher_path([p for p in libraries if p.name.startswith('junit-platform-engine-')],repo)
require(launcher.is_file(),'same-version JUnit launcher exists')
if launcher not in cp:cp.append(launcher);libraries.append(launcher)
hashes={str(p):sha(p)for p in libraries};jdk=fixed_jdk([props['java.home']],B);compiled=O/'launcher';compiled.mkdir(mode=0o700);(O/'tmp').mkdir(mode=0o700)
classpath=os.pathsep.join(map(str,cp));env={k:v for k,v in os.environ.items()if k not in['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS']};env['JAVA_HOME']=str(jdk.parent);env['TZ']='Asia/Tokyo';env['SCHUBERT_PG_ROOT']='/nonexistent-pgpt-dblife-noexec'
args=[str(jdk/'javac'),'-Xlint:all','-Werror','-cp',classpath,'-d',str(compiled),str(source)]
with(O/'compile.private.log').open('xb')as log:built=subprocess.run(args,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=60)
require(built.returncode==0,'diagnostic launcher must really compile')
test_class=T/'test-classes/dev/codex/schubert/nk/batch/repository/ExpiryAuditRepositoryTest.class';before=sha(test_class)
args=[str(jdk/'java'),'--enable-native-access=ALL-UNNAMED','-Djava.io.tmpdir='+str(O/'tmp'),'-Dnk.pt.repository='+str(S),'-cp',str(compiled)+os.pathsep+classpath,'DbFixtureBeforeAllFailureLauncher']
with(O/'junit.private.log').open('xb')as log:actual=subprocess.run(args,cwd=S,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=90)
(O/'exit.safe.json').write_text(json.dumps({'compileExit':built.returncode,'launcherExit':actual.returncode}))
require(actual.returncode==0,'actual BeforeAll failure must retain IO without secondary NPE')
text=(O/'junit.private.log').read_text();require('DBLIFE_FOUND=1 STARTED=0 CONTAINER_FAILED=1 BEFOREALL_IO=true SECONDARY_NPE=false PT_CREDIT=0'in text,'exact independent JUnit lifecycle postcondition')
require(sha(test_class)==before and sha(manifest)==INPUT['relatedManifestSha256']and sha(S/INPUT['test'])==INPUT['testSha256']and all(sha(Path(p))==h for p,h in hashes.items()),'all actual Test/Jar/source/library authorities unchanged')
value={'actualExit':0,'productionSource':INPUT['source'],'sourceSnapshot':INPUT['snapshot'],'run':INPUT['slot'],'found':1,'started':0,'containerFailed':1,'beforeAllIoPreserved':True,'secondaryNpe':False,'dbExecutableAbsent':True,'newPtCredit':0,'vmActions':0,'formalUpdated':False,'originalXmlSha256':sha(xml),'actualTestClassSha256':before,'libraryHashes':hashes,'compileLogSha256':sha(O/'compile.private.log'),'junitLogSha256':sha(O/'junit.private.log'),'exitManifestSha256':sha(O/'exit.safe.json')}
(O/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));value['serverManifestSha256']=sha(O/'manifest.safe.json');print(json.dumps(value))
'''


def server_source(data):
    raw = ('INPUT=' + repr(data) + '\n'
           + '\n'.join(inspect.getsource(f) for f in [require, fixed_jdk, launcher_path]) + '\n' + SERVER)
    compile(raw, '<actual BeforeAll cleanup regression>', 'exec')
    require(check(raw, '<actual BeforeAll final namespace>') == 0, 'complete namespace')
    return raw


def main():
    normal = json.loads((W / 'pg3366-maintenance-boundary-group-v2/manifest.safe.json').read_bytes())
    r = normal['result']; require(normal['actualExit'] == r['actualExit'] == 0 and r['tests'] == 54, 'actual normal54 required')
    actual = (ROOT / TEST).read_bytes()
    require(actual == subprocess.check_output(['git', 'show', r['sourceSnapshot'] + ':' + TEST], cwd=ROOT), 'current Test equals actual normal execution')
    data = {'source': SOURCE, 'snapshot': r['sourceSnapshot'], 'slot': SLOT,
            'relatedManifestSha256': r['serverManifestSha256'], 'test': TEST,
            'testSha256': hashlib.sha256(actual).hexdigest(),
            'launcherSha256': hashlib.sha256((ROOT / JAVA).read_bytes()).hexdigest(),
            'batchXmlSha256': r['modules']['batch']['xmlHashes']['TEST-dev.codex.schubert.nk.batch.repository.ExpiryAuditRepositoryTest.xml']}
    raw = server_source(data); os.umask(0o077); out = W / SLOT.lower(); out.mkdir(mode=0o700)
    script = out / 'canary.private.py'; script.write_text(raw)
    base = '/home/mini/schubert-nk-pgpt'
    rc, _ = run('test ! -e ' + base + '/runs/' + SLOT + ' && mkdir -m700 ' + base + '/transfer/' + SLOT, timeout=30)
    require(rc == 0, 'new-only lifecycle diagnostic slot')
    for p in [ROOT / JAVA, script]:
        rc, _ = copy(p, base + '/transfer/' + SLOT + '/', timeout=60); require(rc == 0, 'fixed diagnostic transfer')
    rc, output = run('python3 -B ' + shlex.quote(base + '/transfer/' + SLOT + '/canary.private.py'), timeout=180)
    (out / 'observer.private.log').write_text(output)
    value = {'actualExit': rc, 'payloadSha256': hashlib.sha256(raw.encode()).hexdigest(), 'formalUpdated': False}
    if rc == 0:value['result'] = json.loads([x for x in output.splitlines() if x.startswith('{')][-1])
    (out / 'manifest.safe.json').write_text(json.dumps(value, sort_keys=True))
    print(json.dumps({k:v for k,v in value.items() if k != 'result'}))
    return rc


if __name__ == '__main__':
    raise SystemExit(main())

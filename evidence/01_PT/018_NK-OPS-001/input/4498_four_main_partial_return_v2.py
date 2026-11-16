"""Verify actual successes and unresolved static results, with no fabricated quality acceptance."""
from pathlib import Path
import copy
import datetime
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
import zipfile

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001/evidence'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
cp=b/'PG36844-ssc449-four-main-compile-v1/manifest.json';c=load(cp)
sp=b/'PG36848-ssc449-fresh-sibling-spotbugs-v1/manifest.json';s=load(sp)
pm=b/'PG36846-ssc449-boot-batch-static-v1/manifest.json';p=load(pm)
out=b/'PG36854-ssc449-four-main-partial-return-v2';assert not out.exists()
assert c['actualExit']==s['actualExit']==0 and not c['timedOut']
assert s['compile']==ref(cp) and p['compile']==ref(cp)
snapshot=Path(c['cwd']);counts={k:len(v) for k,v in c['physicalClassHashes'].items()}
assert counts==dict(protocol=175,storage=80,bootstrap=191,batch=646)
for module,expected in c['physicalClassHashes'].items():
    folder=snapshot/('src/schubert-nk-'+module)/'target/classes'
    assert {str(f.relative_to(folder)):sha(f) for f in folder.rglob('*.class')}==expected
assert all(sha(r/name)==h==sha(snapshot/name) for name,h in c['inputHashes'].items())
log=(cp.parent/'maven.stdout.log').read_text()
assert '[INFO] BUILD SUCCESS' in log and 'warning:' not in log and '[ERROR]' not in log
assert log.count('--- compiler:3.14.0:compile (default-compile)')==4
assert not list(snapshot.rglob('surefire-reports'))
ns={'m':'http://maven.apache.org/POM/4.0.0'}
name='src/schubert-nk-bootstrap/pom.xml'
old=ET.fromstring(subprocess.check_output(['git','show','7123bb3bc8319cfadea41e5be38a75e825e5c14c:'+name]))
new=ET.parse(r/name).getroot();deps=new.find('m:dependencies',ns)
added=[d for d in deps if d.findtext('m:artifactId',namespaces=ns)=='checker-qual']
assert len(added)==1 and added[0].findtext('m:version',namespaces=ns)=='3.55.1'
assert added[0].find('m:scope',ns) is None;deps.remove(added[0])
def structural(node):return (node.tag,(node.text or '').strip(),tuple(structural(v) for v in node))
assert structural(old)==structural(new)
before_fix=subprocess.check_output(['git','rev-parse',c['sourceCore']+'^'],text=True).strip()
changed=subprocess.check_output(['git','diff','--name-only',before_fix,c['sourceCore'],'--','src','pom.xml'],text=True).splitlines()
def validate_build_delta(paths):
    if paths!=[name]:raise ValueError('POM-only build-fix delta must not alter Main/Test/Root')
validate_build_delta(changed)
domain_negative=[]
for extra in ['src/schubert-nk-bootstrap/src/main/java/Changed.java',
              'src/schubert-nk-bootstrap/src/test/java/ChangedTest.java','pom.xml']:
    try:validate_build_delta(changed+[extra])
    except ValueError:domain_negative.append(extra)
    else:raise ValueError('changed source-domain was accepted')

protocol_cfg=load(r/'evidence/01_PT/018_NK-OPS-001/input/4425_ssc447_profile.json')
previous_protocol=load(r/protocol_cfg['slots']['prepare']/'manifest.json')
previous_storage=load(b/'PG36820-storage-main-compile-v1/manifest.json')
assert c['physicalClassHashes']['protocol']==previous_protocol['physicalClassHashes']
assert c['physicalClassHashes']['storage']==previous_storage['physicalClassHashes']
def require(value,message):
    if not value:raise ValueError(message)
def validate_sibling(module,value):
    require(value['source']==c['sourceCore'],'source domain')
    path=Path(value['path']);require(path.parent==r.parent/'pgpt-runs/PG379/pg36848-fresh-sibling-static-v1','owned fresh sibling path, not old local m2')
    require(value['physical']==len(c['physicalClassHashes'][module]),'complete sibling count')
    require(sha(path)==value['sha256'],'actual sibling hash')
    with zipfile.ZipFile(path) as archive:
        require(set(archive.namelist())==set(c['physicalClassHashes'][module]),'whole sibling class set')
        require(all(hashlib.sha256(archive.read(n)).hexdigest()==h for n,h in c['physicalClassHashes'][module].items()),'every sibling byte')
for module,v in s['freshSiblingArtifacts'].items():validate_sibling(module,v)
negative=[]
for label,change in [('old-source',{'source':'OLD'}),('old-local-m2',{'path':str(r.parent/'toolchain/m2/repository/dev/codex/schubert/schubert-nk-storage/0.1.0-SNAPSHOT/schubert-nk-storage-0.1.0-SNAPSHOT.jar')}),('incomplete-count',{'physical':79}),('wrong-hash',{'sha256':'0'*64})]:
    wrong=copy.deepcopy(s['freshSiblingArtifacts']['storage']);wrong.update(change)
    try:validate_sibling('storage',wrong)
    except ValueError:negative.append(label)
    else:raise ValueError('invalid sibling accepted')
bugs=[]
for module,expected_count in [('bootstrap',191),('batch',646)]:
    xml=sp.parent/(module+'-spotbugs.xml');root=ET.parse(xml).getroot()
    assert not root.findall('.//MissingClass') and not root.findall('.//Error')
    stats=[n.get('class') for n in root.findall('.//ClassStats')]
    assert len(stats)==len(set(stats))==expected_count
    assert {n.replace('.','/')+'.class' for n in stats}==set(c['physicalClassHashes'][module])
    actual_cp={n.text for n in root.findall('.//Project/AuxClasspathEntry')}
    assert actual_cp==set(s['contexts'][module]['classpath'])
    assert not any('/m2/repository/dev/codex/schubert/' in x for x in actual_cp)
    for item in root.findall('BugInstance'):
        method=item.find('Method');line=item.find('SourceLine')
        bugs.append(dict(module=module,type=item.get('type'),className=method.get('classname'),
           method=method.get('name'),line=line.get('start'),instanceHash=item.get('instanceHash'),disposition='UNRESOLVED_NOT_QUALITY_PASS'))
assert len(bugs)==10
candidate=load(b/'PG36851-ssc449-all-profile-pmd971-candidates-v1/manifest.json')
assert candidate['currentFindings']==971 and candidate['candidateMatched']==309 and candidate['unmatched']==662
out.mkdir();(out/'remaining-spotbugs10.json').open('x').write(json.dumps(bugs,indent=2)+'\n')
result=dict(actualExit=0,source=c['sourceCore'],sourceDomain='CURRENT477_MAIN_COMPILE_AND_RAW_STATIC_PARTIAL_NOT_PRODUCT_QUALITY_PASS',
 terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),compile=ref(cp),
 freshSiblingStatic=ref(sp),pmdRaw=ref(pm),pmdCandidateReview=ref(b/'PG36851-ssc449-all-profile-pmd971-candidates-v1/manifest.json'),
 mainCompileModules=4,mainSources=477,physicalClasses=1092,physicalByModule=counts,
 sameSourceAndByteReuse=dict(protocol175=True,storage80=True,old152And39Replayed=0),
 exactOnlySourceChange='Bootstrap POM direct compile checker-qual3.55.1; Root flags/all business Java/all Test unchanged from the immediately preceding Unit HEAD',
 beforeBuildFixUnit=before_fix,productionMainReferenceCore='7123bb3bc8319cfadea41e5be38a75e825e5c14c',
 changedPathGuardNegatives=domain_negative,originalFailedPost=ref(b/'PG36852-ssc449-four-main-partial-return-v1/manifest.json'),
 siblingGuardNegatives=negative,staleM2ProjectArtifactsUsedByFinalAnalysis=False,
 sdkMissingClasses=0,analysisErrors=0,unresolvedSpotbugs=10,rawPmd=971,
 pmdReuseCandidatesNotFinal=309,pmdRemainingToReview=662,staticQualityAccepted=False,
 mainClassfileRemaining=['API283','Web262'],qa056='PENDING_NO_HELD_CLASSFILE_ACTIONS',
 productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortCompletionRate=None)
(out/'manifest.json').open('x').write(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,source=c['sourceCore'],compiled477=True,physical1092=True,
 siblingGuardNegatives=len(negative),spotbugsUnresolved=10,pmdRaw=971,formalUpdated=False)))

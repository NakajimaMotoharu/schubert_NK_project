"""New-only signed PG548 candidate from frozen same-source PG540; no guest mutation."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as E
from pg548_candidate_contract import SOURCE,OLD_SOURCE,MODULES,artifacts,class_inventory,verify_delta

os.umask(0o077)
R=Path(__file__).resolve().parent;T=R.parents[3]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');P=Path('/home/mini/codex/project1/work/pgpt-vm/private')
OLD=W/'pg495-release-v1';NEXT=W/'pg548-release-v1';FROZEN=W/'pg540-six-host-v1'
assert not NEXT.exists()and not(P/'pg548-manifest-v1.sig').exists()
assert subprocess.check_output(['git','diff',SOURCE,'--',':(glob)src/*/src/main/**','src/deployment','pom.xml',':(glob)src/*/pom.xml'],cwd=T)==b''
assert subprocess.check_output(['git','diff','HEAD','--','src','tools','pom.xml'],cwd=T)==b''
operator=subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip()
gate_raw=(W/'pg540-six-host-v1.safe.json').read_bytes()
assert hashlib.sha256(gate_raw).hexdigest()=='025d76218f019544c1825c23ea63178c3831ace6c5d4233cfd0c4965a8aa4951'
gate=json.loads(gate_raw)
assert gate['source']==SOURCE and gate['actualExit']==gate['FES']==gate['staticIssues']==0 and gate['staticModules']==6 and gate['tests']==3427 and gate['suiteCount']==510 and gate['sourceUnchanged']
raw=(OLD/'RELEASE-MANIFEST.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44'
data=json.loads(raw);assert data['source']['commit']==OLD_SOURCE and data['versions']['schema']=='028'
old_entries=artifacts(data['artifacts'])
for path,a in old_entries.items():
    p=OLD/path;assert p.is_file()and not p.is_symlink()and p.stat().st_size==a['size']and hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
old_classes={};new_classes={};jar_hashes={}
for module in MODULES:
    row=next(v for v in gate['modules']if v['module']==module)
    p=FROZEN/module/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar')
    assert hashlib.sha256(p.read_bytes()).hexdigest()==row['projectJarSha256']
    assert row['FES']==0 and not E.parse(FROZEN/module/'spotbugsXml.xml').getroot().findall('.//BugInstance')
    assert hashlib.sha256((FROZEN/module/'site/jacoco/jacoco.xml').read_bytes()).hexdigest()==row['coverageXmlSha256']
    for xml in row['XML']:
        q=FROZEN/module/'surefire-reports'/('TEST-'+xml['class']+'.xml')
        assert hashlib.sha256(q.read_bytes()).hexdigest()==xml['xmlSha256']
        test=E.parse(q).getroot();assert int(test.attrib['tests'])==xml['tests']and all(int(test.get(k,'0'))==0 for k in('failures','errors','skipped'))
    old_classes[module]=class_inventory(W/'pg495-host'/module/p.name);new_classes[module]=class_inventory(p)
    jar_hashes[module]=row['projectJarSha256']
assert verify_delta(old_classes,new_classes)==1600
assert {a['path']for a in data['artifacts']}=={p.relative_to(OLD).as_posix()for p in OLD.rglob('*')if p.is_file()}-{'RELEASE-MANIFEST.json','SHA256SUMS'}
started=datetime.datetime.now(datetime.timezone.utc).isoformat();shutil.copytree(OLD,NEXT)
version=NEXT/'VERSION';version.write_bytes(version.read_bytes().replace(b'PG495',b'PG548').replace(OLD_SOURCE.encode(),SOURCE.encode()))
main={'api/api.jar':'api','web/web.jar':'web','operations/batch.jar':'batch'}
for row in data['artifacts']:
    path=row['path'];p=NEXT/path;module=main.get(path)
    if module is None:module=next((m for m in('protocol','storage','bootstrap','api')if p.name=='schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar'),None)
    if module is not None:
        q=FROZEN/module/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar');shutil.copyfile(q,p)
        assert hashlib.sha256(p.read_bytes()).hexdigest()==jar_hashes[module]
    row['size']=p.stat().st_size;row['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
# old_entries shares data row objects; independently re-read the authenticated old manifest.
old_entries=artifacts(json.loads(raw)['artifacts'])
changed=[v['path']for v in data['artifacts']if v['sha256']!=old_entries[v['path']]['sha256']]
allowed={'VERSION',*main}
allowed.update(v['path']for v in data['artifacts']if Path(v['path']).name in{'schubert-nk-'+m+'-0.1.0-SNAPSHOT.jar'for m in('protocol','storage','bootstrap','api')})
assert set(changed)<=allowed and 'operations/batch.jar'in changed
assert len(list((NEXT/'db/migration').glob('*.sql')))==28 and len(data['migrations'])==29
for path in set(old_entries)-allowed:assert (NEXT/path).read_bytes()==(OLD/path).read_bytes()
data['release']='0.1.0-PG548';data['source']['commit']=SOURCE
manifest=json.dumps(data,ensure_ascii=False,indent=2).encode()+b'\n';(NEXT/'RELEASE-MANIFEST.json').write_bytes(manifest)
digest=hashlib.sha256(manifest).hexdigest()
sums={a['path']:a['sha256']for a in data['artifacts']};sums['RELEASE-MANIFEST.json']=digest
(NEXT/'SHA256SUMS').write_bytes(''.join(sums[n]+'  '+n+'\n'for n in sorted(sums)).encode())
assert set(artifacts(data['artifacts']))==set(old_entries)
def exact():
    assert {p.relative_to(NEXT).as_posix()for p in NEXT.rglob('*')if p.is_file()}==set(old_entries)|{'RELEASE-MANIFEST.json','SHA256SUMS'}
    for a in data['artifacts']:
        p=NEXT/a['path'];assert not p.is_symlink()and p.stat().st_size==a['size']and hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
exact();sig=P/'pg548-manifest-v1.sig';log=W/'pg548-sign-v1.private.log';assert not log.exists()
with log.open('xb')as f:
    subprocess.run(['openssl','pkeyutl','-sign','-rawin','-inkey',str(P/'pg381-release-signing.pem'),'-in',str(NEXT/'RELEASE-MANIFEST.json'),'-out',str(sig)],stdout=f,stderr=f,check=True)
    subprocess.run(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey',str(P/'pg381-release-pin.der'),'-in',str(NEXT/'RELEASE-MANIFEST.json'),'-sigfile',str(sig)],stdout=f,stderr=f,check=True)
exact();assert sig.stat().st_size==64
safe={'run':'PG548-candidate-build-v1','operatorSource':operator,'productionSource':SOURCE,'priorSource':OLD_SOURCE,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hostBuildRun':gate['run'],'hostBuildSafeSha256':hashlib.sha256(gate_raw).hexdigest(),'tests':3427,'suites':510,'FES':0,'staticModules':6,'staticIssues':0,'frozenJarHashes':jar_hashes,'classInventoryCount':1600,'onlyChangedClass':'batch:dev/codex/schubert/nk/batch/file/MorningCompletionEvidence.class','release':'0.1.0-PG548','manifestSha256':digest,'artifacts':187,'sql':28,'history':29,'changedArtifactPaths':changed,'signatureVerified':True,'signatureSha256':hashlib.sha256(sig.read_bytes()).hexdigest(),'privateLogSha256':hashlib.sha256(log.read_bytes()).hexdigest(),'helperSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'guestMutations0':True,'formalAccepted':False}
with(W/'pg548-candidate-build-v1.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({'run':safe['run'],'productionSource':SOURCE,'artifacts':187,'signatureVerified':True,'guestMutations0':True,'manifestSha256':digest}))

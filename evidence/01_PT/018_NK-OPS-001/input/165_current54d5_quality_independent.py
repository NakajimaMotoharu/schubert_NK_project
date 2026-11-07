"""Independently check saved static architecture output; do not replay any JVM."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
import zipfile
r = Path.cwd()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
p = r/'evidence/01_PT/018_NK-OPS-001/evidence/PG22042-current54d5-static-architecture-v1/manifest.json'
assert sha(p) == '3a15cd0da2b585d39d85561a7d3a5d4eb9f4879852784d1348d3b101611f6ee1'
m = json.loads(p.read_text())
assert m['actualExit'] == m['stage']['actualExit'] == 0 and not m['stage']['timedOut']
assert m['productInitializations'] == m['productTests'] == m['oldCanaryExecutions'] == 0
assert not m['wholeF02Accepted'] and not m['whole451Accepted'] and m['effortRate'] is None
for n,h in m['files'].items():
    assert sha(p.parent/n) == h
normalp = Path(m['begin']['normalManifest']['path'])
assert sha(normalp) == m['begin']['normalManifest']['sha256'] == 'e91d5a386618f7fc8f3fe374be760451b57bfc4d620de40a76771800d4845640'
normal = json.loads(normalp.read_text())
assert normal['source'] == m['productionMainSource'] == '54d5c19da0117db49edff7b5ae46207fdee59acc'
counts = {'protocol':176,'storage':80,'bootstrap':117,'api':468,'web':359,'batch':645}
assert counts == m['moduleClassCounts'] and m['physicalClasses'] == sum(counts.values()) == 1845
physical = {}
for module,jar in normal['jars'].items():
    jp = Path(jar['path'])
    assert sha(jp) == jar['sha256'] and str(jp) not in m['begin']['observerRuntimeClasspath']
    assert module+'='+str(jp) in m['stage']['command']
    with zipfile.ZipFile(jp) as archive:
        entries = [n for n in archive.namelist() if n.endswith('.class') and not n.startswith('META-INF/')]
        assert len(entries) == counts[module]
        for n in entries:
            physical[module+':'+n] = hashlib.sha256(archive.read(n)).hexdigest()
assert physical == normal['normalPhysicalClassHashes']
stdout = (p.parent/'architecture.stdout').read_text()
assert 'FINDING\t' not in stdout
assert dict((k,int(v)) for k,v in re.findall(r'^RULE\t(\w+)\t(\d+)$',stdout,re.M)) == m['ruleFindings'] == {
    'MODULE_EDGES':0,'FRAMEWORK_FENCES':0,'CONTROLLER_BOUNDARY':0,'REPOSITORY_DIRECTION':0,'INTERNAL_OWNER':0}
assert 'ARCHUNIT\t1.4.2\t1845\t1845' in stdout
assert dict((k,int(v)) for k,v in re.findall(r'^MODULE\t(\w+)\t(\d+)$',stdout,re.M)) == counts
assert 'INSPECTED\t83610\t59194' in stdout
init = re.findall(r"Initializing '([^']+)",(p.parent/'class-init.stdout').read_text())
assert not any(n.startswith('dev/codex/schubert/nk/') for n in init)

lp=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG22040-current54d5-lineage-style-v1/manifest.json'
assert sha(lp)=='1ac9a761197e533fd921baf35cd1679a927dbbc38ab4b86cc26d05d39a33b68c'
lineage=json.loads(lp.read_text());assert lineage['actualExit']==0 and lineage['source']==normal['source'] and lineage['artifactCount']==1068 and lineage['javaSources']==972 and lineage['unchanged']==1067 and lineage['added']==lineage['removed']==0
for n,h in lineage['files'].items():assert sha(lp.parent/n)==h
artifacts=json.loads((lp.parent/'artifacts.json').read_text());oldp=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21942-current56720-static-artifact-lineage-v1/manifest.json';oldm=json.loads(oldp.read_text());oldap=oldp.parent/'artifacts.json';assert sha(oldap)==oldm['files']['artifacts.json'];prior={a['path']:a for a in json.loads(oldap.read_text())};assert len(prior)==len(artifacts)==1068
names=sorted(prior);held={'SnapshotKeyCloseWitness.java','pg9892_snapshot_key_close_witness.py','RootFailedStartRecoveryTest.java','RootFailedStartPairRecoveryTest.java'};assert all(Path(n).name not in held for n in names)
raw=subprocess.check_output(['git','cat-file','--batch'],input=''.join(normal['source']+':'+n+'\n' for n in names).encode());pos=0;hashes={}
for n in names:
 end=raw.index(b'\n',pos);oid,kind,length=raw[pos:end].decode().split();assert kind=='blob';pos=end+1;blob=raw[pos:pos+int(length)];pos+=int(length);assert raw[pos:pos+1]==b'\n';pos+=1;h=hashlib.sha256(blob).hexdigest();assert h==sha(r/n);hashes[n]=h
assert pos==len(raw)
changed=[]
for a in artifacts:
 n=a['path'];old=prior[n];assert a['sha256']==hashes[n] and a['owner']==old['owner'] and a['costOwner']==old['costOwner'] and a['additionalBudgetPp']==old['additionalBudgetPp']==0
 if a['sha256']!=old['sha256']:changed.append(n)
assert changed==['src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebRuntimeStop.java']
occurrences=json.loads((lp.parent/'current-occurrences.json').read_text());assert len(occurrences)==len({a['originalId'] for a in occurrences})==1494
oldstyle=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21976-current56720-main-style-projection-v1';oldrows={a['originalId']:a for a in json.loads((oldstyle/'current-occurrences.json').read_text())};unchanged=0;rebound=0
for a in occurrences:
 n=a['finding']['path'];assert a['currentSourceSha256']==hashes[n] and a['actualViolation'] is False and a['classification']=='CONTEXTUAL_NONAPPLICABLE'
 if n==changed[0]:
  rebound+=1;assert a['finding']['attributes']['beginline']=='35' and a['finding']['attributes']['rule']=='AvoidCatchingGenericException'
 else:assert a==oldrows[a['originalId']];unchanged+=1
assert rebound==1 and unchanged==1493 and lineage['rawPmdOccurrences']==1494 and lineage['applicableViolations']==lineage['unclassified']==0

head = subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+str(Path(__file__).relative_to(r))])).hexdigest() == sha(Path(__file__))
out = r/'evidence/01_PT/018_NK-OPS-001/evidence/PG22044-current54d5-lineage-quality-independent-v1'
assert not out.exists()
out.mkdir()
value = dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),checkerSource=head,
    checkerSha256=sha(Path(__file__)),observerSource=m['observerSource'],productionMainSource=m['productionMainSource'],
    original=dict(path=str(p.relative_to(r)),sha256=sha(p)),physicalClasses=1845,moduleCounts=counts,
    rules=m['ruleFindings'],dependencies=83610,codeAccesses=59194,productInitializations=0,
    productTestsExecuted=0,oldCanaryReplayed=False,productJarInToolRuntimeClasspath=False,
    wholeF02Accepted=False,whole451Accepted=False,newSourceProofs=0,newAcceptance=0,effortRate=None)
value.update(currentLineage=dict(path=str(lp.relative_to(r)),sha256=sha(lp)),artifacts=1068,javaSources=972,modifiedMain=1,unchangedArtifacts=1067,styleOccurrences=1494,reboundOccurrences=1,unchangedOccurrences=1493,applicableViolations=0,unclassified=0,wholeG13Accepted=False,wholeF03Accepted=False)
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,physicalClasses=1845,findings=0,
                     manifestSha256=sha(out/'manifest.json'))))

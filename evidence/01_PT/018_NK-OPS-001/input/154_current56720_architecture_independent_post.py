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
p = r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21964-current56720-static-architecture-v1/manifest.json'
assert sha(p) == '8a0b87dca21558926433cbb5aefdedd95d02ffe8ce494bee8fa14971d40211a1'
m = json.loads(p.read_text())
assert m['actualExit'] == m['stage']['actualExit'] == 0 and not m['stage']['timedOut']
assert m['productInitializations'] == m['productTests'] == m['oldCanaryExecutions'] == 0
assert not m['wholeF02Accepted'] and not m['whole451Accepted'] and m['effortRate'] is None
for n,h in m['files'].items():
    assert sha(p.parent/n) == h
normalp = Path(m['begin']['normalManifest']['path'])
assert sha(normalp) == m['begin']['normalManifest']['sha256'] == 'e925b4c24e0eff9e70f7b3fad0b595d80e90f1a444c87329215d6e4b3d5d8d1f'
normal = json.loads(normalp.read_text())
assert normal['source'] == m['productionMainSource'] == '56720d75714f60d7e31da59c3da8c02baf05de52'
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
head = subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+str(Path(__file__).relative_to(r))])).hexdigest() == sha(Path(__file__))
out = r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21966-current56720-f02-independent-post-v1'
assert not out.exists()
out.mkdir()
value = dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),checkerSource=head,
    checkerSha256=sha(Path(__file__)),observerSource=m['observerSource'],productionMainSource=m['productionMainSource'],
    original=dict(path=str(p.relative_to(r)),sha256=sha(p)),physicalClasses=1845,moduleCounts=counts,
    rules=m['ruleFindings'],dependencies=83610,codeAccesses=59194,productInitializations=0,
    productTestsExecuted=0,oldCanaryReplayed=False,productJarInToolRuntimeClasspath=False,
    wholeF02Accepted=False,whole451Accepted=False,newSourceProofs=0,newAcceptance=0,effortRate=None)
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,physicalClasses=1845,findings=0,
                     manifestSha256=sha(out/'manifest.json'))))

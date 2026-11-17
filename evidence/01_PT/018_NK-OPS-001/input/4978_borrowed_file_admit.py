"""Bind the scoped compilation, public and nonpublic ABI, and exact PMD dispositions."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess

R = Path.cwd()
B = Path('evidence/01_PT/018_NK-OPS-001/evidence')
before = B/'PG38188-borrowed-file-before-prepare-v1/manifest.json'
after = B/'PG38190-borrowed-file-after-prepare-v1/manifest.json'
static = B/'PG38192-borrowed-file-static-v1/manifest.json'
out = B/'PG38194-borrowed-file-admission-v1'
W = R.parent/'pgpt-runs/PG379'
work = W/'pg38190-borrowed-file-after-v1'
previous_work = W/'pg38188-borrowed-file-before-v1'

def load(path):
    return json.loads(path.read_bytes())

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def ref(path):
    return {'path':str(path),'sha256':sha(path)}

p,old,s = load(after),load(before),load(static)
assert p['actualExit']==old['actualExit']==s['actualExit']==0
assert p['inputHashes']==s['inputHashes']
assert all(sha(n)==h for n,h in p['inputHashes'].items())
assert not s['processingErrors'] and s['checkstyleFindings']==0
assert all(s['spotbugs'][k]==0 for k in ('bugs','missing','errors'))
assert all(v['actualExit']==(4 if k=='pmd' else 0) for k,v in s['stages'].items())
assert set(s['spotbugs']['classStats']) == {n.removesuffix('.class').replace('/','.') for n in p['mainClassHashes']}
assert set(old['physicalClassHashes']) == set(p['physicalClassHashes'])
changed=[n for n,h in p['physicalClassHashes'].items() if old['physicalClassHashes'][n]!=h]
assert {Path(n).stem for n in changed} == {'MediaBodyStreamer','TransferContentVerifier'}
jdk=R.parent/'toolchain/jdk-25.0.4/bin/javap'
abi={}
for n in sorted(p['mainClassHashes']):
    qualified_name=n.removesuffix('.class').replace('/','.')
    forms=[subprocess.check_output([str(jdk),'-p','-cp',str(w/'component'),qualified_name],timeout=15) for w in (previous_work,work)]
    assert forms[0]==forms[1], n
    abi[n]=hashlib.sha256(forms[0]).hexdigest()
screen = {
 ('MediaBodyStreamerTest.java','CloseResource',line): reason
 for line,reason in [
 ('33','Output owns only ByteArrayOutputStream; observably borrowed along the real FileChannel path.'),
 ('44','Synthetic Channel owns an array and a close flag; no acquired OS resource.'),
 ('46','Output owns only ByteArrayOutputStream; short-read path observes the supplied sink remains open.'),
 ('67','Fault-injection Channel owns only synthetic bytes and a close flag.'),
 ('69','Output fault sink owns only a ByteArrayOutputStream; close is a fixture observation.'),
 ('81','Synthetic read-failure Channel holds no external resource; source closure belongs to caller.'),
 ('84','Partial-output fixture holds only an array buffer; close is a fixture observation.')]
}
screen['MediaBodyStreamerTest.java','AssignmentInOperand','136']='Existing fault fixture uses short-circuit order to leave read count unchanged for the immediate read fault; the counter here selects fail-after-one with no external effect.'
for cl in ('MediaBodyStreamer','TransferContentVerifier'):
    screen[cl+'NamespaceContractTest.java','AvoidAccessibilityAlteration','37']='Single local static namespace constructor; restores original accessibility in finally and checks the restored flag.'
rows=[]
for row in s['rawFindings']:
    key = (Path(row['path']).name, row['rule'], row['line'])
    rows.append(dict(row,disposition='NOT_APPLICABLE_TO_FIXTURE_OR_INVARIANT',reason=screen.pop(key),sourceSha256=sha(row['path'])))
assert len(rows)==10 and not screen
assert set(Path(n).name for n in p['dependencies']) == {'jspecify-1.0.1.jar','junit-platform-console-standalone-1.13.4.jar',Path(load(R/p['currentProto']['path'])['jar']['path']).name}
assert p['expectedTests']==7 and len(p['expectedCases'])==7
core=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
assert all(hashlib.sha256(subprocess.check_output(['git','show',f'{core}:{n}'])).hexdigest()==h for n,h in p['inputHashes'].items())
test_hashes = {n:p['inputHashes'][n] for n in p['apiTestSources']}
norm=dict(actualExit=0,sourceCore=core,work=str(work),mainInputHashes={n:h for n,h in p['inputHashes'].items() if n not in test_hashes},
          testSourceHashes=test_hashes,physicalClassHashes=p['physicalClassHashes'],testPhysicalHashes=p['testClassHashes'],
          toolDependencyHashes=p['dependencies'],classpath=os.pathsep.join([str(work/'component'),*p['dependencies']]),
          expectedTests=7,expectedCases=p['expectedCases'])
out.mkdir()
def save(name,data):
    (out/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
save('normalized-prepare.json',norm)
save('strict-classpath-allowlist.safe.json',dict(actualExit=0,exactDependencyHashes=p['dependencies']))
save('manifest.json',dict(actualExit=0,terminalAtUTC=dt.datetime.now(dt.timezone.utc).isoformat(),source=core,applicable=0,unclassified=0,
     pmdDispositions=rows,allVisibilityAbi=abi,physicalDelta=changed,sharedBytesUnchanged=178,
     declaredTargets=sorted(n.removesuffix('.class') for n in changed),
     prepare=ref(out/'normalized-prepare.json'),before=ref(before),after=ref(after),static=ref(static),
     actualProductTests=0,newAcceptance=0))
print(json.dumps(dict(actualExit=0,abi=len(abi),changed=changed,pmdDispositions=len(rows))))

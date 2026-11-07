"""Read-only validation of saved tool regression and original receipt bindings; no tool replay."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
r=Path.cwd();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_text());root=r/'evidence/01_PT/018_NK-OPS-001/evidence'
p=root/'PG22060-proof-lookup-provenance-tool-regression-v1/manifest.json';m=load(p);assert sha(p)=='f6e95f6fa4a67ab472451b936924cb93b3132975833b50cd0dc60d32db1d4ca2' and m['actualExit']==m['stage']['actualExit']==0 and m['toolTests']==33 and m['newToolTests']==8 and m['productTestsExecuted']==0
for n,h in m['files'].items():assert sha(p.parent/n)==h
for n,h in m['inputHashes'].items():assert sha(r/n)==h==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+n])).hexdigest()
text=(p.parent/'unit.stderr').read_text();assert 'Ran 33 tests' in text and text.rstrip().endswith('OK')
assert len(re.findall(r'^test_\w+ \(test_pgpt_program_proof_lookup.ProgramProofLookupTest.test_\w+\).* ok$',text,re.M))==33
matrix=load(p.parent/'cross-schema.json');assert len(matrix['rows'])==3 and len(matrix['excluded'])==1
for row in matrix['rows']:
 ref=r/row['path'];assert sha(ref)==row['manifestSha256'];original=load(ref);c=row['discovery'];v=original['inputProvenance'];assert c['evidenceSchema']=='SINGLE_TARGET_INPUT_PROVENANCE' and c['mainPath']==v['mainInputPath']==row['main'] and c['mainSha256']==v['mainInputHash'] and c['currentMainByteEqual']==(sha(r/row['main'])==v['mainInputHash'])
 assert original['physicalClosureComplete'] is True and len(original['physical'])==1 and original['counterExclusions']==[] and original['oldExecCombined'] is False
 target,h=next(iter(original['physical'].items()));assert c['declaredNormalClassSha256']==h and c['declaredCrc64']==original['crc'][0][0] and target==original['crc'][0][1]
 assert c['fourCounters']==original['counters'] and c['originalExit']==original['actualExit'] and c['source']==original['source'] and c['tests']==original['tests']
 assert not c['permissionInferred'] and not c['acceptanceInferred'] and not c['wholeSourceQualificationInferred']
red=root/'PG22056-proof-lookup-provenance-original-red-v1/manifest.json';rm=load(red);assert rm['actualExit']==rm['stage']['actualExit']==1 and rm['productTests']==0
for n,h in rm['files'].items():assert sha(red.parent/n)==h
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();driver=str(Path(__file__).relative_to(r));assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+driver])).hexdigest()==sha(__file__)
out=root/'PG22062-proof-lookup-provenance-independent-post-v1';assert not out.exists();out.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),checkerSource=head,checkerSha256=sha(__file__),toolSource=m['source'],regression=dict(path=str(p.relative_to(r)),sha256=sha(p)),red=dict(path=str(red.relative_to(r)),sha256=sha(red)),toolTests=33,newToolTests=8,provenanceRows=3,excludedUnsplit=1,productTestsExecuted=0,regressionReplayed=False,newProductTests=0,newSourceProofs=0,newAcceptance=0,formalUpdated=False,effortRate=None)
(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,toolTests=33,productTests=0,manifestSha256=sha(out/'manifest.json'))))

"""Validate tool-only regression and declared old receipt fields; no tests are replayed."""
from pathlib import Path
import ast, datetime, hashlib, json, re, subprocess
r=Path.cwd();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
p=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21806-source-units-schema-metadata-v1/manifest.json';assert sha(p)=='045af06ffb3f0cf8363cab0df8b43d618339d4f25a9ff0e8f742d2ba145b78d6';m=load(p)
assert m['actualExit']==0 and m['totalMetadataTests']==25 and m['newMetadataTests']==10 and m['necessaryExistingMetadataRegression']==15 and m['productTests']==0
for n,h in m['files'].items():assert sha(p.parent/n)==h
for n,h in m['begin']['inputHashes'].items():
 assert sha(r/n)==h
 assert hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+n])).hexdigest()==h
for stage in m['stages'].values():assert stage['actualExit']==0 and not stage['timedOut']
cmd=m['stages']['metadata']['command'];assert cmd==['env','PYTHONPATH=tools/quality','python3','-B','-m','unittest','discover','-s','tools/quality/tests','-p','test_pgpt_program_proof_lookup.py','-v']
stderr=(p.parent/'metadata.stderr').read_text();assert re.search(r'^Ran 25 tests in ',stderr,re.M) and stderr.rstrip().endswith('OK')
tree=ast.parse((r/'tools/quality/tests/test_pgpt_program_proof_lookup.py').read_text());methods={x.name for x in ast.walk(tree) if isinstance(x,ast.FunctionDef) and x.name.startswith('test_')};assert len(methods)==25 and len([n for n in methods if n.startswith('test_source_units_')])==10
reported=set(re.findall(r'^(test_\w+) \(test_pgpt_program_proof_lookup\.ProgramProofLookupTest\.test_\w+\) \.\.\. ok$',stderr,re.M));assert reported==methods
red=load(p.parent/'tdd-red-manifest.safe.json');assert red['actualExit']==1 and red['expectedUnimplementedTddRed'] and red['newMetadataTests']==10
oldp=r/m['originalReceipt']['path'];assert sha(oldp)==m['originalReceipt']['sha256'];old=load(oldp)
assert old['actualExit']==old['failures']==old['errors']==old['skipped']==0 and old['tests']==14
normalp=Path(m['normalManifest']['path']);assert sha(normalp)==m['normalManifest']['sha256'];normal=load(normalp)
assert len(m['qualifiedMetadataCandidates'])==2
for row in m['qualifiedMetadataCandidates']:
 item=row['proof'];main=item['mainPath'];cls=main.split('/src/main/java/',1)[1][:-5];unit=old['sourceUnits'][cls]
 assert item['evidenceSchema']=='SOURCE_UNITS_SOURCE_PINS' and item['originalExit']==old['actualExit'] and item['tests']==old['tests']
 assert item['source']==old['source'] and item['mainSha256']==old['sourcePins'][main]==normal['begin']['inputHashes'][main]==sha(r/main)
 assert item['fourCounters']==unit['counters'] and all(unit['counters'][k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH'])
 assert item['declaredNormalClassSha256']==unit['normalClassSha256']==normal['normalPhysicalClassHashes'][row['module']+':'+cls+'.class']
 assert item['declaredCrc64']==unit['crc64'] and item['currentMainByteEqual'] and row['physicalCurrentNormalBound']
 assert item['counterScope']=='NAMED_CLASS_OR_METHOD_SUBSET_COUNTERS' and not item['wholeSourceQualificationInferred'] and not item['acceptanceInferred'] and not item['permissionInferred']
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+str(Path(__file__).relative_to(r))])).hexdigest()==sha(Path(__file__))
out=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21808-source-units-schema-independent-post-v1';assert not out.exists();out.mkdir()
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),checkerSource=head,checkerSha256=sha(Path(__file__)),source=m['source'],original=dict(path=str(p.relative_to(r)),sha256=sha(p)),metadataTests=25,newMetadataTests=10,necessaryExistingMetadataRegression=15,originalProductCasesReferenced=14,currentNormalTargetClassBindings=2,dependencyClosureCurrentQualificationTransferred=False,oldSourceExecTransferred=False,productTests=0,newMethods=0,newSourceProofs=0,newAcceptance=0,wholeG13Accepted=False,effortRate=None)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,metadataTests=25,currentNormalClassBindings=2,productTests=0,manifestSha256=sha(out/'manifest.json'))))

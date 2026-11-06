"""Metadata-only regression and two explicit historical receipt bindings."""
from pathlib import Path
import datetime
import hashlib
import json
import platform
import re
import shutil
import subprocess
import pg9666_pagination_static as c
from pgpt_program_proof_lookup import candidate

r=Path.cwd();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
tool=r/'tools/quality/pgpt_program_proof_lookup.py';tests=r/'tools/quality/tests/test_pgpt_program_proof_lookup.py';spec=r/'evidence/01_PT/018_NK-OPS-001/3614_公開sourceUnits証拠形式の限定対応仕様.md'
for p in [tool,tests,spec,Path(__file__)]:
 assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+str(p.relative_to(r))])).hexdigest()==sha(p)
slot=r.parent/'pgpt-runs/PG379/pg21806-source-units-schema-metadata-v1';assert not slot.exists();slot.mkdir();c.SLOT=slot
begin=dict(source=head,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),inputHashes={str(p.relative_to(r)):sha(p) for p in [tool,tests,spec,Path(__file__)]},os=platform.platform(),pythonVersion=platform.python_version(),productTests=0,metadataTests=25)
(slot/'begin.json').write_text(json.dumps(begin,indent=2)+'\n')
stages={}
stages['python-static']=c.step('python-static',['env','PYTHONPATH=/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime','python3','-B','-m','pyflakes',str(tool),str(tests),str(Path(__file__))],r,timeout=30)
assert stages['python-static']['actualExit']==0 and not stages['python-static']['timedOut']
stages['metadata']=c.step('metadata',['env','PYTHONPATH=tools/quality','python3','-B','-m','unittest','discover','-s','tools/quality/tests','-p','test_pgpt_program_proof_lookup.py','-v'],r,timeout=30)
assert stages['metadata']['actualExit']==0 and not stages['metadata']['timedOut']
stderr=(slot/'metadata.stderr').read_text();assert re.search(r'^Ran 25 tests in ',stderr,re.M) and stderr.rstrip().endswith('OK')
assert 'skipped=' not in stderr and 'expected failures' not in stderr and 'unexpected successes' not in stderr
red=r.parent/'pgpt-runs/PG379/pg21802-source-units-metadata-red-v1';redm=load(red/'manifest.safe.json');assert redm['actualExit']==1 and redm['expectedUnimplementedTddRed'] and redm['newMetadataTests']==10
original=r/'evidence/01_PT/005_NK-MSG-001/evidence/provisional/PG18644-jms-uuid-normal-post-v1/manifest.json';assert sha(original)=='5cafcb6a2f2d4a8b61dcc33a614de0338b5e4dc99980da102a10a1f0ea8d3ba6'
old=load(original);assert old['actualExit']==old['failures']==old['errors']==old['skipped']==0 and old['tests']==14
normalp=r.parent/'pgpt-runs/PG379/pg20990-outbox-required-six-main-compile-v1/manifest.safe.json';assert sha(normalp)=='1db34d8f2ccee9fc90244bea86c3e446be0c0e010c66516a1e25c92df3426618';normal=load(normalp);assert normal['actualExit']==0
proofs=[]
for cls,unit in old['sourceUnits'].items():
 simple=cls.rsplit('/',1)[-1];module='api' if simple=='JmsMessageGuard' else 'web';assert simple in ['JmsMessageGuard','JmsReplyDecoder']
 main='src/schubert-nk-'+module+'/src/main/java/'+cls+'.java';current=normal['begin']['inputHashes'][main];assert sha(r/main)==current==old['sourcePins'][main]
 item=candidate(old,simple,current);assert item is not None and item['evidenceSchema']=='SOURCE_UNITS_SOURCE_PINS' and item['currentMainByteEqual'] and item['originalExit']==0 and item['allFourMissedZero']
 assert item['declaredNormalClassSha256']==normal['normalPhysicalClassHashes'][module+':'+cls+'.class']==unit['normalClassSha256']
 assert item['declaredCrc64']==unit['crc64'] and not item['wholeSourceQualificationInferred'] and not item['acceptanceInferred'] and not item['permissionInferred']
 proofs.append(dict(className=simple,module=module,physicalCurrentNormalBound=True,proof=item))
assert len(proofs)==2
for n,h in begin['inputHashes'].items():assert sha(r/n)==h
out=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21806-source-units-schema-metadata-v1';assert not out.exists();out.mkdir();files={}
for p in slot.iterdir():
 if p.is_file():shutil.copyfile(p,out/p.name);files[p.name]=sha(out/p.name)
for name in ['manifest.safe.json','metadata-red.stdout','metadata-red.stderr']:
 p=red/name;target='tdd-red-'+name;shutil.copyfile(p,out/target);files[target]=sha(out/target)
m=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=head,begin=begin,stages=stages,files=files,newMetadataTests=10,necessaryExistingMetadataRegression=15,totalMetadataTests=25,productTests=0,
 originalReceipt=dict(path=str(original.relative_to(r)),sha256=sha(original),source=old['source'],originalTests=14),normalManifest=dict(path=str(normalp),sha256=sha(normalp)),qualifiedMetadataCandidates=proofs,
 lookupFullScanRepeated=False,oldProductTestsReplayed=False,newMethods=0,newSourceProofs=0,newAcceptance=0,wholeSourceQualificationInferred=False,wholeG13Accepted=False,formalUpdated=False,effortRate=None)
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,metadataTests=25,newMetadataTests=10,currentNormalBoundCandidates=2,productTests=0,manifestSha256=sha(out/'manifest.json'))))

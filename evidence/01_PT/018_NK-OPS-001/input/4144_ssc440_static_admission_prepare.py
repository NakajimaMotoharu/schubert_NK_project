"""Rebind individually justified original findings to exact current source and manifests."""
from pathlib import Path
import hashlib,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=hashlib.sha256(p.read_bytes()).hexdigest());cfg=ld(i/'4134_ssc440_namespace39_profile.json');anchors=[]
for name in ['2290_resource26_static_admission.json','2299_env10_static_admission.json']:
 for original in ld(i/name)['sourceAnchors']:
  a=dict(original)
  if a['path'].endswith('/ResourceScope.java'):
   old=a['sourceLine'];a['sourceLine']=old-1
  assert (r/a['path']).read_text().splitlines()[a['sourceLine']-1].strip()==a['sourceAnchor']
  anchors.append(a)
p='src/schubert-nk-storage/src/test/java/dev/codex/schubert/nk/storage/StoragePublicContractTest.java';lines=(r/p).read_text().splitlines();positions=[n+1 for n,v in enumerate(lines) if v.strip()=='copy[0] = null;'];assert len(positions)==1
anchors.append(dict(path=p,rule='NullAssignment',sourceAnchor='copy[0] = null;',sourceLine=positions[0],occurrences=1,message='Assigning an Object to null is a code smell.  Consider refactoring.',rawMultiplicity=1,reason='The closed enum values defensive-array contract deliberately nulls only the returned copy, then independently asserts the next values() call retains all original constants. No production state or nullable API is introduced.',disposition='NOT_APPLICABLE'))
sp=r/cfg['slots']['static']/'manifest.json';st=ld(sp);actual=[v for v in st['rawFindings'] if v['path'].endswith('/StoragePublicContractTest.java')];assert len(actual)==1 and actual[0]['rule']=='NullAssignment';anchors[-1]['message']=actual[0]['message']
v=dict(schema='PGPT_STATIC_ADMISSION_V1',profile=cfg['id'],prepare=ref(r/cfg['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=anchors)
(i/'4135_ssc440_namespace39_static_admission.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(anchors=len(anchors),raw=len(st['rawFindings']))))

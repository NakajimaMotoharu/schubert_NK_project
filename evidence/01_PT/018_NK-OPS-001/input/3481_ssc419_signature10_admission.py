"""Reconcile exact ten static sites, preserving triple identity multiplicity and bounded pool reasons."""
from pathlib import Path
from collections import Counter
import hashlib,json
import pgpt_closed_host_stages as stage
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
c=ld(b/'input/3480_ssc419_signature10_profile.json');m=ld(r/c['slots']['static']/'manifest.json');old=ld(b/'input/2221_signature9_static_admission.json')
assert m['spotbugs']['bugs']==m['spotbugs']['missing']==m['spotbugs']['errors']==0 and m['processingErrors']==[]
legacy={(x['rule'],x['sourceAnchor']):x for x in old['sourceAnchors']};assert len(legacy)==7
rows=Counter((v['path'],v['rule'],v['line'],v['message']) for v in m['rawFindings']);anchors=[]
for (path,rule,line,message),multiplicity in rows.items():
 p=Path(path);assert p.name=='ReleaseSignatureVerifierTest.java';rel=str(p.relative_to(r));line=int(line);anchor=p.read_text().splitlines()[line-1].strip();key=(rule,anchor)
 if key in legacy:
  oldrow=legacy[key];assert multiplicity==oldrow.get('rawMultiplicity',1);reason=oldrow['reason']
 else:
  assert rule=='AvoidLiteralsInIfCondition' and line==239 and anchor=='if (attempts.size() == 1) throw failure;' and multiplicity==1
  reason='SIGN010 uses exactly two independent phases: first call throws the synthetic public RuntimeException, second succeeds. Fixed1 selects that known fault phase, not a configurable business threshold. Clone erasure, retained input/pinned value, distinct next allocations and exact2 calls are independently asserted.'
 row=dict(path=rel,rule=rule,message=message,sourceAnchor=anchor,sourceLine=line,occurrences=1,reason=reason,disposition='NOT_APPLICABLE')
 if multiplicity!=1:row['rawMultiplicity']=multiplicity
 anchors.append(row)
classified=stage.classify_source_findings(c['mainSources']+[x['path'] for x in c['testSources']],anchors,m['rawFindings'],lambda p:(r/p).read_text());assert len(classified)==len(m['rawFindings'])==10
p=b/'input/3482_ssc419_signature10_admission.json';p.open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=c['id'],prepare=ref(r/c['slots']['prepare']/'manifest.json'),static=ref(r/c['slots']['static']/'manifest.json'),sourceAnchors=anchors),ensure_ascii=False,indent=2)+'\n');print('raw10 individually classified, tripleidentity retained, applicable0/unclassified0')

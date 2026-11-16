"""Classify exact current findings using prior per-site reviews on unchanged source and two new fixtures."""
from pathlib import Path
from collections import Counter
import hashlib,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));c=ld(b/'input/4425_ssc447_profile.json');sp=r/c['slots']['static']/'manifest.json';st=ld(sp);assert st['actualExit']==0 and st['checkstyleFindings']==0 and not st['processingErrors'] and all(st['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
priors=[b/'input'/name for name in ['4349_ssc445_static_admission.json','4366_wire_metadata_static_admission.json','4391_protocol_aggregate_static_admission_v4.json']];old=[a for p in priors for a in ld(p)['sourceAnchors']];counts=Counter((x['path'],x['rule'],int(x['line']),x['message']) for x in st['rawFindings']);anchors=[]
for (path,rule,line,message),multiplicity in counts.items():
 rel=str(Path(path).relative_to(r));text=(r/rel).read_text().splitlines()[line-1].strip();matches=[a for a in old if a['path']==rel and a['rule']==rule and a['sourceAnchor']==text and ('message' not in a or a['message']==message)]
 assert matches,dict(path=rel,rule=rule,line=line,source=text)
 anchors.append(dict(path=rel,rule=rule,sourceAnchor=text,occurrences=1,sourceLine=line,rawMultiplicity=multiplicity,message=message,reason=matches[0]['reason'],disposition='NOT_APPLICABLE'))
v=dict(schema='PGPT_STATIC_ADMISSION_V1',profile=c['id'],prepare=ref(r/c['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=anchors,originalSourceApplicabilityReviews=[ref(p) for p in priors]);(b/'input/4435_ssc447_static_admission.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,rawFindings=len(st['rawFindings']),exactAnchors=len(anchors),applicable=0,unclassified=0,spotbugs=0,checkstyle=0)))

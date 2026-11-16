"""Bind the same concrete per-site reviews for the necessary nineteen-case caller closure."""
from pathlib import Path
import hashlib,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda x:json.loads(x.read_text());sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest();ref=lambda x:dict(path=str(x.relative_to(r)),sha256=sha(x));c=ld(b/'input/4313_named_record_collection_profile_v3.json');st=r/c['slots']['static']/'manifest.json';s=ld(st);assert not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']);reviews={}
for file in ['4287_ssc444_protocol_static_admission.json','4310_named_record_static_admission_v2.json']:
 for a in ld(b/'input'/file)['sourceAnchors']:reviews[(a['path'],a['rule'],a['sourceAnchor'])]=a
anchors={}
for f in s['rawFindings']:
 path=Path(f['path']);name=str(path.relative_to(r));line=path.read_text().splitlines()[int(f['line'])-1].strip();key=(name,f['rule'],line);assert key in reviews,key;a=dict(reviews[key]);assert path.read_text().count(line)==a['occurrences'];anchors[key]=a
v=dict(schema='PGPT_STATIC_ADMISSION_V1',profile=c['id'],prepare=ref(r/c['slots']['prepare']/'manifest.json'),static=ref(st),sourceAnchors=list(anchors.values()));(b/'input/4319_named_record_static_admission_v3.json').open('x').write(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,rawFindings=len(s['rawFindings']),concreteAnchors=len(anchors),unclassified=0)))

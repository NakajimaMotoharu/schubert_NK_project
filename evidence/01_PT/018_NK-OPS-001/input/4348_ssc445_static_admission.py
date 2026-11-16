"""Bind concrete unchanged reviews and the new bounded-reader fixture; no suppression or defaulting."""
from pathlib import Path
import hashlib,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda x:json.loads(x.read_text());sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest();ref=lambda x:dict(path=str(x.relative_to(r)),sha256=sha(x));c=ld(b/'input/4344_ssc445_registry_profile_v2.json');st=r/c['slots']['static']/'manifest.json';s=ld(st);assert not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']);reviews={}
for file in ['4287_ssc444_protocol_static_admission.json','4319_named_record_static_admission_v3.json','4328_protocol_metadata_static_admission.json']:
 for a in ld(b/'input'/file)['sourceAnchors']:reviews[(a['path'],a['rule'],a['sourceAnchor'])]=a
anchors={}
for f in s['rawFindings']:
 path=Path(f['path']);name=str(path.relative_to(r));line=path.read_text().splitlines()[int(f['line'])-1].strip();key=(name,f['rule'],line)
 if key in reviews:
  a=dict(reviews[key]);assert path.read_text().count(line)==a['occurrences'];anchors[key]=a;continue
 assert path.name=='PayloadTypeCatalogStateContractTest.java' and f['rule'] in ['CloseResource','DoNotUseThreads'],(name,f['rule'],line)
 reason='This standalone JUnit fixture owns exactly two bounded readers, not a J2EE container. Ready/start awaits and both futures have10second bounds; finally releases the start latch, calls shutdownNow and asserts awaitTermination(10seconds), including failed assertions/interruptions. All input rows are immutable independent SS323 literals, each worker owns its result list, and no backend/service/VM thread is started.'
 anchors[key]=dict(path=name,rule=f['rule'],sourceAnchor=line,occurrences=path.read_text().count(line),reason=reason,disposition='NOT_APPLICABLE')
assert len(s['rawFindings'])==42;v=dict(schema='PGPT_STATIC_ADMISSION_V1',profile=c['id'],prepare=ref(r/c['slots']['prepare']/'manifest.json'),static=ref(st),sourceAnchors=list(anchors.values()));(b/'input/4349_ssc445_static_admission.json').open('x').write(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,rawFindings=len(s['rawFindings']),concreteAnchors=len(anchors),unclassified=0,suppressionAdded=0)))

"""Reuse unchanged concrete dispositions and review the three additive collection-contract sites."""
from pathlib import Path
import hashlib,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));c=ld(b/'input/4297_named_record_collection_profile.json');st=r/c['slots']['static']/'manifest.json';s=ld(st);old=ld(b/'input/4287_ssc444_protocol_static_admission.json');assert len(s['rawFindings'])==12 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']);anchors=[]
for f in s['rawFindings']:
 path=Path(f['path']);name=str(path.relative_to(r));line=path.read_text().splitlines()[int(f['line'])-1].strip();rule=f['rule'];matches=[x for x in old['sourceAnchors'] if (x['path'],x['rule'],x['sourceAnchor'])==(name,rule,line)]
 if matches:
  assert len(matches)==1;a=dict(matches[0]);assert path.read_text().count(line)==a['occurrences'];anchors.append(a);continue
 assert path.name=='IndependentNamedFieldOracle.java'
 if rule=='UseConcurrentHashMap':
  assert line in ['Map<Object, String> recordIndex = new HashMap<>();','Map<Object, String> wireIndex = new HashMap<>();'];reason='This collection is local to one verifyType invocation and has no concurrent access or publication. Its stable keys are the independently constructed immutable record or the completed independent wire-field map; fixed lookup text tests actual equality/hash composition. The input map is no longer mutated.'
 elif rule=='EqualsNull':
  assert line=='org.junit.jupiter.api.Assertions.assertFalse(constructed.equals(null));';reason='This direct negative assertion verifies the public immutable record equality contract rejects null, rather than production null comparison logic. All69 named types are checked.'
 else:raise AssertionError((rule,line))
 anchors.append(dict(path=name,rule=rule,sourceAnchor=line,occurrences=1,reason=reason,disposition='NOT_APPLICABLE'))
a=dict(schema='PGPT_STATIC_ADMISSION_V1',profile=c['id'],prepare=ref(r/c['slots']['prepare']/'manifest.json'),static=ref(st),sourceAnchors=anchors);(b/'input/4302_named_record_static_admission.json').open('x').write(json.dumps(a,indent=2)+'\n');print(json.dumps(dict(actualExit=0,rawFindings=12,unclassified=0,suppressionAdded=0)))

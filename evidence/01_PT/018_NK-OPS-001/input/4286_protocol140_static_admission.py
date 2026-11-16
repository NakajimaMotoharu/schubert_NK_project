"""Record concrete applicability for the twenty-eight inspected static findings; no suppression."""
from pathlib import Path
import hashlib,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));c=ld(b/'input/4284_ssc444_protocol_profile_v3.json');st=r/c['slots']['static']/'manifest.json';s=ld(st);assert len(s['rawFindings'])==28 and not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors']);anchors={}
for finding in s['rawFindings']:
 path=Path(finding['path']);name=str(path.relative_to(r));rule=finding['rule'];line=path.read_text().splitlines()[int(finding['line'])-1].strip();key=(name,rule,line)
 if rule=='UseConcurrentHashMap':
  if path.name=='PayloadCodec.java':reason='decodeArea creates a method-local LinkedHashMap, fills it only within that invocation and constructs a FieldValueSet from it. Independent concurrent codec callers have separate maps; this is no concurrently shared mutable map.'
  elif path.name=='IndependentNamedFieldOracle.java':reason='This map is confined to the one verifyAll/verifyType call stack and holds independent expected field/accessor metadata or a copy for one optional-value negative case. The helper does not publish it or submit it to worker threads.'
  else:reason='This map is confined to one ordinary immutable-value test invocation, never shared or published. Actual key lookup by independently equal values is the assertion; there is no concurrent map access.'
 elif rule=='CompareObjectsWithEquals':
  assert path.name in ['FailedJmsIsolationException.java','UnconfirmedJmsRollbackException.java'];reason='The references are Throwables. Identity intentionally determines whether the same Throwable would be attached to itself via suppressed failures; equals() could be overridden and must not replace the identity contract. Whole original tests verify distinct and identical causes.'
 elif rule=='NullAssignment':
  if path.name=='WireEnumCatalogValueContractTest.java':reason='Caller-owned array copy is deliberately corrupted to verify a second copy and subsequent values() retain the catalog, without changing production/shared state.'
  else:reason='A test-local Object[] copy deliberately replaces exactly one public constructor argument with null to verify the independent nonnull invariant. This is negative fixture input, not a production null assignment.'
 elif rule=='EqualsNull':reason='This explicit assertFalse verifies each public immutable path value implements Object.equals(null) as false. It is the required independent negative contract under test.'
 elif rule in ['CloseResource','DoNotUseThreads']:
  assert path.name in ['PayloadGoldenVectorTest.java','WebLogActionContractTest.java'];reason='This standalone JUnit fixture owns its bounded pool (8 golden-vector workers or 2 QA054 category workers), not a J2EE container. All await/get operations have 10-second bounds; finally releases the start latch where present, shutdownNow(), and asserts awaitTermination(10s). The pool is closed on every path, including failed assertions.'
 else:raise AssertionError((name,rule))
 if key not in anchors:anchors[key]=dict(path=name,rule=rule,sourceAnchor=line,occurrences=path.read_text().count(line),reason=reason,disposition='NOT_APPLICABLE')
a=dict(schema='PGPT_STATIC_ADMISSION_V1',profile=c['id'],prepare=ref(r/c['slots']['prepare']/'manifest.json'),static=ref(st),sourceAnchors=list(anchors.values()));(b/'input/4287_ssc444_protocol_static_admission.json').open('x').write(json.dumps(a,indent=2)+'\n');print(json.dumps(dict(actualExit=0,rawFindings=28,concreteAnchors=len(anchors),unclassified=0,suppressionAdded=0)))

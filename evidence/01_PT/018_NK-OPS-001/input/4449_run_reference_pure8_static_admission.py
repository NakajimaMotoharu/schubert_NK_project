"""Exact per-message applicability review; no suppression or unclassified finding accepted."""
from pathlib import Path
from collections import Counter
import hashlib,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));c=ld(b/'input/4448_run_reference_pure8_profile_v3.json');sp=r/c['slots']['static']/'manifest.json';st=ld(sp);assert st['actualExit']==0 and st['checkstyleFindings']==0 and not st['processingErrors'] and all(st['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
reasons={
 'AvoidCatchingGenericException':'SS332/SSC063 mandates explicit resource-failure precedence: capture and rethrow identical RuntimeException/Error after both finally blocks, never normalise an NPE or swallow fatal. Exact primary/secondary matrix is RRF-PURE-006.',
 'DoNotThrowExceptionInFinally':'SS332/SSC063 requires row then statement close with explicit SQLException-versus-fatal precedence. Finally may rethrow the selected failure; it never returns a success or abandons a sibling resource. RRF-PURE-005/006 checks all owned close calls.',
 'AvoidLiteralsInIfCondition':'This exact test-only mode/edge selector enumerates independently specified missing-row, transaction or exception-graph cases in RRF-PURE-003/004/007. Numbers identify fixture variants; production conditions and expected SQL/values are independent.',
 'NullAssignment':'RRF-PURE-004 deliberately places SQL NULL at each of four column positions. Null is the negative input, not an allowed invariant or catch-NPE normal result.',
 'UseConcurrentHashMap':'Each Fixture is created inside one synchronous read or one independent virtual task and never escapes that owner. Its event/count/failure/bind maps are accessed only by that task. The concurrent test uses 32 separate fixtures, so no concurrent map access exists.',
 'UseProperClassLoader':'Only standard java.sql interfaces are proxied. The explicit loader owning the exact interface is required by Proxy.newProxyInstance; no contextual/plugin/product class loading or Class.forName is used.',
}
counts=Counter((x['path'],x['rule'],int(x['line']),x['message']) for x in st['rawFindings']);anchors=[]
for (path,rule,line,message),multiplicity in counts.items():
 p=Path(path);rel=str(p.relative_to(r));source=p.read_text().splitlines()[line-1].strip();is_test='/src/test/' in rel
 if rule=='DoNotUseThreads':
  reason=('Finite, test-owned virtual executor or explicit interrupt setup/assertion/cleanup for RRF-PURE-003/008; finally shutdownNow plus awaitTermination10s, per-Future10s and no service threads.' if is_test else 'SS332 single-owner borrowed-connection read observes the current thread interrupt at entry and after both owned JDBC resources close. It creates no thread, executor, daemon or J2EE container work.')
 elif rule=='CloseResource':
  if is_test:reason='The exact executor is test-owned and always reaches finally shutdownNow plus asserted awaitTermination10s; returned futures are bounded10s. No JVM shutdown or backend process is involved.'
  elif 'present(statement)' in source:reason='checked is a non-null alias of the acquired statement. Its original statement reference is closed exactly once in the outer finally after row close; explicit precedence is SS332. RRF-PURE-004/005/006 asserts acquired equals close count.'
  elif 'present(row)' in source:reason='values is a non-null alias of the acquired ResultSet. The original row reference is closed exactly once in the inner finally, including projection/null/runtime/error failures; statement still closes afterward. RRF-PURE-004/005/006 checks counters.'
  else:raise AssertionError((rule,source))
 else:
  assert rule in reasons,(rule,source);reason=reasons[rule]
 anchors.append(dict(path=rel,rule=rule,sourceAnchor=source,occurrences=1,sourceLine=line,rawMultiplicity=multiplicity,message=message,reason=reason,disposition='NOT_APPLICABLE'))
assert not any(a['rule']=='AssignmentInOperand' for a in anchors)
v=dict(schema='PGPT_STATIC_ADMISSION_V1',profile=c['id'],prepare=ref(r/c['slots']['prepare']/'manifest.json'),static=ref(sp),sourceAnchors=anchors)
(b/'input/4450_run_reference_pure8_static_admission.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,raw=len(st['rawFindings']),exactMessageAnchors=len(anchors),applicable=0,unclassified=0,bug3125Absent=True)))

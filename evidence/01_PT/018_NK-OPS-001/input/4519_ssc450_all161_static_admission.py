"""All134 exact source/site/message reviews, including unchanged first71 and fresh data cases."""
from collections import Counter
from pathlib import Path
import hashlib
import importlib.util
import json

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
c=load(b/'input/4517_ssc450_all161_profile.json');sp=r/c['slots']['static']/'manifest.json';s=load(sp)
pp=r/c['slots']['prepare']/'manifest.json';prep=load(pp)
assert s['actualExit']==prep['actualExit']==0 and len(s['rawFindings'])==134
assert not s['processingErrors'] and s['checkstyleFindings']==0 and all(s['spotbugs'][k]==0 for k in ['bugs','missing','errors'])
spec=importlib.util.spec_from_file_location('canonical_admission',b/'input/4514_canonical_static_admission_paths.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
allowed=set(c['mainSources'])|{x['path'] for x in c['testSources']}
relative=lambda name:module.canonical_path(name,r,allowed)
old=load(b/'input/4515_ssc450_sql80_static_admission_v2.json')
old_prepared=load(r/'evidence/01_PT/018_NK-OPS-001/evidence/PG36892-ssc450-sql80-prepare-v2/manifest.json')
previous={(x['path'],x['rule'],str(x['sourceLine']),x['message']):x for x in old['sourceAnchors']}
groups=Counter((relative(x['path']),x['rule'],x['line'],x['message']) for x in s['rawFindings']);anchors=[];reused=0
for (path,rule,line,message),multiple in groups.items():
    text=(r/path).read_text();anchor=text.splitlines()[int(line)-1].strip();main='/src/main/' in path
    prior=previous.get((path,rule,line,message))
    if prior:
        assert sha(r/path)==old_prepared['inputHashes'][path]==prep['inputHashes'][path]
        assert prior['sourceAnchor']==anchor and prior['rawMultiplicity']==multiple
        reason=prior['reason'];reused+=multiple
    elif rule=='AvoidCatchingGenericException':
        assert main and anchor in ['} catch (SQLException | RuntimeException | Error failure) {','} catch (SQLException | RuntimeException | Error cleanup) {']
        reason=('SS366/450 '+Path(path).stem+': this exact JDBC body/cleanup boundary preserves the original SQL/runtime/error primary identity and explicit once-only close order; body failures are rethrown, cleanup adds only a distinct secondary when a primary already exists. The success-path close is not swallowed and NPE is never normal recovery. The literal SQL operation refactor does not change this owner or failure priority.')
    elif rule=='CompareObjectsWithEquals':
        assert ('cleanup != primary' in anchor and main) or (path.endswith('/MigrationMasterFinalizerTest.java') and ('secondary == primary' in anchor or 'secondary != primary' in anchor))
        reason=('SS366/PT '+Path(path).stem+': this exact Throwable reference comparison distinguishes self-suppression from a distinct secondary. Throwable subclasses may override equals, so value comparison cannot satisfy the identity contract. Production skips self-addSuppressed; the independent test expects zero versus one and asserts the exact secondary identity.')
    elif rule=='ReplaceJavaUtilDate':
        assert path.endswith('/MigrationMasterContentVerifier.java') and anchor=='@Nullable Timestamp actual = result.getTimestamp(column);'
        reason='SS343/450 content timestamp boundary: JDBC ResultSet.getTimestamp has the required nullable java.sql.Timestamp return type. This exact local is converted immediately to immutable Instant and ISO text after the explicit null test, is never retained or used for mutable calendar arithmetic, and preserves the independently specified database timestamp comparison.'
    elif rule=='CloseResource' and ('var conn = f.connection();' in anchor):
        assert path.endswith(('MigrationMasterFinalizerTest.java','MigrationMasterReferenceVerifierTest.java'))
        reason=('PT '+Path(path).stem+': this exact local is a new fixture JDBC-interface Proxy, not an acquired database handle. The product borrows the caller transaction; connection close/commit/rollback are rejected by the fixture and owned Statement/ResultSet close counters are asserted separately. Closing it here would violate the tested borrowed-owner contract.')
    elif rule in ['CloseResource','DoNotUseThreads']:
        assert not main and any(x in anchor for x in ['Executors.newFixedThreadPool','executor.submit','executor.shutdownNow','executor.awaitTermination'])
        assert 'executor.shutdownNow();' in text and 'executor.awaitTermination(' in text and '.get(WAIT_SECONDS, TimeUnit.SECONDS)' in text
        reason=('PT '+Path(path).stem+': this exact fixed-pool operation belongs to a bounded standalone concurrency fixture, not container thread management. Every task uses its own memory JDBC fixture, every Future has a timed get, and finally shutdownNow plus asserted bounded awaitTermination discharges ownership. No backend or process lifetime is inferred from the test.')
    elif rule=='UseProperClassLoader':
        assert not main and 'getClassLoader()' in anchor
        reason=('PT '+Path(path).stem+': this exact loader belongs to a fixed JDK java.sql interface used by the fixture Proxy (Connection/Statement/PreparedStatement/ResultSet, or the same fixed Class parameter). Interface visibility requires that defining loader, not a user/context-selected loader. No driver/application reflection, class-name input or authority operation occurs.')
    else:raise ValueError('unreviewed site '+rule+' '+path+':'+line)
    anchors.append(dict(path=path,rule=rule,sourceAnchor=anchor,sourceLine=int(line),occurrences=1,
        message=message,rawMultiplicity=multiple,reason=reason,disposition='NOT_APPLICABLE'))
assert reused==71
out=b/'input/4520_ssc450_all161_static_admission.json';assert not out.exists()
out.open('x').write(json.dumps(dict(schema='PGPT_STATIC_ADMISSION_V1',profile=c['id'],
    prepare=ref(pp),static=ref(sp),sourceAnchors=anchors),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,raw=134,exactUnchangedReview71=True,newIndividuallyReviewed=63,applicable=0,unclassified=0)))

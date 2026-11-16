"""Per-site review of all71 raw findings; no blanket rule/file/Test suppression."""
from collections import Counter
from pathlib import Path
import hashlib
import json

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';cfg=json.loads((b/'input/4509_ssc450_sql80_profile_v2.json').read_text())
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
sp=r/cfg['slots']['static']/'manifest.json';p=load(sp);pp=r/cfg['slots']['prepare']/'manifest.json';prep=load(pp)
assert p['actualExit']==prep['actualExit']==0 and len(p['rawFindings'])==71
assert not p['processingErrors'] and p['checkstyleFindings']==0 and all(p['spotbugs'][x]==0 for x in ['bugs','missing','errors'])
groups=Counter((x['path'],x['rule'],x['line'],x['message']) for x in p['rawFindings']);anchors=[]
for (name,rule,line,message),multiplicity in groups.items():
    text=(r/name).read_text();anchor=text.splitlines()[int(line)-1].strip()
    main='/src/main/' in name
    if rule=='AvoidCatchingGenericException':
        assert main and anchor in ['} catch (SQLException | RuntimeException | Error failure) {','} catch (SQLException | RuntimeException | Error cleanup) {']
        if ' failure)' in anchor:
            reason='SS366/450 '+Path(name).stem+': this exact owned JDBC body boundary records the original SQL/runtime/error identity then rethrows, with the same outer finally closing the acquired statement/result once. It never converts an unknown failure into success or catches NPE for normal recovery.'
        else:
            reason='SS366/450 '+Path(name).stem+': this exact private close helper catches the one cleanup attempt only after a primary already exists, preserves the original primary and adds a distinct secondary once; the success-path close is outside this catch. This implements the approved Java compound-failure contract, not error recovery.'
    elif rule=='CompareObjectsWithEquals':
        assert main and anchor=='if (cleanup != primary) primary.addSuppressed(cleanup);'
        reason='SS366/450 '+Path(name).stem+': exact Throwable reference inequality prevents Java self-suppression; value equals could be overridden and cannot establish exception identity. Existing independent tests inject identical and distinct primary/cleanup objects and retain the same priority.'
    elif rule=='CloseResource' and main:
        assert name.endswith('/ScenarioStagingTables.java') and anchor=='@Nullable Statement created = connection.createStatement();'
        reason='SS366 Scenario staging unchanged helper: this exact created statement is null-checked and transferred to the immediately enclosing explicit try/finally closeStatement scope in prepare/transfer. Borrowed Connection is not closed; no return bypasses the statement close. Whole helper counters remain visible and are not claimed100 by this target scope.'
    elif rule=='CloseResource' and anchor=='var connection = f.connection();':
        assert name.endswith('/AssetStagingTablesTest.java')
        reason='PT scenarioTwoThenAssetThreeShareTheSameBorrowedTransactionInRequiredOrder: this exact value is a JDK JDBC-interface Proxy from a new private Fixture, not a driver or acquired DB handle. It is borrowed by both staging objects and connection-close/commit/rollback are forbidden by the fixture; statement4/result15/order25 postconditions are asserted separately.'
    elif rule in ['CloseResource','DoNotUseThreads']:
        assert not main and any(x in anchor for x in ['Executors.newFixedThreadPool','executor.submit','executor.shutdownNow','executor.awaitTermination'])
        assert 'finally {' in text and 'executor.shutdownNow();' in text and 'executor.awaitTermination(' in text and '.get(WAIT_SECONDS, TimeUnit.SECONDS)' in text
        reason='PT '+Path(name).stem+' finiteWorkers: this exact owned fixed-pool operation exercises independent in-memory JDBC fixtures, not container/server thread management. Every Future has a bounded get and finally shutdownNow plus asserted bounded awaitTermination. Each worker creates its own fixture; no backend/service lifetime or shared transaction is assumed.'
    elif rule=='UseConcurrentHashMap':
        assert name.endswith('/AssetStagingTablesTest.java') and any(x in anchor for x in ['Map<String, Long> staged','Map<String, Long> targets'])
        assert 'var f = new Fixture();' in text and 'private static final class Fixture' in text
        reason='PT Asset Fixture '+anchor.split('>')[-1].split('=')[0].strip()+': this exact nonstatic private map belongs to one newly constructed JDBC fixture. The finite-worker body allocates a separate Fixture per task, and sequential combined staging deliberately shares only that one borrowed transaction. No map is concurrently shared, so concurrent-map semantics are not required.'
    elif rule=='UseProperClassLoader':
        assert not main and ('getClassLoader()' in anchor)
        reason='PT '+Path(name).stem+': this exact loader is the loader of the fixed java.sql Connection/Statement/ResultSet interface (or the same fixed Class argument in the fixture Proxy factory). JDK Proxy must define those interfaces in their visible loader; no context/user-selected class names, application reflection, backend driver or authority loader is used.'
    else:raise ValueError('unreviewed rule/site: '+rule+' '+name+':'+line)
    anchors.append(dict(path=name,rule=rule,sourceAnchor=anchor,sourceLine=int(line),occurrences=1,
        message=message,rawMultiplicity=multiplicity,reason=reason,disposition='NOT_APPLICABLE'))
value=dict(schema='PGPT_STATIC_ADMISSION_V1',profile=cfg['id'],prepare=ref(pp),static=ref(sp),sourceAnchors=anchors)
out=b/'input/4513_ssc450_sql80_static_admission.json';assert not out.exists();out.open('x').write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,raw=71,distinctSiteMessages=len(anchors),applicable=0,unclassified=0)))

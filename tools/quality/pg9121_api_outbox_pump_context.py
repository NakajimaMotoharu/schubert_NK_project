"""Private finite claim lock and monotonic-failure rethrow; current PT/source, actual PMD join at post."""
from collections import Counter
import datetime as dt
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import pg9120_api_outbox_pump_host as selected
from host_tool_invocation import capture,verify

host=selected.run.host
OUT=host.BASE/'PG9121-api-outbox-pump-context-v1'
MAIN='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiOutboxObservationPump.java'
HOST=host.W/'pg9120-api-outbox-pump-host-v1/manifest.safe.json'
HOST_SHA='0258aba171785acf61d4451b2833b431bd41c0d16341d7c48d3fcdad96aa699a'


def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and host.sha(HOST)==HOST_SHA
    raw=json.loads(HOST.read_bytes());assert raw['actualExit']==0 and raw['source']==selected.SOURCE
    assert len(raw['cases'])==32 and all(row['result']=='PASS' and not row['nonPass'] for row in raw['cases'])
    names=[]
    for file in (HOST.parent/'xml').glob('TEST-*.xml'):
        assert raw['xmlHashes'][file.name]==host.sha(file)
        for case in ET.parse(file).getroot().findall('testcase'):
            assert not list(case);names.append(case.get('name'))
    assert set(names)=={'outboxPump'+str(i).zfill(3) for i in range(1,33)}
    text=(host.ROOT/MAIN).read_text();digest=host.sha(host.ROOT/MAIN);assert raw['begin']['sourceHashes'][MAIN]==digest
    assert 'private final Object lock = new Object();' in text and text.count('synchronized (lock)')==1
    assert text.count('nanos.getAsLong()')==text.count('attempts.get()')==1
    assert text.index('retained.set(Optional.of(attempt));')<text.index('source.observe(attempt);')
    assert 'return !active.get() && !unconfirmed.get();' in text and 'if (stopping.get() || unconfirmed.get()) return Optional.empty();' in text
    assert 'Duration.ofSeconds(15)' in text and 'now - lastClaim < intervalNanos' in text
    assert 'catch (RuntimeException | Error failure)' in text and 'source.missing();\n        throw failure;' in text
    for forbidden in ('new Thread(','.start(','.join(','.sleep(','.getConnection(','.commit(','.rollback(','.close(', 'System.err', 'System.getenv('):assert forbidden not in text
    decisions=[]
    for number,line in enumerate(text.splitlines(),1):
        if 'synchronized (lock)' in line:
            decisions.append(dict(raw=dict(begincolumn='5',beginline=str(number),endcolumn='17',endline=str(number),
              externalInfoUrl='https://docs.pmd-code.org/snapshot/pmd_rules_java_multithreading.html#avoidsynchronizedstatement',message='Use ReentrantLock rather than synchronization',
              method='sampleIfDue',package='dev.codex.schubert.nk.api.monitoring',priority='3',rule='AvoidSynchronizedStatement',ruleset='Multithreading'),
              reason='411 private final claim-only monitor serializes due/active admission. JDBC/factory/UNKNOWN policy run outside it; get/stop/quiescence use atomics. Current overlap, factory-stop, SQL-stop and UNKNOWN fixtures prove no second checkout or false quiescence. No worker/join acceptance inferred.'))
        if 'catch (RuntimeException | Error failure)' in line:
            for kind in ('RuntimeException','Error'):
                column=line.index(kind)+1
                decisions.append(dict(raw=dict(begincolumn=str(column),beginline=str(number),endcolumn=str(column+len(kind)),endline=str(number),
                  externalInfoUrl='https://docs.pmd-code.org/snapshot/pmd_rules_java_errorprone.html#avoidcatchinggenericexception',message=f'Avoid catching {kind} in try-catch block',
                  method='sampleIfDue',package='dev.codex.schubert.nk.api.monitoring',priority='3',rule='AvoidCatchingGenericException',ruleset='Error Prone'),
                  reason='Catch only marks current metadata missing and rethrows the same Runtime/Error union. No NPE-normal fallback or provider text; current 021/022 independently assert identity, no factory/SQL and quiescence.'))
    assert len(decisions)==3 and Counter(row['raw']['rule'] for row in decisions)==Counter(AvoidSynchronizedStatement=1,AvoidCatchingGenericException=2)
    for row in decisions:
        row['raw']['class']='ApiOutboxObservationPump';row.update(classification='NECESSARY_FINITE_SAMPLER_CONTRACT_REVIEWED',sourcePath=MAIN,sourceSha256=digest,sourceOrRulesChanged=False,suppressionAdded=False,ordinaryTestWitness='PG9120-api-outbox-pump-host-v1:OUTBOXPUMP001..032')
    verify(invocation);OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=selected.SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,currentHostManifestSha256=HOST_SHA,
      staticDispositions=decisions,rawPmd=3,unclassified=0,actualViolationsOutstanding=0,expectedRawPmdPendingActualJoin=True,
      staticAnalysisExecuted=False,productTestsExecuted=0,suppressionsAdded=False,actualWorkerNativePt='UNRUN_HOLD',formalUpdated=False,newAccepted=0))
    print(json.dumps(dict(actualExit=0,reviewedExpectedRows=3,actualRawJoinPending=True,manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':main()

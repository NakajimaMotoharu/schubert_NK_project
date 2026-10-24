"""Current two private writer locks/old and cleanup-confirmed overload; actual PMD join remains post."""
import datetime as dt
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import pg9106_api_cleanup_publication_host as selected
from host_tool_invocation import capture,verify

host=selected.run.host
OUT=host.BASE/'PG9107-api-cleanup-publication-lock-review-v1'
MAIN='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiOutboxObservationSource.java'
HOST=host.W/'pg9106-api-cleanup-publication-host-v1/manifest.safe.json'
HOST_SHA='76dfef768ceb1be291cca95bd8bf909e3a1b88f4d16ea75e5cac9849eb09551e'


def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and host.sha(HOST)==HOST_SHA
    raw=json.loads(HOST.read_bytes());assert raw['actualExit']==0 and raw['source']==selected.SOURCE
    assert len(raw['cases'])==34 and all(row['result']=='PASS' and not row['nonPass'] for row in raw['cases'])
    text=(host.ROOT/MAIN).read_text();digest=host.sha(host.ROOT/MAIN);assert raw['begin']['sourceHashes'][MAIN]==digest
    assert 'private final Object writerLock = new Object();' in text and text.count('synchronized (writerLock)')==2
    assert text.count('Entry pending = new Entry(Optional.empty());')==2 and text.count('current.set(pending);')==2 and text.count('current.compareAndSet(pending, new Entry(supplied))')==2
    assert text.count('repository.read(connection, asOf)')==1 and text.count('attempt.read()')==1
    start=text.index('public Optional<Snapshot> observe(ApiReadOnlyObservationAttempt attempt)')
    assert text.index('Objects.requireNonNull(attempt',start)<text.index('synchronized (writerLock)',start)<text.index('current.set(pending);',start)<text.index('attempt.read()',start)<text.index('current.compareAndSet(',start)
    for method in ('missing','get'):
        body=re.search(r'public (?:void|Optional<Snapshot>) '+method+r'\(\) \{([^}]+)\}',text).group(1)
        assert 'synchronized' not in body and 'repository.' not in body and 'attempt.' not in body
    names=[]
    for file in (HOST.parent/'xml').glob('TEST-*.xml'):
        assert raw['xmlHashes'][file.name]==host.sha(file)
        for case in ET.parse(file).getroot().findall('testcase'):
            assert not list(case);names.append(case.get('name'))
    assert set(names)=={'outboxPublish'+str(i).zfill(3) for i in range(1,15)}|{'outboxSource'+str(i).zfill(3) for i in range(1,21)}
    standard=host.ROOT/'documents/400_PGPT/410_工程標準/411_コーディング規約.md'
    assert '内部状態/secret/resource寿命の排他はprivate final lockで行い' in standard.read_text()
    decisions=[]
    for number,line in enumerate(text.splitlines(),1):
        if 'synchronized (writerLock)' not in line:continue
        expected=dict(begincolumn='5',beginline=str(number),endcolumn='17',endline=str(number),
          externalInfoUrl='https://docs.pmd-code.org/snapshot/pmd_rules_java_multithreading.html#avoidsynchronizedstatement',
          message='Use ReentrantLock rather than synchronization',method='observe',
          package='dev.codex.schubert.nk.api.monitoring',priority='3',rule='AvoidSynchronizedStatement',ruleset='Multithreading')
        expected['class']='ApiOutboxObservationSource'
        decisions.append(dict(raw=expected,classification='NECESSARY_PRIVATE_LOCK_CONTRACT_REVIEWED',sourcePath=MAIN,sourceSha256=digest,sourceOrRulesChanged=False,suppressionAdded=False,
          ordinaryTestWitness='PG9106-api-cleanup-publication-host-v1:OUTBOXSOURCE017/018;OUTBOXPUBLISH008/011/012/014',
          reason='411 private final nonpublished writer monitor serializes RO observations/cleanup before immutable CAS publication. get/missing never take it or touch JDBC/SDK. Current original-connection and cleanup-confirmed overloads are both executed, including missing ABA fence, retained UNKNOWN callback, repeat owner refusal and concurrent service rendering. This is an explicit source/test-bound lock choice, not PMD raw0, blanket suppression, actor deadline or actual DB/worker acceptance.'))
    assert len(decisions)==2
    verify(invocation);OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=selected.SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      currentHostManifestSha256=HOST_SHA,standardSha256=host.sha(standard),staticDispositions=decisions,
      expectedRawPmdPendingActualJoin=True,rawPmd=2,unclassified=0,actualViolationsOutstanding=0,staticAnalysisExecuted=False,
      productTestsExecuted=0,suppressionsAdded=False,formalUpdated=False,newAccepted=0))
    print(json.dumps(dict(actualExit=0,reviewedPrivateLocks=2,actualRawJoinPending=True,manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':main()

"""Current private-lock requirement review; expected PMD row must later join actual raw XML exactly."""
import datetime as dt
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import pg9044_api_outbox_source_host as selected
from host_tool_invocation import capture,verify

host=selected.run.host
OUT=host.BASE/'PG9045-api-outbox-source-lock-review-v1'
MAIN='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiOutboxObservationSource.java'
HOST=host.W/'pg9044-api-outbox-source-host-v1/manifest.safe.json'
HOST_SHA='807a12324f097a15af1a89c73394cedd1c6e4842ed7767ae6bf6fe5502339712'


def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and host.sha(HOST)==HOST_SHA
    raw=json.loads(HOST.read_bytes());assert raw['actualExit']==0 and raw['source']==selected.SOURCE
    assert len(raw['cases'])==36 and all(row['result']=='PASS' and not row['nonPass'] for row in raw['cases'])
    text=(host.ROOT/MAIN).read_text();digest=host.sha(host.ROOT/MAIN)
    assert raw['begin']['sourceHashes'][MAIN]==digest
    assert 'private final Object writerLock = new Object();' in text
    assert text.count('synchronized (writerLock)')==1 and 'synchronized (this)' not in text
    assert text.index('current.set(pending);')<text.index('repository.read(connection, asOf)')<text.index('current.compareAndSet(pending, new Entry(supplied))')
    for method in ('missing','get'):
        body=re.search(r'public (?:void|Optional<Snapshot>) '+method+r'\(\) \{([^}]+)\}',text).group(1)
        assert 'synchronized' not in body and 'repository.' not in body
    xml=host.W/'pg9044-api-outbox-source-host-v1/xml'
    names=[]
    for file in xml.glob('TEST-*.xml'):
        assert raw['xmlHashes'][file.name]==host.sha(file)
        for case in ET.parse(file).getroot().findall('testcase'):
            assert not list(case);names.append(case.get('name'))
    assert all(any(n.startswith('outboxSource'+str(i).zfill(3)) for n in names) for i in (11,12,13,14,15,17,18,19,20))
    standard=host.ROOT/'documents/400_PGPT/410_工程標準/411_コーディング規約.md'
    assert '内部状態/secret/resource寿命の排他はprivate final lockで行い' in standard.read_text()
    line=next(i for i,line in enumerate(text.splitlines(),1) if 'synchronized (writerLock)' in line)
    expected=dict(begincolumn='5',beginline=str(line),endcolumn='17',endline=str(line),
      externalInfoUrl='https://docs.pmd-code.org/snapshot/pmd_rules_java_multithreading.html#avoidsynchronizedstatement',
      message='Use ReentrantLock rather than synchronization',method='observe',
      package='dev.codex.schubert.nk.api.monitoring',priority='3',rule='AvoidSynchronizedStatement',ruleset='Multithreading')
    expected['class']='ApiOutboxObservationSource'
    row=dict(raw=expected,classification='NECESSARY_PRIVATE_LOCK_CONTRACT_REVIEWED',
      sourcePath=MAIN,sourceSha256=digest,sourceOrRulesChanged=False,suppressionAdded=False,
      ordinaryTestWitness='PG9044-api-outbox-source-host-v1:OUTBOXSOURCE011-015/017-020',
      reason='411 private final non-published monitor serializes only borrowed-RO read/cleanup/publication writers. get/missing are lock-free AtomicReference operations. No this/class lock; immutable fresh Entry CAS prevents delayed publication/ABA. Current failure identity, suppressed close, writer serialization and concurrent invalidation were independently asserted. This is an explicit reviewed private-lock choice, not zero raw PMD or general suppression; owner deadline/producer/actual DB remain unqualified.')
    verify(invocation);OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=selected.SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),
      invocation=invocation,currentHostManifestSha256=HOST_SHA,standardSha256=host.sha(standard),
      expectedRawPmdPendingActualJoin=True,staticDispositions=[row],unclassified=0,actualViolationsOutstanding=0,
      staticAnalysisExecuted=False,productTestsExecuted=0,suppressionsAdded=False,formalUpdated=False,newAccepted=0))
    print(json.dumps(dict(actualExit=0,reviewedPrivateLock=1,actualRawJoinPending=True,manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':main()

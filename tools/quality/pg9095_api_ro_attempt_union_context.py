"""Current typed owner fourteen PMD rows: explicit private-lock/cleanup/nullable-owner reasons, not raw0."""
from collections import Counter
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import pg9092_api_ro_attempt_union_host as selected
from host_tool_invocation import capture,verify

host=selected.run.host
OUT=host.BASE/'PG9095-api-ro-attempt-union-context-v1'
STATIC=host.BASE/'PG9093-api-ro-attempt-union-static-v1/manifest.json'
STATIC_SHA='a77fe6575e9c038a29b67cdab4c3d288242c5531e04d3439399165e6027aa400'
HOST=host.W/'pg9092-api-ro-attempt-union-host-v1/manifest.safe.json'
HOST_SHA='8337c6a91af36f9945ab338dec5bec4274f3cb712f80cf278bdc7240c46a516e'
MAIN='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiReadOnlyObservationAttempt.java'


def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and host.sha(STATIC)==STATIC_SHA and host.sha(HOST)==HOST_SHA
    raw=json.loads(STATIC.read_bytes());actual=json.loads(HOST.read_bytes())
    assert raw['source']==actual['source']==selected.SOURCE and actual['actualExit']==0
    assert len(actual['cases'])==32 and all(row['result']=='PASS' and not row['nonPass'] for row in actual['cases'])
    names=[]
    for file in (HOST.parent/'xml').glob('TEST-*.xml'):
        assert actual['xmlHashes'][file.name]==host.sha(file)
        for case in ET.parse(file).getroot().findall('testcase'):
            assert not list(case);names.append(case.get('name'))
    assert set(names)=={'roAttempt'+str(i).zfill(3) for i in range(1,33)}
    for name in ('checkstyle','spotbugs'):
        row=raw['static'][name];assert row['receipt']['actualExit']==0 and row['receipt']['timedOut'] is False and row['findings']==row['processingErrors']==0
    pmd=raw['static']['pmd'];assert pmd['receipt']['actualExit']==4 and pmd['processingErrors']==0 and pmd['findings']==14
    xml=host.W/'pg9093-api-ro-attempt-union-static-v1/pmd.xml';assert pmd['reportSha256']==host.sha(xml)
    parsed=[dict(node.attrib,message=' '.join(''.join(node.itertext()).split())) for node in ET.parse(xml).getroot().findall('.//{*}violation')]
    canonical=lambda rows:Counter(json.dumps(row,sort_keys=True) for row in rows)
    assert canonical(parsed)==canonical(pmd['rawFindings'])
    assert all(host.sha(Path(path))==digest for path,digest in raw['toolHashes'].items())
    text=(host.ROOT/MAIN).read_text();digest=host.sha(host.ROOT/MAIN);assert actual['begin']['sourceHashes'][MAIN]==raw['sourceHashes'][MAIN]==digest
    assert 'throw (RuntimeException)' not in text and 'throw runtime;' not in text
    assert 'catch (SQLException | RuntimeException | Error primary)' in text and 'throw primary;' in text
    assert text.index('failures.add(primary);')<text.index('cleanup();')<text.index('attachSecondary(primary, secondary)')<text.index('preserveFatal(primary)')<text.index('throw primary;')
    assert all(value in text for value in ('transactionAttempted = true;', 'rollbackAttempted = true;', 'closeAttempted = true;', 'if (!closeAttempted)', 'if (transactionAttempted && !rollbackAttempted)'))
    assert 'private final Object lock = new Object();' in text and text.count('synchronized (lock)')==1
    assert text.index('owned.close();')<text.index('retained = null;')<text.index('unconfirmed.set(true);')<text.index('onUnconfirmed.accept(close);')
    expected=[]
    for number,line in enumerate(text.splitlines(),1):
        if 'synchronized (lock)' in line:expected.append(('AvoidSynchronizedStatement',str(number),str(line.index('synchronized')+1)))
        if '} catch (' in line:
            for name in ('RuntimeException','Error'):
                if name in line:expected.append(('AvoidCatchingGenericException',str(number),str(line.index(name)+1)))
        for variable in ('supplied','owned'):
            if 'Connection '+variable+' =' in line:expected.append(('CloseResource',str(number),str(line.index(variable)+1)))
        if 'retained = null;' in line:expected.append(('NullAssignment',str(number),str(line.index('null')+1)))
    assert len(expected)==14 and Counter(expected)==Counter((row['rule'],row['beginline'],row['begincolumn']) for row in parsed)
    assert Counter(row['rule'] for row in parsed)==Counter(AvoidSynchronizedStatement=1,AvoidCatchingGenericException=10,CloseResource=2,NullAssignment=1)
    reasons={
      'AvoidSynchronizedStatement':'411 private final owner lock, not this/class; serialize one attempt. ROATTEMPT005/022/032 validate repeat/reentry/concurrent single checkout, status is nonblocking.',
      'AvoidCatchingGenericException':'All failures remain captured only through mandatory cleanup, then same typed failure/fatal graph is rethrown. No normal fallback/NPE catch or provider logging. ROATTEMPT007-031 independently cover checked/runtime/fatal/compound/diagnostic/alias/cyclic and suppression-disabled cases.',
      'CloseResource':'The two locals are aliases of one Connection held in retained before mode setup; every acquired branch reaches one close after required rollback, with UNKNOWN policy retaining exact frame on failure. ROATTEMPT003-032 assert physical close/open/rollback counts and rejecting reuse, no TWR implicit retry.',
      'NullAssignment':'Private annotated nullable ownership slot is cleared only after owned.close returns. On exception the reference remains retained before UNKNOWN policy, not converted to missing success. ROATTEMPT003/022-030 prove confirmed vs unconfirmed and callback/reentry state.'}
    decisions=[dict(raw=row,classification='EXPLICIT_NECESSARY_OWNER_CONTRACT_REVIEWED',reason=reasons[row['rule']],sourcePath=MAIN,sourceSha256=digest,
      sourceOrRulesChanged=False,suppressionAdded=False,ordinaryTestWitness='PG9092-api-ro-attempt-union-host-v1:ROATTEMPT001..032') for row in parsed]
    verify(invocation);OUT.mkdir()
    host.write(OUT/'manifest.json',dict(actualExit=0,source=selected.SOURCE,invocation=invocation,currentHostManifestSha256=HOST_SHA,
      rawStaticManifestSha256=STATIC_SHA,staticDispositions=decisions,rawPmd=14,checkstyle=0,spotbugs=0,unclassified=0,actualViolationsOutstanding=0,
      oldSourceResultsTransferred=False,productTestsExecuted=0,suppressionsAdded=False,actualDbNativePt='UNRUN_HOLD',formalUpdated=False,newAccepted=0))
    print(json.dumps(dict(actualExit=0,reviewedPmd=14,unclassified=0,spotbugs=0,manifestSha256=host.sha(OUT/'manifest.json'))))


if __name__=='__main__':main()

"""Exact-source reuse of thirteen existing API readonly-owner diagnostic rationales; no PT replay."""
from collections import Counter
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = 'f24d1649e170e46aafb59a37b9750c602206364c'
TARGET = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiReadOnlyObservationAttempt.java'
OUT = data.BASE/'PG10934-api-ro-prior-context13-v1'


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    prior_path = data.BASE/'PG9095-api-ro-attempt-union-context-v1/manifest.json'
    prior = data.read_checked(prior_path,'64157d793d00ab8222dd3380262e2cff6ceb2f32ef216565ca0ebb39f6ab7918')
    normal = data.read_checked(data.BASE/'PG10892-web-boundary-line-six-compile-v1/manifest.json',
        '345e989275ba9dd52da2356d303c7c1a818feeaf4a41244b6ba05b8e26bf2de9')
    assert prior['actualExit'] == normal['actualExit'] == 0 and normal['source'] == SOURCE and prior['source'] != SOURCE
    before = subprocess.check_output(['git','show',prior['source']+':'+TARGET],cwd=data.ROOT)
    digest = normal['begin']['inputHashes'][TARGET]
    assert before == (data.ROOT/TARGET).read_bytes() and data.sha(before) == digest
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    current_rows = [r for r in original if r['path'] == TARGET]
    assert len(current_rows) == len(prior['staticDispositions']) == 14
    result,excluded = [],[]
    for old in prior['staticDispositions']:
        assert old['sourcePath'] == TARGET and old['sourceSha256'] == digest and old['reason']
        raw = old['raw']
        matches = [r for r in current_rows if r['rule'] == raw['rule'] and r['attributes'] == {k:v for k,v in raw.items() if k != 'message'}
            and ' '.join(r['message'].split()) == ' '.join(raw['message'].split())]
        assert len(matches) == 1
        row = matches[0]
        if row['id'] == 'PMD-00346':
            assert row['rule'] == 'NullAssignment'
            excluded.append(row['id'])
            continue
        result.append(dict(id=row['id'],source=SOURCE,path=TARGET,sourceSha256=digest,rule=row['rule'],
            attributes=row['attributes'],originalRowSha256=row['rowSha256'],reason=old['reason'],
            technicalPriorClassification=old['classification'],priorSource=prior['source'],
            priorManifestSha256=data.sha(prior_path.read_bytes()),historicalTestWitness=old['ordinaryTestWitness'],
            status='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',currentWholeCaseRefs=[],rawWarningRetained=True,
            oldRuntimeReassigned=False,scopeGeneralized=False,productTestsExecuted=0,coverage=None,ptExecutionExempt=False))
    assert len(result) == len({r['id'] for r in result}) == 13 and excluded == ['PMD-00346']
    assert Counter(r['rule'] for r in result) == Counter(AvoidCatchingGenericException=10,CloseResource=2,AvoidSynchronizedStatement=1)
    prior_nullable = data.read_checked(data.BASE/'PG10922-main-null-owner-route-context-v1/manifest.json',
        '9360be53ed58a1cf468f0968ca1b91b51fe288a4e217b6576fd342e6c1a88480')
    values = data.read_checked(data.BASE/'PG10922-main-null-owner-route-context-v1/contexts.json',prior_nullable['contextsSha256'])
    assert 'PMD-00346' in {r['id'] for r in values} and not {r['id'] for r in result}&{r['id'] for r in values}
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'contexts.json',result)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        contextsSha256=data.sha((OUT/'contexts.json').read_bytes()),priorManifestSha256=data.sha(prior_path.read_bytes()),
        sourceSha256=digest,exactPriorMainSource=prior['source'],findings=13,excludedAlreadyReferenced=excluded,
        ruleCounts=dict(Counter(r['rule'] for r in result)),sourceDerivedRaw=9248,
        referencedRowsBefore=2711,referencedRowsAfter=2724,currentWholePendingBefore=31,currentWholePendingAfter=44,
        noCurrentReferenceBefore=6537,noCurrentReferenceAfter=6524,rawWarningsRemoved=0,
        productTestsExecuted=0,coverage=None,wholeF03Accepted=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()

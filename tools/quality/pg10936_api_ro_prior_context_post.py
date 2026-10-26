"""Independent thirteen exact legacy owner references; nullable one excluded, old runtime not transferred."""
from collections import Counter
import copy
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = 'f24d1649e170e46aafb59a37b9750c602206364c'
TARGET = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiReadOnlyObservationAttempt.java'
OUT = data.BASE/'PG10936-api-ro-prior-context-post-v1'


def contract(rows,original,prior,source_hash):
    expected_ids = {r['id'] for r in original.values() if r['path'] == TARGET and r['id'] != 'PMD-00346'}
    if len(rows) != 13 or {r['id'] for r in rows} != expected_ids:
        raise ValueError('thirteen existing findings once, nullable already bound')
    if Counter(r['rule'] for r in rows) != Counter(AvoidCatchingGenericException=10,CloseResource=2,AvoidSynchronizedStatement=1):
        raise ValueError('exact reviewed rules')
    for row in rows:
        old = original[row['id']]
        if row['source'] != SOURCE or row['path'] != TARGET or row['sourceSha256'] != source_hash or row['sourceSha256'] != old['inputSha256']:
            raise ValueError('exact current source')
        if row['attributes'] != old['attributes'] or row['rule'] != old['rule'] or row['originalRowSha256'] != old['rowSha256']:
            raise ValueError('same original raw identity')
        matches = [v for v in prior['staticDispositions'] if v['sourcePath'] == TARGET and
            {k:value for k,value in v['raw'].items() if k != 'message'} == row['attributes']]
        if len(matches) != 1:
            raise ValueError('one existing precise assessment')
        value = matches[0]
        if row['reason'] != value['reason'] or row['technicalPriorClassification'] != value['classification'] or row['historicalTestWitness'] != value['ordinaryTestWitness'] or row['priorSource'] != prior['source']:
            raise ValueError('no rationale/witness/source substitution')
        if row['status'] != 'SOURCE_REBOUND_CURRENT_WHOLE_PENDING' or row['currentWholeCaseRefs'] != [] or row['oldRuntimeReassigned'] is not False:
            raise ValueError('old tests not current success')
        if row['productTestsExecuted'] != 0 or row['coverage'] is not None or row['ptExecutionExempt'] is not False or row['scopeGeneralized'] is not False or row['rawWarningRetained'] is not True:
            raise ValueError('no dynamic credit or suppression')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    path = data.BASE/'PG10934-api-ro-prior-context13-v1/manifest.json'
    primary = data.read_checked(path,'69b5240316368ec534dd837ca1b95b9b8f2cd36af1a87775b165e1e6a780350f')
    rows = data.read_checked(path.parent/'contexts.json',primary['contextsSha256'])
    prior = data.read_checked(data.BASE/'PG9095-api-ro-attempt-union-context-v1/manifest.json',primary['priorManifestSha256'])
    raw = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    original = {r['id']:r for r in raw}
    normal = data.read_checked(data.BASE/'PG10892-web-boundary-line-six-compile-v1/manifest.json',
        '345e989275ba9dd52da2356d303c7c1a818feeaf4a41244b6ba05b8e26bf2de9')
    digest = normal['begin']['inputHashes'][TARGET]
    assert primary['actualExit'] == prior['actualExit'] == 0 and primary['source'] == normal['source'] == SOURCE
    assert prior['source'] != SOURCE
    before = subprocess.check_output(['git','show',prior['source']+':'+TARGET],cwd=data.ROOT)
    assert before == (data.ROOT/TARGET).read_bytes() and data.sha(before) == digest
    contract(rows,original,prior,digest)
    previous = data.read_checked(data.BASE/'PG10928-main-empty-catch-policy-v1/manifest.json',
        '6e1ed0ff67610462fd6d3e0830dc5bd8ccaad18248a7625f351707de9fad340f')
    assert primary['referencedRowsAfter'] == previous['referencedRows']+13 == 2724
    assert primary['currentWholePendingAfter'] == previous['currentWholePending']+13 == 44
    assert primary['noCurrentReferenceAfter'] == previous['noCurrentReference']-13 == 6524
    nullable = data.read_checked(data.BASE/'PG10922-main-null-owner-route-context-v1/manifest.json',
        '9360be53ed58a1cf468f0968ca1b91b51fe288a4e217b6576fd342e6c1a88480')
    nullable_rows = data.read_checked(data.BASE/'PG10922-main-null-owner-route-context-v1/contexts.json',nullable['contextsSha256'])
    assert 'PMD-00346' in {r['id'] for r in nullable_rows}
    assert not {r['id'] for r in nullable_rows}&{r['id'] for r in rows}
    bads = [rows[:-1],rows+[rows[0]]]
    for field,value in [('sourceSha256','0'*64),('source','old'),('reason','fake'),('historicalTestWitness','fake'),
                        ('oldRuntimeReassigned',True),('currentWholeCaseRefs',['old-case']),('status','PASS')]:
        bad = copy.deepcopy(rows)
        bad[0][field] = value
        bads.append(bad)
    for bad in bads:
        try: contract(bad,original,prior,digest)
        except ValueError: pass
        else: raise AssertionError('incomplete/forged/rationale-transfer metadata accepted')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        primaryManifestSha256=data.sha(path.read_bytes()),contextsSha256=primary['contextsSha256'],
        findings=13,mainSources=1,metadataNegativeVectors=len(bads),excludedAlreadyReferenced=['PMD-00346'],
        sourceDerivedRaw=9248,referencedRows=2724,currentWholePending=44,noCurrentReference=6524,
        productTestsExecuted=0,coverage=None,wholeF03Accepted=False,rawWarningRemoved=False,
        externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()

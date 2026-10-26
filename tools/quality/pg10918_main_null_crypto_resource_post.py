"""Independent five Main source/rule/coordinate and historical-only reference checks."""
import copy
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = 'f24d1649e170e46aafb59a37b9750c602206364c'
OUT = data.BASE/'PG10918-main-null-crypto-resource-post-v1'
EXPECTED = {
    'PMD-00124':'REQUIRED_CONTRACT',
    'PMD-00125':'REQUIRED_CONTRACT',
    'PMD-00128':'FALSE_POSITIVE_RUNTIME_INPUT_LABEL_NOT_KEY_MATERIAL',
    'PMD-00129':'FALSE_POSITIVE_EXPLICIT_END_FINALLY_NO_SCRATCH_ACQUISITION_GAP',
    'PMD-00130':'FALSE_POSITIVE_EXPLICIT_END_FINALLY_NO_SCRATCH_ACQUISITION_GAP',
}


def contract(rows,original,current):
    if len(rows) != 5 or {r['id'] for r in rows} != set(EXPECTED):
        raise ValueError('five exact original finding IDs')
    for row in rows:
        old = original[row['id']]
        if row['source'] != SOURCE or row['path'] != old['path'] or row['sourceSha256'] != current[row['path']] or row['sourceSha256'] != old['inputSha256']:
            raise ValueError('exact current Main source bytes')
        if row['rule'] != old['rule'] or row['attributes'] != old['attributes'] or row['originalRowSha256'] != old['rowSha256']:
            raise ValueError('raw rule/coordinates/provenance retained')
        if row['technicalDisposition'] != EXPECTED[row['id']] or not row['basis']:
            raise ValueError('only original specific rationale')
        if row['status'] != 'SOURCE_REBOUND_CURRENT_WHOLE_PENDING' or row['currentWholeCaseRefs'] != [] or row['priorRuntimeReassigned'] is not False or row['newProductExecutions'] != 0 or row['newCoverage'] is not None:
            raise ValueError('historical source results not current PT/coverage')
        if row['rawWarningRetained'] is not True or row['scopeGeneralized'] is not False:
            raise ValueError('no suppression or blanket exception')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    path = data.BASE/'PG10916-main-null-crypto-resource-context-v1/manifest.json'
    primary = data.read_checked(path,'d41f3747340987cf0a408a71e2224b07b9ec5f08664b79f687b75b240f19492d')
    rows = data.read_checked(path.parent/'contexts.json',primary['contextsSha256'])
    original_rows = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    original = {r['id']:r for r in original_rows}
    normal = data.read_checked(data.BASE/'PG10892-web-boundary-line-six-compile-v1/manifest.json',
        '345e989275ba9dd52da2356d303c7c1a818feeaf4a41244b6ba05b8e26bf2de9')
    assert primary['actualExit'] == 0 and primary['source'] == normal['source'] == SOURCE
    current = normal['begin']['inputHashes']
    contract(rows,original,current)
    assert all(data.sha((data.ROOT/r['path']).read_bytes()) == r['sourceSha256'] for r in rows)
    legacy = data.read_checked(data.BASE/'PG5426-static-findings-v1/manifest.json',
        '41ddbd7c37b2bbcbc7ee69ef911c4743f59b29523559068581622c24efdb42bc')
    nonce = data.read_checked(data.BASE/'PG9876-snapshot-nonce-quality-source-post-v1/manifest.json',
        '00eb2fb3eb8d9cb763e7a2a91eb0aa0352eff63ba17725b5f305d75a7e939f48')
    old_normal = data.read_checked(data.BASE/'PG9866-snapshot-nonce-six-compile-v1/manifest.json',
        '2b00918c64ac9dfc7e9b4d648c93ef8ef0bee293ae1faa65cc280c3dd21ab535')
    prior_three = data.read_checked(data.BASE/'PG9876-snapshot-nonce-quality-source-post-v1/pmd-three-applicability.json',
        nonce['pmdApplicabilitySha256'])
    for row in rows:
        if row['technicalDisposition'] == 'REQUIRED_CONTRACT':
            hits = [r for r in legacy['findings'] if r['findingId'] == row['evidence']['originalFindingId']]
            assert len(hits) == 1
            old = hits[0]
            assert old['sourcePath'] == row['path'] and old['sourceSha256'] == row['sourceSha256'] and old['status'] == row['technicalDisposition']
            assert old['reason'] == row['basis'] and old['wholeCaseRefs'] == row['evidence']['historicalWholeCaseRefs']
            assert row['priorSource'] == legacy['source'] != SOURCE
        else:
            assert row['priorSource'] == nonce['source'] == old_normal['source'] != SOURCE
            assert old_normal['begin']['inputHashes'][row['path']] == row['sourceSha256']
            hits = [v for v in prior_three if v['classification'] == row['technicalDisposition'] and
                all(v.get(k) == value for k,value in row['attributes'].items())]
            assert len(hits) == 1
            assert row['evidence']['historicalSelectedTests'] == nonce['selectedTests'] and row['evidence']['historicalTargetFour100'] == nonce['targetUnitFour100']
    parent = data.read_checked(data.BASE/'PG10910-current-f03-web-metric-delta-v1/manifest.json',primary['parentDeltaManifestSha256'])
    prior_contexts = data.read_checked(data.BASE/'PG10910-current-f03-web-metric-delta-v1/delta.json',parent['deltaSha256'])
    assert not set(EXPECTED) & {r['id'] for r in prior_contexts['legacyContextOverlay']}
    assert not set(EXPECTED) & set(prior_contexts['removedFindingIds'])
    assert primary['referencedRowsAfter'] == parent['joinedContextWarnings']+5 == 2691
    assert primary['noCurrentReferenceAfter'] == parent['noCurrentReferenceInThisJoin']-5 == 6557
    assert primary['currentWholePendingAfter'] == parent['sourceReboundCurrentWholePending']+5 == 11
    bads = [rows[:-1],rows+[rows[0]]]
    for field,value in [('sourceSha256','0'*64),('source','old'),('technicalDisposition','PASS'),
                        ('currentWholeCaseRefs',['old-case']),('priorRuntimeReassigned',True),
                        ('newCoverage',100),('scopeGeneralized',True)]:
        bad = copy.deepcopy(rows)
        bad[0][field] = value
        bads.append(bad)
    for bad in bads:
        try: contract(bad,original,current)
        except ValueError: pass
        else: raise AssertionError('stale/forged/whole-source transfer accepted')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        originalManifestSha256=data.sha(path.read_bytes()),contextsSha256=primary['contextsSha256'],
        findings=5,mainSourcesUnchanged=2,originalTechnicalRequired=2,originalTechnicalFalsePositive=3,
        metadataNegativeVectors=9,currentWholePending=11,referencedRows=2691,noCurrentReference=6557,
        sourceDerivedRaw=9248,wholeF03Accepted=False,productTestsExecuted=0,coverage=None,
        externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()

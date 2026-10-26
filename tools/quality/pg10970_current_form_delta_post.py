"""Independent original-ID set accounting and source/XML binding for a small F03 delta; no analyzer replay."""
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = 'e7c2e2c89c41dcfced875a7fd480e6fc96da0ca6'
OUT = data.BASE/'PG10970-current-form-delta-post-v1'


def contract(delta,expected,summary):
    if delta != expected or summary != dict(raw=9235,main=1512,test=7723,referenced=2724,pending=48,noReference=6511):
        raise ValueError('exact immutable raw/source/context set accounting; no dynamic credit')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    path = data.BASE/'PG10968-current-form-delta-v1/manifest.json'
    primary = data.read_checked(path,'ab7756868701839934166c59efb053380f40467f4c497815385de376357d6e33')
    delta = data.read_checked(path.parent/'delta.json',primary['deltaSha256'])
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    original_by_id = {r['id']:r for r in original}
    parent_path = data.BASE/'PG10834-current-f03-derived-index-v1/manifest.json'
    parent = data.read_checked(parent_path,'0ffc85f61a9fefb4b15d4688c980970324fa671c417985d9f7d7abbcb5fe7055')
    rows = data.read_checked(parent_path.parent/'current-index.json',parent['currentIndexSha256'])
    web_path = data.BASE/'PG10910-current-f03-web-metric-delta-v1/manifest.json'
    web = data.read_checked(web_path,'7c283b56f26f3c73e1b198dee9c91000278b10961713c6de2766c728acf85d66')
    old_delta = data.read_checked(web_path.parent/'delta.json',web['deltaSha256'])
    normal = data.read_checked(data.BASE/'PG10950-form-literal-six-compile-v1/manifest.json',
        '4cd53877ce16c93b44af747c29afdace410d2dc1ce7fec7eb5ebd48a67093baf')
    old_normal = data.read_checked(data.BASE/'PG10892-web-boundary-line-six-compile-v1/manifest.json',
        '345e989275ba9dd52da2356d303c7c1a818feeaf4a41244b6ba05b8e26bf2de9')
    hashes = normal['begin']['inputHashes']
    java = {p:h for p,h in hashes.items() if p.startswith('src/') and p.endswith('.java')}
    assert normal['source'] == SOURCE and normal['actualExit'] == 0 and len(java) == 1810
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    changed = {p:h for p,h in java.items() if h != old_normal['begin']['inputHashes'][p]}
    assert changed == delta['formScope'] and len(changed) == 2
    expected = copy.deepcopy(delta)
    expected.update(source=SOURCE,previousIndexSource=old_normal['source'],replacedContextWarnings=4,
        contextWarningsAddedNet=0,newProductExecutions=0,wholeCurrentAnalyzerReissued=False,
        existingFormIndependentPostSha256='6982240ef677049a33d34597bf14d134b56137afd0bb394132d1f56f6e6de906')
    retained = {r['id'] for r in rows}-set(old_delta['removedFindingIds'])
    assert len(retained) == 9248 and {r['id'] for r in old_delta['freshRows']} <= retained
    base_refs = ({r['id'] for r in rows if r['contextReferences']}-set(old_delta['removedFindingIds']))
    base_refs |= {r['id'] for r in old_delta['freshRows']}|{r['id'] for r in old_delta['legacyContextOverlay']}
    assert len(base_refs) == 2686
    bindings = delta['mainContextBindings']
    assert len(bindings) == len({r['id'] for r in bindings}) == 38
    expected_bindings = []
    for binding in bindings:
        mpath = data.BASE/binding['contextManifest']/'manifest.json'
        m = data.read_checked(mpath,binding['contextManifestSha256'])
        contexts = data.read_checked(mpath.parent/'contexts.json',m['contextsSha256'])
        matches = [r for r in contexts if r['id'] == binding['id']]
        assert m['actualExit'] == 0 and len(matches) == 1
        row = matches[0]
        assert row['id'] in retained and row['id'] not in base_refs
        assert hashes[row['path']] == old_normal['begin']['inputHashes'][row['path']] == row['sourceSha256']
        assert original_by_id[row['id']]['rowSha256'] == row['originalRowSha256']
        expected_bindings.append(dict(id=row['id'],path=row['path'],currentSha256=row['sourceSha256'],
            originalRowSha256=row['originalRowSha256'],contextManifest=binding['contextManifest'],
            contextManifestSha256=binding['contextManifestSha256'],historicalContextSource=m['source'],
            oldRuntimeReassigned=False,currentWholePending=True))
    expected['mainContextBindings'] = expected_bindings
    fresh = delta['freshRows']
    assert len(fresh) == len({r['id'] for r in fresh}) == 4
    static_path = data.BASE/'PG10952-form-literal-static-v1/manifest.json'
    static = data.read_checked(static_path,'1867bf0302e96d03904faa3d800761182628e4ea6be97782f9a436a14f4e37f1')
    xml = (static_path.parent/'pmd.xml').read_bytes()
    assert data.sha(xml) == static['reports']['pmd']['sha256']
    measured = []
    for file in ET.fromstring(xml):
        if file.tag.rpartition('}')[2] != 'file':
            continue
        fpath = str(Path(file.get('name')).relative_to(data.ROOT))
        for node in file:
            if node.tag.rpartition('}')[2] == 'violation':
                measured.append((fpath,dict(node.attrib)))
    assert len(measured) == 4
    for row in fresh:
        assert (row['path'],row['attributes']) in measured and row['rule'] == row['attributes']['rule'] == 'DoNotUseThreads'
        assert row['source'] == SOURCE and row['currentInputSha256'] == hashes[row['path']]
        assert row['id'] in base_refs and row['originalRowSha256'] == original_by_id[row['id']]['rowSha256']
        assert row['derivedStatus'] == 'SOURCE_REBOUND_CURRENT_WHOLE_PENDING'
        assert row['contextReferences'] == ['PG10956_FORM_FINITE_FIXTURE_LOCAL_CURRENT16_PT_NOT_WHOLE451']
    scope_ids = {r['id'] for r in rows if r['path'] in changed}
    removed = scope_ids-{r['id'] for r in fresh}
    assert len(scope_ids) == 17 and len(removed) == 13 and all(original_by_id[i]['rule'] == 'AvoidDuplicateLiterals' for i in removed)
    assert set(delta['removedFindingIds']) == removed
    current_ids = retained-removed
    refs = base_refs|{r['id'] for r in bindings}
    assert not removed&refs and len(set(original_by_id)-current_ids) == 174
    pending = {r['id'] for r in old_delta['legacyContextOverlay']}|{r['id'] for r in bindings}|{r['id'] for r in fresh}
    summary = dict(raw=len(current_ids),main=sum(original_by_id[i]['sourceKind']=='MAIN' for i in current_ids),
        test=sum(original_by_id[i]['sourceKind']=='TEST' for i in current_ids),referenced=len(refs),pending=len(pending),noReference=len(current_ids-refs))
    contract(delta,expected,summary)
    bads = []
    for key,value in [('source','old'),('removedFindingIds',[]),('replacedContextWarnings',8),('newProductExecutions',16),('wholeCurrentAnalyzerReissued',True)]:
        bad = copy.deepcopy(delta)
        bad[key] = value
        bads.append(bad)
    for bad in bads:
        try:
            contract(bad,expected,summary)
        except ValueError:
            pass
        else:
            raise AssertionError('forged scope/source/run accepted')
    assert primary['source'] == SOURCE and primary['sourceDerivedRaw'] == summary['raw'] and primary['actualViolationCount'] is None
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,primaryManifestSha256=data.sha(path.read_bytes()),
        deltaSha256=primary['deltaSha256'],summary=summary,metadataNegativeVectors=len(bads),originalRaw=9409,removedHistoricalIds=174,
        productTestsExecuted=0,coverage=None,oldRuntimeReassigned=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()

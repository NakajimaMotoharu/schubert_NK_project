"""Small immutable current-source delta: form17-to4 plus four pre-existing exact-Main rationale layers."""
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10910_current_f03_web_metric_delta import reconstruct, attrs

SOURCE = 'e7c2e2c89c41dcfced875a7fd480e6fc96da0ca6'
OUT = data.BASE/'PG10968-current-form-delta-v1'
LAYERS = [
    ('PG10916-main-null-crypto-resource-context-v1','d41f3747340987cf0a408a71e2224b07b9ec5f08664b79f687b75b240f19492d',5),
    ('PG10922-main-null-owner-route-context-v1','9360be53ed58a1cf468f0968ca1b91b51fe288a4e217b6576fd342e6c1a88480',5),
    ('PG10928-main-empty-catch-policy-v1','6e1ed0ff67610462fd6d3e0830dc5bd8ccaad18248a7625f351707de9fad340f',15),
    ('PG10934-api-ro-prior-context13-v1','69b5240316368ec534dd837ca1b95b9b8f2cd36af1a87775b165e1e6a780350f',13)]


def inputs():
    parent_path = data.BASE/'PG10834-current-f03-derived-index-v1/manifest.json'
    parent = data.read_checked(parent_path,'0ffc85f61a9fefb4b15d4688c980970324fa671c417985d9f7d7abbcb5fe7055')
    parent_rows = data.read_checked(parent_path.parent/'current-index.json',parent['currentIndexSha256'])
    old_path = data.BASE/'PG10892-web-boundary-line-six-compile-v1/manifest.json'
    old = data.read_checked(old_path,'345e989275ba9dd52da2356d303c7c1a818feeaf4a41244b6ba05b8e26bf2de9')
    web_path = data.BASE/'PG10910-current-f03-web-metric-delta-v1/manifest.json'
    web = data.read_checked(web_path,'7c283b56f26f3c73e1b198dee9c91000278b10961713c6de2766c728acf85d66')
    web_delta = data.read_checked(web_path.parent/'delta.json',web['deltaSha256'])
    normal = data.read_checked(data.BASE/'PG10950-form-literal-six-compile-v1/manifest.json',
        '4cd53877ce16c93b44af747c29afdace410d2dc1ce7fec7eb5ebd48a67093baf')
    post = data.read_checked(data.BASE/'PG10956-form-literal-post-v1/manifest.json',
        '6982240ef677049a33d34597bf14d134b56137afd0bb394132d1f56f6e6de906')
    current = {p:h for p,h in normal['begin']['inputHashes'].items() if p.endswith('.java') and p.startswith('src/')}
    old_input = {p:h for p,h in old['begin']['inputHashes'].items() if p in current}
    assert len(current) == len(old_input) == 1810 and normal['source'] == post['source'] == SOURCE
    assert normal['actualExit'] == normal['testsExecuted'] == post['actualExit'] == 0
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in current.items())
    rows = reconstruct(parent_rows,web_delta,old_input)
    assert len(rows) == 9248
    return rows,current,old_input,post


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    rows,current,old_input,post = inputs()
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    original_by_id = {r['id']:r for r in original}
    indexed = {r['id']:r for r in rows}
    bindings = []
    for folder,digest,count in LAYERS:
        path = data.BASE/folder/'manifest.json'
        manifest = data.read_checked(path,digest)
        values = data.read_checked(path.parent/'contexts.json',manifest['contextsSha256'])
        assert manifest['actualExit'] == 0 and len(values) == count
        for value in values:
            row = indexed[value['id']]
            assert row['sourceKind'] == 'MAIN' and not row['contextReferences']
            assert row['path'] == value['path'] and row['rule'] == value['rule']
            assert current[row['path']] == old_input[row['path']] == value['sourceSha256']
            assert original_by_id[value['id']]['rowSha256'] == value['originalRowSha256']
            row['contextReferences'].append(folder+'_EXACT_MAIN_INPUT_OLD_RUNTIME_NOT_CURRENT')
            row['derivedStatus'] = 'SOURCE_REBOUND_CURRENT_WHOLE_PENDING'
            bindings.append(dict(id=value['id'],path=value['path'],currentSha256=value['sourceSha256'],
                originalRowSha256=value['originalRowSha256'],contextManifest=folder,contextManifestSha256=digest,
                historicalContextSource=manifest['source'],oldRuntimeReassigned=False,currentWholePending=True))
    assert len(bindings) == len({r['id'] for r in bindings}) == 38
    static_path = data.BASE/'PG10952-form-literal-static-v1/manifest.json'
    static = data.read_checked(static_path,'1867bf0302e96d03904faa3d800761182628e4ea6be97782f9a436a14f4e37f1')
    scope = static['sourceHashes']
    assert len(scope) == 2 and {p for p in current if current[p] != old_input[p]} == set(scope)
    assert all(current[p] == h for p,h in scope.items())
    removed_scope = [r for r in rows if r['path'] in scope]
    assert len(removed_scope) == 17 and sum(bool(r['contextReferences']) for r in removed_scope) == 4
    xml = (static_path.parent/'pmd.xml').read_bytes()
    assert data.sha(xml) == static['reports']['pmd']['sha256']
    fresh = []
    for file in ET.fromstring(xml):
        if file.tag.rpartition('}')[2] != 'file':
            continue
        path = str(Path(file.get('name')).relative_to(data.ROOT))
        assert path in scope
        for node in file:
            if node.tag.rpartition('}')[2] != 'violation':
                continue
            matches = [r for r in original if r['path'] == path and r['rule'] == node.get('rule') and
                attrs(r['attributes']) == attrs(node.attrib) and ' '.join(r['message'].split()) == ' '.join((node.text or '').split())]
            assert len(matches) == 1 and node.get('rule') == 'DoNotUseThreads'
            old = indexed[matches[0]['id']]
            assert old['contextReferences'] and old['path'] in scope
            fresh.append(dict(id=old['id'],path=path,rule=node.get('rule'),source=SOURCE,currentInputSha256=scope[path],
                attributes=node.attrib,originalRowSha256=matches[0]['rowSha256'],sourceKind='TEST',
                contextReferences=['PG10956_FORM_FINITE_FIXTURE_LOCAL_CURRENT16_PT_NOT_WHOLE451'],
                historicalContextReferences=old['contextReferences'],derivedStatus='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',
                measurementBinding='EXISTING_PG10952_ACTUAL_STATIC_XML',sourceMeasurementSource=SOURCE))
    assert len(fresh) == len({r['id'] for r in fresh}) == 4
    removed = sorted({r['id'] for r in removed_scope}-{r['id'] for r in fresh})
    assert len(removed) == 13 and all(original_by_id[i]['rule'] == 'AvoidDuplicateLiterals' for i in removed)
    combined = [r for r in rows if r['path'] not in scope]+fresh
    assert len(combined) == len({r['id'] for r in combined}) == 9235
    referenced = sum(bool(r['contextReferences']) for r in combined)
    pending = sum(r['derivedStatus'] == 'SOURCE_REBOUND_CURRENT_WHOLE_PENDING' for r in combined)
    assert referenced == 2724 and pending == 48 and len(combined)-referenced == 6511
    assert Counter(r['sourceKind'] for r in combined) == Counter(MAIN=1512,TEST=7723)
    verify(invocation)
    OUT.mkdir()
    delta = dict(source=SOURCE,previousIndexSource='f24d1649e170e46aafb59a37b9750c602206364c',
        formScope=scope,freshRows=fresh,removedFindingIds=removed,mainContextBindings=bindings,
        existingFormIndependentPostSha256='6982240ef677049a33d34597bf14d134b56137afd0bb394132d1f56f6e6de906',
        replacedContextWarnings=4,contextWarningsAddedNet=0,newProductExecutions=0,wholeCurrentAnalyzerReissued=False)
    data.write(OUT/'delta.json',delta)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),
        sourceCount=1810,changedSourcePaths=2,otherSourcePathsUnchanged=1808,originalRaw=9409,priorDerivedRaw=9248,
        sourceDerivedRaw=9235,mainRaw=1512,testRaw=7723,totalPriorCorrections=174,sourceScopeCorrectionsAlreadyCounted=13,
        joinedContextWarnings=referenced,contextReferences=sum(len(r['contextReferences']) for r in combined),
        sourceReboundCurrentWholePending=pending,noCurrentReferenceInThisJoin=6511,actualViolationCount=None,
        productTestsExecuted=0,coverage=None,externalActions=0,wholeF03Accepted=False,newAccepted=0,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()

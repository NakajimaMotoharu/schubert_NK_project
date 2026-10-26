"""Independent source/row/reference accounting for derived current F03 index; no analyzer/PT replay."""
from collections import Counter,defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = 'e73e9558971a81d30d7f81f6ab0bc5d9662667d2'
OUT = data.BASE/'PG10836-current-f03-derived-index-post-v1'


def contract(rows,original,hashes,removed,references):
    if len(rows) != 9305 or Counter(r['id'] for r in rows) != Counter(set(original)-set(removed)):
        raise ValueError('exact remaining original ids/multiplicity')
    for row in rows:
        old = original[row['id']]
        if row['source'] != SOURCE or row['path'] != old['path'] or row['currentInputSha256'] != hashes.get(old['path']):
            raise ValueError('exact current source/path/input')
        if row['scanner'] != 'pmd' or row['rule'] != old['rule'] or row['sourceKind'] != old['sourceKind'] or row['originalRowSha256'] != old['rowSha256']:
            raise ValueError('original rule/kind/provenance')
        if Counter(row['contextReferences']) != Counter(references.get(row['id'],[])):
            raise ValueError('only exact qualified context references')
        expected = 'CONTEXT_JOINED_NOT_APPLICABLE_NO_DYNAMIC_QUALIFICATION' if references.get(row['id']) else 'NO_CURRENT_REFERENCE_IN_THIS_JOIN_NOT_ASSERTED_VIOLATION'
        if row['derivedStatus'] != expected:
            raise ValueError('unknown is not PASS or established violation')
        if row['measurementBinding'] == 'UNCHANGED_INPUT_FROM_ORIGINAL_FULL_SCAN':
            if old['inputSha256'] != row['currentInputSha256'] or row['attributes'] != old['attributes']:
                raise ValueError('raw unchanged-input warning')
        elif row['measurementBinding'] != 'FRESH_CURRENT_PROTOCOL_SUBSET_PG10806' or not row['path'].startswith('src/schubert-nk-protocol/'):
            raise ValueError('explicit measured replacement scope')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    path = data.BASE/'PG10834-current-f03-derived-index-v1/manifest.json'
    primary = data.read_checked(path,'0ffc85f61a9fefb4b15d4688c980970324fa671c417985d9f7d7abbcb5fe7055')
    assert primary['actualExit'] == 0 and primary['source'] == SOURCE
    assert primary['wholeCurrentAnalyzerReissued'] is primary['wholeF03Accepted'] is False
    assert primary['actualViolationCount'] is None
    rows = data.read_checked(path.parent/'current-index.json',primary['currentIndexSha256'])
    current = data.read_checked(path.parent/'source-inputs.json',primary['sourceInputsSha256'])
    delta = data.read_checked(path.parent/'source-delta.json',primary['sourceDeltaSha256'])
    original_rows = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    original = {r['id']:r for r in original_rows}
    assert len(original_rows) == len(original) == 9409
    old_inputs = data.read_checked(data.BASE/'PG10688-current-global-static-v1/inputs.json',
        '806af97b308508cafb3bc660a1bba74e01aa1ed032f5ce15a35005bf171ce837')
    assert set(current) == set(old_inputs) and len(current) == 1810
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in current.items())
    changed = sorted(p for p,h in current.items() if h != old_inputs[p])
    assert changed == delta['changedSources'] and len(changed) == 17
    assert set(changed) <= set(delta['replacementSourceHashes']) and len(delta['replacementSourceHashes']) == 191
    assert all(current[p] == h for p,h in delta['replacementSourceHashes'].items())
    replaced = [r for r in original_rows if r['path'] in delta['replacementSourceHashes']]
    fresh = [r for r in rows if r['measurementBinding'] == 'FRESH_CURRENT_PROTOCOL_SUBSET_PG10806']
    assert len(replaced) == 114 and len(fresh) == 10
    removed = sorted({r['id'] for r in replaced}-{r['id'] for r in fresh})
    assert removed == delta['removedFindingIds'] and len(removed) == 104
    raw = data.BASE/'PG10806-protocol-quality-module-static-v1/pmd.xml'
    assert data.sha(raw.read_bytes()) == 'cc01d0b34d6d25c70928d802e0d5d816c6e0b77433cba61ed7a7566b7cb8e115'
    signatures = [(str(Path(f.get('name')).relative_to(data.ROOT)),tuple(sorted(n.attrib.items()))) for f in ET.fromstring(raw.read_bytes()) for n in f if n.tag.rpartition('}')[2]=='violation']
    assert Counter(signatures) == Counter((r['path'],tuple(sorted(r['attributes'].items()))) for r in fresh)
    references = defaultdict(list)
    for parent,sha,label,identifier in [
        ('PG10822-global-thread-context-v1','ea2f5a8c9056874991de9a40bf9b9395ad1364be0cf3a0aca941257e855758c8','PG10822/PG10824','id'),
        ('PG10828-classloader-context-v1','38fa14db4463903e7485623a1f4d923eb7b93b25a7236543323474b3b36416db','PG10828/PG10830','id'),
        ('PG10810-protocol-static-context-v1','1fd906c89fcff0804b8f4fb6b3644c850b1e9103108b89048246daf2ef1afadb','PG10810/PG10814','originalFindingId')]:
        meta = data.read_checked(data.BASE/parent/'manifest.json',sha)
        key = 'dispositionsSha256' if identifier == 'id' else 'contextsSha256'
        file = 'dispositions.json' if identifier == 'id' else 'contexts.json'
        for r in data.read_checked(data.BASE/parent/file,meta[key]):
            assert r['sourceSha256'] == current[r['path']]
            references[r[identifier]].append(label)
    json_meta = data.read_checked(data.BASE/'PG10726-json-peek-locale-context-v1/manifest.json',
        '412995d03337a68d8e8b2ab5f1462bfb429e4bb362d2e11c73444b8438bb6726')
    for r in data.read_checked(data.BASE/'PG10726-json-peek-locale-context-v1/contexts.json',json_meta['rowsSha256']):
        if r['originalFinding']['rule']=='UnusedReturnValue':
            assert r['sourceSha256'] == current[r['originalFinding']['path']]
            references[r['originalFinding']['id']].append('PG10726/PG10728')
    contract(rows,original,current,removed,references)
    assert len(references) == 2679 and sum(map(len,references.values())) == 2681
    assert Counter(r['sourceKind'] for r in rows) == Counter(MAIN=1512,TEST=7793)
    bads = [rows[:-1],rows+[rows[0]]]
    for field,value in [('id','unknown'),('currentInputSha256','0'*64),('source','old-source'),('rule','unknown'),
        ('contextReferences',['FAKE']),('derivedStatus','PASS'),('measurementBinding','WHOLE_CURRENT_SCAN')]:
        bad = [dict(rows[0]),*rows[1:]]
        bad[0][field] = value
        bads.append(bad)
    for bad in bads:
        try: contract(bad,original,current,removed,references)
        except ValueError: pass
        else: raise AssertionError('incomplete/stale/false classification accepted')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        primaryManifestSha256=data.sha(path.read_bytes()),originalRaw=9409,sourceDerivedRaw=9305,
        original114ReplacedByCurrent10=True,actualSourceScopeCorrections=104,joinedContextWarnings=2679,
        noCurrentReferenceInThisJoin=6626,contextReferences=2681,changedSources=17,allJavaSources=1810,
        metadataNegativeVectors=len(bads),wholeCurrentAnalyzerReissued=False,wholeF03Accepted=False,
        actualViolationCount=None,productTestsExecuted=0,newAccepted=0,formalUpdated=False,effortPercent=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()

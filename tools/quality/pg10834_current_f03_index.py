"""Source-derived current F03 index; immutable full baseline plus exact measured subset replacements."""
from collections import Counter
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = 'e73e9558971a81d30d7f81f6ab0bc5d9662667d2'
OUT = data.BASE/'PG10834-current-f03-derived-index-v1'


def attrs(value):
    return {k:v for k,v in value.items() if k not in ('beginline','endline','begincolumn','endcolumn')}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    baseline = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    old_inputs = data.read_checked(data.BASE/'PG10688-current-global-static-v1/inputs.json',
        '806af97b308508cafb3bc660a1bba74e01aa1ed032f5ce15a35005bf171ce837')
    normal = data.read_checked(data.BASE/'PG10800-protocol-quality-six-compile-v1/manifest.json',
        'ee02e1c29144a78486897564d0840a86c90bfe96f6fd19f5f75af8fbe4d311b4')
    assert normal['source'] == SOURCE and normal['actualExit'] == 0
    current = {p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/') and p.endswith('.java')}
    assert set(current) == set(old_inputs) and len(current) == 1810
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in current.items())
    graph = data.read_checked(data.BASE/'PG10716-graph-constants-static-v1/manifest.json',
        '9bc20c08a83b293bb25c83998ebae4b332d273c42e6e975ad966283bc260a4fd')
    protocol_path = data.BASE/'PG10806-protocol-quality-module-static-v1/manifest.json'
    protocol = data.read_checked(protocol_path,'21e4e7d595f27d5404a7bf2c97405bd18f41cce0a7ad934de29eb3983ab2368f')
    assert graph['actualExit'] == 0 and all(r['findings'] == r['processingErrors'] == 0 for r in graph['reports'].values())
    assert len(graph['sourceHashes']) == 3 and protocol['source'] == SOURCE and protocol['actualExit'] == 1
    replacement = {**graph['sourceHashes'],**protocol['sourceHashes']}
    assert len(protocol['sourceHashes']) == 188 and len(replacement) == 191
    assert all(current[p] == h for p,h in replacement.items())
    changed = {p for p,h in current.items() if h != old_inputs[p]}
    assert changed <= set(replacement)
    assert all(current[p] == h for p,h in old_inputs.items() if p not in replacement)
    removed_scope = [r for r in baseline if r['path'] in replacement]
    assert len(baseline) == 9409 and len(removed_scope) == 114
    rows = []
    for old in baseline:
        if old['path'] in replacement: continue
        assert old['inputSha256'] == current[old['path']]
        rows.append(dict(id=old['id'],originalRowSha256=old['rowSha256'],path=old['path'],scanner=old['scanner'],rule=old['rule'],
            sourceKind=old['sourceKind'],source=SOURCE,currentInputSha256=current[old['path']],attributes=old['attributes'],
            measurementBinding='UNCHANGED_INPUT_FROM_ORIGINAL_FULL_SCAN',contextReferences=[]))
    raw = protocol_path.parent/'pmd.xml'
    assert data.sha(raw.read_bytes()) == protocol['reports']['pmd']['sha256']
    for file in ET.fromstring(raw.read_bytes()):
        if file.tag.rpartition('}')[2] != 'file': continue
        path = str(Path(file.get('name')).relative_to(data.ROOT))
        for node in file:
            if node.tag.rpartition('}')[2] != 'violation': continue
            matches = [r for r in removed_scope if r['path'] == path and r['rule'] == node.get('rule')
                and attrs(r['attributes']) == attrs(node.attrib) and ' '.join(r['message'].split()) == ' '.join((node.text or '').split())]
            assert len(matches) == 1
            old = matches[0]
            rows.append(dict(id=old['id'],originalRowSha256=old['rowSha256'],path=path,scanner='pmd',rule=node.get('rule'),
                sourceKind=old['sourceKind'],source=SOURCE,currentInputSha256=current[path],attributes=node.attrib,
                measurementBinding='FRESH_CURRENT_PROTOCOL_SUBSET_PG10806',contextReferences=[]))
    assert len(rows) == 9305 and len({r['id'] for r in rows}) == len(rows)
    by_id = {r['id']:r for r in rows}
    def attach(identity,path,digest,rule,proof):
        row = by_id[identity]
        assert row['path'] == path and row['currentInputSha256'] == digest and row['rule'] == rule
        assert proof not in row['contextReferences']
        row['contextReferences'].append(proof)
    threads = data.read_checked(data.BASE/'PG10822-global-thread-context-v1/manifest.json',
        'ea2f5a8c9056874991de9a40bf9b9395ad1364be0cf3a0aca941257e855758c8')
    for r in data.read_checked(data.BASE/'PG10822-global-thread-context-v1/dispositions.json',threads['dispositionsSha256']):
        assert r['source'] == SOURCE and r['qualityGatePass'] is False
        attach(r['id'],r['path'],r['sourceSha256'],r['rule'],'PG10822/PG10824')
    loaders = data.read_checked(data.BASE/'PG10828-classloader-context-v1/manifest.json',
        '38fa14db4463903e7485623a1f4d923eb7b93b25a7236543323474b3b36416db')
    for r in data.read_checked(data.BASE/'PG10828-classloader-context-v1/dispositions.json',loaders['dispositionsSha256']):
        assert r['source'] == SOURCE and r['qualityGatePass'] is False
        attach(r['id'],r['path'],r['sourceSha256'],r['rule'],'PG10828/PG10830')
    contexts = data.read_checked(data.BASE/'PG10810-protocol-static-context-v1/manifest.json',
        '1fd906c89fcff0804b8f4fb6b3644c850b1e9103108b89048246daf2ef1afadb')
    for r in data.read_checked(data.BASE/'PG10810-protocol-static-context-v1/contexts.json',contexts['contextsSha256']):
        assert r['source'] == SOURCE
        attach(r['originalFindingId'],r['path'],r['sourceSha256'],r['rule'],'PG10810/PG10814')
    json_meta = data.read_checked(data.BASE/'PG10726-json-peek-locale-context-v1/manifest.json',
        '412995d03337a68d8e8b2ab5f1462bfb429e4bb362d2e11c73444b8438bb6726')
    for r in data.read_checked(data.BASE/'PG10726-json-peek-locale-context-v1/contexts.json',json_meta['rowsSha256']):
        old = r['originalFinding']
        if old['rule'] == 'UnusedReturnValue':
            attach(old['id'],old['path'],r['sourceSha256'],old['rule'],'PG10726/PG10728')
    for row in rows:
        row['derivedStatus'] = 'CONTEXT_JOINED_NOT_APPLICABLE_NO_DYNAMIC_QUALIFICATION' if row['contextReferences'] else 'NO_CURRENT_REFERENCE_IN_THIS_JOIN_NOT_ASSERTED_VIOLATION'
    joined = [r for r in rows if r['contextReferences']]
    pending = [r for r in rows if not r['contextReferences']]
    assert len(joined) == 2679 and len(pending) == 6626
    assert sum(len(r['contextReferences']) for r in rows) == 2681
    assert {r['id'] for r in rows if len(r['contextReferences']) == 2} == {'PMD-06789','PMD-06790'}
    removed_ids = sorted({r['id'] for r in baseline}-set(by_id))
    assert len(removed_ids) == 104
    verify(invocation)
    OUT.mkdir()
    with (OUT/'current-index.json').open('x') as stream:
        json.dump(rows,stream,sort_keys=True,separators=(',',':'))
        stream.write('\n')
    data.write(OUT/'source-inputs.json',current)
    data.write(OUT/'source-delta.json',dict(changedSources=sorted(changed),replacementSourceHashes=replacement,removedFindingIds=removed_ids))
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        currentIndexSha256=data.sha((OUT/'current-index.json').read_bytes()),sourceInputsSha256=data.sha((OUT/'source-inputs.json').read_bytes()),
        sourceDeltaSha256=data.sha((OUT/'source-delta.json').read_bytes()),originalRaw=9409,sourceDerivedRaw=9305,
        oldReplacementWarnings=114,currentSubsetWarnings=10,removedWarningIds=104,sourceCount=1810,changedSources=len(changed),
        replacementSources=191,unchangedOtherSources=1619,scannerCounts=dict(Counter(r['scanner'] for r in rows)),
        sourceKindCounts=dict(Counter(r['sourceKind'] for r in rows)),joinedContextWarnings=2679,contextReferences=2681,
        noCurrentReferenceInThisJoin=6626,unjoinedRuleCounts=dict(Counter(r['rule'] for r in pending)),
        actualViolationCount=None,applicabilityOutsideCurrentJoinUnknown=True,wholeCurrentAnalyzerReissued=False,
        productTestsExecuted=0,coverage=None,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None,externalActions=0))
    print(dict(actualExit=0,derivedRaw=9305,joined=2679,noCurrentReference=6626,changedSources=len(changed),
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes())))


if __name__ == '__main__':
    main()

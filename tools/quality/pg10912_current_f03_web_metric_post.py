"""Independent F03 delta/source/legacy statement checks; no analyzer, PT or VM execution."""
from collections import Counter
import copy
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10398_role_view_preflight import canonical

SOURCE = 'f24d1649e170e46aafb59a37b9750c602206364c'
OUT = data.BASE/'PG10912-current-f03-web-metric-post-v1'


def check(delta,parent,current,scope,fresh_signatures):
    if delta['source'] != SOURCE or set(delta['replacedSourcePaths']) != set(scope):
        raise ValueError('exact current source/replaced scope')
    old_by_id = {r['id']:r for r in parent}
    if len(delta['freshRows']) != 17 or len({r['id'] for r in delta['freshRows']}) != 17:
        raise ValueError('all fresh17 exact unique IDs')
    signatures = []
    for row in delta['freshRows']:
        old = old_by_id.get(row['id'])
        if old is None or old['path'] != row['path'] or row['path'] not in scope:
            raise ValueError('existing finding in exact replaced source')
        if row['source'] != SOURCE or row['currentInputSha256'] != current[row['path']] or row['originalRowSha256'] != old['originalRowSha256']:
            raise ValueError('exact source bytes/original row')
        if row['rule'] != old['rule'] or row['contextReferences'] != ['PG10900/PG10902'] or row['derivedStatus'] != 'CONTEXT_JOINED_NOT_APPLICABLE_NO_DYNAMIC_QUALIFICATION':
            raise ValueError('no fake rule/context/PASS')
        signatures.append((row['path'],tuple(sorted(row['attributes'].items()))))
    if Counter(signatures) != Counter(fresh_signatures):
        raise ValueError('exact current XML coordinates')
    fresh_ids = {r['id'] for r in delta['freshRows']}
    removed = {r['id'] for r in parent if r['path'] in scope}-fresh_ids
    if len(delta['removedFindingIds']) != 57 or set(delta['removedFindingIds']) != removed:
        raise ValueError('only truly vanished57 original IDs')
    legacy = delta['legacyContextOverlay']
    if len(legacy) != 6 or len({r['id'] for r in legacy}) != 6:
        raise ValueError('six original legacy refs once')
    for row in legacy:
        old = old_by_id.get(row['id'])
        if old is None or row['path'] != old['path'] or row['sourceSha256'] != current[row['path']] or row['rule'] != old['rule']:
            raise ValueError('exact legacy finding/current input')
        if row['disposition'] != 'SOURCE_REBOUND_CURRENT_WHOLE_PENDING' or row['currentWholeJoinPending'] is not True or row['currentWholeCaseRefs'] != [] or row['priorRuntimeReassigned'] is not False or row['rawWarningRetained'] is not True:
            raise ValueError('historical review is not current whole/runtime PASS')
        if row['currentCoordinates'] != old['attributes'] or row['originalRowSha256'] != old['originalRowSha256']:
            raise ValueError('original current finding coordinates/provenance')
    if delta['oldMetricRuntimeReassigned'] or delta['newProductExecutions'] or delta['wholeCurrentAnalyzerReissued']:
        raise ValueError('no dynamic success or full analyzer replay')
    return removed


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    path = data.BASE/'PG10910-current-f03-web-metric-delta-v1/manifest.json'
    primary = data.read_checked(path,'7c283b56f26f3c73e1b198dee9c91000278b10961713c6de2766c728acf85d66')
    delta = data.read_checked(path.parent/'delta.json',primary['deltaSha256'])
    prior_path = data.BASE/'PG10834-current-f03-derived-index-v1/manifest.json'
    prior = data.read_checked(prior_path,primary['parentManifestSha256'])
    parent = data.read_checked(prior_path.parent/'current-index.json',prior['currentIndexSha256'])
    inputs = data.read_checked(prior_path.parent/'source-inputs.json',prior['sourceInputsSha256'])
    normal = data.read_checked(data.BASE/'PG10892-web-boundary-line-six-compile-v1/manifest.json',primary['currentNormalManifestSha256'])
    current = {p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/') and p.endswith('.java')}
    assert primary['actualExit'] == normal['actualExit'] == 0 and primary['source'] == normal['source'] == SOURCE
    assert set(inputs) == set(current) and len(current) == 1810
    actual_delta = {p:h for p,h in current.items() if inputs[p] != h}
    assert actual_delta == delta['sourceInputDelta'] and len(actual_delta) == 8
    assert all('/schubert-nk-web/src/test/java/' in p for p in actual_delta)
    assert dict(inputs,**actual_delta) == current
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in current.items())
    raw_path = data.BASE/'PG10894-web-boundary-line-static-v1/manifest.json'
    raw = data.read_checked(raw_path,primary['freshWebStaticManifestSha256'])
    assert data.sha((raw_path.parent/'pmd.xml').read_bytes()) == raw['reports']['pmd']['sha256']
    signatures = [(str(Path(f.get('name')).relative_to(data.ROOT)),tuple(sorted(n.attrib.items())))
        for f in ET.parse(raw_path.parent/'pmd.xml').getroot() for n in f if n.tag.rpartition('}')[2] == 'violation']
    removed = check(delta,parent,current,raw['sourceHashes'],signatures)
    # Reconstruct by original ID replacement instead of producer's source-scope list append.
    old_by_id = {r['id']:r for r in parent}
    new_by_id = {r['id']:r for r in delta['freshRows']}
    active = {identity:row for identity,row in old_by_id.items() if identity not in removed}
    active.update(new_by_id)
    assert len(active) == 9248 and set(active) == set(old_by_id)-removed
    references = {identity:list(row['contextReferences']) for identity,row in active.items()}
    for row in delta['legacyContextOverlay']:
        references[row['id']].append('PG7014/1544/PG7016_EXACT_SOURCE_HISTORICAL')
    assert sum(bool(v) for v in references.values()) == 2686
    assert sum(len(v) for v in references.values()) == 2688
    assert sum(not v for v in references.values()) == 6562
    prior_static = data.read_checked(data.BASE/'PG7014-metric-catalog-post-v1/manifest.json',primary['legacyStaticManifestSha256'])
    closed = {'detailedMetricsEnabled':'boolean','retentionDays':'int','retentionBytes':'long'}
    reused,reauthenticated = [],[]
    for row in delta['legacyContextOverlay']:
        p = row['path']
        if row['sourceRebindMode'] == 'EXACT_WHOLE_FILE_SOURCE_REUSE':
            assert p.endswith('/MetricContract.java') and row['statementBinding'] is None
            assert current[p] == prior_static['sourceFiles'][p] and row['priorDisposition'] == 'REQUIRED_CONTRACT'
            reused.append(row['id'])
        else:
            assert row['sourceRebindMode'] == 'EXACT_STATEMENTS_REBOUND_SOURCE_CHANGED' and p.endswith('/MonitoringModePolicy.java')
            binding = row['statementBinding']
            assert binding['priorSourceSha256'] == prior_static['sourceFiles'][p] != binding['currentSourceSha256'] == current[p]
            name = row['currentCoordinates']['variable']
            kind = closed[name]
            expected = ['private final '+kind+' '+name+';', 'public '+kind+' '+name+'() { return '+name+'; }']
            assert kind == binding['primitiveType']
            assert [canonical(v) for v in binding['declarationAndGetter']] == [canonical(v) for v in expected]
            before = subprocess.check_output(['git','show',prior_static['source']+':'+p],cwd=data.ROOT)
            assert data.sha(before) == binding['priorSourceSha256']
            for text in (before.decode(),(data.ROOT/p).read_text()):
                tokens = canonical(text)
                for expected_statement in expected:
                    needle = canonical(expected_statement)
                    assert sum(tokens[i:i+len(needle)] == needle for i in range(len(tokens)-len(needle)+1)) == 1
            reauthenticated.append(row['id'])
    assert len(reused) == len(reauthenticated) == 3
    bads = []
    for edit in [
        lambda v:v.update(source='wrong'),
        lambda v:v['freshRows'].pop(),
        lambda v:v['freshRows'].append(v['freshRows'][0]),
        lambda v:v['freshRows'][0].update(currentInputSha256='0'*64),
        lambda v:v['freshRows'][0].update(contextReferences=['FAKE']),
        lambda v:v['legacyContextOverlay'][0].update(disposition='PASS'),
        lambda v:v['legacyContextOverlay'][0].update(priorRuntimeReassigned=True),
        lambda v:v.update(removedFindingIds=[]),
        lambda v:v.update(newProductExecutions=1)]:
        bad = copy.deepcopy(delta)
        edit(bad)
        try: check(bad,parent,current,raw['sourceHashes'],signatures)
        except ValueError: bads.append(True)
        else: raise AssertionError('incomplete/forged/source-transfer delta accepted')
    assert len(bads) == 9
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        primaryManifestSha256=data.sha(path.read_bytes()),deltaSha256=primary['deltaSha256'],
        sourceDerivedRaw=9248,parentRaw=9305,alreadyCountedCorrections=57,currentReferencedRows=2686,
        notApplicableContextReferences=2680,currentWholePending=6,noCurrentReference=6562,
        exactWholeSourceLegacyReuseIds=reused,changedSourceStatementReauthenticationIds=reauthenticated,
        metadataNegativeVectors=9,allJavaSources=1810,sourceInputDelta=8,otherSourcePathsUnchanged=1802,
        actualViolationCount=None,wholeF03Accepted=False,wholeCurrentAnalyzerReissued=False,productTestsExecuted=0,
        coverage=None,formalUpdated=False,newAccepted=0,effortPercent=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()

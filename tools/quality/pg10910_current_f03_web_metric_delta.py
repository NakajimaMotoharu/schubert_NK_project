"""Immutable F03 delta: exact Web remeasurement plus six existing metric-context references; no Product run."""
from collections import Counter
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = 'f24d1649e170e46aafb59a37b9750c602206364c'
OUT = data.BASE/'PG10910-current-f03-web-metric-delta-v1'
PARENT = '0ffc85f61a9fefb4b15d4688c980970324fa671c417985d9f7d7abbcb5fe7055'


def attrs(value):
    return {k:v for k,v in value.items() if k not in ('beginline','endline','begincolumn','endcolumn')}


def reconstruct(parent,delta,current):
    scopes = set(delta['replacedSourcePaths'])
    legacy = {r['id']:r for r in delta['legacyContextOverlay']}
    result = []
    for old in parent:
        if old['path'] in scopes: continue
        assert old['currentInputSha256'] == current[old['path']]
        row = dict(old,source=SOURCE,contextReferences=list(old['contextReferences']),
            sourceMeasurementSource=old['source'],originalMeasurementBinding=old['measurementBinding'],
            measurementBinding='REUSED_EXACT_INPUT_FROM_PARENT_INDEX')
        if row['id'] in legacy:
            row['contextReferences'].append('PG7014/1544/PG7016_EXACT_SOURCE_HISTORICAL')
            row['derivedStatus'] = 'SOURCE_REBOUND_CURRENT_WHOLE_PENDING'
        result.append(row)
    result += delta['freshRows']
    return result


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    parent_path = data.BASE/'PG10834-current-f03-derived-index-v1/manifest.json'
    parent = data.read_checked(parent_path,PARENT)
    rows = data.read_checked(parent_path.parent/'current-index.json',parent['currentIndexSha256'])
    old_inputs = data.read_checked(parent_path.parent/'source-inputs.json',parent['sourceInputsSha256'])
    normal_path = data.BASE/'PG10892-web-boundary-line-six-compile-v1/manifest.json'
    normal = data.read_checked(normal_path,'345e989275ba9dd52da2356d303c7c1a818feeaf4a41244b6ba05b8e26bf2de9')
    assert normal['actualExit'] == normal['testsExecuted'] == 0 and normal['source'] == SOURCE
    current = {p:h for p,h in normal['begin']['inputHashes'].items() if p.startswith('src/') and p.endswith('.java')}
    assert set(current) == set(old_inputs) and len(current) == 1810
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in current.items())
    web_path = data.BASE/'PG10894-web-boundary-line-static-v1/manifest.json'
    web = data.read_checked(web_path,'7f77e05354f41debaaf0a7b767a2fc1acb55c863b54771e9a439418e7cf2d140')
    assert web['source'] == SOURCE and web['actualExit'] == 1 and web['reports']['pmd']['findings'] == 17
    scope = web['sourceHashes']
    assert len(scope) == 8 and all(current[p] == h for p,h in scope.items())
    changed = {p:h for p,h in current.items() if h != old_inputs[p]}
    assert set(changed) == set(scope)
    removed_scope = [r for r in rows if r['path'] in scope]
    assert len(removed_scope) == 74
    context_path = data.BASE/'PG10900-web-view-context-v1/manifest.json'
    context = data.read_checked(context_path,'6c250409c3b0f780be51558e623abe2a8c9035930ab7d6dc773c1cea361e1fc5')
    contexts = data.read_checked(context_path.parent/'contexts.json',context['contextsSha256'])
    context_ids = {r['originalFindingId'] for r in contexts}
    assert context['source'] == SOURCE and context['actualExit'] == 0 and len(contexts) == len(context_ids) == 17
    raw = web_path.parent/'pmd.xml'
    assert data.sha(raw.read_bytes()) == web['reports']['pmd']['sha256']
    original_path = data.BASE/'PG10690-current-global-static-post-v1/findings.json'
    original = data.read_checked(original_path,'92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    fresh = []
    for file in ET.fromstring(raw.read_bytes()):
        if file.tag.rpartition('}')[2] != 'file': continue
        path = str(Path(file.get('name')).relative_to(data.ROOT))
        for node in file:
            if node.tag.rpartition('}')[2] != 'violation': continue
            matches = [r for r in original if r['path'] == path and r['rule'] == node.get('rule') and
                attrs(r['attributes']) == attrs(node.attrib) and ' '.join(r['message'].split()) == ' '.join((node.text or '').split())]
            assert len(matches) == 1
            old = matches[0]
            assert old['id'] in context_ids
            fresh.append(dict(id=old['id'],originalRowSha256=old['rowSha256'],path=path,scanner='pmd',rule=node.get('rule'),
                sourceKind='TEST',source=SOURCE,currentInputSha256=current[path],attributes=node.attrib,
                measurementBinding='FRESH_WEB_SUBSET_PG10894',sourceMeasurementSource=SOURCE,
                contextReferences=['PG10900/PG10902'],derivedStatus='CONTEXT_JOINED_NOT_APPLICABLE_NO_DYNAMIC_QUALIFICATION'))
    assert len(fresh) == 17 and {r['id'] for r in fresh} == context_ids
    prior_path = data.BASE/'PG7014-metric-catalog-post-v1/manifest.json'
    prior = data.read_checked(prior_path,'3e0f98bf55ff1277289326e48578abca7fc65cfe1e5f0c8f593307a6f6dc2b1d')
    oracle_path = data.BASE/'PG7016-metric-oracle-audit-v1/manifest.json'
    oracle = data.read_checked(oracle_path,'a5c2abeffb8d5fed963dd1c979e826344a6a4adad313fbe992c62be0bc02d752')
    assert prior['actualExit'] == oracle['actualExit'] == 0 and prior['source'] == oracle['source']
    assert oracle['matchedMetrics'] == 26 and oracle['productionMethodUsedForExpected'] is False
    assert data.sha((data.ROOT/oracle['fixture']['path']).read_bytes()) == oracle['fixture']['sha256']
    canonical_design = subprocess.check_output(['git','show','origin/main:'+oracle['design']['path']],cwd=data.ROOT)
    assert data.sha(canonical_design) == oracle['design']['sha256']
    review = data.ROOT/'evidence/01_PT/018_NK-OPS-001/1544_MetricContract_実行結果.md'
    assert data.sha(review.read_bytes()) == '0363a731be2cbdef9e57b712465a8d010bd37367e0b0fcc06b418073e7babb46'
    review_text = review.read_text()
    assert 'MetricContract13 service重複4|REQUIRED_CONTRACT' in review_text
    assert '同26 retentionDays|CONTEXT_NOT_APPLICABLE' in review_text
    legacy = []
    for old in prior['staticRaw']['pmd']['findings']:
        class_name = old['class']
        matching_paths = [p for p in prior['sourceFiles'] if p.endswith('/'+class_name+'.java')]
        assert len(matching_paths) == 1
        path = matching_paths[0]
        if prior['sourceFiles'][path] == current[path]:
            rebind_mode = 'EXACT_WHOLE_FILE_SOURCE_REUSE'
            statement_binding = None
        else:
            assert class_name == 'MonitoringModePolicy' and old['rule'] == 'AvoidFieldNameMatchingMethodName'
            before = subprocess.check_output(['git','show',prior['source']+':'+path],cwd=data.ROOT).decode()
            after = (data.ROOT/path).read_text()
            assert data.sha(before.encode()) == prior['sourceFiles'][path] and data.sha(after.encode()) == current[path]
            name = old['variable']
            kind = {'detailedMetricsEnabled':'boolean','retentionDays':'int','retentionBytes':'long'}[name]
            declaration = r'private\s+final\s+'+kind+r'\s+'+re.escape(name)+r'\s*;'
            getter = r'public\s+'+kind+r'\s+'+re.escape(name)+r'\(\)\s*\{\s*return\s+'+re.escape(name)+r'\s*;\s*\}'
            tokens = []
            for text in (before,after):
                field = re.findall(declaration,text)
                method = re.findall(getter,text)
                assert len(field) == len(method) == 1
                tokens.append([re.sub(r'\s+',' ',v).strip() for v in [field[0],method[0]]])
            assert tokens[0] == tokens[1]
            rebind_mode = 'EXACT_STATEMENTS_REBOUND_SOURCE_CHANGED'
            statement_binding = dict(priorSourceSha256=prior['sourceFiles'][path],currentSourceSha256=current[path],
                declarationAndGetter=tokens[0],primitiveType=kind,priorCoordinates={k:old[k] for k in ('beginline','endline','begincolumn','endcolumn')},
                scope='THREE_FINAL_PRIMITIVE_READ_ONLY_ACCESSORS_ONLY_NOT_NEW_MODE_BEHAVIOR')
        diagnostic = {k:v for k,v in old.items() if k != 'message'}
        matches = [r for r in original if r['path'] == path and r['rule'] == old['rule'] and
            attrs(r['attributes']) == attrs(diagnostic) and ' '.join(r['message'].split()) == ' '.join(old['message'].split())]
        assert len(matches) == 1
        old_row = matches[0]
        assert old_row['inputSha256'] == current[path]
        prior_disposition = 'REQUIRED_CONTRACT' if class_name == 'MetricContract' else 'CONTEXT_NOT_APPLICABLE'
        assert prior_disposition in review_text
        if rebind_mode == 'EXACT_WHOLE_FILE_SOURCE_REUSE':
            assert old_row['attributes'] == diagnostic
        legacy.append(dict(id=old_row['id'],path=path,sourceSha256=current[path],rule=old_row['rule'],
            sourceRebindMode=rebind_mode,statementBinding=statement_binding,currentCoordinates=old_row['attributes'],
            originalRowSha256=old_row['rowSha256'],priorSource=prior['source'],priorDisposition=prior_disposition,
            disposition='SOURCE_REBOUND_CURRENT_WHOLE_PENDING',currentWholeJoinPending=True,currentWholeCaseRefs=[],
            priorManifestSha256=data.sha(prior_path.read_bytes()),reviewSha256=data.sha(review.read_bytes()),
            priorRuntimeReassigned=False,rawWarningRetained=True))
    assert len(legacy) == 6 and len({r['id'] for r in legacy}) == 6
    delta = dict(source=SOURCE,parentSource=parent['source'],parentManifestSha256=PARENT,
        replacedSourcePaths=sorted(scope),sourceInputDelta=changed,freshRows=fresh,legacyContextOverlay=legacy,
        removedFindingIds=sorted({r['id'] for r in removed_scope}-{r['id'] for r in fresh}),
        oldScopeFindings=74,newScopeFindings=17,wholeCurrentAnalyzerReissued=False,
        oldMetricRuntimeReassigned=False,newProductExecutions=0)
    built = reconstruct(rows,delta,current)
    assert len(built) == len({r['id'] for r in built}) == 9248
    assert len(delta['removedFindingIds']) == 57
    joined = [r for r in built if r['contextReferences']]
    pending = [r for r in built if not r['contextReferences']]
    assert len(joined) == 2686 and len(pending) == 6562
    assert sum(len(r['contextReferences']) for r in built) == 2688
    assert Counter(r['derivedStatus'] for r in built)['SOURCE_REBOUND_CURRENT_WHOLE_PENDING'] == 6
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'delta.json',delta)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        parentManifestSha256=PARENT,deltaSha256=data.sha((OUT/'delta.json').read_bytes()),
        currentNormalManifestSha256=data.sha(normal_path.read_bytes()),freshWebStaticManifestSha256=data.sha(web_path.read_bytes()),
        sourceDerivedRaw=9248,priorDerivedRaw=9305,sourceScopeCorrectionsAlreadyCounted=57,
        oldScopeFindings=74,newScopeFindings=17,sourceCount=1810,changedFromParentSources=8,unchangedParentSourcePaths=1802,
        joinedContextWarnings=2686,contextReferences=2688,notApplicableContextReferences=2680,
        sourceReboundCurrentWholePending=6,noCurrentReferenceInThisJoin=6562,
        pendingRuleCounts=dict(Counter(r['rule'] for r in pending)),actualViolationCount=None,
        priorMetricContextReuseOnly=6,newMetricCorrections=0,originalRaw=9409,totalPriorCorrections=161,
        legacyStaticManifestSha256=data.sha(prior_path.read_bytes()),legacyOracleManifestSha256=data.sha(oracle_path.read_bytes()),
        productTestsExecuted=0,coverage=None,externalActions=0,wholeCurrentAnalyzerReissued=False,
        wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(dict(actualExit=0,derivedRaw=9248,referenced=2686,sourceReboundPending=6,noReference=6562,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes())))


if __name__ == '__main__':
    main()

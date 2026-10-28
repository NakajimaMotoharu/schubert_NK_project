"""Current two-source oracle PG binding; no warning removals, runtime reassignment or owner/cost changes."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg13324_state_oracle_config as cfg
from pg9954_pure_query_registry_metadata import INV,SNAP
from pg9338_wbs_reference_metadata_post import validate as validate_docs
from pg9880_snapshot_nonce_trace import audit
from f03_literal_batch_trace import documents

SOURCE = '703876e73d6ec1bd06229a8b9a119e66d8d99a30'
OUT = data.BASE/'PG13336-state-oracle-v1'
POST = data.BASE/'PG13337-state-oracle-v1'

def state_after():
    ids,refs,pending = cfg.PREVIOUS_STATE()
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    scope = {r['id'] for r in original if r['id'] in ids and r['path'] in cfg.SPECS};assert len(scope) == 54
    return ids,refs,pending|(scope&refs)

def inputs():
    prior = data.read_checked(data.BASE/cfg.PRIOR_TRACE[0]/'manifest.json',cfg.PRIOR_TRACE[1])
    n = data.read_checked(data.BASE/'PG13330-state-oracle-v1/manifest.json','1d4bc617cab74a361cb8222a563e8080cc67857546d71525a49d224cb7b6ddb2')
    p = data.read_checked(data.BASE/'PG13334-state-oracle-source-post-v1/manifest.json','8e20e5c61cc3f92f96bebaa8cd6ac8dedc9ac6cb7ba190d881960a2e953e98d1')
    s = data.read_checked(data.BASE/'PG13335-state-oracle-v1/manifest.json','3ffd53a0802109b74ef0cf37b55931b5a6b76f944269c6e339593d0202bc244c')
    assert n['source'] == p['source'] == s['source'] == SOURCE and n['actualExit'] == p['actualExit'] == s['actualExit'] == n['testsExecuted'] == 0
    assert p['oracleCallsCorrected'] == len(p['independentUiDomainCases']) == 8
    assert p['newPrivateHelperMethods'] == 2 and p['newPrivateFields'] == p['productTestsExecuted'] == 0
    assert p['allMainPhysicalUnchanged'] == 1843 and p['currentTestPhysical'] == 1974 and p['newTestPhysical'] == 0 and p['diagnosticMultisetUnchanged']
    hashes = n['begin']['inputHashes'];assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in hashes.items())
    assert {r['path'] for r in prior['sourceRows'] if r['sha256'] != hashes[r['path']]} == set(cfg.SPECS)
    for path,spec in cfg.SPECS.items():
        row, = [r for r in prior['sourceRows'] if r['path'] == path];assert row['sha256'] == spec['sha256'] and row['canonicalOwner'] == row['canonicalCostOwner'] == spec['owner']
    raw,snap = [subprocess.check_output(['git','show',SOURCE+':'+path],cwd=data.ROOT) for path in [INV,SNAP]]
    return prior,p,hashes,raw,snap

def expected(prior,p,hashes):
    v = copy.deepcopy(prior)
    for k in ['invocation','wholeWbsAuditBefore']:v.pop(k,None)
    rows = copy.deepcopy(prior['sourceRows'])
    for r in rows:
        if r['path'] in cfg.SPECS:r['sha256'] = hashes[r['path']]
    ids,refs,pending = state_after()
    v.update(source=SOURCE,sourceRows=rows,modifiedTestPaths=sorted(cfg.SPECS),newTestPaths=[],newMethodIds=[],newTestIds=[],newPathsAdded=0,
        priorRegistryReference=dict(path=str((data.BASE/cfg.PRIOR_TRACE[0]/'manifest.json').relative_to(data.ROOT)),sha256=cfg.PRIOR_TRACE[1],source=prior['source'],oldRuntimeDomainsReassigned=False),
        currentQualification=dict(source=SOURCE,status='PG_ORACLE_SOURCE_ONLY_NOT_PT_QUALIFIED',proofManifestSha256='8e20e5c61cc3f92f96bebaa8cd6ac8dedc9ac6cb7ba190d881960a2e953e98d1',
            productTestsExecuted=0,dynamicPtStatus='NOT_EXECUTED_HOLD',coverageStatus='NOT_MEASURED',measuredProductCounters=None,allMainPhysicalUnchanged=1843,currentTestPhysical=1974,newTestPhysical=0,
            changedTestPhysical=p['changedTestPhysical'],rawStatic=54,rawStaticGateExit=1,spotbugsSixExit=0,oldPtQualificationTransferred=False),
        oracleSourceBinding=dict(changeOwner='WBS-G03.01',sourceOwnerCostsPreserved=True,oldChangeOwnerFieldsAreHistoricalNotNewWorkAssignment=True,correctedCalls=8,newNonTestPrivateHelperMethods=2,
            helperBindings=[dict(path=path,method=spec['helper'],enum=spec['enum'],callerMethodCounts=spec['methods'],fixedUiValues=list(spec['fields']),sourceOwner=spec['owner'],sourceCostOwner=spec['owner']) for path,spec in cfg.SPECS.items()],
            uiReference=dict(path=cfg.UI[0],sha256=cfg.UI[1]),currentPmdMultisetUnchanged=True,actualTestIdsAdded=0,newFixtureOrHarness=False,originalDynamicScopeInvoked=False,
            unresolvedOtherScope='R09/BIZ007 and BUG1830 authority remain outside this group'),
        sourceDerivedRaw=len(ids),joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),contextStateTransition='pg13336_state_oracle_trace.state_after',
        rawDeltaBasis='Eight state expected/fixture Production encoder dependencies removed via two Test-local exhaustive UI mappings; all54 scoped PMD diagnostics unchanged, no warning-count corrections',
        originalOracleGroupAccounting=dict(raw=7747,corrections=1694,refs=3349,pending=1370),actualViolationCount=None,wholeCurrentGlobalAnalyzerReissued=False,
        historicalMeasuredGlobalReferenceSource='db33c6a371d3dbc8e84f70462e0e56351bbb18b4',productTestsExecuted=0,newAccepted=0,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,effortPercent=None,externalActions=0)
    assert v['totalPriorCorrections'] == 1694 and v['mainRaw'] == 1502 and v['testRaw'] == 6245 and len(rows) == 995
    return v

def validate(v,prior,p,hashes):
    actual = copy.deepcopy(v)
    for k in ['invocation','wholeWbsAuditBefore']:actual.pop(k,None)
    assert json.dumps(actual,sort_keys=True) == json.dumps(expected(prior,p,hashes),sort_keys=True)

def main():
    invocation = capture(__file__);assert not OUT.exists();prior,p,hashes,raw,snap = inputs()
    assert (data.ROOT/INV).read_bytes() == raw and (data.ROOT/SNAP).read_bytes() == snap
    v = expected(prior,p,hashes);observed = audit();assert observed['actualExit'] == 1 and not observed['passed']
    v.update(invocation=invocation,wholeWbsAuditBefore=observed);validate(v,prior,p,hashes);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',v);print(data.sha((OUT/'manifest.json').read_bytes()))

def post():
    invocation = capture(__file__);assert not POST.exists();prior,p,hashes,raw,snap = inputs();v = json.loads((OUT/'manifest.json').read_bytes());validate(v,prior,p,hashes)
    actual_raw,actual_snap = (data.ROOT/INV).read_bytes(),(data.ROOT/SNAP).read_bytes();validate_docs(actual_raw,actual_snap,json.loads(raw),json.loads(snap));assert (actual_raw,actual_snap) == documents(cfg,SOURCE,raw,snap)
    labels = []
    for label,change in [('source',lambda x:x.update(source='0'*40)),('owner',lambda x:x['sourceRows'][0].update(canonicalCostOwner='WBS-G03.01')),('raw',lambda x:x.update(sourceDerivedRaw=7739)),
        ('PMD-correction',lambda x:x.update(totalPriorCorrections=1702)),('helper-as-Test',lambda x:x['oracleSourceBinding'].update(actualTestIdsAdded=2)),('PT',lambda x:x['currentQualification'].update(productTestsExecuted=8)),
        ('coverage',lambda x:x['currentQualification'].update(measuredProductCounters={'LINE':100})),('accepted',lambda x:x.update(newAccepted=1))]:
        bad = copy.deepcopy(v);change(bad)
        try:validate(bad,prior,p,hashes)
        except AssertionError:labels.append(label)
        else:raise AssertionError('false oracle PG qualification accepted')
    observed = audit();assert observed['actualExit'] == 1 and not observed['passed'];verify(invocation);POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,invocation=invocation,source=SOURCE,traceManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),metadataNegativeVectors=len(labels),negativeLabels=labels,
        oldRegistryRows=995,currentRegistryRows=995,modifiedTestPaths=sorted(cfg.SPECS),allOther993RowsAndEveryOwnerCostRuntimePreserved=True,unknownPathsUnchanged=2,wholeWbsAudit=observed,
        inventorySha256=data.sha(actual_raw),snapshotSha256=data.sha(actual_snap),productTestsExecuted=0,newAccepted=0,whole451Accepted=False))
    print(data.sha((POST/'manifest.json').read_bytes()))

if __name__ == '__main__':main()

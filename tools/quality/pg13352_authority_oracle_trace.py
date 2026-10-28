"""Seven source oracle corrections and one PMD correction, preserving every old owner/cost/runtime domain."""
import copy
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg13340_authority_oracle_config as cfg
from pg9954_pure_query_registry_metadata import INV,SNAP
from pg9338_wbs_reference_metadata_post import validate as validate_docs
from pg9880_snapshot_nonce_trace import audit
from f03_literal_batch_trace import documents

SOURCE = 'b95a31982a8a6066a9608e56af5fd17d5665576e'
OUT = data.BASE/'PG13352-authority-oracle-v1'
POST = data.BASE/'PG13353-authority-oracle-v1'
PROOF = '008b5e9fc37448d9f9a0d20cf585b372a99b7d9d6105cad3aac4d91ebcc6cbc5'

def state_after():
    ids,refs,pending = cfg.PREVIOUS_STATE()
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json','92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    scope = {r['id'] for r in original if r['id'] in ids and r['path'] in cfg.SPECS};assert len(scope) == 44 and cfg.REMOVED_FINDING in scope-refs
    result = ids-{cfg.REMOVED_FINDING},refs,pending|(scope&refs)
    assert [len(v) for v in result] == [7746,3349,1372];return result

def inputs():
    prior = data.read_checked(data.BASE/cfg.PRIOR_TRACE[0]/'manifest.json',cfg.PRIOR_TRACE[1])
    n = data.read_checked(data.BASE/'PG13346-authority-oracle-v1/manifest.json','310c52175ecb38fdab18ec14e791e0b240a38295e346322cfedad7b317d25de9')
    p = data.read_checked(data.BASE/'PG13350-authority-oracle-source-post-v1/manifest.json',PROOF)
    s = data.read_checked(data.BASE/'PG13351-authority-oracle-v1/manifest.json','a68b5fbaf9c55a936e19d5ae3ad85961dd71e985d3d31bfe4c0c12b83e1778ba')
    assert n['source'] == p['source'] == s['source'] == SOURCE and n['actualExit'] == p['actualExit'] == s['actualExit'] == n['testsExecuted'] == 0
    assert p['oracleCallsCorrected'] == 7 and len(p['independentSsDomainCases']) == 2 and p['newPrivateHelperMethods'] == 6 and p['newPrivateFields'] == 12
    assert p['allMainPhysicalUnchanged'] == 1843 and p['currentTestPhysical'] == 1978 and p['newTestPhysical'] == 4 and p['onlySpecifiedDuplicateLiteralRemoved'] and p['rawStatic'] == 43
    hashes = n['begin']['inputHashes'];assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in hashes.items())
    assert {r['path'] for r in prior['sourceRows'] if r['sha256'] != hashes[r['path']]} == set(cfg.SPECS)
    for path,spec in cfg.SPECS.items():
        row, = [r for r in prior['sourceRows'] if r['path'] == path];assert row['sha256'] == spec['sha256'] and row['canonicalOwner'] == row['canonicalCostOwner'] == spec['owner']
    raw,snap = [subprocess.check_output(['git','show',SOURCE+':'+path],cwd=data.ROOT) for path in [INV,SNAP]]
    return prior,p,hashes,raw,snap

def expected(prior,p,hashes):
    v = copy.deepcopy(prior)
    for key in ['invocation','wholeWbsAuditBefore']:v.pop(key,None)
    rows = copy.deepcopy(prior['sourceRows'])
    for row in rows:
        if row['path'] in cfg.SPECS:row['sha256'] = hashes[row['path']]
    ids,refs,pending = state_after()
    v.update(source=SOURCE,sourceRows=rows,modifiedTestPaths=sorted(cfg.SPECS),newTestPaths=[],newMethodIds=[],newTestIds=[],newPathsAdded=0,
        priorRegistryReference=dict(path=str((data.BASE/cfg.PRIOR_TRACE[0]/'manifest.json').relative_to(data.ROOT)),sha256=cfg.PRIOR_TRACE[1],source=prior['source'],oldRuntimeDomainsReassigned=False),
        priorStateOracleBindingHistorical=copy.deepcopy(prior['oracleSourceBinding']),
        currentQualification=dict(source=SOURCE,status='PG_ORACLE_SOURCE_ONLY_NOT_PT_QUALIFIED',proofManifestSha256=PROOF,productTestsExecuted=0,dynamicPtStatus='NOT_EXECUTED_HOLD',coverageStatus='NOT_MEASURED',measuredProductCounters=None,
            allMainPhysicalUnchanged=1843,previousTestPhysical=1974,currentTestPhysical=1978,newTestPhysical=4,changedTestPhysical=p['changedTestPhysical'],rawStatic=43,rawStaticGateExit=1,spotbugsSixExit=0,oldPtQualificationTransferred=False),
        oracleSourceBinding=dict(changeOwner='WBS-G03.01',sourceOwnerCostsPreserved=True,oldChangeOwnerFieldsAreHistoricalNotNewWorkAssignment=True,correctedCalls=7,newNonTestPrivateHelperMethods=6,newPrivateFields=12,
            helperBindings=[dict(path=path,method=cfg.HELPER,inputType='SessionPrincipal',callerMethodCounts=spec['methods'],fixedSsValues=[value for _,value in cfg.FIELDS.values()],sourceOwner=spec['owner'],sourceCostOwner=spec['owner']) for path,spec in cfg.SPECS.items()],
            ssReference=dict(path=cfg.SS[0],sha256=cfg.SS[1]),removedPmdFinding=cfg.REMOVED_FINDING,otherScopedPmdMultisetUnchanged=True,protectedActualEncoderSources=p['protectedSourceHashes'],actualTestIdsAdded=0,newFixtureOrHarness=False,originalDynamicScopeInvoked=False,
            unresolvedR09AcceptanceOwnership='UNKNOWN_UNCHANGED_NOT_SOURCE_OWNER_INFERRED'),
        sourceDerivedRaw=len(ids),mainRaw=1502,testRaw=6244,totalPriorCorrections=1695,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),contextStateTransition='pg13352_authority_oracle_trace.state_after',
        rawDeltaBasis='Seven authority oracle dependencies removed with six exhaustive SS mappings, one duplicate ROLE_USER literal correction; other43 scoped PMD retained',
        originalOracleGroupAccounting=dict(raw=7747,corrections=1694,refs=3349,pending=1370),actualViolationCount=None,wholeCurrentGlobalAnalyzerReissued=False,historicalMeasuredGlobalReferenceSource='db33c6a371d3dbc8e84f70462e0e56351bbb18b4',
        productTestsExecuted=0,newAccepted=0,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,effortPercent=None,externalActions=0)
    assert len(rows) == 995 and len(ids) == v['mainRaw']+v['testRaw']
    return v

def validate(v,prior,p,hashes):
    actual = copy.deepcopy(v)
    for key in ['invocation','wholeWbsAuditBefore']:actual.pop(key,None)
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
    for label,change in [('source',lambda x:x.update(source='0'*40)),('owner',lambda x:x['sourceRows'][0].update(canonicalCostOwner='WBS-G03.01')),('raw',lambda x:x.update(sourceDerivedRaw=7747)),
        ('PMD-correction',lambda x:x.update(totalPriorCorrections=1701)),('helper-as-Test',lambda x:x['oracleSourceBinding'].update(actualTestIdsAdded=6)),('PT',lambda x:x['currentQualification'].update(productTestsExecuted=7)),
        ('coverage',lambda x:x['currentQualification'].update(measuredProductCounters={'LINE':100})),('unknown-ownership',lambda x:x['oracleSourceBinding'].update(unresolvedR09AcceptanceOwnership='RESOLVED_FROM_SOURCE_OWNER'))]:
        bad = copy.deepcopy(v);change(bad)
        try:validate(bad,prior,p,hashes)
        except AssertionError:labels.append(label)
        else:raise AssertionError('false authority PG qualification accepted')
    observed = audit();assert observed['actualExit'] == 1 and not observed['passed'];verify(invocation);POST.mkdir()
    data.write(POST/'manifest.json',dict(actualExit=0,invocation=invocation,source=SOURCE,traceManifestSha256=data.sha((OUT/'manifest.json').read_bytes()),metadataNegativeVectors=len(labels),negativeLabels=labels,oldRegistryRows=995,currentRegistryRows=995,
        modifiedTestPaths=sorted(cfg.SPECS),allOther989RowsAndEveryOwnerCostRuntimePreserved=True,unknownPathsUnchanged=2,unresolvedR09AcceptanceOwnership='UNKNOWN_UNCHANGED_NOT_SOURCE_OWNER_INFERRED',wholeWbsAudit=observed,
        inventorySha256=data.sha(actual_raw),snapshotSha256=data.sha(actual_snap),productTestsExecuted=0,newAccepted=0,whole451Accepted=False))
    print(data.sha((POST/'manifest.json').read_bytes()))

if __name__ == '__main__':main()

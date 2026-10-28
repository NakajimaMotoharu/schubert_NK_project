"""Current exact static catalog supplement, preserving code qualification and every owner/cost row."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg13248_business_delivery_trace import state_after as previous_state

OUT = data.BASE/'PG13258-current-catalog-supplement-v1'
RECONCILE = ('PG13256-current-static-catalog-reconcile-v1','625f1b7f45924159ce8f15fb03994e0d42b71ae90f836fa03d7b00437c4c7889')
PRIOR = ('PG13248-business-delivery-literal-v1','d7cf2af90910d98c46c0c0727c6b95e2e4b0baa2f53dcec3bc3552b2d0a8bd8a')

def extra_rows():
    m = data.read_checked(data.BASE/RECONCILE[0]/'manifest.json',RECONCILE[1])
    v = data.read_checked(data.BASE/RECONCILE[0]/'reconciliation.json',m['reconciliationSha256'])
    assert v['priorDiagnosticsMissing'] == 0 and v['priorCatalog'] == 8008 and v['currentMeasured'] == 8022
    return v['additionalObservations']

def state_after():
    ids,refs,pending = previous_state();new = {r['id'] for r in extra_rows()}
    assert len(new) == 14 and not ids&new and [len(ids),len(refs),len(pending)] == [8008,3273,1183]
    return ids|new,refs,pending

def expected():
    prior = data.read_checked(data.BASE/PRIOR[0]/'manifest.json',PRIOR[1]);value = copy.deepcopy(prior)
    for k in ['invocation','wholeWbsAuditBefore']:value.pop(k,None)
    ids,refs,pending = state_after()
    value.update(sourceDerivedRaw=len(ids),mainRaw=1502,testRaw=6520,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),
        priorRegistryReference=dict(path=str((data.BASE/PRIOR[0]/'manifest.json').relative_to(data.ROOT)),sha256=PRIOR[1],source=prior['source'],oldRuntimeDomainsReassigned=False),
        additionalStaticFindings=extra_rows(),catalogReconciliationReference=dict(path=str((data.BASE/RECONCILE[0]/'manifest.json').relative_to(data.ROOT)),sha256=RECONCILE[1]),
        measuredCurrentGlobalReference=dict(path=str((data.BASE/'PG13253-current-all-java-static-v2/manifest.json').relative_to(data.ROOT)),sha256='751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf',warnings=8022,qualityGateExit=1),
        originalGroupStartAccounting=dict(sourceDerivedRaw=8008,joinedContextWarnings=3273,pending=1183,totalPriorCorrections=1419),
        contextStateTransition='pg13258_current_catalog_supplement.state_after',rawDeltaBasis='Current full1821 measured diagnostics: all7990 retained original IDs and18 prior supplemental occurrences match;14 additional unclassified observations, no completion',
        actualViolationCount=None,newAccepted=0,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,effortPercent=None,productTestsExecuted=0,externalActions=0)
    assert len(value['sourceRows']) == 995 and value['sourceRows'] == prior['sourceRows'] and value['currentQualification'] == prior['currentQualification']
    assert value['totalPriorCorrections'] == 1419 and len(ids-refs) == 4749
    return value

def validate(value):
    actual = copy.deepcopy(value);actual.pop('invocation',None)
    assert json.dumps(actual,sort_keys=True) == json.dumps(expected(),sort_keys=True)

def main():
    invocation = capture(__file__);assert not OUT.exists();value = expected();validate(value);labels = []
    for label,change in [('source',lambda x:x.update(source='0'*40)),('owners',lambda x:x['sourceRows'][0].update(canonicalCostOwner='WBS-F03')),('runtime',lambda x:x['currentQualification'].update(productTestsExecuted=1)),
        ('corrections',lambda x:x.update(totalPriorCorrections=1433)),('purpose',lambda x:x.update(joinedContextWarnings=3287)),('actual',lambda x:x.update(actualViolationCount=0)),
        ('exempt',lambda x:x['additionalStaticFindings'][0].update(ptExecutionExempt=True)),('accepted',lambda x:x.update(newAccepted=1))]:
        bad = copy.deepcopy(value);change(bad);assert json.dumps(bad,sort_keys=True) != json.dumps(value,sort_keys=True)
        try:validate(bad)
        except AssertionError:labels.append(label)
        else:raise AssertionError('invalid static catalog qualification accepted')
    value.update(invocation=invocation);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',value)
    data.write(OUT/'verification.json',dict(actualExit=0,manifestSha256=data.sha((OUT/'manifest.json').read_bytes()),metadataNegativeVectors=len(labels),labels=labels,
        preserved995RowsOwnersCostsAndOldRuntime=True,additionalUnclassified=14,newCorrections=0,newAccepted=0,productTestsExecuted=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()

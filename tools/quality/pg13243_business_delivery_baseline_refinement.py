"""Add two independently observed baseline diagnostics, never completion or a rewritten original baseline."""
import copy
import json
from types import SimpleNamespace
import pg13237_business_delivery_literal_config as original_cfg
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG13243-business-delivery-baseline-refinement-v1'
RECOVERY = ('PG13239-business-delivery-preflight-recovery-v1','4a09dd839415e6b4728e8913f3e4ecfc5da7340f861ee5fe297f868f9432c4fa')

def supplement():
    value = data.read_checked(data.BASE/RECOVERY[0]/'manifest.json',RECOVERY[1]);extra = value['additionalFindings']
    assert len(extra) == 2 and value['baseSource'] == original_cfg.BASE_SOURCE and not value['businessOrPtOracleChanged']
    assert all(r['actualViolation'] is None and r['manualPurposeReviewComplete'] and not r['ptExecutionExempt'] for r in extra)
    return extra

def refined_state():
    ids,refs,pending = original_cfg.PREVIOUS_STATE();extra = {r['id'] for r in supplement()}
    assert len(extra) == 2 and not extra&ids and [len(ids),len(refs),len(pending)] == [8143,3271,1118]
    result = ids|extra,refs|extra,pending|extra
    assert [len(x) for x in result] == [8145,3273,1120]
    return result

def expected():
    prior = data.read_checked(data.BASE/original_cfg.PRIOR_TRACE[0]/'manifest.json',original_cfg.PRIOR_TRACE[1])
    value = copy.deepcopy(prior)
    for key in ['invocation','wholeWbsAuditBefore']:value.pop(key,None)
    ids,refs,pending = refined_state()
    value.update(sourceDerivedRaw=len(ids),testRaw=6643,mainRaw=1502,totalPriorCorrections=1282,joinedContextWarnings=len(refs),sourceReboundCurrentWholePending=len(pending),noCurrentReferenceInThisJoin=len(ids-refs),
        priorRegistryReference=dict(path=str((data.BASE/original_cfg.PRIOR_TRACE[0]/'manifest.json').relative_to(data.ROOT)),sha256=original_cfg.PRIOR_TRACE[1],source=prior['source'],oldRuntimeDomainsReassigned=False),
        additionalStaticFindings=supplement(),diagnosticSupplementReference=dict(path=str((data.BASE/RECOVERY[0]/'manifest.json').relative_to(data.ROOT)),sha256=RECOVERY[1]),
        originalGroupStartAccounting=dict(sourceDerivedRaw=8143,testRaw=6641,totalPriorCorrections=1282,joinedContextWarnings=3271,pending=1118),
        baselineRefinement=dict(kind='ADDITIONAL_OBSERVATIONS_NOT_COMPLETION',sourceCodeChanges=0,observedNewDiagnosticIds=2,originalGlobalCatalogRewritten=False,businessOrPtOracleChanged=False,formalRequalification=False),
        contextStateTransition='pg13243_business_delivery_baseline_refinement.refined_state',rawDeltaBasis='Two already-existing Connection source diagnostics newly observed under current partial static conditions; cause of original omission and dynamic/pre-handoff correctness remain HOLD',
        actualViolationCount=None,newAccepted=0,wholeF03Accepted=False,whole451Accepted=False,formalUpdated=False,effortPercent=None,productTestsExecuted=0,externalActions=0)
    assert value['source'] == original_cfg.BASE_SOURCE and len(value['sourceRows']) == 995
    assert value['sourceRows'] == prior['sourceRows'] and value['currentQualification'] == prior['currentQualification'] and value['totalPriorCorrections'] == prior['totalPriorCorrections']
    return value

def validate(value):
    actual = copy.deepcopy(value);actual.pop('invocation',None)
    assert json.dumps(actual,sort_keys=True) == json.dumps(expected(),sort_keys=True)

def main():
    invocation = capture(__file__);assert not OUT.exists();value = expected();validate(value);labels = []
    for label,change in [('source',lambda x:x.update(source='0'*40)),('correction',lambda x:x.update(totalPriorCorrections=1284)),
        ('original-baseline',lambda x:x['originalGroupStartAccounting'].update(sourceDerivedRaw=8145)),('row',lambda x:x['sourceRows'][0].update(sha256='0'*64)),
        ('accepted',lambda x:x.update(newAccepted=1)),('exempt',lambda x:x['additionalStaticFindings'][0].update(ptExecutionExempt=True)),
        ('actual',lambda x:x.update(actualViolationCount=0)),('old-runtime',lambda x:x['currentQualification'].update(productTestsExecuted=1))]:
        bad = copy.deepcopy(value);change(bad);assert json.dumps(bad,sort_keys=True) != json.dumps(value,sort_keys=True)
        try:validate(bad)
        except AssertionError:labels.append(label)
        else:raise AssertionError('false diagnostic refinement accepted')
    value.update(invocation=invocation);verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',value)
    data.write(OUT/'verification.json',dict(actualExit=0,source=original_cfg.BASE_SOURCE,manifestSha256=data.sha((OUT/'manifest.json').read_bytes()),metadataNegativeVectors=len(labels),labels=labels,
        old995RowsOwnersCostsRuntimeUnchanged=True,newDiagnostics=2,newCorrections=0,newAccepted=0,formalUpdated=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

def trace_cfg():
    # This is a new, explicit accounting view. The original frozen cfg/start event
    # and original8143 are preserved; the additional2 do not count as completion.
    value = json.loads((OUT/'manifest.json').read_bytes());validate(value)
    fields = {key:getattr(original_cfg,key) for key in vars(original_cfg) if key.isupper()}
    fields.update(PRIOR_TRACE=(OUT.name,data.sha((OUT/'manifest.json').read_bytes())),PREVIOUS_STATE=refined_state,BEFORE_RAW=8145,BEFORE_TEST_RAW=6643)
    return SimpleNamespace(**fields)

if __name__ == '__main__':main()

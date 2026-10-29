"""Tool-only event dependency and real WBS role contract checks; no process or event replay."""
import json
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify

OUT=data.BASE/'PG14619-group-start-role-exit-contract-v1'

def may_issue_product(result):
    return isinstance(result,dict) and type(result.get('exit_code')) is int and result['exit_code']==0 and result.get('eventPersisted') is True

def main():
    invocation=capture(__file__);assert not OUT.exists()
    nodes={}
    def collect(v):
        if isinstance(v,dict):
            if isinstance(v.get('id'),str):nodes[v['id']]=v
            for child in v.values():collect(child)
        elif isinstance(v,list):
            for child in v:collect(child)
    input_hashes={}
    for name in ['481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json']:
        path=data.ROOT/'documents/400_PGPT/470_PMO'/name;payload=path.read_bytes();input_hashes[str(path.relative_to(data.ROOT))]=data.sha(payload);collect(json.loads(payload))
    def leaf(name):return name in nodes and not nodes[name].get('children') and ':' not in name
    checks=[]
    for name in ['WBS-P016-07','WBS-P018-06','WBS-P015-07']:
        assert leaf(name);checks.append('known-leaf-'+name)
    assert not leaf('WBS-P016-25') and not leaf('WBS-UNKNOWN');checks+=['actual-parent-not-cost-leaf','unknown-not-cost-leaf']
    for name,value in [('failed',dict(exit_code=1,eventPersisted=False)),('unknown',{}),('bool-exit',dict(exit_code=False,eventPersisted=True)),('missing-event',dict(exit_code=0,eventPersisted=False))]:
        assert not may_issue_product(value);checks.append('no-child-on-'+name)
    assert may_issue_product(dict(exit_code=0,eventPersisted=True));checks.append('only-real-zero-plus-persisted-event-eligible')
    events=Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')
    rows=[json.loads(line) for line in events.read_bytes().splitlines()];by_id={v['eventId']:v for v in rows}
    current=by_id['PGPT-20261008-3113']
    assert current['eventType']=='CHECKPOINT' and current['attemptResult']=='DELAYED_START_RECORD_PRODUCT_TERMINAL_POST_PENDING'
    assert current['estimateAtGroupStartPp']==dict(low=1,base=4,high=8) and current['primaryWbs']=='WBS-P016-07'
    assert current['componentReferenceParents']==['WBS-P016-25'] and current['componentAdditionalBudgetPp']==0 and current['groupBudgetAdditive'] is False
    assert all(leaf(n) for n in current['wbsLeafIds']) and 'WBS-P016-25' not in current['wbsLeafIds'];checks.append('delayed-record-no-backdate-no-rebudget')
    for number in range(3107,3113):
        event=by_id[f'PGPT-20261008-{number}']
        assert all(leaf(n) for n in event['wbsLeafIds']) and event['groupBudgetAdditive'] is False
    checks.append('six-prior-event-roles-no-Product-rerun')
    assert len(checks)==12
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source='6b53efeec87f3ec36a840dd8e7759656cb4aee5c',invocation=invocation,toolChecks=checks,toolCheckCount=len(checks),inputHashes=input_hashes,delayedEventId=current['eventId'],delayedEventSha256=data.sha(json.dumps(current,ensure_ascii=False,sort_keys=True).encode()),originalBudgetPp=dict(low=1,base=4,high=8),originalBudgetChanged=False,productTestsExecuted=0,productOperationsIssued=0,metricsEventsWrittenByCheck=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,regressionSemantics='TOOL_ONLY_FIXED_INPUT_NEGATIVES_NOT_PRODUCT_COVERAGE_OR_RECONSTRUCTED_START',relatedBug='BUG-2105',relatedYkt='YKT-1852'))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()

"""Record original C01 format subcriterion, not leaf/full coverage acceptance or new Java IDs."""
import json
from pathlib import Path
import pg998_metrics as metrics
from host_tool_invocation import capture,verify
from source_evidence_binding import bind

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9022-caddy-format-metrics-v1'
GROUP='C01_CANONICAL_CADDY_FORMAT_PGPT_V1'
SOURCE='f690fa6be336550f8078e2bdde40ef34ab5efe6b'


def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in events)
    proofs=bind([(BASE/'PG9012-caddy-format-static-v1/manifest.json','5cd9e50e288ea56e38341b3e0fbceb60868f72aa9702f290b4a7220fdae620af'),
                 (BASE/'PG9018-caddy-format-post-v1/manifest.json','7bcec8d77845b98e988498766121756e8bafe5e465b95afc04b6cf16a2461ce8'),
                 (BASE/'PG9020-caddy-format-trace-v1/manifest.json','6a531018c9ed7a493d4f3cd50a5d0bd85481d53e2ece0f185c91b7a43e87d76f')],SOURCE)
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-C01',source=SOURCE,
       sourceBefore='fb9fce0f91de3d9fdfa634fe277592700f915e45',workCategory='IMPLEMENTATION',
       groupStartEstimatePp={'low':2,'base':4,'high':8},groupCapPp=10,
       quotaBefore={'usedPercent':50,'remainingPercent':50,'resetsAt':1793382075},
       quotaAfter={'usedPercent':50,'remainingPercent':50,'resetsAt':1793382075},
       quotaAfterObservedAtUTC='2026-10-24T20:02:52+00:00',sameQuotaWindow=True,observedSharedPp=0,
       attemptResult='CONFIG_ONLY_INDENT_PG;STATIC5_ORDINARY3_PASS;WHOLE_CLASS_FOUR100_UNMET_NO_EXCLUSION',
       technicalMeasurementDelta={'changedProductionConfig':1,'newStaticConfigCaseIds':5,'actualStaticCases':5,
             'actualOrdinaryJavaTests':3,'newTestIds':0,'newMain':0,'physicalMain':1835,'changedMain':0,
             'wholeClassCoverage':{'LINE':{'covered':24,'missed':109},'METHOD':{'covered':2,'missed':21},'CLASS':{'covered':1,'missed':0},'BRANCH':{'covered':22,'missed':78}},
             'four100':False,'formalAccepted':0},
       originalPlanEngineeringDelta={'wbs':'WBS-C01','subcriterion':'CANONICAL_TEMPLATE_AND_RENDERED_FMT',
                                     'completedEvidence':'PG9012_STATIC5','leafAccepted':False},
       workNature='ORIGINAL_PLAN_FORMAT_REMEDIATION_NOT_LEAF_ACCEPTANCE_OR_NEW_JAVA_TEST_IDS',
       sourceProofs=proofs,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1851_C01書式是正_実行結果・残品質.md'],
       failureIds=['BUG-1728','YKT-1479'],actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,
       tokenMeasurementIds=['6257df3caccbd75507b96bddeac3d0e6dc548f8e953e53f60a40c5c7605caba3'],
       pgptAllComplete=False,stopReason=None,nextCommand='9024 public scan/commit-push; scoped C07 API outbox owner/context source-contract review before implementation'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,invocation=invocation,eventId=identifier,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier)))


if __name__=='__main__':main()

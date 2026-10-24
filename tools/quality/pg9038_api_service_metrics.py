"""Record new17/necessary21 and metadata-tool rework separately; no whole/runtime acceptance."""
import hashlib
import json
from pathlib import Path
import pg998_metrics as metrics
from host_tool_invocation import capture,verify
from source_evidence_binding import bind

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9038-api-service-metrics-v1'
GROUP='P01809_API_SERVICE_OUTBOX_METADATA_V1'
SOURCE='73d94fc525c6ea8828ca82d906ec583146fee7bf'


def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    events=[json.loads(row) for row in metrics.EVENTS.read_bytes().splitlines()]
    assert not any(row['groupId']==GROUP and row.get('groupBoundary')=='END' for row in events)
    proofs=bind([(BASE/'PG9032-api-service-post-v1/manifest.json','4585f25047cd5f657152facf8486a44a69fe73c67d17345b864cd61e3965a358'),
                 (BASE/'PG9034-api-service-trace-v3/manifest.json','caf310661eae47595a3b71f5472c052e4c6059e4e31ecdb3e5fead192aa17f4c')],SOURCE)
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    assert digest(inventory['artifacts'])=='ac5dee93b15167133a713c60d255b490400cbaee12362d7f1d0328161318ef99'
    assert digest(inventory['currentPhysicalCandidate'])=='38247ee2b8850d5ab64f37f8d5536c8b14d7aa1962fab7be9c7ec190a930a01a'
    assert inventory['currentIncrementalHostOwnership']['source']==SOURCE and inventory['currentIncrementalHostOwnership']['sourceRows']==235
    verify(invocation)
    identifier=metrics.append(GROUP,'GROUP_END',dict(primaryWbs='WBS-P018-09',source=SOURCE,
       sourceBefore='f690fa6be336550f8078e2bdde40ef34ab5efe6b',workCategory='IMPLEMENTATION',
       groupStartEstimatePp={'low':2,'base':5,'high':9},groupCapPp=10,
       quotaBefore={'usedPercent':51,'remainingPercent':49,'resetsAt':1793382075},
       quotaAfter={'usedPercent':52,'remainingPercent':48,'resetsAt':1793382075},
       quotaAfterObservedAtUTC='2026-10-24T20:51:38+00:00',sameQuotaWindow=True,observedSharedPp=1,
       attemptResult='ACTUAL38_F0_E0_S0_NEW17_NECESSARY21; TWO_MAIN_FOUR100_STATIC0; LIVE_SOURCE_UNSUPPLIED_HOLD',
       technicalMeasurementDelta={'newTestIds':17,'necessaryRegressionTests':21,'actualSelectedTests':38,
              'newMain':1,'physicalMain':1836,'sourceOwners':235,
              'scopedCoverage':{'LINE':60,'METHOD':10,'CLASS':2,'BRANCH':8,'missed':0},
              'rawPmd':0,'checkstyleFindings':0,'spotbugsFindings':0,'callerRawPmd':2,
              'callerContextNotApplicableJ2ee':2,'callerDynamicPt':'UNRUN_HOLD','formalAccepted':0},
       originalPlanEngineeringDelta={'item':'API_SERVICE_IMMUTABLE_OUTBOX_METADATA_SUPPLY','componentOnly':True,'liveSourceSupplied':False},
       rework={'toolDefects':['BUG-1729','BUG-1730'],'originalVersionsPreserved':True,'productJobsRerun':0,'exclusivePp':None},
       sourceProofs=proofs,sourceEvidenceRefs=['evidence/01_PT/018_NK-OPS-001/1853_APIServiceOutboxMetadata_実行結果・残依存.md'],
       failureIds=['BUG-1729','YKT-1480','BUG-1730','YKT-1481'],actualAllocatedPp=None,tokenTotals=None,effortCompletionRate=None,
       tokenMeasurementIds=['b36a4440dfc8b5ef64d1ff1ef7f14ab203df57057093c8a8190847bd5251fa6e'],
       pgptAllComplete=False,stopReason=None,nextCommand='9040 public scan/commit-push; SDK-independent borrowed-RO observation cache PG/PT before any live owner/producer'))
    OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,invocation=invocation,eventId=identifier,logical941AndHistorical943Unchanged=True,formalUpdated=False,newAccepted=0),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,eventId=identifier,sourceRows=235)))


if __name__=='__main__':main()

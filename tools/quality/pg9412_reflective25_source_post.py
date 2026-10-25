"""Exact module-qualified literal responsibility25; runtime uncertainty is not waived."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9412-reflective25-source-post-v1'
SUBJECT=BASE/'PG9410-reflective25-source-metadata-v2'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'

def path(module,name):return 'src/schubert-nk-'+module+'/src/test/java/dev/codex/schubert/nk/'+name+'.java'

# Independent literal full-path table; no basename lookup/fallback in the postcondition.
ORACLE={
 path('api','api/application/log/LogApplicationFixture'):'WBS-P006-01',
 path('api','api/dispatch/ApiReadinessFailureGraph330Test'):'WBS-P018-05',
 path('api','api/idempotency/JdbcScenarioSnapshotReplacementTest'):'WBS-P006-01',
 path('api','api/idempotency/SnapshotScratchOwnershipTest'):'WBS-P006-01',
 path('api','api/messaging/inbound/ParentGraph334Test'):'WBS-P005-03',
 path('api','api/messaging/outbound/OutboxFailureOwnershipTest'):'WBS-P006-02',
 path('api','api/messaging/outbound/OutboxSecondary330Test'):'WBS-P006-02',
 path('batch','batch/mq/AcceptorObjectBoundaryTest'):'WBS-P017-10',
 path('batch','batch/mq/ArtemisDetailedValuesTest'):'WBS-P017-10',
 path('batch','batch/platform/ServiceDeadlineArgumentTest'):'WBS-P018-03',
 path('bootstrap','api/maintenance/SchemaHistoryAdmissionTest'):'WBS-P019-01',
 path('bootstrap','bootstrap/FixedNativeCoverageRemovalDuringShutdownProbe'):'WBS-P018-08',
 path('bootstrap','bootstrap/SystemdBinderAbiTest'):'WBS-P018-03',
 path('web','web/bootstrap/WebReadinessFailureGraph330Test'):'WBS-P018-06',
 path('web','web/logging/JdbcWebSessionStoreTest'):'WBS-P015-01',
 path('web','web/messaging/BrokerGraph334Test'):'WBS-P005-02',
 path('web','web/messaging/ReplyCleanup333Test'):'WBS-P005-02',
 path('web','web/messaging/ReplyCommittedTerminalAdmissionContractTest'):'WBS-P005-02',
 path('web','web/messaging/ReplyConsumerGraph332Test'):'WBS-P005-02',
 path('web','web/messaging/ReplyFatalIsolationContractTest'):'WBS-P005-02',
 path('web','web/messaging/ReplyRollbackSignalContractTest'):'WBS-P005-02',
 path('web','web/messaging/ReplyRollbackUnconfirmedContractTest'):'WBS-P005-02',
 path('web','web/receipt/ReceiptFailureGraph329Test'):'WBS-P011-04',
 path('web','web/receipt/ReceiptReferenceFaultTest'):'WBS-P011-04',
 path('web','web/session/SessionRollbackAttachment329Test'):'WBS-P015-01'}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def validate(rows,expected):
    if rows!=expected:raise ValueError('exact source responsibility and unwaived runtime reasons required')

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    raw=(SUBJECT/'manifest.json').read_bytes();assert sha(raw)=='3a091fd42596d8529b93c65147a7045e82824c049d5d507ca024eac08f6d8f13'
    value=json.loads(raw);assert value['source']==SOURCE and value['actualExit']==0 and value['frozenPrimaryOwners']==ORACLE
    catalog=(SUBJECT/'candidates.json').read_bytes();assert sha(catalog)==value['candidatesSha256']=='dd3c143636705aa89f1a03e584de5a57fec355a03b4e49f3b1d93e8f11de1cf5'
    rows=json.loads(catalog);assert len(rows)==25 and {row['path'] for row in rows}==set(ORACLE)
    assert path('api','api/messaging/config/BrokerGraph334Test') not in ORACLE
    graph_dir=BASE/'PG9386-composite-reference-graph-v3'
    graph_raw=(graph_dir/'manifest.json').read_bytes();assert sha(graph_raw)==value['graphManifestSha256']=='3b092052e7724400870c72d7d92a163e5fdbe9c536eebe2bfe38403d3c187b15'
    graph=json.loads(graph_raw);reference_raw=(graph_dir/'unresolved.json').read_bytes();assert sha(reference_raw)==graph['unresolvedSha256']
    references={row['path']:row for row in json.loads(reference_raw)}
    expected=[]
    for row in rows:
        source_path=row['path'];primary=ORACLE[source_path];original=references[source_path]
        assert original['mainOwners']==[primary] and original['unresolvedReasons']==['REFLECTION_OR_DYNAMIC_CLASS_RESOLUTION']
        assert row['sha256']==original['sha256']==sha((ROOT/source_path).read_bytes())
        expected.append(dict(path=source_path,sha256=original['sha256'],owner=primary,costOwner=primary,relatedOwners=[],originalReferenceOwners=[primary],
          unresolvedRuntimeReasons=['REFLECTION_OR_DYNAMIC_CLASS_RESOLUTION'],targetRuntimeAccepted=False,
          basis='FROZEN_LITERAL_SOURCE_PRIMARY_AND_RELATED_SCOPES_RUNTIME_UNCERTAINTY_RETAINED_NOT_PT'))
    validate(rows,expected)
    for name,key in (('class-proofs.json','classProofsSha256'),('main-source-proofs.json','mainProofsSha256')):assert sha((SUBJECT/name).read_bytes())==value[key]
    rejected=[]
    for label,edit in (('cost-only',lambda v:v[0].update(costOwner='WBS-G13.07')),('primary-only',lambda v:v[0].update(owner='WBS-G13.07')),
      ('related-invented',lambda v:v[0].update(relatedOwners=['WBS-F02'])),('runtime-hold-erased',lambda v:v[0].update(unresolvedRuntimeReasons=[])),
      ('runtime-success-invented',lambda v:v[0].update(targetRuntimeAccepted=True)),('source-other-module',lambda v:v[0].update(path=path('api','api/messaging/config/BrokerGraph334Test'))),
      ('missing',lambda v:v.pop()),('duplicate',lambda v:v.append(copy.deepcopy(v[0])))):
        changed=copy.deepcopy(rows);edit(changed)
        if label=='cost-only':assert {k for k in rows[0] if rows[0][k]!=changed[0][k]}=={'costOwner'}
        try:validate(changed,expected)
        except ValueError:rejected.append(label)
        else:raise AssertionError('forged static ownership accepted')
    verify(invocation);OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          subjectManifestSha256=sha(raw),catalogSha256=sha(catalog),primaryKeyKind='FULL_REPO_PATH',literalPrimaryOwners=ORACLE,
          runtimeUncertaintyPreserved=True,apiBrokerGraphSameNameNotSelected=True,sourceSelectionVectors=value['sourceSelectionVectors'],
          independentClassMetadata=value['independentClassMetadata'],independentMainSourceFiles=value['independentMainSourceFiles'],
          positiveBeforeNegatives=True,metadataCounterexamples=rejected,productTestsExecuted=0,newAccepted=0,coverage=None,formalUpdated=False),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,literalOwners=25,metadataNegatives=len(rejected),manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()

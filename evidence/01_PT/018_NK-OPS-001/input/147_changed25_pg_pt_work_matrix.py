"""Classify explicit evidence for25 changed artifacts without claiming acceptance."""
from pathlib import Path
import collections,datetime,hashlib,json,subprocess
r=Path.cwd();load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
base=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21766-current4217-static-artifact-lineage-v2';manifest=load(base/'manifest.json');assert sha(base/'manifest.json')=='ee465df2a40a6bba40c02680062a2cbc7d0441a0bc012c67efebfb752ac70a09'
changed=load(base/'changed-artifacts.json');added=load(base/'added-artifacts.json');targets={x['path']:dict(x,changeKind='M') for x in changed};targets.update({x['path']:dict(x,changeKind='A') for x in added});assert len(targets)==25
full={x['path']:x for x in load(base/'artifacts.json')};lookup=load(r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21792-current4217-changed-twenty-proof-candidates-v1/manifest.json');candidates={x['path']:x for x in lookup['rows']}
def ref(n):
 p=r/n;assert p.is_file() and 'private' not in p.name;return dict(path=n,sha256=sha(p))
def evidence(n):
 x=ref(n);assert load(r/n)['actualExit']==0;return x
refs={
 'added':evidence('evidence/01_PT/018_NK-OPS-001/evidence/PG21780-qa054-two-artifact-existing-proof-trace-v2/manifest.json'),
 'resources':evidence('evidence/01_PT/016_NK-WEB-002/evidence/PG21840-three-current-resources-existing-proof-trace-v1/manifest.json'),
 'protocol':evidence('evidence/01_PT/002_NK-PRO-002/evidence/PG21852-current-protocol-four-source-existing-proof-trace-v1/manifest.json'),
 'reply':evidence('evidence/01_PT/005_NK-MSG-001/evidence/PG21824-jms-reply-current-codec-seven-v1/manifest.json'),
 'replyPost':evidence('evidence/01_PT/005_NK-MSG-001/evidence/PG21830-jms-reply-current-codec-independent-post-v2/manifest.json'),
 'guardMetadata':evidence('evidence/01_PT/018_NK-OPS-001/evidence/PG21806-source-units-schema-metadata-v1/manifest.json')}
reviews={
 'LogQueryApplicationService':('a077dddaae8ca05c98f6d8ba8ef9dd859744a2df','documents/400_PGPT/470_PMO/500_SV計画整備_20261104/848_QA054ログ検索API製造・PG強化レビュー.md'),
 'WebLogIngestService':('aac358fec5673691f2663c9cf810c2f57a29b982','documents/400_PGPT/470_PMO/500_SV計画整備_20261104/851_QA054メニュー記録PG強化レビュー・残存条件.md'),
 'WebRequestLogProducer':('aac358fec5673691f2663c9cf810c2f57a29b982','documents/400_PGPT/470_PMO/500_SV計画整備_20261104/851_QA054メニュー記録PG強化レビュー・残存条件.md')}
protocol_names={'LayoutFieldCatalog','PayloadCodec','PayloadSemanticValidator','WebLogEventData'};added_names={'WebHttpLogKind','CorrelatedLogEvidenceValidator'}
rows=[]
for n,a in sorted(targets.items()):
 assert not any(t in n for t in ['RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest','SnapshotKeyCloseWitness','pg9892_snapshot_key_close_witness']);assert sha(r/n)==a['currentSha256']==full[n]['sha256']
 assert hashlib.sha256(subprocess.check_output(['git','show','4217e14083c6ecac116216e08d57f4361eb2f12d:'+n])).hexdigest()==a['currentSha256']
 name=Path(n).stem;proof=[];special={};remaining='Whole WBS criteria/dependencies/source-run451/native/actualCHR/QA051final are not accepted by this artifact row.'
 if name in reviews:
  source,doc=reviews[name];assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+n])).hexdigest()==a['currentSha256'];proof=[ref(doc)];status='PG_REVIEW_CURRENT_BYTE_BOUND_DYNAMIC_HOLD';special=dict(reviewSource=source,reviewCurrentByteExact=True,ptExecutionExempt=False);nextwork='Keep complete graph dynamicHOLD; only concrete source/design/static follow-up is permitted. No new fixture or partial extraction.'
 elif name=='LinuxSystemdSession':
  diff=subprocess.check_output(['git','diff','--unified=5','6b53efeec87f3ec36a840dd8e7759656cb4aee5c','4217e14083c6ecac116216e08d57f4361eb2f12d','--',n],text=True);assert '-      bytes[end++] = octet;' in diff and '+      bytes[end] = octet;' in diff and '+      end++;' in diff
  assert [x for x in diff.splitlines() if x.startswith('-') and not x.startswith('---')]==['-      bytes[end++] = octet;']
  assert [x for x in diff.splitlines() if x.startswith('+') and not x.startswith('+++')]==['+      bytes[end] = octet;','+      end++;']
  status='STYLE_DIFF_STATIC_REVIEW_NATIVE_HOLD';special=dict(oldSource='6b53efeec87f3ec36a840dd8e7759656cb4aee5c',changedNativeBehaviorClaimed=False,diff=diff);nextwork='Native/manager/default route remains held; no actual syscall, native fixture or execution follows from static equivalence.'
 elif a['kind']!='JAVA':status='CURRENT_RESOURCE_ORIGINAL_PROOF_TRACE_BOUND';proof=[refs['resources']];nextwork='Original8/7 and3resource bytes already bound; actual Browser/HTTP/computed CSS remains held. Do not replay.'
 elif name in added_names:status='CURRENT_ADDED_ARTIFACT_HISTORICAL_SUITE_TRACE_BOUND';proof=[refs['added']];nextwork='23method test-set binding already complete; no per-single-test probe attribution or actual capture acceptance.'
 elif name in protocol_names:status='CURRENT_PROTOCOL_HISTORICAL_WHOLE_SOURCE_TRACE_BOUND';proof=[refs['protocol']];nextwork='Original63/4source/7physical already bound; no need to replay or add to formal count.'
 elif name=='JmsReplyDecoder':status='CURRENT_CODEC_DEPENDENCY_ORIGINAL7_REQUALIFIED';proof=[refs['reply'],refs['replyPost']];nextwork='Current7/23Main-dependency identity witness complete; actual reply consumer/broker/business path stays held.'
 elif name=='JmsMessageGuard':status='CURRENT_CLASS_HISTORICAL_RECEIPT_METADATA_BOUND';proof=[refs['guardMetadata']];nextwork='Static current dependency/source-level complete-scope join remains explicit; do not rerun merely because parser once lacked sourceUnits.'
 elif name in {'GateCli','GateContractValidator'}:status='METHOD_SUBSET_SUCCESS_WHOLE_DYNAMIC_HOLD';proof=[evidence('evidence/01_PT/020_NK-CHR-001/evidence/PG21140-gate-synthetic-sixty-v1/manifest.json')];nextwork='Existing selected60 are method subsets. Whole gate/baseline/promote/capture remains held; no new partial fixture or success replay.'
 elif name=='TargetAdapter':status='HISTORICAL_WHOLE_FACT_CURRENT_JOIN_PENDING';proof=[ref('evidence/01_PT/020_NK-CHR-001/006_NK-CHR-001_gate定義単体結果.md')];nextwork='Resolve original18716 same-byte two-physical/source proof from existing receipts only before updating this row; no replay.'
 else:
  row=candidates[n];same=[x for x in row['candidates'] if x['currentMainByteEqual'] and x['originalExit']==0];assert same;status='SAME_BYTE_COUNTER_CANDIDATE_SCOPE_JOIN_PENDING';proof=[dict(path=x['path'],sha256=x['sha256']) for x in same];nextwork='Verify full source/nested physical/current closure/TestID-oracle scope from these original candidates; named-class zero counters alone do not close a source or leaf.'
 rows.append(dict(path=n,changeKind=a['changeKind'],source='4217e14083c6ecac116216e08d57f4361eb2f12d',sha256=a['currentSha256'],owner=full[n]['owner'],costOwner=full[n]['costOwner'],additionalBudgetPp=0,status=status,evidenceRefs=proof,special=special,remainingCriteria=remaining,nextPermittedWork=nextwork,wholeSourceAcceptedByMatrix=False,newLeafAccepted=False,newProductTests=0))
counts=dict(collections.Counter(x['status'] for x in rows));assert sum(counts.values())==25
spec=r/'evidence/01_PT/018_NK-OPS-001/3616_現変更二五artifact製造試験・残条件matrix仕様.md'
for p in [spec,Path(__file__)]:assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+str(p.relative_to(r))])).hexdigest()==sha(p)
out=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21866-current-changed25-pg-pt-evidence-matrix-v1';assert not out.exists();out.mkdir()
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),observerSource=head,productionCoreMain='4217e14083c6ecac116216e08d57f4361eb2f12d',baseDescriptor=dict(path=str((base/'manifest.json').relative_to(r)),sha256=sha(base/'manifest.json')),rows=rows,statusCounts=counts,changedArtifacts=23,addedArtifacts=2,totalDeltaArtifacts=25,scopeIsCompletionDenominator=False,newProductTests=0,newMethods=0,newSourceProofs=0,newAcceptance=0,wholeG13Accepted=False,whole451Accepted=False,effortRate=None)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,rows=25,statusCounts=counts,newProductTests=0,manifestSha256=sha(out/'manifest.json'))))

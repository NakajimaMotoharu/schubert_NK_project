"""Check explicit classifications and boundaries, not a Product acceptance gate."""
from pathlib import Path
import collections,datetime,hashlib,json,subprocess
r=Path.cwd();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
p=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21866-current-changed25-pg-pt-evidence-matrix-v1/manifest.json';assert sha(p)=='aaf804e3295cb6afe5404f03ba496784b5db7e396a8d096fdb7406078d089b64';m=load(p)
assert m['actualExit']==0 and len(m['rows'])==25 and m['newProductTests']==m['newMethods']==m['newSourceProofs']==m['newAcceptance']==0 and not m['scopeIsCompletionDenominator'] and m['effortRate'] is None
base=r/m['baseDescriptor']['path'];assert sha(base)==m['baseDescriptor']['sha256'];full={x['path']:x for x in load(base.parent/'artifacts.json')};expected={x['path']:'M' for x in load(base.parent/'changed-artifacts.json')};expected.update({x['path']:'A' for x in load(base.parent/'added-artifacts.json')});assert set(expected)=={x['path'] for x in m['rows']}
counts=collections.Counter();refs=set();review_count=0
for row in m['rows']:
 n=row['path'];assert row['changeKind']==expected[n] and sha(r/n)==row['sha256']==full[n]['sha256'] and row['owner']==row['costOwner']==full[n]['owner']
 assert row['additionalBudgetPp']==row['newProductTests']==0 and not row['wholeSourceAcceptedByMatrix'] and not row['newLeafAccepted']
 assert row['remainingCriteria'] and row['nextPermittedWork']
 for ref in row['evidenceRefs']:
  assert sha(r/ref['path'])==ref['sha256'];refs.add((ref['path'],ref['sha256']))
 if row['status']=='PG_REVIEW_CURRENT_BYTE_BOUND_DYNAMIC_HOLD':
  assert row['special']['reviewCurrentByteExact'] and not row['special']['ptExecutionExempt'];source=row['special']['reviewSource'];assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+n])).hexdigest()==row['sha256'];review_count+=1
 if row['status']=='STYLE_DIFF_STATIC_REVIEW_NATIVE_HOLD':
  source=(r/n).read_text();assert 'while (end < bytes.length)' in source and 'bytes[end] = octet;\n      end++;' in source and 'if (octet == 0) break;' in source
  assert row['special']['changedNativeBehaviorClaimed'] is False
 if row['status']=='METHOD_SUBSET_SUCCESS_WHOLE_DYNAMIC_HOLD':assert Path(n).stem in ['GateCli','GateContractValidator']
 counts[row['status']]+=1
assert dict(counts)==m['statusCounts'] and review_count==3 and collections.Counter(expected.values())=={'M':23,'A':2}
bound=sum(counts[k] for k in ['CURRENT_ADDED_ARTIFACT_HISTORICAL_SUITE_TRACE_BOUND','CURRENT_PROTOCOL_HISTORICAL_WHOLE_SOURCE_TRACE_BOUND','CURRENT_CODEC_DEPENDENCY_ORIGINAL7_REQUALIFIED','CURRENT_RESOURCE_ORIGINAL_PROOF_TRACE_BOUND'])
pending=sum(counts[k] for k in ['SAME_BYTE_COUNTER_CANDIDATE_SCOPE_JOIN_PENDING','HISTORICAL_WHOLE_FACT_CURRENT_JOIN_PENDING','CURRENT_CLASS_HISTORICAL_RECEIPT_METADATA_BOUND'])
held=sum(counts[k] for k in ['PG_REVIEW_CURRENT_BYTE_BOUND_DYNAMIC_HOLD','STYLE_DIFF_STATIC_REVIEW_NATIVE_HOLD','METHOD_SUBSET_SUCCESS_WHOLE_DYNAMIC_HOLD'])
assert (bound,pending,held)==(10,9,6)
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+str(Path(__file__).relative_to(r))])).hexdigest()==sha(Path(__file__))
out=r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21868-changed25-matrix-independent-post-v1';assert not out.exists();out.mkdir()
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),checkerSource=head,checkerSha256=sha(Path(__file__)),observerSource=m['observerSource'],productionCoreMain=m['productionCoreMain'],original=dict(path=str(p.relative_to(r)),sha256=sha(p)),artifactRows=25,changeKinds=dict(collections.Counter(expected.values())),statusCounts=dict(counts),currentSpecificEvidenceTraceBoundRows=10,remainingEvidenceJoinRows=9,wholeDynamicOrNativeHeldRows=6,distinctEvidenceRefs=len(refs),scopeIsCompletionDenominator=False,newProductTests=0,newMethods=0,newSourceProofs=0,newAcceptance=0,wholeG13Accepted=False,whole451Accepted=False,effortRate=None)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,rows=25,traceBound=10,pendingJoin=9,dynamicHeld=6,manifestSha256=sha(out/'manifest.json'))))

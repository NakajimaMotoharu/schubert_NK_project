"""Current Java source and original public proof scope only; no binary or runtime access."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
root=Path.cwd();base=root/'evidence/01_PT/018_NK-OPS-001';inp=base/'input';evidence=base/'evidence';output=evidence/'PG33726-ledger-recent18-source-join-v1';assert not output.exists()
load=lambda path:json.loads(path.read_text());sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest();plan=load(inp/'3440_ledger_recent18_plan.json')
ledger=root/'documents/900_OTHER/910_台帳/915_障害表.md';text=ledger.read_text();sections={int(match.group(1)):match.group(0) for match in re.finditer(r'^## BUG-(\d+)\b.*?(?=^## BUG-|\Z)',text,re.M|re.S)};proofs={}
def proof(prefix):
 paths=list(evidence.glob(prefix+'*'));assert len(paths)==1;path=paths[0]/'manifest.json';value=load(path);assert value['actualExit']==0;proofs[prefix]=dict(path=str(path.relative_to(root)),sha256=sha(path));return value
source_refs=[]
def source(name,call,expected):
 paths=list((root/'src').glob('*/src/main/java/**/'+name+'.java'));assert len(paths)==1;path=paths[0];value=path.read_text();found=[n+1 for n,line in enumerate(value.splitlines()) if call in line];assert len(found)==expected,(name,found,expected)
 source_refs.append(dict(path=str(path.relative_to(root)),sha256=sha(path),reviewedCall=call,expectedSourceSites=expected,lines=found,compiledOrRunHere=False));return value
source('UserAdminController','JmsRequestReplyException.preserveFatal(',13)
wire=source('ProtectedReadWireClient','JmsRequestReplyException.preserveFatal(',1)
source('OwnedTransferDirectory','StorageIoException.preserveFatal(',3)
source('LargeResultReader','SessionStoreException.preserveFatal(',1)
source('ContentDetailController','JmsRequestReplyException.preserveFatal(',3)
source('PendingRevocationRepository','SessionStoreException.preserveFatal(',1)
source('ScenarioFileRegenerator','TemporaryInfrastructureException.preserveFatal(',1)
source('ScenarioReplayService','TemporaryInfrastructureException.preserveFatal(',6)
for name,count in [('CaddyClientAddressResolver',1),('CaddyTransportContextFilter',1),('EncryptedSessionRequestCache',3),('EncryptedSessionSecurityContextRepository',2),('FormCsrfTokenRequestHandler',1),('WebCsrfToken',1),('WebRequestContext',3)]:source(name,'SessionStoreException.preserveFatal(',count)
question=next((root/'src').glob('*/src/main/java/**/QuestionSubmissionService.java'));question_text=question.read_text();assert 'if (failure.getSuppressed().length != 0)' in question_text
source_refs.append(dict(path=str(question.relative_to(root)),sha256=sha(question),review='Collision recovery rejects suppressed cleanup uncertainty; actual caller/TX PT unrun',compiledOrRunHere=False))
wire_proof=proof('PG27836-');assert wire_proof['tests']==40 and wire_proof['targetFour100']['dev/codex/schubert/nk/web/messaging/ProtectedReadWireClient'] is True and wire_proof['wholeScopeFour100'] is False
wire_path=next((root/'src').glob('*/src/main/java/**/ProtectedReadWireClient.java'));assert subprocess.check_output(['git','show',wire_proof['source']+':'+str(wire_path.relative_to(root))])==wire_path.read_bytes()
for prefix,count in [('PG26506-',163),('PG27400-',29),('PG27830-',40)]:
 value=proof(prefix);assert value['tests']==count and all(value[name]==0 for name in ['failures','errors','skipped'])
jms=proof('PG26508-');assert jms['tests']==163 and jms['wholeClosureMeasuredFour100'] and jms['allPositiveMainCrcMatchCurrent']
session=proof('PG27402-');assert session['tests']==29 and session['actualDeployedKeysOrBackendOrFourClassAccess']==0
for name in ['SessionAttributeCodecTest','SessionPayloadCodecTest','WebSessionIdTest']:
 paths=list((root/'src').glob('*/src/test/java/**/'+name+'.java'));assert len(paths)==1;path=paths[0];assert subprocess.check_output(['git','show',session['source']+':'+str(path.relative_to(root))])==path.read_bytes()
address=proof('PG23238-');assert address['tests']==5 and address['wholeTargetCodeCoverage100'] and address['originalTestsCompiled']==0
whitespace=proof('PG27727-');assert whitespace['initialPublisherExit']==1 and whitespace['originalAstInverseExact'] and whitespace['MainOrTestChanges']==0
budget=proof('PG27762-');assert budget['scopeStatus']=='LIMITED_CLOSED_192_HISTORY_30_STARTS_AND_CENTRAL_FORWARD_GUARD' and budget['originalAndFrozenStartEstimatesUnchanged'] and not budget['oldProducersReplayed']
storage_helper=proof('PG27696-');assert storage_helper['tests']==4 and storage_helper['wholeSelectedHelperScopeFour100'] and not storage_helper['wholeProjectFour100']
assert 'dev/codex/schubert/nk/storage/OwnedTransferDirectory' not in storage_helper['classIds']
child=proof('PG23100-');assert child['sourceFixStatus']=='SOURCE_FIXED_STATIC_ALTERNATIVE_ORIGINAL_NATIVE_PT_NOT_RUN_HOLD' and child['productTestsExecuted']==0
closed={2721:('ProtectedReadWireClient40 and eight new provider graph cases qualified originally; current Java byte exact, target100/whole13Main false preserved.',None),2720:('Original192 forecast history/30 starts reconciled; exact source guard now enforces gross=completed+remaining. Frozen original estimates unchanged.',2377),2719:('One generated whitespace tool correction, original AST inverse exact; publisher originalexit1 preserved, Main/Test0.',2376),2705:('Three original session Test source bytes match qualified3c845652; four finite worker shutdown pools/whole29 original proof, no replay.',None),2659:('Original provider error classification163/188physical/172Code CRC/four100 qualified; current broader workflow/backend not accepted.',2339),2478:('Original finite settings Test five cases/whole target Code100; literal rename value identity, no current broker acceptance.',2216)}
partial={2722:'Thirteen guard calls present; controller/session/DB/Actual4 whole dynamic PT remain HOLD. SharedYKT2359 staysOPEN.',2718:'Three storage catalog guards present. PG27696 four tests qualify StorageIoException helper only, not OwnedTransferDirectory runtime/FS; keep original PT HOLD.',2716:'LargeResultReader one guard present; actual native FS/private owner/HTTP graph ending remains HOLD.',2715:'ContentDetailController three guards present; actual controller/FS/DB/session chain not accepted.',2709:'PendingRevocationRepository one metadata guard present; old pre-change Port16 cannot qualify changed repository. Actual SQL/PT HOLD.',2707:'All seven source12 external Servlet/provider guards present. Existing Token4 subset cannot close all seven/actual chain; dynamic scope remains HOLD.',2699:'Collision retry suppressed-nonempty guard present before further recovery; actual compound SQL/rollback and Actual4/DB PT remain unrunHOLD.',2680:'ScenarioFileRegenerator guard now present. Original26862 was a discovery contract, not a retest; actual snapshot/FS/Actual4/whole PT HOLD.',2679:'ScenarioReplayService six guards present; old26850 source-only exactlysix proof is not executed PT or coverage.',2473:'Owned child helper source rename/static alternative confirmed by23100; original native ProcessBuilder/FFM PT and coverage remain HOLD.',2943:'Role width11 source/V030 fix is already recorded, original DDL001..029 unchanged. Actual DB8/rollback/nontruncation cases unrunHOLD; keepBUG2943/YKT2472OPEN.',2400:'Global pre-freeze/source-static workflow issue contains multiple foreign completed bugs. Specific closures do not close all current SDK/Actual4/native and globalF03/451 conditions; preserve generalOPEN.'}
assert set(closed)|set(partial)==set(plan['targetBugIds']) and not set(closed)&set(partial)
rows=[]
for number in plan['targetBugIds']:
 rows.append(dict(bug=number,originalSectionSha256=hashlib.sha256(sections[number].encode()).hexdigest(),state='HISTORICAL_LIMITED_CLOSED_VERIFIED' if number in closed else 'PG_SOURCE_PRESENT_OR_PARTIAL_DYNAMIC_OR_GLOBAL_HOLD',reason=closed[number][0] if number in closed else partial[number],newManufactureHere=0,newTestExecutionHere=0,newAcceptance=0))
# Validate all limited YKT locations before any ledger write; shared2339 is only its provider scope.
ykt=root/'documents/900_OTHER/910_台帳/916_横展開管理台帳.md';ykt_text=ykt.read_text()
for _,number in closed.values():
 if number is not None:assert re.search(r'^## YKT-'+str(number)+r'\b',ykt_text,re.M)
output.mkdir();manifest=dict(actualExit=0,source='fb1783d3dfb1a2e850b81be50ec26b3949ccc398',productionCoreMain='fb1783d3dfb1a2e850b81be50ec26b3949ccc398',terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=rows,currentSourceOnlyRefs=source_refs,originalPublicProofRefs=list(proofs.values()),reviewedOriginalCandidates=18,historicalLimitedSync=6,partialOrHold=12,totalOriginalReviewed=96,remainingOriginalUnreviewed=129,currentMainOrTestChanged=False,productTestsExecuted=0,oldQualifiedTestReplayed=0,whole451Accepted=False,formalUpdated=False,effortRate=None,newAcceptance=0,noSdkClassPrivateVmDbNativeRootOperations=True,newPgcopy24='NOT_RUN_HOLD')
(output/'manifest.json').open('x').write(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
for row in rows:
 number=row['bug'];section=sections[number];header,rest=section.split('\n',1);label='現在CLOSED（既存歴史限定scopeのみ）' if number in closed else '現在OPEN/PG source是正済又はpartial・動的/global未受入'
 note='\n\n2026-11-15 scope照合: '+label+'。'+row['reason']+' PG33726へcurrent Java source/hash/元公開proofを結合。新source製造・試験再演・正式受入加算0。元記録/外国BUG closureは履歴保全。\n'
 text=text.replace(section,header+note+rest,1)
ledger.write_text(text)
for bug,(reason,number) in closed.items():
 if number is None:continue
 match=re.search(r'^## YKT-'+str(number)+r'\b.*?(?=^## YKT-|\Z)',ykt_text,re.M|re.S);section=match.group(0);header,rest=section.split('\n',1);ykt_text=ykt_text.replace(section,header+'\n\n2026-11-15 PG33726 BUG'+str(bug)+'歴史限定scopeのみCLOSEDを元公開proof/後条件で同期。'+reason+' 共有の他対象/実backend/global451は未受入、新実行0。\n'+rest,1)
ykt.write_text(ykt_text)
print(dict(actualExit=0,reviewed18=18,historicalSync=6,sourceOrGlobalHold=12,originalReviewed=96,unreviewed=129,newProductTests=0,newManufacture=0))

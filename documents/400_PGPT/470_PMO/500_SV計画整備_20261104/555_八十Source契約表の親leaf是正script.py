import json,hashlib,collections,os
from pathlib import Path
root=Path.cwd();base=root/'documents/400_PGPT/470_PMO/500_SV計画整備_20261104'
live=Path('/home/mini/codex/project1/work/PMO/pgpt-completion-stage-20261102')
def load(name): return json.loads((live/name).read_bytes())
src=load('source-reuse-matrix.json');groups=load('common-cause-groups.json')['groups'];pkgs={x['packageId']:x for x in load('remaining-work-packages.json')['packages']}
reference={x['id']:x for x in load('remaining-work-packages.json')['referenceOnlyExcludedFromCost']}
def resolve(owner):
 if owner in pkgs:return 'DIRECT_LEAF',[pkgs[owner]]
 children=[p for k,p in pkgs.items() if owner and k.startswith(owner+'.')]
 if children:return 'SPLIT_PARENT_CANDIDATES_NOT_ALLOCATION',children
 if owner in reference:return 'REFERENCE_ONLY',[]
 return 'UNRESOLVED_OWNER',[]
partial={x['path']:x for x in src['rows'] if x['evidenceStatus']=='PARTIAL'};seen=set();rows=[]
contracts={
'AUTH_ADMIN_SQL':('認証/lock/session/管理検索の独立SQL状態とAPI結果','固定clock・専用DBfixture・既存audit/lock/role/null contract','承認済みUI313/SS設計から認証結果・lock時刻・監査/role/検索順の独立期待表。PBKDF等の既vectorとSQL後条件を区別する'),
'BATCH_BACKUP_CLEANUP_BROKER':('Morning admission/Backup/Cleanup/Broker観測の所有と終端','固定stateの観測fixtureと実VM経路を分離。既boot/owner/Unit/DB/原本を現在値へ転用しない','各stepの成功/失敗/skip/再開、原本Backup保持、逆順停止と資源後条件。実permit/Unit/DB操作は事前条件未確定のまま保留'),
'JMS_INBOX_OUTBOX_AUDIT':('JMS接続/transaction/監査のreplayと所有','broker接続providerの公開設定・固定fault・独立DB/JMS期待値','DB commit前/後ACK前/再配送、rollback/重複、close時失敗を区別。実broker起動と純粋fault注入を同一許可と扱わない'),
'QUESTION_JOB_NOTIFICATION':('質問query/更新metadata/receiptのowner・DB後条件','独立SQLfixtureと固定wire/golden、正規owner及び未実行例外系','queryのpage/snapshot/可視性/SQL障害、通知と受付の冪等性。PG14762の18件限定再利用と新未達branchを分離'),
'SCENARIO_MEDIA':('検索/明細/media response・Rangeの独立data契約','SS323 offsetsと固定fixture、DB結果とfile/crypto/HTTPを別層化','page/順/byte/null/未知値/response-layout、descriptorと実file存在・hash・Rangeを混同しない。現PG15664等の限定意味再利用は別記'),
'STARTUP_OWNERSHIP_NATIVE':('API/Web/Root/Caddyの世代・所有・ready・終端・native','public fixed観測metadataの静的確認、真正OS/guest状態と署名世代は別の開始条件','親budget/Unit期限/same-peer identity/socket/info/逆順stop/資源後条件。過去のOS未回収18474を再演せず、nativeは同sourceの別資格'),
'STORAGE_TRANSACTION_RESOURCE':('Storage/Inspector/参照transaction/設定の資源と永続条件','既source/公開設定・固定SQL/FS fault fixtureと実system resourceの境界','constructor invariant、null/欠落/未知値、commit/rollback/close/並行、original保全。原本DB/鍵/実permitへの操作を計画metadataから許可しない'),
'WEB_SESSION_FORMS_AND_VIEWS':('revocation retryとtrusted Caddy transportのrequest lifetime','検証済みactor/transportの固定fixture・独立clock、cookie/session実体なし','再送backoff/15分、期限/上限/非重複、未信頼headerとNPE/unknown。承認QA048049050を適用し新たな仕様へ置換しない')}
for g in groups:
 for path in g['partialPaths']:
  assert path in partial and path not in seen;seen.add(path);s=partial[path];kind,parents=resolve(s['owner']);assert kind in ('DIRECT_LEAF','SPLIT_PARENT_CANDIDATES_NOT_ALLOCATION');assert parents
  p={key:sorted({x for q in parents for x in q[key]}) for key in ('requirements','ss','designFiles','holdIds')}
  p['definitionOfDone']=[{'input':{'candidateTestFiles':sorted({x for q in parents for x in q['definitionOfDone'][0]['input']['candidateTestFiles']})}}]
  p['exitDependencies']={q['packageId']:q['exitDependencies'] for q in parents};p['costOwner']=s['owner']
  contract,fixture,expected=contracts[g['id']]
  misses={k:v['missed'] for k,v in s['counters'].items()}
  rows.append({'sourcePath':path,'sourceSha256':s['sha256'],'owner':s['owner'],'family':g['id'],'ownerRelation':kind,'candidateLeafIds':[q['packageId'] for q in parents],'costAllocationToChildren':None,'contract':contract,'requirements':p['requirements'],'ss':p['ss'],'designFiles':p['designFiles'],'existingProof':s['qualifiedUnitProof'],'existingCounters':s['counters'],'missingCounterQuantity':misses,'counterQuantityIsNotIndependentConditions':True,'inputAndFixtureBoundary':fixture,'independentExpectedResultObligation':expected,'candidateTestFiles':p['definitionOfDone'][0]['input']['candidateTestFiles'],'relatedHoldIds':p['holdIds'],'staticReviewAllowed':'Only named public source/evidence read and already permitted static checks; held paths excluded','dynamicStart':'NOT_YET_AUTHENTICATED_PER_OPERATION; package hold/name does not establish a blanket refusal or permission','necessaryPG':'Review exact missed lines/conditions and oracle before changing; actual defect is entered915 before fix; design feedback follows classification','necessaryPT':'Use existing same-source qualified meaning where valid; add actual missing normal/boundary/null/exception/retry/concurrency obligations; no blind full rerun','unitExit':'All four counters according451 and independent oracle/negative/resource proof for this source; no counter-only whole-WBS acceptance','parentExitDependencies':p['exitDependencies'],'costOwner':p['costOwner'],'countsAsNewCostGroup':False,'estimatedRemainingPp':{'low':None,'base':None,'high':None},'missingPriceBasis':'No same-kind full accepted cycle or exclusive cost; preserve old estimates separately, V did not calibrate','newAcceptance':False})
assert seen==set(partial) and len(rows)==80
membership=collections.Counter(k for g in groups for k in g['leafIds']);assert len(membership)==252 and all(v==1 for v in membership.values()) and set(membership)==set(pkgs)
ownerRows=[{'path':x['path'],'originalOwner':x['owner'],'relation':resolve(x['owner'])[0],'candidateLeafIds':[p['packageId'] for p in resolve(x['owner'])[1]],'allocationPp':None,'newAccepted':False} for x in src['rows']]
assert len(ownerRows)==932
assert sum(x['ownerRelation']=='SPLIT_PARENT_CANDIDATES_NOT_ALLOCATION' for x in rows)==27
for owner in ('WBS-P017-01','WBS-P017-02','WBS-P017-03','WBS-P017-07','WBS-P017-12','WBS-P018-03','WBS-P018-04','WBS-P018-08'):
 assert resolve(owner)[0]=='SPLIT_PARENT_CANDIDATES_NOT_ALLOCATION' and len(resolve(owner)[1])==3
assert resolve('UNRECOGNIZED-FIXED-METADATA-OWNER')==('UNRESOLVED_OWNER',[])
assert resolve('WBS-P019-02')==('REFERENCE_ONLY',[])
stages=[
{'id':'D1','work':'Existing semantic proof reconciliation/necessary public static review','after':[],'exit':'Actual TestID/oracle/source/post joins; no unqualified pass transfer'},
{'id':'D2','work':'Common-cause fixes and source-specific PG/PT closure','after':['D1'],'exit':'All affected targets fixed or justified nonapplicable, preventive tests and source/run/BUG/YKT proof'},
{'id':'D3','work':'Owned actual route/native/Browser/CHR','after':['D2'],'exit':'Per-operation authority/fixture/ownership start proven, authentic terminal plus independent resource post; all CHR/DIF'},
{'id':'D4','work':'Candidate source fixed and full451/trace/requirements/defect gate','after':['D2','D3'],'exit':'Same source/run all required scopes/counters, no major unresolved/QA/feedback issues or trace/secret gaps'},
{'id':'D5','work':'Normal publication/main accepted code, PG/PT closure and IT/ST handoff','after':['D4'],'exit':'Remote evidence/PR/check/protection honored, formal qualification updated, explicit IT/ST start/unmeasured conditions'}]
out={'executionId':'PGPT-SV-20261104-01','pool':'S_POST_SAME10','source':src['source'],'designMain':'bf11a7b63e0d97c34f15a56b41bfd57681c38ccc','scope':'EXACT80_SOURCE_WORK_BREAKDOWN_NOT_PROVEN_COMMON_ROOT_CAUSE_OR_NEW_GROUPS','sourceContractRows':rows,'all932OwnerRelations':ownerRows,'ownerRelationCounts':dict(collections.Counter(x['relation'] for x in ownerRows)),'originalFailure':{'receipt':'d4c4f2','actualExit':1,'exception':'KeyError WBS-P017-03','originalScript':'554_八十Source契約表の原失敗script.py'},'regressionMetadataVectors':10,'counts':{'partialSources':80,'realLeaves':251,'reserve':1,'nonoverlappingFamilyMembership':252,'families':18},'quantityPricingForbidden':True,'referenceOnlyP01902Cost':0,'reserveEarnedProgress':0,'all251SemanticallyAccepted':False,'remaining282':'PG18520:278 executable,4 separate characterization build; no wholeSource NoCode/native exemption','remainingOrdinary':'PG18522 390 class packets with2980 missing references;551 adds26 static method reviews,2954 outstanding; two held source packets15methods excluded','dependencyStages':stages,'criticalPath':'D1>D2>D3>D4>D5; same-source snapshot and actual-route ownership can force requalification. No claim that all D1 work blocks every D2 task.','scheduleInputs':{'perFamilyAcceptedFullCyclePrice':None,'applicableFutureCapacity':None,'parallelSharedAccountUse':None,'holdResolutionUpperBounds':None},'remainingCostPp':{'low':None,'base':None,'high':None},'completionDateRangeJST':{'low':None,'base':None,'high':None},'forecastValidity':'PLAN_NOT_VALIDATED','notBasis':['withdrawn630pp/Dec23','uniform cost per source/test','assumed90pp weekly supply','all unknowns zero'],'newProductPT':0,'newAcceptedCriteria':0,'effortCompletion':None}
f=base/'556_部分未達八十Source作業契約・全所有関係の是正.json';assert not f.exists()
with f.open('x') as stream:json.dump(out,stream,ensure_ascii=False,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
print(json.dumps({'actualExit':0,'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'sourceContracts':80,'families':18,'newAcceptance':0},ensure_ascii=False))

"""P00703 own15 preparation and genuine authorization132 technical result, no original acceptance."""
from pathlib import Path
import copy, datetime, hashlib, json
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';D=R/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106';P=R/'evidence/01_PT/007_NK-AUT-001'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
old=D/'731_WBS65予実・最大二session原三source後版60.json';f=copy.deepcopy(load(old));m=B/'evidence/PG26732-api-context-contract-v1/manifest.json';a=load(m);post=B/'evidence/PG26744-authorization-current-independent-v1/manifest.json';p=load(post);assert a['actualExit']==p['actualExit']==0 and p['tests']==132
out=D/'734_WBS65予実・APIcontext十五source認可一三二後版61.json';assert not out.exists();f.update(revision='WBS65-EXEC-FORECAST-61-API_CONTEXT15_PREPARATION_AUTHORIZATION132',atJST=p['atJST'],previousForecast=ref(old))
wid='WBS-P007-03/1';assert wid not in f['completedPlanWorkIds'];f['completedPlanWorkIds'].append(wid);f['completedPreparationWorkIds'].append(wid)
for k,x in dict(low=.087,base=.227,high=.455).items():
 f['completedPlanPriceSumPp'][k]=round(f['completedPlanPriceSumPp'][k]+x,3);f['remainingOriginalPlanPricePp'][k]=round(f['remainingOriginalPlanPricePp'][k]-x,3);f['revisedRemainingPp'][k]=round(f['revisedRemainingPp'][k]-x,3)
f['partiallyCompletedPlanWorkIds'].append('WBS-P007-03')
for k in ['canonicalSchedulePricePrefixBasePp','startedRowPriceSumBasePp']:f[k]=round(f[k]+.65,3)
technical=dict(kind='API_CONTEXT15_PREPARATION_AND_AUTHORIZATION2_CURRENT_PROTOCOL130',source=p['source'],coreMain=p['productionCoreMain'],run=p['run'],tests=132,newDefinitions=0,physicalClasses=182,positiveMainCrc=167,coverage=p['coverage'],evidence=ref(post),contractAudit=ref(m),MainOrTestChanged=False,originalPriceRetained=True,newAcceptance=0)
f['latestGroupTechnicalResult']=technical;f['individualDecisions'].append(dict(id='WBS-P007-03',preparation='COMPLETED_ONLY_625_ROW_1',ending='NOT_ACCEPTED',evidence=ref(m),currentNormal132=ref(post),reason='Own15 contract/source and pure candidate bodies reviewed. Current wholeAuthorization2+Protocol130 full182 physical single-run four100; originalverify6/admin8 target source/Test/physical unchanged retained no replay. Crypto7/hash3 finite worker/restore qualification pending; actualDB whole10/7 and actor scalar site8/ending dependencies/whole451 not accepted.'))
f['knownObservedProductRunRoster'].append(dict(run=p['run'],tests=132,success=132,failed=0,errors=0,skipped=0,evidence=ref(post),scope='ORIGINAL_AUTHORIZATION2_AND_NECESSARY_CURRENT_PROTOCOL130_SAME_RUN_NOT_UNIQUE_OR_FORMAL'))
tot=f['knownObservedProductRunTotals'];tot['runs']+=1;tot['actualExecutions']+=132;tot['success']+=132;tot['scope']='EXPLICIT_OBSERVED25_RUN1715_EXECUTION_ROSTER_ONLY_NOT_GLOBAL_UNIQUE_FORMAL_OR_NEW_DEFINITIONS'
f['legacyNumericCounterSnapshot']['noteCurrentAuthorization132']='Legacy counters retained as historical snapshots; use knownObservedProductRunRoster/Total for current explicit executions. No arithmetic unique-case qualification.'
f['remainingPriceAccountingNote']='P00703/1 original .087/.227/.455 preparation completed; /2 .163/.423/.845 unchanged for DB/current crypto finite workers/actor scalar and exit dependencies. Whole132 needed normal evidence within original .25/.65/1.3, no extra fees/new scope/new definitions. Price reduction is not effort or dedicated shared-token cost.'
write(out,f)
spec=P/'4067_P00703認可二件・現Protocol全一三二_単体テスト仕様書.md';assert not spec.exists();spec.write_text('''# P00703 API context・USER/ADMIN・owner再検証

Program NK-AUT-001、AUT-001/002/003・QST-008、UI225/226/234/241、SS314 §6/9/11/12。原15sourceの範囲・設計commit/hash・個別期待値は [PG26732 manifest](../018_NK-OPS-001/evidence/PG26732-api-context-contract-v1/manifest.json) のownedSourceHashes/checksへ対応。

通常PT: AuthorizationServiceTestの元2method全件（PT-AUT-008-01/02）＋現Protocol元130件、PG26742-AUTHORIZATION-CURRENT132。USER/ADMIN本人通知許可・他人通知は両role0104、他人質問ADMINのみ許可、USER管理0103。N12/64byte/null/closed denial code/redacted displayのliteralを独立期待値とする。Productionをexpected算出に使わない。Java25.0.4、JUnit1.13.4、JaCoCo0.8.15、branch/source/input/tool hash・command・終了code・環境はmanifest。

Main/Testは変更なし。許可されたAPI6entry（認可3、Role、package2）だけを旧normal buildの同一source/byteから取り出し、現在Protocol176physical/既資格Test47class/5resourceと結合。API wholejar・他entry payload・actual四classをread/hashしない。全2methodをfresh compile、PMD/Checkstyle/format0。MainのNullAway/Mainstyle/SpotBugsはsource/6byte/ClassStatsの厳密一致で既証拠を再利用。

実行commandはinput/1323_authorization_current_qualifier.pyのprepare/run、1324 static、1325 preflight、1326 independent post。実command配列とunit terminalは [PG26744](../018_NK-OPS-001/evidence/PG26744-authorization-current-independent-v1/manifest.json)にhash付き保存。132 found/started/success、failure/error/skipped/abort0。旧exec合成・手動除外0。

coverageは全182physical・167positiveCRC・163実行classを同一runで照合。line3518/method752/class163/branch1044（instruction17637/complexity1301）すべてmiss0。Code無し15（package9/abstract6）と標準switchmap4は入力に保持し、classinfo173/XML173/実行163を区別。これをAPI認証DBや全PGPT coverageへ転用しない。

原verify6/admin8はsource/Test/target physicalが同じことだけ確認し、原run制限付き保存・再演0。実DB whole10/7はHOLD。AuthContextCodecTest7/ContextHashTest3の全source/独立JCA oracleは読取済みだが、無期限future/Executor close所有の有限検証が未完のため未実行。部分選択で補わない。ActorのUTF8 scalar/site8も全条件確認済みにせずglobalYKT2328へ残す。

当群原/1準備のみ完了。/2、P00401/P00601終了依存、実権限/DB/HTTP、451、元190項目は未受入。Main/Test変更0/新定義0/追加費0。正式1964PT/53scope、工数完成率nullを維持。
''')
for name in ['001_NK-AUT-001_単体テスト仕様書.md','002_NK-AUT-001_実行結果.md']:
 q=P/name;q.write_text(q.read_text()+'\n\n## WBS65 P00703 原十五sourceと通常認可132（2026-11-12）\n\n[4067仕様・結果](4067_P00703認可二件・現Protocol全一三二_単体テスト仕様書.md)へ対応。PG26742全132真正0→PG26744独立0、全182physical/167CRC・L3518M752C163B1044全miss0。原verify6/admin8再演0、DB/暗号有限owner/actor scalar/終了依存と全451未受入。原/1準備だけ完了、元190新0。\n')
nextcmd='Continue actual625 P00704 original logout/revocation and CSRF inventory/SS314 mapping in dependency order; own safe synthetic normal permitted after full footprint, retain bounded existing original proofs without confirming replay. P00703 crypto/hash whole tests need finite owner/final restoration before fresh execution; source role owner/realDB/actor Unicode/current dependencies remain pending. No actual auth/key/DB/Root/VM/held4/intent. usage11:25:53 nextNOTBEFORE12:25:53 actualclock. Continue notstopatnormalboundary.'
cfg=load(B/'input/1322_api_context_contract_start.json');c=dict(groupId=cfg['groupId'],recordPath=str((D/'735_WBS65APIcontext十五source認可一三二結果.json').relative_to(R)),manifestPath=str(m.relative_to(R)),manifestSha256=sha(m),terminalAtUTC=p['atJST'],run=p['run'],workIds=cfg['workIds'],outcome='OWN15_PREPARATION_COMPLETE_AUTHORIZATION_CURRENT132_100_ENDING_UNACCEPTED',technical=technical,forecastRef=ref(out),nextCommand=nextcmd,checkpointText='P00703 own15/SS3146・9・11契約対応完了。PG26736 freshTest2compile→26738PMD/CS/GJF0→26740source/Main6静的bytebind0→26742全132 genuine0→26744 ab79611d独立0。182physical/167positiveCRC/163実行、L3518M752C163B1044全miss0・旧exec/手動除外0。Main629不変更/新defs0、原verify6/admin8 source/Test/physical同一限定保持・再演0。crypto7/hash3有限owner/実DB/actor scalar site8/終了依存・451未受入。原/1 .087/.227/.455準備のみ完了、版61残'+str(f['revisedRemainingPp'])+'未較正、明示25run1715exec1707success8fail（globaluniqueではない）、元190新0/正式1964-53/工数null。次P00704、usage次12:25:53実clock。')
write(B/'input/1329_api_context_close.json',c);print(json.dumps(dict(actualExit=0,remaining=f['revisedRemainingPp'],forecast=ref(out)),ensure_ascii=False))

"""Join committed source and already executed source-only checks, never actual SDK/PT."""
from pathlib import Path
from decimal import Decimal
import datetime,hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';e=b/'evidence/PG33710-pgcopy-source-pt-unrun-review-v1';out=b/'evidence/PG33712-pgcopy-source-only-limited-join-v1';d=r/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
core=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert core=='fb1783d3dfb1a2e850b81be50ec26b3949ccc398'
checks=load(e/'source-only-checks-v2.json');v=load(e/'source-only-review-v2.json');assert checks['actualExit']==v['actualExit']==0
for path,h in checks['inputHashes'].items():
 assert sha(r/path)==h
 assert subprocess.check_output(['git','show',core+':'+path])==(r/path).read_bytes()
out.mkdir();refs=[dict(path=str(p.relative_to(r)),sha256=sha(p)) for p in sorted(e.iterdir()) if p.is_file()]
technical=dict(kind='PGCOPY_SOURCE_MANUFACTURED24_PT_SOURCE_NOT_RUN_HOLD',productionCoreMain=core,sourceCommit=core,compiledSource=None,actualUnitSource=None,sourceFormatFindings=0,sourceParseCheckstyleFindings=0,sourceOnlyReviewActualExit=0,plannedTests=24,applicationTestsExecuted=0,all24='NOT_RUN_HOLD',coverage=None,unfilteredCoverage=None,sdkAbiCompilation='NOT_RUN_HOLD',nullability='NOT_RUN_HOLD',semanticPMD='NOT_RUN_HOLD',spotbugs='NOT_RUN_HOLD',wholeBuild='NOT_RUN_HOLD',actualDriverDB='NOT_RUN_HOLD',sourceGuardUnchanged=True,previous1050Applicability='HISTORICAL_PRE_NEW_POM_ONLY_NO_QUALIFICATION_TRANSFER',bug3001='WITHDRAWN_FALSE_POSITIVE_NOT_SOURCE_FIX',bug3002And3003='SOURCE_FIXED_DYNAMIC_PT_OPEN_HOLD',bug3004='CLOSED_SOURCE_METADATA_REVIEW_ONLY',formalUpdated=False,global451Accepted=False,newAcceptance=0,effortRate=None)
manifest=dict(actualExit=0,source=core,productionCoreMain=core,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),branch='dev-foundation',technical=technical,evidenceRefs=refs,claims='SOURCE_ONLY_NOT_PT_PASS_OR_MEASURED_COVERAGE',runtimeOperations=0,refusalRetry=0,credentialRecords=0)
write(out/'manifest.json',manifest)
f=load(next(d.glob('2089*')));f['revision']='604-PGCOPY_SOURCE_ONLY_COMPLETED24_PT_NOT_RUN_HOLD';f['atJST']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();f['previousForecast']=dict(path=str(next(d.glob('2089*')).relative_to(r)),sha256=sha(next(d.glob('2089*'))))
estimate=dict(low=1.,base=3.,high=8.)
for k,a in estimate.items():
 for field,delta in [('additionalCompletedWorkPp',a),('additionalDiscoveredRemainingPp',-a),('revisedRemainingPp',-a)]:f[field][k]=float(Decimal(str(f[field][k]))+Decimal(str(delta)))
f['currentFullForecastBudgetBridge']['additionalRemainingPp']=f['additionalDiscoveredRemainingPp']
f['completedPreparationWorkIds'].append('P01903_SSC417_PGJDBC_COPY_SOURCE_PT_SOURCE_REVIEW_HOLD')
f['latestGroupTechnicalResult']=technical
f['latestNewDefinitionDisclosure']=dict(planned=24,executed=0,status='NOT_RUN_HOLD',coverage=None,notAddedToProductRunRoster=True)
f['followupPgcopySdkPtHold']=dict(scope='SDK ABI/type/static+dynamic24/fresh impacted regression/raw coverage/actual driver DB contracts',status='NOT_RUN_HOLD',budget='Original P019/451/K owners retain uncompleted work; this additional1/3/8 only source+review. Not additive repricing, not zero remaining effort.',additionalBudgetAddedPp=0,oldSuccessCannotTransfer=True)
fp=d/'2092_WBS65予実・PgJDBC COPY source段後版604.json';write(fp,f)
c=load(i/'3410_pgcopy_source_start.json');c.update(recordPath='documents/400_PGPT/470_PMO/600_通常PGPT_20261106/2093_WBS65PgJDBC COPY source段終了.json',sourceAfter=core,forecastRef=dict(path=str(fp.relative_to(r)),sha256=sha(fp)),manifestPath=str((out/'manifest.json').relative_to(r)),manifestSha256=sha(out/'manifest.json'),terminalAtUTC=manifest['terminalAtUTC'],outcome='SOURCE_MANUFACTURED_REVIEW_ONLY24_PT_NOT_RUN_HOLD_NO_FORMAL_ACCEPTANCE',technical=technical,summary='SSC417具象六COPY sourceと未来24PT定義をCorefb1783d3へ固定。GJF/CS source parse0と独立六SQL/wire/所有レビュー、原SQL正常・BUG3001誤検知取り下げ、BUG3002/3003source是正だが型/動的OPEN、BUG3004metadata限定閉鎖。SDK読取/compile/ABI/NullAway/SB/semanticPMD/build/PT/coverage未実行、全24NOT_RUN_HOLD。旧Coreef461eba/Unita48eec60の全1050はPOM前歴史資格で新sourceへ流用0。source段1/3/8のみ完了、元P019/451未完費を保持し二重費用0、残397.324/837.386/1643.415。正式1964/53・正本184/625・元190新0・工数null/App raw179/35140/35075/歴史不成功65不変更。SDK/actualDB/native/Root/aru/HOLD未受入。',nextCommand='Publish onlySSC417 source-stage status to914/main via ordinaryPR, never code/POM/Test/evidence. Continue permitted originalPG/PT and173remaining ledger candidate scope audit without replaying prior successes. Freshquota/hourly; group completion not overall stop. AllSDK/DB/Root/native/aru HOLD preserved.')
write(i/'3418_pgcopy_source_end.json',c)
p=r/'documents/900_OTHER/910_台帳/914_詳細設計修正管理台帳.md'
with p.open('a') as stream:stream.write('\n2026-11-15 SSC417 source段結果: Core'+core+'、PG33710/33712。Production source+24未来PT source/149仕様/150結果を固定、GJF/CSsource parse指摘0と独立sourceレビューのみ終了0。SDK ABI/type/compile/NullAway/SB/semanticPMD/build/動的PT/四coverageはNOT_RUN_HOLD・null、旧1050はPOM前別scopeで流用0。BUG3001は誤検知取り下げ、BUG3002/3003はsource是正・動的OPEN、BUG3004metadata限定閉鎖。PG/PT全体は未完、正式/受入/工数率不変更。mainへ当台帳source段限定反映予定。\n')
print(json.dumps(dict(actualExit=0,core=core,manifest=str((out/'manifest.json').relative_to(r)),newActualPT=0,remaining=f['revisedRemainingPp'])))

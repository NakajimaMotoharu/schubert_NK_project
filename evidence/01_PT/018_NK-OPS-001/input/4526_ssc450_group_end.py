"""Return actual SQL6 PG/PT to its canonical owner; no original parent acceptance inferred."""
from pathlib import Path
import datetime
import hashlib
import json
import sys

r=Path.cwd();sys.path[:0]=[str(r/'tools/quality'),str(r/'tools/quality/vm/050_s1')]
import pg998_metrics as metrics
from pmo_quota_binding import digest,end_fields
from source_evidence_binding import bind
b=r/'evidence/01_PT/018_NK-OPS-001';d=r/'documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
start=load(d/'039_SSC450閉SQL六Main群開始.json')
p=b/'evidence/PG36948-ssc450-six-main-quality-join-v1/manifest.json';m=load(p)
assert m['actualExit']==0 and m['targetSixSourceRawFour100'] and m['tests']==162
q=load(Path(sys.argv[1]));now=datetime.datetime.now(datetime.timezone.utc).isoformat()
bound=end_fields(start['quota'],q,digest(q),now,m['terminalAtUTC'],4)
assert not any(x['groupId']==start['groupId'] and x.get('groupBoundary')=='END' for x in map(json.loads,metrics.EVENTS.read_text().splitlines()))
next_command=('Publish SSC450 limited914 result and push feature proofs. Continue F03 original2.4 row: inspect the remaining BackupStartIntentFiles DMI/useless-suppression two actual sites and unchanged SS308 acquisition contract, before corrective PG/PT. Keep QA056 four classfiles/API-Web pending, no Root/operational native/VM/DB/key/HOLD operations. Reuse successful current477 compile and exact unchanged module bytes; no same-success regression replay. Then original-item P01808/P00405 permitted ordinary contracts and individual criteria, not unrelated utility loops.')
values=dict(bound,source=m['source'],actualUnitSource=m['actualUnitSource'],run=m['run'],groupBoundary='END',
    wbsLeafIds=start['values']['wbsLeafIds'],workCategory='SELECTED_TEST',workAttributionKind='ADDITIONAL_FINDING',
    estimateAtGroupStartPp=start['values']['estimateAtGroupStartPp'],groupCapPp=4,
    canonicalChangeAndCostOwner='WBS-P019-03',resultRecipient='WBS-F03',sameSharedWorkChargedOnce=True,
    managementWorkIds=['追加A-SSC450-SQL6'],completedAddedTaskPricePp=1.2,completedOriginalRowPricePp=0,
    sourceEvidenceBinding=bind([(p,sha(p))],m['source']),newAcceptance=0,formalUpdated=False,effortCompletionRate=None,
    criterionReductions=['F03 static/quality: six closed SQL Main 76 literal operations now SB0/missing0/errors0; all134 sites individually reviewed, no rule changes',
      'P01903 local SQL6: actual162/FES-notrun0, source/Core/Unit/CRC/Root bytes and independent original160 oracles intact',
      'P01903 local quality: raw544L147M7C254B2715I all hit, all12 self-suppression sites and six public ABIs verified',
      'F03 remaining: Backup two raw sites, Bootstrap/Batch global PMD971 classification and API/Web QA056 still unresolved; helpers raw retained'],
    technicalMeasurementDelta=dict(tests=162,success=162,failed=0,errors=0,skipped=0,notRun=0,mainSources=26,physical=46,targetSixRaw=m['targetRawCounters'],spotbugs=0,staticRawReviewed=134,cleanupSites=12,publicApis=6,wholeComponentRaw100=False),
    bugsClosed=['BUG3132','BUG3136'],horizontalClosed=['YKT2603','YKT2607'],nextCommand=next_command)
event=metrics.append(start['groupId'],'CHECKPOINT',values)
target=d/'043_SSC450通常162・六Main局所品質閉鎖.json'
report=dict(actualExit=0,eventId=event,groupId=start['groupId'],values=values,quota=q,proof=ref(p),
    forecast=dict(asIssuedDetailRemainingPp='1099.386',completedIssuedTaskPricePp='5.050',completedAddedTaskPricePp='3.150',remainingDetailBasePp='1094.336',effortCompletionRate=None,newOriginal190Acceptance=0,actualDedicatedPp=None,tokenTotals=None))
target.open('x').write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
summary=('SSC450 Core84d9d3ed/Unit0864b0a2/PG36942、通常162全成功・F/E/S/notrun0。PG36948独立照合: 六sourceのraw544L147M7C254B2715I全miss0、全12cleanup条件両branchhit、六publicABI不変、SQL76/元160Test本文不変、Root1101の該当46byte完全一致・他Bootstrap184及びProtocol175/Storage80/Batch646byte不変。PMDraw134全site適用/未分類0・SB46全ClassStats/missing/errors/bug0。真NoCode9も物理へ保持。helper全体raw未達は残し、旧80/161exec合算0。BUG3132/3136とYKT2603/2607当六Main対象CLOSED。元F03/P01903/451全体/正式1964-53/元190新規受入は未更新。追加A1.2だけ完了、累計元価格5.050＋追加3.150、残1094.336ppは未較正作業価格で工数率でない。')
l=r/'documents/900_OTHER/910_台帳'
with (l/'914_詳細設計修正管理台帳.md').open('a') as f:f.write('\nSSC450 PG/PT限定結果（2026-11-17）: '+summary+' 証跡 '+str(p.relative_to(r))+' SHA256 '+sha(p)+'。\n')
for name,ids in [('915_障害表.md',['BUG3132','BUG3136']),('916_横展開管理台帳.md',['YKT2603','YKT2607'])]:
    with (l/name).open('a') as f:
        for ident in ids:f.write('\n2026-11-17 '+ident+' 全対象の是正/独立期待/再試験・横展開を完了し限定CLOSED。'+summary+' 修正Core '+m['source']+'、Unit '+m['actualUnitSource']+'、証跡PG36948 SHA256 '+sha(p)+'。完了2026-11-17。\n')
for name in ['456_領域別進捗・利用枠・中断再開管理.md','460_基盤残件・再開優先順.md']:
    p2=r/'documents/400_PGPT/450_品質'/name;title,body=p2.read_text().split('\n',1)
    p2.write_text(title+'\n\n## WBS66 SSC450六Main通常162・局所品質閉鎖 '+now+'\n\n'+summary+' own unit/post/raw/ABI全真正終了0、既知own job残0、foreign VM/DB/aru未照会UNKNOWN・二重操作0。fresh残'+str(q['primary']['remainingPercent'])+'、共有同窓差'+str(bound['observedSharedPp'])+'pp、event '+event+'。次: '+next_command+'\n'+body)
s=r.parent/'PMO/pgpt-completion-stage-20261102'
for name in ['checkpoint.json','continuation-gate.json','cost-ledger.json']:
    p2=s/name;v=load(p2);v.update(lastEventId=event,ordinaryActiveGroup=None,ordinaryGroupNotYetClosed=False,currentQuota=q,mayFinishTurn=False,executionAllowed=True,newImplementationAllowed=bound['newImplementationAllowedByQuota'],productionCoreMain=m['source'],actualUnitSource=m['actualUnitSource'],headAtCheckpoint=m['actualUnitSource'],currentWbs66RemainingDetailBasePp='1094.336',latestWbs66Record=ref(target),nextCommand=next_command)
    v['currentManufacturingBoundary']=dict(source=m['source'],unit=m['actualUnitSource'],run=m['run'],ownJobState='TRUE_TERMINAL0_UNIT_POST_RAW_ABI',foreignHostVmDbState='UNQUERIED_UNKNOWN',scope='SQL6_LOCAL_RAW100_HELPERS_RAW_INCOMPLETE',evidence=ref(p),whole451Accepted=False,newAcceptance=0)
    p2.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
(b/'4456_SSC450通常162実行結果.md').open('x').write('# SSC450 通常162実行結果\n\n'+summary+'\n\n公開証跡 '+str(p.relative_to(r))+' SHA256 '+sha(p)+'。元80/161の品質不足、compile/admission失敗を保持し合格へ加算しない。環境・全command・開始終了時刻・raw入力と出力のhashは各referenced manifest。実DB/master移行後条件・QA051 final・他module全品質は別未完。\n')
print(json.dumps(dict(actualExit=0,event=event,tests=162,targetSixRaw100=True,newOriginalAcceptance=0,remainingDetail='1094.336',observedSharedPp=bound['observedSharedPp'])))
